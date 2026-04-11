import pytest

from source_lens_api.evals.assertions import (
    assert_eval_case,
    assert_expected_evidence_substrings,
)
from source_lens_api.evals.cases import EvalCase


def test_assert_eval_case_accepts_matching_grounded_case() -> None:
    case = EvalCase(
        name="grounded_case",
        question="Question?",
        expected_grounding_status="grounded",
        expected_evidence_substrings=("Qdrant local mode",),
    )

    assert_eval_case(
        case=case,
        grounding_status="grounded",
        answer="A non-empty answer",
        evidence_texts=["Source Lens uses Qdrant local mode for vectors."],
    )


def test_assert_expected_evidence_substrings_raises_clear_message() -> None:
    with pytest.raises(AssertionError, match="missing expected evidence substrings"):
        assert_expected_evidence_substrings(
            ["SQLite metadata repository"],
            ("Qdrant local mode",),
            case_name="missing_evidence_case",
        )
