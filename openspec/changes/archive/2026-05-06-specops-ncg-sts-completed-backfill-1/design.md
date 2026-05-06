# Design

## Batch Choice

The selected 7 sources are a coherent STS completed slice group from 2026-04-06. They share the same parent source and describe accepted STS hardening, compose, proxy, cutover, E2E and migration gates.

## Entity Shape

Each imported source becomes a primary `type: spec` entity with:

1. exact `source:` path,
2. `source_type: completed_narrative_spec`,
3. `backfill_batch: historical-001-ncg-sts-1`,
4. `project: NCG / STS`,
5. `parent_source:` pointing at the active STS onboarding spec.

## Metadata Quality

All 7 sources use `metadata_quality: explicit` because their headers include accepted statuses and no formal missing/decision/blocked markers were found.

## Runtime

No runtime validation is applicable for this metadata-only import.
