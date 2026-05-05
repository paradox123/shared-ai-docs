# Acceptance Criteria Matrix

## Control Change Criteria

| Criterion | Status | Evidence |
|---|---|---|
| OpenSpec change exists with proposal, design, tasks, spec, acceptance matrix and evidence | pass | `openspec/changes/specops-full-historical-backfill-control/` |
| Inventory baseline is referenced | pass | `proposal.md`, `design.md`, `specs/specops-historical-backfill-control/spec.md` |
| `historical-001` is treated as done and not re-importable | pass | `design.md`, `tasks.md`, capability spec |
| `type: spec` / `type: document` / OpenSpec relationship rules are explicit | pass | `design.md`, capability spec |
| Negative guard for `openspec_change_artifact` primary spec entities is defined | pass | capability spec and verification plan |

## Source Group Coverage Baseline

| Phase | Source Path | Expected Source Count | source_type | Intended Entity Type | Current Imported Count | Skipped / Linked-Only Count | metadata_quality Summary | Status |
|---:|---|---:|---|---|---:|---:|---|---|
| 0 | `historical-001` batch | 5 | mixed narrative | `type: spec` | 5 | 0 | explicit/inferred/conflict | done |
| 1 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed/` | included in 42 shared specs | `completed_narrative_spec` | `type: spec` | included in 7 shared imports | 0 | mixed | planned |
| 2 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/` active specs | included in 42 shared specs | `narrative_spec` | `type: spec` | included in 7 shared imports | 0 | mixed | planned |
| 3 | `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/` | 19 | `narrative_spec` | `type: spec` | 2 | 0 | explicit so far | planned |
| 4 | `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/` | 29 | `narrative_spec` / `completed_narrative_spec` | `type: spec` | 0 | 0 | unknown | planned |
| 5 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/` | 10 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | relationship/evidence, not primary spec by default | 1 primary OpenSpec-derived spec exists from earlier work | 0 | explicit | planned |
| 5 | `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/openspec/` | 17 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | relationship/evidence, not primary spec by default | 0 | 0 | unknown | planned |
| 6 | `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/openspec/` | 87 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | relationship/evidence after narrative dedupe | 0 | 0 | unknown | planned |
| 7 | `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_legacy/v1-node-prototype/openspec/` | 35 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | legacy relationship/evidence | 0 | 0 | unknown | planned |
| 8 | Historical documents discovered during source review | variable | document-like | `type: document` | 3 current ADR documents | 0 | explicit so far | planned |

## Per-Run Acceptance Contract

Each future delivery run MUST report:

1. selected phase/source subset,
2. new/updated entity paths,
3. skipped existing duplicates,
4. linked-only OpenSpec artefacts,
5. metadata_quality distribution,
6. negative guard result for `source_type: openspec_change_artifact`,
7. verification command statuses.
