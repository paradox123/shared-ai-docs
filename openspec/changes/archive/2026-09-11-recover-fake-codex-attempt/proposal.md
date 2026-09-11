## Why

Ticket 04 needs an external fake Codex attempt whose failure remains diagnosable after worker replacement. Admission and repository control exist, but the worker currently reports only lifecycle evidence and cannot recover an agent session or preserve rejected results.

## What Changes

- Add a versioned external fake session adapter, deterministic preparation, stable attempt/session correlation and replay-safe observation ingestion.
- Persist redacted observations before interpretation; distinguish failure categories and semantic rejection.
- Expose attempt detail and truthful Open in Codex capabilities through authenticated HTTP and CLI.
- Prove worker death in the session/result gap, concurrent recovery, and independent operator read-back.

## Capabilities

### New Capabilities
- `recoverable-fake-codex-attempt`: external fake execution, recovery, lossless diagnostics and attempt selection.

### Modified Capabilities
None. This adds execution to the existing admission/control contracts.

## Impact

The isolated Microsoft Agent Framework pilot's domain, PostgreSQL store, worker, API and CLI, plus an external deterministic fake fixture and process-level tests. Existing Ticket 03 changes are preserved. No real Codex, repository write, human control command, or Azure provisioning is introduced.
