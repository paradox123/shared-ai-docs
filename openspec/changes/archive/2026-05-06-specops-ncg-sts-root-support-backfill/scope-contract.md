# Scope Contract

## In Scope

1. Import the next bounded NCG STS source subset:
   - parent/root STS onboarding source,
   - active/optional STS sources 04, 06 and 11,
   - accepted STS support slices 04.1 and 04.2,
   - the STS Deferred Topics TODO as a document entity.
2. Create 6 primary SpecOps `type: spec` entity notes and 1 `type: document` entity note.
3. Update inventory, Control Spec and backlog counts for NCG docs Specs from 14/29 to 21/29.

## Out Of Scope

1. No edits to NCG source specs.
2. No runtime implementation or validation inside `ncg-backend` or `ncg-security-token`.
3. No import of older non-STS NCG infrastructure specs in this run.
4. No OpenSpec relationship audit.
5. No promotion of the Deferred Topics TODO into a primary spec entity.

## Acceptance Targets

1. Exactly 7 new entity notes exist for batch `historical-001-ncg-sts-root-support`.
2. Batch split is exactly 6 specs and 1 document.
3. All 7 selected source paths are represented exactly once.
4. NCG docs Specs represented-source count increases from 14/29 to 21/29.
5. No duplicate NCG docs Specs source paths exist across SpecOps spec/document entities.
6. No `source_type: openspec_change_artifact` primary entity is created.
7. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Count all NCG docs Specs source files.
2. Count NCG docs Specs sources represented in SpecOps entities.
3. Count batch `historical-001-ncg-sts-root-support` and split by spec/document directories.
4. Run selected-source missing guard.
5. Run duplicate NCG docs Specs source guard.
6. Run negative OpenSpec artifact guard.
7. Run `openspec validate specops-ncg-sts-root-support-backfill --strict --json`.
8. Run `openspec status --change specops-ncg-sts-root-support-backfill --json`.
9. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. The parent onboarding source is still explicitly marked Draft, but its roadmap states the gate-relevant child specs are completed; it is imported with `status: draft` and `metadata_quality: conflict`.
2. The Deferred Topics TODO is represented as a document, not a primary spec, because it is a backlog/support artifact.
3. Runtime validation is not applicable because this change only creates SpecOps metadata/entity notes.
