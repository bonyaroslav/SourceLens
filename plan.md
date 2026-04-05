# Project working concept

Build a **local-first knowledge workspace** that lets a user:

- import a knowledge source
- process and index it ahead of time
- select that source in the UI
- ask questions against that source
- receive grounded answers based on retrieved relevant content

The product direction is broader than “chat with a file”, but the first implementation should stay narrow and practical.

---

## Current intent

The current goal is to lock in a **practical MVP architecture** that can:

1. run fully on a local machine
2. avoid paid external AI services
3. stay reasonably compatible with future enterprise deployment constraints
4. deliver one real end-to-end workflow quickly

This document is now a **working architecture plan**, not just an open planning snapshot.

---

## Confirmed product goals

The system should support a workflow where a user can:

1. view a list of available knowledge sources
2. see basic metadata for each source:
  - name
  - description
3. open a selected source
4. ask questions about that source
5. receive answers generated from retrieved indexed content
6. inspect the retrieved evidence used for the answer

The first target scenarios are:

- project documents / notes
- science papers
- local code or exported code docs

---

## Locked high-level decisions

### Frontend

Use:

- Angular
- TypeScript

Frontend work should start only after the backend vertical slice works.

### Backend

Use:

- Python only

Reason:

- fastest path for local AI / RAG workflows
- easiest local experimentation
- simplest MVP architecture
- avoids unnecessary multi-runtime complexity

### Model serving

Use:

- **Ollama** as the local model service

Reason:

- local API
- simple setup for MVP
- avoids paid external APIs
- can run both embedding and chat models behind one local service

### Embeddings

Use:

- a local embedding model served via Ollama

Phase 2 bootstrap default:

- use **`qwen3-embedding:0.6b`** for the local dependency-proof phase

Why this default is locked for Phase 2:

- keeps the first local proof lightweight and faster to pull
- reduces RAM / VRAM pressure during early integration work
- is good enough to validate the embedding -> vector-store path
- stays deterministic when pinned to an exact tag

Reasonable later alternative:

- revisit a stronger embedding model such as **`qwen3-embedding:4b`** after Phase 2 if evals show the MVP needs better retrieval quality

Important principle:

- embedding dimension follows the selected model
- do not hardcode vector dimensionality as an architectural decision
- pin exact model tags instead of relying on `latest`
- treat the Phase 2 embedding model as a bootstrap default, not a permanent MVP quality lock

### Answer generation

Use:

- a separate local chat model via Ollama

Phase 2 bootstrap default:

- use **`qwen3:4b`** for the local dependency-proof phase

Why this default is locked for Phase 2:

- keeps setup cost and first-run latency lower than larger models
- is stronger than very small chat models for deterministic smoke prompts
- is sufficient to prove the local chat integration before product-quality tuning
- stays deterministic when pinned to an exact tag

Reasonable later alternative:

- revisit a stronger chat model such as **`qwen3:8b`** after Phase 2 if local hardware and evals support a quality-first upgrade

Important principle:

- **embedding model and answer model are separate concerns**
- do not use one model for every task by default
- pin exact model tags instead of relying on `latest`
- treat the Phase 2 chat model as a bootstrap default, not a permanent MVP quality lock

### Vector storage

Use:

- **Qdrant local mode** for MVP

Reason:

- simple local setup
- persistent local vector storage
- easy later upgrade path to server deployment if needed

### Metadata storage

Use:

- **SQLite** for MVP metadata storage
- a **repository / storage adapter abstraction** so metadata can later move to PostgreSQL or another store

Reason:

- lowest local resource overhead
- no separate database server process
- sufficient for single-user local metadata workloads
- keeps CPU and RAM available for embedding and chat models
- preserves a clean migration path to heavier database infrastructure later

### Scope control

The MVP should be intentionally narrow:

- one selected source at a time
- local file / folder import first
- grounded question answering
- evidence snippets shown with the answer

Everything else is secondary.

---

## MVP definition

### Included in MVP

