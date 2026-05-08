# DocWorkflow Agent Delivery Testsuite Delta

## ADDED Requirements

### Requirement: DWT-S2 L2 parent-first orchestration agent harness

The testsuite SHALL provide an L2 parent-first orchestration harness that proves an oversized parent/master spec is routed through child orchestration and hardening instead of direct implementation.

#### Scenario: Oversized parent does not enter direct implementation

- **GIVEN** an oversized parent/master spec fixture with no generated child-control artifacts at the start
- **WHEN** the DWT-S2 L2 runner executes the parent-first orchestration prompt or validates a stored output bundle
- **THEN** the result SHALL fail if runtime implementation, Docker, deployment, credential copying, KI-fuer-KMU original writes or parent-as-child delivery are attempted
- **AND** a passing agent proof SHALL include `agent_execution_status: ran-target`.

#### Scenario: Parent-first orchestration produces child control surface

- **GIVEN** the parent-first orchestration output
- **WHEN** the DWT-S2 validator evaluates it
- **THEN** the output SHALL include generated child specs or skeletons, an exact operational Child Index, a Coverage Matrix, Dependencies, a Hardening Queue and at least one valid leading next child state
- **AND** copied or stale child-control artifacts SHALL NOT pass without provenance.

#### Scenario: Thin generated child cannot become ready

- **GIVEN** a generated child skeleton without parent conformance, concrete write-set, persisted handoff or command rehearsal evidence
- **WHEN** the DWT-S2 validator evaluates readiness
- **THEN** the child SHALL NOT receive an implementation-allowing verdict
- **AND** the next action SHALL NOT name `spec-change-delivery`.

#### Scenario: Valid next child state is singular and gated

- **GIVEN** a parent-first orchestration output with generated children
- **WHEN** the DWT-S2 validator evaluates the next child recommendation
- **THEN** exactly one leading next child state SHALL be identified
- **AND** `implementation_ready` SHALL require matching Child Index, persisted handoff, concrete write-set and readiness validator evidence.

#### Scenario: Blocked agent path is not accepted as proof

- **GIVEN** Promptfoo/Codex cannot run because of auth, provider, runtime or network prerequisites
- **WHEN** fallback artifact mode runs
- **THEN** deterministic validators MAY produce contract evidence
- **AND** the overall L2 agent proof SHALL be reported as `blocked`, not `pass`.

#### Scenario: L2 output follows reporting, style and efficiency contracts

- **GIVEN** a DWT-S2 output bundle
- **WHEN** summary, telemetry, style and efficiency validation runs
- **THEN** the summary SHALL follow `docworkflow-agent-delivery-summary.v1`
- **AND** telemetry SHALL flag forbidden command classes, secret exposure and unjustified command drift
- **AND** DWT-S3 and DWT-S5 SHALL remain unreleased unless their own later hardening gates authorize them.
