from pathlib import Path

from source_lens_api.application.imports import FAILED, INTERRUPTED_ERROR_MESSAGE, ImportRequest
from source_lens_api.infra.qdrant.vector_store import QdrantLocalVectorStore

from .support import (
    FakeEmbeddingsClient,
    build_test_runtime,
    wait_for_job_status,
    write_text_fixture,
)


def test_import_job_completes_and_vectors_are_queryable_by_source(tmp_path: Path) -> None:
    vector_store = QdrantLocalVectorStore(
        collection_name="source_lens_chunks",
        storage_path=tmp_path / "qdrant",
    )
    runtime = build_test_runtime(
        tmp_path,
        vector_store=vector_store,
    )
    runtime.initialize(start_worker=True)
    input_file = write_text_fixture(
        tmp_path / "notes.txt",
        "First paragraph for import.\n\nSecond paragraph for retrieval.",
    )

    try:
        submission = runtime.coordinator.submit_import(ImportRequest(path=str(input_file)))
        wait_for_job_status(runtime, submission.job_id, "completed")
        matches = vector_store.query([10.0, 1.0, 1.0], limit=10, source_id=submission.source_id)
    finally:
        runtime.shutdown()

    assert matches
    assert all(match.payload["source_id"] == submission.source_id for match in matches)
    assert all(match.payload["text"] for match in matches)


def test_import_job_marks_failure_when_embeddings_error(tmp_path: Path) -> None:
    runtime = build_test_runtime(
        tmp_path,
        embeddings=FakeEmbeddingsClient(error_message="Embedding failed for test"),
    )
    runtime.initialize(start_worker=True)
    input_file = write_text_fixture(tmp_path / "notes.txt", "Failure path input")

    try:
        submission = runtime.coordinator.submit_import(ImportRequest(path=str(input_file)))
        wait_for_job_status(runtime, submission.job_id, FAILED)
        job = runtime.coordinator.get_job(submission.job_id)
    finally:
        runtime.shutdown()

    assert job is not None
    assert job.error_message == "Embedding failed for test"


def test_runtime_reconciles_interrupted_queued_jobs_as_failed(tmp_path: Path) -> None:
    runtime = build_test_runtime(tmp_path)
    runtime.initialize(start_worker=False)
    input_file = write_text_fixture(tmp_path / "notes.txt", "Queued input")
    submission = runtime.coordinator.submit_import(ImportRequest(path=str(input_file)))
    runtime.shutdown()

    second_runtime = build_test_runtime(tmp_path)
    second_runtime.initialize(start_worker=False)
    try:
        job = second_runtime.coordinator.get_job(submission.job_id)
    finally:
        second_runtime.shutdown()

    assert job is not None
    assert job.status == FAILED
    assert job.error_message == INTERRUPTED_ERROR_MESSAGE


def test_reimporting_same_path_creates_distinct_source_ids(tmp_path: Path) -> None:
    runtime = build_test_runtime(tmp_path)
    runtime.initialize(start_worker=True)
    input_file = write_text_fixture(tmp_path / "notes.txt", "Reusable import source")

    try:
        first = runtime.coordinator.submit_import(ImportRequest(path=str(input_file)))
        second = runtime.coordinator.submit_import(ImportRequest(path=str(input_file)))
        wait_for_job_status(runtime, first.job_id, "completed")
        wait_for_job_status(runtime, second.job_id, "completed")
    finally:
        runtime.shutdown()

    assert first.source_id != second.source_id
