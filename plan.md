# Source Lens Backend Vertical Slice Plan

## Summary

`plan.md` is the forward-looking source of truth for the current milestone.

The current milestone is:

- finish the **backend vertical slice**
- keep the scope **backend-only**
- defer frontend work to the next milestone

This plan intentionally avoids shipped-history notes, phase retrospectives, and implementation logs.

## Locked Product Scope

The backend vertical slice for **Source Lens** includes:

- local-first knowledge workspace backend
- one selected source at a time
- local import from:
  - single file
  - folder
- supported formats:
  - `.txt`
  - `.md`
  - `.pdf`
  - `.html`
  - `.htm`
- async import job flow:
  - accept import
  - snapshot source content into managed storage
  - parse text
  - normalize text
  - chunk text
  - generate embeddings
  - store metadata and vectors
- source query flow:
  - list sources
  - get source detail
  - ask one question against one selected source
  - retrieve top evidence
  - generate grounded answer
  - return evidence snippets
- evaluation baseline:
  - one grounded golden-path check
  - one insufficient-evidence check

## Explicitly Out Of Scope

These are deferred until after the backend vertical slice is complete:

- Angular UI
- browser upload
- multi-source querying
- connector ecosystem
- crawling
- hybrid retrieval
- ranking experiments
- agent workflows
- OCR
- retry, cancel, delete, or resume import workflows
- enterprise deployment work

## Locked Architectural Decisions

- Product name: `Source Lens`
- Backend runtime: Python
- Frontend target for the next milestone: Angular + TypeScript
- Model runtime: Ollama
- Chat model default: `qwen3:4b`
- Embedding model default: `qwen3-embedding:0.6b`
- Model tags must be pinned and must not use `latest`
- Embedding and chat models are separate concerns
- Vector dimensionality must be derived from the active embedding model
- Vector storage: Qdrant local mode
- Metadata storage: SQLite behind repository/adapter abstractions
- Query scope: exactly one selected source at a time
- Import execution: async job-based
- Query execution: synchronous
- Local data root: repo-local ignored storage
- Chunk vectors and retrieval payload remain in Qdrant for this milestone
- Do not add a normalized chunk table in SQLite in this milestone
- `GET /health` stays shallow; dependency proof belongs in deterministic commands and evals

## Stable Interfaces

### Commands

These are the canonical local commands for the milestone:

- `.\tools\setup.ps1`
- `.\tools\dev.ps1`
- `.\tools\test.ps1`
- `.\tools\lint.ps1`
- `.\tools\typecheck.ps1`
- `.\tools\eval.ps1`

### API

The backend vertical slice exposes:

- `GET /health`
- `POST /sources/import`
- `GET /import-jobs/{job_id}`
- `GET /sources`
- `GET /sources/{source_id}`
- `POST /sources/{source_id}/ask`

### Storage Boundaries

- SQLite stores source metadata and import-job metadata
- Qdrant stores chunk vectors and retrieval payload used during answering
- Domain services must go through repository or adapter boundaries

## Definition Of Done

The backend vertical slice is done only when all of the following are true:

1. Deterministic commands exist and are the canonical way to run and verify the backend:
   - `setup`
   - `dev`
   - `test`
   - `lint`
   - `typecheck`
   - `eval`

2. The API surface is stable and implemented:
   - `GET /health`
   - `POST /sources/import`
   - `GET /import-jobs/{job_id}`
   - `GET /sources`
   - `GET /sources/{source_id}`
   - `POST /sources/{source_id}/ask`

3. Import supports both:
   - local file path
   - local folder path

4. Import behavior is complete for the locked file types:
   - `.txt`
   - `.md`
   - `.pdf`
   - `.html`
   - `.htm`

5. The import pipeline works end to end:
   - validates input
   - snapshots content before background processing
   - stores source metadata and import-job metadata in SQLite
   - parses and chunks supported content
   - embeds through Ollama
   - stores vectors in Qdrant
   - marks jobs and sources `queued`, `running`, `completed`, or `failed`
   - reconciles interrupted jobs on startup

6. The ask flow works end to end:
   - only queries one selected source
   - embeds the question
   - retrieves source-scoped evidence
   - builds a grounded prompt
   - returns answer plus evidence snippets
   - returns insufficient-evidence behavior when evidence is absent

7. Evaluation is real and repeatable:
   - `eval` checks one grounded happy path through the real import flow
   - `eval` checks one insufficient-evidence path
   - `eval` exits non-zero on failure

8. Docs are aligned:
   - `plan.md` reflects only the locked backend architecture and done criteria
   - `README.md` does not imply that frontend is part of the current milestone
   - `AGENTS.md` remains consistent with the narrowed milestone

## Acceptance Scenarios

### File Import

- valid `.txt` file imports successfully and becomes queryable
- unsupported file path fails before queueing work

### Folder Import

- folder with supported files imports successfully as one source
- empty folder fails clearly
- unsupported-only folder fails clearly

### Import Job Lifecycle

- queued job can be polled
- completed job has a finished timestamp
- parser or embedding failure marks both the job and source as failed
- interrupted queued or running jobs reconcile to failed on restart

### Ask Flow

- asking a completed source returns a grounded answer plus evidence
- asking a missing source returns a clear error
- asking a non-ready source returns a clear conflict or readiness error
- insufficient-evidence path returns the locked contract

### Eval

- grounded golden path passes on a repo-owned fixture
- insufficient-evidence case passes
- a broken expectation makes `eval` fail non-zero

## Next Step After This Milestone

After the backend vertical slice is complete:

- create a separate plan for the Angular UI milestone
- do not extend this file with frontend scope

## Planning Rule

For any new idea, ask:

1. does it finish the backend vertical slice?
2. does it keep the system simpler?
3. does it preserve clear storage and service boundaries?

If not, defer it.