#### 1. Source catalog

A user can:

- see stored sources
- open one source
- read name and description

#### 2. Local ingestion

Support first:

- local file import
- local folder import
- `.txt`
- `.md`
- `.pdf`
- `.html`
- `.htm`

Not required in MVP:

- GitHub import
- crawler behavior
- broad web import automation

#### 3. Processing pipeline

For imported content:

- create async import jobs
- snapshot imported content into managed workspace storage
- parse text
- chunk text
- generate embeddings through Ollama
- store chunks + metadata + vectors

#### 4. Retrieval

For a selected source:

- embed the user query
- retrieve top relevant chunks
- pass those chunks into the answer stage

#### 5. Grounded answer mode

The answer layer should:

- answer from retrieved evidence
- qualify uncertainty when evidence is weak
- expose supporting snippets in the UI / response payload

---

## Out of scope for MVP

Do **not** optimize for these now:

- multi-source querying
- advanced ranking experiments
- hybrid sparse+dense retrieval
- autonomous agents
- GitHub-specific import logic
- URL crawling depth
- background scheduling
- enterprise deployment automation
- .NET compatibility layers

These can be added later only after the core vertical slice works.

---

## Proposed MVP architecture

```text
Angular UI
   ↓
Python API
   ├─ source catalog
   ├─ import endpoint
   ├─ processing pipeline
   │   ├─ parser
   │   ├─ chunker
   │   ├─ embedding adapter (Ollama)
   │   └─ vector storage (Qdrant local)
   ├─ retrieval service
   └─ answer service
       ├─ query embedding via Ollama
       ├─ top-k retrieval from Qdrant
       └─ answer generation via Ollama chat model
```

---

## Core modules

### 1. Source registry

Stores:

- source id
- name
- description
- type
- import status
- original path
- snapshot path
- content hash
- timestamps

### 2. Import / processing

Responsibilities:

- accept file / folder input
- create async import job records
- copy source content into managed workspace storage
- extract text
- normalize content
- split into chunks
- attach metadata
- call Ollama embedding endpoint
- write results into Qdrant

### 3. Retrieval service

Responsibilities:

- embed the question
- filter by selected source
- retrieve top-k chunks
- return chunks and metadata

### 4. Answer service

Responsibilities:

- build grounded prompt
- send prompt + retrieved chunks to Ollama chat model
- return answer + evidence snippets

### 5. UI

Responsibilities:

- source list
- source details
- import action
- question input
- answer panel
- evidence panel

---

## Data shape to keep simple

### Source

- id
- name
- description
- source_type
- original_path
- snapshot_path
- content_hash
- import_status
- created_at
- updated_at

### Chunk

- chunk_id
- source_id
- text
- chunk_index
- path_or_origin
- token_estimate
- vector

### Query result

- answer
- grounding_status
- retrieved_chunks[]
- optional notes / uncertainty flag

### Import job

- job_id
- source_id
- status
- started_at
- finished_at
- error_message

---

## Enterprise compatibility direction

The MVP is local-first, but should avoid decisions that block later enterprise use.

### Keep compatible with future controlled environments

- no paid API dependency in core flow
- all inference through local Ollama service
- local vector storage
- metadata persistence behind an abstraction layer
- simple service boundaries
- clear configuration for model names and endpoints

### Expected enterprise-friendly posture later

- local-only model serving
- local or internal-network storage
- no confidential data sent to external model providers
- model names configurable through environment settings
- metadata backend replaceable with PostgreSQL or another managed store

This does **not** mean enterprise deployment should be implemented now.

---

## First vertical slice spec

The first slice should be **backend first** and prove one real workflow:

1. start the backend
2. import one local file by path
3. create an import job
4. parse, chunk, embed, and store it
5. ask one question against that source
6. return an answer plus evidence snippets

This is the smallest slice that proves the architecture is real. It also forces deterministic commands early and keeps UI work out of the critical path.

### First-slice boundaries

Keep the first slice narrow:

