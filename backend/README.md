# Source Lens Backend

This backend scaffold is the first implementation slice for Source Lens.

Current scope:

- FastAPI application scaffold
- local config loading
- `GET /health`
- `POST /sources/import`
- `GET /import-jobs/{job_id}`
- `GET /sources`
- `GET /sources/{source_id}`
- `POST /sources/{source_id}/ask`
- request-time source snapshotting and queued local import jobs
- local file and folder import
- parser support for `.txt`, `.md`, `.pdf`, `.html`, and `.htm`
- source catalog reads from SQLite metadata
- ask flow retrieves source-scoped evidence from Qdrant and returns grounded answers
- eval runner with one grounded fixture case and one insufficient-evidence case
- deterministic PowerShell commands from the repo root
- repo-specific Phase 2 implementation plan in `..\phase-2-implementation-plan.md`

This is the backend-only milestone. Frontend work is intentionally deferred.

Windows-first commands from the repo root:

- `.\tools\setup.ps1`
- `.\tools\bootstrap-models.ps1`
- `.\tools\dev.ps1`
- `.\tools\test.ps1`
- `.\tools\lint.ps1`
- `.\tools\typecheck.ps1`
- `.\tools\eval.ps1`

`setup.ps1` bootstraps a repo-local helper environment for `uv` under `.tools\bootstrap` and then syncs the backend project dependencies.

`bootstrap-models.ps1` pulls the pinned Phase 2 Ollama chat and embedding models through the local Ollama HTTP API.

`eval.ps1` runs the grounded and insufficient-evidence backend eval cases with deterministic eval model doubles by default. Use `uv run --project backend python -m source_lens_api.eval_smoke --live-deps` when you also want live Ollama dependency proof.
