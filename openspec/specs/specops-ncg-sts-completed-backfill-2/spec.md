# specops-ncg-sts-completed-backfill-2 Specification

## Purpose
TBD - created by archiving change specops-ncg-sts-completed-backfill-2. Update Purpose after archive.
## Requirements
### Requirement: NCG STS Completed Backfill Batch 2

The SpecOps historical backfill MUST import the selected late NCG STS Completed sources as dashboard-visible primary spec entities without modifying the source documents or runtime repositories.

#### Scenario: Selected late STS sources become specs
- **WHEN** the NCG STS batch 2 import completes
- **THEN** each of the 7 selected Completed sources has one primary `type: spec` entity note with exact `source:` path and batch `historical-001-ncg-sts-2`

#### Scenario: NCG coverage advances
- **WHEN** the batch completes
- **THEN** NCG docs Specs source coverage is 14/29 across SpecOps entities

#### Scenario: Duplicate and OpenSpec artifact guards pass
- **WHEN** verification runs
- **THEN** no selected source path is missing, no NCG docs Specs source path is duplicated, and no `openspec_change_artifact` source type is used as a primary entity

