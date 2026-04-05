import sqlite3
from dataclasses import dataclass
from datetime import datetime

from ...domain.models import ImportJobRecord, SourceRecord
from ...domain.ports.import_job_repository import ImportJobRepositoryPort
from ...domain.ports.source_repository import SourceRepositoryPort


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


@dataclass
class SQLiteSourceRepository(SourceRepositoryPort):
    connection: sqlite3.Connection

    def create(self, record: SourceRecord) -> None:
        self.connection.execute(
            """
            INSERT INTO sources (
                id, name, description, source_type, original_path, snapshot_path,
                content_hash, import_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.name,
                record.description,
                record.source_type,
                record.original_path,
                record.snapshot_path,
                record.content_hash,
                record.import_status,
                _serialize_datetime(record.created_at),
                _serialize_datetime(record.updated_at),
            ),
        )
        self.connection.commit()

    def get_by_id(self, source_id: str) -> SourceRecord | None:
        row = self.connection.execute(
            "SELECT * FROM sources WHERE id = ?",
            (source_id,),
        ).fetchone()
        if row is None:
            return None

        return SourceRecord(
            id=str(row["id"]),
            name=str(row["name"]),
            description=str(row["description"]),
            source_type=str(row["source_type"]),
            original_path=str(row["original_path"]),
            snapshot_path=str(row["snapshot_path"]),
            content_hash=str(row["content_hash"]),
            import_status=str(row["import_status"]),
            created_at=_parse_datetime(str(row["created_at"])),
            updated_at=_parse_datetime(str(row["updated_at"])),
        )


@dataclass
class SQLiteImportJobRepository(ImportJobRepositoryPort):
    connection: sqlite3.Connection

    def create(self, record: ImportJobRecord) -> None:
        self.connection.execute(
            """
            INSERT INTO import_jobs (
                job_id, source_id, status, started_at, finished_at, error_message
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.job_id,
                record.source_id,
                record.status,
                _serialize_datetime(record.started_at),
                _serialize_datetime(record.finished_at),
                record.error_message,
            ),
        )
        self.connection.commit()

    def get_by_id(self, job_id: str) -> ImportJobRecord | None:
        row = self.connection.execute(
            "SELECT * FROM import_jobs WHERE job_id = ?",
            (job_id,),
        ).fetchone()
        if row is None:
            return None

        finished_at = row["finished_at"]
        error_message = row["error_message"]
        return ImportJobRecord(
            job_id=str(row["job_id"]),
            source_id=str(row["source_id"]),
            status=str(row["status"]),
            started_at=_parse_datetime(str(row["started_at"])),
            finished_at=_parse_datetime(str(finished_at)) if finished_at is not None else None,
            error_message=str(error_message) if error_message is not None else None,
        )
