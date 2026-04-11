from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .application.sources import GROUNDED, INSUFFICIENT_EVIDENCE
from .config import get_settings
from .domain.models import ImportJobRecord, SourceRecord, VectorRecord
from .evals.assertions import assert_eval_case
from .evals.cases import EvalCase
from .infra.ollama.client import OllamaChatClient, OllamaEmbeddingsClient
from .infra.sqlite.database import connect_sqlite, initialize_metadata_schema
from .infra.sqlite.repositories import SQLiteImportJobRepository, SQLiteSourceRepository
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


def main() -> None:
    settings = get_settings()
    runtime = build_runtime(settings=settings)
    runtime.initialize(start_worker=True)
    paths = runtime.paths
    print(f"eval scaffold ready: {settings.app_name} [{settings.environment}]")
    print(f"data directory: {paths.data_dir}")

    connection = connect_sqlite(paths.metadata_db_path)
    try:
        initialize_metadata_schema(connection)
        source_repository = SQLiteSourceRepository(connection)
        import_job_repository = SQLiteImportJobRepository(connection)

        timestamp = datetime.now(UTC)
        source_id = str(uuid4())
        job_id = str(uuid4())
        source_record = SourceRecord(
            id=source_id,
            name="Phase 2 dependency proof",
            description="Minimal metadata repository smoke check.",
            source_type="phase2-smoke",
            original_path="phase2://smoke-source",
            snapshot_path="phase2://snapshot",
            content_hash="phase2-smoke-hash",
            import_status="completed",
            created_at=timestamp,
            updated_at=timestamp,
        )
        import_job_record = ImportJobRecord(
            job_id=job_id,
            source_id=source_id,
            status="completed",
            started_at=timestamp,
            finished_at=timestamp,
            error_message=None,
        )

        source_repository.create(source_record)
        import_job_repository.create(import_job_record)

        stored_source = source_repository.get_by_id(source_id)
        stored_job = import_job_repository.get_by_id(job_id)
        if stored_source is None or stored_job is None:
            raise RuntimeError("SQLite repository smoke check failed.")
        if not any(record.id == source_id for record in source_repository.list_all()):
            raise RuntimeError("SQLite source listing smoke check failed.")
        catalog_source = runtime.catalog_service.get_source(source_id)
        if catalog_source.id != source_id:
            raise RuntimeError("Source catalog smoke check failed.")
        print("sqlite repository write/read/list: ok")

        embeddings_client = OllamaEmbeddingsClient(
            base_url=settings.ollama_base_url,
            model=settings.embedding_model,
        )
        embedding = embeddings_client.embed(["Source Lens Phase 2 dependency proof"])[0]
        if not embedding:
            raise RuntimeError("Embedding smoke check returned an empty vector.")
        print(f"ollama embedding: ok ({len(embedding)} dimensions)")

        vector_store = runtime.vector_store
        vector_store.ensure_collection(len(embedding))
        point_id = str(uuid4())
        vector_store.upsert(
            [
                VectorRecord(
                    point_id=point_id,
                    vector=embedding,
                    payload={
                        "source_id": source_id,
                        "chunk_id": f"{source_id}:0",
                        "chunk_index": 0,
                        "text": "Source Lens dependency proof chunk for ask flow smoke testing.",
                    },
                )
            ]
        )
        matches = vector_store.query(embedding, limit=1, source_id=source_id)
        if not matches or matches[0].point_id != point_id:
            raise RuntimeError("Qdrant similarity query smoke check failed.")
        print(f"qdrant local insert/query: ok ({matches[0].score:.4f})")

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

        _run_grounded_eval_case(runtime)
        print(f"eval case {GOLDEN_CASE.name}: ok")

        _run_insufficient_evidence_case(
            source_repository=source_repository,
            runtime=runtime,
            timestamp=timestamp,
        )
        print(f"eval case {WEAK_CASE.name}: ok")
    finally:
        connection.close()
        runtime.shutdown()


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


def _run_insufficient_evidence_case(
    *,
    source_repository: SQLiteSourceRepository,
    runtime,
    timestamp: datetime,
) -> None:
    empty_source_id = str(uuid4())
    source_repository.create(
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
