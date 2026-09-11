## Why

Ticket 03 needs repository-derived human authorization and exclusive run control. Ticket 02 currently trusts fixture actor IDs and has no lease or mutation fencing.

## What Changes

- Authenticate Operator requests with provider credentials and normalize effective repository read/contributor permissions, with GitHub as the first adapter.
- Persist one human Control Lease per run and atomically fence claim/release by attempt, run version, head, and epoch.
- Revalidate permissions on every request, expose current permitted decisions, and distinguish humans from technical process evidence and audit.
- Replace the public synthetic actor authorization path; retain synthetic issue/redaction inputs and the loopback harness capability.

## Capabilities

### New Capabilities
- `repository-control-lease`: Provider-derived access, durable exclusive control, mutation fencing, and authorization audit.

### Modified Capabilities
- `authorized-issue-observable-run`: Replace fixture actor authorization with current provider identity/permission while retaining synthetic issue admission.

## Impact

Only the isolated Microsoft pilot, its public HTTP/CLI tests, documentation, and Ticket 03 change. No provider writes, Azure calls, live repository mutations, or changes to the LangGraph pilot. Transfer/takeover and agent commands remain Tickets 08 and 07.
