from pathlib import Path

from fastapi.testclient import TestClient

from source_lens_api.main import create_app

from .support import build_test_runtime, wait_for_job_status, write_text_fixture


def test_post_import_creates_snapshot_and_queued_job_before_background_execution(
    tmp_path: Path,
) -> None:
    runtime = build_test_runtime(tmp_path)
    input_file = write_text_fixture(tmp_path / "notes.txt", "Alpha\n\nBeta")
    client = TestClient(create_app(runtime=runtime, start_worker=False))

    with client:
        response = client.post("/sources/import", json={"path": str(input_file)})
        payload = response.json()

        snapshot_path = (
            runtime.paths.snapshots_dir / payload["source_id"] / input_file.with_suffix(".txt").name
        )
        if not snapshot_path.exists():
            snapshot_path = runtime.paths.snapshots_dir / payload["source_id"] / "source.txt"

        job_response = client.get(f"/import-jobs/{payload['job_id']}")

    assert response.status_code == 202
    assert payload["status"] == "queued"
    assert snapshot_path.exists()
    assert snapshot_path.read_text(encoding="utf-8") == "Alpha\n\nBeta"
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "queued"


def test_post_import_rejects_missing_or_unsupported_paths(tmp_path: Path) -> None:
    runtime = build_test_runtime(tmp_path)
    unsupported = write_text_fixture(tmp_path / "notes.json", "{}")
    client = TestClient(create_app(runtime=runtime, start_worker=False))

    with client:
        missing = client.post("/sources/import", json={"path": str(tmp_path / "missing.txt")})
        unsupported_response = client.post("/sources/import", json={"path": str(unsupported)})

    assert missing.status_code == 400
    assert "does not exist" in missing.json()["detail"]
    assert unsupported_response.status_code == 400
    assert "Unsupported file type" in unsupported_response.json()["detail"]


def test_import_job_endpoint_returns_completed_job_after_background_worker_runs(
    tmp_path: Path,
) -> None:
    runtime = build_test_runtime(tmp_path)
    input_file = write_text_fixture(tmp_path / "notes.txt", "Paragraph one.\n\nParagraph two.")
    client = TestClient(create_app(runtime=runtime, start_worker=True))

    with client:
        response = client.post("/sources/import", json={"path": str(input_file)})
        payload = response.json()
        wait_for_job_status(runtime, payload["job_id"], "completed")
        job_response = client.get(f"/import-jobs/{payload['job_id']}")

    assert response.status_code == 202
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "completed"
    assert job_response.json()["finished_at"] is not None
