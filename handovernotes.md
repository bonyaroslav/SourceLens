# Handover Notes — Session ending 2026-06-21

## What was done this session

**GitHub issue #19 — Ask flow** is fully implemented and verified in the browser.

### Files created
- `frontend/src/features/workspace/api/askApi.ts` — `askSource()` fetch function, `AskResponse` and `EvidenceItem` types
- `frontend/src/features/workspace/hooks/useAsk.ts` — TanStack Query `useMutation` wrapping the POST call
- `frontend/src/features/workspace/components/AskPanel.tsx` — question form, loading state, error state, answer block, evidence list

### Files modified
- `frontend/src/features/workspace/routes/WorkspaceRoute.tsx` — replaced `"Ask flow coming in issue #19"` placeholder with `<AskPanel>`
- `frontend/src/styles.css` — added all `.ask-panel__*` styles; removed the now-dead `.workspace-content__ask-placeholder` rule

### Verified in browser
- Selecting the `completed` source (`5cb18289-4a25-4053-b809-7a0b16beef0f`) shows the question input and Ask button.
- Selecting the `failed` source (`91ac4263-667d-4204-b956-f49a5ff38eb3`) shows "This source is not ready. Import must complete before you can ask questions."
- The ask form is disabled while a request is in flight.
- Switching source clears the previous answer (React Router remount).

### Not yet committed
The working tree has these uncommitted changes from this session. Commit before starting the next issue.

Suggested commit message options:
1. `implement ask flow for issue #19 — form, mutation, evidence display`
2. `add POST /ask integration with loading, error, and not-ready states`
3. `wire up source ask panel: question input, answer, and evidence list`

---

## Next issue to pick up

**GitHub issue #20 — Design** (follows #19 in the chain `#19 → #20 → #21 → PRD #15 done`).

Check the issue body on GitHub for its exact scope before starting. The label to look for is `ready-for-agent`.

---

## Leftovers / known gaps

These are things noticed this session that are not yet done and were not in scope for #19:

### Immediate follow-ons (from the issue chain)
- **#20 Design** — visual polish / design pass on the workspace (next unblocked issue).
- **#21 Frontend tests** — unit/integration test coverage for the ask flow components and hooks.
- **PRD #15** — done only after #21 lands.

### Functional gaps not covered by #19
- **Switching source does not reset the question text** in the input field. React Router remounts `AskPanel` so the answer clears, but if the component ever becomes non-remounting this will be a bug. Low risk for now.
- **No optimistic UI** — the Ask button just shows "Asking…"; no skeleton or streaming. Acceptable for MVP.
- **`grounding_status` display** — only shows a warning when status is not `"grounded"`. The exact set of non-grounded values from the backend is not documented; the frontend handles any string but the label says "Confidence: …" which may be confusing for some statuses.
- **Evidence `relative_path` is nullable** — handled (the path line is hidden when null), but the backend does not always populate it. Worth confirming the backend fills this for file-based sources.
- **Error message granularity** — `409` maps to "source not ready", all other non-ok statuses collapse to "Something went wrong." A `400` bad-request case would silently show the generic message; this is fine for MVP.

### Backend / infra leftovers (pre-existing, not introduced this session)
- **Storage migration pending** — backend still uses legacy SQLite and Qdrant adapters. New backend work should avoid deepening that surface. PostgreSQL + pgvector is the target.
- **Import flow not wired in the frontend** — `POST /sources/import` and `GET /import-jobs/{job_id}` have no frontend UI yet. The current source list is populated via fixtures or direct API calls.
- **No frontend for `GET /sources/{source_id}`** — the detail panel pulls from the already-loaded `useSources()` list. If a `sourceId` arrives by URL without a prior sources fetch, the name falls back to the raw ID until the list loads.

### Docs alignment check (do before closing the milestone)
- Confirm `docs/afk-handoff.md` still describes the current repo reality (it still says the frontend "is not yet wired end to end to source loading and ask behavior" — this is now stale for the ask slice).
- `README.md` may need a brief update once the milestone is fully done.

---

## How to start servers

```powershell
# Backend (uvicorn on http://127.0.0.1:8000)
.\tools\dev.ps1

# Frontend (Vite on http://localhost:5173)
cd frontend && npm run dev
```

## Useful source IDs for manual testing

| ID | Name | Status |
|----|------|--------|
| `5cb18289-4a25-4053-b809-7a0b16beef0f` | Source Lens eval fixture | `completed` — ask flow works |
| `91ac4263-667d-4204-b956-f49a5ff38eb3` | Source Lens eval fixture | `failed` — shows not-ready message |
