## Why

The pilot currently documents how an authorized `probare-crm` issue should enter the local control plane, but it has no executable ingress or persistent workflow. The first implementation slice must make one authenticated, authorized delivery durable and observable as exactly one claimed run before later worktree and review slices can build on it.

## What Changes

- Add a local HTTP workflow interface that accepts signed GitHub issue-label deliveries only for explicitly configured repositories, events, and actions.
- Persist each accepted delivery atomically by `X-GitHub-Delivery` before returning success, with a request-size limit and rejection paths that have no durable or GitHub effect.
- Dispatch an unblocked issue carrying `ready-for-agent` into exactly one persistent LangGraph run and project the `agent-running` label through a GitHub adapter.
- Expose persisted delivery, run, checkpoint, and claim state through the productive workflow interface so restart recovery and idempotency are directly observable.
- Add behavior tests using real SQLite inbox and LangGraph checkpoint persistence with controlled GitHub, clock, and delivery adapters.

## Capabilities

### New Capabilities

- `local-github-issue-claim`: Authenticated local delivery acceptance, durable idempotent issue claiming, persistent LangGraph execution, and workflow-state observation for the `probare-crm` pilot.

### Modified Capabilities

None.

## Impact

- **Write-set:** a new Python package under `langgraph-github-issue-pilot/`, its behavior tests and dependency metadata, the new OpenSpec change artifacts, and the issue status checklist after direct verification.
- **Interfaces:** local webhook `POST` acceptance and read-only workflow-state lookup; GitHub effects remain behind an injected adapter.
- **Data:** a local SQLite database stores inbox deliveries, issue-to-run ownership, claim projection state, and LangGraph checkpoints; runtime database files remain ignored.
- **Dependencies:** Python HTTP/runtime validation plus LangGraph with SQLite checkpoint support.
- **Direct verification:** execute signed and rejected deliveries through the HTTP interface, repeat the same delivery, restart the application on the same database, and observe response, state lookup, GitHub-adapter effects, and persisted checkpoint/run identity.
