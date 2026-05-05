# specops-final-completed-support-rag-backfill Specification

## Purpose
TBD - created by archiving change specops-final-completed-support-rag-backfill. Update Purpose after archive.
## Requirements
### Requirement: Final Completed Support And RAG Backfill

The SpecOps historical backfill MUST classify and import the final remaining shared-ai-docs Completed sources as dashboard-visible entity notes without promoting support or history documents into primary specs.

#### Scenario: RAG phase sources become specs
- **WHEN** the final Completed run imports the five 2026-04-21 DanielsVault RAG phase sources
- **THEN** each source has one primary `type: spec` entity note with exact `source:` path and batch `historical-001-completed-final`

#### Scenario: Support sources become documents
- **WHEN** the final Completed run imports the CheckBuild user guide and Nebenkosten support/history sources
- **THEN** each source has one `type: document` entity note and is not represented as a primary `type: spec`

#### Scenario: Completed coverage is closed
- **WHEN** the final Completed run completes
- **THEN** shared-ai-docs Completed source coverage is 32/32 across SpecOps spec and document entities

#### Scenario: Duplicate and OpenSpec artifact guards pass
- **WHEN** verification runs
- **THEN** no Completed source path is duplicated and no `openspec_change_artifact` source type is used as a primary entity

