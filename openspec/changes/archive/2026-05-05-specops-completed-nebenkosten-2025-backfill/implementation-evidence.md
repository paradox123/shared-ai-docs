# Implementation Evidence

## Pre-Implementation Analysis

1. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed` contains 32 Markdown source files.
2. The selected Nebenkostenabrechnung 2025 source subset contains 14 files.
3. Exactly one selected exact source already had an entity before the run: `nebenkostenabrechnung-be2-heiznebenkosten-sonderverteilung-2026-04-10`.
4. The selected source files are accepted/closed Completed specs with closeout evidence.
5. This run is an entity backfill only; no historical Nebenkosten runtime commands were rerun.

## Imported Entities

| Entity | Source | Status |
|---|---|---|
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-gebaeudeversicherungen-review-2026-04-09.md` | `2026-04-09 Nebenkostenabrechnung 2025 Gebäudeversicherungen Review-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-hkv-korrektur-2026-04-09.md` | `2026-04-09 Nebenkostenabrechnung 2025 HKV Korrektur-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-messwerte-review-2026-04-09.md` | `2026-04-09 Nebenkostenabrechnung 2025 Messwerte Review-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-realdaten-und-abrechnungspfad-2026-04-09.md` | `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-restkosten-review-2026-04-09.md` | `2026-04-09 Nebenkostenabrechnung 2025 Restkosten Review-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-stromtarif-korrektur-2026-04-09.md` | `2026-04-09 Nebenkostenabrechnung 2025 Stromtarif Korrektur-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-tibber-review-2026-04-09.md` | `2026-04-09 Nebenkostenabrechnung 2025 Tibber Review-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-warmwasserkosten-ableitung-2026-04-09.md` | `2026-04-09 Nebenkostenabrechnung 2025 Warmwasserkosten Ableitung-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-be2-wasser-und-sonderverteilung-2026-04-10.md` | `2026-04-10 Nebenkostenabrechnung 2025 BE2 Wasser und Sonderverteilung Korrektur-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-carryover-brennstoffkosten-2026-04-10.md` | `2026-04-10 Nebenkostenabrechnung 2025 Carryover Brennstoffkosten Korrektur-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-ne1-leerstand-messwerte-nachtrag-2026-04-10.md` | `2026-04-10 Nebenkostenabrechnung 2025 NE1 Leerstand Messwerte Nachtrag-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-2025-periodische-verbrauchsverteilung-nachtrag-2026-04-10.md` | `2026-04-10 Nebenkostenabrechnung 2025 Periodische Verbrauchsverteilung Nachtrag-Slice.md` | imported |
| `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/nebenkostenabrechnung-pdf-zahlungshinweis-vorauszahlungsempfehlung-2026-04-10.md` | `2026-04-10 Nebenkostenabrechnung PDF Zahlungshinweis und Vorauszahlungsempfehlung.md` | imported |

## Verification Checklist

| Check | Status | Evidence |
|---|---|---|
| Completed source files | ran | `find .../Completed -maxdepth 1 -type f -name '*.md' \| wc -l` returned `32`. |
| Selected source files | ran | Selected 2026-04-09/10 Nebenkosten query returned `14`. |
| New batch count | ran | `rg -l 'backfill_batch: historical-001-completed-1b' ... \| wc -l` returned `13`. |
| Completed coverage | ran | Exact Completed source fields in spec entities returned `24`. |
| Selected source entities | ran | Exact selected source fields returned `14`. |
| Duplicate selected source guard | ran | Sorted selected source paths with `uniq -d` returned no duplicates. |
| Missing selected source guard | ran | `comm -23` between selected source files and entity source fields returned no output. |
| Extra selected source guard | ran | `comm -13` between selected source files and entity source fields returned no output. |
| Negative OpenSpec guard | ran | `rg -n 'source_type: openspec_change_artifact' ...` returned no matches. |
| OpenSpec validate | ran | `openspec validate specops-completed-nebenkosten-2025-backfill --strict --json` returned `valid: true`. |
| OpenSpec status | ran | `openspec status --change specops-completed-nebenkosten-2025-backfill --json` returned `isComplete: true`. |
| OpenSpec validate all | ran | `openspec validate --all --strict --json` returned 6/6 passed. |
