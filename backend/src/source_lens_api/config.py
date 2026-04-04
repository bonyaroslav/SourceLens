from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Source Lens API"
    environment: str = "local"

    model_config = SettingsConfigDict(
        env_prefix="SOURCE_LENS_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

