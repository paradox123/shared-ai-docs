## ADDED Requirements

### Requirement: MD-E2E-5 external controller integration

The Agent Delivery testsuite SHALL run `MD-E2E-5` child sessions through an external visible-session controller rather than launching child sessions from inside an app-server-backed parent turn.

#### Scenario: Parent publishes five child launch requests

- **GIVEN** a live `MD-E2E-5` run directory
- **WHEN** the parent visible Codex App session completes its orchestration turn
- **THEN** it SHALL publish child launch request artifacts for exactly `RSW-C1`, `RSW-C2`, `RSW-C3`, `RSW-C4`, and `RSW-C5`
- **AND** each request SHALL use `schema_id: "agent-delivery.visible-session-controller.request.v1"` or a versioned successor accepted by this integration
- **AND** each request SHALL reference a child handoff, expected output path, expected output text, and launch output directory below the run directory
- **AND** the parent SHALL NOT invoke `AgentDeliverySessionLauncher.cs`, `codex app-server`, or any other child launch command.

#### Scenario: Controller launches five children externally

- **GIVEN** the parent has published ordered child launch requests
- **WHEN** the external controller consumes the requests
- **THEN** it SHALL launch `RSW-C1` through `RSW-C5` from the controller process using `AgentDeliverySessionLauncher.cs --adapter codex-app-server`
- **AND** it SHALL write one response artifact for every discovered request
- **AND** it SHALL write a controller summary that records parent evidence, all request paths, all response paths, launcher evidence paths, and terminal statuses
- **AND** it SHALL fail the integration if fewer than five child responses exist or any response is not a passing launched response.

#### Scenario: Runner consumes controller evidence

- **GIVEN** a controller-backed `MD-E2E-5` run directory
- **WHEN** `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep` evaluates the run
- **THEN** the runner SHALL read the controller summary and response artifacts
- **AND** it SHALL resolve the parent and five child launcher evidence paths from those artifacts
- **AND** it SHALL validate all six visible evidence records through `ValidateVisibleCodexAppSessionEvidence.cs`
- **AND** it SHALL require non-empty distinct visible thread ids for the parent, all five children, and any recorded control session id.

#### Scenario: Controller-backed final output and closeout pass together

- **GIVEN** all five child responses are launched and visible
- **WHEN** the runner evaluates final delivery and closeout evidence
- **THEN** `target/output/count.txt` SHALL equal exactly `1\n2\n3\n4\n5\n`
- **AND** the S4 control-boundary summary SHALL report `control_session_status: "observed_only"`
- **AND** the S5 archive or retained-session summary SHALL include explicit passing records for the parent and all five child visible sessions
- **AND** `visible-session-summary.json` SHALL report `overall_workflow_status: "pass"` only when the controller, visible-session, control-boundary, archive, redaction, and final-output dimensions all pass.

#### Scenario: One-child controller MVP evidence is not enough

- **GIVEN** retained evidence from the accepted external visible-session controller MVP
- **WHEN** the `MD-E2E-5` runner evaluates that evidence
- **THEN** the runner SHALL report `overall_workflow_status: "not_ready"` or `fail`
- **AND** it SHALL name missing `RSW-C1` through `RSW-C5` controller responses or visible evidence as blockers
- **AND** it SHALL NOT treat the MVP's single `CTRL-C1` child launch as a substitute for any `RSW-C*` child.

#### Scenario: Nested child launch evidence is rejected

- **GIVEN** a parent transcript or retained launch evidence shows a child launch was started from inside the parent app-server-backed turn
- **WHEN** the runner evaluates the live run
- **THEN** the runner SHALL fail the controller integration dimension
- **AND** it SHALL retain the offending transcript or evidence path without converting the nested launch to visible-session success.
