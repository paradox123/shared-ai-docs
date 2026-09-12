## Context

Ticket 08 extends the accepted Ticket 03/06/07 boundaries and ADRs 0003/0007. The owning Git root is `shared-ai-docs`; the initial checkout is `codex/continue-human-requests-in-codex` at `df43a56` with unrelated dirty documentation. Implementation uses the isolated worktree `shared-ai-docs-ticket-08`, branch `codex/transfer-run-control`, based on `df43a56`, which is also the review baseline. No matching active change existed at the routing gate.

## Goals / Non-Goals

Goals: durable request/decision, one winner per expected epoch, contributor-only forced takeover, truthful observation and old-controller fencing across hosts/restarts.
Non-goals: process/window ownership transfer, real Codex integration (Ticket 10), live multi-account acceptance (Ticket 14), automatic dispatch, merge/deployment or an administrator role.

## Decisions

- Use the existing PostgreSQL run row lock for the complete provider-revalidated decision. Persist one current transfer request on the run, addressed by a UUID and its original holder/epoch. A new request cannot silently replace a pending request. Request/reject advance run version only; ownership changes advance epoch once. The existing ControlMutation fences remain required. Repeated deliveries cannot cause another transition.
- A requesting observer must have contributor permission (ADR 0007). Persist the provider login only as a lookup hint; approval rechecks target permission and immutable subject ID using the holder's request-scoped credential. No requester credential or membership cache is stored.
- Add `request-transfer`, `approve-transfer`, `reject-transfer`, `force-takeover`. Each requires a reason; request/decisions also address a transfer request UUID. Read-back includes pending request and permitted actions. History includes previous/new holder, time, reason, mode and request identity.
- Distinguish pending operator work from already accepted external effects. Before switching, fence pending session operations at the controlled adapter by immutable operation key: a durable tombstone prevents a delayed write/start; an already-existing receipt is preserved and reconciled before a retry of the ownership decision. Unknown/malformed fencing fails closed. No transfer-created session, attempt, head or workflow transition is allowed.
- Serialize session dispatch with the run row lock, re-read the durable command before calling the adapter, and never redispatch a fenced command on restart. Pending live queue entries are invalidated while the current autonomous operation and its session remain unchanged. An already accepted continuation/repository recovery or a live command promoted to current operation must settle its existing receipt before handover; an explicit conflict prevents orphaning that decision. Session-write success gaps are reconciled once and require fresh fences before retrying transfer.
- Test through public HTTP/CLI, real disposable PostgreSQL, separate API/worker/adapter processes. Use independent adapter diagnostics and controlled delay/crash boundaries, never private SQL assertions.

## Risks / Trade-offs

- Provider/adapter availability is required to safely settle an uncertain pending effect; failures leave ownership unchanged and inspectable.
- Adapter tombstones are durable external safety state. If a database transaction rolls back after fencing, retries must converge on that tombstone instead of recreating the operation.
- Row locks across bounded adapter requests serialize takeover with dispatch, increasing decision latency but avoiding an unlocked authorization-to-effect gap.
- Old processes continue to display their session; every new writing action still passes the current lease. Controlled fixtures do not claim real Codex App fencing.

## Verified provider contract

GitHub's [repository permission endpoint](https://docs.github.com/en/rest/collaborators/collaborators#get-repository-permissions-for-a-user) reports effective base permission (`write` also represents maintain) and recipient identity, and supports Metadata read permission. Checked 2026-09-12. Production adapter behavior is verified against a controlled HTTP fixture, not a live provider account.

## Migration Plan

Add nullable transfer state and allow a fenced continuation state through idempotent schema initialization. Existing completed operations remain untouched. Stop old API/worker binaries before upgrading; mixed-version writers are not supported. No live database is changed by this task.
