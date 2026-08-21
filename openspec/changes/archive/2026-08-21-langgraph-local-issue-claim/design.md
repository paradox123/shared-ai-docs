## Context

`shared-ai-docs` has the pilot requirements and operating guidance but no runtime package. This slice introduces the first executable control-plane boundary: a signed GitHub delivery enters a local durable inbox, becomes one persistent LangGraph thread when its issue is eligible, and produces an idempotent `agent-running` GitHub projection. The pilot is local and single-process for now, but must survive process restart and must not acknowledge accepted work before it is durable.

## Goals / Non-Goals

**Goals:**

- Authenticate and bound the raw request before JSON interpretation, then enforce explicit repository/event/action allowlists.
- Atomically persist an accepted delivery by its GitHub delivery ID before a positive response is sent.
- Claim an eligible issue as exactly one active run, persist LangGraph checkpoints in SQLite, and project `agent-running` through a GitHub port.
- Make delivery, run, claim, and checkpoint state observable through the productive HTTP interface after restart.
- Prove behavior at that interface with real SQLite storage and controlled external-boundary adapters.

**Non-Goals:**

- Cloudflare Worker, Queue, Tunnel, retry, or dead-letter implementation.
- Worktree creation, Codex execution, evidence production, reviews, pull requests, or merge handling.
- Startup reconciliation, macOS launch automation, multi-repository scheduling, or production-scale database operation.
- Inventing a second authorization label beyond `ready-for-agent`.

## Decisions

### Use a small Python HTTP application as the public workflow interface

The package exposes `POST /webhooks/github` and `GET /workflows/{owner}/{repository}/issues/{number}`. The webhook reads a bounded raw body, verifies `X-Hub-Signature-256` with constant-time HMAC comparison, and only then parses JSON. FastAPI supplies the HTTP seam and request/response validation without making framework internals part of the domain interface.

Alternative considered: a CLI-only receiver. It would make the eventual Queue/Tunnel handoff and HTTP acceptance semantics indirect, so it is not the productive seam required by the issue.

### Separate durable acceptance from background dispatch

The request transaction inserts the immutable delivery envelope into an `inbox_deliveries` table keyed by `X-GitHub-Delivery`, commits it, and only then returns `202`. A duplicate with the same body digest returns `200` and schedules no work; reusing an ID with a different body returns `409`. A background dispatch starts only for a newly committed row.

Alternative considered: running the graph before replying. That couples GitHub acknowledgement latency to processing and weakens the explicit “persist before positive response” boundary.

### Keep orchestration records and LangGraph checkpoints in one SQLite database

Application tables record delivery status, issue-to-run ownership, and claim projection. LangGraph's `SqliteSaver` uses a separate thread-safe connection to the same database for actual graph checkpoints. The graph thread ID is the persisted run ID. SQLite WAL mode and explicit transactions provide a durable local pilot implementation; the package creates its schema idempotently on startup.

Alternative considered: an in-memory checkpointer plus application rows. That would label a row as a checkpoint without using real LangGraph persistence and would not prove restart recovery of the workflow itself.

### Claim through database uniqueness and an idempotent GitHub port

An `issue_runs` uniqueness constraint gives each repository/issue one run, and a partial unique index permits at most one `running` run per repository. Dispatch asks the GitHub port for current issue eligibility (`ready-for-agent`, open blockers, open state), obtains or creates the run in one transaction, and invokes the graph under that run ID. The claim node calls an idempotent `ensure_label` port and records `agent-running` in graph state and the application projection row.

Alternative considered: treating the webhook payload as the eligibility source. GitHub events are snapshots and can arrive late; reading through the port keeps the claim decision tied to current controlled state.

### Inject only external seams

The application factory accepts a GitHub port and a clock. Production uses an HTTP GitHub adapter configured by token and API base URL; tests use a deterministic adapter. Deliveries are driven through the real HTTP application, and storage plus LangGraph remain real rather than mocked. This keeps tests independent of node ordering and private helpers.

### Return a workflow read model, not database internals

The GET route returns domain fields: delivery identity/status, run identity/status, projected labels, and the latest LangGraph checkpoint values. It obtains checkpoint values through the compiled graph's state interface. Table names, checkpoint serialization, and node sequence remain hidden.

## Risks / Trade-offs

- [SQLite and synchronous graph execution do not scale to multiple receiver processes] → Constrain this slice to the local single-process pilot and keep persistence/ports replaceable.
- [A crash can occur after GitHub applies a label but before local projection is recorded] → Require `ensure_label` to be idempotent and allow replay against the same run without a duplicate visible claim.
- [Background execution can outlive an HTTP request] → Persist first, record dispatch failures durably, and expose them in the read model; later operational slices can add retry supervision.
- [A database file can contain webhook payload data] → Persist only the fields needed for correlation and dispatch, store a body digest, and never persist secrets or request signature values.
- [Dependency security changes over time] → Resolve a lockfile and require a fixed `langgraph-checkpoint-sqlite` release containing the SQLite metadata-filter injection fix; the application never accepts user-controlled checkpoint filter keys.

## Migration Plan

1. Add the isolated package and lockfile without changing existing repository workflows.
2. Configure a local database path, webhook secret, allowed repository, and GitHub token outside version control.
3. Start the application and exercise signed test deliveries through the local endpoint.
4. Roll back by stopping the application and removing its untracked runtime database; no existing repository data is migrated.

## Open Questions

None for this slice. Queue delivery, retry supervision, and production launch behavior belong to later pilot issues.
