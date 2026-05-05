**Date:** 2026-05-05
**Status:** 🔵 Implemented
**Scope:** SpecOps Dashboard UX Follow-up fuer klickbare Karten, schlankes Root-Cockpit und schaerfere Projektarbeitslisten

---

## Kontext

Der Slice `SpecOps Dashboard UX Overview` hat die SpecOps-Dashboards von breiten Dataview-Tabellen auf Snapshot-, Lane-, Triage- und Projektarbeitsansichten umgestellt. Das Global Spec Board ist nach Lifecycle-Status gruppiert und innerhalb der Swimlanes projektweise untergliedert.

Das anschliessende UX-Review hat vier konkrete Verbesserungsfelder identifiziert:

1. Karten zeigen gute Uebersicht, sind aber noch keine klickbaren Drilldowns.
2. Das Root-Dashboard embedded weiterhin zu viele Detailboards und kann dadurch wieder wie ein langer Bericht wirken.
3. Projektboards sortieren alle nicht accepted Specs in `Now`, wodurch `implemented` Specs faelschlich wie aktive Arbeit wirken.
4. Accepted Specs koennen im Global Spec Board langfristig die aktiven Lifecycle-Lanes dominieren.

Dieses Spec beschreibt einen kleinen Folge-Slice, der genau diese vier Findings adressiert, ohne Entity-Schema, Backfill oder Workflow-Verhalten zu veraendern.

## Ziel

SpecOps soll sich im Obsidian-Alltag mehr wie ein Cockpit anfuehlen:

1. Uebersichtskarten fuehren direkt zur passenden Entity, Quelle oder Projektarbeitsansicht.
2. Das Root-Dashboard bleibt kurz und handlungsorientiert.
3. Projektboards unterscheiden aktive Arbeit von Closeout-/Acceptance-Arbeit.
4. Accepted Specs bleiben auffindbar, dominieren aber nicht die globale Steuerungsansicht.

## In Scope

1. Klickbare Karten und Listen in:
   - `_shared/SpecOps/Dashboard.md`
   - `_shared/SpecOps/Dashboards/global-spec-board.md`
   - `_shared/SpecOps/Dashboards/specops-backlog.md`
   - `_shared/SpecOps/Dashboards/missing-metadata.md`
   - `_shared/SpecOps/Dashboards/projects/*.md`
2. Root-Dashboard von umfassenden Embeds auf ein kompaktes Cockpit mit Navigationskarten umstellen.
3. Projektboards von `Now / Next / Later` auf differenziertere Arbeitsgruppen schaerfen:
   - `Now`
   - `Closeout / Acceptance`
   - `Next`
   - `Later`
4. Global Spec Board so anpassen, dass aktive Lifecycle-Lanes sichtbar priorisiert bleiben und `accepted` als Archiv-/Traceability-Bereich weniger dominant wirkt.
5. Bestehende Detailtabellen als Fallback oder Detailbereich erhalten.

## Out of Scope

1. Keine Entity-Schema-Aenderung.
2. Keine neuen Pflichtfelder in Entity Notes.
3. Keine historische Backfill-Erweiterung.
4. Keine Aenderung an Skills, Agents, RAG-Runtime oder Fachcode.
5. Kein neues Obsidian-Plugin als harte Voraussetzung.
6. Keine CSS-Pflicht. Optional duerfen bestehende Inline-Styles weiter konsolidiert werden, wenn die Dashboards ohne CSS lesbar bleiben.

## Requirements

### R1 - Clickable Cards and Drilldowns

Dashboard-Karten muessen als Einstiege in die Arbeit funktionieren, nicht nur als statische Anzeige.

Akzeptanzkriterien:

