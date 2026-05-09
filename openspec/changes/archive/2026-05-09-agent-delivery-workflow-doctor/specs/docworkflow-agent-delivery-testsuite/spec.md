## ADDED Requirements

### Requirement: Workflow Doctor post-orchestration wrapper

The testsuite SHALL provide a reduced Workflow Doctor that wraps accepted Agent Delivery workflow tooling for the `post-orchestration` phase without adding new workflow policy.

#### Scenario: Post-orchestration evaluation is aggregated

- **GIVEN** an orchestration pack accepted by `EvaluateOrchestrationNextStep.cs`
- **WHEN** `WorkflowDoctor.cs` runs with `--phase post-orchestration --format json`
- **THEN** the JSON report SHALL contain exactly one tool run for `EvaluateOrchestrationNextStep.cs`
- **AND** the report SHALL include the underlying parsed JSON result
- **AND** the report SHALL surface the recommended next action fields from the underlying evaluator.

#### Scenario: Required next step can fail the wrapper

- **GIVEN** an orchestration pack where `EvaluateOrchestrationNextStep.cs` reports a required next skill
- **WHEN** `WorkflowDoctor.cs` runs with `--fail-on-required-next-step`
- **THEN** the wrapper SHALL exit `1`
- **AND** the aggregate report SHALL keep the underlying parsed JSON visible.

#### Scenario: Unsupported broader phases are blocked

- **GIVEN** Slice A only supports `post-orchestration`
- **WHEN** `WorkflowDoctor.cs` runs with `--phase pre-delivery`
- **THEN** it SHALL exit `2`
- **AND** it SHALL explain that the phase is outside Slice A.

#### Scenario: Missing underlying tool is explicit

- **GIVEN** `EvaluateOrchestrationNextStep.cs` is absent beside `WorkflowDoctor.cs`
- **WHEN** `WorkflowDoctor.cs` runs with `--phase post-orchestration`
- **THEN** it SHALL exit `2`
- **AND** it SHALL include a missing-underlying-tool finding.
