# specops-historical-backfill-phase-1a Specification

## Purpose
TBD - created by archiving change specops-full-historical-backfill-phase-1a. Update Purpose after archive.
## Requirements
### Requirement: Phase 1A Entity Import

The Phase 1A run MUST import exactly five completed Nebenkostenabrechnung narrative sources as SpecOps spec entities.

#### Scenario: Five entities are created
- **WHEN** the Phase 1A run completes
- **THEN** exactly five entities exist with `backfill_batch: historical-001-phase-1a`

#### Scenario: Sources remain traceable
- **WHEN** an imported Phase 1A entity is reviewed
- **THEN** its `source` field points to the original completed source file

#### Scenario: Dashboard discovery works
- **WHEN** SpecOps dashboards query `_shared/SpecOps/Entities/specs`
- **THEN** the Phase 1A entities are discoverable as `type: spec`

#### Scenario: OpenSpec artefacts are not imported as specs
- **WHEN** the negative guard is checked
- **THEN** no Phase 1A entity has `source_type: openspec_change_artifact`

