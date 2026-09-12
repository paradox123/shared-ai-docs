## Context

Ticket 04 persists one recoverable fake session and exposes an attempt detail, but
the stored receipt is keyed once per run and opening is permanently
`unsupported`. Ticket 05 deliberately defines repository `retry` as recovery of
the same effect; it is not a new agent conversation. Ticket 06 needs an
Operator-controlled, durable continuation model without bypassing Ticket 03's
provider authorization, Control Lease, or CAS fences.

The public seam is the loopback API and Operator CLI. The controlled fake
adapter is the only session implementation in this ticket: it models capabilities
and receipts, but it must not impersonate a real Codex App integration.

## Goals / Non-Goals

**Goals:**

- Store a redacted, target-bound Human Request and session lineage durably.
- Make `resume`, `fork`, `fresh-retry`, explicit handoff, open, and write
  observable, fenced, idempotent operations in the same `ImplementationRun`.
- Let a replacement API/worker adopt persisted continuation intent and adapter
  receipt rather than creating a duplicate session or write.
- Prove behavior through separate API/CLI/worker/fake-provider processes and
  disposable PostgreSQL, never through table inspection.

**Non-Goals:**

- Real Codex App/App Server integration, a graphical Operator UI, live GitHub
  or repository writes, control transfer/takeover, generic live-control command
  queueing, and automatic continuation without an explicit human decision.
- Reinterpreting Ticket 05 `retry`, replacing the old LangGraph intervention
  flow, copying a full transcript into a fresh retry, or storing unredacted
  user/session data.

## Decisions

- Add a versioned `HumanRequest` record keyed by immutable request ID and bound
  to one run, target attempt, session, phase, expected head, problem, evidence,
  allowed actions, and state. The worker creates it atomically with the blocked
  attempt result; projections and attempt detail expose it after restart.
- Model a continuation decision as an immutable command identity plus a
  redacted digest. Under the existing run row lock, provider revalidation,
  lease/attempt/version/head/epoch checks, command idempotency, canonical event
  append, operation intent, and request state change happen atomically. Reusing
an ID with a differing decision conflicts; replaying it returns its original
outcome. Adapter completion accepts only a versioned receipt whose operation
identity matches that durable intent; write completion additionally matches the
redacted canonical message.
- Keep every session receipt per attempt, rather than the current one-receipt
  per-run assumption. `Resume` reuses the target receipt/session ID; `Fork` and
  confirmed `Handoff` create a new attempt/session with a parent session ID;
  `Fresh Retry` creates a new attempt/session whose ancestry/import are null.
  The adapter receives only a stable operation key and derives identities itself.
- `Open in Codex` is a read-authorized, side-effect bounded operation. A
  same-session-supported capability opens only the selected session and records
  a correlated observation. Provider revalidation and durable open intent share
  the same serialized run decision. A capability requiring handoff returns the reason
  and performs no fork until a separately fenced confirmation; unsupported
  capability has no URL or hidden fallback.
- Opened-session writes use the same command-id/fence transaction as decisions,
  then a durable adapter operation/receipt. The command digest is derived from
  the same redacted canonical message that reaches the adapter. Redacted message, tool, result and
  decision events retain the original run and attempt correlation. The fake
  adapter is deliberately used to prove this port instead of granting an API
  caller authority to invent session events.

## Risks / Trade-offs

- [Schema change can disturb old one-session rows] → retain old receipt JSON,
  migrate the table to per-attempt rows, and read legacy data by its attempt.
- [Adapter effect succeeds before local commit] → persist operation intent first
  and use independent fake-adapter receipt lookup/adoption on replacement.
- [A visible open could be mistaken for a mutation] → narrow its contract to
  opening observation only; phase, head, effects and session identity stay fixed.
- [A fake capability could overclaim production support or leak adapter text] →
  capability projection is redacted before persistence, names the controlled
  adapter, and never returns a real Codex URL.

## Migration Plan

1. Make `EnsureSchemaAsync` expand existing pilot tables safely for the new
   Human Request, command, operation, lineage and per-attempt receipt model.
2. Preserve existing Ticket 04 session rows and events; newly created requests
   use the new tables and old runs remain readable.
3. Roll back only by deploying the prior binary before a new continuation is
   accepted; already-created records remain append-only and readable.

## Open Questions

None for the controlled pilot. Ticket 10 determines whether a real Codex
adapter can safely advertise same-session opening.
