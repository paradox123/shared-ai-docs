# Scope Contract

## In Scope

1. Audit these archived Nebenkosten OpenSpec change groups:
   - `2026-04-10-2026-04-10-2025-be2-heiznebenkosten-correction`,
   - `2026-04-10-2026-04-10-2025-be2-water-fuel-correction`,
   - `2026-04-10-2026-04-10-2025-carryover-brennstoff-correction`,
   - `2026-04-10-2026-04-10-2025-hkv-correction`,
   - `2026-04-10-2026-04-10-2025-ne1-vacancy-readings`.
2. Map all 30 selected markdown files as relationship/evidence sources.
3. Link selected sources to existing Nebenkosten SpecOps targets:
   - `nebenkostenabrechnung-be2-heiznebenkosten-sonderverteilung-2026-04-10`,
   - `nebenkostenabrechnung-2025-be2-wasser-und-sonderverteilung-2026-04-10`,
   - `nebenkostenabrechnung-2025-carryover-brennstoffkosten-2026-04-10`,
   - `nebenkostenabrechnung-2025-hkv-korrektur-2026-04-09`,
   - `nebenkostenabrechnung-2025-ne1-leerstand-messwerte-nachtrag-2026-04-10`.
4. Update source inventory, Control Spec and backlog evidence to show Nebenkosten OpenSpec coverage at 62/87.

## Out Of Scope

1. No import of Nebenkosten OpenSpec files as new primary SpecOps spec entities.
2. No edits to `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung`.
3. No runtime, PDF generation, calculation validation, or dashboard UI changes.

## Acceptance Targets

1. Selected Nebenkosten OpenSpec markdown count is exactly 30.
2. The relationship audit contains exactly 62 total Nebenkosten rows after this batch.
3. Full Nebenkosten OpenSpec coverage is measurable as 62/87 mapped.
4. No primary SpecOps entity is created with `source_type: openspec_change_artifact`.
5. Marker scan shows no current blocking marker in selected sources.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Marker scan for `[MISSING]`, `[DECISION]` and `[BLOCKED]` in selected sources.
2. Count selected batch 2 markdown files.
3. Count full Nebenkosten OpenSpec markdown files and total Nebenkosten audit rows.
4. Run negative primary entity guard.
5. Run `openspec validate specops-nebenkosten-openspec-relationship-audit-2 --strict --json`.
6. Run `openspec status --change specops-nebenkosten-openspec-relationship-audit-2 --json`.
7. Run `openspec validate --all --strict --json`.
