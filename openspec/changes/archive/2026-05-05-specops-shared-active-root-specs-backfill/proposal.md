# Proposal

## Why

The full historical backfill is moving through bounded source groups. The next recommended M-scale run is the active root of `_shared/shared-ai-docs/_specs`, where 13 narrative sources exist and only the RAG operating model already has a SpecOps spec entity.

## What Changes

1. Create 12 missing SpecOps `type: spec` entities for shared-ai-docs active root specs.
2. Preserve exact source traceability.
3. Use one batch marker, `historical-001-shared-active-root`.
4. Update source inventory and control evidence from 1/13 to 13/13 for the active root group.

## Impact

The Global Spec Board and related SpecOps dashboards will discover all active shared-ai-docs root specs through their existing entity queries. No dashboard query changes are required.
