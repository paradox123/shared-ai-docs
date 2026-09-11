## Context

Ticket 02 owns canonical history in PostgreSQL. Ticket 03 adds fresh repository authorization and row-locked control decisions. The external-agent slice must preserve both, including unrelated uncommitted work. ADR 0002 separates Operator Clients from agent sessions; ADR 0008 keeps Codex behind an adapter and deterministic work in regular executors.

## Goals / Non-Goals

Goals: one recoverable external fake session, lossless redacted observations, typed failure diagnostics, and authenticated attempt selection. Non-goals: real Codex invocation, resume/fork/live control (Tickets 06/07), Git/provider effect reconciliation (Ticket 05), and new managed infrastructure.

## Decisions

- Use a typed Agent Framework graph with deterministic preparation and an external fake adapter executor. The bounded local worker command explicitly delivers/re-delivers the graph; PostgreSQL receipts make completed preparation and the logical attempt reusable. The already-proven managed DTS probe remains separate; local replacement evidence is not a claim of automatic DTS scheduling of this new graph.
- Persist an attempt/start intent before the external HTTP call. `AgentSessionAdapter/v1` uses the attempt ID as an idempotent session operation key. The fake provider runs outside the worker, persists its session independently, and supports read/adoption by that key. A retry can never request a fresh key implicitly. Conflicting identity or transcript fails closed.
- A dedicated PostgreSQL session advisory lock serializes worker deliveries for one run while short row-locked transactions append canonical events and update state. Process death releases the worker lock. Human control uses the existing row lock; workers neither claim nor impersonate the human lease.
- External events have contiguous source sequence, type and causal predecessor, stable run/activity/attempt/session IDs. Store each redacted original before validation/interpretation. Deduplicate equal replay; reject conflicting replay or gaps. Session state is distinct from activity processing state.
- Valid blocked output remains `AgentResultObserved`, with a separate `AgentResultRejected` for configured downstream evidence rejection. Process, timeout, transport, contract, schema, blocked, semantic rejection and infrastructure categories are public. Store outages return an infrastructure code at the available process/API boundary; they cannot promise to append to unavailable storage.
- Attempt detail includes history selection, provenance, session status and explicit `openInCodex` capability (`unsupported`, no URL, same-session false, app-task visibility false). It never creates an app task or silently forks. Existing repository-read authorization guards the route.

## Risks / Trade-offs

- Provider receipts are necessary for the external-success/local-commit gap → independently durable fake service, process-kill tests both before and after local session mapping.
- A local driver is not managed scheduler evidence → document the delivery boundary explicitly; preserve the existing DTS gate.
- Controlled redaction is not general DLP → exercise configured canaries across message, tool, artifact, error and result values before persistence/output.
- Preview framework APIs → reuse the pilot's pinned Workflows version; lock dependencies and validate the real process surface.

## Migration Plan

Add a session receipt table without changing historical admission rows. Keep lifecycle-only worker invocation compatible; fake execution requires explicit adapter origin. Rollback disables that invocation mode and retains historical events. No live database migration or external resource mutation is required.
