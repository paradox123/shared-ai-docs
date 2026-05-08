# docworkflow-agent-delivery-testsuite Specification

## Purpose
Capture accepted DocWorkflow Agent Delivery Testsuite requirements that have been archived from OpenSpec changes. The current canonical requirements record the accepted DWT-S0 Promptfoo-first framework spike evidence gate, the accepted DWT-S1 deterministic L1 contract harness, the accepted DWT-S2 L2 parent-first orchestration agent harness, the accepted DWT-S3 L2 single-child delivery and closeout gate harness, and the accepted DWT-S4 reporting, telemetry, style and summary contract.
## Requirements
### Requirement: DWT-S0 framework spike evidence

The system SHALL run or reproducibly block a one-time Promptfoo-first framework spike before recurring L1/L2/L3 testsuite implementation starts.

#### Scenario: Promptfoo adoption is evidence-gated

- **GIVEN** the parent testsuite spec and framework ADR
- **WHEN** `DWT-S0` is executed
- **THEN** the output SHALL include one of `ADOPT_PROMPTFOO`, `ADOPT_WITH_LIMITATIONS`, `FALLBACK_TO_INSPECT`, or `REOPEN_EVALUATION`
- **AND** the result SHALL be backed by isolated fixture evidence, runner/config evidence, stored output or blocker evidence, and deterministic assertion evidence or blocker rationale.

#### Scenario: Static fake output cannot adopt Promptfoo

- **GIVEN** the spike uses static fake outputs, manual-only steps, hidden fixture normalization, or non-reproducible workarounds instead of a reproducible agent/coding-agent path
- **WHEN** the ADR is re-evaluated
- **THEN** the result SHALL NOT be `ADOPT_PROMPTFOO`.

### Requirement: DWT-S1 deterministic L1 contract checks

The testsuite SHALL provide deterministic L1 checks for fixture provenance, child-readiness gate regression and forbidden agent/runtime dependencies before agentic L2 workflow proof is treated as credible.

#### Scenario: Parent-only fixture has no child artifacts

- **GIVEN** a parent-only L1 start fixture
- **WHEN** the L1 parent-only check runs
- **THEN** the result SHALL pass only if Child Index, Child Specs and Child Handoffs are absent from the fixture start state
- **AND** the fixture manifest SHALL record removed or intentionally absent child artifacts.

#### Scenario: Generated child control surface has provenance

- **GIVEN** a generated child index, child spec or handoff output fixture
- **WHEN** the L1 provenance check runs
- **THEN** the result SHALL pass only if the output is linked to source hashes or stable source identifiers
- **AND** copied source child-control artifacts SHALL NOT pass as newly generated outputs without provenance.

#### Scenario: Thin child cannot pass readiness

- **GIVEN** a child skeleton without parent conformance, concrete write-set, persisted handoff or command rehearsal evidence
- **WHEN** the L1 readiness check runs
- **THEN** the result SHALL block implementation readiness.

#### Scenario: High-risk ready claim without rehearsal cannot pass

- **GIVEN** a child claims implementation readiness with high-risk runtime commands
- **AND** the child spec or handoff has no command-contract rehearsal evidence or explicit blocker
- **WHEN** the L1 readiness check runs
- **THEN** the result SHALL block implementation readiness.

#### Scenario: Hidden normalization cannot pass

- **GIVEN** a fixture output depends on a normalization not listed in the fixture manifest
- **WHEN** the L1 provenance check runs
- **THEN** the result SHALL fail or block.

#### Scenario: S0 limitations remain context only

- **GIVEN** `DWT-S0` was accepted with `ADOPT_WITH_LIMITATIONS`
- **WHEN** the DWT-S1 L1 runner executes
- **THEN** the runner SHALL record the S0 result as dependency context
- **AND** the runner SHALL NOT require Promptfoo, Inspect AI, Codex credentials, isolated npm registry access or agent execution.

### Requirement: DWT-S4 reporting, telemetry, style and summary contract

The testsuite SHALL provide a deterministic reporting contract for summary artifacts, telemetry manifests, style/usability gates and efficiency/command-drift gates before L2/L3 outputs are accepted as comparable workflow evidence.

#### Scenario: Retained DWT-S1 summary remains a compatible baseline

- **GIVEN** the retained DWT-S1 `l1-summary.json` from accepted closeout evidence
- **WHEN** the DWT-S4 reporting validator reads it
- **THEN** the summary SHALL parse as JSON
- **AND** it SHALL satisfy the legacy compatibility baseline for suite level, version, absolute roots, test results, provenance checks, readiness checks, forbidden actions, evidence truth and S0 dependency context.

#### Scenario: New summary artifacts carry evidence truth

- **GIVEN** a new DWT-S4 v1 summary fixture
- **WHEN** summary schema validation runs
- **THEN** each test result SHALL have a status from the allowed vocabulary
- **AND** each case SHALL have an evidence truth label from the allowed vocabulary
- **AND** missing or invalid evidence truth SHALL fail validation.

#### Scenario: Telemetry flags forbidden command classes

- **GIVEN** a reporting-only or spec-only test run telemetry manifest
- **WHEN** the efficiency validator evaluates command classes
- **THEN** Docker, runtime build/test, credential-copy, KI-fuer-KMU write and deployment command classes SHALL fail unless the fixture explicitly expects the negative failure.

#### Scenario: Style gate catches unsynchronized handoff and index output

- **GIVEN** child output with a Child Index row, child spec and persisted handoff
- **WHEN** style/usability validation runs
- **THEN** child id, readiness verdict, handoff pointer, target repository, allowed write-set, verification commands, evidence and next action SHALL be consistent
- **AND** stale or mismatched pointers SHALL fail validation.

#### Scenario: Efficiency gate distinguishes warning from failure

- **GIVEN** command/read telemetry with broad scans or repeated reads
- **WHEN** the efficiency validator evaluates the telemetry
- **THEN** justified drift within budget SHALL produce `warn`
- **AND** hidden or unjustified drift SHALL produce `fail`.

#### Scenario: DWT-S4 does not release downstream child delivery

- **GIVEN** DWT-S4 reporting validation passes
- **WHEN** downstream DWT-S2, DWT-S3 or DWT-S5 states are reported
- **THEN** those descendants SHALL remain `blocked` or `planned` unless their own child verdict, handoff, dependencies and verification gates authorize delivery.

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
