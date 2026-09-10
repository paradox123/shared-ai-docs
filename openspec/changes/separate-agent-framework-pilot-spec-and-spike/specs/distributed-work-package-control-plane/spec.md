## ADDED Requirements

### Requirement: One durable work package per authorized issue
The system SHALL create at most one durable `ImplementationRun` for an authorized repository issue and SHALL keep all implementation, verification, review, repair, intervention, approval, and completion activities under that run.

#### Scenario: Duplicate authorization delivery
- **WHEN** the same authorized issue command is delivered repeatedly
- **THEN** exactly one run and no duplicate external effect are observable

### Requirement: Observable history is canonical product state
The system SHALL expose one ordered, redacted Run History containing every observable activity assignment, attempt, message, tool call/result, artifact reference, head, error, control command, human decision, and state transition without claiming private model reasoning.

#### Scenario: Another client diagnoses a failed attempt
- **WHEN** an authorized second user opens a failed run without access to the original worker
- **THEN** the user can identify the last successful observation, first failure, retained artifacts, exact attempt/session, and current recovery options

### Requirement: Agent sessions are isolated and explicitly continued
Every agentic activity SHALL start with a fresh, bounded Codex session by default. Resume SHALL preserve session identity, Fork SHALL create a new session with ancestry, and Fresh Retry SHALL create a new session without automatic conversation carry-over.

#### Scenario: Three continuation modes
- **WHEN** an authorized controller chooses Resume, Fork, or Fresh Retry for an explicit attempt
- **THEN** the resulting session identity and ancestry match the chosen semantics and all prior history remains unchanged

### Requirement: A targeted activity session can be opened in Codex
The Operator Client SHALL offer `Open in Codex` for an explicit activity attempt. The system SHALL open the same Codex session when that is safely supported. Otherwise it SHALL disclose the limitation and require explicit confirmation before creating a clearly identified handoff fork with ancestry. Any write-capable interaction SHALL require the current Control Lease and SHALL remain correlated into the canonical Run History.

#### Scenario: Headless background session is not directly displayable
- **WHEN** a controller opens a failed background attempt whose original session cannot be surfaced safely in Codex
- **THEN** the system does not silently substitute another session and offers an explicitly labelled handoff fork whose subsequent observable events remain under the same run

### Requirement: Deterministic work remains outside the model
Authorization, scheduling, Git/worktree effects, deterministic tests, evidence qualification, head checks, state projection, and approval policy SHALL be deterministic application responsibilities rather than model decisions.

#### Scenario: Model output proposes a forbidden transition
- **WHEN** agent output claims that a head is verified or approved without the deterministic gates
- **THEN** the system rejects the transition and records the reason

### Requirement: Stateless remote Operator access
Authorized users SHALL inspect and control the same run from separate stateless Operator Clients. A client reconnecting from an acknowledged event position SHALL receive every later authorized event once and in stable order.

#### Scenario: Reconnect after client and worker restart
- **WHEN** a client acknowledges event N, disconnects, and reconnects after API and worker restart
- **THEN** it observes events N+1 through the current position without gaps, duplicates, or reordering

### Requirement: Repository-derived authorization and exclusive human control
The system SHALL derive observation and mutation eligibility from current repository-provider permissions and SHALL require exactly one run-wide human Control Lease for mutations. It SHALL provide atomic transfer and audited Forced Takeover without a separate administrator role.

#### Scenario: Stale lease holder races a takeover
- **WHEN** the previous holder submits a mutation concurrently with a completed transfer or Forced Takeover
- **THEN** the old lease epoch is fenced and only the current holder can mutate the run

### Requirement: Targeted live commands
The lease holder SHALL send `interrupt` or `queue` to one explicit active activity attempt. `interrupt` SHALL fence the current operation and make exactly one accepted command next after effect reconciliation; `queue` SHALL retain stable accepted order after the current operation.

#### Scenario: Restart between command acceptance and delivery
- **WHEN** a process stops after a command is accepted but before delivery
- **THEN** recovery delivers the logical command once to the intended attempt or reports an explicit fenced/terminal rejection

### Requirement: At-least-once recovery does not duplicate business effects
Every external effect SHALL have an application-owned identity, receipt, reconciliation, and adoption path. Restart SHALL continue only missing work and SHALL fail closed when an observed effect is ambiguous or conflicting.

#### Scenario: Effect succeeds before activity result persists
- **WHEN** a worker stops immediately after a Git, provider, file, or session effect succeeds
- **THEN** recovery adopts the matching effect without repeating it or exposes an explicit human decision when adoption is unsafe

### Requirement: Work starts from an authoritative repository base
The system SHALL resolve and record the provider-authoritative base SHA after all required predecessors are complete and SHALL refuse to start or publish from a stale local repository reference.

#### Scenario: Previous issue merged while local mirror is stale
- **WHEN** a sequential successor is eligible but the local repository base differs from the provider's merged head
- **THEN** the successor remains unstarted until the exact expected base is available and recorded

