**Date:** 2026-05-05
**Status:** 🔵 Implemented
**Scope:** UX-Optimierung der SpecOps Boards und Dashboards fuer grafische, scanbare Uebersicht ohne horizontale Tabellenlast

---

## Kontext

Der SpecOps Control Plane MVP hat die lokale Grundlage fuer eine visuelle Spec-Steuerung im DanielsVault geschaffen. Der MVP setzt bewusst auf Markdown Entity Notes, Obsidian Dataview und Mermaid. Die aktuelle Dashboard-Expansion hat bereits Root-Dashboard, Global Spec Board, Projektboards, Backlog und Missing-Metadata-Sichten konsistenter erreichbar gemacht.

Die aktuelle User Experience bleibt trotzdem zu stark tabellarisch:

1. Die wichtigsten Steuerungsfragen sind in breiten Dataview-Tabellen versteckt.
2. Horizontale Scrollbalken entstehen durch zu viele Spalten pro View.
3. Projektboards zeigen Daten, aber noch keine klare "Was ist los und was mache ich als naechstes?"-Priorisierung.
4. Backlog-Items sind sichtbar, aber nicht als operative Naechste-Schritte-Ansicht gestaltet.
5. Grafische Signale existieren punktuell als Mermaid-Diagramme, helfen aber noch nicht bei der taeglichen Statusuebersicht.

Dieses Spec beschreibt einen UX-Slice, der die vorhandenen Datenquellen besser lesbar macht, ohne den Entity-Schema-MVP oder das langfristige Frontend-Ziel vorwegzunehmen.

## Gegencheck zum bestehenden MVP

Der UX-Slice ueberschneidet sich nicht mit dem bereits umgesetzten MVP-Scope:

1. Der Parent-MVP definiert Control-Plane-Konzept, Entity Notes, Statusachsen, Backlog-Prinzip und Dataview-/Mermaid-Basis.
2. Die Project Dashboard Expansion liefert konsistente Dashboard-Dateien und Mindestbereiche, aber keine eigentliche Lesefuehrung, keine Dashboard-Kacheln, keine Lane-Boards und keine verdichtete Next-Action-Ansicht.
3. Die bisherige Arbeit ist damit eine Daten-/Strukturgrundlage. Dieses Spec setzt darauf auf und betrifft Darstellung, Informationsarchitektur und Scanbarkeit.

Relevant source set:

1. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-04 SpecOps Control Plane MVP Obsidian Dataview Mermaid.md`
2. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Project Dashboard Expansion.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/global-spec-board.md`
5. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/specops-backlog.md`
6. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/`

RAG retrieval note: Eine semantische Suche ueber `--scope all` fand keine bessere SpecOps-spezifische UX-Quelle als die lokalen SpecOps-Dateien; generische private Dashboard-/Backlog-Notizen wurden nicht als normative Quellen verwendet.

## Ziel

SpecOps soll beim Oeffnen des Root-Dashboards oder eines Projektboards sofort als Uebersicht funktionieren:

1. Der Einstieg beantwortet in wenigen Blicken, wie viele Specs in welchem Status stehen.
2. Projektboards zeigen pro Projekt, was aktiv, blockiert, accepted, im Backlog und als naechster Schritt relevant ist.
3. Backlog-Ansichten fuehren zu Entscheidungen: parken, triagieren, ready for spec, promoted oder done.
4. Detailtabellen bleiben verfuegbar, stehen aber nicht mehr im Vordergrund.
5. Horizontale Scrollbalken werden in Hauptansichten vermieden.
6. Visuelle Elemente nutzen Obsidian-native Mittel: Callouts, Mermaid, Dataview/DataviewJS, kurze Listen und optional CSS-Klassen.

## UX-Prinzipien

1. **Overview first:** Jede Hauptseite startet mit einer knappen Status-Zusammenfassung, nicht mit einer breiten Tabelle.
2. **Decision-oriented:** Jede View soll eine operative Frage beantworten, z. B. "Was braucht eine Spec?", "Was ist als naechstes zu tun?", "Was ist blockiert?"
3. **Progressive detail:** Detailtabellen wandern in einklappbare Detailbereiche oder eigene Drilldown-Views.
4. **Narrow by default:** Hauptansichten zeigen maximal 3-4 Datenpunkte pro Item.
5. **Project as home base:** Projektboards sind Arbeitsoberflaechen, nicht nur gefilterte globale Tabellen.
6. **No schema churn:** Die erste UX-Iteration nutzt bestehende Entity Notes und berechnet Darstellung, statt neue Pflichtfelder einzufuehren.

