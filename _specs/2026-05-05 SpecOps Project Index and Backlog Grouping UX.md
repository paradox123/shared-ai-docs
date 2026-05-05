**Date:** 2026-05-05
**Status:** 🟢 Accepted
**Scope:** SpecOps UX Follow-up fuer Project Index als Projekt-Auswahl und Backlog-Gruppierung nach Projekt

---

## Kontext

Die SpecOps Dashboard UX wurde in zwei Slices deutlich verbessert:

1. `SpecOps Dashboard UX Overview` hat Tabellen durch Snapshot-, Lane-, Triage- und Projektarbeitsansichten ergaenzt.
2. `SpecOps Clickable Dashboard Navigation Cleanup` hat Karten klickbar gemacht, das Root-Dashboard entschlackt und Projektboards in aktive Arbeit vs. Closeout getrennt.

Nach dem Review bleiben zwei naheliegende UX-Luecken:

1. `project-index.md` ist noch eine einfache Tabelle, obwohl es als zentrale Projekt-Auswahl dienen koennte.
2. `specops-backlog.md` gruppiert nach Status, aber innerhalb der Status-Lanes noch nicht nach Projekt. Dadurch ist weniger klar, welches Projekt als naechstes Aufmerksamkeit braucht.

Dieses Spec beschreibt den naechsten kleinen Dashboard-only Slice.

## Ziel

SpecOps soll Projekt- und Backlog-Navigation noch schneller machen:

1. Der Project Index zeigt pro Projekt eine klickbare Karte mit Status, Counts und Projektboard-/Entity-Drilldown.
2. Das Backlog bleibt statusorientiert, gruppiert Items innerhalb der Lanes aber projektweise.
3. Der Nutzer kann vom Root oder Project Index schnell entscheiden, welches Projekt und welches Backlog-Thema als naechstes relevant ist.

## In Scope

1. `_shared/SpecOps/Dashboards/project-index.md` von Tabelle auf DataviewJS-Projektkarten umstellen.
2. Projektkarten zeigen mindestens:
   - Projekttitel
   - Projektstatus
   - Metadata Quality
   - Anzahl Specs
   - Anzahl aktiver Specs
   - Anzahl Backlog-Items
   - Anzahl Metadata-Attention-Items
   - Link zur Project Entity
   - Link zum Projektboard, falls vorhanden
3. `_shared/SpecOps/Dashboards/specops-backlog.md` so anpassen, dass Status-Lanes innerhalb jeder Lane nach Projekt gruppiert werden.
4. Backlog-Karten bleiben klickbar.
5. Bestehende Detailtabellen bleiben als Fallback erhalten.

## Out of Scope

1. Keine Entity-Schema-Aenderung.
2. Keine neuen Pflichtfelder in Entity Notes.
3. Keine neuen Project Entity Notes.
4. Keine historische Backfill-Erweiterung.
5. Keine Aenderung an Skills, Agents, RAG-Runtime oder Fachcode.
6. Kein CSS- oder Obsidian-Plugin-Zwang.

## Requirements

### R1 - Project Index Cards

Der Project Index muss eine echte Projekt-Auswahl sein, nicht nur eine Tabelle.

Akzeptanzkriterien:

1. `project-index.md` enthaelt eine DataviewJS-Kartenansicht.
2. Jede Projektkarte zeigt Titel, Status, Metadata Quality, Spec Count, aktive Spec Count, Backlog Count und Metadata-Attention Count.
3. Jede Projektkarte verlinkt mindestens die Project Entity.
4. Fuer bekannte Projektboards verlinkt die Karte zusaetzlich das Projektboard.
5. Die alte Tabelle bleibt hoechstens als `## Details` erhalten.

### R2 - Backlog Grouped by Project

Das Backlog muss innerhalb der Status-Lanes nach Projekt gruppiert sein.

Akzeptanzkriterien:

1. `specops-backlog.md` behalt Status-Lanes fuer `proposed`, `triaged`, `ready_for_spec`, `promoted`, `done`, `parked`.
2. Innerhalb jeder Status-Lane werden Items nach Projekt gruppiert.
3. Jede Projektgruppe zeigt Projektname und Item Count.
4. Backlog-Items bleiben klickbar.
5. Die Detailtabelle bleibt erhalten.

