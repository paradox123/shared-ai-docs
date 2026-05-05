# Acceptance Criteria Matrix

## Control Change Criteria

| Criterion | Status | Evidence |
|---|---|---|
| Active OpenSpec change exists | pass | `openspec/changes/specops-full-historical-backfill-delivery-plan/` |
| Scope Contract exists and is bounded | pass | `scope-contract.md` |
| Proposal, design, tasks, spec delta, matrix and evidence exist | pass | OpenSpec change directory |
| Archived false-start change is not implementation basis | pass | Control Spec and design notes |
| No entity imports are performed in this change | pass | Scope Contract out-of-scope |

## Source Group Coverage Baseline

| Phase | Source Path / Subset | Expected Source Count | source_type | Intended Entity Type | Current Imported Count | Remaining Candidate Count | Skipped / Linked-Only Count | metadata_quality Summary | Proposed Scale | Status |
|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 0 | `historical-001` batch | 5 | mixed narrative | `type: spec` | 5 | 0 | 0 | explicit/inferred/conflict | n/a | done |
| 1 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed/` | 32 | `completed_narrative_spec` plus support docs | `type: spec` or `type: document` by classification | 11 | 21 | 0 current | mixed | M next | in progress |
| 2 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/` active root files | 13 | `narrative_spec` | `type: spec` | 1 | 12 | 0 current | mixed | M | planned |
| 3 | `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/` | 19 | `narrative_spec` | `type: spec` | 19 | 0 | 0 current | explicit plus one inferred index | completed L | done |
| 4 | `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/` | 29 | `narrative_spec` / `completed_narrative_spec` | `type: spec` | 0 | 29 | 0 current | unknown | M then L | planned |
| 5 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/` | 19 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | relationship/evidence, not primary spec by default | 1 legacy OpenSpec-derived entity exists | 18 relationship candidates | tbd by narrative dedupe | explicit/unknown | S relationship audit | planned |
| 6 | `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/openspec/` | 17 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | relationship/evidence, not primary spec by default | 0 | 17 relationship candidates | tbd by narrative dedupe | unknown | S relationship audit | planned |
| 7 | `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/openspec/` | 87 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | relationship/evidence after narrative dedupe | 0 | 87 relationship candidates | tbd by narrative dedupe | unknown | XL blocked for manual import | planned |
| 8 | `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_legacy/v1-node-prototype/openspec/` | 35 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | legacy relationship/evidence | 0 | 35 relationship candidates | tbd by narrative dedupe | unknown | XL blocked for manual import | planned |
| 9 | `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/adr/` | 3 | document-like ADR | `type: document` | 3 | 0 | 0 current | explicit | n/a | done |

## First Proposed Delivery Run

| Run | Scale | Source Subset | Expected Source Count | Intended Entity Type | Acceptance Gate |
|---|---|---|---:|---|---|
| Phase 1A | S | `2026-03-23 Nebenkostenabrechnung Einzelabrechnung.md`, `2026-03-24 Nebenkostenabrechnung Applikation.md`, `2026-03-26 Stromkosten-Datenkorrektur und Test-Oracle Alignment.md`, `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`, `2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md` | 5 | primary `type: spec` unless duplicate guard finds an existing primary entity | five sources classified, imported or explicitly skipped with duplicate/evidence reason; dashboard count updated |

## Per-Run Acceptance Contract

Each future delivery run MUST report:

1. selected phase/source subset,
2. exact source files or source query,
3. new/updated entity paths,
4. skipped existing duplicates,
5. linked-only OpenSpec artefacts,
6. metadata_quality distribution,
7. negative guard result for `source_type: openspec_change_artifact`,
8. verification command statuses.