- backend only
- import one local file at a time
- import starts from a local filesystem path, not browser upload
- import is job-based and async from day 1
- query remains synchronous
- SQLite stores source and import-job metadata
- Qdrant stores chunk vectors and retrieval payload
- design must stay compatible with later folder import and UI work

Tradeoff:

- this moves fastest for backend proof
- folder import, browser upload, and UI are deferred even though they remain part of the MVP

### Phase 1: deterministic scaffold

Goal:

- remove setup guesswork before feature work begins

Build:

- Python project scaffold
- FastAPI app
- config loading
- health endpoint
- deterministic commands: `setup`, `dev`, `test`, `lint`, `typecheck`, `eval`

Why this order is good:

- it creates one stable way to run and verify the project
- it matches the rule to add deterministic scripts before serious prompting

Tradeoff:

- slightly more setup on day one
- less rework and less confusion after that

Acceptance checks:

- `setup` installs and prepares the backend locally
- `dev` starts the API
- `GET /health` returns success
- `test`, `lint`, and `typecheck` run even if they are minimal at first

### Phase 2: local dependency proof

Goal:

- prove the hard local dependencies before business logic hides failures

Execution note:

- use `phase-2-implementation-plan.md` as the repo-specific checklist for this phase

Build:

- Ollama embedding client using the local HTTP API
- Ollama chat client using the local HTTP API
- sync-first adapter interfaces for chat, embeddings, metadata, and vector storage
- SQLite connection and repository abstraction
- Qdrant local connection with on-disk persistence
- deterministic model bootstrap command
- smoke checks for each dependency

Locked Phase 2 decisions:

- use exact pinned model tags, not `latest`
- bootstrap defaults are `qwen3:4b` for chat and `qwen3-embedding:0.6b` for embeddings
- these model choices are for dependency proof and may be upgraded intentionally in later phases
- keep both defaults in the Qwen3 family for Phase 2 simplicity
- use sync-first adapters behind interfaces; do not overbuild async internals yet
- store local SQLite and Qdrant data in a repo-local ignored directory
- use Qdrant local mode, not Docker or Qdrant server mode, as the default path for this phase
- keep `GET /health` shallow; dependency proof belongs in deterministic commands and evals, not app boot

Implementation notes:

- add config for Ollama base URL, exact chat model, exact embedding model, and repo-local data directory
- add a dedicated model bootstrap script instead of folding model pulls into `setup`
- derive vector dimensionality from a real embedding response before creating the Qdrant collection
- create the Phase 3-aligned metadata schema early enough to prove the real repository path, not a throwaway smoke table

Why this order is good:

- failures are easier to isolate before the import pipeline exists
- the core stack is proven early instead of assumed
- the smallest live proof stays reproducible across machines and over time

Tradeoff:

- more plumbing before the first feature appears
- Phase 2 models optimize for integration reliability, not final answer quality

Acceptance checks:

- one embedding request succeeds against Ollama
- one chat request succeeds against Ollama
- one SQLite write and read succeeds through the repository layer
- one Qdrant insert and similarity query succeeds
- the exact pinned models can be pulled and verified through a deterministic command
- a collection created from the selected embedding model fails clearly if a later run tries to reuse it with a different dimension

### Phase 3: import pipeline v1

Goal:

- prove that one local file can become one queryable source

Build:

- `POST /sources/import` that accepts a local file path
- import job creation with status tracking
- source record creation
- source snapshot into managed workspace storage
- parser selection by file type
- text normalization and chunking
- embedding generation
- Qdrant upsert with source-scoped payload
- import job completion or failure state

Supported file types in this phase:

- `.txt`
- `.md`
- `.pdf`
- `.html`
- `.htm`

Why this order is good:

- it proves the local-first ingestion model in its simplest useful form
- supporting the MVP file types now avoids immediately reworking the parser surface

Tradeoff:

- file upload and folder import are deferred
- parser support adds work to the first slice

Acceptance checks:

