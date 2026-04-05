from typing import Protocol

from ..models import ImportJobRecord


class ImportJobRepositoryPort(Protocol):
    def create(self, record: ImportJobRecord) -> None:
        ...

    def get_by_id(self, job_id: str) -> ImportJobRecord | None:
        ...

    def update_status(
        self,
        job_id: str,
        status: str,
        finished_at_iso: str | None,
        error_message: str | None,
    ) -> None:
        ...

    def list_by_statuses(self, statuses: list[str]) -> list[ImportJobRecord]:
        ...
