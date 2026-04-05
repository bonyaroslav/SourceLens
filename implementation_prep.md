# Source Lens Implementation Prep

Updated: 2026-04-05

## Current status
- Phase 1 repo checks are passing on this machine.
- Python is installed and `py` works.
- Ollama is not installed yet, so Phase 2 is not ready to start.
- SQLite does not need a separate install.
- Qdrant server does not need a separate install because the project is locked to Qdrant local mode for MVP.

## Verified machine status
- `py --version` -> `Python 3.13.7`
- `py -0p` -> `3.13` at `C:\Users\bonya\AppData\Local\Programs\Python\Python313\python.exe`
- `ollama -v` -> not installed yet
- Disk free space observed:
  - `C:` about 923 GB free
  - `D:` about 392 GB free

## Phase 1 done criteria
Phase 1 is done only when all of the following are true:
- `./tools/setup.ps1` succeeds
- `./tools/dev.ps1` starts the API
- `GET http://127.0.0.1:8000/health` returns success
- `./tools/test.ps1` passes
- `./tools/lint.ps1` passes
- `./tools/typecheck.ps1` passes
- `./tools/eval.ps1` passes
- the run path is documented clearly enough to repeat in a fresh chat

## Phase 1 current result
Completed on this machine:
- `./tools/setup.ps1` -> passed
- `./tools/dev.ps1` + `/health` -> passed
- `./tools/test.ps1` -> passed
- `./tools/lint.ps1` -> passed
- `./tools/typecheck.ps1` -> passed
- `./tools/eval.ps1` -> passed

Health response:
```json
{"status":"ok","app":"Source Lens API","environment":"local"}
```

## Canonical local setup path
Use native Windows setup, not Docker.

Why:
- the repo already uses Windows PowerShell scripts
- `tools/setup.ps1` requires the `py` launcher
- SQLite is built into Python via `sqlite3`
- Qdrant local mode avoids a separate server for the MVP path
- native Ollama is the simplest local runtime for this repo

## Install steps before Phase 2
### 1. Python
Goal: satisfy the repo baseline in `backend/pyproject.toml` and the `py` launcher requirement in `tools/setup.ps1`.

Official sources:
- [Python 3.13 downloads](https://www.python.org/downloads/latest/python3.13/)
- [Using Python on Windows](https://docs.python.org/3/using/windows.html)

Micro steps:
1. Install Python 3.13 x64 on Windows.
2. Ensure the Python launcher is installed.
3. Open a new PowerShell window.
4. Run `py --version`.
5. Run `py -0p`.
6. If `py` is missing, fix Python installation before doing anything else.

### 2. Ollama
Goal: install the local model runtime needed for Phase 2 dependency proof.

Official sources:
- [Ollama Windows](https://docs.ollama.com/windows)
- [Ollama FAQ](https://docs.ollama.com/faq)

Micro steps:
1. Download and install Ollama for Windows.
2. Decide whether to keep model files in the default path or set `OLLAMA_MODELS` first.
3. Start Ollama.
4. Run `ollama -v`.
5. Open `http://localhost:11434` or test the local API once Ollama is running.
6. Do not choose final production models yet; Phase 2 only needs one chat-capable model and one embedding-capable model.

Current blocker:
- `ollama` is not currently installed on this machine.

### 3. SQLite
Goal: confirm that no extra install is required.

Official source:
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)

Rule:
- do not install a separate SQLite server
- use Python standard library `sqlite3`
- Phase 2 will prove one write/read through the repository abstraction

### 4. Qdrant
Goal: prepare vector storage without introducing a separate service too early.

Official sources:
- [Qdrant quickstart](https://qdrant.tech/documentation/quick-start/)
- [Qdrant local mode](https://python-client.qdrant.tech/qdrant_client.local.qdrant_local)

Rule:
- do not install Docker for Qdrant now
- do not run a separate Qdrant server now
- use Qdrant local mode in Phase 2
- Phase 2 will prove one local create, upsert, and similarity query cycle

### 5. Docker
Default decision:
- skip Docker for Phase 1 and Phase 2 preparation
- revisit only if the project later needs Qdrant server mode, containerized demos, or reproducible cross-machine packaging

## Exact Phase 1 run path
From repo root:
1. `./tools/setup.ps1`
2. `./tools/dev.ps1`
3. check `http://127.0.0.1:8000/health`
4. `./tools/test.ps1`
5. `./tools/lint.ps1`
6. `./tools/typecheck.ps1`
7. `./tools/eval.ps1`

Expected passing outputs currently observed:
- `setup` -> `Backend environment is ready.`
- `health` -> status `ok`
- `test` -> `1 passed`
- `lint` -> `All checks passed!`
- `typecheck` -> `0 errors, 0 warnings, 0 informations`
- `eval` -> `eval scaffold ready: Source Lens API [local]`

## Pre-Phase-2 entry criteria
Do not start the Phase 2 implementation slice until all of these are true:
- Python is installed and `py` works
- Ollama is installed and `ollama -v` works
- the model storage location decision is made if disk location matters
- it is clear that SQLite needs no separate install
- it is clear that Qdrant server is not needed for the current MVP path
- all Phase 1 commands pass on this machine

## Phase 2 prep checklist
Environment:
- Python present
- `py` present
- Ollama present
- enough disk space for at least one chat model and one embedding model
- no Docker dependency assumed

Repo:
- `tools/setup.ps1` works
- `tools/dev.ps1` works
- backend scaffold remains deterministic

Proofs to implement next:
- one Ollama embedding request succeeds
- one Ollama chat request succeeds
- one SQLite write/read succeeds through the repository abstraction
- one Qdrant local insert/query succeeds

## Canonical working rules
These are the repo habits to keep following.

1. Keep `AGENTS.md` small and durable.
- Benefit: stable repo rules persist across chats.
- If skipped: the same mistakes get re-explained repeatedly.

2. Use deterministic entrypoints.
- Benefit: `setup`, `dev`, `test`, `lint`, `typecheck`, and `eval` give one repeatable path.
- If skipped: every chat invents a different run procedure.

3. Start non-trivial work with a short plan and acceptance checks.
- Benefit: scope and done criteria stay explicit.
- If skipped: work drifts and verification becomes subjective.

4. Build one vertical slice before adding complexity.
- Benefit: the architecture is proven with a real workflow.
- If skipped: abstractions grow before the product promise is real.

5. Add evals early.
- Benefit: behavior regressions become visible.
- If skipped: quality depends on manual memory and ad hoc testing.

6. Create skills only after a workflow repeats.
- Benefit: skills encode real reusable work.
- If skipped: skills become unstable and speculative.

7. Prefer instruction-first skills.
- Benefit: skills stay small and reusable.
- If skipped: skills become heavyweight too early.

8. Keep context small.
- Benefit: higher signal and more reliable agent behavior.
- If skipped: prompt bloat makes the model less precise.

9. Review non-trivial diffs.
- Benefit: naming, scope, architecture, and storage boundaries stay aligned.
- If skipped: important regressions slip through.

## Candidate skills to revisit later
These are recommendations, not fixed commitments yet.
- `$implementation-strategy`
- `$code-change-verification`
- `$docs-alignment-check`
- `$local-stack-proof`
- `$vertical-slice-smoke`
- `$grounding-review`

## Next exact steps
1. Install Ollama from the official Windows page.
2. Verify `ollama -v` in a fresh shell.
3. Decide whether `OLLAMA_MODELS` should stay default or move to another drive.
4. Return to this repo and confirm the pre-Phase-2 entry criteria are fully satisfied.
5. Then write the detailed Phase 2 implementation plan.
