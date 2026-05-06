# specops-ncg-infrastructure-completed-backfill Specification

## Purpose
TBD - created by archiving change specops-ncg-infrastructure-completed-backfill. Update Purpose after archive.
## Requirements
### Requirement: NCG Infrastructure Completed Backfill

The SpecOps historical backfill MUST import the final older NCG infrastructure Completed sources as dashboard-visible primary spec entities while preserving historical marker conflicts in metadata.

#### Scenario: Final NCG infrastructure sources become specs
- **WHEN** the NCG infrastructure final batch completes
- **THEN** each of the 8 selected Completed sources has one primary `type: spec` entity note with exact `source:` path and batch `historical-001-ncg-infrastructure-final`

#### Scenario: NCG coverage is complete
- **WHEN** the batch completes
- **THEN** NCG docs Specs source coverage is 29/29 across SpecOps entities

#### Scenario: Historical marker conflicts are explicit
- **WHEN** a selected Completed source still contains old missing or decision markers
- **THEN** the entity keeps `metadata_quality: conflict`

#### Scenario: Duplicate and OpenSpec artifact guards pass
- **WHEN** verification runs
- **THEN** no selected source path is missing, no NCG docs Specs source path is duplicated, and no `openspec_change_artifact` source type is used as a primary entity

