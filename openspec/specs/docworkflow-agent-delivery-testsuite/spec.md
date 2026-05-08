# docworkflow-agent-delivery-testsuite Specification

## Purpose
Capture accepted DocWorkflow Agent Delivery Testsuite requirements that have been archived from OpenSpec changes. The current canonical requirements record the accepted DWT-S0 Promptfoo-first framework spike evidence gate, the accepted DWT-S1 deterministic L1 contract harness and the accepted DWT-S4 reporting, telemetry, style and summary contract.
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
