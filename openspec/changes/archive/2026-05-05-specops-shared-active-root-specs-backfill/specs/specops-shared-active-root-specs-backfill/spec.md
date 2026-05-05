## ADDED Requirements

### Requirement: Shared Active Root Specs Backfill

The SpecOps historical backfill MUST import every active root `_shared/shared-ai-docs/_specs` narrative source as a dashboard-visible SpecOps spec entity unless the exact source path already has an entity.

#### Scenario: Missing active root sources are imported
- **WHEN** the shared active root backfill completes
- **THEN** the 12 previously missing root sources have new SpecOps spec entities

#### Scenario: Existing RAG root source is not duplicated
- **WHEN** the backfill encounters the RAG operating model source path
- **THEN** the existing entity is counted as done and is not duplicated

#### Scenario: Dashboard visibility uses existing queries
- **WHEN** SpecOps dashboards query `_shared/SpecOps/Entities/specs` for `type = "spec"`
- **THEN** all 13 active root sources are discoverable through their entity notes

#### Scenario: Formal decision markers remain visible
- **WHEN** a source contains a formal unresolved decision marker
- **THEN** the imported entity exposes non-clean metadata with `metadata_quality: conflict`
