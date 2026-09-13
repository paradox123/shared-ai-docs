## Why

Ticket 10 is the first real Codex runtime boundary after the controlled session,
repository, live-command and dossier slices. Fake receipts cannot establish
schema compatibility, session recovery or safe interactive Codex access.

## What Changes

- Pin the installed Codex executable and public protocol; probe prerequisites in
  an isolated disposable repository before admitting real issue work.
- Keep worker-result-v3 complete and derive a separate endpoint schema whose
  acceptance must be tested against the real endpoint.
- Record session identities, process ownership, recovery uncertainty and explicit
  unsupported capabilities. A missing safe Codex surface stops the candidate.
- Expose preflight evidence through the existing authenticated Run History.
- Only enable issue execution and interactive access when all required runtime,
  observability and lease/fencing capabilities have executable evidence.

## Capabilities

### New Capabilities
- `real-codex-runtime-gate`: fail-closed admission of the pinned real runtime.

### Modified Capabilities

## Impact

Only the sibling Microsoft Agent Framework pilot, its tests, and Ticket 10.
No changes to LangGraph, its services/data, remote repositories or deployments.
