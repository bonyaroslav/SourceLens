# Domain Docs

This repo uses a single-context documentation layout.

## Read these first

- `CONTEXT.md` at the repo root for domain language and current architectural direction
- `plan.md` for the active milestone, implementation rules, and done criteria
- `README.md` for product positioning
- `docs/adr/` if ADRs are added later

## Consumer rules

- Prefer the vocabulary defined in `CONTEXT.md`.
- Treat `CONTEXT.md` as the current architecture source of truth when older docs or tickets disagree.
- Treat `plan.md` as the implementation source of truth for the active milestone.
- If a future ADR conflicts with an older assumption, surface the conflict explicitly instead of silently overriding it.
