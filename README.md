<div align="center">

# Source Lens Knowledge Workspace

**A local-first AI workspace for turning private knowledge into grounded answers, evidence, and reusable insight.**

<p>
  <img alt="Local First" src="https://img.shields.io/badge/Local--First-Private%20by%20Default-111827">
  <img alt="Runtime" src="https://img.shields.io/badge/Runtime-Ollama-7C3AED">
  <img alt="Retrieval" src="https://img.shields.io/badge/RAG-Grounded%20Answers-0F766E">
  <img alt="Evidence" src="https://img.shields.io/badge/UX-Evidence%20Visible-1D4ED8">
  <img alt="Status" src="https://img.shields.io/badge/Status-MVP%20Building-0A7EA4">
</p>

<p>
  <strong>Import knowledge. Index it once. Ask sharper questions forever.</strong>
</p>

<p>
  Built for documents, notes, research, and code-related knowledge that should stay under your control.
</p>

</div>

---

## Why this exists

Most AI tools still feel like generic chat wrapped around vague context.

**Source Lens** is designed as a **knowledge workspace**, not just a chatbot:
- bring in a source
- process and index it locally
- ask questions against that source
- get answers grounded in retrieved evidence
- evolve toward a private internal AI assistant without depending on paid external inference

The goal is simple: make private knowledge feel searchable, explainable, and actually useful.

---

## Core experience

### 1. Source-aware exploration
Choose a knowledge source and ask focused questions against it instead of throwing everything into one giant context window.

### 2. Grounded answers
Retrieve the most relevant chunks first, then generate the answer from evidence instead of free-form guessing.

### 3. Evidence you can inspect
Surface the supporting snippets so the user can validate why the answer was produced.

### 4. Local-first runtime
Run the core AI workflow locally through **Ollama**, with local indexing and retrieval as the default posture.

### 5. Enterprise-friendly direction
Keep the architecture compatible with controlled environments where external APIs may be restricted or forbidden.

---

## What makes it feel powerful

<table>
  <tr>
    <td valign="top" width="50%">
      <h3>Grounded Question Answering</h3>
      <p>Ask questions about one selected source and get answers built from retrieved evidence, not generic model improvisation.</p>
    </td>
    <td valign="top" width="50%">
      <h3>Evidence Panel</h3>
      <p>See the exact snippets behind the answer to improve trust, debugging, and source awareness.</p>
    </td>
  </tr>
  <tr>
    <td valign="top" width="50%">
      <h3>Reusable Knowledge Index</h3>
      <p>Import once, query many times. Turn raw files and notes into a persistent private retrieval layer.</p>
    </td>
    <td valign="top" width="50%">
      <h3>Local AI by Default</h3>
      <p>Keep inference and retrieval close to the data when privacy, cost control, or enterprise constraints matter.</p>
    </td>
  </tr>
</table>

---

## Demo scenarios

### Project Knowledge Assistant
Import project notes, architecture docs, exported tickets, and technical writeups.

Ask things like:
- What are the main risks in this project?
- Which decisions were made about authentication?
- What unresolved questions still exist?

### Research Navigator
Import papers, articles, or structured notes.

Ask things like:
- What are the major claims across these sources?
- Compare methods and limitations.
- Which findings are weakly supported?

### Codebase Companion
Import code-adjacent documentation, exported repo summaries, or design notes.

Ask things like:
- Where is authentication handled?
- What modules look tightly coupled?
- What operational risks are implied by the current design?

---

## MVP scope

### In progress now
- source catalog
- local file and folder import
- initial support for txt / md / pdf / html
- text parsing and chunking
- embedding-based retrieval
- grounded answer generation
- answer + evidence snippets
- local runtime via Ollama

### Intentionally not overbuilt yet
- deep crawling
- broad connector ecosystem
- autonomous agents
- multi-source orchestration
- complex ranking pipelines

The MVP is a **sharp vertical slice**: one selected source, one clean retrieval flow, one clear grounded-answer experience.

