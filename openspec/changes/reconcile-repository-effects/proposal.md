## Why

Ticket 05 closes the stale-local-base and manual-database-recovery failures from the earlier pilot. Ticket 04 supplies recoverable sessions but explicitly excludes repository effects and repository serialization.

## What Changes

- Pin repository execution configuration, record provider and local base evidence, and block before agent work when either base or predecessor completion is wrong.
- Journal controlled Git, provider and session operations with stable identities, readable receipts, crash adoption and explicit human conflict cases.
- Add fenced Retry, Reconcile, Adopt and Retire through the existing Operator HTTP/CLI surface; preserve history and release repository ownership on settled terminal outcomes.
- Prove the contract with real Git repositories, independent controlled HTTP providers, PostgreSQL and killed/replacement worker processes.

## Capabilities

### New Capabilities
- `repository-effect-reconciliation`: authoritative preflight, durable repository ownership and recoverable external effects with supported operator decisions.

### Modified Capabilities
None. Existing admission, authorization and fake-session requirements continue to apply.

## Impact

Only the isolated Microsoft Agent Framework pilot's domain, store, worker, API, CLI and tests. No live repository writes, merges, Azure resources or changes to the LangGraph pilot. Git and provider effect execution remains deterministic; the existing fake Agent Framework graph supplies the session step.
