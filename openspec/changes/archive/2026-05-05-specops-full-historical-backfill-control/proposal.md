## Why

The accepted `historical-001` slice created a reliable source inventory and first batch, but the remaining full historical backfill is too broad to manage as many small Child-Specs. SpecOps needs one OpenSpec-controlled workstream that turns the inventory into phased, verifiable delivery runs.

## What Changes

- Add an OpenSpec control capability for the remaining SpecOps Full Historical Backfill.
- Define source-to-entity rules for narrative specs, completed narrative specs, documents and OpenSpec artefacts.
- Define phased source groups derived from the inventory.
- Define acceptance and evidence structures for future delivery runs.
- Preserve `historical-001` as an accepted baseline and prevent duplicate imports.
- Keep actual entity creation out of this change; future delivery runs will operate from Scope Contracts against the OpenSpec tasks/phases.

## Capabilities

### New Capabilities

- `specops-historical-backfill-control`: Controls phased historical SpecOps backfill from the accepted inventory baseline, including entity rules, OpenSpec relationship guards and acceptance evidence.

### Modified Capabilities

- None.

## Impact

- Affected areas are documentation/control artefacts only:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/changes/specops-full-historical-backfill-control/`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Full Historical Backfill Control Spec.md`
- No runtime code, APIs, external integrations or NCG backend services are changed.
