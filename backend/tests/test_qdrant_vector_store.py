from pathlib import Path

import pytest

from source_lens_api.domain.models import VectorRecord
from source_lens_api.infra.qdrant.vector_store import (
    QdrantLocalVectorStore,
    VectorDimensionMismatchError,
)


def test_qdrant_query_can_be_scoped_to_a_single_source(tmp_path: Path) -> None:
    store = QdrantLocalVectorStore(
        collection_name="source_lens_chunks",
        storage_path=tmp_path / "qdrant",
    )
    store.ensure_collection(3)
    store.upsert(
        [
            VectorRecord(
                point_id="11111111-1111-1111-1111-111111111111",
                vector=[1.0, 0.0, 0.0],
                payload={"source_id": "source-a", "label": "a"},
            ),
            VectorRecord(
                point_id="22222222-2222-2222-2222-222222222222",
                vector=[1.0, 0.0, 0.0],
                payload={"source_id": "source-b", "label": "b"},
            ),
        ]
    )

    matches = store.query([1.0, 0.0, 0.0], limit=5, source_id="source-a")

    assert [match.point_id for match in matches] == ["11111111-1111-1111-1111-111111111111"]
    assert [match.payload["source_id"] for match in matches] == ["source-a"]


def test_qdrant_collection_dimension_mismatch_raises_clearly(tmp_path: Path) -> None:
    store = QdrantLocalVectorStore(
        collection_name="source_lens_chunks",
        storage_path=tmp_path / "qdrant",
    )
    store.ensure_collection(3)

    with pytest.raises(VectorDimensionMismatchError):
        store.ensure_collection(4)


def test_qdrant_upsert_requires_source_id_payload(tmp_path: Path) -> None:
    store = QdrantLocalVectorStore(
        collection_name="source_lens_chunks",
        storage_path=tmp_path / "qdrant",
    )
    store.ensure_collection(3)

    with pytest.raises(ValueError, match="source_id"):
        store.upsert(
            [
                VectorRecord(
                    point_id="33333333-3333-3333-3333-333333333333",
                    vector=[1.0, 0.0, 0.0],
                    payload={"label": "missing-source"},
                )
            ]
        )
