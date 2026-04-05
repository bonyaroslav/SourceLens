from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SourceRecord:
    id: str
    name: str
    description: str
    source_type: str
    original_path: str
    snapshot_path: str
    content_hash: str
    import_status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ImportJobRecord:
    job_id: str
    source_id: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    error_message: str | None


@dataclass(frozen=True)
class VectorRecord:
    point_id: str
    vector: list[float]
    payload: dict[str, Any]


@dataclass(frozen=True)
class VectorMatch:
    point_id: str
    score: float
    payload: dict[str, Any]
