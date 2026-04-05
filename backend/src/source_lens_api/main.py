from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .application.imports import ImportRequest, ImportRequestError
from .runtime import AppRuntime, build_runtime


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


class ImportRequestBody(BaseModel):
    path: str
    name: str | None = None
    description: str | None = None


class ImportSubmissionResponse(BaseModel):
    source_id: str
    job_id: str
    status: str


class ImportJobResponse(BaseModel):
    job_id: str
    source_id: str
    status: str
    started_at: str
    finished_at: str | None
    error_message: str | None


def create_app(
    *,
    runtime: AppRuntime | None = None,
    start_worker: bool = True,
) -> FastAPI:
    resolved_runtime = runtime or build_runtime()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        resolved_runtime.initialize(start_worker=start_worker)
        app.state.runtime = resolved_runtime
        try:
            yield
        finally:
            resolved_runtime.shutdown()

    app = FastAPI(title=resolved_runtime.settings.app_name, lifespan=lifespan)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            app=resolved_runtime.settings.app_name,
            environment=resolved_runtime.settings.environment,
        )

    @app.post("/sources/import", response_model=ImportSubmissionResponse, status_code=202)
    def import_source(request: ImportRequestBody) -> ImportSubmissionResponse:
        try:
            submission = resolved_runtime.coordinator.submit_import(
                ImportRequest(
                    path=request.path,
                    name=request.name,
                    description=request.description,
                )
            )
        except ImportRequestError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return ImportSubmissionResponse(
            source_id=submission.source_id,
            job_id=submission.job_id,
            status=submission.status,
        )

    @app.get("/import-jobs/{job_id}", response_model=ImportJobResponse)
    def get_import_job(job_id: str) -> ImportJobResponse:
        job = resolved_runtime.coordinator.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"Import job not found: {job_id}")
        return ImportJobResponse(
            job_id=job.job_id,
            source_id=job.source_id,
            status=job.status,
            started_at=job.started_at.isoformat(),
            finished_at=job.finished_at.isoformat() if job.finished_at is not None else None,
            error_message=job.error_message,
        )

    return app


app = create_app()
