from typing import Protocol

from ..models import VectorMatch, VectorRecord


class VectorStorePort(Protocol):
    def ensure_collection(self, vector_size: int) -> None:
        ...

    def upsert(self, records: list[VectorRecord]) -> None:
        ...

    def query(self, query_vector: list[float], limit: int) -> list[VectorMatch]:
        ...
