## Why

Ticket 08 needs two contributors to change responsibility for a running work package without overlapping writing rights. Claim/release alone cannot provide an atomic handover, and restart delivery of pending session commands currently outlives the accepting lease.

## What Changes

- Add durable transfer request, holder approval/rejection and explicit forced takeover through Operator HTTP/CLI.
- Serialize ownership changes with current request, attempt, version, head and epoch checks; preserve workflow/session/effect identity.
- Fence pending old-lease mutations and serialize session adapter dispatch with ownership changes.
- Record redacted reasons, immutable previous/new human identities, time and transfer mode in canonical history.

## Capabilities

### New Capabilities
- `atomic-run-control-transfer`: durable transfer decisions, forced takeover and old-controller fencing.

### Modified Capabilities
- `repository-control-lease`: add the explicitly authorized transfer/takeover exceptions to holder-only control.

## Impact

The isolated .NET pilot's domain contracts, PostgreSQL store, Operator API/CLI, controlled provider fixtures and public process tests. No live credentials, real Codex integration, managed dispatch, merge or deployment are introduced. Source: `.scratch/distributed-codex-work-package-control-plane/issues/agent-framework-pilot/08-steuerung-atomar-uebertragen-oder-uebernehmen.md`.
