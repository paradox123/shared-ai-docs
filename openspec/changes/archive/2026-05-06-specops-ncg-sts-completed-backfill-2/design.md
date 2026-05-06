# Design

## Batch Choice

The selected 7 sources are a coherent late STS completed slice group. They cover the post-migration backend rehearsal, vanity cutover gates, admin-plane reachability, account screen parity and frontend authorization-code handover.

## Entity Shape

Each imported source becomes a primary `type: spec` entity with:

1. exact `source:` path,
2. `source_type: completed_narrative_spec`,
3. `backfill_batch: historical-001-ncg-sts-2`,
4. `project: NCG / STS`,
5. `parent_source:` pointing at the active STS onboarding spec.

## Metadata Quality

All 7 sources use `metadata_quality: explicit` because their headers include accepted statuses and no formal missing/decision/blocked markers were found.

## Runtime

No runtime validation is applicable for this metadata-only import.
