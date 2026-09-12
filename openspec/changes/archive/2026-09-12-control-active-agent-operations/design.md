## Context

Ticket 06 persists waiting sessions and idempotent continuation receipts. Its run-wide delivery lock and latest-attempt control context cannot represent parallel live operations. Ticket 07 adds an independently executable live fake-adapter path alongside the existing blocked-result proof.

## Goals / Non-Goals

**Goals:** Durable attempt-addressed commands, observable process stop, ordered replies, replacement-worker delivery and fencing of late receipts.

**Non-Goals:** Real Codex integration (Ticket 10), lease transfer (Ticket 08), managed DTS scheduling, repository writer execution or automatic repair. The live fixture has no repository write capability; its reconciliation receipt proves the empty effect set. Nonempty/conflicting effects block delivery rather than implying successful reconciliation.

## Decisions

- PostgreSQL serializes acceptance with the existing run row lock and repository permission revalidation. Commands require explicit attempt, command UUID, current version/head/lease; interrupt/cancel also require a reason. CLI exposes all targets and does not silently choose the latest attempt.
- A persisted live operation contains run/activity/attempt/session, stable adapter operation key, process status and operation fence epoch. A FIFO inbox stores redacted messages and durable acceptance positions. Interrupt reserves the next slot ahead of queued commands; a second pending interrupt is rejected. Cancel supports explicit `operation` or `attempt` scope: operation cancellation terminates only the current operation and permits previously queued work; attempt cancellation explicitly rejects pending commands and admits no retry.
- External delivery uses stable idempotency identities and immutable payloads. Workers read attempt snapshots for bounded delivery passes and serialize receipt adoption under the run row lock; adapter idempotency and operation fences permit concurrent replacement without exclusive worker ownership. No delivery lock is held while an external operation runs. A replacement worker can start/read/stop/reconcile/deliver from the persisted state. API accepts commands without binding them to an HTTP response or original worker.
- Stop intent and fence advancement commit together before the adapter call. The adapter persists a stop tombstone even if start has not arrived, then returns a stopped-process receipt and an explicit reconciled effect set. Delivery waits for that receipt. A saved old operation receipt can append redacted late evidence but cannot alter current operation, run state or head.
- The external fake service owns durable SQLite receipts and actual child processes. Public fixture completion controls the child for deterministic process tests. CLI/API provide read-back; tests do not query product tables. Existing fake/continuation behavior remains regression-tested.

## Risks / Trade-offs

- Adapter exactly-once effects require idempotent start/stop/message receipts → reject mismatched identities and effects; preserve pending work on unavailable/invalid responses.
- This pilot uses explicit worker delivery invocations → document replacement invocation; DTS/real Codex proof remains separate.
- Concurrent repository writers would require repository-effect integration → reject live registration on a registered repository and repository registration while an external live process remains active; live operations are isolated non-writing attempts.

## Migration Plan

Add tables and optional projection fields with backward-compatible schema initialization. No live database migration is performed. Existing records retain their behavior. Rollback stops the new worker mode and retains durable command/history records.
