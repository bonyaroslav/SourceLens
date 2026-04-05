import time
from pathlib import Path

from source_lens_api.bootstrap import get_runtime_paths
from source_lens_api.config import Settings
from source_lens_api.domain.models import VectorMatch, VectorRecord
from source_lens_api.domain.ports.embeddings import EmbeddingsPort
from source_lens_api.domain.ports.vector_store import VectorStorePort
from source_lens_api.runtime import AppRuntime, build_runtime


class FakeEmbeddingsClient(EmbeddingsPort):
    def __init__(self, *, error_message: str | None = None) -> None:
        self._error_message = error_message

    def embed(self, inputs: list[str]) -> list[list[float]]:
        if self._error_message is not None:
            raise RuntimeError(self._error_message)

        return [
            [float(len(text)), float(index + 1), float(sum(ord(char) for char in text) % 997)]
            for index, text in enumerate(inputs)
        ]


class InMemoryVectorStore(VectorStorePort):
    def __init__(self) -> None:
        self.vector_size: int | None = None
        self.records: list[VectorRecord] = []

    def ensure_collection(self, vector_size: int) -> None:
        if self.vector_size is None:
            self.vector_size = vector_size
            return
        if self.vector_size != vector_size:
            raise RuntimeError("Vector size mismatch")

    def upsert(self, records: list[VectorRecord]) -> None:
        self.records.extend(records)

    def query(
        self,
        query_vector: list[float],
        limit: int,
        source_id: str | None = None,
    ) -> list[VectorMatch]:
        filtered = [
            record
            for record in self.records
            if source_id is None or record.payload["source_id"] == source_id
        ]
        return [
            VectorMatch(point_id=record.point_id, score=1.0, payload=record.payload)
            for record in filtered[:limit]
        ]


def build_test_runtime(
    tmp_path: Path,
    *,
    embeddings: EmbeddingsPort | None = None,
    vector_store: VectorStorePort | None = None,
) -> AppRuntime:
    settings = Settings(data_dir=tmp_path / ".local" / "source-lens")
    return build_runtime(
        settings=settings,
        embeddings=embeddings or FakeEmbeddingsClient(),
        vector_store=vector_store or InMemoryVectorStore(),
    )


def metadata_db_path(runtime: AppRuntime) -> Path:
    return get_runtime_paths(runtime.settings).metadata_db_path


def wait_for_job_status(
    runtime: AppRuntime,
    job_id: str,
    expected_status: str,
    *,
    timeout_seconds: float = 5.0,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        job = runtime.coordinator.get_job(job_id)
        if job is not None and job.status == expected_status:
            return
        if job is not None and job.status == "failed" and expected_status != "failed":
            raise AssertionError(
                f"Job {job_id} failed while waiting for {expected_status}: {job.error_message}"
            )
        time.sleep(0.05)

    raise AssertionError(f"Timed out waiting for job {job_id} to reach status {expected_status}.")


def write_text_fixture(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def write_minimal_pdf(path: Path, text: str) -> Path:
    escaped_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT\n/F1 18 Tf\n72 100 Td\n({escaped_text}) Tj\nET\n".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
        ),
        f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("latin-1"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("latin-1")
    )

    path.write_bytes(bytes(pdf))
    return path
