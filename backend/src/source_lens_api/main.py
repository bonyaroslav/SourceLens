from fastapi import FastAPI
from pydantic import BaseModel

from .config import get_settings


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            app=settings.app_name,
            environment=settings.environment,
        )

    return app


app = create_app()

