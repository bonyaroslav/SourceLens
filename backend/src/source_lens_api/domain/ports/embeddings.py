from typing import Protocol


class EmbeddingsPort(Protocol):
    def embed(self, inputs: list[str]) -> list[list[float]]:
        ...
