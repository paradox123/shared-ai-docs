## ADDED Requirements

### Requirement: Mock-only standard Agent Delivery gate

The testsuite SHALL use the accepted local mock E2E runner as the standard Agent Delivery regression gate and SHALL NOT pass by creating, copying or reading a real product fixture by default.

#### Scenario: Standard command uses mock data

- **GIVEN** the accepted `MD-E2E-2` local mock runner exists
- **WHEN** `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep` runs from the repository root
- **THEN** the command SHALL run only against source-controlled mock data and generated isolated evidence roots
- **AND** it SHALL report success only when both large and small mock paths pass
- **AND** retained evidence SHALL include forbidden-real-fixture validation.

#### Scenario: Legacy all command is mock-only

- **GIVEN** the legacy standard command name still exists
- **WHEN** `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all --keep` runs from the repository root
- **THEN** it SHALL delegate to `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`
- **AND** it SHALL NOT invoke fixture setup or accept fixture source arguments for the `all` selector.

#### Scenario: Legacy fixture setup is explicit-only

- **GIVEN** a user invokes legacy fixture setup
- **WHEN** no source specs are supplied or a forbidden real fixture source is supplied
- **THEN** fixture setup SHALL exit non-zero with a clear message
- **AND** it SHALL NOT copy a real product fixture by default.

#### Scenario: Standard documentation points to the mock gate

- **GIVEN** the testsuite README describes standard local execution
- **WHEN** a user reads the quickstart
- **THEN** the first standard command SHALL be `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`
- **AND** legacy fixture setup SHALL NOT be documented as a no-argument standard path.
