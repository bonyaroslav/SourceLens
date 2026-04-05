from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from source_lens_api.main import create_app

from .support import (
    FakeChatClient,
    build_test_runtime,
    create_source_record,
    wait_for_job_status,
    write_text_fixture,
)


def test_source_catalog_and_ask_flow_returns_grounded_answer_with_evidence(
    tmp_path: Path,
) -> None:
    chat = FakeChatClient(response="Grounded answer from fake chat.")
    runtime = build_test_runtime(tmp_path, chat=chat)
    first_file = write_text_fixture(tmp_path / "alpha.txt", "Alpha paragraph.")
    second_file = write_text_fixture(
        tmp_path / "beta.txt",
        "Beta paragraph one.\n\nBeta paragraph two with answer context.",
    )
    client = TestClient(create_app(runtime=runtime, start_worker=True))

    with client:
        first_import = client.post("/sources/import", json={"path": str(first_file)}).json()
        second_import = client.post("/sources/import", json={"path": str(second_file)}).json()
        wait_for_job_status(runtime, first_import["job_id"], "completed")
        wait_for_job_status(runtime, second_import["job_id"], "completed")

        sources_response = client.get("/sources")
        source_response = client.get(f"/sources/{second_import['source_id']}")
        ask_response = client.post(
            f"/sources/{second_import['source_id']}/ask",
            json={"question": "What does the beta source say?"},
        )

    assert sources_response.status_code == 200
    sources_payload = sources_response.json()
    assert [item["id"] for item in sources_payload] == [
        second_import["source_id"],
        first_import["source_id"],
    ]
    assert "original_path" not in sources_payload[0]
    assert "snapshot_path" not in sources_payload[0]

    assert source_response.status_code == 200
    assert source_response.json()["id"] == second_import["source_id"]
    assert "original_path" not in source_response.json()

    assert ask_response.status_code == 200
    ask_payload = ask_response.json()
    assert ask_payload["source_id"] == second_import["source_id"]
    assert ask_payload["grounding_status"] == "grounded"
    assert ask_payload["answer"] == "Grounded answer from fake chat."
    assert ask_payload["evidence"]
    assert all(item["chunk_id"] for item in ask_payload["evidence"])
    assert all("text" in item and item["text"] for item in ask_payload["evidence"])
    assert all("origin_path" not in item for item in ask_payload["evidence"])
    assert len(chat.prompts) == 1


def test_source_detail_and_ask_return_404_for_missing_source(tmp_path: Path) -> None:
    runtime = build_test_runtime(tmp_path)
    client = TestClient(create_app(runtime=runtime, start_worker=False))

    with client:
        detail_response = client.get("/sources/missing-source")
        ask_response = client.post(
            "/sources/missing-source/ask",
            json={"question": "What is here?"},
        )

    assert detail_response.status_code == 404
    assert ask_response.status_code == 404


@pytest.mark.parametrize("status", ["queued", "running", "failed"])
def test_ask_returns_409_when_source_is_not_ready(tmp_path: Path, status: str) -> None:
    runtime = build_test_runtime(tmp_path)
    client = TestClient(create_app(runtime=runtime, start_worker=False))

    with client:
        create_source_record(runtime, source_id=f"source-{status}", import_status=status)
        ask_response = client.post(
            f"/sources/source-{status}/ask",
            json={"question": "Can I ask now?"},
        )

    assert ask_response.status_code == 409
    assert status in ask_response.json()["detail"]


def test_ask_returns_insufficient_evidence_without_calling_chat(tmp_path: Path) -> None:
    chat = FakeChatClient(response="This should not be used.")
    runtime = build_test_runtime(tmp_path, chat=chat)
    client = TestClient(create_app(runtime=runtime, start_worker=False))

    with client:
        create_source_record(runtime, source_id="source-empty", import_status="completed")
        ask_response = client.post(
            "/sources/source-empty/ask",
            json={"question": "What evidence exists?"},
        )

    assert ask_response.status_code == 200
    assert ask_response.json() == {
        "source_id": "source-empty",
        "question": "What evidence exists?",
        "answer": "I don't have enough evidence in this source to answer that question.",
        "grounding_status": "insufficient_evidence",
        "evidence": [],
    }
    assert chat.prompts == []
