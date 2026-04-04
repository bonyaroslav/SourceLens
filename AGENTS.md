## Project

Source Lens is a local-first knowledge workspace for importing private sources and answering questions with grounded evidence.

## Source Of Truth

- `plan.md` defines architecture, MVP scope, and locked implementation rules.
- `README.md` defines product positioning.
- Keep docs aligned when naming, stack, or scope changes.

## Locked Decisions

- Product name: `Source Lens`.
- Backend: Python.
- Frontend: Angular + TypeScript.
- Model runtime: Ollama.
- Vector storage: Qdrant local mode.
- Metadata storage: SQLite behind a repository or adapter abstraction.
- MVP default: one selected source, local import, grounded QA, visible evidence.
- Do not hardcode vector dimensionality.

## How To Work

- Start non-trivial work with a short plan and explicit acceptance checks.
- Prefer small vertical slices over speculative framework work.
- If a mistake repeats, fix repo instructions or scripts instead of relying on chat memory.
- Keep instructions short; do not duplicate `plan.md` here.

## Verification

- Every non-trivial task should include 3-5 concrete checks.
- Before scripts exist, checks may be doc, API-shape, or workflow based.
- After scripts exist, use deterministic commands as the default verification path.

Examples:
- Naming work: `Source Lens` is used consistently.
- Architecture work: `README.md` and `plan.md` do not contradict each other.
- Early backend work: one deterministic run path, one smoke check, one verification command.
- Feature work: one happy-path check, one failure or weak-evidence check.

## Commands

- Canonical commands do not exist yet.
- Early implementation should add stable `setup`, `dev`, `test`, `lint`, `typecheck`, and `eval` entrypoints.
- Add them in the first implementation scaffold or first real feature PR.
- After they exist, use them instead of ad hoc local command sequences.

## Scope

- Default to the current MVP slice unless the task explicitly widens scope.
- Defer by default: multi-source querying, autonomous agents, MCP-heavy integration, broad connectors, and advanced ranking experiments.

## Review

- Review non-trivial code or architecture-doc diffs.
- Treat changes to naming, scope, architecture, dependencies, storage boundaries, ingestion, retrieval, or answer behavior as non-trivial.
