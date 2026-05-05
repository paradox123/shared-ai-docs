# specops-historical-backfill-delivery-control Specification

## Purpose
TBD - created by archiving change specops-full-historical-backfill-delivery-plan. Update Purpose after archive.
## Requirements
### Requirement: Inventory Baseline Is Current

The delivery-control plan MUST use the current source inventory and current filesystem counts as the baseline for future historical backfill runs.

#### Scenario: Current source counts are represented
- **WHEN** the delivery-control plan is reviewed
- **THEN** shared-ai-docs `_specs`, `ki-fuer-kmu/_specs`, NCG `docs/Specs`, shared OpenSpec, RAG OpenSpec, Nebenkosten OpenSpec, `ki-fuer-kmu` legacy OpenSpec and `ki-fuer-kmu` ADR groups are represented with current counts

#### Scenario: Accepted baseline is not re-imported
- **WHEN** a future delivery run processes sources overlapping `historical-001`
- **THEN** already imported `historical-001` entities are treated as done and not duplicated

### Requirement: Source To Entity Classification Is Enforced

The delivery-control plan MUST distinguish primary spec entities, document entities and OpenSpec relationship/evidence artefacts.

#### Scenario: Narrative specs become primary specs
- **WHEN** a source is classified as `narrative_spec` or `completed_narrative_spec`
- **THEN** it may become a primary `type: spec` entity if no duplicate primary entity already exists

#### Scenario: Documents stay document entities
- **WHEN** a source is an ADR, guide, runbook or comparable document and is not itself a spec
- **THEN** it is modeled as `type: document` rather than `type: spec`

#### Scenario: OpenSpec change artefacts are not primary specs
- **WHEN** a source is classified as `openspec_change_artifact`
- **THEN** it is linked as related evidence or skipped and MUST NOT become a primary `type: spec` entity by default

### Requirement: Delivery Runs Are Scope-Contract Bounded

The remaining full historical backfill MUST be executable through bounded delivery runs without creating a new Child-Spec for every batch.

#### Scenario: Future run selects an exact source subset
- **WHEN** Codex starts a future backfill delivery run
- **THEN** the run defines a Scope Contract naming the selected phase, exact source files or source query, acceptance targets and verification before editing entities

#### Scenario: First proposed run is concrete
- **WHEN** the first delivery run is selected from this plan
- **THEN** Phase 1A identifies exactly five completed shared-ai-docs source files as the proposed Scale-S source subset

### Requirement: Coverage Matrix And Guards Are Measurable

The delivery-control plan MUST keep source-group coverage, metadata quality and duplicate prevention measurable.

#### Scenario: Acceptance matrix tracks each source group
- **WHEN** the OpenSpec acceptance matrix is reviewed
- **THEN** each inventory source group includes source path, expected count, source type, intended entity type, current imported count, remaining candidate count, skipped/linked-only count, metadata quality summary, proposed scale and status

#### Scenario: Negative guard protects OpenSpec artifacts
- **WHEN** future verification checks primary SpecOps spec entities
- **THEN** no primary spec entity uses `source_type: openspec_change_artifact` unless a later explicit promotion decision overrides the default

