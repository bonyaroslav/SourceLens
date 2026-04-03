# plan.md

## Project working concept

Build a **local-first knowledge workspace** that lets a user:

- import a knowledge source
- process and index it ahead of time
- select that source in the UI
- ask questions against that source
- receive answers based on retrieved relevant content

The product direction is intentionally broader than “chat with a file”, but the first implementation should stay narrow and practical.

---

## Current intent

The current goal is to define and lock in **high-level architecture and MVP direction** without overcommitting to detailed implementation choices too early.

The project is still in **planning mode** for:
- detailed architecture
- workflow design
- best practices
- use of Anthropic Code skills / sub-agents
- operational approach for implementation

Those parts will be defined later after better planning.

---

## Confirmed product goals

The system should support a workflow where a user can:

1. view a list of available knowledge sources
2. see basic metadata for each source, such as:
   - name
   - description
3. open a selected source
4. ask questions about that source
5. receive answers generated from retrieved indexed content

The system should be useful for exploring different kinds of information, including examples such as:
- project documents or descriptions
- science papers
- imported repositories
- web-imported content

---

## Confirmed functional areas

### 1. Source catalog UI
A UI should exist where people can choose a stored knowledge source.

At minimum, a source currently needs:
- name
- description

No additional metadata is fixed yet.

### 2. Source import / ingestion
The system should support bringing information into internal storage for later retrieval.

Possible import paths mentioned so far:
- local file
- local folder
- URL
- GitHub repository

The imported content should be processed and stored in an indexed form for future querying.

### 3. Retrieval / RAG backend
A backend component should:
- convert text into embeddings
- search relevant processed content
- return appropriate information for question answering

### 4. AI answering layer
A separate AI endpoint / model layer should support chat or answer generation over retrieved content.

This endpoint may be changeable.

Model direction mentioned so far:
- local Gemma 4
- Gemini API for testing / convenience

### 5. Source-type-specific import behavior
There is interest in having source-specific import behavior, for example:
- GitHub URL -> use GitHub-specific import logic

However, the exact detection and behavior rules are **not fixed yet**.

---

## MVP intent

The intention is to deliver an MVP as early as possible and then add features incrementally.

The MVP should focus on **basic scenarios first**, then expand in layers from simple to more complex.

Current principle:
- ship a narrow but real vertical slice first
- extend feature-by-feature later

---

## Modularity intent

The system should be designed so that parts can evolve independently.

Modularity is currently expected in at least these areas:

- **source ingestion**
  - different importers for different source types
- **indexing / retrieval**
  - preprocessing and embedding-based search
- **AI provider**
  - swappable model / endpoint layer
- **UI**
  - source selection, import flow, and question-answer interaction

A key intent is that the AI backend should not be tightly coupled to one provider.

---

## Technology direction currently under consideration

### Frontend
Confirmed direction under consideration:
- Angular
- TypeScript

### Backend
Still open:
- Python
- .NET

No final backend decision has been made yet.

### AI models / providers
Current working direction:
- focus on Gemma 4 for local usage
- Gemini API may be used for testing or convenience

Exact runtime / serving approach is not fixed yet.

### Environment
Current local machine context provided:
- Windows 11
- GeForce 4080
- 32 GB RAM
- Intel Core i7 10th generation

This is informative context only, not yet a formal requirement.

---

## High-level architectural decisions currently assumed for planning

These are **working assumptions for planning**, based on current discussion, but should still be treated as revisitable until explicitly locked.

### Assumption A — frontend direction
Use:
- Angular
- TypeScript

### Assumption B — backend recommendation
Use:
- Python backend

Reason this is being treated as the current recommendation:
- easier experimentation for AI / RAG workflows
- easier access to model and retrieval ecosystem

This is still not a final irreversible decision.

---

## Open decisions not yet fixed

The following are intentionally **not decided yet**:

### Product scope
- whether MVP should support one source type first or several
- whether querying is limited to one selected source or can span many sources
- how much source metadata is needed beyond name and description

### Import scope
- which import methods are in MVP vs later
- whether URL import means single page, feed, or small site
- whether GitHub import is part of MVP or later
- whether source-type detection is manual, automatic, or mixed

### Retrieval / answer UX
- answer format
- citations / snippets behavior
- whether retrieved chunks are visible in UI
- whether there is debug / inspect mode

### Backend / storage
- Python vs .NET final decision
- specific vector storage choice
- specific metadata storage choice
- file-based vs DB-backed internal storage

### Model serving
- exact Gemma 4 runtime path
- local model serving approach
- provider switching approach
- whether one provider is configured at a time or selectable in UI

### Execution / implementation process
- use of Anthropic Code skills
- use of sub-agents
- development workflow
- planning conventions
- coding best practices to enforce

These are expected to be decided later.

---

## Current positioning

A useful current positioning statement is:

> A local-first AI workspace for importing, indexing, and exploring knowledge sources with grounded answers.

This is only a working positioning statement, not a finalized product statement.

---

## Planning principle for next steps

Before implementation begins, the next focus should be on clarifying a small set of architectural decisions rather than expanding the feature list.

Recommended next planning focus:
1. define MVP source scope
2. define backend choice
3. define model/provider strategy
4. define retrieval + answer output shape
5. define storage/indexing approach
6. define implementation workflow and best-practice setup

---

## Notes

- This document intentionally avoids locking in detailed constraints that were not explicitly confirmed.
- This document is a **first draft planning snapshot**, not a final specification.
- Additional architecture, implementation process, and toolchain conventions should be added only after explicit decisions are made.
