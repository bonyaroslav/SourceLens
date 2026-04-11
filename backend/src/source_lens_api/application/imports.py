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


@dataclass(frozen=True)
class ImportTarget:
    resolved_path: Path
    source_type: str
    files: list[Path]


@dataclass(frozen=True)
class PreparedChunk:
    chunk_id: str
    chunk_index: int
    text: str
    origin_path: str
    snapshot_path: str
    relative_path: str


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
        target = self._resolve_import_target(request.path)
        resolved_path = target.resolved_path
        source_id = str(uuid4())
        job_id = str(uuid4())
        snapshot_path = self._snapshot_path(
            source_id=source_id,
            source_type=target.source_type,
            original_path=resolved_path,
        )
        self._snapshot_import_target(target=target, snapshot_path=snapshot_path)
        content_hash = self._hash_snapshot(snapshot_path)
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
            source_type=target.source_type,
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
            self._cleanup_snapshot(snapshot_path)
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
            chunks = self._prepare_chunks(source=source, snapshot_path=snapshot_path)
            if not chunks:
                raise ImportRequestError("Imported content did not produce any indexable text.")

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
                        "origin_path": chunk.origin_path,
                        "snapshot_path": chunk.snapshot_path,
                        "relative_path": chunk.relative_path,
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

    def _resolve_import_target(self, raw_path: str) -> ImportTarget:
        path = Path(raw_path).expanduser()
        try:
            resolved_path = path.resolve(strict=True)
        except FileNotFoundError as error:
            raise ImportRequestError(f"File path does not exist: {raw_path}") from error

        if resolved_path.is_file():
            extension = resolved_path.suffix.lower()
            if extension not in SUPPORTED_EXTENSIONS:
                raise ImportRequestError(
                    "Unsupported file type. Supported extensions: "
                    + ", ".join(sorted(SUPPORTED_EXTENSIONS))
                )
            return ImportTarget(
                resolved_path=resolved_path,
                source_type="local_file",
                files=[resolved_path],
            )

        if resolved_path.is_dir():
            files = sorted(
                (
                    item
                    for item in resolved_path.rglob("*")
                    if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS
                ),
                key=lambda item: str(item.relative_to(resolved_path)).lower(),
            )
            if not files:
                raise ImportRequestError(
                    "Folder import requires at least one supported file. Supported extensions: "
                    + ", ".join(sorted(SUPPORTED_EXTENSIONS))
                )
            return ImportTarget(
                resolved_path=resolved_path,
                source_type="local_folder",
                files=files,
            )

        raise ImportRequestError(f"Import path must be a file or folder: {resolved_path}")

    def _snapshot_path(self, *, source_id: str, source_type: str, original_path: Path) -> Path:
        if source_type == "local_folder":
            return self._runtime_paths.snapshots_dir / source_id / "source"
        return (
            self._runtime_paths.snapshots_dir
            / source_id
            / f"source{original_path.suffix.lower()}"
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
        return digest.hexdigest()

    def _snapshot_import_target(self, *, target: ImportTarget, snapshot_path: Path) -> None:
        if target.source_type == "local_file":
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target.resolved_path, snapshot_path)
            return

        snapshot_path.mkdir(parents=True, exist_ok=True)
        for file_path in target.files:
            relative_path = file_path.relative_to(target.resolved_path)
            destination = snapshot_path / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, destination)

    def _hash_snapshot(self, snapshot_path: Path) -> str:
        if snapshot_path.is_file():
            return self._sha256(snapshot_path)

        digest = hashlib.sha256()
        for file_path in sorted(
            (path for path in snapshot_path.rglob("*") if path.is_file()),
            key=lambda item: str(item.relative_to(snapshot_path)).lower(),
        ):
            digest.update(str(file_path.relative_to(snapshot_path)).encode("utf-8"))
            with file_path.open("rb") as handle:
                for block in iter(lambda: handle.read(65536), b""):
                    digest.update(block)
        return digest.hexdigest()

    def _cleanup_snapshot(self, snapshot_path: Path) -> None:
        snapshot_root = snapshot_path if snapshot_path.is_dir() else snapshot_path.parent
        shutil.rmtree(snapshot_root, ignore_errors=True)

    def _prepare_chunks(self, *, source: SourceRecord, snapshot_path: Path) -> list[PreparedChunk]:
        if source.source_type == "local_folder":
            return self._prepare_folder_chunks(source=source, snapshot_path=snapshot_path)
        return self._prepare_file_chunks(
            source=source,
            source_path=Path(source.original_path),
            snapshot_path=snapshot_path,
            relative_path=Path(source.original_path).name,
            start_index=0,
        )

    def _prepare_folder_chunks(
        self,
        *,
        source: SourceRecord,
        snapshot_path: Path,
    ) -> list[PreparedChunk]:
        source_root = Path(source.original_path)
        prepared: list[PreparedChunk] = []
        next_index = 0
        for file_path in sorted(
            (path for path in snapshot_path.rglob("*") if path.is_file()),
            key=lambda item: str(item.relative_to(snapshot_path)).lower(),
        ):
            relative_path = str(file_path.relative_to(snapshot_path)).replace("\\", "/")
            original_file_path = source_root / Path(relative_path)
            file_chunks = self._prepare_file_chunks(
                source=source,
                source_path=original_file_path,
                snapshot_path=file_path,
                relative_path=relative_path,
                start_index=next_index,
            )
            prepared.extend(file_chunks)
            next_index += len(file_chunks)
        return prepared

    def _prepare_file_chunks(
        self,
        *,
        source: SourceRecord,
        source_path: Path,
        snapshot_path: Path,
        relative_path: str,
        start_index: int,
    ) -> list[PreparedChunk]:
        raw_text = extract_text_from_path(snapshot_path)
        normalized_text = normalize_text(raw_text)
        chunks = chunk_text(normalized_text, source_id=source.id)
        prepared: list[PreparedChunk] = []
        for offset, chunk in enumerate(chunks):
            chunk_index = start_index + offset
            prepared.append(
                PreparedChunk(
                    chunk_id=f"{source.id}:{chunk_index}",
                    chunk_index=chunk_index,
                    text=chunk.text,
                    origin_path=str(source_path),
                    snapshot_path=str(snapshot_path),
                    relative_path=relative_path,
                )
            )
        return prepared