## In Scope

1. UX-Konzept fuer Root-Dashboard, Global Spec Board, Projektboards, Backlog-Board und Missing-Metadata-Ansicht.
2. Definition von kompakten Status-Kacheln fuer Specs, Backlog, Projekte und Metadata Quality.
3. Definition von Lane-/Board-Ansichten fuer Spec Lifecycle und Backlog Status.
4. Definition von projektlokalen "Now / Next / Later"-Bereichen.
5. Definition, welche Tabellen in Hauptansichten ersetzt, verkleinert oder in Detailbereiche verschoben werden.
6. Definition von Obsidian-nativen Darstellungsbausteinen, die spaeter umgesetzt werden koennen.
7. Verifikationskriterien fuer Markdown-/Dataview-Struktur und Obsidian-Review.

## Out of Scope

1. Keine Aenderung am Entity-Schema als Pflichtmigration.
2. Keine vollstaendige historische Backfill-Arbeit.
3. Kein Backstage-, OpenProject-, Web-App- oder Jira-Frontend.
4. Keine automatische Dashboard-Generator-Engine.
5. Keine Aenderung an Skills, Agents, RAG-Runtime oder Fachcode.
6. Keine Obsidian-Plugin-Installation als harte Voraussetzung ausser Dataview und Mermaid; optionale Plugin-Empfehlungen sind erlaubt.
7. Keine endgueltige visuelle Design-System-Spezifikation fuer ein spaeteres Web-Frontend.

## Requirements

### R1 - Root Dashboard Snapshot

Das Root-Dashboard muss mit einem kompakten Snapshot starten, der die SpecOps-Lage auf einen Blick zeigt.

Akzeptanzkriterien:

1. Vor den eingebetteten Detailboards steht ein Bereich `## Snapshot`.
2. Der Snapshot zeigt mindestens:
   - Specs nach Lifecycle-Status.
   - Backlog-Items nach Status.
   - Projekte mit offenen oder aktiven Items.
   - Metadata-Quality-Warnungen.
3. Der Snapshot nutzt keine breite Tabelle mit mehr als vier Spalten.
4. Die Detailboards bleiben vom Root-Dashboard aus erreichbar.

### R2 - Spec Lifecycle Board

Das globale Spec Board muss eine scanbare Lifecycle-Ansicht erhalten.

Akzeptanzkriterien:

1. Specs werden in Lanes fuer `spec`, `plan`, `implemented`, `accepted` und relevante Sonderstatus gruppiert.
2. Jede Spec-Karte zeigt Titel, Projekt, Status und maximal einen weiteren Hinweis wie `metadata_quality`, `source` oder `next_action`.
3. Die bisherige breite Tabelle bleibt nur als Detail-/Appendix-View erhalten.
4. Die Ansicht kann in Obsidian Reading Mode gelesen werden, ohne horizontal zu scrollen.

### R3 - Project Board Working View

Jedes Projektboard muss als Arbeitsansicht funktionieren, nicht nur als gefilterte Tabelle.

Akzeptanzkriterien:

1. Jedes Projektboard startet mit einem Projekt-Snapshot.
2. Jedes Projektboard enthaelt einen Bereich `## Now / Next / Later`.
3. `Now` zeigt aktive, blockierte oder noch nicht accepted Specs.
4. `Next` zeigt Backlog-Items mit `triaged` oder `ready_for_spec`.
5. `Later` zeigt `proposed`, `parked` oder weniger dringende Backlog-Items.
6. Breite Tabellen werden unter `## Details` verschoben oder auf wenige Spalten reduziert.

### R4 - Backlog Triage Board

Das Backlog muss als Triage-Board lesbar sein.

Akzeptanzkriterien:

1. Backlog-Items werden nach Status-Lanes gruppiert: `proposed`, `triaged`, `ready_for_spec`, `promoted`, `done`, `parked`.
2. Jedes Item zeigt Titel, Projekt, Candidate Slice und Next Action.
3. Die View hebt `ready_for_spec` als eigentliche Naechste-Schritte-Liste hervor.
4. Promoted und Done bleiben sichtbar, dominieren aber nicht den oberen Bereich.

