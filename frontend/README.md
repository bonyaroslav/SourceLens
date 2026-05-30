# Source Lens Frontend

The frontend workspace is a React + TypeScript single-page app built with Vite. Angular is removed from the active repo direction. The current frontend implementation is still a React shell that keeps the Python backend as the integration seam while the remaining source-loading and ask-flow slices are completed.

## Run locally

From the repo root:

```powershell
.\tools\setup.ps1
.\tools\dev.ps1
```

Then, in `frontend\`:

```powershell
npm run dev
```

The Vite app runs on `http://127.0.0.1:5173` by default. It expects the backend seam at `http://127.0.0.1:8000`, or the origin supplied through `VITE_SOURCE_LENS_API_BASE_URL`.

## Verification

Repo-root canonical commands:

```powershell
.\tools\test.ps1
.\tools\lint.ps1
.\tools\typecheck.ps1
```

Frontend-only commands:

```powershell
npm run test:ci
npm run lint
npm run typecheck
```

## MVP boundaries

- exactly one selected source at a time
- the current slice is a React shell, not the full source-loading or ask workflow
- grounded answers and visible evidence remain in scope for follow-on frontend slices
- multi-source querying, browser upload, and richer answer history remain out of scope
