# Proposal

## Why

The Mittelstand KI Startbahn sources were moved from the old private location into the dedicated `/Users/dh/Documents/DanielsVault/ki-fuer-kmu` repository. Existing SpecOps dashboards only render entity notes under `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs`, and only two of the 19 `ki-fuer-kmu/_specs` sources are currently represented there.

## What Changes

1. Create 17 missing SpecOps `type: spec` entity notes for `ki-fuer-kmu/_specs`.
2. Preserve the historical/current distinction by marking superseded old Free Entry sources as `status: superseded`.
3. Link current v2 child specs to the existing `Free Entry v2 Master Spec` entity where applicable.
4. Update inventory and control evidence so the dashboard-visible KI count is 19/19.

## Impact

The Global Spec Board and project-oriented SpecOps dashboards will discover the imported KI specs through their existing Dataview queries. No dashboard query change is required.
