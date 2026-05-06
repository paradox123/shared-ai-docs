## ADDED Requirements

### Requirement: NCG STS Completed Backfill Batch 1

The SpecOps historical backfill MUST import the selected accepted NCG STS Completed sources as dashboard-visible primary spec entities without modifying the source documents or runtime repositories.

#### Scenario: Selected STS sources become specs
- **WHEN** the NCG STS batch 1 import completes
- **THEN** each of the 7 selected Completed sources has one primary `type: spec` entity note with exact `source:` path and batch `historical-001-ncg-sts-1`

#### Scenario: NCG coverage advances
- **WHEN** the batch completes
- **THEN** NCG docs Specs source coverage is 7/29 across SpecOps entities

#### Scenario: Duplicate and OpenSpec artifact guards pass
- **WHEN** verification runs
- **THEN** no selected source path is missing, no NCG docs Specs source path is duplicated, and no `openspec_change_artifact` source type is used as a primary entity
