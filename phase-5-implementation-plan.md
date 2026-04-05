# Phase 5 Implementation Plan

This file turns the locked Phase 5 architecture in `plan.md` into the next executable quality slice for this repo.

## Goal

Add a small but real evaluation baseline for the first end-to-end Source Lens workflow:

- import one known sample source
- ask one grounded question against that source
- verify returned evidence contains expected source text
- verify the current insufficient-evidence contract on a controlled weak case

Keep `.\tools\eval.ps1` as the canonical command. Phase 5 should harden that command into a repeatable regression check, not replace it with a broader benchmark framework.

## Why this phase matters now

The repo already has the first vertical slice:

- local import
- source catalog
- ask flow
- evidence return path

What it does not have yet is a repo-owned quality baseline that survives code changes. Phase 5 should be the first durable regression layer for grounded behavior, not another one-off smoke script.

## Starting point in this repo

- `.\tools\eval.ps1` currently invokes `python -m source_lens_api.eval_smoke`
- `backend/src/source_lens_api/eval_smoke.py` mixes dependency proof with ask-flow smoke checks
- ask-flow tests already cover grounded and insufficient-evidence branches with fake adapters
- no repo-owned eval fixture set or case definitions exist yet

## Constructive criticism of the first draft

The first draft was usable, but it left a few important decisions too soft:

- it did not clearly define whether `eval` still owns the existing dependency-proof checks or only the new quality cases
- it left the weak-evidence case too vague by saying "empty or vectorless" without choosing a deterministic path
- it named broad target folders but not the minimal code structure needed to keep eval logic maintainable
- it did not specify a verification path beyond high-level acceptance checks

This revision resolves those gaps.

## Scope

In scope:

- repo-owned eval fixtures for the first slice
- one grounded eval case using the real import path
- one weak-evidence eval case using the current ask contract
- a small eval case model plus assertion helpers
- deterministic console output and non-zero exit on case failure
- automated tests for eval-specific logic that do not require live model calls

Out of scope:

- a generic benchmark framework
- exact answer scoring or LLM-as-judge
- multi-source evals
- prompt tuning sweeps
- retrieval threshold policy redesign
- frontend eval UI

## Locked defaults for this repo

- keep `.\tools\eval.ps1` as the canonical entrypoint
- preserve the existing dependency-proof role already carried by `eval`; Phase 5 adds a quality layer and must not silently remove earlier guarantees
- run eval against repo-local data paths, not machine-global state
- use the real import pipeline for the grounded case
- assert on grounding status and evidence content before answer wording
- keep the weak-evidence baseline aligned to the current API contract: `grounding_status == "insufficient_evidence"` and `evidence == []`

## Determinism rules

Use these rules when designing fixtures and assertions:

- fixture text should include distinctive phrases unlikely to appear in model priors
- do not assert the full answer string for grounded cases
- prefer evidence substring checks over answer substring checks
- avoid timestamps, random identifiers, or machine-specific paths in expected output
- case names and console output should be stable enough to support CI later

## Ordered workstreams

### 1. Separate dependency proof from quality cases inside the eval runner

Refactor `backend/src/source_lens_api/eval_smoke.py` into clear phases:

1. dependency preflight
2. eval fixture setup
3. case execution
4. assertion summary

The implementation may stay in one module at first, but the control flow should stop looking like one long inline script.

### 2. Add repo-owned eval fixtures

Create a small fixture area such as:

- `backend/evals/fixtures/golden_source.md`

The grounded fixture should contain two or three distinctive facts or phrases that:

- are easy to retrieve semantically
- are easy to assert as evidence substrings
- do not depend on exact answer wording from the chat model

Keep the fixture small enough that failures are easy to debug from console output.

### 3. Add a minimal eval case model

Introduce a small Python structure for eval cases, for example under:

- `backend/src/source_lens_api/evals/cases.py`
- `backend/src/source_lens_api/evals/assertions.py`

Each case should define only what the runner needs:

- case name
- setup mode
- question
- expected grounding status
- expected evidence substrings
- optional answer substring checks

Do not build a plugin system or generalized manifest loader for Phase 5.

### 4. Implement the grounded golden-path case

For the grounded case:

- copy the repo fixture into a controlled eval workspace
- import it through the existing import API or import service path
- wait for the import job to complete
- ask the configured question
- verify the result is `grounded`
- verify at least one evidence snippet contains an expected phrase from the fixture
- verify evidence belongs only to the imported source

This must exercise the real first-slice workflow rather than bypassing import with direct vector insertion.

### 5. Implement the weak-evidence baseline

Choose one deterministic weak case and lock it in. For this repo, prefer:

- create a completed source record with no vectors
- ask a question against that source through the normal ask service
- assert `grounding_status == "insufficient_evidence"`
- assert `evidence == []`

This is narrower than a future "weak retrieval quality" evaluation, but it matches the current behavior of the ask flow and avoids pretending the repo already has thresholded relevance logic.

### 6. Stabilize `tools/eval.ps1`

Keep `tools/eval.ps1` thin:

- call the Python eval runner
- preserve non-zero exit codes
- avoid embedding test logic in PowerShell

If the Python runner prints a final summary, PowerShell should pass it through without reshaping the result.

### 7. Add automated tests around eval-specific logic

Add narrow tests for:

- case construction
- evidence assertion helpers
- deterministic failure messages
- weak-case assertion behavior without live Ollama calls

These tests should stay fast and fake-backed. Live model integration belongs to `.\tools\eval.ps1`.

## Suggested file targets

The implementation can stay small if it lands roughly here:

- `phase-5-implementation-plan.md`
- `tools/eval.ps1`
- `backend/evals/fixtures/`
- `backend/src/source_lens_api/eval_smoke.py`
- `backend/src/source_lens_api/evals/cases.py`
- `backend/src/source_lens_api/evals/assertions.py`
- `backend/tests/`

## Acceptance checks

Phase 5 is complete when all of these are true:

1. `.\tools\eval.ps1` remains the canonical repo command and exits non-zero when either dependency proof or an eval case fails.
2. The eval command imports one repo-owned sample source through the real import path and asks one grounded question against it.
3. The grounded case asserts `grounding_status == "grounded"` and checks for at least one expected evidence phrase from the imported fixture.
4. The weak case asserts `grounding_status == "insufficient_evidence"` and returns no evidence snippets.
5. Eval-specific helper logic is covered by automated tests that do not require live Ollama calls.

## Verification path

Use these checks when implementing or reviewing Phase 5:

1. Confirm `phase-5-implementation-plan.md` still matches the locked Phase 5 scope in `plan.md`.
2. Run `.\tools\test.ps1` and confirm eval-helper tests pass without requiring live Ollama calls.
3. Run `.\tools\eval.ps1` and confirm both the dependency proof and the new quality cases pass on repo-local state.
4. Intentionally break one expected evidence substring and confirm `.\tools\eval.ps1` exits non-zero with a readable failure.

## First review pass after implementation

Before calling Phase 5 done, review the diff for:

- exact-answer assertions that are too brittle for local model variation
- grounded eval setup that bypasses the real import path
- weak-case setup that quietly depends on future retrieval-threshold behavior
- hidden dependence on machine-global paths instead of repo-local state
- PowerShell logic growing into a second eval implementation
- regressions to the dependency-proof behavior already carried by `eval`
