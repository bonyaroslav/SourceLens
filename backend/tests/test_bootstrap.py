from pathlib import Path

from source_lens_api.bootstrap import ensure_runtime_directories, get_runtime_paths
from source_lens_api.config import Settings


def test_runtime_paths_follow_configured_data_dir(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path / "source-lens-data")

    paths = get_runtime_paths(settings)

    assert paths.data_dir == tmp_path / "source-lens-data"
    assert paths.metadata_db_path == tmp_path / "source-lens-data" / "metadata" / "source_lens.db"
    assert paths.qdrant_dir == tmp_path / "source-lens-data" / "qdrant"


def test_runtime_directory_bootstrap_creates_expected_directories(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path / "source-lens-data")

    paths = ensure_runtime_directories(get_runtime_paths(settings))

    assert paths.data_dir.is_dir()
    assert paths.metadata_dir.is_dir()
    assert paths.qdrant_dir.is_dir()
