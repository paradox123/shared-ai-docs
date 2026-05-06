# Scope Contract

## In Scope

1. Audit the remaining Nebenkosten OpenSpec sources:
   - `2026-04-10-2026-04-10-2025-periodic-consumption-allocation`,
   - `2026-04-10-2026-04-10-2025-stromtarif-correction`,
   - `2026-04-10-2026-04-10-2025-warmwasser-revalidation`,
   - `2026-04-11-2026-04-10-pdf-vorauszahlungsempfehlung`,
   - canonical `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/openspec/specs/pdf-vorauszahlungsempfehlung/spec.md`.
2. Map all 25 selected markdown files as relationship/evidence sources.
3. Link selected sources to existing Nebenkosten SpecOps targets:
   - `nebenkostenabrechnung-2025-periodische-verbrauchsverteilung-nachtrag-2026-04-10`,
   - `nebenkostenabrechnung-2025-stromtarif-korrektur-2026-04-09`,
   - `nebenkostenabrechnung-2025-warmwasserkosten-ableitung-2026-04-09`,
   - `nebenkostenabrechnung-pdf-zahlungshinweis-vorauszahlungsempfehlung-2026-04-10`.
4. Update source inventory, Control Spec and backlog evidence to close Nebenkosten OpenSpec coverage at 87/87.

## Out Of Scope

1. No import of Nebenkosten OpenSpec files as new primary SpecOps spec entities.
2. No edits to `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung`.
3. No runtime, PDF generation, calculation validation, or dashboard UI changes.

## Acceptance Targets

1. Selected Nebenkosten OpenSpec markdown count is exactly 25.
2. The relationship audit contains exactly 87 total Nebenkosten rows after this batch.
3. Full Nebenkosten OpenSpec coverage is measurable as 87/87 mapped.
4. No primary SpecOps entity is created with `source_type: openspec_change_artifact`.
5. Marker scan shows no current blocking marker in selected sources.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Marker scan for `[MISSING]`, `[DECISION]` and `[BLOCKED]` in selected sources.
2. Count selected batch 3 markdown files.
3. Count full Nebenkosten OpenSpec markdown files and total Nebenkosten audit rows.
4. Run negative primary entity guard.
5. Run `openspec validate specops-nebenkosten-openspec-relationship-audit-3 --strict --json`.
6. Run `openspec status --change specops-nebenkosten-openspec-relationship-audit-3 --json`.
7. Run `openspec validate --all --strict --json`.