### R3 - Root Navigation Compatibility

Die bestehende Root-Navigation darf durch diesen Slice nicht verschlechtert werden.

Akzeptanzkriterien:

1. Root-Dashboard verlinkt weiterhin `Dashboards/project-index`.
2. Project Index bleibt vom Root-Dashboard aus erreichbar.
3. Root-Dashboard wird nicht wieder zu einer grossen Embed-Seite.

## UX Model

Der erwartete Nutzerfluss ist:

1. Root-Dashboard oeffnen.
2. Project Index oder Backlog aus den Board-Karten oeffnen.
3. Im Project Index ein Projekt anhand von Counts und Warnungen auswaehlen.
4. Im Backlog nach Status und Projekt erkennen, was als naechstes Aufmerksamkeit braucht.
5. Von Karten direkt in Entity, Projektboard oder Backlog-Item springen.

## Data and Implementation Constraints

1. Quelle der Wahrheit bleiben Entity Notes unter `_shared/SpecOps/Entities/`.
2. DataviewJS ist erlaubt.
3. Bekannte Projektboard-Pfade duerfen in einer lokalen Mapping-Tabelle im DataviewJS-Block gepflegt werden.
4. Wenn kein Projektboard existiert, bleibt die Project Entity der Drilldown.
5. Keine neuen Felder duerfen fuer die Anzeige vorausgesetzt werden; fehlende Werte werden defensiv angezeigt.

## Decision Freeze Pack

### Zielbild und Scope

Dieser Slice verbessert Projekt- und Backlog-Navigation in den bestehenden SpecOps-Dashboards. Er veraendert nur Markdown-/DataviewJS-Dashboard-Dateien und die zugehoerige Spec-Evidence.

### Betroffene Vault-Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/project-index.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/specops-backlog.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md` nur falls Linkkompatibilitaet oder Evidence einen kleinen Guard braucht
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/specops-project-index-backlog-grouping-ux.md`
5. Diese Spec unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/`

### Secret-/Config-Contract

Keine Secrets. Obsidian Dataview und DataviewJS bleiben lokale Anzeigevoraussetzungen.

### Datenmigration/Fallback

Keine Datenmigration. Bestehende Detailtabellen bleiben als Fallback erhalten.

### Externe Integrationen

Keine externen Integrationen.

### Sicherheits-/Exposure-Entscheidungen

Alle Daten bleiben lokal im DanielsVault.

### Abnahmekriterien Go/No-Go

Go:

1. Project Index hat klickbare Projektkarten mit Counts.
2. Backlog Status-Lanes gruppieren Items nach Projekt.
3. Detailtabellen bleiben erreichbar.
4. Root-Dashboard verlinkt Project Index weiterhin und wird nicht wieder zur Embed-Seite.
5. Verification Commands laufen mit Exit-Code `0`, ausser explizit negative Guards.

No-Go:

1. Project Index bleibt nur eine Tabelle.
2. Backlog verliert Status-Lanes.
3. Backlog-Karten werden wieder statischer Text.
4. Der Slice fuehrt Entity-Schema-, Backfill- oder Skill-Aenderungen ein.

### Owner fuer offene Risiken

1. User: Obsidian-Review, ob Project Index und Backlog-Gruppierung praktisch scanbar sind.
2. Codex: Markdown-/DataviewJS-Struktur, Linklogik und Shell-Verifikation.

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Shell-/Plattformvertrag:

1. Zielplattform ist macOS.
2. Shell ist `zsh`.
3. `rg` ist installiert und wird fuer Textchecks verwendet.
4. `node` ist installiert und wird fuer DataviewJS-Syntaxchecks verwendet.
5. Obsidian-Rendering und Link-Klickverhalten bleiben manuelle Review-Signale.

Pflichtchecks fuer einen spaeteren Implementation-Slice:

