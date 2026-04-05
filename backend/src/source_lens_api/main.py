from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .application.imports import ImportRequest, ImportRequestError
from .application.sources import AskRequestError, SourceNotFoundError, SourceNotReadyError
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


class SourceResponse(BaseModel):
    id: str
    name: str
    description: str
    source_type: str
    import_status: str
    created_at: str
    updated_at: str


class AskRequestBody(BaseModel):
    question: str = Field(min_length=1)


class EvidenceResponse(BaseModel):
    chunk_id: str
    chunk_index: int
    text: str
    score: float


class AskResponse(BaseModel):
    source_id: str
    question: str
    answer: str
    grounding_status: str
    evidence: list[EvidenceResponse]


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

    @app.get("/sources", response_model=list[SourceResponse])
    def list_sources() -> list[SourceResponse]:
        return [
            SourceResponse(
                id=source.id,
                name=source.name,
                description=source.description,
                source_type=source.source_type,
                import_status=source.import_status,
                created_at=source.created_at,
                updated_at=source.updated_at,
            )
            for source in resolved_runtime.catalog_service.list_sources()
        ]

    @app.get("/sources/{source_id}", response_model=SourceResponse)
    def get_source(source_id: str) -> SourceResponse:
        try:
            source = resolved_runtime.catalog_service.get_source(source_id)
        except SourceNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

        return SourceResponse(
            id=source.id,
            name=source.name,
            description=source.description,
            source_type=source.source_type,
            import_status=source.import_status,
            created_at=source.created_at,
            updated_at=source.updated_at,
        )

    @app.post("/sources/{source_id}/ask", response_model=AskResponse)
    def ask_source(source_id: str, request: AskRequestBody) -> AskResponse:
        try:
            result = resolved_runtime.ask_service.ask(
                source_id=source_id,
                question=request.question,
            )
        except AskRequestError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except SourceNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except SourceNotReadyError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

        return AskResponse(
            source_id=result.source_id,
            question=result.question,
            answer=result.answer,
            grounding_status=result.grounding_status,
            evidence=[
                EvidenceResponse(
                    chunk_id=item.chunk_id,
                    chunk_index=item.chunk_index,
                    text=item.text,
                    score=item.score,
                )
                for item in result.evidence
            ],
        )

    return app


app = create_app()
