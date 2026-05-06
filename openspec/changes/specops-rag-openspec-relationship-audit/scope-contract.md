# Scope Contract

## Batch Size Decision

This run intentionally increases batch size from the previous canonical-only audit. The selected RAG OpenSpec pool contains 17 markdown files, which fits Scale L (`16-30`) and is homogeneous enough for one relationship audit because all files belong to the same DanielsVault RAG OpenSpec source family.

## In Scope

1. Audit all 17 markdown files under `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/openspec/`.
2. Map the single canonical RAG OpenSpec spec and 16 archived OpenSpec artifacts as relationship/evidence sources.
3. Link the RAG OpenSpec material to existing SpecOps targets:
   - `danielsvault-local-rag-wissensplattform-2026-04-13`,
   - `danielsvault-rag-agent-integration-research-review-spec-closeout-2026-04-21`,
   - `rag-operating-model-2026-04-26`.
4. Update the shared OpenSpec relationship audit reference with a RAG batch.
5. Update the source inventory, Control Spec and backlog evidence.

## Out Of Scope

1. No import of RAG OpenSpec files as new primary SpecOps spec entities.
2. No runtime implementation or verification replay inside `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag`.
3. No edits to historical RAG OpenSpec source files.
4. No Nebenkosten, KI legacy or shared-ai-docs archived artifact audit in this run.
5. No dashboard UI changes.

## Acceptance Targets

1. RAG OpenSpec markdown count is exactly 17.
2. The relationship audit contains exactly 17 RAG OpenSpec rows.
3. No primary SpecOps entity is created with `source_type: openspec_change_artifact`.
4. The RAG source inventory phase advances from classified-only to relationship audit done.
5. Historical blocked evidence in the 2026-04-22 hardening archive is visible as metadata conflict context.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Marker scan for `[MISSING]`, `[DECISION]` and `[BLOCKED]` in the RAG OpenSpec pool.
2. Count RAG OpenSpec markdown files.
3. Count canonical RAG OpenSpec specs and archived RAG OpenSpec markdown artifacts.
4. Count RAG rows in `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/openspec-relationship-audit.md`.
5. Run the negative guard for primary entities with `source_type: openspec_change_artifact`.
6. Run `openspec validate specops-rag-openspec-relationship-audit --strict --json`.
7. Run `openspec status --change specops-rag-openspec-relationship-audit --json`.
8. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. Old `[BLOCKED]` strings occur in archived evidence files. They describe historical runtime blockers from 2026-04-22, not current blockers for this metadata-only relationship audit.
2. Runtime validation is not applicable because this change only edits SpecOps metadata/reference documentation and OpenSpec delivery artifacts.
3. A future closeout will create another canonical OpenSpec spec for this audit; closeout should synchronize counts if the user accepts the change.
