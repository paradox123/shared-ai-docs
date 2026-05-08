# DocWorkflow Agent Delivery Testsuite Delta

## ADDED Requirements

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
