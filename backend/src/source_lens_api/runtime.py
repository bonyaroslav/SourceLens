import queue
import threading
from dataclasses import dataclass

from .application.imports import ImportCoordinator, ImportWorkItem
from .bootstrap import RuntimePaths, ensure_runtime_directories, get_runtime_paths
from .config import Settings, get_settings
from .domain.ports.embeddings import EmbeddingsPort
from .domain.ports.vector_store import VectorStorePort
from .infra.ollama.client import OllamaEmbeddingsClient
from .infra.qdrant.vector_store import QdrantLocalVectorStore
from .infra.sqlite.database import metadata_connection


class ImportWorker:
    def __init__(
        self,
        coordinator: ImportCoordinator,
        work_queue: "queue.Queue[ImportWorkItem | None]",
    ) -> None:
        self._coordinator = coordinator
        self._work_queue = work_queue
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._run,
            name="source-lens-import-worker",
            daemon=True,
        )

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._work_queue.put(None)
        self._thread.join(timeout=5)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            item = self._work_queue.get()
            if item is None:
                self._work_queue.task_done()
                break
            try:
                self._coordinator.run_job(item)
            finally:
                self._work_queue.task_done()


@dataclass
class AppRuntime:
    settings: Settings
    paths: RuntimePaths
    coordinator: ImportCoordinator
    worker: ImportWorker
    vector_store: VectorStorePort
    _worker_started: bool = False

    def initialize(self, *, start_worker: bool) -> None:
        ensure_runtime_directories(self.paths)
        with metadata_connection(self.paths.metadata_db_path):
            pass
        self.coordinator.reconcile_interrupted_jobs()
        if start_worker and not self._worker_started:
            self.worker.start()
            self._worker_started = True

    def shutdown(self) -> None:
        if self._worker_started:
            self.worker.stop()
            self._worker_started = False
        close = getattr(self.vector_store, "close", None)
        if callable(close):
            close()


def build_runtime(
    *,
    settings: Settings | None = None,
    embeddings: EmbeddingsPort | None = None,
    vector_store: VectorStorePort | None = None,
) -> AppRuntime:
    resolved_settings = settings or get_settings()
    paths = get_runtime_paths(resolved_settings)
    work_queue: "queue.Queue[ImportWorkItem | None]" = queue.Queue()
    resolved_embeddings = embeddings or OllamaEmbeddingsClient(
        base_url=resolved_settings.ollama_base_url,
        model=resolved_settings.embedding_model,
    )
    resolved_vector_store = vector_store or QdrantLocalVectorStore(
        collection_name=resolved_settings.qdrant_collection,
        storage_path=paths.qdrant_dir,
    )
    coordinator = ImportCoordinator(
        metadata_db_path=paths.metadata_db_path,
        runtime_paths=paths,
        embeddings=resolved_embeddings,
        vector_store=resolved_vector_store,
        work_queue=work_queue,
    )
    return AppRuntime(
        settings=resolved_settings,
        paths=paths,
        coordinator=coordinator,
        worker=ImportWorker(coordinator=coordinator, work_queue=work_queue),
        vector_store=resolved_vector_store,
    )
