## Context

The local receiver already persists every accepted webhook delivery in SQLite, runs one repository workflow at a time, and recovers non-terminal runs before the FastAPI lifespan accepts traffic. Cloudflare Queue covers only the first 24 hours of an outage. After that boundary the receiver needs a one-shot current-state read, but it must preserve the same inbox, dispatch, run, and crash-recovery semantics as webhook work.

The process-start time is not a reliable Mac-boot identity: launchd or a supervisor can restart the pilot multiple times without rebooting macOS. Conversely, a boot may follow a long power-off period in which no heartbeat could be written. The boundary therefore needs both a durable liveness timestamp and an operating-system boot-session provider, with both injected in behavior tests.

## Goals / Non-Goals

**Goals:**

- Evaluate the offline interval once per operating-system boot and start one durable reconciliation run when the last known liveness is at least 24 hours old.
- Resume an interrupted reconciliation under the same boot/run identity without starting a second run.
- Read current ready/authorized issues and the persisted active run's associated pull request through repository-adapter boundaries.
- Represent recovered readiness and human-merge facts as deterministic synthetic commands accepted by the ordinary inbox and executed by ordinary dispatch.
- Deduplicate a synthetic command and a later transport delivery by semantic command identity while retaining each real `X-GitHub-Delivery` receipt.
- Expose bounded reconciliation state through existing workflow read-back and keep normal operation event-driven.

**Non-Goals:**

- Periodic GitHub polling, replacement of Cloudflare Queue, or replay of GitHub's historical event stream.
- Recovery of arbitrary deleted comments or transient GitHub events that are not represented by current issue/pull-request state.
- Multiple hosts, distributed reconciliation leadership, macOS launchd installation, process supervision, merge, deployment, or release.
- Replacing the existing workflow crash-recovery path or repository scheduling policy.

## Decisions

### Use an injected OS boot-session provider plus a local heartbeat

Production resolves one stable ID for the current OS boot (`kern.boottime` on macOS, with the Linux kernel boot ID supported for tests/development). `create_app` accepts an injectable provider. SQLite stores `last_alive_at` and one evaluation row per boot ID. Startup atomically reads the prior timestamp, records the boot evaluation, and advances liveness; a lightweight local heartbeat and graceful shutdown update only SQLite and never call GitHub.

On a first-ever start, a missing prior timestamp is recorded as `not_required` because no known offline interval can be measured. A gap of exactly 24 hours qualifies. A shorter or negative gap does not. Once a boot has been evaluated, later process starts reuse that row. A `running` reconciliation is resumed under the same row; `completed` or `not_required` is not re-executed.

Using process UUIDs was rejected because they cannot distinguish supervisor restarts from Mac boots. Using wall-clock gap alone was rejected because a second restart in the same long-running boot could incorrectly trigger reconciliation.

### Reconcile before ordinary crash recovery and before serving HTTP

FastAPI startup first claims or resumes the current boot's reconciliation, then runs the existing non-terminal workflow recovery, then begins serving requests. Reconciliation processes active pull-request completion facts before ready-issue wake commands so a terminal GitHub state can prevent stale work from being resumed and can release the repository slot. Startup remains single-process and synchronous, matching the existing recovery boundary.

Running ordinary crash recovery first was rejected because an expired human-merge webhook could leave GitHub terminal while the pilot unnecessarily resumes machine work.

### Separate transport receipts from semantic inbox commands

`inbox_deliveries` continues to persist every real `X-GitHub-Delivery` and detect same-ID body conflicts. An additive command ledger stores one canonical semantic command key and its first source. Webhook parsing and reconciliation generate the same key for the same observable fact, such as a ready issue or a human-merged pull request at an exact head. A new transport receipt whose command already exists is acknowledged as already accepted and is not dispatched again.

Synthetic delivery IDs are deterministic from boot ID and command key, contain no payload data, and enter through the same store acceptance and `WorkflowRuntime.dispatch` path. Existing run uniqueness, completion guards, and operation ledgers remain the downstream defense in depth.

Deduplicating only by synthetic delivery ID was rejected because a delayed Queue delivery has GitHub's different transport ID. Skipping the inbox for reconciliation was rejected because it would create a second scheduling and persistence path.

### Keep current-state discovery behind the repository adapter

The adapter exposes a bounded reconciliation snapshot: ready or otherwise already-authorized open issues, and current pull-request facts only for the pilot's persisted active publication. The GitHub HTTP adapter reuses the existing issue/backlog and pull-request endpoints and returns typed, payload-minimized facts. The workflow core converts those facts into repository-neutral commands; it does not branch on `probare-crm`.

The first slice recovers facts expressible by current state: repository scheduling readiness and human merge completion. It does not infer missing historical comment/review events whose current meaning is ambiguous.

### Record bounded status, counts, and command identities

The boot reconciliation row records boot ID, prior/current liveness, measured gap, status/outcome, and discovered/accepted/deduplicated command counts. The command ledger stores generated identity, repository, issue/PR correlation, kind, and timestamps—not webhook bodies, issue bodies, feedback, tokens, actor email, or arbitrary exception strings. Existing workflow GET read-back includes the latest repository reconciliation summary.

## Risks / Trade-offs

- [The process can die during reconciliation] → Persist the boot row as `running` before GitHub reads and resume the same row; semantic command uniqueness and existing workflow ledgers make replay convergent.
- [A delayed Queue delivery races startup] → The lifespan does not accept HTTP until reconciliation completes, and the semantic command ledger handles either pre-existing Queue-first state or post-startup Queue-second state.
- [A heartbeat can be slightly older than the actual crash] → Use a short bounded interval and update on graceful shutdown; the threshold remains intentionally conservative around the last durable proof of life.
- [The wall clock moves backward] → Treat a negative interval as not qualifying and record the bounded outcome.
- [GitHub is unavailable during qualifying startup] → Leave the same boot reconciliation `running`/failed-retryable so a process restart resumes it rather than allocating another run; do not mark it complete with partial discovery.
- [Current state cannot reconstruct every historical event] → Reconcile only readiness and active human-merge facts with unambiguous current meaning; retain Queue/DLQ diagnostics for event-only gaps.

## Migration Plan

1. Deploy additive liveness, boot-run, and command-ledger tables plus the boot-ID provider.
2. The first startup records liveness and the current boot as `not_required`; no historical scan is guessed without a prior timestamp.
3. Later qualifying boots run reconciliation before ordinary recovery and HTTP acceptance.
4. Rollback can remove the startup caller while leaving additive rows inert; the existing delivery inbox and workflow data remain readable.

## Open Questions

None for this single-Mac, single-process pilot slice.
