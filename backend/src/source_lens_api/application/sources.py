from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from ..domain.models import SourceRecord, VectorMatch
from ..domain.ports.chat import ChatPort
from ..domain.ports.embeddings import EmbeddingsPort
from ..domain.ports.vector_store import VectorStorePort
from ..infra.sqlite.database import metadata_connection
from ..infra.sqlite.repositories import SQLiteSourceRepository
from .evidence import EvidenceSufficiencyGate

COMPLETED = "completed"
GROUNDED = "grounded"
INSUFFICIENT_EVIDENCE = "insufficient_evidence"
DEFAULT_RETRIEVAL_LIMIT = 5
INSUFFICIENT_EVIDENCE_ANSWER = (
    "I don't have enough evidence in this source to answer that question."
)


class SourceNotFoundError(ValueError):
    """Raised when a source cannot be found."""


class SourceNotReadyError(ValueError):
    """Raised when a source cannot yet be queried."""


class AskRequestError(ValueError):
    """Raised when an ask request is invalid."""


@dataclass(frozen=True)
class SourceView:
    id: str
    name: str
    description: str
    source_type: str
    import_status: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class EvidenceView:
    chunk_id: str
    chunk_index: int
    text: str
    score: float


@dataclass(frozen=True)
class AskResult:
    source_id: str
    question: str
    answer: str
    grounding_status: str
    evidence: list[EvidenceView]


@contextmanager
def _source_repository(metadata_db_path: Path) -> Iterator[SQLiteSourceRepository]:
    with metadata_connection(metadata_db_path) as connection:
        yield SQLiteSourceRepository(connection)


def _to_source_view(record: SourceRecord) -> SourceView:
    return SourceView(
        id=record.id,
        name=record.name,
        description=record.description,
        source_type=record.source_type,
        import_status=record.import_status,
        created_at=record.created_at.isoformat(),
        updated_at=record.updated_at.isoformat(),
    )


class SourceCatalogService:
    def __init__(self, metadata_db_path: Path) -> None:
        self._metadata_db_path = metadata_db_path

    def list_sources(self) -> list[SourceView]:
        with _source_repository(self._metadata_db_path) as repository:
            return [_to_source_view(record) for record in repository.list_all()]

    def get_source(self, source_id: str) -> SourceView:
        with _source_repository(self._metadata_db_path) as repository:
            record = repository.get_by_id(source_id)
        if record is None:
            raise SourceNotFoundError(f"Source not found: {source_id}")
        return _to_source_view(record)


class AskService:
    def __init__(
        self,
        *,
        metadata_db_path: Path,
        embeddings: EmbeddingsPort,
        chat: ChatPort,
        vector_store: VectorStorePort,
        evidence_gate: EvidenceSufficiencyGate | None = None,
        retrieval_limit: int = DEFAULT_RETRIEVAL_LIMIT,
    ) -> None:
        self._metadata_db_path = metadata_db_path
        self._embeddings = embeddings
        self._chat = chat
        self._vector_store = vector_store
        self._evidence_gate = evidence_gate or EvidenceSufficiencyGate()
        self._retrieval_limit = retrieval_limit

    def ask(self, *, source_id: str, question: str) -> AskResult:
        normalized_question = question.strip()
        if not normalized_question:
            raise AskRequestError("Question must not be empty.")

        with _source_repository(self._metadata_db_path) as repository:
            source = repository.get_by_id(source_id)
        if source is None:
            raise SourceNotFoundError(f"Source not found: {source_id}")
        if source.import_status != COMPLETED:
            raise SourceNotReadyError(
                f"Source {source_id} is not ready for questions. Current status: "
                f"{source.import_status}."
            )

        query_vector = self._embeddings.embed([normalized_question])[0]
        matches = self._vector_store.query(
            query_vector,
            limit=self._retrieval_limit,
            source_id=source_id,
        )
        evidence = self._build_evidence(matches)
        if not evidence or not self._evidence_gate.is_sufficient(
            question=normalized_question,
            evidence_texts=[item.text for item in evidence],
        ):
            return AskResult(
                source_id=source_id,
                question=normalized_question,
                answer=INSUFFICIENT_EVIDENCE_ANSWER,
                grounding_status=INSUFFICIENT_EVIDENCE,
                evidence=[],
            )

        answer = self._chat.generate(self._build_prompt(source, normalized_question, evidence))
        return AskResult(
            source_id=source_id,
            question=normalized_question,
            answer=answer.strip(),
            grounding_status=GROUNDED,
            evidence=evidence,
        )

    @staticmethod
    def _build_evidence(matches: list[VectorMatch]) -> list[EvidenceView]:
        evidence: list[EvidenceView] = []
        for match in matches:
            chunk_id = match.payload.get("chunk_id")
            chunk_index = match.payload.get("chunk_index")
            text = match.payload.get("text")
            if not isinstance(chunk_id, str) or not chunk_id.strip():
                continue
            if not isinstance(chunk_index, int):
                continue
            if not isinstance(text, str) or not text.strip():
                continue
            evidence.append(
                EvidenceView(
                    chunk_id=chunk_id,
                    chunk_index=chunk_index,
                    text=text.strip(),
                    score=float(match.score),
                )
            )
        return evidence

    @staticmethod
    def _build_prompt(
        source: SourceRecord,
        question: str,
        evidence: list[EvidenceView],
    ) -> str:
        evidence_blocks = "\n\n".join(
            (
                f"[{index}] chunk_id={item.chunk_id} chunk_index={item.chunk_index} "
                f"score={item.score:.4f}\n{item.text}"
            )
            for index, item in enumerate(evidence, start=1)
        )
        return (
            "You are answering questions about one imported source in Source Lens.\n"
            "Use only the evidence provided below.\n"
            "If the evidence is insufficient, say that you do not have enough evidence from "
            "the source.\n"
            "Do not mention any information outside the evidence.\n\n"
            f"Source name: {source.name}\n"
            f"Question: {question}\n\n"
            f"Evidence:\n{evidence_blocks}\n\n"
            "Answer:"
        )
