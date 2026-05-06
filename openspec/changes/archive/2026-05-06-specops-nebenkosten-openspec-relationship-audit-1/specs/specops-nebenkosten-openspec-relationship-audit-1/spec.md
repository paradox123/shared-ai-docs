## ADDED Requirements

### Requirement: Nebenkosten OpenSpec Relationship Audit Batch 1

The SpecOps historical backfill MUST map the first Nebenkosten OpenSpec material batch as relationship/evidence sources without creating new primary SpecOps spec entities from OpenSpec change artifacts.

#### Scenario: Nebenkosten batch 1 is mapped
- **WHEN** the Nebenkosten OpenSpec relationship audit batch 1 completes
- **THEN** all 32 selected markdown files are listed in the relationship audit with exact paths and existing SpecOps targets

#### Scenario: Nebenkosten OpenSpec coverage is measurable
- **WHEN** the Control Spec and source inventory are reviewed
- **THEN** Nebenkosten OpenSpec coverage shows 32/87 mapped and 55 remaining

#### Scenario: Archived OpenSpec artifacts stay relationship-only
- **WHEN** selected Nebenkosten OpenSpec artifacts are counted
- **THEN** they remain relationship/evidence sources and are not imported as primary `type: spec` entities
