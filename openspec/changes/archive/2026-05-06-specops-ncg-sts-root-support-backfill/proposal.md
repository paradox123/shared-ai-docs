# Proposal

## Why

After the first two NCG STS completed batches, the STS parent, optional/root specs and support TODOs still remain unrepresented in SpecOps. They should be imported before moving to older non-STS NCG infrastructure specs.

## What Changes

This change imports 7 selected NCG STS sources:

1. 6 primary `type: spec` entities.
2. 1 `type: document` entity for `STS Deferred Topics TODO`.

## Impact

1. NCG docs Specs coverage moves from 14/29 to 21/29.
2. STS parent/root/support context becomes dashboard-visible.
3. No NCG source specs or runtime repositories are modified.
