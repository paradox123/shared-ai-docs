# Scope Contract

## In Scope

1. Audit these archived Nebenkosten OpenSpec change groups under `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/openspec/changes/archive/`:
   - `2026-04-10-2026-04-09-2025-messwerte-review`,
   - `2026-04-10-2026-04-09-2025-operativpfad`,
   - `2026-04-10-2026-04-09-2025-restkosten-review`,
   - `2026-04-10-2026-04-09-2025-tibber-review`,
   - `2026-04-10-2026-04-09-2025-versicherung-review`,
   - `2026-04-10-2026-04-09-2025-warmwasser-derivation`.
2. Map all 32 selected markdown files as relationship/evidence sources.
3. Link selected sources to existing Nebenkosten SpecOps targets:
   - `nebenkostenabrechnung-2025-messwerte-review-2026-04-09`,
   - `nebenkostenabrechnung-2025-realdaten-und-abrechnungspfad-2026-04-09`,
   - `nebenkostenabrechnung-2025-restkosten-review-2026-04-09`,
   - `nebenkostenabrechnung-2025-tibber-review-2026-04-09`,
   - `nebenkostenabrechnung-2025-gebaeudeversicherungen-review-2026-04-09`,
   - `nebenkostenabrechnung-2025-warmwasserkosten-ableitung-2026-04-09`.
4. Update the shared OpenSpec relationship audit reference with Nebenkosten batch 1.
5. Update the source inventory, Control Spec and backlog evidence to show Nebenkosten OpenSpec relationship coverage at 32/87.

## Out Of Scope

1. No import of Nebenkosten OpenSpec files as new primary SpecOps spec entities.
2. No edits to `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung`.
3. No shared-ai-docs archive artifact audit.
4. No Nebenkosten runtime, PDF generation, or calculation validation.
5. No dashboard UI changes.

## Acceptance Targets

1. Selected Nebenkosten OpenSpec markdown count is exactly 32.
2. The relationship audit contains exactly 32 Nebenkosten batch 1 rows.
3. Full Nebenkosten OpenSpec coverage is measurable as 32/87 mapped.
4. No primary SpecOps entity is created with `source_type: openspec_change_artifact`.
5. Marker scan shows no current blocking marker in selected sources.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Marker scan for `[MISSING]`, `[DECISION]` and `[BLOCKED]` in selected Nebenkosten sources.
2. Count selected Nebenkosten batch 1 markdown files.
3. Count full Nebenkosten OpenSpec markdown files and total Nebenkosten audit rows.
4. Count Nebenkosten batch 1 rows in `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/openspec-relationship-audit.md`.
5. Run the negative guard for primary entities with `source_type: openspec_change_artifact`.
6. Run `openspec validate specops-nebenkosten-openspec-relationship-audit-1 --strict --json`.
7. Run `openspec status --change specops-nebenkosten-openspec-relationship-audit-1 --json`.
8. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. Selected Nebenkosten OpenSpec material is delivery/evidence context and remains relationship/evidence only; narrative completed specs remain the canonical primary SpecOps entities.
2. Runtime validation is not applicable because this change only edits SpecOps metadata/reference documentation and OpenSpec delivery artifacts.
