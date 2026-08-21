## ADDED Requirements

### Requirement: Dedicated Agent Delivery testsuite is retired

The repository SHALL NOT require a dedicated Agent Delivery orchestration testsuite when the active-scope validator provides the maintained direct verification surface.

#### Scenario: Missing historical testsuite is not a failure

- **GIVEN** the former Agent Delivery fixtures, E2E runner, cleanup validator, and prose-budget validator have been intentionally deleted
- **WHEN** current workflow readiness is evaluated
- **THEN** their absence SHALL NOT fail delivery or archive checks
- **AND** historical specs and evidence SHALL NOT claim those paths are retained.

#### Scenario: Active scope uses the maintained direct validator

- **GIVEN** a narrow active OpenSpec change
- **WHEN** its scope contract is verified
- **THEN** `skills-repo/tools/ValidateActiveOpenSpecScope.cs` SHALL be the maintained direct validation surface.

## REMOVED Requirements

### Requirement: Simplified Agent Delivery active-scope checks

**Reason**: The dedicated fixtures and E2E runner were intentionally removed after the original change completed.

**Migration**: Verify active scope directly with `skills-repo/tools/ValidateActiveOpenSpecScope.cs`.

### Requirement: Cleanup manifest checks

**Reason**: The one-time cleanup validator was intentionally removed after the cleanup finished.

**Migration**: Preserve the archived manifest and evidence as historical records, not an active runtime gate.

### Requirement: Skill prose budget checks

**Reason**: The affected Agent Delivery skills and their dedicated prose-budget validator were subsequently removed.

**Migration**: Do not reintroduce the retired skills or their testsuite solely to satisfy historical closeout evidence.
