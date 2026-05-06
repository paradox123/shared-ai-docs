# Design

## Batch Choice

The selected 8 sources are the remaining older NCG infrastructure and CI/CD specs not covered by the STS-focused batches.

## Entity Shape

Each imported source becomes a primary `type: spec` entity with:

1. exact `source:` path,
2. `source_type: completed_narrative_spec`,
3. `backfill_batch: historical-001-ncg-infrastructure-final`,
4. project aligned to NCG infrastructure, CI/CD or docs as appropriate.

## Metadata Quality

Sources with old formal open markers use `metadata_quality: conflict`; this preserves the fact that the file is in `Completed/` while still containing historical missing or decision markers.

## Runtime

No runtime validation is applicable for this metadata-only import.
