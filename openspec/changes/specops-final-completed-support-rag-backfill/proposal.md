# Proposal

## Why

The Full Historical Backfill still has 8 unrepresented Completed sources. Without importing or explicitly classifying them, the SpecOps dashboards cannot close the shared-ai-docs Completed coverage group.

## What

This change imports the final Completed sources:

1. 5 DanielsVault RAG phase specs become `type: spec` entities.
2. 1 CheckBuild user guide becomes a `type: document` entity.
3. 2 Nebenkosten support/history files become `type: document` entities because they contain historical planning or blocked implementation notes rather than current primary spec contracts.

The run also updates the source inventory, Control Spec and backlog to show Completed coverage at 32/32.

## Impact

1. Completed coverage for shared-ai-docs moves from 24/32 to 32/32.
2. The dashboards gain visibility into the final RAG specs and support documents.
3. Existing primary entities are not duplicated.
4. Historical source files remain unchanged.
