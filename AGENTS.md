## Project

Source Lens is a local-first knowledge workspace for importing private sources and answering questions with grounded evidence.

## Source Of Truth

- `docs/afk-handoff.md` is the fastest pickup guide for a fresh session or new machine.
- `CONTEXT.md` defines the current architecture direction, stack, and domain vocabulary.
- `plan.md` defines the active MVP milestone, implementation rules, and done criteria.
- `README.md` defines product positioning and user-facing framing.
- Keep these docs aligned when naming, stack, scope, or milestone language changes.

## Locked Decisions

- Product name: `Source Lens`.
- Backend: Python.
- Frontend: React + TypeScript.
- Frontend toolchain: Vite.
- Model runtime: Ollama.
- Storage direction: PostgreSQL + pgvector.
- Keep metadata and retrieval concerns behind repository or adapter abstractions.
- MVP default: one selected source, local import, grounded QA, visible evidence.
- Do not hardcode vector dimensionality.

## Transitional Note

- Angular is not part of the active repo direction.
- Legacy SQLite and Qdrant adapters may still exist in the backend implementation, but they are transitional internals and should not drive new design or tracking decisions.

## How To Work

- Start non-trivial work with a short plan and explicit acceptance checks.
- Prefer small vertical slices over speculative framework work.
- If a mistake repeats, fix repo instructions or scripts instead of relying on chat memory.
- Keep instructions short; do not duplicate `CONTEXT.md` or `plan.md` here.

## Verification

- Every non-trivial task should include 3-5 concrete checks.
- Before scripts exist, checks may be doc, API-shape, or workflow based.
- After scripts exist, use deterministic commands as the default verification path.

Examples:
- Naming work: `Source Lens` is used consistently.
- Architecture work: `CONTEXT.md`, `plan.md`, and `README.md` do not contradict each other.
- Early backend work: one deterministic run path, one smoke check, one verification command.
- Frontend wiring work: one source-loading check, one grounded ask check, one handled not-ready or empty-state check.
- Feature work: one happy-path check, one failure or weak-evidence check.

## Commands

- Canonical commands exist at the repo root: `setup`, `dev`, `test`, `lint`, `typecheck`, `eval`, and the opt-in `live-deps` smoke check.
- Use the stable entrypoints in `tools/` instead of ad hoc local command sequences.

## Scope

- Default to the current MVP slice unless the task explicitly widens scope.
- Defer by default: multi-source querying, autonomous agents, MCP-heavy integration, broad connectors, and advanced ranking experiments.

## Review

- Review non-trivial code or architecture-doc diffs.
- Treat changes to naming, scope, architecture, dependencies, storage boundaries, ingestion, retrieval, or answer behavior as non-trivial.

## Agent skills

### Issue tracker

Issues and PRDs for this repo live in GitHub Issues for `bonyaroslav/SourceLens`. See `docs/agents/issue-tracker.md`.

### Triage labels

This repo uses the default triage label vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repo. See `docs/agents/domain.md`.
