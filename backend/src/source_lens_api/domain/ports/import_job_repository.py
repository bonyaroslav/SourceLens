from typing import Protocol

from ..models import ImportJobRecord


class ImportJobRepositoryPort(Protocol):
    def create(self, record: ImportJobRecord) -> None:
        ...

    def get_by_id(self, job_id: str) -> ImportJobRecord | None:
        ...
