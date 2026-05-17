# Source Lens Frontend

The Angular workspace is wired to the current MVP backend slice. It loads sources from `GET /sources`, lets the user select one active source, submits one question to `POST /sources/{source_id}/ask`, and renders the grounded answer plus evidence snippets.

## Run locally

From the repo root:

```powershell
.\tools\setup.ps1
.\tools\dev.ps1
```

Then, in `frontend\`:

```powershell
npm start
```

The Angular dev server runs on `http://localhost:4200` and proxies `/api` requests to `http://127.0.0.1:8000`.

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
- path-based local import remains the MVP import UX
- grounded answers and visible evidence are in scope
- multi-source querying, browser upload, and richer answer history remain out of scope
