# Scope Contract

## Change

`specops-shared-active-root-specs-backfill`

## Goal

Import the remaining active root specs from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs` into SpecOps Entity Notes so the existing dashboards can discover all active shared-ai-docs root specs.

## In Scope

1. Import the 12 missing root-level Markdown sources from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs`.
2. Exclude `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed`.
3. Preserve the existing already-imported RAG operating model entity.
4. Use `project: Shared AI Platform` according to the controlled project taxonomy.
5. Use `source_type: narrative_spec`.
6. Mark all newly imported entities with `backfill_batch: historical-001-shared-active-root`.
7. Preserve visible metadata uncertainty with `metadata_quality: conflict` when the source contains a formal decision marker.

## Out of Scope

1. No edits to the source specs themselves.
2. No import from `Completed/`, NCG docs or OpenSpec relationship groups.
3. No dashboard redesign.
4. No OpenSpec change artifacts imported as primary spec entities.

## Acceptance Targets

1. Root source count is 13.
2. One exact-source entity exists before the run and is not duplicated.
3. The new batch contains exactly 12 entities.
4. All 13 root source paths are represented by exactly one SpecOps spec entity after the run.
5. No imported entity has `source_type: openspec_change_artifact`.
6. The OpenSpec change validates in strict mode and reports complete status.

## Planned Verification

1. `find /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs -maxdepth 1 -type f -name '*.md' | wc -l`
2. `rg -n 'source: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/[^/]+\\.md' /Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs`
3. `rg -l 'backfill_batch: historical-001-shared-active-root' /Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs | wc -l`
4. Duplicate-source guard over shared active root entity sources.
5. Missing/extra source guard between root source files and entity source fields.
6. `rg -n 'source_type: openspec_change_artifact' /Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs || true`
7. `openspec validate specops-shared-active-root-specs-backfill --strict --json`
8. `openspec status --change specops-shared-active-root-specs-backfill --json`
9. `openspec validate --all --strict --json`
