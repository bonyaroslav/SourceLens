# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Use the GitHub integration for create, read, update, and label operations.

## Repository

- `bonyaroslav/SourceLens`

## Conventions

- Create PRDs and implementation tickets as GitHub issues.
- Apply `ready-for-agent` only to issues that are fully specified, unblocked, and aligned with the current repo source of truth.
- Keep only one implementation issue `ready-for-agent` at a time for AFK sequential execution unless parallel work is explicitly intended.
- Encode issue dependencies explicitly in the issue body with `Blocked by`.
- Include concrete acceptance checks and a deterministic verification path before marking an issue ready.
- Infer the repository from the local clone when working inside this repo.

## When a skill says "publish to the issue tracker"

Create a GitHub issue in `bonyaroslav/SourceLens`.

## When a skill says "fetch the relevant ticket"

Read the GitHub issue, including its labels and comments.