### R5 - Metadata Attention View

Missing Metadata muss als Pflegeaufgabenliste lesbar werden.

Akzeptanzkriterien:

1. Die View gruppiert Probleme nach `metadata_quality`.
2. Jedes Item zeigt Entity-Typ, Projekt, Titel und vermuteten Pflegebedarf.
3. Die Ansicht trennt `missing`, `inferred` und `conflict` sichtbar.
4. Detailquellen bleiben verlinkt.

### R6 - Visual Language

Die UX muss mit Obsidian-nativen Mitteln grafischer werden, ohne ein neues Frontend zu bauen.

Akzeptanzkriterien:

1. Mermaid wird fuer Beziehungs- oder Flow-Uebersichten genutzt, nicht fuer jede einzelne Liste.
2. Dataview oder DataviewJS erzeugt kompakte Listen/Karten statt breiter Haupttabellen.
3. Callouts markieren Statusgruppen, Warnungen und naechste Schritte.
4. Optional duerfen CSS-Klassen vorbereitet werden, aber die Views muessen auch ohne CSS lesbar bleiben.

## Proposed View Architecture

### Root Dashboard

1. `## Snapshot`
   - Spec lifecycle counts.
   - Backlog counts.
   - Metadata warnings.
   - Active project count.
2. `## Needs Attention`
   - Ready-for-spec backlog.
   - Conflicting or missing metadata.
   - Blocked or stale specs, sofern aus bestehenden Feldern ableitbar.
3. `## Projects`
   - Kompakte Projektliste mit Status und Drilldown-Link.
4. `## Boards`
   - Links oder Embeds zu Global Spec Board, Backlog, Missing Metadata und Detailboards.

### Global Spec Board

1. Lifecycle lanes als Hauptansicht.
2. Metadata warnings als kompakte Warnliste.
3. Detailtabelle in `## Details`.

### Project Boards

1. Projekt-Snapshot.
2. `Now / Next / Later`.
3. Specs und Backlog als kompakte Kartenlisten.
4. Artifacts/Evidence nur dort, wo Daten vorhanden sind.
5. Detailtabellen am Ende.

### Backlog Board

1. Ready-for-spec und triaged oben.
2. Status-Lanes darunter.
3. Done/promoted als Archiv-/Traceability-Bereich.

## Data and Implementation Constraints

1. Quelle der Wahrheit bleiben Entity Notes unter `_shared/SpecOps/Entities/`.
2. Der erste Slice darf keine Pflichtfelder einfuehren.
3. Wenn ein Feld fuer eine UX-Frage fehlt, wird die View defensiv formuliert oder der Pflegebedarf in Missing Metadata sichtbar gemacht.
4. DataviewJS ist fuer den MVP-UX-Slice erlaubt und soll fuer Karten-, Lane- und Snapshot-Views genutzt werden, wenn reine Dataview-Queries zu breiten Tabellen fuehren wuerden.
5. Jede Hauptansicht muss in plain Markdown verstaendlich bleiben, falls Dataview gerade nicht rendert.

## Optional Plugin Recommendations

Die erste Umsetzung darf optionale Obsidian-Plugins empfehlen, solange die Kern-UX mit Dataview, DataviewJS, Mermaid und Markdown lesbar bleibt.

Empfehlenswerte Kandidaten fuer Review nach dem ersten Slice:

1. **Style Settings** - erleichtert kontrollierte Anpassungen an CSS-Snippets, ohne Styles hart im Dashboard zu erklaeren.
2. **Minimal Theme Settings** oder ein vergleichbares Theme-Settings-Plugin - kann Kartenabstaende, Callout-Dichte und Lesbarkeit verbessern, bleibt aber optional.
3. **Iconize** - kann Projekt-, Status- und Board-Links visuell schneller erfassbar machen, darf aber nicht benoetigt werden, um Inhalte zu verstehen.
4. **Obsidian Charts** - nur pruefen, wenn DataviewJS-Counts als echte Diagramme gewuenscht sind; fuer den ersten UX-Slice reichen Snapshot-Kacheln.

## Decision Freeze Pack

### Zielbild und Scope

Dieser Slice optimiert die Lesbarkeit der bestehenden SpecOps-Dashboards. Er veraendert zuerst Darstellung, Informationsarchitektur und Obsidian-native Views. Datenmodell, Backfill-Strategie und langfristiges Frontend bleiben ausserhalb des Scopes.