1. `test -f _shared/SpecOps/Dashboards/project-index.md`
2. `test -f _shared/SpecOps/Dashboards/specops-backlog.md`
3. `rg -n '```dataviewjs' _shared/SpecOps/Dashboards/project-index.md`
4. `rg -n 'Spec Count|Active Specs|Backlog|Metadata Attention|Project Entity|Project Board' _shared/SpecOps/Dashboards/project-index.md`
5. `rg -n 'byProject|projectHeading|Project Group' _shared/SpecOps/Dashboards/specops-backlog.md`
6. `rg -n 'internal-link|href=' _shared/SpecOps/Dashboards/project-index.md _shared/SpecOps/Dashboards/specops-backlog.md`
7. `rg -n '^## Details' _shared/SpecOps/Dashboards/project-index.md _shared/SpecOps/Dashboards/specops-backlog.md`
8. `rg -n 'Dashboards/project-index' _shared/SpecOps/Dashboard.md`
9. DataviewJS syntax check:

```bash
node - <<'NODE'
const fs = require('fs');
const files = [
  '_shared/SpecOps/Dashboards/project-index.md',
  '_shared/SpecOps/Dashboards/specops-backlog.md',
];
let count = 0;
for (const file of files) {
  const text = fs.readFileSync(file, 'utf8');
  const blocks = [...text.matchAll(/```dataviewjs\n([\s\S]*?)\n```/g)];
  for (const [idx, block] of blocks.entries()) {
    count++;
    try {
      new Function('dv', block[1]);
    } catch (err) {
      console.error(`${file} block ${idx + 1}: ${err.message}`);
      process.exitCode = 1;
    }
  }
}
if (!process.exitCode) console.log(`Parsed ${count} dataviewjs blocks`);
NODE
```

Negative UX-Guard:

1. `rg -n '^TABLE status, metadata_quality, source' _shared/SpecOps/Dashboards/project-index.md`

Success Criteria:

1. Positive checks 1-9 geben Exit-Code `0` zurueck.
2. Der negative Project-Index-Table-Guard muss Exit-Code `1` liefern.
3. Manuelles Obsidian-Review bestaetigt, dass Project Index und Backlog ohne horizontales Scrollen scanbar bleiben.

## Implementation Readiness

Diese Spec ist bereit fuer einen anschliessenden Scope-Contract-/Delivery-Run, wenn:

1. keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker offen sind,
2. der Slice als Dashboard-only Change behandelt wird,
3. die Verification Commands als DoD-Basis akzeptiert werden.

Aktueller Stand: umgesetzt und mit den Pflichtchecks verifiziert. Obsidian-Rendering bleibt als manuelles Review-Signal offen.

## Implementation Evidence

Target runtime: lokaler DanielsVault unter `/Users/dh/Documents/DanielsVault`.

Execution mode: direct, ohne OpenSpec Change.

Pre-Implementation Analysis:

1. Formal marker check: keine blockierenden `[MISSING]`, `[DECISION]` oder `[BLOCKED]` Marker gefunden; Treffer waren nur Readiness-/Review-Formulierungen zu nicht vorhandenen Markern.
2. Codebase reality: `project-index.md` war noch eine einfache Dataview-Tabelle; `specops-backlog.md` hatte bereits klickbare Status-Lanes ohne Projektuntergruppen; `Dashboard.md` verlinkte `Dashboards/project-index` nicht mehr.
3. Umsetzbarkeit: Entity Notes liefern `title`, `project`, `status`, `metadata_quality`, `file.path` und reichen fuer Projektkarten, Counts und Drilldowns ohne Schema-Aenderung.
4. Logische Inkonsistenzen: keine blockierenden Widersprueche zwischen Spec-Anforderungen und existierenden Dashboards gefunden.
5. Runtime/build applicability: Keine NCG-Backend-Dateien, kein Docker-/Compose-Stack und kein Build-Artefakt in Scope; `check-build-watcher` ist fuer diesen Dashboard-only Slice nicht anwendbar.

Scope Contract:

