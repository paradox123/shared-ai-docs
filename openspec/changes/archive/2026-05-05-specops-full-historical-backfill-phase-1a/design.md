## Context

SpecOps dashboards are entity-driven. The Delivery Plan counted and classified source files, but it did not import new entity notes. This run implements the first bounded import batch.

## Decisions

1. **Use completed path inference**
   - The sources live in `_specs/Completed`, so the default status is `accepted`.
   - If source text signals partial or conflicting implementation state, keep `metadata_quality: conflict`.

2. **Use existing project**
   - All five sources belong to `Nebenkostenabrechnung`.
   - No new project entity is required.

3. **Use explicit batch marker**
   - `backfill_batch: historical-001-phase-1a` distinguishes this run from the original `historical-001` batch.

4. **Relationship style**
   - The pipeline umbrella remains related or parent context where useful.
   - New entities may link to already imported parent entities, but no parent entity is edited in this run.

## Source Classification

| Source | Entity Type | Status | Metadata Quality | Notes |
|---|---|---|---|---|
| `2026-03-23 Nebenkostenabrechnung Einzelabrechnung.md` | `type: spec` | `accepted` | `inferred` | Completed path plus implementation-plan/spec content. |
| `2026-03-24 Nebenkostenabrechnung Applikation.md` | `type: spec` | `accepted` | `inferred` | Completed path; no explicit frontmatter status. |
| `2026-03-26 Stromkosten-Datenkorrektur und Test-Oracle Alignment.md` | `type: spec` | `accepted` | `inferred` | Completed path; analysis/spec correction artifact. |
| `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md` | `type: spec` | `accepted` | `inferred` | Completed path; explicit spec title and rules. |
| `2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md` | `type: spec` | `accepted` | `conflict` | Completed path, but source says it is not operationally fully implemented. |

## Runtime Notes

This is an entity-note import. No runtime service changes are made.
