# Source Lens Frontend Phase 2 Plan, Lean Version

## Summary

Wire the existing ask flow to the backend and replace the Phase 1 placeholders with real answer and evidence rendering, while keeping the implementation intentionally small. Phase 2 should reuse the current Angular workspace and Phase 1 NgRx feature, but only add the minimum state and UI needed for `POST /sources/{source_id}/ask`.

Key simplification choices:
- keep one active source only
- clear answer, evidence, and ask error when the active source changes
- keep the draft question local to the ask panel component
- keep NgRx for server state and request lifecycle only
- show raw evidence scores directly

## Key Changes

### API layer

- Add ask types to the existing API layer:
  - `AskSourceRequest`
  - `AskResponseDto`
  - `EvidenceDto`
- Add `askSource(sourceId, request)` to `WorkspaceApiService`.
- Add one mapper for:
  - answer view model
  - evidence item view model
  - grounding status label if needed
- Do not add new backend endpoints or extra frontend-only response abstractions beyond what the UI actually renders.

### NgRx changes

- Extend `AskState` to hold only:
  - `submitting`
  - `error`
  - `result`
- `result` stores the latest successful backend ask response.
- Do not store `question` in NgRx.
- Do not store `resultSourceId` separately because `result.source_id` already exists.
- Add actions:
  - `submitAsk`
  - `submitAskSuccess`
  - `submitAskFailure`
- Extend the existing `setActiveSource` reducer so it clears:
  - `ask.error`
  - `ask.result`
- Keep the draft question in the component, so changing source clears only server-derived ask state.

### Ask effect and request flow

- Use `exhaustMap` for `submitAsk`.
  - Rationale: the button will already be disabled while submitting, so this is simpler than cancellation logic.
- `submitAsk` action should carry:
  - `sourceId`
  - `question`
- Trim the question before dispatching `submitAsk`.
- Handle backend failures by mapping:
  - `400` to validation message
  - `404` to missing-source message
  - `409` to source-not-ready message
  - fallback to generic request failure
- On `submitAskSuccess`, replace any previous ask result completely.
- Recommended default: clear the current result at submit start so the UI always reflects the latest request lifecycle cleanly.

### Ask panel behavior

- Convert `AskPanelComponent` into a real input component with:
  - local textarea state
  - submit output event
  - loading, error, and result inputs
- Enable submit only when:
  - there is an active source
  - the active source is `completed`
  - the trimmed question is non-empty
  - no ask request is in flight
- Show these states:
  - source not ready
  - ready to ask
  - submitting
  - grounded answer
  - insufficient evidence
  - ask error
- Do not add keyboard shortcuts in Phase 2.
- Do not add answer history in Phase 2.

### Evidence panel behavior

- Replace the placeholder with real evidence rendering from `ask.result`.
- Keep the existing top section with active source metadata.
- Below that, render one of:
  - no answer yet
  - loading
  - insufficient-evidence empty state
  - evidence list
- Each evidence item shows:
  - `chunk_index`
  - raw `score`
  - `text`
- Do not invent titles or labels for evidence entries if the backend does not provide them.
- If `grounding_status` is `insufficient_evidence`, show a deliberate empty-evidence state rather than an error.

### Component and selector boundaries

- `WorkspaceShellComponent`
  - keeps store bindings
  - passes active source readiness and ask server state into children
  - dispatches `submitAsk`
- `AskPanelComponent`
  - owns local question input state
  - emits submit event with trimmed question
  - renders answer text and ask errors
- `EvidencePanelComponent`
  - renders evidence from store-backed ask result
- Keep selectors minimal:
  - `selectAskSubmitting`
  - `selectAskError`
  - `selectAskResult`
  - `selectEvidenceItems`
  - `selectHasInsufficientEvidence`
  - `selectCanAsk`
- Avoid selector proliferation unless a template becomes unreadable.

## Public Interfaces and Contracts

No backend API changes.

Frontend additions:
- `AskSourceRequest`
  - `question: string`
- `AskResponseDto`
  - `source_id: string`
  - `question: string`
  - `answer: string`
  - `grounding_status: string`
  - `evidence: EvidenceDto[]`
- `EvidenceDto`
  - `chunk_id: string`
  - `chunk_index: number`
  - `text: string`
  - `score: number`

Behavior contracts:
- client trims question text before dispatch
- whitespace-only questions do not submit
- source switch clears answer, evidence, and ask error but does not force-clear the draft question input
- `insufficient_evidence` is treated as a successful response state
- evidence is rendered as plain text, not markdown

## Test Plan

### Store and effect tests

- `submitAsk` calls the backend with the active source id and trimmed question
- `submitAskSuccess` stores answer and evidence
- `submitAskFailure` stores the mapped error
- `400`, `404`, and `409` responses produce distinct handled messages
- `setActiveSource` clears ask result and ask error
- `exhaustMap` prevents duplicate concurrent ask requests

### Component tests

- ask button stays disabled for non-ready sources
- ask button enables for completed sources with non-empty trimmed question
- ask panel shows loading state during request
- ask panel shows grounded answer text on success
- ask panel shows insufficient-evidence answer without error styling
- evidence panel renders raw score, chunk index, and text
- evidence panel renders an explicit empty-evidence state when evidence is absent

### Manual scenarios

- ask a completed source and see answer plus evidence render
- ask a source with weak evidence and see the fallback answer with empty evidence
- switch to another source and verify the previous answer and evidence clear immediately
- re-ask the same question against the new source and see a fresh result
- attempt to ask a queued, running, or failed source and confirm the UI blocks submission

## Assumptions and Defaults

- maintainability is prioritized over preserving stale answers across source switches
- the local question draft does not need to be globally stored
- only the latest ask result is supported
- no markdown rendering, answer history, retry UX, or keyboard shortcuts are included
- no additional `GET /sources/{source_id}` fetch is required for Phase 2 unless implementation reveals missing fields in the current list payload
- this phase should remain under the existing workspace feature and should not introduce additional feature stores
