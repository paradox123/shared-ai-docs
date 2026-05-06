## ADDED Requirements

### Requirement: Shared OpenSpec Canonical Relationship Audit

The SpecOps historical backfill MUST map shared-ai-docs canonical OpenSpec specs as relationships or evidence without creating new primary SpecOps spec entities from OpenSpec change artifacts.

#### Scenario: Canonical OpenSpec specs are mapped
- **WHEN** the shared OpenSpec canonical audit completes
- **THEN** all 11 canonical `openspec/specs/*/spec.md` files are listed in the relationship audit with exact paths and existing SpecOps targets

#### Scenario: Archived artifacts remain out of primary entity scope
- **WHEN** archived OpenSpec change artifacts are counted
- **THEN** they remain relationship/evidence candidates and are not imported as primary `type: spec` entities

#### Scenario: Current OpenSpec counts are visible
- **WHEN** the Control Spec and source inventory are reviewed
- **THEN** shared-ai-docs OpenSpec coverage shows `119` markdown files total, split into `11` canonical specs and `108` archived change artifacts

#### Scenario: Legacy exception is documented
- **WHEN** existing OpenSpec-derived primary entities are checked
- **THEN** the single legacy entity `rag-source-precision-gate-harmonization-2026-04-23` is retained and explicitly documented as an exception
