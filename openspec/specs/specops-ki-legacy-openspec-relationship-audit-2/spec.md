# specops-ki-legacy-openspec-relationship-audit-2 Specification

## Purpose
TBD - created by archiving change specops-ki-legacy-openspec-relationship-audit-2. Update Purpose after archive.
## Requirements
### Requirement: KI Legacy OpenSpec Relationship Audit Batch 2

The SpecOps historical backfill MUST map the remaining KI legacy OpenSpec material as relationship/evidence sources without creating new primary SpecOps spec entities from OpenSpec change artifacts.

#### Scenario: KI legacy batch 2 is mapped
- **WHEN** the KI legacy OpenSpec relationship audit batch 2 completes
- **THEN** all 14 selected markdown files are listed in the relationship audit with exact paths and existing SpecOps targets

#### Scenario: KI legacy OpenSpec coverage is complete
- **WHEN** the Control Spec and source inventory are reviewed
- **THEN** KI legacy OpenSpec coverage shows 35/35 mapped and 0 remaining

#### Scenario: Legacy artifacts stay relationship-only
- **WHEN** selected KI legacy OpenSpec artifacts are counted
- **THEN** they remain relationship/evidence sources and are not imported as primary `type: spec` entities

