from pathlib import Path

from fastapi.testclient import TestClient

from source_lens_api.main import create_app

from .support import build_test_runtime


def test_health_endpoint_returns_ok(tmp_path: Path) -> None:
    client = TestClient(create_app(runtime=build_test_runtime(tmp_path), start_worker=False))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "Source Lens API",
        "environment": "local",
    }
