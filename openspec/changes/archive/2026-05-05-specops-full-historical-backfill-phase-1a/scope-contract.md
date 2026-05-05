# Scope Contract

## Mode

OpenSpec mode. This run imports the first Scale-S batch from the SpecOps Full Historical Backfill Delivery Plan.

## In Scope

1. Create five `type: spec` entity notes under `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/`.
2. Use exactly these source files from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed/`:
   - `2026-03-23 Nebenkostenabrechnung Einzelabrechnung.md`
   - `2026-03-24 Nebenkostenabrechnung Applikation.md`
   - `2026-03-26 Stromkosten-Datenkorrektur und Test-Oracle Alignment.md`
   - `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`
   - `2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
3. Assign all five entities to project `Nebenkostenabrechnung`.
4. Mark all five with `backfill_batch: historical-001-phase-1a`.
5. Preserve duplicate guards by not creating entities for already imported sources.
6. Record metadata quality explicitly, including conflicts where a Completed path and source status are not fully aligned.

## Out Of Scope

1. No import beyond the five listed source files.
2. No edits to historical source specs.
3. No source file renames, typo fixes or content cleanup.
4. No dashboard UX changes.
5. No automatic metadata reconstruction.
6. No NCG backend runtime or application code changes.

## Acceptance Targets

1. Five new SpecOps spec entities exist.
2. Each entity has required fields: `type`, `id`, `title`, `project`, `status`, `source`, `source_type`, `backfill_batch`, `metadata_quality`.
3. Each entity source path exists.
4. No entity uses `source_type: openspec_change_artifact`.
5. Dashboard queries will pick up the entities via `FROM "_shared/SpecOps/Entities/specs"` and `WHERE backfill_batch`.
6. Phase 1A evidence lists imported and skipped sources.

## Planned Verification

1. `test -f` for each created entity.
2. `test -f` for each source path.
3. `rg -n 'historical-001-phase-1a' _shared/SpecOps/Entities/specs`
4. `rg -n 'source_type: openspec_change_artifact' _shared/SpecOps/Entities/specs` as a negative guard; if it returns no matches, the guard passes.
5. Count Phase 1A entities with `rg -l 'backfill_batch: historical-001-phase-1a' _shared/SpecOps/Entities/specs | wc -l`.
6. `openspec validate specops-full-historical-backfill-phase-1a --strict --json`
7. `openspec status --change specops-full-historical-backfill-phase-1a --json`
