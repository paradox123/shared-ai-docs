# specops-rag-openspec-relationship-audit Specification

## Purpose
TBD - created by archiving change specops-rag-openspec-relationship-audit. Update Purpose after archive.
## Requirements
### Requirement: RAG OpenSpec Relationship Audit

The SpecOps historical backfill MUST map DanielsVault RAG OpenSpec material as relationship/evidence sources without creating new primary SpecOps spec entities from OpenSpec change artifacts.

#### Scenario: RAG OpenSpec pool is mapped
- **WHEN** the RAG OpenSpec relationship audit completes
- **THEN** all 17 RAG OpenSpec markdown files are listed in the relationship audit with exact paths and existing SpecOps targets

#### Scenario: Archived RAG artifacts stay relationship-only
- **WHEN** archived RAG OpenSpec change artifacts are counted
- **THEN** they remain relationship/evidence sources and are not imported as primary `type: spec` entities

#### Scenario: Historical blocker evidence is visible
- **WHEN** the 2026-04-22 hardening archive is reviewed
- **THEN** old blocked runtime evidence is documented as historical metadata conflict context, not hidden or treated as current runtime validation

#### Scenario: Larger batch size remains bounded
- **WHEN** batch size is reviewed
- **THEN** the 17-file RAG OpenSpec pool is justified as a Scale L relationship-audit batch after a successful smaller OpenSpec audit

