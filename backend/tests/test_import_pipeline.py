from pathlib import Path

import pytest

from source_lens_api.application.imports import FAILED, INTERRUPTED_ERROR_MESSAGE, ImportRequest
from source_lens_api.infra.qdrant.vector_store import QdrantLocalVectorStore

from .support import (
    FakeEmbeddingsClient,
    build_test_runtime,
    get_source_record,
    wait_for_job_status,
    write_minimal_pdf,
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


@pytest.mark.parametrize(
    ("file_name", "writer"),
    [
        ("notes.md", lambda path: write_text_fixture(path, "# Title\n\nMarkdown body text.")),
        (
            "notes.html",
            lambda path: write_text_fixture(
                path,
                "<html><body><h1>HTML title</h1><p>HTML body text.</p></body></html>",
            ),
        ),
        (
            "notes.htm",
            lambda path: write_text_fixture(
                path,
                "<html><body><p>Short HTML body.</p></body></html>",
            ),
        ),
        ("notes.pdf", lambda path: write_minimal_pdf(path, "PDF import text")),
    ],
)
def test_import_job_supports_all_phase3_non_txt_formats(
    tmp_path: Path,
    file_name: str,
    writer,
) -> None:
    runtime = build_test_runtime(tmp_path)
    runtime.initialize(start_worker=True)
    input_file = writer(tmp_path / file_name)

    try:
        submission = runtime.coordinator.submit_import(ImportRequest(path=str(input_file)))
        wait_for_job_status(runtime, submission.job_id, "completed")
        matches = runtime.vector_store.query(
            [10.0, 1.0, 1.0],
            limit=10,
            source_id=submission.source_id,
        )
    finally:
        runtime.shutdown()

    assert matches
    assert all(match.payload["source_id"] == submission.source_id for match in matches)
    assert all(
        isinstance(match.payload["text"], str) and match.payload["text"] for match in matches
    )


def test_import_job_marks_source_and_job_failed_when_parser_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = build_test_runtime(tmp_path)
    runtime.initialize(start_worker=True)
    input_file = write_text_fixture(tmp_path / "notes.txt", "Parser failure input")

    def fail_parser(_: Path) -> str:
        raise RuntimeError("Parser exploded")

    monkeypatch.setattr("source_lens_api.application.imports.extract_text_from_path", fail_parser)

    try:
        submission = runtime.coordinator.submit_import(ImportRequest(path=str(input_file)))
        wait_for_job_status(runtime, submission.job_id, FAILED)
        job = runtime.coordinator.get_job(submission.job_id)
        source = get_source_record(runtime, submission.source_id)
    finally:
        runtime.shutdown()

    assert job is not None
    assert job.error_message == "Parser exploded"
    assert source is not None
    assert source.import_status == FAILED


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


def test_folder_import_indexes_supported_files_as_one_source(tmp_path: Path) -> None:
    vector_store = QdrantLocalVectorStore(
        collection_name="source_lens_chunks",
        storage_path=tmp_path / "qdrant",
    )
    runtime = build_test_runtime(
        tmp_path,
        vector_store=vector_store,
    )
    runtime.initialize(start_worker=True)
    source_folder = tmp_path / "folder-source"
    write_text_fixture(source_folder / "alpha.md", "# Alpha\n\nAlpha evidence")
    write_text_fixture(source_folder / "nested" / "beta.txt", "Beta evidence")
    write_text_fixture(source_folder / "ignored.json", "{}")

    try:
        submission = runtime.coordinator.submit_import(ImportRequest(path=str(source_folder)))
        wait_for_job_status(runtime, submission.job_id, "completed")
        matches = vector_store.query([10.0, 1.0, 1.0], limit=10, source_id=submission.source_id)
    finally:
        runtime.shutdown()

    assert matches
    assert {match.payload["relative_path"] for match in matches} == {
        "alpha.md",
        "nested/beta.txt",
    }
    assert all(match.payload["source_id"] == submission.source_id for match in matches)


def test_folder_import_rejects_empty_folder(tmp_path: Path) -> None:
    runtime = build_test_runtime(tmp_path)
    runtime.initialize(start_worker=False)
    empty_folder = tmp_path / "empty"
    empty_folder.mkdir()

    try:
        with pytest.raises(ValueError, match="requires at least one supported file"):
            runtime.coordinator.submit_import(ImportRequest(path=str(empty_folder)))
    finally:
        runtime.shutdown()
