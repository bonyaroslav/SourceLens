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

Working default:

- start with **Qwen3 Embedding** via Ollama if practical in local setup

Important principle:

- embedding dimension follows the selected model
- do not hardcode vector dimensionality as an architectural decision

### Answer generation

Use:

- a separate local chat model via Ollama

Important principle:

- **embedding model and answer model are separate concerns**
- do not use one model for every task by default

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

## Immediate implementation priorities

Build in this order:

1. **backend skeleton**
  - FastAPI app
  - health endpoint
  - config
  - metadata repository abstraction
2. **Ollama integration**
  - verify local embed call works
  - verify local chat call works
3. **SQLite metadata integration**
  - define source and import-job tables
  - implement repository interfaces
4. **Qdrant local integration**
  - create collection
  - insert test vectors
  - run similarity search
5. **file ingestion vertical slice**
  - import one text or html file
  - create import job
  - snapshot source
  - chunk it
  - embed chunks
  - store chunks
6. **ask endpoint**
  - accept source id + question
  - retrieve top chunks
  - generate grounded answer
  - return snippets
7. **minimal UI**
  - source list
  - source detail page
  - ask question
  - show answer + snippets

Only after this works should more features be added.

---

## Very short setup path

1. install Python environment
2. install Ollama
3. pull one embedding model and one chat model
4. install backend dependencies
5. add SQLite metadata layer
6. add Qdrant local dependency
7. create one import script for a text or html file
8. create one ask script / endpoint
9. test the full flow on one document

---

## Open decisions still allowed

These remain open, but they should not block MVP start:

- exact chunking strategy
- exact chat model choice
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
