# Phase 2 Implementation Plan

This file turns the locked Phase 2 architecture in `plan.md` into the next executable backend slice for this repo.

## Goal

Prove the local dependency stack end to end before building import and ask flows:

- Ollama embeddings
- Ollama chat
- SQLite through a repository boundary
- Qdrant local mode with on-disk persistence

This phase should leave the repo with deterministic commands and minimal production-shaped modules, not one-off smoke scripts.

## Scope

In scope:

- config for Ollama endpoints, pinned model names, and repo-local data paths
- sync-first adapter interfaces for embeddings, chat, metadata, and vector storage
- SQLite repository bootstrap with the first real schema for sources and import jobs
- Qdrant local bootstrap with collection creation based on observed embedding size
- deterministic model bootstrap and dependency smoke evaluation

Out of scope:

- import endpoints
- file parsing and chunking
- source query endpoints
- Angular work
- model quality tuning beyond the locked Phase 2 defaults

## Locked defaults for this repo

- chat model: `qwen3:4b`
- embedding model: `qwen3-embedding:0.6b`
- Ollama base URL: configurable, default local
- repo-local data root: `.local/source-lens/`
- SQLite path: `.local/source-lens/metadata/source_lens.db`
- Qdrant path: `.local/source-lens/qdrant/`
- collection name: config-driven, single collection for the first slice

Vector size must be derived from a real embedding response and must not be hardcoded.

## Ordered workstreams

### 1. Extend configuration and app wiring

Add settings for:

- `SOURCE_LENS_OLLAMA_BASE_URL`
- `SOURCE_LENS_CHAT_MODEL`
- `SOURCE_LENS_EMBEDDING_MODEL`
- `SOURCE_LENS_DATA_DIR`
- `SOURCE_LENS_QDRANT_COLLECTION`

Create one bootstrap path that ensures parent directories exist without making `GET /health` depend on Ollama, SQLite, or Qdrant availability.

### 2. Add domain ports and infra adapters

Add a small backend structure under `backend/src/source_lens_api/`:

- `domain/ports/embeddings.py`
- `domain/ports/chat.py`
- `domain/ports/source_repository.py`
- `domain/ports/import_job_repository.py`
- `domain/ports/vector_store.py`
- `infra/ollama/`
- `infra/sqlite/`
- `infra/qdrant/`

Keep adapters sync-first behind interfaces. Query-time async can wait until later phases.

### 3. Implement SQLite repository bootstrap

Create:

- one schema bootstrap function
- one SQLite connection factory
- repository implementations for source metadata and import jobs

Phase 2 only needs enough CRUD to prove the abstraction path:

- insert source
- get source by id
- insert import job
- get import job by id

Use production-shaped tables now so Phase 3 does not need a throwaway migration.

### 4. Implement Ollama and Qdrant proof path

Create:

- Ollama embedding client
- Ollama chat client
- Qdrant local adapter with collection bootstrap

Collection bootstrap rules:

- request one real embedding
- derive vector dimension from the response
- create the collection if it does not exist
- fail clearly if an existing collection dimension does not match the current embedding model

### 5. Add deterministic commands for Phase 2 proof

Add a new stable tool entrypoint:

- `.\tools\bootstrap-models.ps1`

Extend `eval` so it performs a deterministic dependency proof in this order:

1. verify config loading
2. verify SQLite repository write and read
3. verify Ollama embedding call
4. verify Qdrant insert and similarity query
5. verify Ollama chat call

Keep `GET /health` shallow. The deep proof belongs in `bootstrap-models.ps1` and `eval.ps1`.

## Suggested file targets

The implementation can stay small if it lands roughly here:

- `backend/src/source_lens_api/config.py`
- `backend/src/source_lens_api/main.py`
- `backend/src/source_lens_api/eval_smoke.py`
- `backend/src/source_lens_api/bootstrap.py`
- `backend/src/source_lens_api/domain/`
- `backend/src/source_lens_api/infra/`
- `backend/tests/`
- `tools/bootstrap-models.ps1`

## Acceptance checks

Phase 2 is complete when all of these are true:

1. `.\tools\bootstrap-models.ps1` pulls and verifies `qwen3:4b` and `qwen3-embedding:0.6b`.
2. `.\tools\eval.ps1` proves one SQLite write and read through repository interfaces.
3. `.\tools\eval.ps1` proves one Ollama embedding call and uses its returned dimension to bootstrap Qdrant.
4. `.\tools\eval.ps1` proves one Qdrant insert plus one similarity query against repo-local persisted storage.
5. `.\tools\eval.ps1` proves one Ollama chat call and exits non-zero on collection dimension mismatch.

## First review pass after implementation

Before calling Phase 2 done, review the diff for:

- hardcoded vector dimensions
- direct SQLite access from domain services
- hidden dependency checks in app startup
- model tags using `latest`
- repo-local data paths missing from `.gitignore`
