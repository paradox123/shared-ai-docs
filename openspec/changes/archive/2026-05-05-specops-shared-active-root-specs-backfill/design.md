# Design

## Source Set

The source set is exactly the root-level Markdown files under `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs`, excluding `Completed/`. At preflight, the set contains 13 files.

## Duplicate Handling

The RAG operating model already exists as `rag-operating-model-2026-04-26`. This run does not edit or duplicate it.

## Status Mapping

| Source signal | Entity status |
|---|---|
| `**Status:** 🟡 Spec` | `spec` |
| `**Status:** 🔵 Implemented` | `implemented` |
| `**Status:** 🟢 Accepted` | `accepted` |

## Metadata Quality

Most source metadata is explicit in the header. `SpecOps Environment Tracking Model` contains a formal parent-model decision marker, so its entity uses `metadata_quality: conflict` and explicit evidence for the marker.

## Entity Shape

Each imported entity uses:

1. `type: spec`
2. stable `id`
3. `project: Shared AI Platform`
4. absolute `source`
5. `source_type: narrative_spec`
6. `backfill_batch: historical-001-shared-active-root`
7. `metadata_quality`

## Dashboard Integration

Existing dashboards query `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs`. Entity creation is sufficient; local Dataview may need a refresh.
