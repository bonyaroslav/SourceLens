import re
from collections.abc import Iterable

_TOKEN_PATTERN = re.compile(r"[a-z0-9]{4,}")
_STOPWORDS = {
    "about",
    "after",
    "against",
    "answer",
    "answers",
    "backend",
    "before",
    "being",
    "between",
    "could",
    "does",
    "enough",
    "evidence",
    "from",
    "have",
    "into",
    "local",
    "question",
    "questions",
    "really",
    "should",
    "source",
    "sources",
    "stored",
    "their",
    "there",
    "these",
    "this",
    "those",
    "through",
    "uses",
    "using",
    "what",
    "when",
    "where",
    "which",
    "without",
    "would",
    "your",
}


class EvidenceSufficiencyGate:
    def is_sufficient(self, *, question: str, evidence_texts: Iterable[str]) -> bool:
        question_tokens = _extract_content_tokens(question)
        if not question_tokens:
            return False

        for text in evidence_texts:
            if question_tokens.intersection(_extract_content_tokens(text)):
                return True
        return False


def _extract_content_tokens(text: str) -> set[str]:
    return {
        normalized
        for token in _TOKEN_PATTERN.findall(text.lower())
        if (normalized := _normalize_token(token)) not in _STOPWORDS
    }


def _normalize_token(token: str) -> str:
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("es") and len(token) > 5:
        return token[:-2]
    if token.endswith("s") and len(token) > 4:
        return token[:-1]
    return token
