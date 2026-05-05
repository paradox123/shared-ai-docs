## Why

The Delivery Plan is ready, but dashboards only show SpecOps entity notes. Phase 1A imports the first bounded batch so the selected historical specs become visible in the SpecOps spec and backfill dashboards.

## What Changes

1. Add five SpecOps `type: spec` entity notes for the Phase 1A completed Nebenkostenabrechnung sources.
2. Link them to existing project `Nebenkostenabrechnung`.
3. Mark them with `backfill_batch: historical-001-phase-1a`.
4. Capture duplicate guard and verification evidence.

## Impact

Dashboards that query `_shared/SpecOps/Entities/specs` will show five additional historical spec entities after Dataview refresh. No historical source files or application runtime files are changed.
