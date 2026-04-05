from datetime import UTC, datetime
from uuid import uuid4

from .application.sources import GROUNDED, INSUFFICIENT_EVIDENCE
from .config import get_settings
from .domain.models import ImportJobRecord, SourceRecord, VectorRecord
from .infra.ollama.client import OllamaChatClient, OllamaEmbeddingsClient
from .infra.sqlite.database import connect_sqlite, initialize_metadata_schema
from .infra.sqlite.repositories import SQLiteImportJobRepository, SQLiteSourceRepository
from .main import create_app
from .runtime import build_runtime


def main() -> None:
    settings = get_settings()
    runtime = build_runtime(settings=settings)
    app = create_app(runtime=runtime, start_worker=False)
    runtime.initialize(start_worker=False)
    paths = runtime.paths
    print(f"eval scaffold ready: {settings.app_name} [{settings.environment}]")
    print(f"registered routes: {len(app.routes)}")
    print(f"data directory: {paths.data_dir}")

    connection = connect_sqlite(paths.metadata_db_path)
    try:
        initialize_metadata_schema(connection)
        source_repository = SQLiteSourceRepository(connection)
        import_job_repository = SQLiteImportJobRepository(connection)

        timestamp = datetime.now(UTC)
        source_id = str(uuid4())
        job_id = str(uuid4())
        source_record = SourceRecord(
            id=source_id,
            name="Phase 2 dependency proof",
            description="Minimal metadata repository smoke check.",
            source_type="phase2-smoke",
            original_path="phase2://smoke-source",
            snapshot_path="phase2://snapshot",
            content_hash="phase2-smoke-hash",
            import_status="completed",
            created_at=timestamp,
            updated_at=timestamp,
        )
        import_job_record = ImportJobRecord(
            job_id=job_id,
            source_id=source_id,
            status="completed",
            started_at=timestamp,
            finished_at=timestamp,
            error_message=None,
        )

        source_repository.create(source_record)
        import_job_repository.create(import_job_record)

        stored_source = source_repository.get_by_id(source_id)
        stored_job = import_job_repository.get_by_id(job_id)
        if stored_source is None or stored_job is None:
            raise RuntimeError("SQLite repository smoke check failed.")
        if not any(record.id == source_id for record in source_repository.list_all()):
            raise RuntimeError("SQLite source listing smoke check failed.")
        catalog_source = runtime.catalog_service.get_source(source_id)
        if catalog_source.id != source_id:
            raise RuntimeError("Source catalog smoke check failed.")
        print("sqlite repository write/read/list: ok")

        embeddings_client = OllamaEmbeddingsClient(
            base_url=settings.ollama_base_url,
            model=settings.embedding_model,
        )
        embedding = embeddings_client.embed(["Source Lens Phase 2 dependency proof"])[0]
        if not embedding:
            raise RuntimeError("Embedding smoke check returned an empty vector.")
        print(f"ollama embedding: ok ({len(embedding)} dimensions)")

        vector_store = runtime.vector_store
        vector_store.ensure_collection(len(embedding))
        point_id = str(uuid4())
        vector_store.upsert(
            [
                VectorRecord(
                    point_id=point_id,
                    vector=embedding,
                    payload={
                        "source_id": source_id,
                        "chunk_id": f"{source_id}:0",
                        "chunk_index": 0,
                        "text": "Source Lens dependency proof chunk for ask flow smoke testing.",
                    },
                )
            ]
        )
        matches = vector_store.query(embedding, limit=1, source_id=source_id)
        if not matches or matches[0].point_id != point_id:
            raise RuntimeError("Qdrant similarity query smoke check failed.")
        print(f"qdrant local insert/query: ok ({matches[0].score:.4f})")

        chat_client = OllamaChatClient(
            base_url=settings.ollama_base_url,
            model=settings.chat_model,
        )
        chat_response = chat_client.generate(
            "You are running a deterministic smoke test. "
            "Reply with exactly SOURCE_LENS_PHASE2_OK and nothing else."
        )
        if "SOURCE_LENS_PHASE2_OK" not in chat_response:
            raise RuntimeError(
                "Chat smoke check returned an unexpected response: "
                f"{chat_response!r}"
            )
        print("ollama chat: ok")

        ask_result = runtime.ask_service.ask(
            source_id=source_id,
            question="What is this source about?",
        )
        if ask_result.grounding_status != GROUNDED or not ask_result.evidence:
            raise RuntimeError("Ask flow grounded smoke check failed.")
        if not ask_result.answer.strip():
            raise RuntimeError("Ask flow returned an empty answer.")
        print("ask flow grounded answer: ok")

        empty_source_id = str(uuid4())
        empty_source = SourceRecord(
            id=empty_source_id,
            name="Phase 4 weak evidence proof",
            description="No vectors are stored for this source.",
            source_type="phase4-smoke",
            original_path="phase4://weak-source",
            snapshot_path="phase4://weak-snapshot",
            content_hash="phase4-weak-hash",
            import_status="completed",
            created_at=timestamp,
            updated_at=timestamp,
        )
        source_repository.create(empty_source)
        insufficient_result = runtime.ask_service.ask(
            source_id=empty_source_id,
            question="Can you answer without evidence?",
        )
        if (
            insufficient_result.grounding_status != INSUFFICIENT_EVIDENCE
            or insufficient_result.evidence
        ):
            raise RuntimeError("Ask flow insufficient-evidence smoke check failed.")
        print("ask flow insufficient evidence gate: ok")
    finally:
        connection.close()
        runtime.shutdown()


if __name__ == "__main__":
    main()
