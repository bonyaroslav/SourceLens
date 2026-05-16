from source_lens_api.config import Settings
from source_lens_api.live_dependency_smoke import run_live_dependency_smoke


def test_run_live_dependency_smoke_reports_embedding_and_chat(monkeypatch, capsys) -> None:
    class FakeEmbeddingsClient:
        def __init__(self, *, base_url: str, model: str) -> None:
            self.base_url = base_url
            self.model = model

        def embed(self, texts: list[str]) -> list[list[float]]:
            assert texts == ["Source Lens Phase 2 dependency proof"]
            return [[0.1, 0.2, 0.3]]

    class FakeChatClient:
        def __init__(self, *, base_url: str, model: str) -> None:
            self.base_url = base_url
            self.model = model

        def generate(self, prompt: str) -> str:
            assert "SOURCE_LENS_PHASE2_OK" in prompt
            return "SOURCE_LENS_PHASE2_OK"

    monkeypatch.setattr(
        "source_lens_api.live_dependency_smoke.OllamaEmbeddingsClient",
        FakeEmbeddingsClient,
    )
    monkeypatch.setattr(
        "source_lens_api.live_dependency_smoke.OllamaChatClient",
        FakeChatClient,
    )

    run_live_dependency_smoke(Settings())

    output = capsys.readouterr().out
    assert "ollama embedding: ok (3 dimensions)" in output
    assert "ollama chat: ok" in output
