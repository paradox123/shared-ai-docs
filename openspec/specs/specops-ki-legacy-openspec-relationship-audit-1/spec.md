# specops-ki-legacy-openspec-relationship-audit-1 Specification

## Purpose
TBD - created by archiving change specops-ki-legacy-openspec-relationship-audit-1. Update Purpose after archive.
## Requirements
### Requirement: KI Legacy OpenSpec Relationship Audit Batch 1

The SpecOps historical backfill MUST map the first selected KI legacy OpenSpec batch as relationship/evidence sources without creating new primary SpecOps spec entities from OpenSpec change artifacts.

#### Scenario: KI legacy batch 1 is mapped
- **WHEN** the KI legacy OpenSpec relationship audit batch 1 completes
- **THEN** all 21 selected markdown files are listed in the relationship audit with exact paths and existing SpecOps targets

#### Scenario: Remaining KI legacy coverage is explicit
- **WHEN** the Control Spec and source inventory are reviewed
- **THEN** KI legacy OpenSpec coverage shows 21/35 mapped and 14 remaining

#### Scenario: Legacy artifacts stay relationship-only
- **WHEN** selected KI legacy OpenSpec artifacts are counted
- **THEN** they remain relationship/evidence sources and are not imported as primary `type: spec` entities

#### Scenario: Manual batch size remains bounded
- **WHEN** batch size is reviewed
- **THEN** the 21-file selected batch is justified as a Scale L relationship-audit batch instead of an uncontrolled 35-file XL import

