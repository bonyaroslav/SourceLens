from dataclasses import dataclass, field
from pathlib import Path

from qdrant_client import QdrantClient, models

from ...domain.models import VectorMatch, VectorRecord
from ...domain.ports.vector_store import VectorStorePort


class VectorDimensionMismatchError(RuntimeError):
    """Raised when an existing collection has a different vector size."""


def _extract_vector_size(
    vectors_config: models.VectorParams | dict[str, models.VectorParams],
) -> int:
    if isinstance(vectors_config, dict):
        first_config = next(iter(vectors_config.values()), None)
        if first_config is None:
            raise VectorDimensionMismatchError("Qdrant collection is missing vector configuration.")
        return int(first_config.size)

    return int(vectors_config.size)


def _source_filter(source_id: str | None) -> models.Filter | None:
    if source_id is None:
        return None

    return models.Filter(
        must=[
            models.FieldCondition(
                key="source_id",
                match=models.MatchValue(value=source_id),
            )
        ]
    )


@dataclass
class QdrantLocalVectorStore(VectorStorePort):
    collection_name: str
    storage_path: Path
    _client: QdrantClient | None = field(init=False, default=None, repr=False)

    def _get_client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(path=str(self.storage_path))
        return self._client

    def ensure_collection(self, vector_size: int) -> None:
        client = self._get_client()
        if client.collection_exists(collection_name=self.collection_name):
            collection = client.get_collection(collection_name=self.collection_name)
            vectors_config = collection.config.params.vectors
            if vectors_config is None:
                raise VectorDimensionMismatchError(
                    "Qdrant collection is missing vector configuration."
                )
            existing_size = _extract_vector_size(vectors_config)
            if existing_size != vector_size:
                raise VectorDimensionMismatchError(
                    "Existing Qdrant collection vector size does not match "
                    "the active embedding model: "
                    f"expected {existing_size}, got {vector_size}."
                )
            return

        client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )

    def upsert(self, records: list[VectorRecord]) -> None:
        for record in records:
            if "source_id" not in record.payload:
                raise ValueError("VectorRecord payload must include source_id.")

        self._get_client().upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=record.point_id,
                    vector=record.vector,
                    payload=record.payload,
                )
                for record in records
            ],
        )

    def query(
        self,
        query_vector: list[float],
        limit: int,
        source_id: str | None = None,
    ) -> list[VectorMatch]:
        response = self._get_client().query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=_source_filter(source_id),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return [
            VectorMatch(
                point_id=str(point.id),
                score=float(point.score),
                payload=dict(point.payload or {}),
            )
            for point in response.points
        ]

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
