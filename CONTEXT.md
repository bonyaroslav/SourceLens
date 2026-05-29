# Source Lens Context

## Product

Source Lens is a local-first knowledge workspace for importing private sources and answering questions with grounded evidence.

## Current MVP

- One selected source at a time
- Local file or folder import
- Grounded question answering
- Visible evidence snippets

## Core Concepts

- Source: an imported local file or folder that becomes queryable after indexing
- Import job: the queued or running workflow that snapshots, parses, chunks, embeds, and stores source data
- Chunk: a normalized slice of source text used for retrieval
- Evidence: retrieved chunk text shown to support an answer
- Embedding profile: the named model configuration used to generate chunk embeddings
- Grounded answer: an answer generated only from retrieved evidence
- Insufficient evidence: the explicit outcome when retrieved evidence does not support an answer

## Current Architectural Direction

- Backend runtime: Python
- Frontend: Angular + TypeScript
- Model runtime: Ollama
- Vector storage: Qdrant local mode
- Metadata storage: SQLite behind repository or adapter boundaries
- Retrieval and metadata concerns remain isolated behind vector store and repository boundaries
- Vector dimensionality must not be hardcoded

## Working Rules

- Prefer small vertical slices over speculative framework work
- Keep product scope inside the current MVP unless explicitly widened
- Preserve deterministic repo-level setup, development, and verification commands
