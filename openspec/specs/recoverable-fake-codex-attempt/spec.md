# recoverable-fake-codex-attempt Specification

## Purpose
Define recoverable external fake-agent attempts with stable session correlation,
redacted canonical history, lossless outcome diagnostics and truthful Operator
opening capabilities.
## Requirements
### Requirement: External fake execution has stable product correlation
The worker SHALL run deterministic preparation without a model agent and invoke an external fake session through `AgentSessionAdapter/v1`. Before session creation it SHALL persist one activity, attempt and operation key. Session, activity, attempt and run correlation SHALL survive redelivery; completed preparation SHALL not create duplicate work.

#### Scenario: Fake attempt executes visible steps
- **WHEN** the worker executes an admitted run with the fake adapter
- **THEN** the public history exposes preparation, one attempt, one session, numbered messages, tool calls, tool results, artifact references and a controlled terminal outcome with contiguous source sequence and causal correlation

### Requirement: Worker replacement adopts the external session
The worker SHALL reconcile by the persisted operation key and SHALL NOT silently create another session or activity. Equal observations SHALL be idempotent; inconsistent session identity, sequence or replay SHALL fail closed. All public canonical events SHALL remain strictly ordered and redacted before persistence.

#### Scenario: Worker dies before session mapping commits
- **WHEN** worker one is killed after external session creation but before the local mapping commits
- **THEN** worker two adopts the same provider session and exposes exactly one logical activity and transcript

#### Scenario: Worker dies after mapping or result capture
- **WHEN** worker one is killed after session mapping or original result capture but before activity completion
- **THEN** worker two finishes missing processing, preserves confirmed history and does not start a second session, repeat preparation or duplicate observations

### Requirement: Original outcomes precede interpretation and failures remain typed
The system SHALL persist redacted adapter observations before downstream interpretation. It SHALL distinguish `process-failure`, `timeout`, `transport-failure`, `contract-incompatible`, `schema-failure`, `blocked`, `semantic-rejection` and `infrastructure-failure` in public diagnostics. An unavailable run store SHALL expose infrastructure failure through the available HTTP/worker boundary without fabricating persisted history.

#### Scenario: Valid blocked result is rejected downstream
- **WHEN** a schema-valid blocked result is rejected by downstream evidence processing
- **THEN** the original redacted result stays readable, the session remains blocked, and a separate rejection identifies the original observation while the attempt exposes semantic rejection

#### Scenario: External boundary fails
- **WHEN** the fake process fails, times out, loses transport, returns an incompatible contract, returns malformed output, or reports infrastructure unavailability
- **THEN** the public attempt and history expose the corresponding distinct category and no implicit fresh session is started

### Requirement: Operators select attempts and see truthful opening capabilities
An independently authenticated read-authorized Operator Client SHALL select a concrete attempt via HTTP and CLI and read its session status, provenance, original observation, processing outcome, durable Human Request and continuation lineage. History SHALL be independent of Codex App task visibility. The controlled fake adapter SHALL expose truthful per-attempt same-session, handoff-confirmation-required, or unsupported opening capability, with a concrete reason and no misleading production Codex URL. A capability that cannot safely display the original session SHALL provide no implicit fork.

#### Scenario: Second operator inspects failed attempt
- **WHEN** a second read-authorized operator selects the failed attempt after worker replacement and API restart
- **THEN** it reads the same session and immutable original result, separate processing rejection, durable Human Request and truthful Open in Codex capability without worker or database access

#### Scenario: Same-session capability opens the selected attempt only
- **WHEN** an Operator Client opens an attempt whose adapter declares same-session support
- **THEN** public read-back identifies exactly the persisted session as opened while its phase, expected head, external effects and session identity remain unchanged

#### Scenario: Unsupported opening does not silently fork
- **WHEN** an Operator Client opens an attempt whose adapter does not safely support same-session display
- **THEN** it receives the concrete capability limitation and no new session, fork or uncorrelated run is created before an explicit fenced Handoff decision

#### Scenario: Unauthorized attempt selection
- **WHEN** an operator without repository read permission requests an attempt
- **THEN** the request is rejected without exposing attempt or session contents
