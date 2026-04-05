from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Source Lens API"
    environment: str = "local"
    ollama_base_url: str = "http://127.0.0.1:11434"
    chat_model: str = "qwen3:4b"
    embedding_model: str = "qwen3-embedding:0.6b"
    data_dir: Path = _repo_root() / ".local" / "source-lens"
    qdrant_collection: str = "source_lens_chunks"

    model_config = SettingsConfigDict(
        env_prefix="SOURCE_LENS_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
