# Source Lens React MVP Workspace Plan

## Summary

`plan.md` defines the active MVP milestone and its locked implementation rules.

The current milestone is:

- establish the React MVP workspace
- preserve the shipped Python backend seam
- keep the scope to one selected source, grounded QA, and visible evidence

This plan intentionally avoids shipped-history notes, migration logs, and retrospective detail.

## Locked Product Scope

The current MVP milestone for **Source Lens** includes:

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
  - store metadata and retrieval data
- source query flow:
  - list sources
  - select one active source in the UI
  - ask one question against one selected source
  - retrieve top evidence
  - generate grounded answer
  - return evidence snippets
- React workspace flow:
  - load sources from `GET /sources`
  - surface loading, empty, and request-error states
  - block ask when the selected source is not ready
  - handle `409` source-not-ready ask failures
  - render the grounded answer and evidence snippets for the latest ask result
- evaluation baseline:
  - one grounded golden-path check
  - one insufficient-evidence check

## Explicitly Out Of Scope

These are deferred until after the current React MVP workspace milestone is complete:

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
- Frontend target: React + TypeScript
- Frontend toolchain: Vite
- Model runtime: Ollama
- Chat model default: `qwen3:4b`
- Embedding model default: `qwen3-embedding:0.6b`
- Model tags must be pinned and must not use `latest`
- Embedding and chat models are separate concerns
- Vector dimensionality must be derived from the active embedding model
- Storage direction: PostgreSQL + pgvector
- Metadata and retrieval boundaries remain isolated behind repository or adapter abstractions
- Query scope: exactly one selected source at a time
- Import execution: async job-based
- Query execution: synchronous
- Local data root: repo-local ignored storage
- `GET /health` stays shallow; dependency proof belongs in deterministic verification commands, with `eval` as the canonical regression gate and `live-deps` as the separate opt-in Ollama smoke check

## Transitional Implementation Note

- Angular is removed from the active repo direction.
- The current backend implementation still uses legacy SQLite and Qdrant adapters behind the locked boundaries.
- Until the storage migration is explicitly scheduled, new work should avoid deepening those legacy implementation details.

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

The backend slice exposed to the React workspace is:

- `GET /health`
- `POST /sources/import`
- `GET /import-jobs/{job_id}`
- `GET /sources`
- `GET /sources/{source_id}`
- `POST /sources/{source_id}/ask`

### Storage Boundaries

- Metadata persistence and retrieval persistence may share PostgreSQL, but they must remain isolated behind stable boundaries
- Embedding profile and vector shape rules must stay explicit
- Domain services must go through repository or adapter boundaries

## Definition Of Done

The current React MVP workspace milestone is done only when all of the following are true:

1. Deterministic commands exist and are the canonical way to run and verify the repo slice:
   - `setup`
   - `dev`
   - `test`
   - `lint`
   - `typecheck`
   - `eval`

2. The API surface remains stable and implemented:
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

5. The backend import pipeline works end to end:
   - validates input
   - snapshots content before background processing
   - stores source metadata and import-job metadata behind stable persistence boundaries
   - parses and chunks supported content
   - embeds through Ollama
   - stores retrieval data with explicit embedding-shape handling
   - marks jobs and sources `queued`, `running`, `completed`, or `failed`
   - reconciles interrupted jobs on startup

6. The ask flow works end to end:
   - only queries one selected source
   - embeds the question
   - retrieves source-scoped evidence
   - builds a grounded prompt
   - returns answer plus evidence snippets
   - returns insufficient-evidence behavior when evidence is absent

7. The React workspace is wired to the backend slice end to end:
   - source list loads from `GET /sources`
   - one active source can be selected in the UI
   - ask submits to `POST /sources/{source_id}/ask`
   - grounded answers render in the UI
   - evidence snippets render in the UI
   - loading, empty, error, and source-not-ready states are handled deliberately

8. Evaluation is real and repeatable:
   - `eval` checks one grounded happy path through the real import flow
   - `eval` checks one insufficient-evidence path
   - `eval` exits non-zero on failure
   - live Ollama dependency proof remains a separate opt-in smoke command, not part of the canonical `eval` gate

9. Docs are aligned:
   - `CONTEXT.md` reflects the current architecture direction
   - `plan.md` reflects the current React MVP milestone scope and done criteria
   - `README.md` describes the current frontend and backend direction without widening scope
   - `AGENTS.md` remains consistent with the current MVP slice

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

### React Workspace

- the source list shows loading while `GET /sources` is in flight
- an empty catalog shows a deliberate empty state
- a source-list request failure shows a deliberate error state
- selecting another source clears the previous ask result and evidence
- asking a completed source renders the latest answer and evidence snippets
- asking a source that becomes not-ready surfaces the handled `409` message

### Eval

- grounded golden path passes on a repo-owned fixture
- insufficient-evidence case passes
- a broken expectation makes `eval` fail non-zero

## Next Step After This Milestone

After the current React MVP workspace milestone is complete:

- evaluate the next MVP slice without widening beyond one selected source by default
- keep future plans separate from this file's locked milestone scope

## Planning Rule

For any new idea, ask:

1. does it finish the current React MVP workspace milestone?
2. does it keep the system simpler?
3. does it preserve clear storage and service boundaries?

If not, defer it.
