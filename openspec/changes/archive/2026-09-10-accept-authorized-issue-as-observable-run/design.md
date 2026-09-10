## Context

The completed managed-DTS gate establishes a tightly scoped Azure Durable Task Scheduler Consumption exception for this isolated pilot. It proves one framework workflow can survive a replacement worker, but it does not create a product-level issue command, canonical `ImplementationRun`, or independent Operator surface. Ticket 02 is the V1 control-plane slice from the local spike plan: it must make durable domain state observable through public seams while preserving the existing LangGraph pilot and the historical OSS no-go.

The target plan assigns PostgreSQL ownership of commands, canonical domain events, and rebuildable projections. Agent Framework and Durable Task scheduling history are useful execution/recovery evidence, but they cannot become the product's sole or canonical history. Ticket 03 owns repository-derived authorization and the Control Lease; Ticket 04 owns real fake-Codex activity execution and failure recovery; Ticket 09 owns complete reconnect/export behavior.

## Goals / Non-Goals

**Goals:**

- Provide a small ASP.NET Core Operator API with a controlled synthetic repository-provider seam that admits an authorized issue command.
- Persist command idempotency, one issue-to-run correlation, canonical ordered events, read projections, and redaction metadata transactionally in a dedicated local PostgreSQL instance.
- Supply a separate `Wpcp.OperatorCli` HTTP client so a second process can inspect the same run, activities, attempts, and event positions without database, worker, or worktree access.
- Record API/worker lifecycle observations and distinct run, attempt, process, and heartbeat clocks with source/package/configuration/contract provenance.
- Keep framework and Durable Task identifiers as explicit supplemental correlation evidence, never as a replacement for canonical domain events.
- Prove the slice through a black-box two-client/restart test that uses only the API and Operator CLI outputs plus controlled process boundaries.

**Non-Goals:**

- Real repository-provider authorization, roles, Control Lease, mutation fencing, or a client-managed ACL (Ticket 03).
- Agent-session execution, retries, external effects, real Codex invocation, or durable orchestration recovery semantics (Ticket 04 and later).
- Full stream reconnect protocol, export/restore, artifact retention, or a production hosting topology (Ticket 09 and later).
- Replacing the completed managed durability probe, altering its OSS conclusion, or modifying the LangGraph pilot, Cloudflare relay, macOS services, GitHub configuration, or ProBara CRM.

## Decisions

### Use a dedicated PostgreSQL event store and transactional command inbox

`Wpcp.Storage.Postgres` will own an `implementation_runs` projection, a command-inbox row keyed by command ID, and append-only domain events with a monotonic per-run position. A unique repository/issue key and a command-ID-plus-digest comparison make repeated delivery return the original run while a digest mismatch produces a stable public conflict with no additional event or effect.

The API will commit command classification, run creation, projection, and the initial event in one database transaction before returning a successful response. This makes API restarts safe after commit but before response and provides the process-independent atomic boundary required by the local spike plan.

Each public projection or event page is read through one PostgreSQL Repeatable
Read snapshot. An operator therefore cannot receive a heartbeat/evidence row
from a newer lifecycle transition alongside an older process/redaction view.

Alternative considered: reuse the managed gate's JSONL/file ledger. Rejected because its process probe is not a transactionally safe command/event store and cannot establish cross-process uniqueness, stable event positions, or a later CAS/fencing boundary.

### Make HTTP and a separate Operator CLI the only acceptance seams

`Wpcp.Api` exposes the synthetic start endpoint and read-only run/event endpoints. `Wpcp.OperatorCli` is a distinct executable which talks only to those endpoints; it has no storage or worker references. The black-box test starts the API, invokes one CLI as the initiator and another as the observer, and verifies no result by querying PostgreSQL or a framework dashboard.

Alternative considered: test domain classes directly or expose a console-only command. Rejected because neither proves an independently observable public Operator surface.

### Bound the authorization seam to deterministic synthetic fixtures

