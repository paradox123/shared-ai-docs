# Scope Contract

## In Scope

1. Import these three KI-fuer-KMU v2 support docs as document entities:
   - `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/APPLICATION-FLOW.md`,
   - `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/FREE-ENTRY-V2-SLICE-PLAN.md`,
   - `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/S0-REPO-FREEZE-LEGACY-QUARANTINE.md`.
2. Mark shared-ai-docs archived OpenSpec artifacts as excluded generated delivery evidence.
3. Update source inventory, Control Spec and backlog evidence.

## Out Of Scope

1. No import of shared-ai-docs archived OpenSpec change artifacts.
2. No edits to `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`.
3. No dashboard UI changes.
4. No runtime validation beyond metadata checks.

## Acceptance Targets

1. Exactly three new KI-fuer-KMU v2 support document entities exist.
2. KI-fuer-KMU v2 docs coverage is measurable as 6/6 document-like sources, including the three previously imported ADRs.
3. Shared-ai-docs archived OpenSpec artifacts are explicitly excluded from remaining backfill scope.
4. Formal marker scan has no current blocking marker in selected source docs.
5. OpenSpec validation and status checks pass.

## Planned Verification

1. Marker scan for `[MISSING]`, `[DECISION]` and `[BLOCKED]` in selected sources.
2. Count selected KI-fuer-KMU v2 root docs and full v2 docs.
3. Confirm three new document entity files exist.
4. Confirm all six KI-fuer-KMU v2 doc sources are represented by document entities.
5. Run `openspec validate specops-kmu-v2-support-documents-backfill --strict --json`.
6. Run `openspec status --change specops-kmu-v2-support-documents-backfill --json`.
7. Run `openspec validate --all --strict --json`.
