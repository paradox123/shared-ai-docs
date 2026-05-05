**Date:** 2026-05-04
**Status:** 🔵 Implemented
**Scope:** Erster vertikaler SpecOps-MVP-Slice fuer ein Obsidian-Dashboard unter `_shared/SpecOps/` mit RAG-nahen Entity Notes, Projektboard, Backlog-View und Missing-Metadata-View

---

## Kontext

Die Parent-Spec `2026-05-04 SpecOps Control Plane MVP Obsidian Dataview Mermaid.md` definiert SpecOps als lokale Control Plane fuer Specs, Dokumente, Artefakte, Releases, Environments und Learnings.

Dieser Child-Slice setzt nicht das gesamte SpecOps-Zielbild um. Er beweist nur, dass der Ansatz in Obsidian praktisch sichtbar wird:

1. Entity Notes mit Frontmatter liegen unter `_shared/SpecOps/Entities/`.
2. Das Dashboard liegt unter `_shared/SpecOps/Dashboard.md`.
3. Dataview kann daraus Projekt-, Spec-, Backlog- und Missing-Metadata-Sichten erzeugen.
4. RAG-nahe reale Specs und Artefakte werden exemplarisch erfasst.

## Ziel

Ein sichtbarer RAG Project Board Pilot existiert im Vault und beantwortet:

1. Welche RAG-nahen Specs sind erfasst?
2. In welchem Status stehen sie?
3. Welche Artefakte/Evidence sind verlinkt?
4. Welche Folgethemen liegen im SpecOps-Backlog?
5. Welche Entity Notes haben noch fehlende oder nur rekonstruierte Metadaten?

## Non-Goals

1. Kein Voll-Backfill aller historischen Specs.
2. Keine automatische Skill-/Workflow-Integration.
3. Keine eigenen Release-Entity-Notes im MVP; Releases bleiben zunaechst Felder an Specs/Artefakten.
4. Kein produktives Deployment-/Environment-Tracking.
5. Kein eigenes ADR-Board; ADRs/Dokumente werden nur im Entity-Schema vorbereitet.

## In Scope

1. `_shared/SpecOps/`-Ordnerstruktur:
   - `Dashboard.md`
   - `Reference/`
   - `Entities/`
   - `Dashboards/`
   - `Examples/`
2. Reference-Dateien:
   - `field-reference.md`
   - `project-taxonomy.md`
   - `relationship-types.md`
   - `status-definitions.md`
3. Entity Notes fuer den RAG-Pilot:
   - Projekt `DanielsVault RAG`
   - Spec `DanielsVault RAG Operating Model`
   - Spec `RAG Gate Alignment / Source Precision`
   - Artifact `RAG Operating Model Documentation`
   - Backlog Item `Document Entity Support for ADRs`
4. Dashboard-Dateien:
   - Portfolio-Map
   - RAG Project Board
   - SpecOps Backlog
   - Missing Metadata
5. Root-Dashboard `_shared/SpecOps/Dashboard.md`, das die Teilviews zusammenfuehrt.

## Decision Freeze Pack

### Zielbild und Scope

Der Slice erzeugt einen lauffaehigen, local-first SpecOps-Prototyp in Obsidian. Er nutzt Markdown-Entity-Notes mit YAML-Frontmatter und Dataview-Queries, um RAG-nahe Specs und Folgearbeit sichtbar zu machen.

