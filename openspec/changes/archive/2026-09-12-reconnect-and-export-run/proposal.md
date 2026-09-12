## Why

Ticket 09 requires a failed run to remain completely observable from another
client and portable after its API and worker disappear. Current history reads
are unbounded and artifact references do not preserve their bytes.

## What Changes

- Add bounded cursor pages and an authenticated SSE tail over canonical history.
- Preserve redacted large observations and binary artifacts outside workflow state
  in an immutable content-addressed store, with versioned availability evidence.
- Export a versioned ZIP/JSON run dossier and restore it into fresh local storage
  for authenticated historical read-back, without executing the original workflow.
- Expose artifact integrity as a prerequisite for later qualification.
- Prove restart/reconnect over more than 10,000 events, large output, failure,
  controlled-canary absence, and public checksum parity after restore.

## Capabilities

### New Capabilities
- `portable-run-dossier`: Reconnect, immutable artifacts, portable export and restore.

### Modified Capabilities

## Impact

The isolated .NET pilot's Domain, PostgreSQL store, API, worker, CLI, and process
tests change. Existing LangGraph runtime and managed DTS dispatch remain separate.
