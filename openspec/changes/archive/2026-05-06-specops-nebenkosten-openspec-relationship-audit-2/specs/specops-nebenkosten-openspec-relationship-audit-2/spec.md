## ADDED Requirements

### Requirement: Nebenkosten OpenSpec Relationship Audit Batch 2

The SpecOps historical backfill MUST map the second Nebenkosten OpenSpec material batch as relationship/evidence sources without creating new primary SpecOps spec entities from OpenSpec change artifacts.

#### Scenario: Nebenkosten batch 2 is mapped
- **WHEN** the Nebenkosten OpenSpec relationship audit batch 2 completes
- **THEN** all 30 selected markdown files are listed in the relationship audit with exact paths and existing SpecOps targets

#### Scenario: Nebenkosten OpenSpec coverage advances
- **WHEN** the Control Spec and source inventory are reviewed
- **THEN** Nebenkosten OpenSpec coverage shows 62/87 mapped and 25 remaining

#### Scenario: Archived OpenSpec artifacts stay relationship-only
- **WHEN** selected Nebenkosten OpenSpec artifacts are counted
- **THEN** they remain relationship/evidence sources and are not imported as primary `type: spec` entities