The API receives a fixture-defined synthetic issue and actor identity, but it does
not trust the actor ID alone. The isolated test harness creates an ephemeral
fixture-access capability at launch, supplies it to the loopback-only API outside
the command payload, and the separate Operator CLI sends it in a dedicated
header. The API compares that capability in constant time before consulting the
fixture's actor-to-issue permissions. The capability is never persisted, logged,
included in an event, or serialized publicly.

This gives the pilot a real boundary against an unauthenticated local caller
impersonating a fixture actor, while deliberately not claiming production
repository authentication or an ACL. Ticket 03 still owns repository-derived
authorization and the Control Lease.

Alternative considered: trust an `authorized` Boolean supplied by the caller. Rejected because a caller-controlled flag would not prove authorized intake.

### Redact before any durable write or public serialization

An injected versioned redaction policy contains controlled canary values and replaces matches with a visible marker before requests are hashed for safe correlation, command data is persisted, events are appended, or API/CLI responses are serialized. The projection records redaction occurrence and policy version, never raw canary text. The black-box test scans API responses, CLI output, canonical-history responses, and fixture-controlled storage-visible payloads for the raw canary.

Alternative considered: redact only responses. Rejected because state/history/exports could retain a durable secret leak.

### Treat run history as canonical and framework/durability data as referenced evidence

Run events have product-owned positions, event types, state transitions, correlation IDs, timestamps, and provenance. A worker-process observation may attach opaque Agent Framework workflow/session and Durable Task orchestration/task identifiers under a separate `executionEvidence` field. They are readable as correlations but cannot provide event positions, replace run state, or be returned as the sole activity history.

Alternative considered: expose Durable Task/Agent Framework history directly as the run timeline. Rejected because framework execution records lack the product's redaction, command, projection, and cross-client semantics.

### Keep time axes separately named and measured

The run projection stores `runStartedAt`; an admission activity/attempt stores its own timestamps; API and worker lifecycle entries store `processStartedAt`/`processStoppedAt`; and each worker heartbeat has an independent `heartbeatAt`. Provenance is recorded as source, package, configuration, and contract revision values captured at start. No timeout inference is implemented in this slice, so an old run or host sleep cannot be misclassified as a process timeout.

## Risks / Trade-offs

- [Local PostgreSQL is unavailable or a port collides] → The test harness launches a uniquely named, disposable `postgres:17-alpine` container with a Docker-assigned host port and always removes it; API bind races retry on a new loopback port.
- [A fixture actor ID is forged] → The loopback API requires the harness-generated ephemeral fixture-access capability before evaluating fixture permissions; it is never a substitute for Ticket 03's repository identity model.
- [API stops after durable commit but before response] → Retrying the same command ID reads the inbox row and returns the original run without a second event.
- [Raw canaries enter diagnostic paths] → Route all persisted/public text through the versioned redactor and make canary absence a black-box regression assertion.
- [A future worker treats framework IDs as source of truth] → Store them only in a separate evidence shape and require the product event position/run ID on every observation.
- [The managed exception is mistaken for a broader architecture decision] → Documentation and configuration name it an isolated pilot exception; this slice neither claims an OSS backend nor changes the historical gate.

## Migration Plan

1. Add the minimal solution/projects, PostgreSQL schema bootstrap, fixture configuration, API, worker lifecycle writer, and HTTP-only Operator CLI under the isolated pilot directory.
2. Add a public black-box test covering authorized start, duplicate/conflicting command semantics, second-client read-back, restart persistence, time/provenance/evidence fields, and redaction.
3. Run the test against a disposable local PostgreSQL container, then stop/remove that container; the database is not shared with the existing pilot.
4. Roll back by deleting only the new `Wpcp.*` projects and their dedicated test/runtime resources. The completed managed gate and existing systems remain unaffected.

## Open Questions

None for this bounded foundation. The provider authorization contract, workers' real Agent Framework/Durable Task activity history, and reconnect/export protocol remain deliberately assigned to later tickets.
