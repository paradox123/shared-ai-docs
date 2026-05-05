# Design

## Source Classification

The source folder is homogeneous enough for an L-scale manual import because all 19 files are narrative spec sources, and an earlier S run has already verified the import pattern. Two sources are already imported from `historical-001`; this change imports only the remaining 17 exact source paths.

## Status Mapping

| Source signal | Entity status |
|---|---|
| `**Status:** 🟠 Plan` | `plan` |
| `**Status:** 🟡 Spec` | `spec` |
| `**Status:** 🟢 Accepted` | `accepted` |
| `**Status:** 🔵 Implemented` | `implemented` |
| Leading `Superseded for Free Entry v2` notice | `superseded`, `lifecycle: legacy` |

Superseded notices win over older source header statuses because dashboard users need to distinguish current v2 work from historical design sources.

## Entity Shape

Each imported entity uses:

1. `type: spec`
2. stable `id`
3. `project: Mittelstand KI Startbahn`
4. `source` with the absolute `ki-fuer-kmu/_specs` path
5. `source_type: narrative_spec`
6. `backfill_batch: historical-001-kmu`
7. `metadata_quality: explicit` unless the source is an index with inferred status semantics

## Dashboard Integration

Existing dashboards query `FROM "_shared/SpecOps/Entities/specs" WHERE type = "spec"`, so entity creation is sufficient. Dataview may require a local Obsidian refresh, but no code/query change is needed.
