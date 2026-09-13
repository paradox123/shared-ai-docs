## Why

Agent Framework pilot issue 13 requires an evidence-ready draft to become review-ready only for one immutable head. Publication currently stops before independent review and has no bounded writer repair loop.

## What Changes

- Add an opt-in qualification contract to the trusted publication plan, with executable verification and pinned reviewer skills.
- Persist head-bound verification, three isolated Codex review results, invalidation, and up to three repairs using the original writer and worktree.
- Recapture evidence and update the existing draft for each repair head; retain a concrete Human Request on failure or exhaustion.
- Expose all results through authenticated run read-back and export. Qualification means readiness for human review only.

## Capabilities

### New Capabilities

- `agent-framework-head-qualification`: Durable qualification and bounded repair for the .NET pilot, carrying forward the independent-review and bounded-repair behavioral baseline.

### Modified Capabilities

None. The LangGraph-specific baseline remains unchanged.

## Impact

Touches the isolated Agent Framework pilot's publication worker, PostgreSQL publication projection, Codex adapter, trusted plan validation, tests and operator documentation. No new service dependency, merge, deployment or release action.

Owning Git root: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`; current and intended target branch: `main`; starting commit: `688d92d2680eda5cf92c03b8d03da26d2dde08d9`. Existing README/Renovate changes are outside scope. No active OpenSpec change matched issue 13; this change owns the new runtime and persistence behavior.
