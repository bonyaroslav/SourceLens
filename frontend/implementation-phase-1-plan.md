# Source Lens Frontend Phase 1 Plan

## Summary

Phase 1 wires the existing Angular workspace shell to the current Python backend for source loading and path-based import. The UI keeps the chosen three-panel layout, but replaces fake in-memory source data with real backend state managed through classic NgRx actions, reducers, selectors, and effects.

Phase 1 scope:
- real source catalog loading
- path-based file or folder import
- import job polling
- one active source only
- ask and evidence panels visible but not yet wired to the backend

Phase 2 remains responsible for:
- `POST /sources/{source_id}/ask`
- grounded answer rendering
- evidence rendering
- handled insufficient-evidence UX

## Locked Decisions

- Keep the current single-screen workspace layout.
- Use classic NgRx Store and Effects to teach the explicit event flow.
- Keep one `workspace` feature state.
- Keep import path-based to match the existing backend API.
- Remove interactive multi-select behavior for now.

## Phase 1 Event Model

Actions:
- `workspaceEntered`
- `loadSources`
- `loadSourcesSuccess`
- `loadSourcesFailure`
- `setActiveSource`
- `submitImport`
- `submitImportSuccess`
- `submitImportFailure`
- `pollImportJob`
- `pollImportJobSuccess`
- `pollImportJobFailure`

Effects:
- load sources on workspace entry
- submit import request
- poll the import job until a terminal state
- refresh sources after terminal import state

## Acceptance Checks

- App startup renders real backend sources instead of fake local seed data.
- A valid local file or folder path creates a real import job.
- Import job status transitions are visible in the UI.
- Source list refreshes after import completes or fails.
- Only one source can be active at a time.
- Ask remains disabled until Phase 2.
- Backend validation errors are shown clearly in the import area.
