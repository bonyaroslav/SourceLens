from typing import Protocol

from ..models import SourceRecord


class SourceRepositoryPort(Protocol):
    def create(self, record: SourceRecord) -> None:
        ...

    def get_by_id(self, source_id: str) -> SourceRecord | None:
        ...
