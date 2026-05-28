# Domain Docs

This repo uses a single-context documentation layout.

## Read these first

- `CONTEXT.md` at the repo root for domain language and current architectural direction
- `plan.md` for locked implementation rules and milestone scope
- `README.md` for product positioning
- `docs/adr/` if ADRs are added later

## Consumer rules

- Prefer the vocabulary defined in `CONTEXT.md`.
- Treat `plan.md` as the implementation source of truth when product positioning and implementation detail differ.
- If a future ADR conflicts with an older assumption, surface the conflict explicitly instead of silently overriding it.
