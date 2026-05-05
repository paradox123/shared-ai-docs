# Scope Contract

## Change

`specops-completed-nebenkosten-2025-backfill`

## Goal

Import the completed Nebenkostenabrechnung 2025 slice specs from 2026-04-09 and 2026-04-10 into SpecOps Entity Notes so this cohesive Completed source group becomes dashboard-visible and deduplicated.

## In Scope

1. Process 14 completed Nebenkostenabrechnung 2025 source files:
   - eight `2026-04-09 Nebenkostenabrechnung 2025 ...` sources,
   - five not-yet-imported `2026-04-10 Nebenkostenabrechnung 2025 ...` sources,
   - one `2026-04-10 Nebenkostenabrechnung PDF Zahlungshinweis und Vorauszahlungsempfehlung.md` source.
2. Preserve the existing already-imported `BE2 Heiznebenkosten Sonderverteilung` entity and do not duplicate it.
3. Use `project: Nebenkostenabrechnung`.
4. Use `source_type: completed_narrative_spec`.
5. Mark all newly imported entities with `backfill_batch: historical-001-completed-1b`.
6. Link imported child specs to `nebenkostenabrechnung-pipeline-2026-03-14`.

## Out of Scope

1. No edits to the source specs.
2. No rerun of the historical Nebenkosten runtime commands; this is an entity backfill, not a functional Nebenkosten delivery run.
3. No import of `.history`, `.userguide` or RAG Completed sources.
4. No dashboard redesign.

## Acceptance Targets

1. Completed source count remains 32.
2. The selected Nebenkosten 2025 source subset has 14 files.
3. One exact-source entity in the subset exists before the run and is not duplicated.
4. The new batch contains exactly 13 entities.
5. All 14 selected source paths are represented by exactly one SpecOps spec entity after the run.
6. Completed source coverage increases from 11/32 to 24/32.
7. No imported entity has `source_type: openspec_change_artifact`.
8. The OpenSpec change validates in strict mode and reports complete status.

## Planned Verification

1. `find /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed -maxdepth 1 -type f -name '*.md' | wc -l`
2. Selected-subset source count for 2026-04-09/10 Nebenkosten 2025/PDF sources.
3. `rg -l 'backfill_batch: historical-001-completed-1b' /Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs | wc -l`
4. Exact-source search for the selected subset.
5. Duplicate-source guard over selected subset entity sources.
6. Missing/extra source guard between selected source files and entity source fields.
7. Completed coverage count via exact Completed source fields.
8. `rg -n 'source_type: openspec_change_artifact' /Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs || true`
9. `openspec validate specops-completed-nebenkosten-2025-backfill --strict --json`
10. `openspec status --change specops-completed-nebenkosten-2025-backfill --json`
11. `openspec validate --all --strict --json`
