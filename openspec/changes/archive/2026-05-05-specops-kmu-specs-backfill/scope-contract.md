# Scope Contract

## Change

`specops-kmu-specs-backfill`

## Goal

Import the remaining `ki-fuer-kmu/_specs` narrative specs into SpecOps Entity Notes so they appear on the existing SpecOps spec dashboards through the standard `type: spec` Dataview queries.

## In Scope

1. Import the 17 missing Markdown sources from `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/`.
2. Use `project: Mittelstand KI Startbahn`.
3. Use `source_type: narrative_spec`.
4. Preserve source status semantics:
   - active v2 child specs keep `spec`, `plan`, `accepted` or `implemented` according to source header;
   - superseded legacy sources use `status: superseded` and `lifecycle: legacy`.
5. Mark all imported entities with `backfill_batch: historical-001-kmu`.
6. Update inventory/control evidence counts for `ki-fuer-kmu/_specs`.

## Out of Scope

1. No edits to the KI source specs.
2. No implementation work inside `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`.
3. No dashboard redesign; existing dashboard queries are expected to pick up the new entity notes.
4. No import of legacy OpenSpec artifacts from `ki-fuer-kmu/_legacy/v1-node-prototype/openspec`.

## Acceptance Targets

1. `ki-fuer-kmu/_specs` has 19 Markdown sources.
2. All 19 source paths are represented by exactly one SpecOps spec entity after the run.
3. The new batch contains exactly 17 entities.
4. Existing already-imported KI entities are not duplicated.
5. No imported KI entity has `source_type: openspec_change_artifact`.
6. The OpenSpec change validates in strict mode.

## Planned Verification

1. `find /Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs -maxdepth 1 -type f -name '*.md' | wc -l`
2. `rg -n 'source: /Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/' /Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs`
3. `rg -l 'backfill_batch: historical-001-kmu' /Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs | wc -l`
4. Duplicate-source guard over KI entity sources.
5. `rg -n 'source_type: openspec_change_artifact' /Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs || true`
6. `openspec validate specops-kmu-specs-backfill --strict --json`
7. `openspec status --change specops-kmu-specs-backfill --json`
8. `openspec validate --all --strict --json`
