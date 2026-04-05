from typing import Protocol


class ChatPort(Protocol):
    def generate(self, prompt: str) -> str:
        ...
