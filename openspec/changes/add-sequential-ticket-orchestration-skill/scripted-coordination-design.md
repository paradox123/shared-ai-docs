# Scripted coordination extension (2026-09-21)

Owning Git root: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`. Target: `main`, explicitly confirmed by Daniel. Working branch: `codex/scripted-ticket-coordination`. Preserve the earlier uncommitted event-protocol extension. No push, merge, live-batch migration or automation mutation is part of this implementation.

## Interface and ownership

Extend the existing standard-library CLI with a managed coordination ledger and cohesive commands. The public CLI with real temporary files is the test seam. Keep the existing low-level helpers compatible for old ledgers, but reject their writes to a managed ledger so normal callers cannot bypass workflow checks.

- `coordinate --ledger ... --expect-revision ... --input ...` processes one local operation: initialize, prepare an external command, record its outcome, consume a worker event (optionally with a next decision), advance a verified phase, change capacity reservations, or record bounded observation/recovery facts.
- `report --packet ... --result ... --status ...` binds a durable worker result to its generated assignment and allocates the next event sequence. It returns callback text; it does not send it.
- `status --ledger ...` returns the current revision and compact actionable context without full history or repeated instructions.

The coordinator supplies substantive decisions and evidence references. Code enforces lifecycle prerequisites, identity/correlation, capacity, immutable receipts and revision-checked atomic bookkeeping. Unknown sends remain pending until inspected and explicitly resolved. Mechanical success is not acceptance or authority to call an external tool.

## Invariants and scope

One managed file owns each batch's ticket states, current requests, command packets, receipts and reservations. Packet/event files are immutable; commands may only be dispatched after their recorded preparation succeeds. An interrupted local publication is recovered through the existing pending command and the same request ID. Confirmed worker identities remain coordinator-verified facts; provisional task creation never grants implementation readiness. Dependencies/conflicts are declared by the coordinator and enforced mechanically; code does not infer semantic overlap.

A decision-ready event does not automatically accept work, move a phase or release capacity. Acceptance is bound to its reported content identity. Integration preparation remains distinct from a merge grant; preparation results and grants bind content and tested target. Actual target freshness, permissions, quiescence, remote delivery and evidence quality require live coordinator checks and recorded proof.

Use a new managed schema for new batches only. Existing ledgers and live workers remain untouched; adoption requires explicit reconciliation outside this implementation. No scheduler/daemon, task API adapter, database or external dependency is introduced. Callback wake liveness remains a runtime concern.

## Documentation outcome

Replace repeated low-level recipes with the cohesive CLI interface; preserve authority, evidence, integration and cleanup decisions. Load recovery and cleanup details only when needed. Measure before/after instruction words and exercise realistic CLI scenarios. Implementation readiness and acceptance-triggered technical completion remain separate.
