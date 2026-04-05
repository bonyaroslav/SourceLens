import hashlib
import queue
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid4, uuid5

from ..bootstrap import RuntimePaths
from ..domain.models import ImportJobRecord, SourceRecord, VectorRecord
from ..domain.ports.embeddings import EmbeddingsPort
from ..domain.ports.vector_store import VectorStorePort
from ..infra.sqlite.database import metadata_connection
from ..infra.sqlite.repositories import SQLiteImportJobRepository, SQLiteSourceRepository
from ..ingest.chunking import chunk_text
from ..ingest.parsing import SUPPORTED_EXTENSIONS, extract_text_from_path
from ..ingest.text import normalize_text

QUEUED = "queued"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"
INTERRUPTED_ERROR_MESSAGE = "Import interrupted because the application stopped before completion."


class ImportRequestError(ValueError):
    """Raised when an import request cannot be accepted."""


@dataclass(frozen=True)
class ImportRequest:
    path: str
    name: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class ImportSubmission:
    source_id: str
    job_id: str
    status: str


@dataclass(frozen=True)
class ImportWorkItem:
    source_id: str
    job_id: str


@dataclass(frozen=True)
class ImportJobView:
    job_id: str
    source_id: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    error_message: str | None


class ImportCoordinator:
    def __init__(
        self,
        metadata_db_path: Path,
        runtime_paths: RuntimePaths,
        embeddings: EmbeddingsPort,
        vector_store: VectorStorePort,
        work_queue: "queue.Queue[ImportWorkItem | None]",
    ) -> None:
        self._metadata_db_path = metadata_db_path
        self._runtime_paths = runtime_paths
        self._embeddings = embeddings
        self._vector_store = vector_store
        self._work_queue = work_queue

    @contextmanager
    def _metadata(self) -> Iterator[tuple[SQLiteSourceRepository, SQLiteImportJobRepository]]:
        with metadata_connection(self._metadata_db_path) as connection:
            yield SQLiteSourceRepository(connection), SQLiteImportJobRepository(connection)

    def submit_import(self, request: ImportRequest) -> ImportSubmission:
        resolved_path = self._resolve_import_path(request.path)
        source_id = str(uuid4())
        job_id = str(uuid4())
        snapshot_path = self._snapshot_path(
            source_id=source_id,
            extension=resolved_path.suffix.lower(),
        )
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(resolved_path, snapshot_path)
        content_hash = self._sha256(snapshot_path)
        timestamp = datetime.now(UTC)

        source_record = SourceRecord(
            id=source_id,
            name=(
                request.name.strip()
                if request.name and request.name.strip()
                else resolved_path.stem
            ),
            description=(
                request.description.strip()
                if request.description and request.description.strip()
                else f"Imported from {resolved_path}"
            ),
            source_type="local_file",
            original_path=str(resolved_path),
            snapshot_path=str(snapshot_path),
            content_hash=content_hash,
            import_status=QUEUED,
            created_at=timestamp,
            updated_at=timestamp,
        )
        job_record = ImportJobRecord(
            job_id=job_id,
            source_id=source_id,
            status=QUEUED,
            started_at=timestamp,
            finished_at=None,
            error_message=None,
        )

        try:
            with self._metadata() as (source_repository, import_job_repository):
                source_repository.create(source_record)
                import_job_repository.create(job_record)
        except Exception:
            shutil.rmtree(snapshot_path.parent, ignore_errors=True)
            raise

        self._work_queue.put(ImportWorkItem(source_id=source_id, job_id=job_id))
        return ImportSubmission(source_id=source_id, job_id=job_id, status=QUEUED)

    def get_job(self, job_id: str) -> ImportJobView | None:
        with self._metadata() as (_, import_job_repository):
            record = import_job_repository.get_by_id(job_id)
        if record is None:
            return None

        return ImportJobView(
            job_id=record.job_id,
            source_id=record.source_id,
            status=record.status,
            started_at=record.started_at,
            finished_at=record.finished_at,
            error_message=record.error_message,
        )

    def reconcile_interrupted_jobs(self) -> None:
        timestamp_iso = datetime.now(UTC).isoformat()
        with self._metadata() as (source_repository, import_job_repository):
            interrupted_jobs = import_job_repository.list_by_statuses([QUEUED, RUNNING])
            for job in interrupted_jobs:
                import_job_repository.update_status(
                    job_id=job.job_id,
                    status=FAILED,
                    finished_at_iso=timestamp_iso,
                    error_message=INTERRUPTED_ERROR_MESSAGE,
                )
                source_repository.update_import_status(
                    source_id=job.source_id,
                    import_status=FAILED,
                    updated_at_iso=timestamp_iso,
                )

    def run_job(self, work_item: ImportWorkItem) -> None:
        started_at_iso = datetime.now(UTC).isoformat()
        with self._metadata() as (source_repository, import_job_repository):
            source = source_repository.get_by_id(work_item.source_id)
            if source is None:
                import_job_repository.update_status(
                    job_id=work_item.job_id,
                    status=FAILED,
                    finished_at_iso=started_at_iso,
                    error_message="Source record was not found for the queued import job.",
                )
                return
            source_repository.update_import_status(
                source_id=source.id,
                import_status=RUNNING,
                updated_at_iso=started_at_iso,
            )
            import_job_repository.update_status(
                job_id=work_item.job_id,
                status=RUNNING,
                finished_at_iso=None,
                error_message=None,
            )

        try:
            snapshot_path = Path(source.snapshot_path)
            raw_text = extract_text_from_path(snapshot_path)
            normalized_text = normalize_text(raw_text)
            chunks = chunk_text(normalized_text, source_id=source.id)
            if not chunks:
                raise ImportRequestError("Imported file did not produce any indexable text.")

            embeddings = self._embeddings.embed([chunk.text for chunk in chunks])
            if len(embeddings) != len(chunks):
                raise RuntimeError("Embedding response count did not match the number of chunks.")

            self._vector_store.ensure_collection(len(embeddings[0]))
            records = [
                VectorRecord(
                    point_id=str(uuid5(NAMESPACE_URL, chunk.chunk_id)),
                    vector=embedding,
                    payload={
                        "source_id": source.id,
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text,
                        "origin_path": source.original_path,
                        "snapshot_path": source.snapshot_path,
                        "content_hash": source.content_hash,
                    },
                )
                for chunk, embedding in zip(chunks, embeddings, strict=True)
            ]
            self._vector_store.upsert(records)
        except Exception as error:
            self._mark_job_failed(
                job_id=work_item.job_id,
                source_id=work_item.source_id,
                error_message=str(error),
            )
            return

        completed_at_iso = datetime.now(UTC).isoformat()
        with self._metadata() as (source_repository, import_job_repository):
            source_repository.update_import_status(
                source_id=work_item.source_id,
                import_status=COMPLETED,
                updated_at_iso=completed_at_iso,
            )
            import_job_repository.update_status(
                job_id=work_item.job_id,
                status=COMPLETED,
                finished_at_iso=completed_at_iso,
                error_message=None,
            )

    def _mark_job_failed(self, job_id: str, source_id: str, error_message: str) -> None:
        finished_at_iso = datetime.now(UTC).isoformat()
        with self._metadata() as (source_repository, import_job_repository):
            source_repository.update_import_status(
                source_id=source_id,
                import_status=FAILED,
                updated_at_iso=finished_at_iso,
            )
            import_job_repository.update_status(
                job_id=job_id,
                status=FAILED,
                finished_at_iso=finished_at_iso,
                error_message=error_message[:1000],
            )

    def _resolve_import_path(self, raw_path: str) -> Path:
        path = Path(raw_path).expanduser()
        try:
            resolved_path = path.resolve(strict=True)
        except FileNotFoundError as error:
            raise ImportRequestError(f"File path does not exist: {raw_path}") from error

        if not resolved_path.is_file():
            raise ImportRequestError(f"Import path must be a file: {resolved_path}")

        extension = resolved_path.suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise ImportRequestError(
                "Unsupported file type. Supported extensions: "
                + ", ".join(sorted(SUPPORTED_EXTENSIONS))
            )

        return resolved_path

    def _snapshot_path(self, source_id: str, extension: str) -> Path:
        return self._runtime_paths.snapshots_dir / source_id / f"source{extension}"

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
        return digest.hexdigest()
