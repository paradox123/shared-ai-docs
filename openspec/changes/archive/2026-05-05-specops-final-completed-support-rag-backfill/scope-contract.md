# Scope Contract

## In Scope

1. Import the final 8 missing Completed sources from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed/`.
2. Classify the 5 DanielsVault RAG phase documents as primary `type: spec` entities.
3. Classify the CheckBuild user guide and 2 Nebenkosten support/history documents as `type: document` entities.
4. Update the SpecOps source inventory, Control Spec and backlog evidence to show Completed coverage at 32/32.

## Out Of Scope

1. No edits to historical source files.
2. No implementation inside RAG, NCG or Nebenkosten runtime repositories.
3. No OpenSpec relationship audit for archived OpenSpec folders.
4. No automated metadata reconstruction.
5. No promotion of support guides, history logs or blocked implementation plans into primary spec entities.

## Acceptance Targets

1. Exactly 8 new entity notes exist for batch `historical-001-completed-final`.
2. Batch split is exactly 5 `type: spec` entities and 3 `type: document` entities.
3. Completed source coverage across SpecOps spec and document entities is 32/32 with no duplicate source paths.
4. `source_type: openspec_change_artifact` is not used for any primary entity in this run.
5. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Count Completed source files.
2. Count Completed sources represented in SpecOps entities.
3. Check missing Completed sources after import.
4. Check duplicate Completed source paths after import.
5. Check batch size and type split.
6. Run negative guard for `source_type: openspec_change_artifact`.
7. Run `openspec validate specops-final-completed-support-rag-backfill --strict --json`.
8. Run `openspec status --change specops-final-completed-support-rag-backfill --json`.
9. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. Historical blocker markers inside Nebenkosten support documents are preserved as source evidence and are not current blockers for this classification-only run.
2. Runtime validation is not applicable because this change only creates local SpecOps metadata/documentation.
3. `metadata_quality: conflict` is intentionally used where Completed-path status conflicts with old blocker markers.
