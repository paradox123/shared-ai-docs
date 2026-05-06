# Proposal

## Why

The NCG docs Specs source group has 29 Markdown specs but no SpecOps entities keyed to the NCG docs source path. The first safe import should be a bounded, coherent STS subset rather than a bulk import.

## What Changes

This change imports 7 accepted STS Completed specs from 2026-04-06 as SpecOps `type: spec` entities and records the batch in inventory, Control Spec and backlog evidence.

## Impact

1. NCG docs Specs coverage moves from 0/29 to 7/29.
2. The STS cutover foundation specs become dashboard-visible in SpecOps.
3. No NCG source specs or runtime repositories are modified.
