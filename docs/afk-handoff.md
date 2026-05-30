# AFK Handoff

## Purpose

Use this file as the fastest pickup guide for a fresh session or a new machine.

Read this file first, then read:

1. `AGENTS.md`
2. `CONTEXT.md`
3. `plan.md`
4. `README.md`
5. `docs/agents/issue-tracker.md`

## Current Direction

- Product: `Source Lens`
- Backend: Python
- Frontend direction: React + TypeScript
- Frontend toolchain direction: Vite
- Model runtime: Ollama
- Storage direction: PostgreSQL + pgvector
- MVP scope: one selected source, local import, grounded question answering, visible evidence
- Angular is removed from the active product direction
- Legacy SQLite and Qdrant adapters may still exist in the backend implementation, but they are transitional internals and not the target architecture

## Source Of Truth

- `CONTEXT.md` is the current architecture source of truth.
- `plan.md` is the active implementation milestone source of truth.
- `README.md` is the product-positioning source of truth.

If an older file, local code path, or issue still mentions Angular, SQLite, or Qdrant as the active direction, treat that as stale unless it is explicitly marked as legacy or transitional.

## Active Work Style

- Work sequentially for AFK execution.
- Do one issue at a time.
- Do one commit per issue.
- Verify before moving to the next issue.
- Respect `Blocked by` dependencies.
- Do not widen scope opportunistically.

## Preferred Issue State

- Keep only currently actionable work open in GitHub Issues.
- Close or archive stale Angular, SQLite, and Qdrant tracking so the queue reflects the active React path.
- Keep at most one implementation issue marked `ready-for-agent` at a time unless parallel execution is explicitly intended.

## Current Repo Reality

- The repo uses a React + TypeScript + Vite frontend workspace.
- The current frontend implementation is still shell-level and is not yet wired end to end to source loading and ask behavior.
- The backend currently keeps legacy SQLite and Qdrant adapters behind repository and vector-store boundaries.
- The docs treat PostgreSQL + pgvector as the target storage direction and the legacy adapters as transitional implementation detail.

## Known Blockers And Risks

- PowerShell script execution may require an execution-policy bypass on a new machine.
- Storage migration work has not landed yet, so new backend work should avoid deepening the legacy SQLite and Qdrant dependency surface.
- Do not assume the repo is ready for new requirements until docs, tracker state, and stale files are aligned.

## Preflight Checklist

Before starting the next implementation issue, confirm:

1. `AGENTS.md`, `CONTEXT.md`, `plan.md`, and `README.md` still agree.
2. The next issue is unblocked and is the only implementation issue marked `ready-for-agent`.
3. The local verification commands can run non-interactively on the current machine.
4. The working tree is clean before starting the next issue.
5. Acceptance checks and a deterministic verification path are present in the issue body.

## Suggested Next Steps

1. Keep the GitHub issue queue aligned with the current React direction.
2. Remove or archive stale repo files that still advertise old implementation plans.
3. Start the next requirement only after the repo docs and tracker describe one consistent state.

## Concise Prompt For A Fresh Session

Use this prompt on a new machine if needed:

```text
Work in C:\Projects\SourceLens.

Read docs/afk-handoff.md first, then AGENTS.md, CONTEXT.md, plan.md, README.md, and docs/agents/issue-tracker.md.

Treat CONTEXT.md as the architecture source of truth and plan.md as the active implementation milestone.
Follow React + TypeScript + Vite and PostgreSQL + pgvector.
Ignore stale Angular, SQLite, and Qdrant assumptions unless explicitly marked transitional or legacy.

Work AFK-style: one issue at a time, one commit per issue, verify before moving on, and respect Blocked by dependencies.

First assess readiness for the next issue, fix any blocking repo or issue-queue contradictions, then continue with the next unblocked issue in the active React chain.
```
