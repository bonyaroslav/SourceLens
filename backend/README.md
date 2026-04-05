# Source Lens Backend

This backend scaffold is the first implementation slice for Source Lens.

Current scope:

- FastAPI application scaffold
- local config loading
- `GET /health`
- deterministic PowerShell commands from the repo root
- repo-specific Phase 2 implementation plan in `..\phase-2-implementation-plan.md`

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
