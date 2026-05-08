# DocWorkflow Agent Delivery Testsuite Delta

## ADDED Requirements

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
