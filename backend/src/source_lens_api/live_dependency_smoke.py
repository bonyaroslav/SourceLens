from .config import Settings, get_settings
from .infra.ollama.client import OllamaChatClient, OllamaEmbeddingsClient


def main() -> None:
    run_live_dependency_smoke(get_settings())


def run_live_dependency_smoke(settings: Settings) -> None:
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


if __name__ == "__main__":
    main()
