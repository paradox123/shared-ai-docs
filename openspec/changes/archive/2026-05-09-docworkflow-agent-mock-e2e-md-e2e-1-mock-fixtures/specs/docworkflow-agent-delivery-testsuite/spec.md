## ADDED Requirements

### Requirement: Mock E2E fixture family

The testsuite SHALL provide source-controlled mock fixture data for the Agent Delivery Mock E2E baseline without using KI-fuer-KMU or other real product artifacts as positive fixture inputs.

#### Scenario: Large parent mock fixture is manifest-backed

- **GIVEN** the `large-parent` mock fixture root
- **WHEN** the manifest schema validator reads `manifest.json`
- **THEN** the manifest SHALL declare `expected_delivery_mode: parent_child`
- **AND** it SHALL declare exactly `ML-C1`, `ML-C2`, `ML-C3`, `ML-C4` and `ML-C5`
- **AND** it SHALL declare `mock-target/output/count.txt` with exact content `1\n2\n3\n4\n5\n`.

#### Scenario: Small direct mock fixture forbids child artifacts

- **GIVEN** the `small-direct` mock fixture root
- **WHEN** the manifest schema validator reads `manifest.json`
- **THEN** the manifest SHALL declare `expected_delivery_mode: direct`
- **AND** it SHALL declare no expected children
- **AND** it SHALL forbid child index, child spec and child session handoff outputs.

#### Scenario: Real product fixtures are rejected

- **GIVEN** any positive mock fixture, write-set, target workspace declaration or evidence input
- **WHEN** the forbidden-real-fixture validator scans it
- **THEN** the validator SHALL fail if it contains `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**`, `ki-fuer-kmu/**` or a real-fixture compatibility marker
- **AND** the standard mock fixture family SHALL NOT preserve KI-fuer-KMU as a fallback or compatibility fixture.
