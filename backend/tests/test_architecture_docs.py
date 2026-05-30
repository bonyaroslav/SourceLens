from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def read_repo_doc(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


def assert_legacy_storage_is_not_presented_as_active(doc: str) -> None:
    if "SQLite" in doc or "Qdrant" in doc:
        assert "legacy" in doc.lower()
        assert "transitional" in doc.lower()


def test_context_matches_locked_mvp_architecture() -> None:
    context = read_repo_doc("CONTEXT.md")

    assert "Frontend: React + TypeScript" in context
    assert "Frontend toolchain: Vite" in context
    assert "Model runtime: Ollama" in context
    assert "Storage direction: PostgreSQL + pgvector" in context
    assert_legacy_storage_is_not_presented_as_active(context)


def test_context_keeps_current_mvp_scope_language() -> None:
    context = read_repo_doc("CONTEXT.md")

    assert "One selected source at a time" in context
    assert "Grounded question answering" in context
    assert "Visible evidence snippets" in context


def test_repo_architecture_docs_do_not_conflict_on_locked_stack() -> None:
    plan = read_repo_doc("plan.md")
    agents = read_repo_doc("AGENTS.md")
    readme = read_repo_doc("README.md")

    for doc in (plan, agents, readme):
        assert "React" in doc
        assert "Vite" in doc
        assert "Ollama" in doc
        assert "PostgreSQL + pgvector" in doc
        assert "Qdrant local mode" not in doc
        assert_legacy_storage_is_not_presented_as_active(doc)
