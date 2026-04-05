from dataclasses import dataclass

import httpx

from ...domain.ports.chat import ChatPort
from ...domain.ports.embeddings import EmbeddingsPort


class OllamaError(RuntimeError):
    """Raised when Ollama returns an invalid or unsuccessful response."""


@dataclass
class OllamaEmbeddingsClient(EmbeddingsPort):
    base_url: str
    model: str
    timeout_seconds: float = 60.0

    def embed(self, inputs: list[str]) -> list[list[float]]:
        try:
            response = httpx.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": inputs, "truncate": True},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            if error.response.status_code != 404:
                raise
            return self._embed_with_legacy_endpoint(inputs)

        payload = response.json()
        return _parse_embed_payload(payload)

    def _embed_with_legacy_endpoint(self, inputs: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for text in inputs:
            response = httpx.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            embedding = payload.get("embedding")
            if not isinstance(embedding, list) or not embedding:
                raise OllamaError("Ollama legacy embeddings response did not include an embedding.")
            embeddings.append([float(value) for value in embedding])

        return embeddings


@dataclass
class OllamaChatClient(ChatPort):
    base_url: str
    model: str
    timeout_seconds: float = 120.0

    def generate(self, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        generated_text = payload.get("response")
        if not isinstance(generated_text, str) or not generated_text.strip():
            raise OllamaError("Ollama generate response did not include response text.")

        return generated_text.strip()


def _parse_embed_payload(payload: object) -> list[list[float]]:
    if not isinstance(payload, dict):
        raise OllamaError("Ollama embed response payload was not a JSON object.")

    embeddings = payload.get("embeddings")
    if not isinstance(embeddings, list) or not embeddings:
        raise OllamaError("Ollama embed response did not include embeddings.")

    if not all(isinstance(item, list) and item for item in embeddings):
        raise OllamaError("Ollama embed response contained an invalid embeddings payload.")

    return [[float(value) for value in item] for item in embeddings]
