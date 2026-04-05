from datetime import UTC, datetime

from source_lens_api.domain.models import ImportJobRecord, SourceRecord
from source_lens_api.infra.sqlite.database import initialize_metadata_schema
from source_lens_api.infra.sqlite.repositories import (
    SQLiteImportJobRepository,
    SQLiteSourceRepository,
)


def test_sqlite_repositories_round_trip_records(sqlite_connection) -> None:
    initialize_metadata_schema(sqlite_connection)
    source_repository = SQLiteSourceRepository(sqlite_connection)
    import_job_repository = SQLiteImportJobRepository(sqlite_connection)
    timestamp = datetime.now(UTC)

    source_record = SourceRecord(
        id="source-1",
        name="Source Lens smoke source",
        description="Repository smoke test.",
        source_type="test",
        original_path="C:/input/source.md",
        snapshot_path="C:/snapshot/source.md",
        content_hash="abc123",
        import_status="completed",
        created_at=timestamp,
        updated_at=timestamp,
    )
    import_job_record = ImportJobRecord(
        job_id="job-1",
        source_id="source-1",
        status="completed",
        started_at=timestamp,
        finished_at=timestamp,
        error_message=None,
    )

    source_repository.create(source_record)
    import_job_repository.create(import_job_record)

    stored_source = source_repository.get_by_id("source-1")
    stored_job = import_job_repository.get_by_id("job-1")

    assert stored_source == source_record
    assert stored_job == import_job_record
