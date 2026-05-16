from source_lens_api.application.evidence import EvidenceSufficiencyGate


def test_evidence_gate_accepts_question_with_shared_content_token() -> None:
    gate = EvidenceSufficiencyGate()

    assert gate.is_sufficient(
        question="What vector store does the backend vertical slice use?",
        evidence_texts=["Source Lens uses Qdrant local mode for vectors."],
    )


def test_evidence_gate_rejects_unrelated_evidence_even_when_text_exists() -> None:
    gate = EvidenceSufficiencyGate()

    assert not gate.is_sufficient(
        question="What does the gamma source say about authentication?",
        evidence_texts=["Beta paragraph with import details and retrieval context."],
    )
