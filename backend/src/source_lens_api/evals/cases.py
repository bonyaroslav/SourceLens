from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    name: str
    question: str
    expected_grounding_status: str
    expected_evidence_substrings: tuple[str, ...] = ()
    require_non_empty_answer: bool = True
