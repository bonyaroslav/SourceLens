# Potential Features

## Purpose

This note collects feature candidates that may be considered for the project after the initial MVP direction is clarified.

The goal of this document is to:
- capture realistic feature extensions
- describe their functional value
- keep implementation notes lightweight
- record external references that informed these ideas

This document does **not** finalize scope or architecture.

---

## Candidate features

## 1. Grounded Answer Mode

### Summary
Extend the MVP grounded-answer baseline with a stricter mode where the system is expected to answer only from retrieved source evidence.

### Functional value
- reduces unsupported synthesis
- makes source-aware behavior explicit
- is suitable for document, research, and codebase exploration

### Possible behavior
- enforce stricter answer-only-from-evidence behavior
- decline or qualify answers when evidence is insufficient
- make grounding status more explicit

### Small use case
A user asks for the authentication approach used in a project.  
The system answers using retrieved design notes and shows the supporting excerpts.

### Implementation note
Complexity: **small to medium**

### MVP boundary note
Baseline grounded answers and evidence exposure are already part of MVP.
This feature refers only to stricter grounding behavior beyond the baseline contract.

### Related references
- Galileo Agent Control (governance / guardrails for AI agents)  
  https://www.opensourceforu.com/2026/03/galileo-launches-open-source-control-layer-for-enterprise-ai-agents/
- New Stack summary of Galileo Agent Control  
  https://thenewstack.io/galileo-agent-control-open-source/

---

## 2. Evidence / Snippet Panel

### Summary
Extend the MVP evidence display into a richer dedicated panel that shows the retrieved snippets or chunks used in the answer.

### Functional value
- improves traceability of responses
- supports validation of RAG output
- makes the retrieval layer visible to the user

### Possible behavior
- show top retrieved chunks with clearer structure
- allow expanding the original source segment
- optionally show retrieval score, rank, or chunk metadata later

### Small use case
For a science paper collection, the user asks for limitations of a method.  
The answer is accompanied by the exact relevant excerpts from the papers.

### Implementation note
Complexity: **small**

### MVP boundary note
Showing evidence snippets is already part of MVP.
This feature refers to a richer evidence experience, not the initial baseline display.

### Related references
This feature is closely related to grounded-answer behavior and source-aware retrieval.  
See the same guardrail-oriented references as above.

---

## 3. Import-time Secret Scan

### Summary
Run a lightweight scan for secrets or sensitive tokens when importing files or repositories.

### Functional value
- helps identify exposed credentials early
- is relevant for repository import workflows
- fits enterprise-oriented code and document ingestion scenarios

### Possible behavior
- detect likely API keys, tokens, and credentials
- show file paths and suspicious matches
- mark findings for manual review

### Small use case
A GitHub repository is imported and the system flags a suspicious token in a configuration file before indexing is completed.

### Implementation note
Complexity: **small to medium**

### Related references
- GitHub secret scanning coverage update  
  https://github.blog/changelog/2026-03-31-github-secret-scanning-nine-new-types-and-more/
- Coverage summary mentioning expansion in this area  
  https://www.devopschat.co/articles/github-adds-37-new-secret-detectors-in-march-extends-scanning-to-ai-coding-agents

---

## 4. Source Memory Cards

### Summary
Allow users to save persistent findings related to a source.

### Functional value
- preserves important observations across sessions
- supports repeated work on the same source
- creates reusable summaries and notes without changing the source data

### Possible behavior
Users can save items such as:
- key findings
- open questions
- pinned snippets
- important facts
- source-specific notes

### Small use case
A user reviews a codebase and saves memory cards for:
- authentication entry points
- deployment assumptions
- known risks

### Implementation note
Complexity: **small**

### Related references
- Zilliz / MemSearch announcement  
  https://www.prnewswire.com/news-releases/zilliz-open-sources-memsearch-giving-ai-agents-persistent-human-readable-memory-302711968.html
- Hpcwire / BigDataWire coverage of MemSearch  
  https://www.hpcwire.com/bigdatawire/this-just-in/zilliz-open-sources-memsearch-giving-ai-agents-persistent-human-readable-memory/

---

## 5. Multi-perspective Review

### Summary
Allow the user to review the same source from several predefined perspectives.

### Functional value
- supports structured analysis without requiring true autonomous agents
- useful for code, documents, and research sources
- can make review output more systematic

### Example perspectives
- architecture
- security
- maintainability
- operations
- research quality

### Small use case
A repository is reviewed from architecture, security, and operational perspectives and the system returns three separate analyses.

### Implementation note
Complexity: **small to medium**

### Related references
- Anthropic multi-agent code review coverage  
  https://thenewstack.io/anthropic-launches-a-multi-agent-code-review-tool-for-claude-code/

---

## 6. Acceptance Criteria / Output Checklist

### Summary
Allow the user to define what an answer or review must contain before the system generates it.

### Functional value
- clarifies expected output shape
- helps verify generated content against explicit requirements
- aligns with current AI coding and review practices

### Possible behavior
Before generating output, the user can specify:
- required sections
- required topics
- excluded content
- formatting expectations

### Small use case
A user asks for a project summary and requires the answer to include:
- risks
- dependencies
- unresolved questions
- recommended next actions

### Implementation note
Complexity: **small**

### Related references
- Stack Overflow blog: coding guidelines for AI and people  
  https://stackoverflow.blog/2026/03/26/coding-guidelines-for-ai-agents-and-people-too/

---

## 7. Source Map / Relationship View

### Summary
Provide a visual view of relationships inside a source or between imported items.

### Functional value
- supports exploration beyond chat
- helps users understand structure, clusters, and relationships
- can be useful for papers, repositories, or larger document sets

### Possible forms
- topic clusters
- document relationship graph
- file/folder graph
- module relationship map
- paper comparison map

### Small use case
A user imports a paper collection and opens a visual map showing clusters by topic and relationships between methods.

### Implementation note
Complexity: **medium**

### Related references
- OpenAI: interactive math and science visual explanations  
  https://openai.com/index/new-ways-to-learn-math-and-science-in-chatgpt/

---

## Prioritization notes

At this stage, the most straightforward feature candidates to evaluate after MVP are:

1. Stricter Grounded Answer Mode
2. Richer Evidence / Snippet Panel
3. Source Memory Cards
4. Acceptance Criteria / Output Checklist
5. Import-time Secret Scan

These features are relatively contained and can fit the current project direction without requiring a full autonomous-agent architecture.

---

## Deferred or not prioritized in this note

The following areas are intentionally not expanded here:
- full autonomous agents
- complex multi-source orchestration
- broad connector ecosystems
- domain-specific therapy or wellbeing features
- advanced scheduling / workflow automation

These may be reconsidered later if the project scope changes.

---

## Notes

- This document is a candidate feature list, not a final roadmap.
- External references are included as context and inspiration, not as mandatory implementation models.
- Final feature selection should follow after MVP architecture and scope decisions are clarified.
- MVP ingestion scope currently includes `.txt`, `.md`, `.pdf`, `.html`, and `.htm`.