1. Projektkarten im Root-Dashboard fuehren zur passenden Projektboard-Datei oder Project Entity.
2. Spec-Karten im Global Spec Board fuehren zur Spec Entity und, wenn sinnvoll verfuegbar, zur `source`.
3. Backlog-Karten fuehren zur Backlog Entity.
4. Metadata-Attention-Karten fuehren zur betroffenen Entity.
5. Wenn eine `source` fehlt oder kein Projektboard existiert, bleibt mindestens die Entity Note klickbar.

### R2 - Root Dashboard Cockpit

Das Root-Dashboard muss kurz bleiben und darf nicht erneut zur Textwand werden.

Akzeptanzkriterien:

1. Root enthaelt oben weiterhin `Snapshot`, `Needs Attention` und `Projects`.
2. Detailboards werden nicht mehr alle direkt embedded.
3. Stattdessen gibt es eine kompakte `## Boards`-Navigation mit Links/Karten zu:
   - Global Spec Board
   - Backlog
   - Missing Metadata
   - Documents
   - Coverage / Backfill
   - Projektboards
4. Root darf maximal zwei grosse Detail-Embeds enthalten; bevorzugt null.
5. Reference-Links bleiben erreichbar, aber unterhalb der Cockpit-Navigation.

### R3 - Project Work Buckets

Projektboards muessen aktive Arbeit von Abschluss-/Akzeptanzarbeit trennen.

Akzeptanzkriterien:

1. `Now` enthaelt nur Specs mit Status `spec`, `plan`, `blocked` oder unbekannten aktiven Sonderstatus.
2. `Closeout / Acceptance` enthaelt Specs mit Status `implemented`.
3. `Next` enthaelt Backlog-Items mit Status `triaged` oder `ready_for_spec`.
4. `Later` enthaelt Backlog-Items mit Status `proposed` oder `parked`.
5. `accepted` Specs erscheinen nicht in `Now`; sie bleiben in Details oder einem Archiv-/Traceability-Bereich sichtbar.

### R4 - Accepted Specs as Archive Lane

Das Global Spec Board muss aktive Arbeit priorisieren und accepted Specs als Traceability behandeln.

Akzeptanzkriterien:

1. Lifecycle-Lanes fuer `spec`, `plan`, `implemented` und `blocked` stehen vor `accepted`.
2. `accepted` wird als Archive-/Traceability-Bereich markiert.
3. Accepted Specs bleiben projektweise gruppiert und klickbar.
4. Die Detailtabelle bleibt vollstaendig, damit keine Traceability verloren geht.

## UX Model

Der erwartete Nutzerfluss ist:

1. Root-Dashboard oeffnen.
2. Snapshot und Needs Attention scannen.
3. Von Projektkarte, Backlog-Karte oder Global Spec Board direkt in die relevante Entity oder Projektarbeitsansicht springen.
4. Auf Projektboards aktive Arbeit (`Now`) und Abschlussarbeit (`Closeout / Acceptance`) getrennt bearbeiten.
5. Detailtabellen nur fuer Recherche, Audit und Traceability verwenden.

## Data and Implementation Constraints

1. Quelle der Wahrheit bleiben Entity Notes unter `_shared/SpecOps/Entities/`.
2. DataviewJS ist erlaubt.
3. Links sollen Obsidian-native Links nutzen, wo moeglich:
   - `dv.fileLink(...)`
   - `file.link`
   - bekannte Wiki-Links zu Dashboard-Dateien
4. Externe oder absolute `source`-Pfade duerfen nur als Text oder Link angezeigt werden, wenn Obsidian sie sinnvoll oeffnen kann.
5. Hauptansichten muessen ohne horizontales Scrollen nutzbar bleiben.

## Decision Freeze Pack

### Zielbild und Scope

Dieser Slice macht die bereits grafischeren SpecOps-Dashboards arbeitsfaehiger: Karten werden klickbar, das Root-Dashboard wird ein schlankes Cockpit, Projektboards trennen aktive Arbeit von Abschlussarbeit, und accepted Specs werden im Global Spec Board weniger dominant.

