## ADDED Requirements

### Requirement: NCG STS Root And Support Backfill

The SpecOps historical backfill MUST import the selected NCG STS parent/root/support sources as dashboard-visible entity notes while keeping the Deferred Topics TODO as a document rather than a primary spec.

#### Scenario: Selected STS root and support sources are represented
- **WHEN** the NCG STS root/support batch completes
- **THEN** each of the 7 selected sources has one entity note with exact `source:` path and batch `historical-001-ncg-sts-root-support`

#### Scenario: Deferred TODO remains a document
- **WHEN** the batch imports `2026-04-06 STS Deferred Topics TODO.md`
- **THEN** it is represented as `type: document`, not as a primary `type: spec`

#### Scenario: NCG coverage advances
- **WHEN** the batch completes
- **THEN** NCG docs Specs source coverage is 21/29 across SpecOps entities

#### Scenario: Duplicate and OpenSpec artifact guards pass
- **WHEN** verification runs
- **THEN** no selected source path is missing, no NCG docs Specs source path is duplicated, and no `openspec_change_artifact` source type is used as a primary entity