### Betroffene Vault-Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/specops-dashboard-ux-overview.md`
5. Diese Spec unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/`

### Secret-/Config-Contract

Keine Secrets. Obsidian Dataview und Mermaid bleiben lokale Anzeigevoraussetzungen. DataviewJS darf verwendet werden, muss aber ohne externe Netzwerkzugriffe auskommen.

### Datenmigration/Fallback

Keine Datenmigration. Bestehende Detailtabellen bleiben als Fallback oder Appendix erhalten.

### Externe Integrationen

Keine externen Integrationen.

### Sicherheits-/Exposure-Entscheidungen

Alle Daten bleiben lokal im DanielsVault.

### Abnahmekriterien Go/No-Go

Go:

1. Root-Dashboard startet mit einem Snapshot.
2. Global Spec Board hat eine Lifecycle-Lane-Ansicht.
3. Backlog Board hat eine statusbasierte Triage-Ansicht.
4. Projektboards haben `Now / Next / Later`.
5. Hauptansichten vermeiden breite Tabellen und horizontale Scrollbalken.
6. Detailtabellen bleiben erreichbar.

No-Go:

1. UX-Slice besteht nur aus umbenannten Tabellen.
2. Hauptansichten erfordern horizontales Scrollen.
3. Neue Pflichtfelder werden ohne eigenes Schema-Spec eingefuehrt.
4. Grafische Darstellung ersetzt Quellenlinks oder Evidence-Traceability.

### Owner fuer offene Risiken

1. User: Obsidian-Review der Lesbarkeit und Priorisierung.
2. Codex: Markdown-/Dataview-/DataviewJS-Struktur und Verifikationschecks.

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Shell-/Plattformvertrag:

1. Zielplattform ist macOS.
2. Shell ist `zsh`.
3. `rg` ist installiert und wird fuer Textchecks verwendet.
4. Obsidian-Rendering bleibt ein manuelles Review-Signal.

Pflichtchecks fuer einen spaeteren Implementation-Slice:

1. `test -f _shared/SpecOps/Dashboard.md`
2. `test -f _shared/SpecOps/Dashboards/global-spec-board.md`
3. `test -f _shared/SpecOps/Dashboards/specops-backlog.md`
4. `rg -n '^## Snapshot' _shared/SpecOps/Dashboard.md`
5. `rg -n 'Lifecycle|Spec Lifecycle|status-lane|spec-lane' _shared/SpecOps/Dashboards/global-spec-board.md`
6. `rg -n 'Now / Next / Later|^## Now' _shared/SpecOps/Dashboards/projects`
7. `rg -n 'ready_for_spec|triaged|proposed|parked' _shared/SpecOps/Dashboards/specops-backlog.md`
8. `rg -n '^## Details|Detail' _shared/SpecOps/Dashboards/global-spec-board.md _shared/SpecOps/Dashboards/specops-backlog.md`
9. `rg -n 'TABLE .*project, status, lifecycle, metadata_quality, source, artifacts, evidence' _shared/SpecOps/Dashboards/global-spec-board.md`

Success Criteria:

1. Checks 1-8 geben Exit-Code `0` zurueck.
2. Check 9 ist ein negativer UX-Guard und muss Exit-Code `1` liefern, weil die alte breite Haupttabelle nicht unveraendert als primare Ansicht bestehen darf.
3. Manuelles Obsidian-Review bestaetigt, dass Root-, Global-, Backlog- und mindestens ein Projektboard ohne horizontales Scrollen lesbar sind.

## Implementation Readiness

Diese Spec ist bereit fuer einen anschliessenden Scope-Contract-/Delivery-Run.

Ready-Signale:

1. Der User hat die UX-Richtung bestaetigt.
2. DataviewJS ist fuer Karten-, Lane- und Snapshot-Views erlaubt.
3. Optionale Plugin-Empfehlungen sind erlaubt, aber keine harte Voraussetzung.
4. Es gibt keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker.
5. Der Scope bleibt auf UX, Informationsarchitektur und Dashboard-Darstellung begrenzt.

Aktueller Stand: umgesetzt und mit den Pflichtchecks verifiziert. Obsidian-Lesbarkeit bleibt als User-Review-Signal offen.

## Implementation Evidence

Target runtime: lokaler DanielsVault unter `/Users/dh/Documents/DanielsVault`.

Execution mode: direct, ohne OpenSpec Change.

Scope Contract:

1. In scope: bestehende SpecOps-Dashboard-Dateien, Dataview-/DataviewJS-Views, schmalere Detailbereiche, UX-Spec-Evidence.
2. Out of scope: Entity-Schema, Backfill, Skill-/Agent-Verhalten, RAG-Runtime, neue Pflicht-Plugins.
3. Acceptance targets: Root-Snapshot, Global-Spec-Lifecycle-Lanes, Backlog-Triage-Lanes, Project `Now / Next / Later`, Metadata-Attention-Lanes, keine alte breite Global-Spec-Haupttabelle.

Changed files:

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/global-spec-board.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/specops-backlog.md`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/missing-metadata.md`
5. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/danielsvault-rag.md`
6. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md`
7. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/ncg-checkbuild.md`
8. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Dashboard UX Overview.md`

Runtime / watcher applicability:

1. Keine Runtime-Validierung mit `docker compose` erforderlich, weil dieser Slice ausschliesslich Markdown-/Dataview-Dashboard-Dateien aendert.
2. `check-build-watcher` ist nicht anwendbar, weil kein NCG-Backend-Code, keine Pipeline und kein Build-Artefakt in Scope sind.
3. Obsidian-/Dataview-Renderpruefung bleibt ein manuelles Review-Signal.

| Check | Status | Evidence |
|-------|--------|----------|
| 1. Dashboard exists | ran-target | `test -f _shared/SpecOps/Dashboard.md` returned exit code `0`. |
| 2. Global Spec Board exists | ran-target | `test -f _shared/SpecOps/Dashboards/global-spec-board.md` returned exit code `0`. |
| 3. Backlog board exists | ran-target | `test -f _shared/SpecOps/Dashboards/specops-backlog.md` returned exit code `0`. |
| 4. Root dashboard has Snapshot | ran-target | `rg -n '^## Snapshot' _shared/SpecOps/Dashboard.md` found the section. |
| 5. Global board has lifecycle/lane markers | ran-target | `rg -n 'Lifecycle\|Spec Lifecycle\|status-lane\|spec-lane' _shared/SpecOps/Dashboards/global-spec-board.md` found the expected markers. |
| 6. Project boards have Now / Next / Later | ran-target | `rg -n 'Now / Next / Later\|^## Now' _shared/SpecOps/Dashboards/projects` found all three project boards. |
| 7. Backlog board has triage statuses | ran-target | `rg -n 'ready_for_spec\|triaged\|proposed\|parked' _shared/SpecOps/Dashboards/specops-backlog.md` found the lane/status logic. |
| 8. Global and Backlog boards have Details | ran-target | `rg -n '^## Details\|Detail' _shared/SpecOps/Dashboards/global-spec-board.md _shared/SpecOps/Dashboards/specops-backlog.md` found both detail sections. |
| 9. Old broad Global Spec table absent | ran-target | `rg -n 'TABLE .*project, status, lifecycle, metadata_quality, source, artifacts, evidence' _shared/SpecOps/Dashboards/global-spec-board.md` returned expected exit code `1`. |
| 10. DataviewJS syntax parses | ran-target | Node syntax check parsed 14 `dataviewjs` blocks from changed dashboard files. |

Verdict: READY for Obsidian review. Shell-verifiable acceptance criteria passed; final visual acceptance depends on opening the dashboards in Obsidian.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | Bedarf fuer grafischere und besser scanbare SpecOps Boards/Dashboards beschrieben. |
| 2026-05-05 | Codex | Erste UX-Spec fuer SpecOps Dashboard Overview erstellt. |
| 2026-05-05 | User | DataviewJS und optionale Plugin-Empfehlungen fuer die UX-Umsetzung freigegeben. |
| 2026-05-05 | Codex | DataviewJS-Entscheidung aufgeloest und Spec als implementation-ready markiert. |
| 2026-05-05 | Codex | Direct-Mode Scope Contract fuer dashboard-only DataviewJS-Umsetzung fixiert und Spec-Status auf Plan gesetzt. |
| 2026-05-05 | Codex | Dashboard UX mit Snapshot-, Lane-, Triage- und Projektarbeitsansichten umgesetzt, verifiziert und Spec-Status auf Implemented gesetzt. |

SessionId: codex-desktop-current-thread
