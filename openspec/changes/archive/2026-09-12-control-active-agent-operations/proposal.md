## Why

Ticket 07 needs durable control of a running business attempt. The existing Human Request continuation controls waiting sessions, but has no ordered live inbox, process stop receipt, or operation fence.

## What Changes

- Accept targeted queue, interrupt and scoped cancel commands under the current repository authorization and Control Lease.
- Persist acceptance order, delivery identity, process lifecycle, reconciliation and replies in the same Run History.
- Recover accepted commands on replacement workers; reject stale output from canonical state updates.
- Prove parallel targeting and crash recovery using the local external fake adapter and real PostgreSQL/API/worker processes.

## Capabilities

### New Capabilities
- `active-agent-operation-control`: Attempt-targeted live commands, durable delivery, cancellation, process fencing and observable recovery.

### Modified Capabilities

None. Existing Human Request and repository-effect contracts remain applicable.

## Impact

The isolated .NET pilot's domain, PostgreSQL store, API, Operator CLI, worker and external fake fixture. No new framework dependencies, live provider writes, Codex task creation or changes to the LangGraph pilot. Real Codex integration remains Ticket 10.
