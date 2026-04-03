<div align="center">

# Nexus Knowledge Workspace

**A local-first AI workspace for exploring documents, papers, codebases, and imported web sources with grounded answers.**

<p>
  <img alt="Angular" src="https://img.shields.io/badge/UI-Angular-DD0031?logo=angular&logoColor=white">
  <img alt="TypeScript" src="https://img.shields.io/badge/Frontend-TypeScript-3178C6?logo=typescript&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Backend-Python-3776AB?logo=python&logoColor=white">
  <img alt="Local AI" src="https://img.shields.io/badge/LLM-Gemma%204%20%7C%20Gemini-6C47FF">
  <img alt="Status" src="https://img.shields.io/badge/Status-MVP%20in%20Progress-0A7EA4">
</p>

**Import knowledge. Index it once. Ask better questions forever.**

</div>

---

## Why this exists

Most AI demos stop at “chat with a file.”

**Nexus** is designed as a reusable knowledge workspace:
- choose a source
- ingest and index it
- ask grounded questions
- switch between **local AI** and hosted models
- keep the architecture open for enterprise-safe deployments

It is built for scenarios where data locality, explainability, and source-aware retrieval matter more than flashy generic chat.

---

## What it can do

- **Source Catalog** — browse indexed knowledge sources with name and description
- **Grounded Q&A** — ask questions against a selected source
- **RAG Retrieval** — retrieve relevant chunks before answer generation
- **Pluggable Models** — run with **local Gemma 4** or a hosted API such as Gemini
- **Import Pipeline** — ingest local files, folders, URLs, and later GitHub repositories
- **Enterprise-Friendly Direction** — designed for local-first or controlled deployments

---

## Demo scenarios

### 1. Project Knowledge Assistant
Import project docs, architecture notes, specs, and meeting records.  
Ask:
- “What are the main risks in this project?”
- “Which decisions were made about authentication?”
- “Summarize open questions from the design notes.”

### 2. Research Paper Explorer
Import a set of papers or reports.  
Ask:
- “What are the main claims across these papers?”
- “Compare methods and limitations.”
- “Extract future work ideas.”

### 3. Codebase Companion
Import a repository snapshot or prepared code docs.  
Ask:
- “Where is auth handled?”
- “What modules are coupled to billing?”
- “Explain the architecture of this service.”

---

## Why it feels different

- **Local-first by design**
- **Swappable model backend**
- **One UI for many source types**
- **Focused on grounded answers, not generic chatbot theater**
- **Built to evolve from MVP to enterprise-style internal tool**

---

## MVP scope

### Included now
- Source list
- Source details
- Chat against one selected source
- File/folder import
- Basic URL import
- Embedding + retrieval pipeline
- Model provider abstraction
- Support for local and hosted inference

### Planned next
- GitHub repo importer
- crawler profiles by source type
- scheduled re-indexing
- hybrid retrieval
- answer citations/snippet viewer
- source sync history
- cross-source querying

---

## Architecture at a glance

```text
Angular UI
   ↓
API Backend
   ├─ Importers (files / folders / URL / GitHub)
   ├─ Processing (parse → chunk → embed)
   ├─ Index storage
   ├─ Retrieval layer
   └─ LLM adapters (Gemma 4 local / Gemini API)
````

---

## Quick start

```bash
# 1. clone the repo
git clone https://github.com/yourname/nexus-knowledge-workspace.git

# 2. start backend
cd backend
# install deps, configure model provider, run API

# 3. start frontend
cd ../frontend
npm install
npm start
```

Then:

1. add a source
2. import files or a URL
3. wait for indexing
4. open the source
5. start asking questions

---

## Example workflow

```text
Import source → Process content → Build embeddings → Search relevant chunks → Generate grounded answer
```

---

## Vision

This project starts as a concise, local-first RAG workspace.

It is intentionally designed to grow into:

* a private internal knowledge assistant
* a research navigator
* a code exploration tool
* a foundation for enterprise-safe AI workflows

---

## Tech direction

* **Frontend:** Angular + TypeScript
* **Backend:** Python API
* **Local models:** Gemma 4
* **Hosted fallback:** Gemini API
* **Retrieval:** embedding-based search over preprocessed source chunks

---

## Project status

This repository is currently focused on shipping a sharp MVP fast:

* one clean import flow
* one clean chat flow
* one clean retrieval flow
* extensibility without overengineering

---

## Screenshots

> Add one GIF or screenshot here as soon as the first vertical slice works.
> Best first screenshot: **Source Catalog + Source Chat + Retrieved Snippets**.

```html
<p align="center">
  <img src="./docs/demo.gif" alt="Nexus demo" width="900">
</p>
```

---

## Roadmap

* [ ] MVP source catalog
* [ ] file/folder import
* [ ] URL import
* [ ] source chat
* [ ] local Gemma 4 adapter
* [ ] Gemini adapter
* [ ] snippet/citation panel
* [ ] GitHub importer
* [ ] scheduled sync
* [ ] retrieval evaluation page

---

## Who this is for

* engineers exploring local AI
* teams with sensitive internal knowledge
* developers who want a reusable RAG foundation
* anyone who wants to query their own curated information, not a public web index

---

## License

TBD