from .cases import EvalCase


def assert_grounding_status(actual_status: str, expected_status: str, *, case_name: str) -> None:
    if actual_status != expected_status:
        raise AssertionError(
            f"[{case_name}] expected grounding_status={expected_status!r}, "
            f"got {actual_status!r}"
        )


def assert_non_empty_answer(answer: str, *, case_name: str) -> None:
    if not answer.strip():
        raise AssertionError(f"[{case_name}] answer must not be empty")


def assert_expected_evidence_substrings(
    evidence_texts: list[str],
    expected_substrings: tuple[str, ...],
    *,
    case_name: str,
) -> None:
    combined = "\n".join(evidence_texts)
    missing = [substring for substring in expected_substrings if substring not in combined]
    if missing:
        raise AssertionError(
            f"[{case_name}] missing expected evidence substrings: {missing}"
        )


def assert_eval_case(
    *,
    case: EvalCase,
    grounding_status: str,
    answer: str,
    evidence_texts: list[str],
) -> None:
    assert_grounding_status(
        grounding_status,
        case.expected_grounding_status,
        case_name=case.name,
    )
    if case.require_non_empty_answer:
        assert_non_empty_answer(answer, case_name=case.name)
    assert_expected_evidence_substrings(
        evidence_texts,
        case.expected_evidence_substrings,
        case_name=case.name,
    )
