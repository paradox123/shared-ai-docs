## Why

The Full Historical Backfill Control Spec is now implementation-ready as a control-plane artifact, but the earlier OpenSpec change was too narrow and has been archived. SpecOps needs one active delivery-control change that reflects the current repository layout, current source counts and the new `ki-fuer-kmu` source location.

## What Changes

1. Create an active OpenSpec change for the delivery-control plan.
2. Use the updated source inventory as the baseline.
3. Define phased source groups, entity classification rules, duplicate guards and run-scale rules.
4. Define the first proposed Scale-S delivery run without importing entities in this change.
5. Capture verification evidence for the control-plane implementation.

## Capabilities

### New Capabilities

- `specops-historical-backfill-delivery-control`: active control-plane capability for bounded historical backfill delivery runs.

### Modified Capabilities

- None. Existing canonical specs are not modified by this change.

## Impact

Affected files are limited to the Control Spec and this OpenSpec change directory. No application runtime, backend service, historical source file, entity import, or automation is changed.
