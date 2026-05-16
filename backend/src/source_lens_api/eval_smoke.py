import argparse
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .application.sources import GROUNDED, INSUFFICIENT_EVIDENCE
from .config import Settings, get_settings
from .domain.models import SourceRecord
from .evals.assertions import assert_eval_case
from .evals.cases import EvalCase
from .evals.doubles import DeterministicEvalChatClient, DeterministicEvalEmbeddingsClient
from .infra.ollama.client import OllamaChatClient, OllamaEmbeddingsClient
from .infra.sqlite.database import metadata_connection
from .infra.sqlite.repositories import SQLiteSourceRepository
from .runtime import build_runtime

GOLDEN_CASE = EvalCase(
    name="grounded_golden_path",
    question="What vector store does the backend vertical slice use?",
    expected_grounding_status=GROUNDED,
    expected_evidence_substrings=("Qdrant local mode",),
)

WEAK_CASE = EvalCase(
    name="insufficient_evidence",
    question="Can you answer without stored evidence?",
    expected_grounding_status=INSUFFICIENT_EVIDENCE,
    require_non_empty_answer=True,
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run Source Lens backend eval smoke checks.")
    parser.add_argument(
        "--live-deps",
        action="store_true",
        help="Also verify live Ollama chat and embedding dependencies.",
    )
    args = parser.parse_args(argv)
    run_eval(get_settings(), include_live_dependency_proof=args.live_deps)


def run_eval(
    settings: Settings,
    *,
    include_live_dependency_proof: bool = False,
) -> None:
    eval_settings = settings.model_copy(update={"data_dir": settings.data_dir / "eval-smoke"})
    runtime = build_runtime(
        settings=eval_settings,
        chat=None if include_live_dependency_proof else DeterministicEvalChatClient(),
        embeddings=(
            None if include_live_dependency_proof else DeterministicEvalEmbeddingsClient()
        ),
    )
    runtime.initialize(start_worker=True)
    paths = runtime.paths
    print(f"eval scaffold ready: {eval_settings.app_name} [{eval_settings.environment}]")
    print(f"data directory: {paths.data_dir}")

    try:
        if include_live_dependency_proof:
            _run_live_dependency_proof(eval_settings)

        _run_grounded_eval_case(runtime)
        print(f"eval case {GOLDEN_CASE.name}: ok")

        _run_insufficient_evidence_case(runtime)
        print(f"eval case {WEAK_CASE.name}: ok")
    finally:
        runtime.shutdown()


def _run_live_dependency_proof(settings: Settings) -> None:
    embeddings_client = OllamaEmbeddingsClient(
        base_url=settings.ollama_base_url,
        model=settings.embedding_model,
    )
    embedding = embeddings_client.embed(["Source Lens Phase 2 dependency proof"])[0]
    if not embedding:
        raise RuntimeError("Embedding smoke check returned an empty vector.")
    print(f"ollama embedding: ok ({len(embedding)} dimensions)")

    chat_client = OllamaChatClient(
        base_url=settings.ollama_base_url,
        model=settings.chat_model,
    )
    chat_response = chat_client.generate(
        "You are running a deterministic smoke test. "
        "Reply with exactly SOURCE_LENS_PHASE2_OK and nothing else."
    )
    if "SOURCE_LENS_PHASE2_OK" not in chat_response:
        raise RuntimeError(
            "Chat smoke check returned an unexpected response: "
            f"{chat_response!r}"
        )
    print("ollama chat: ok")


def _run_grounded_eval_case(runtime) -> None:
    fixture_path = Path(__file__).resolve().parents[2] / "evals" / "fixtures" / "golden_source.md"
    submission = runtime.coordinator.submit_import(
        replace(
            _base_import_request(),
            path=str(fixture_path),
        )
    )
    _wait_for_job_completion(runtime, submission.job_id)
    result = runtime.ask_service.ask(
        source_id=submission.source_id,
        question=GOLDEN_CASE.question,
    )
    assert_eval_case(
        case=GOLDEN_CASE,
        grounding_status=result.grounding_status,
        answer=result.answer,
        evidence_texts=[item.text for item in result.evidence],
    )
    if not result.evidence:
        raise AssertionError(f"[{GOLDEN_CASE.name}] evidence must not be empty")
    if any(item.chunk_id.split(":")[0] != submission.source_id for item in result.evidence):
        raise AssertionError(f"[{GOLDEN_CASE.name}] evidence included another source")


def _run_insufficient_evidence_case(runtime) -> None:
    empty_source_id = str(uuid4())
    timestamp = datetime.now(UTC)
    with metadata_connection(runtime.paths.metadata_db_path) as connection:
        SQLiteSourceRepository(connection).create(
            SourceRecord(
                id=empty_source_id,
                name="Eval weak evidence source",
                description="No vectors are stored for this source.",
                source_type="eval-empty",
                original_path="eval://weak-source",
                snapshot_path="eval://weak-snapshot",
                content_hash="eval-weak-hash",
                import_status="completed",
                created_at=timestamp,
                updated_at=timestamp,
            )
        )
    result = runtime.ask_service.ask(
        source_id=empty_source_id,
        question=WEAK_CASE.question,
    )
    assert_eval_case(
        case=WEAK_CASE,
        grounding_status=result.grounding_status,
        answer=result.answer,
        evidence_texts=[item.text for item in result.evidence],
    )
    if result.evidence:
        raise AssertionError(f"[{WEAK_CASE.name}] evidence must be empty")


def _base_import_request():
    from .application.imports import ImportRequest

    return ImportRequest(
        path="",
        name="Source Lens eval fixture",
        description="Repo-owned golden fixture for eval regression checks.",
    )


def _wait_for_job_completion(runtime, job_id: str, *, timeout_seconds: float = 15.0) -> None:
    import time

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        job = runtime.coordinator.get_job(job_id)
        if job is not None and job.status == "completed":
            return
        if job is not None and job.status == "failed":
            raise RuntimeError(f"Import job failed during eval: {job.error_message}")
        time.sleep(0.05)
    raise RuntimeError(f"Timed out waiting for import job {job_id} during eval")


if __name__ == "__main__":
    main()
