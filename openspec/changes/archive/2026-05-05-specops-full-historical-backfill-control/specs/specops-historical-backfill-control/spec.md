## ADDED Requirements

### Requirement: Inventory Baseline Control
The control change MUST use the accepted SpecOps source inventory as the baseline for remaining historical backfill planning.

#### Scenario: Inventory drives phases
- **WHEN** a future delivery run selects historical sources for import
- **THEN** the selected sources map back to a phase or source group from `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`

#### Scenario: Accepted baseline is not re-imported
- **WHEN** a future delivery run processes sources that overlap `historical-001`
- **THEN** already imported `historical-001` entities are treated as done and are not duplicated

### Requirement: Source To Entity Classification
The control change MUST distinguish primary spec entities, document entities and OpenSpec relationship/evidence artefacts.

#### Scenario: Narrative specs become primary specs
- **WHEN** a source is classified as `narrative_spec` or `completed_narrative_spec`
- **THEN** it may become a primary `type: spec` entity if no duplicate primary entity already exists

#### Scenario: Documents stay document entities
- **WHEN** a source is an ADR, guide, runbook or comparable document and is not itself a spec
- **THEN** it is modeled as `type: document` rather than `type: spec`

#### Scenario: OpenSpec change artefacts are not primary specs
- **WHEN** a source is classified as `openspec_change_artifact`
- **THEN** it is linked as related evidence or skipped, and it MUST NOT become a primary `type: spec` entity

### Requirement: Phased Execution By Scope Contract
The remaining full historical backfill MUST be executable through bounded delivery runs without creating a new Child-Spec for every batch.

#### Scenario: Future run selects a bounded phase subset
- **WHEN** Codex starts a future backfill delivery run
- **THEN** the run defines a Scope Contract naming the selected phase, source subset, acceptance targets and verification before editing entities

#### Scenario: OpenSpec evidence grows by run
- **WHEN** a future delivery run finishes
- **THEN** `implementation-evidence.md` records the generated/updated entities, skipped sources, duplicate guards and verification result for that run

### Requirement: Coverage Matrix And Guards
The control change MUST keep source-group coverage and duplicate prevention measurable.

#### Scenario: Acceptance matrix tracks each source group
- **WHEN** the OpenSpec acceptance matrix is reviewed
- **THEN** each inventory source group includes source path, expected count, source type, intended entity type, current imported count, skipped/linked-only count, metadata quality summary and status

#### Scenario: Negative guard protects OpenSpec artifacts
- **WHEN** verification checks primary SpecOps spec entities
- **THEN** no primary spec entity uses `source_type: openspec_change_artifact`