### Betroffene Repositories / Vault-Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps`
2. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`

### Secret-/Config-Contract

Keine Secrets. Dataview ist im Ziel-Vault installiert.

### Datenmigration/Fallback

Kein Big-Bang-Backfill. Nur ausgewaehlte RAG-nahe Pilot-Entities werden manuell/Codex-gestuetzt erfasst.

### Sicherheits-/Exposure-Entscheidungen

Alle Daten bleiben lokal im DanielsVault.

### Abnahmekriterien (Go/No-Go)

Go:

1. `_shared/SpecOps/Dashboard.md` existiert.
2. Reference-Dateien fuer Felder, Status, Taxonomie und Beziehungstypen existieren.
3. Mindestens fuenf Entity Notes existieren.
4. RAG Project Board Dataview-Query ist vorhanden.
5. SpecOps Backlog Dataview-Query ist vorhanden.
6. Missing-Metadata Dataview-Query ist vorhanden.
7. Entity Notes verlinken auf reale Specs/Dokumente/Evidence, soweit bekannt.

No-Go:

1. Dashboard bleibt reine Prosa ohne Dataview-Sichten.
2. Entity Notes verwenden uneinheitliche Pflichtfelder.
3. Folgethemen bleiben nur in der Parent-Spec versteckt.

### Nachweisformat

1. Child-Spec: diese Datei.
2. Reale Dateien unter `_shared/SpecOps/`.
3. Verifikationskommandos mit Exit-Code `0`.

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Pflichtchecks:

1. `test -f _shared/SpecOps/Dashboard.md`
2. `test -f _shared/SpecOps/Reference/field-reference.md`
3. `test -f _shared/SpecOps/Reference/project-taxonomy.md`
4. `test -f _shared/SpecOps/Reference/relationship-types.md`
5. `test -f _shared/SpecOps/Reference/status-definitions.md`
6. `find _shared/SpecOps/Entities -type f -name '*.md' | wc -l`
7. `test "$(find _shared/SpecOps/Entities -type f -name '*.md' | wc -l | tr -d ' ')" -ge 5`
8. `rg -n '```dataview|type: spec|type: backlog_item|metadata_quality|DanielsVault RAG' _shared/SpecOps`
9. `test -f _shared/shared-ai-docs/_specs/2026-04-26\ DanielsVault\ RAG\ Operating\ Model\ rag-default\ qmd-optional.md`
10. `test -f _shared/shared-ai-docs/openspec/specs/rag-metric-gate-alignment/spec.md`

## Implementation Evidence

Target runtime: lokaler DanielsVault unter `/Users/dh/Documents/DanielsVault`.

| Check | Status | Evidence |
|-------|--------|----------|
| Core dashboard exists | ran-target | `test -f _shared/SpecOps/Dashboard.md` returned exit code `0`. |
| Field reference exists | ran-target | `test -f _shared/SpecOps/Reference/field-reference.md` returned exit code `0`. |
| Project taxonomy exists | ran-target | `test -f _shared/SpecOps/Reference/project-taxonomy.md` returned exit code `0`. |
| Relationship types exists | ran-target | `test -f _shared/SpecOps/Reference/relationship-types.md` returned exit code `0`. |
| Status definitions exists | ran-target | `test -f _shared/SpecOps/Reference/status-definitions.md` returned exit code `0`. |
| Minimum entity count | ran-target | `find _shared/SpecOps/Entities -type f -name '*.md'` found five entity notes. |
| Dataview and RAG markers | ran-target | `rg -n '```dataview\|type: spec\|type: backlog_item\|metadata_quality\|DanielsVault RAG' _shared/SpecOps` found dashboard queries and required markers. |
| RAG operating model source exists | ran-target | `test -f _shared/shared-ai-docs/_specs/2026-04-26\ DanielsVault\ RAG\ Operating\ Model\ rag-default\ qmd-optional.md` returned exit code `0`. |
| RAG gate alignment source exists | ran-target | `test -f _shared/shared-ai-docs/openspec/specs/rag-metric-gate-alignment/spec.md` returned exit code `0`. |

Post-review follow-up:

1. Deferred scope items were promoted into visible SpecOps backlog entity notes.
2. Portfolio project placeholders were added so the dashboard shows more than only the RAG pilot.
3. Project index and coverage dashboards were added to make current model coverage visible.

Verdict: READY for Obsidian review.

## Backlog Items

These items capture work that was intentionally out of scope for this first slice and must not disappear after the slice is accepted.

| Backlog Item | Status | Why It Exists | Next Action |
|--------------|--------|---------------|-------------|
| `mixed-backfill-pilot` | `done` | Tests the model beyond RAG with Nebenkosten umbrella, Nebenkosten slice and CheckBuild-style material. | Closed via `2026-05-04 SpecOps Mixed Backfill Pilot.md`. |
| `project-dashboard-expansion` | `done` | Moves from one project board to portfolio and per-project boards. | Closed via `2026-05-05 SpecOps Project Dashboard Expansion.md`. |
| `document-entity-support-for-adrs` | `done` | ADRs, runbooks, guides, architecture and evidence docs need first-class document treatment. | Closed via `2026-05-05 SpecOps Document Entity Support for ADRs.md`. |
| `full-historical-spec-backfill` | `triaged` | Full overview requires historical spec coverage. | Wait until mixed backfill validates reconstruction rules. |
| `release-entity-records` | `triaged` | Releases should link specs, artifacts, environments and evidence. | Promote when field-level release labels are insufficient. |
| `environment-tracking-model` | `triaged` | Spec status and artifact status need environment-level distinction. | Define after real examples appear in mixed backfill. |
| `skill-agent-learning-integration` | `triaged` | Accepted specs and retros should feed skills, custom agents and eval candidates. | Keep fields now, promote after repeated examples. |
| `automated-metadata-reconstruction` | `proposed` | Manual backfill will become repetitive. | Collect inferred examples before scripting. |

## Next Slice Recommendation

The next useful slice is `mixed-backfill-pilot`, not more dashboard styling. It should create entity notes for:

1. One Nebenkosten umbrella spec.
2. One Nebenkosten slice spec.
3. One CheckBuild-style spec.

Done signal:

1. The portfolio view shows at least three projects with real specs.
2. Each project has at least one linked spec or backlog item.
3. Missing metadata exposes reconstruction gaps instead of hiding them.
4. The decision is made whether per-project boards should be generated manually or from a reusable template.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-04 | User | Umsetzung des RAG Project Board Pilot freigegeben. |
| 2026-05-04 | Codex | Child-Spec fuer den ersten SpecOps-MVP-Slice erstellt. |
| 2026-05-04 | Codex | RAG Project Board Pilot unter `_shared/SpecOps/` umgesetzt und Verifikationsevidenz erfasst. |
| 2026-05-04 | User | Fehlende Sichtbarkeit zurueckgestellter Punkte und zu leere Portfolio-Sicht moniert. |
| 2026-05-04 | Codex | Deferred Scope als Backlog-Entities, Projektplatzhalter, Project Index und Coverage View nachgezogen. |
| 2026-05-05 | Codex | Backlog-Tabelle nach Accepted-Closeout von Mixed Backfill und Project Dashboard Expansion synchronisiert. |
| 2026-05-05 | Codex | Backlog-Tabelle nach Accepted-Closeout von Document Entity Support synchronisiert. |

SessionId: codex-desktop-current-thread