- importing a valid local file creates a source record and a completed import job
- importing `.txt`, `.md`, `.pdf`, and `.html` or `.htm` each reaches parsed text and stored chunks
- a bad path fails cleanly and records an error
- source content is snapshotted before parsing
- chunks can be retrieved from Qdrant by source filter

### Phase 4: ask flow v1

Goal:

- complete the first real user value: ask about one source and see the evidence

Build:

- `GET /sources`
- `GET /sources/{source_id}`
- `POST /sources/{source_id}/ask`
- query embedding
- top-k retrieval filtered to one source
- grounded answer prompt
- response with answer, grounding status, and evidence snippets

Why this order is good:

- it closes the loop on the core product promise
- it keeps prompting and retrieval simple until the base flow works

Tradeoff:

- prompt design stays basic
- no multi-source or advanced retrieval yet

Acceptance checks:

- listing sources returns imported sources with basic metadata
- asking a question against an imported source returns an answer and snippets
- asking about a missing source returns a clear error
- weak retrieval produces a cautious answer or low-confidence grounding status
- retrieved evidence comes only from the selected source

### Phase 5: evaluation baseline

Goal:

- add a small but real quality loop as soon as the first slice works

Build:

- a small `eval` command for the first slice
- one golden-path sample source
- one expected-answer or expected-evidence smoke evaluation
- one weak-evidence evaluation

Why this order is good:

- it starts eval-driven development early without overbuilding a framework

Tradeoff:

- early evals will be simple and somewhat brittle
- they still create a real regression check

Acceptance checks:

- `eval` runs on a known sample source
- one check covers the happy path
- one check covers weak or missing evidence behavior

### Minimum first-slice interfaces

Commands to create in the first implementation:

- `setup`
- `dev`
- `test`
- `lint`
- `typecheck`
- `eval`

Minimum backend API:

- `GET /health`
- `POST /sources/import`
  - input: local file path
  - output: source id, import job id, initial status
- `GET /sources`
- `GET /sources/{source_id}`
- `POST /sources/{source_id}/ask`
  - input: question
  - output: answer, grounding status, evidence snippets

Storage boundary for this slice:

- SQLite stores source metadata and import-job metadata
- Qdrant stores chunk vectors plus retrieval payload needed for answering
- domain services must use repositories or adapters, not raw SQLite details

Tradeoff:

- chunk payload lives with vectors in the first slice instead of being fully normalized in SQLite

### Mandatory first-slice test scenarios

- backend boots from deterministic commands
- health endpoint works
- Ollama embed and chat calls both work
- SQLite and Qdrant are both proven independently
- import succeeds for each supported file type
- invalid import path fails clearly
- imported source appears in source listing
- ask flow returns answer plus evidence
- ask flow stays scoped to one selected source
- weak-evidence case returns cautious output
- `eval` runs at least one happy-path and one weak-evidence check

---

## Open decisions still allowed

These remain open, but they should not block MVP start:

- exact chunking strategy
- later upgrade from Phase 2 bootstrap models to stronger MVP defaults
- exact prompt format
- whether URL import enters MVP or phase 2
- whether citations are inline or panel-based in UI

---

## Locked implementation rules

### Storage rule

- keep vector retrieval in Qdrant
- keep metadata in SQLite for MVP
- all metadata access must go through a repository / adapter layer
- domain services must not depend directly on SQLite-specific details

### Import rule

- support `.txt`, `.md`, `.pdf`, `.html`, `.htm` in MVP
- treat HTML as text extraction, not browser rendering
- remove scripts, styles, and obvious navigation noise during extraction
- preserve title, headings, and origin metadata when available

### Execution rule

- import and indexing run as async jobs
- querying remains synchronous
- folder imports must support partial failure reporting

---

## Positioning statement

> A local-first AI workspace for importing, indexing, and exploring knowledge sources with grounded answers using local models.

---

## Planning rule going forward

For every new idea, ask:

1. does it help the first vertical slice work?
2. does it reduce complexity?
3. does it keep the architecture modular?

If not, defer it.
