# Design

## Source Set

The selected source set is the completed Nebenkostenabrechnung 2025 group around the 2026-04-09/10 delivery sequence:

1. 2025 umbrella execution path.
2. 2025 review and correction child slices.
3. 2025 PDF payment note and prepayment recommendation slice.

## Duplicate Handling

`2026-04-10 Nebenkostenabrechnung 2025 BE2 Heiznebenkosten Sonderverteilung Korrektur-Slice.md` is already represented by `nebenkostenabrechnung-be2-heiznebenkosten-sonderverteilung-2026-04-10` and is counted as done.

## Status Mapping

All selected sources are in `Completed/` and contain accepted/closed status or closeout evidence, so new entities use:

1. `status: accepted`
2. `lifecycle: workflow-2`
3. `environment_local: verified`
4. `metadata_quality: explicit`

## Entity Shape

Each imported entity uses:

1. `type: spec`
2. stable `id`
3. `project: Nebenkostenabrechnung`
4. absolute `source`
5. `source_type: completed_narrative_spec`
6. `backfill_batch: historical-001-completed-1b`
7. `parent: nebenkostenabrechnung-pipeline-2026-03-14`

## Dashboard Integration

Existing SpecOps dashboards query the entity store. Entity creation is sufficient; local Dataview may need a refresh.