---

## Architecture at a glance

```text
UI
 ↓
Python API
 ├─ source catalog
 ├─ local import pipeline
 │   ├─ snapshot source
 │   ├─ parse
 │   ├─ chunk
 │   ├─ embed via Ollama
 │   └─ store vectors + metadata
 ├─ retrieval service
 └─ answer service
     ├─ embed the question
     ├─ retrieve top chunks
     └─ generate grounded answer via Ollama
```

---

## Current product decisions

### Locked for MVP
- **Backend:** Python
- **Local model runtime:** Ollama
- **Vector store:** Qdrant local mode
- **Metadata store:** SQLite via a swappable repository / adapter layer
- **Workflow:** import → chunk → embed → retrieve → answer
- **Primary UX:** source selection, question input, answer, evidence

### Why this stack
Because it gets to a real end-to-end prototype fast, stays local-first, and keeps the path open for more controlled enterprise deployment later.

---

## Local backend scaffold

The repo now includes a backend-only scaffold for the first implementation slice.

Windows-first commands from the repo root:

- `.\tools\setup.ps1`
- `.\tools\dev.ps1`
- `.\tools\test.ps1`
- `.\tools\lint.ps1`
- `.\tools\typecheck.ps1`
- `.\tools\eval.ps1`

Current runtime surface:

- `GET /health`

`setup.ps1` bootstraps a repo-local helper environment for `uv` under `.tools\bootstrap` and then syncs the backend project.

---

## Potential AI capabilities

These are the most exciting directions that fit the product and can be layered in without breaking the MVP direction.

### Grounded Answer Mode+
Stricter answer behavior when evidence is weak, missing, or contradictory.

### Evidence / Snippet Panel
A richer view of retrieved chunks, extending the baseline MVP evidence display.

### Source Memory Cards
Save important findings, pinned snippets, risks, or open questions for each source.

### Multi-Perspective Review
Analyze the same source from different lenses such as architecture, security, maintainability, or operations.

### Import-Time Secret Scan
Detect suspicious keys or tokens when ingesting repository-like content.

### Source Map / Relationship View
Visualize clusters, connections, or structural relationships inside a source collection.

These features are not all in the MVP, but they are highly aligned with the product direction and give the project its longer-term wow factor.

---

## Why it stands out

- **Private by design** instead of privacy as an afterthought
- **Grounded answers** instead of generic chatbot theater
- **Evidence-first UX** instead of “just trust the model”
- **Reusable retrieval layer** instead of one-shot document chat
- **A path toward enterprise-safe AI workflows** without making the MVP feel heavy

---

## Example workflow

```text
Import source → Parse text → Split into chunks → Create embeddings → Store vectors → Ask question → Retrieve evidence → Generate grounded answer
```

---

## Roadmap direction

- [ ] source catalog MVP
- [ ] local file/folder import
- [ ] grounded source chat
- [ ] evidence panel
- [ ] stricter grounding mode
- [ ] retrieval tuning
- [ ] source memory cards
- [ ] multi-perspective review
- [ ] GitHub/repository-oriented import path
- [ ] import-time secret scan
- [ ] source relationship view

---

## Screenshots / demo

> Add the first real screenshot or GIF as soon as the vertical slice works.
>
> Best first demo: **source list + selected source + grounded answer + evidence snippets**.

```html
<p align="center">
  <img src="./docs/demo.gif" alt="Source Lens demo" width="920">
</p>
```

---

## Positioning

**Source Lens is a local-first AI knowledge workspace for importing, indexing, and exploring private sources with grounded answers and visible evidence.**

It starts small on purpose, but it is built to grow into something much more powerful than “chat with a file.”

---

## Who this is for

- engineers exploring practical local AI
- teams working with sensitive internal knowledge
- builders who want a reusable RAG foundation
- people who want private knowledge to become searchable, explainable, and reusable

---

## License

TBD
