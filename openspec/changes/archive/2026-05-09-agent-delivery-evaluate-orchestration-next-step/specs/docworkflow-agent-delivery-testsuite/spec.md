## ADDED Requirements

### Requirement: Post-orchestration next-step evaluator

The testsuite SHALL provide a deterministic local tool that evaluates an Agent Delivery orchestration pack after `spec-orchestrator` creates or updates a Child Index and reports the next workflow step without relying on prose interpretation.

#### Scenario: Hardening is required after orchestration

- **GIVEN** an orchestration pack with a Child Index where the first child is `NEEDS HARDENING` and has no unresolved predecessor dependency
- **WHEN** `EvaluateOrchestrationNextStep.cs` runs with `--intent expects-hardening`
- **THEN** the JSON result SHALL set `required_next_skill` to `child-spec-hardening`
- **AND** it SHALL set `first_unblocked_child` to that child id
- **AND** it SHALL classify that child as `harden_now`.

#### Scenario: No implementation does not block hardening

- **GIVEN** an orchestration pack where hardening is expected
- **WHEN** `EvaluateOrchestrationNextStep.cs` runs with `--intent expects-hardening --no-implementation`
- **THEN** the JSON result SHALL still set `required_next_skill` to `child-spec-hardening`
- **AND** it SHALL set `delivery_allowed` to `false`.

#### Scenario: User-requested orchestration-only is explicit

- **GIVEN** an orchestration pack where hardening would otherwise be expected
- **WHEN** `EvaluateOrchestrationNextStep.cs` runs with `--intent orchestration-only`
- **THEN** the JSON result SHALL set `trigger_result` to `orchestration_only_by_user_request`
- **AND** it SHALL NOT require a hardening start.

#### Scenario: Delivery is gated by implementation-ready verdict and intent

- **GIVEN** an orchestration pack whose first child is `IMPLEMENTATION READY`
- **WHEN** `EvaluateOrchestrationNextStep.cs` runs without `--no-implementation`
- **THEN** the JSON result SHALL set `required_next_skill` to `spec-change-delivery`
- **AND** it SHALL set `delivery_allowed` to `true`.
- **WHEN** the same command runs with `--no-implementation`
- **THEN** it SHALL set `delivery_allowed` to `false`
- **AND** it SHALL NOT route to `spec-change-delivery`.

