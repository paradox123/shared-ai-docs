## ADDED Requirements

### Requirement: Spec-orchestrator uses post-orchestration evaluator gate

The `spec-orchestrator` skill SHALL run the accepted post-orchestration next-step evaluator after it creates or updates an operational Child Index and Hardening Queue, then follow the evaluator verdict instead of restating transition rules in broad prose.

#### Scenario: Orchestrator runs evaluator after queue creation

- **GIVEN** `spec-orchestrator` has created or updated an operational Child Index and Hardening Queue
- **WHEN** it reaches the post-orchestration transition point
- **THEN** the skill instructions SHALL require running `EvaluateOrchestrationNextStep.cs`
- **AND** the command SHALL pass the orchestration pack/index path, repository path, Child Index section, intent and JSON output format.

#### Scenario: Hardening verdict starts hardening unless user stopped there

- **GIVEN** the evaluator JSON sets `required_next_skill` to `child-spec-hardening`
- **WHEN** the user did not explicitly request `orchestration-only` or `stop-before-hardening`
- **THEN** the skill instructions SHALL route the first unblocked child to `child-spec-hardening`
- **AND** `--no-implementation` SHALL NOT suppress this hardening route.

#### Scenario: Delivery verdict remains gated

- **GIVEN** the evaluator JSON sets `required_next_skill` to `spec-change-delivery`
- **WHEN** the user did not explicitly request implementation or readiness gates are not valid
- **THEN** the skill instructions SHALL stop at the implementation handoff instead of starting delivery.

#### Scenario: Final wording reports evaluator status token

- **GIVEN** the evaluator emitted `final_status_token`
- **WHEN** `spec-orchestrator` reports its result
- **THEN** the final response SHALL include that token
- **AND** it SHALL not imply workflow advancement when only a queue was created.
