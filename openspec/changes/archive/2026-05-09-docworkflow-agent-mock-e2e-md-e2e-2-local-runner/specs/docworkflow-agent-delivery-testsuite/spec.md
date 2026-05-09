## ADDED Requirements

### Requirement: Local mock E2E runner

The testsuite SHALL provide a deterministic local mock session runner for the accepted mock fixture family without requiring network, Docker, Codex auth, external agent providers or manual starts.

#### Scenario: Large selector proves parent child workflow

- **GIVEN** the accepted `mock-large-parent-v1` fixture
- **WHEN** `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep` runs
- **THEN** the runner SHALL record `sizing_decision: parent_child`
- **AND** it SHALL generate parent-control evidence with exactly `ML-C1`, `ML-C2`, `ML-C3`, `ML-C4` and `ML-C5`
- **AND** each child SHALL reach `ran-target` and `closed` before the next child starts
- **AND** `mock-target/output/count.txt` SHALL contain exactly `1\n2\n3\n4\n5\n`
- **AND** the summary SHALL report `overall_workflow_status: pass` and `evidence_truth: ran-target`.

#### Scenario: Small selector proves direct workflow

- **GIVEN** the accepted `mock-small-direct-v1` fixture
- **WHEN** `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh small --keep` runs
- **THEN** the runner SHALL record `sizing_decision: direct`
- **AND** it SHALL create `mock-target/output/small-direct-result.json` with the accepted expected JSON
- **AND** it SHALL NOT create child index, child spec, child handoff or child session artifacts
- **AND** the summary SHALL report `overall_workflow_status: pass` and `session_chain_status: not_applicable`.

#### Scenario: All selector aggregates large and small evidence

- **GIVEN** accepted large and small mock fixtures
- **WHEN** `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep` runs
- **THEN** the runner SHALL execute large and small in separate isolated run roots
- **AND** it SHALL write `aggregate-summary.json`
- **AND** it SHALL exit successfully only when both sub-runs pass.

#### Scenario: Bad states cannot pass

- **GIVEN** generated or fixture evidence with permanent `queued`, `manual_start_required`, unexpected `blocked`, `failed`, output mismatch, forbidden real fixture paths or external dependency attempts
- **WHEN** the local mock runner validates that evidence
- **THEN** it SHALL NOT produce `overall_workflow_status: pass`
- **AND** it SHALL return a non-zero exit for positive selectors or an explicit expected negative blocker status for negative guard cases.

#### Scenario: Summary schema is machine readable

- **GIVEN** any retained local mock runner summary
- **WHEN** the summary validator reads it
- **THEN** it SHALL require `schema_id: docworkflow-agent-delivery-mock-e2e-summary.v1`
- **AND** it SHALL require sizing, workflow, session, expected output, forbidden fixture, evidence truth, runner mode, session strategy, output evidence and external dependency fields
- **AND** positive summaries SHALL fail validation unless `runner_mode` is `local-mock-session-runner` and external dependency fields are `not_used`.
