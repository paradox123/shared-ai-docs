# authorized-issue-observable-run Specification

## Purpose
Define the isolated local control-plane contract that turns a capability-bound,
synthetically authorized issue command into exactly one durable and independently
observable `ImplementationRun`, with canonical product history and supplemental
worker/framework evidence.
## Requirements
### Requirement: An authorized synthetic issue command creates one durable implementation run
The pilot SHALL accept a start command only when its synthetic repository-provider fixture authorizes the identified actor for the addressed synthetic repository issue. The loopback-only pilot API SHALL require an ephemeral fixture-access capability outside the command payload before it evaluates that actor identity, and SHALL not persist or publicly serialize that capability. It SHALL transactionally create exactly one `ImplementationRun` with immutable repository, issue, command, and run correlation, an initial canonical event, an admission activity, and an admission attempt before returning a successful acceptance response.

#### Scenario: Authorized issue is accepted
- **WHEN** a fixture-authorized actor submits a well-formed start command for an authorized synthetic issue
- **THEN** the public response identifies one new run and public run read-back exposes the same repository, issue, command, activity, attempt, and run identifiers

#### Scenario: Unauthorized synthetic actor is rejected
- **WHEN** an actor absent from the fixture authorization for the addressed issue submits a start command
- **THEN** the public endpoint rejects the command without creating a run, activity, attempt, or canonical event

#### Scenario: Caller lacks the fixture-access capability
- **WHEN** a caller submits an otherwise well-formed command without the harness-provided fixture-access capability
- **THEN** the public endpoint rejects it before it evaluates the caller-supplied actor identity and creates no run, activity, attempt, or canonical event

### Requirement: Start-command delivery is idempotent and conflicting reuse is visible
The pilot SHALL classify a start command by its command identity and redacted canonical payload digest. Repeating an identical command SHALL return the original run without adding a run, activity, attempt, canonical event, worker instruction, or external effect. Reusing that command identity with a different digest SHALL return a public conflict that identifies the original run correlation and SHALL add no state or external effect.

#### Scenario: Identical command delivery is repeated
- **WHEN** the same authorized start command is delivered again after its first transaction commits
- **THEN** the response identifies the original run as an idempotent result and the public run history remains unchanged

#### Scenario: Command identity is reused for another payload
- **WHEN** an authorized actor sends the same command identity with a different canonical payload digest
- **THEN** the endpoint returns a visible conflict, preserves the original run/history, and creates no second run or effect

### Requirement: A separate Operator Client reads canonical run state and ordered history
The pilot SHALL expose public read-only Operator API endpoints for a run projection and events strictly after an acknowledged event position. The run projection SHALL include current state, activities, attempts, redaction metadata, and correlations; every canonical event SHALL have a stable increasing position. A separate Operator Client process SHALL obtain this information only through those HTTP endpoints and SHALL not require database, worker-process, worktree, Agent Framework, or Durable Task access.

#### Scenario: Second client reads an accepted run
- **WHEN** an initiator accepts an authorized issue and a distinct Operator Client later opens that run
- **THEN** the second client reads the same current projection and ordered canonical event history solely through the public Operator interface

#### Scenario: History is read after an acknowledged position
- **WHEN** an Operator Client requests events after a previously acknowledged event position
- **THEN** the response contains only greater positions in stable ascending order and does not substitute framework or durability history for canonical events

### Requirement: Persisted run identity, confirmed history, time axes, and provenance survive process restart
The pilot SHALL persist accepted runs and confirmed canonical events independently of API and worker process lifetime. It SHALL expose separately named run, attempt, API/worker process, and heartbeat times, along with source, package, configuration, and contract revisions captured at admission. Restarting the API or a worker against the same dedicated storage SHALL neither change run identity nor remove/reorder already confirmed history.

#### Scenario: API and worker restart after acceptance
- **WHEN** an authorized run is accepted, the API and a correlated worker process are restarted, and a second Operator Client reads the run
- **THEN** the run correlation and all events confirmed before each restart remain present and ordered, while lifecycle observations have distinct process and heartbeat timestamps

#### Scenario: Time axes are independently visible
- **WHEN** a client reads a run containing admission and worker-lifecycle observations
- **THEN** it can distinguish run age, attempt duration, process lifetime, and latest heartbeat without inferring one value from another

### Requirement: Framework and durability records remain supplemental correlated evidence
The pilot SHALL associate Agent Framework and Durable Task workflow/session/task identifiers with a product-owned execution-evidence record when a worker reports them. It SHALL retain the canonical run, activity, attempt, event position, state, redaction, and provenance data independently of that evidence and SHALL not expose framework or durability history as the sole product-facing run history.

#### Scenario: Worker reports framework and durability correlation
- **WHEN** a correlated worker lifecycle observation supplies Agent Framework and Durable Task identifiers
- **THEN** the Operator projection presents them as supplemental execution evidence alongside, rather than instead of, canonical run history and product identifiers

### Requirement: Controlled secrets are redacted before durable or operator-visible use
The pilot SHALL apply a versioned redaction policy to controlled secret canaries before command persistence, event append, projection update, lifecycle observation, or Operator API/CLI serialization. It SHALL expose a redaction marker and policy version when redaction occurred, while no raw controlled canary appears in run projections, canonical history, execution evidence, or Operator Client output.

#### Scenario: A start command contains a controlled secret canary
- **WHEN** an authorized synthetic start command or worker observation includes a configured controlled secret canary
- **THEN** every public read-back and persisted pilot record contains only the redaction marker and policy version, never the raw canary