### Betroffene Vault-Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/specops-clickable-dashboard-navigation-cleanup.md`
5. Diese Spec unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/`

### Secret-/Config-Contract

Keine Secrets. Obsidian Dataview, DataviewJS und Mermaid bleiben lokale Anzeigevoraussetzungen.

### Datenmigration/Fallback

Keine Datenmigration. Bestehende Entity Notes und Detailtabellen bleiben erhalten.

### Externe Integrationen

Keine externen Integrationen.

### Sicherheits-/Exposure-Entscheidungen

Alle Daten bleiben lokal im DanielsVault.

### Abnahmekriterien Go/No-Go

Go:

1. Root-Dashboard hat Navigationskarten statt umfassender Detail-Embeds.
2. Karten in Root, Global Spec Board, Backlog und Missing Metadata bieten klickbare Drilldowns.
3. Projektboards enthalten `Closeout / Acceptance`.
4. `implemented` Specs erscheinen nicht mehr in `Now`.
5. Accepted Specs bleiben sichtbar, dominieren aber nicht die aktiven Global-Spec-Lanes.
6. Verification Commands laufen mit Exit-Code `0`, ausser explizit negative Guards.

No-Go:

1. Root-Dashboard wird erneut zur langen Embed-Seite.
2. Klickbare Karten ersetzen Traceability-Details.
3. Projektboards verstecken implemented oder accepted Specs vollstaendig.
4. Der Slice fuehrt Pflichtfelder oder Backfill-Arbeit ein.

### Owner fuer offene Risiken

1. User: Obsidian-Review, ob Links und Lesefluss praktisch funktionieren.
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

1. `test -f _shared/SpecOps/Dashboard.md`
2. `test -f _shared/SpecOps/Dashboards/global-spec-board.md`
3. `test -f _shared/SpecOps/Dashboards/specops-backlog.md`
4. `rg -n '^## Boards' _shared/SpecOps/Dashboard.md`
5. `rg -n 'Dashboards/global-spec-board|Dashboards/specops-backlog|Dashboards/missing-metadata|Dashboards/projects' _shared/SpecOps/Dashboard.md`
6. `rg -n 'dv\\.fileLink|file\\.link|internal-link|href=' _shared/SpecOps/Dashboard.md _shared/SpecOps/Dashboards/global-spec-board.md _shared/SpecOps/Dashboards/specops-backlog.md _shared/SpecOps/Dashboards/missing-metadata.md _shared/SpecOps/Dashboards/projects`
7. `rg -n 'Closeout / Acceptance' _shared/SpecOps/Dashboards/projects`
8. `rg -n '\\[\"Now\", specs\\.where\\(p => !\\[\"accepted\"\\]' _shared/SpecOps/Dashboards/projects`
9. `rg -n 'Archive|Traceability|accepted' _shared/SpecOps/Dashboards/global-spec-board.md`
10. DataviewJS syntax check:

```bash
node - <<'NODE'
const fs = require('fs');
const files = [
  '_shared/SpecOps/Dashboard.md',
  '_shared/SpecOps/Dashboards/global-spec-board.md',
  '_shared/SpecOps/Dashboards/specops-backlog.md',
  '_shared/SpecOps/Dashboards/missing-metadata.md',
  '_shared/SpecOps/Dashboards/projects/danielsvault-rag.md',
  '_shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md',
  '_shared/SpecOps/Dashboards/projects/ncg-checkbuild.md',
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

1. `rg -n '^!\\[\\[Dashboards/(portfolio-map|project-index|coverage|global-spec-board|documents|mixed-backfill|backfill-coverage|specops-backlog|missing-metadata|projects/)' _shared/SpecOps/Dashboard.md`

Success Criteria:

1. Positive checks 1-7, 9 und 10 geben Exit-Code `0` zurueck.
2. Check 8 ist ein negativer Guard und muss Exit-Code `1` liefern, weil die alte `Now = not accepted`-Logik nicht mehr existieren darf.
3. Der negative UX-Guard fuer Root-Embeds muss Exit-Code `1` liefern.
4. Manuelles Obsidian-Review bestaetigt, dass relevante Karten klickbar sind und Root nicht mehr als lange Embed-Seite wirkt.

## Implementation Readiness

Diese Spec ist bereit fuer einen anschliessenden Scope-Contract-/Delivery-Run, wenn:

1. keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker offen sind,
2. der Slice als Dashboard-only Change behandelt wird,
3. die Verification Commands als DoD-Basis akzeptiert werden.

Aktueller Stand: umgesetzt und mit den Pflichtchecks verifiziert. Obsidian-Link-Klickverhalten bleibt als manuelles Review-Signal offen.

## Implementation Evidence

Target runtime: lokaler DanielsVault unter `/Users/dh/Documents/DanielsVault`.

Execution mode: direct, ohne OpenSpec Change.

Pre-Implementation Analysis:

1. Formal marker check: keine blockierenden `[MISSING]`, `[DECISION]` oder `[BLOCKED]` Marker gefunden; Treffer im Precheck waren nur die nicht-blockierende Readiness-/Review-Formulierung zu nicht vorhandenen Markern.
2. Codebase reality: Betroffen sind ausschliesslich Markdown-Dashboard-Dateien mit Dataview/DataviewJS unter `_shared/SpecOps/`.
3. Umsetzbarkeit: Requirements passen zur bestehenden Struktur; Entity Notes enthalten `file.path`, `project`, `status`, `metadata_quality`, `source` und reichen fuer klickbare Drilldowns ohne Schema-Aenderung.
4. Logische Inkonsistenzen: keine blockierenden Widersprueche zwischen Requirements und aktuellen Dashboard-Dateien gefunden.
5. Runtime/build applicability: Keine NCG-Backend-Dateien, kein Docker-/Compose-Stack und kein Build-Artefakt in Scope; `check-build-watcher` ist fuer diesen Dashboard-only Slice nicht anwendbar.

Scope Contract:

1. In scope: klickbare Karten/Listen in Root, Global Spec Board, Backlog, Missing Metadata und Projektboards; Root-Navigation statt Detail-Embeds; `Closeout / Acceptance` in Projektboards; accepted Archive-/Traceability-Lane im Global Spec Board; Evidence in dieser Spec.
2. Out of scope: Entity-Schema, Backfill, Skills, Agents, RAG-Runtime, NCG-Backend-Code, neue Pflicht-Plugins und CSS-Pflicht.
3. Acceptance targets: alle Requirements R1-R4 umgesetzt und durch Spec-Verification plus DataviewJS-Syntaxcheck belegt.

Changed files:

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/global-spec-board.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/specops-backlog.md`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/missing-metadata.md`
5. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/danielsvault-rag.md`
6. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md`
7. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/ncg-checkbuild.md`
8. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Clickable Dashboard Navigation Cleanup.md`

Runtime / watcher applicability:

1. Keine Runtime-Validierung mit `docker compose` erforderlich, weil dieser Slice ausschliesslich Markdown-/Dataview-Dashboard-Dateien aendert.
2. `check-build-watcher` ist nicht anwendbar, weil kein NCG-Backend-Code, keine Pipeline und kein Build-Artefakt in Scope sind.
3. Obsidian-/Dataview-Rendering und Link-Klickverhalten bleiben gemaess Spec manuelle Review-Signale.

| Check | Status | Evidence |
|-------|--------|----------|
| 1. Dashboard exists | ran-target | `test -f _shared/SpecOps/Dashboard.md` returned exit code `0`. |
| 2. Global Spec Board exists | ran-target | `test -f _shared/SpecOps/Dashboards/global-spec-board.md` returned exit code `0`. |
| 3. Backlog board exists | ran-target | `test -f _shared/SpecOps/Dashboards/specops-backlog.md` returned exit code `0`. |
| 4. Root has Boards navigation | ran-target | `rg -n '^## Boards' _shared/SpecOps/Dashboard.md` found `## Boards`. |
| 5. Root links core boards and project boards | ran-target | `rg -n 'Dashboards/global-spec-board\|Dashboards/specops-backlog\|Dashboards/missing-metadata\|Dashboards/projects' _shared/SpecOps/Dashboard.md` found all expected navigation targets. |
| 6. Cards/lists expose clickable link markers | ran-target | `rg -n 'dv\\.fileLink\|file\\.link\|internal-link\|href=' ...` found `internal-link`, `href` or `file.link` markers in Root, Global, Backlog, Missing Metadata and project boards. |
| 7. Project boards contain Closeout / Acceptance | ran-target | `rg -n 'Closeout / Acceptance' _shared/SpecOps/Dashboards/projects` found all three project boards. |
| 8. Old Now equals not-accepted logic absent | ran-target | `rg -n '\\[\"Now\", specs\\.where\\(p => !\\[\"accepted\"\\]' _shared/SpecOps/Dashboards/projects` returned expected exit code `1`. |
| 9. Global Spec Board marks accepted archive/traceability | ran-target | `rg -n 'Archive\|Traceability\|accepted' _shared/SpecOps/Dashboards/global-spec-board.md` found the accepted Archive / Traceability lane label. |
| 10. DataviewJS syntax parses | ran-target | Node syntax check parsed 15 `dataviewjs` blocks from changed dashboard files. |
| Negative root embed guard | ran-target | `rg -n '^!\\[\\[Dashboards/(portfolio-map\|project-index\|coverage\|global-spec-board\|documents\|mixed-backfill\|backfill-coverage\|specops-backlog\|missing-metadata\|projects/)' _shared/SpecOps/Dashboard.md` returned expected exit code `1`. |

Acceptance Coverage:

1. R1 covered: cards/lists now create Obsidian-style `internal-link` anchors or preserve `file.link` detail fallback.
2. R2 covered: Root keeps Snapshot, Needs Attention and Projects, then uses `## Boards` navigation cards instead of embedding all downstream dashboards.
3. R3 covered: project boards now include `Now`, `Closeout / Acceptance`, `Next` and `Later`; `implemented` specs are no longer in the old `Now = not accepted` expression.
4. R4 covered: Global Spec Board orders active lanes before `accepted`, labels accepted as `Archive / Traceability`, keeps project grouping and retains Details.

Verdict: READY for Obsidian review. Shell-verifiable acceptance criteria passed; final visual/link-click acceptance depends on opening the dashboards in Obsidian.

## Review

Autorenreview am 2026-05-05:

1. Scope deckt die vier Review-Findings vollstaendig ab.
2. Keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker offen.
3. Verification Commands sind shell-/plattformbezogen und enthalten positive Checks, negative Guards und DataviewJS-Syntaxcheck.
4. Review-Fix angewendet: Node-Syntaxcheck als kopierbarer Shell-Block formuliert, Link-Check auf Projektboards erweitert und Root-Embed-Guard auf Projektboard-Embeds erweitert.
5. Ergebnis: keine offenen Review-Findings.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | UX-Review-Findings fuer klickbare Drilldowns, Root-Cleanup, Now-Bucket und Accepted-Lane als naechsten Spec-Slice freigegeben. |
| 2026-05-05 | Codex | Erste Spec fuer Clickable Dashboard Navigation Cleanup erstellt. |
| 2026-05-05 | Codex | Autorenreview durchgefuehrt und Verification-Guardrails fuer Linkchecks, Root-Embeds und DataviewJS-Syntax geschaerft. |
| 2026-05-05 | Codex | Direct-Mode Scope Contract fixiert und Spec-Status auf Plan gesetzt. |
| 2026-05-05 | Codex | Clickable Dashboard Navigation Cleanup umgesetzt, verifiziert und Spec-Status auf Implemented gesetzt. |

SessionId: codex-desktop-current-thread