### Requirement: Work is admitted only with executable prerequisites
Before starting expensive agent work, the system SHALL validate that the activity's required repository base, contracts, tools, dependencies, access, sandbox permissions, and evidence surfaces are available. Missing prerequisites SHALL become an actionable visible request or blocked state rather than late ambiguous worker failure.

#### Scenario: Required UI evidence cannot be captured
- **WHEN** an acceptance criterion requires browser interaction or a screenshot but the worker has no executable browser/evidence seam
- **THEN** the activity does not begin normal implementation and the missing prerequisite is visible with a bounded resolution path

### Requirement: Evidence deficiencies have a bounded recovery path
Schema validity SHALL NOT be treated as sufficient evidence qualification. If implementation completes but evidence is semantically incomplete, the run SHALL either execute a bounded evidence-correction/capture activity or converge to an explicit blocked state that releases repository serialization according to policy.

#### Scenario: Schema-valid result lacks required evidence phases
- **WHEN** a worker returns valid structured output but omits a required request, response, repeat, read-back, or screenshot phase
- **THEN** the run neither publishes an unqualified PR nor remains indefinitely active; it repairs evidence or exposes a terminal actionable state

### Requirement: Worker outcomes and failures remain diagnosable
The system SHALL persist the redacted observable adapter outcome before downstream interpretation and SHALL distinguish process failure, timeout, transport failure, unsupported contract, schema failure, valid blocked outcome, semantic evidence rejection, and infrastructure failure.

#### Scenario: Downstream parser rejects a valid blocked result
- **WHEN** the adapter receives a valid terminal worker result that later processing cannot accept
- **THEN** the original redacted result remains readable and the rejection is recorded as a separate event rather than replaced by a generic error

### Requirement: Runtime provenance and time semantics are visible
Every attempt SHALL record deployed source/package/config/contract versions and separate run, attempt, process, and heartbeat times. Startup SHALL fail closed on an incompatible runtime/contract tuple.

#### Scenario: Installed worker is older than source contracts
- **WHEN** the deployed runtime cannot consume the configured assignment or result contract
- **THEN** no issue is started and the public status identifies the incompatible versions without exposing secrets

### Requirement: Qualification is bound to one exact head
One head SHALL be qualified only after deterministic verification and fresh, context-isolated requirements, code, and architecture reviews of that same SHA. Any new writer head SHALL invalidate prior qualification and begin a bounded repair or human-handoff path.

#### Scenario: Head changes during review
- **WHEN** a reviewer batch completes after the provider head has changed
- **THEN** none of its verdicts qualifies the new head and all required checks run again for the new SHA

### Requirement: Human approval cannot be automated or imply merge
Approval SHALL require an explicit interactive action by an authenticated authorized human over the currently qualified head. A worker, scheduler, monitor, service identity, or background automation SHALL NOT impersonate this gate. Approval SHALL NOT trigger merge, deployment, or release.

#### Scenario: Oversight automation sees a qualified pull request
- **WHEN** a background monitor observes that all automated gates pass
- **THEN** it may notify and project readiness but cannot approve, mark ready on behalf of a human, merge, deploy, or release

### Requirement: Sensitive data is redacted before durable use
Secrets and configured personal-data classes SHALL be redacted before event, artifact, projection, telemetry, export, or client-display persistence, while the history records that redaction or unavailability occurred.

#### Scenario: Tool output contains controlled canaries
- **WHEN** controlled secrets and personal-data canaries appear in agent or tool output
- **THEN** no durable or displayed surface contains the raw values and the redaction policy version is auditable

### Requirement: Agent definitions evolve only through external human governance
The Agent Evolution Loop MAY propose versioned Agent Definition changes, but SHALL NOT approve, merge, activate, or retroactively apply its own proposal. Every agent attempt SHALL record the externally qualified definition revision it used.

#### Scenario: Evolution proposal has no human repository approval
- **WHEN** a new Agent Definition revision is proposed but not externally qualified
- **THEN** no new or running agent operation uses that revision

### Requirement: The additional pilot preserves the existing LangGraph pilot
The Microsoft Agent Framework pilot SHALL be implemented as a separate sibling application and SHALL NOT replace, migrate, or share writable runtime state with the existing LangGraph pilot. Both SHALL be independently runnable against controlled fixtures.

#### Scenario: Microsoft pilot is started locally
- **WHEN** the new pilot starts or is reset
- **THEN** LangGraph source, database, managed worktrees, Cloudflare relay, macOS services, and ProBara CRM configuration remain unchanged

### Requirement: Workflow infrastructure has a licence-cost-free open-source path
The selected workflow stack SHALL have a production-capable self-hosted open-source path without mandatory framework or managed workflow-service licence fees. Temporal and paid managed workflow services SHALL NOT be dependencies or fallbacks.

#### Scenario: Only the local in-memory emulator is free
- **WHEN** the candidate cannot demonstrate a supported production-capable self-hosted open-source backend beyond its development emulator
- **THEN** the candidate fails Gate 0 before the larger semantic spike proceeds
