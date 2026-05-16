from ..domain.ports.chat import ChatPort
from ..domain.ports.embeddings import EmbeddingsPort


class DeterministicEvalChatClient(ChatPort):
    def generate(self, prompt: str) -> str:
        del prompt
        return "Grounded answer from deterministic eval chat."


class DeterministicEvalEmbeddingsClient(EmbeddingsPort):
    def embed(self, inputs: list[str]) -> list[list[float]]:
        return [
            [float(len(text)), float(index + 1), float(sum(ord(char) for char in text) % 997)]
            for index, text in enumerate(inputs)
        ]
