from datetime import UTC, datetime
from uuid import uuid4

from .bootstrap import ensure_runtime_directories, get_runtime_paths
from .config import get_settings
from .domain.models import ImportJobRecord, SourceRecord, VectorRecord
from .infra.ollama.client import OllamaChatClient, OllamaEmbeddingsClient
from .infra.qdrant.vector_store import QdrantLocalVectorStore
from .infra.sqlite.database import connect_sqlite, initialize_metadata_schema
from .infra.sqlite.repositories import SQLiteImportJobRepository, SQLiteSourceRepository
from .main import create_app


def main() -> None:
    settings = get_settings()
    app = create_app()
    paths = ensure_runtime_directories(get_runtime_paths(settings))
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
        print("sqlite repository write/read: ok")

        embeddings_client = OllamaEmbeddingsClient(
            base_url=settings.ollama_base_url,
            model=settings.embedding_model,
        )
        embedding = embeddings_client.embed(["Source Lens Phase 2 dependency proof"])[0]
        if not embedding:
            raise RuntimeError("Embedding smoke check returned an empty vector.")
        print(f"ollama embedding: ok ({len(embedding)} dimensions)")

        vector_store = QdrantLocalVectorStore(
            collection_name=settings.qdrant_collection,
            storage_path=paths.qdrant_dir,
        )
        vector_store.ensure_collection(len(embedding))
        point_id = str(uuid4())
        vector_store.upsert(
            [
                VectorRecord(
                    point_id=point_id,
                    vector=embedding,
                    payload={"source_id": source_id, "label": "phase2-smoke"},
                )
            ]
        )
        matches = vector_store.query(embedding, limit=1)
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
    finally:
        connection.close()


if __name__ == "__main__":
    main()
