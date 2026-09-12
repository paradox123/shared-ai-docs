## Why

Ticket 04 makes a failed fake Codex attempt inspectable, but a second authorized
operator cannot yet make its concrete session reachable or decide safely how to
continue it. The prior LangGraph intervention pattern created a separate
read-only summary task; it is not a substitute for targeted session continuation
in the shared `ImplementationRun` history.

## What Changes

- Persist a redacted, target-bound Human Request before a run waits, including
  the attempt, session, phase, expected head, problem, evidence and permitted
  actions; show it through the Operator API and CLI after API or worker restart.
- Add fenced, durably idempotent Resume, Fork and Fresh Retry decisions. Resume
  preserves the original session, Fork records explicit session ancestry, and
  Fresh Retry starts without importing the old conversation.
- Make `Open in Codex` truthful and side-effect bounded: a supported adapter
  opens only the selected session; an unsupported direct display exposes its
  limitation and requires a separately confirmed, lineage-marked handoff.
- Route write-capable interaction only through the current holder's Control
  Lease, fresh repository authorization and current run/attempt/head/epoch
  fences; persist its redacted messages, tools, results and decisions in the
  same run history.
- Journal continuation operations and adapter receipts so replacements recover
  one logical effect rather than creating duplicate sessions or interactions.

## Capabilities

### New Capabilities

- `human-request-codex-session-continuation`: Durable targeted Human Requests,
  continuation choices, truthful session opening and lease-fenced interaction.

### Modified Capabilities

- `recoverable-fake-codex-attempt`: Replace the fixed fake-only opening result
  with per-attempt truthful capabilities and durable continuation lineage.
- `repository-control-lease`: Apply the existing atomic authorization and
  fencing rule to Human Request decisions, handoffs and opened-session writes.
- `repository-effect-reconciliation`: Treat continuation/session operations as
  journaled, recoverable controlled effects with stable identities and receipts.

## Impact

Changes are limited to `microsoft-agent-framework-work-package-pilot` domain,
PostgreSQL storage, controlled fake session adapter, API/CLI and process-level
black-box tests. This neither starts real Codex sessions nor changes live
repositories, GitHub, merges, deployments, or the LangGraph pilot.
