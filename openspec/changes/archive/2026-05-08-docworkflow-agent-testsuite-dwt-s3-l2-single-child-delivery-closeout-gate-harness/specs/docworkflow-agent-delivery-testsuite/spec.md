# DocWorkflow Agent Delivery Testsuite Delta

## ADDED Requirements

### Requirement: DWT-S3 L2 single-child delivery and closeout gate harness

The testsuite SHALL provide an L2 single-child delivery and closeout gate harness that proves delivery starts only from the current implementation-ready DWT-S3 handoff in an isolated temp workspace and that closeout does not release DWT-S5 without its own gates.

#### Scenario: Ready child delivery kickoff is temp-workspace only

- **GIVEN** the accepted DWT-S2 retained evidence and a DWT-S3 implementation-ready Child Index row with a persisted handoff
- **WHEN** the DWT-S3 L2 runner executes the delivery kickoff prompt or validates a stored output bundle
- **THEN** the result SHALL pass only if the output targets DWT-S3, validates the current handoff, uses a concrete allowed write-set and points edit-like work at an isolated temp workspace
- **AND** runtime implementation, Docker, deployment, credential copying, KI-fuer-KMU original writes or DWT-S5 delivery SHALL fail.

#### Scenario: Stale handoff blocks delivery

- **GIVEN** a stale, missing or mismatched DWT-S3 handoff fixture
- **WHEN** delivery kickoff validation runs
- **THEN** the child SHALL NOT receive delivery authorization
- **AND** the output SHALL identify the stale or mismatched handoff field.

#### Scenario: Closeout preserves parent coverage and evidence links

- **GIVEN** a synthetic DWT-S3 closeout output
- **WHEN** closeout validation runs
- **THEN** Parent Coverage for `DWT-PR3`, `DWT-PR4`, `DWT-PR5` and `DWT-PR7` SHALL remain present
- **AND** DWT-S3 evidence, retained DWT-S2 predecessor evidence and OpenSpec ledger state SHALL remain distinguishable.

#### Scenario: Next child remains blocked after closeout

- **GIVEN** DWT-S3 closeout has synchronized its own evidence
- **WHEN** the next child state is evaluated
- **THEN** DWT-S5 SHALL remain `blocked_by_dependency` or another non-implementation-allowing state unless DWT-S5 has its own ready child spec, persisted handoff and readiness validator evidence
- **AND** DWT-S5 SHALL NOT name `spec-change-delivery` as next action before those gates pass.

#### Scenario: Blocked agent path is not accepted as proof

- **GIVEN** Promptfoo/Codex cannot run because of auth, provider, runtime or network prerequisites
- **WHEN** fallback artifact mode runs
- **THEN** deterministic validators MAY produce contract evidence
- **AND** the overall DWT-S3 L2 agent proof SHALL be reported as `blocked`, not `pass`.

#### Scenario: DWT-S3 output follows reporting, style and efficiency contracts

- **GIVEN** a DWT-S3 output bundle
- **WHEN** summary, telemetry, style and efficiency validation runs
- **THEN** the summary SHALL follow `docworkflow-agent-delivery-summary.v1`
- **AND** telemetry SHALL flag forbidden command classes, secret exposure and unjustified command drift
- **AND** DWT-S5 SHALL remain blocked unless its own later hardening gates authorize it.