1. In scope: Project Index DataviewJS-Karten mit Counts und Links, Backlog-Status-Lanes mit Projektgruppen, minimale Root-Link-Ergaenzung fuer `Dashboards/project-index`, Evidence in dieser Spec.
2. Out of scope: Entity-Schema, neue Entity Notes, Backfill, Skills, Agents, RAG-Runtime, NCG-Backend-Code, CSS und neue Pflicht-Plugins.
3. Acceptance targets: Requirements R1-R3 umgesetzt und durch Spec-Verification plus DataviewJS-Syntaxcheck belegt.

Changed files:

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/project-index.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/specops-backlog.md`
4. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Project Index and Backlog Grouping UX.md`

Runtime / watcher applicability:

1. Keine Runtime-Validierung mit `docker compose` erforderlich, weil dieser Slice ausschliesslich Markdown-/Dataview-Dashboard-Dateien aendert.
2. `check-build-watcher` ist nicht anwendbar, weil kein NCG-Backend-Code, keine Pipeline und kein Build-Artefakt in Scope sind.
3. Obsidian-/Dataview-Rendering und Link-Klickverhalten bleiben gemaess Spec manuelle Review-Signale.

| Check | Status | Evidence |
|-------|--------|----------|
| 1. Project Index exists | ran-target | `test -f _shared/SpecOps/Dashboards/project-index.md` returned exit code `0`. |
| 2. Backlog board exists | ran-target | `test -f _shared/SpecOps/Dashboards/specops-backlog.md` returned exit code `0`. |
| 3. Project Index has DataviewJS | ran-target | `rg -n '```dataviewjs' _shared/SpecOps/Dashboards/project-index.md` found the DataviewJS block. |
| 4. Project Index has required labels | ran-target | `rg -n 'Spec Count\|Active Specs\|Backlog\|Metadata Attention\|Project Entity\|Project Board' _shared/SpecOps/Dashboards/project-index.md` found expected card labels. |
| 5. Backlog has project grouping markers | ran-target | `rg -n 'byProject\|projectHeading\|Project Group' _shared/SpecOps/Dashboards/specops-backlog.md` found grouping logic. |
| 6. Project Index and Backlog have link markers | ran-target | `rg -n 'internal-link\|href=' _shared/SpecOps/Dashboards/project-index.md _shared/SpecOps/Dashboards/specops-backlog.md` found link markers. |
| 7. Details sections remain | ran-target | `rg -n '^## Details' _shared/SpecOps/Dashboards/project-index.md _shared/SpecOps/Dashboards/specops-backlog.md` found both detail sections. |
| 8. Root links Project Index | ran-target | `rg -n 'Dashboards/project-index' _shared/SpecOps/Dashboard.md` found the Board navigation link. |
| 9. DataviewJS syntax parses | ran-target | Node syntax check parsed 3 `dataviewjs` blocks from `project-index.md` and `specops-backlog.md`. |
| Negative Project Index table guard | ran-target | `rg -n '^TABLE status, metadata_quality, source' _shared/SpecOps/Dashboards/project-index.md` returned expected exit code `1`. |

Acceptance Coverage:

1. R1 covered: Project Index now renders DataviewJS project cards with status, quality, counts, Project Entity link and Project Board link where known.
2. R2 covered: Backlog Status Lanes remain and now group items by project with project headings and counts; cards remain clickable.
3. R3 covered: Root dashboard again links `Dashboards/project-index` and was not turned back into an embed page.

Verdict: READY for Obsidian review. Shell-verifiable acceptance criteria passed; final visual/link-click acceptance depends on opening the dashboards in Obsidian.

## Closeout Evidence

Closeout date: 2026-05-05.

Acceptance signal: User accepted the implemented SpecOps Project Index and Backlog Grouping UX change and requested spec closeout.

Verification replay:

| Check | Status | Evidence |
|-------|--------|----------|
| 1. Project Index exists | ran | `test -f _shared/SpecOps/Dashboards/project-index.md` returned exit code `0`. |
| 2. Backlog board exists | ran | `test -f _shared/SpecOps/Dashboards/specops-backlog.md` returned exit code `0`. |
| 3. Project Index has DataviewJS | ran | `rg -n '```dataviewjs' _shared/SpecOps/Dashboards/project-index.md` found the DataviewJS block. |
| 4. Project Index has required labels | ran | `rg -n 'Spec Count\|Active Specs\|Backlog\|Metadata Attention\|Project Entity\|Project Board' _shared/SpecOps/Dashboards/project-index.md` found expected card labels. |
| 5. Backlog has project grouping markers | ran | `rg -n 'byProject\|projectHeading\|Project Group' _shared/SpecOps/Dashboards/specops-backlog.md` found grouping logic. |
| 6. Project Index and Backlog have link markers | ran | `rg -n 'internal-link\|href=' _shared/SpecOps/Dashboards/project-index.md _shared/SpecOps/Dashboards/specops-backlog.md` found link markers. |
| 7. Details sections remain | ran | `rg -n '^## Details' _shared/SpecOps/Dashboards/project-index.md _shared/SpecOps/Dashboards/specops-backlog.md` found both detail sections. |
| 8. Root links Project Index | ran | `rg -n 'Dashboards/project-index' _shared/SpecOps/Dashboard.md` found the Board navigation link. |
| 9. DataviewJS syntax parses | ran | Node syntax check parsed 3 `dataviewjs` blocks from `project-index.md` and `specops-backlog.md`. |
| Negative Project Index table guard | ran | `rg -n '^TABLE status, metadata_quality, source' _shared/SpecOps/Dashboards/project-index.md` returned expected exit code `1`. |

OpenSpec closure status: not applicable. This change was implemented in direct mode without an OpenSpec change.

Documentation sync:

1. RAG-first discovery used `rag retrieve semantic --scope all --query "SpecOps Project Index Backlog Grouping UX project-index specops-backlog dashboard documentation status accepted" --top-k 7 --format json`.
2. Relevant RAG result: `spec-closeout/SKILL.md` confirmed mandatory verification replay and documentation sync. No project-specific documentation page was identified as requiring content updates.
3. Exact reference search found local SpecOps synchronization targets:
   - `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/specops-project-index-backlog-grouping-ux.md`
   - `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/specops-project-index-and-backlog-grouping-ux-2026-05-05.md`
   - `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`
4. NCG docs search returned no references to this SpecOps dashboard change, so no NCG project docs update was needed.

Closeout result:

1. Narrative spec status set to `🟢 Accepted`.
2. Backlog entity status set to `done`.
3. Spec entity status set to `accepted`.
4. Spec source inventory note updated from implemented to accepted.

Final closeout verdict: READY.

## Review

Autorenreview am 2026-05-05:

1. Scope ist klein und deckt genau die vorgeschlagenen UX-Follow-ups ab: Project Index aufwerten und Backlog projektweise gruppieren.
2. Keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker offen.
3. Verification Commands enthalten Existenzchecks, Strukturchecks, Linkchecks, DataviewJS-Syntaxcheck und einen negativen Guard gegen die alte Project-Index-Tabelle.
4. Keine Scope-Kollision mit den vorherigen Dashboard-Slices: Root wird nur auf Linkkompatibilitaet geprueft, nicht erneut umgebaut.
5. Ergebnis: keine offenen Review-Findings.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | Naechste UX-Verbesserung fuer Project Index und Backlog-Gruppierung als neue Spec freigegeben. |
| 2026-05-05 | Codex | Erste Spec fuer Project Index and Backlog Grouping UX erstellt und reviewt. |
| 2026-05-05 | Codex | Direct-Mode Scope Contract fixiert und Spec-Status auf Plan gesetzt. |
| 2026-05-05 | Codex | Project Index Cards und Backlog-Projektgruppierung umgesetzt, verifiziert und Spec-Status auf Implemented gesetzt. |
| 2026-05-05 | User | Implementierten SpecOps Project Index and Backlog Grouping UX Change akzeptiert. |
| 2026-05-05 | Codex | Closeout-Verification replayed, SpecOps Entities synchronisiert und Spec-Status auf Accepted gesetzt. |

SessionId: codex-desktop-current-thread
