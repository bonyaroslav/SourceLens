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

## Preferred Issue Chain

The intended React implementation chain is:

1. `#16` Rewrite the repo source of truth for the React stack
2. `#17` Replace the Angular workspace with a Vite + React app shell
3. `#18` Deliver the routed React workspace with source list states
4. `#19` Add the React ask flow with grounded answer and evidence
5. `#20` Apply the light liquid-glass design system to the MVP workspace
6. `#21` Restore minimal happy-path verification for the React MVP

Conflicting issues such as `#8`, `#10`, and `#12` should not be treated as the active implementation path unless a human explicitly reactivates them.

## Current Repo Reality

- The docs now point to the React + PostgreSQL direction.
- The local frontend codebase is still transitional and still contains Angular tooling today.
- Frontend script names in `frontend/package.json` are still transitional.
- The GitHub issue queue may still need label cleanup so only one active issue is ready at a time.

## Known Blockers And Risks

- PowerShell script execution may require an execution-policy bypass on a new machine.
- Backend `test` and `typecheck` were previously blocked by a local Python executable access error in `backend/.venv`.
- Frontend lint currently reports formatting noise in the existing workspace.
- Do not assume the repo is fully AFK-ready until the execution path and issue labels are cleaned up.

## Preflight Checklist

Before starting the next implementation issue, confirm:

1. `AGENTS.md`, `CONTEXT.md`, `plan.md`, and `README.md` still agree.
2. The next issue is unblocked and is the only implementation issue marked `ready-for-agent`.
3. The local verification commands can run non-interactively on the current machine.
4. The working tree is clean before starting the next issue.
5. Acceptance checks and a deterministic verification path are present in the issue body.

## Suggested Next Steps

1. Clean the GitHub issue queue so only the React path remains active.
2. Fix the local unattended verification path.
3. Start with the first unblocked issue in the chain.

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
