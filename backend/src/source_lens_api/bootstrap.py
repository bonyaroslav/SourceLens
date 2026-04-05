from dataclasses import dataclass
from pathlib import Path

from .config import Settings


@dataclass(frozen=True)
class RuntimePaths:
    data_dir: Path
    metadata_dir: Path
    metadata_db_path: Path
    qdrant_dir: Path
    snapshots_dir: Path


def get_runtime_paths(settings: Settings) -> RuntimePaths:
    metadata_dir = settings.data_dir / "metadata"
    return RuntimePaths(
        data_dir=settings.data_dir,
        metadata_dir=metadata_dir,
        metadata_db_path=metadata_dir / "source_lens.db",
        qdrant_dir=settings.data_dir / "qdrant",
        snapshots_dir=settings.data_dir / "snapshots",
    )


def ensure_runtime_directories(paths: RuntimePaths) -> RuntimePaths:
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    paths.metadata_dir.mkdir(parents=True, exist_ok=True)
    paths.qdrant_dir.mkdir(parents=True, exist_ok=True)
    paths.snapshots_dir.mkdir(parents=True, exist_ok=True)
    return paths
