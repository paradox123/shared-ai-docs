**Date:** 2026-05-05
**Status:** 🟡 Spec
**Scope:** SpecOps Portfolio Views Slice fuer konsistente Portfolio-, Global-Spec- und projektlokale Dashboard-Sichten auf Basis bestehender Entity Notes

---

## Kontext

Der Parent-SpecOps-MVP und die ersten beiden Child-Slices haben die lokale Control Plane unter `_shared/SpecOps/` aufgebaut:

1. Der RAG Project Board Pilot hat Entity Notes, Reference-Dateien, Root-Dashboard, Backlog-View und Missing-Metadata-View angelegt.
2. Der Mixed Backfill Pilot hat reale Specs fuer Nebenkostenabrechnung und NCG / CheckBuild erfasst und erste projektlokale Boards ergaenzt.
3. Das Backlog-Item `project-dashboard-expansion` stand vor Erstellung dieser Child-Spec auf `ready_for_spec` und fordert den Schritt von einzelnen Pilot-Boards zu Portfolio- und Projekt-Views mit sichtbaren Status-, Artefakt- und Backlog-Beziehungen.

Dieser Slice ist kein neues Feature-Buendel und keine UX-Neuerfindung. Er promoted ausschliesslich das bestehende Backlog-Item `project-dashboard-expansion` mit `candidate_slice: SpecOps Portfolio Views`.

## Ziel

SpecOps soll nach diesem Slice besser als lokale Control Plane lesbar sein:

1. Der Einstieg zeigt Projektlage, Spec-Lage und offene Pflegepunkte ohne manuelle Suche durch Entity-Ordner.
2. Projektboards nutzen eine einheitliche Mindeststruktur.
3. Ein globales Spec Board beantwortet projektuebergreifend, welche Specs in welchem Status stehen.
4. Backlog-, Missing-Metadata- und Coverage-Sichten bleiben sichtbar und werden nicht durch Projektboards ersetzt.
5. Neue Folgeideen werden nur sichtbar als Backlog weitergefuehrt, nicht als spontane Slice-Namen.

## In Scope

1. Bestehendes Root-Dashboard `_shared/SpecOps/Dashboard.md` so strukturieren, dass Portfolio, Global Spec Board, Projektboards, Backlog und Missing Metadata klar auffindbar sind.
2. Neues oder aktualisiertes Dashboard fuer ein projektuebergreifendes Global Spec Board unter `_shared/SpecOps/Dashboards/`.
3. Konsistente Mindeststruktur fuer diese bestehenden Projektboards:
   - `_shared/SpecOps/Dashboards/projects/danielsvault-rag.md`
   - `_shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md`
   - `_shared/SpecOps/Dashboards/projects/ncg-checkbuild.md`
4. Projektboards zeigen mindestens:
   - Specs
   - Related Artifacts, sofern fuer das Projekt vorhanden
   - Backlog Items
   - Missing oder rekonstruierte Metadaten fuer das Projekt
5. Portfolio-/Project-Index-Sichten bleiben Dataview-basiert und verwenden die bestehenden Entity Notes.
6. Das Backlog-Item `project-dashboard-expansion` wird mit dieser Child-Spec verknuepft.

## Out of Scope

1. Kein Full Historical Spec Backfill.
2. Keine neuen fachlichen Spec-Entities ausser zur Reparatur klarer Dashboard-Metadatenfehler.
3. Keine Release-Entity-Notes.
4. Keine Environment-Tracking-Semantik ueber vorhandene Felder hinaus.
5. Keine Document-/ADR-Entity-Implementierung.
6. Keine automatische Dashboard-Generierung oder Template-Engine.
7. Keine Aenderung an Skills, Agents, RAG-Tools oder Fachcode.
8. Keine neuen, nicht aus Backlog-Feldern abgeleiteten Slice-Namen.

## Requirements

### R1 - Dashboard Entry Point

`_shared/SpecOps/Dashboard.md` muss einen klaren Einstieg in Portfolio, Projektindex, Global Spec Board, Projektboards, Backlog und Missing Metadata bieten.

Akzeptanzkriterien:

1. Das Root-Dashboard verlinkt oder embedded die relevanten Dashboard-Dateien.
2. Global Spec Board und Projektboards sind vom Root-Dashboard aus erreichbar.
3. Backlog und Missing Metadata bleiben eigene sichtbare Bereiche.

### R2 - Global Spec Board

Ein globales Spec Board muss projektuebergreifend Specs nach Projekt, Status, Lifecycle, Metadata Quality, Source, Artifacts und Evidence sichtbar machen.

Akzeptanzkriterien:

1. Eine Dashboard-Datei unter `_shared/SpecOps/Dashboards/` enthaelt eine Dataview-Query fuer alle `type: spec` Entities.
2. Die Query zeigt mindestens `project`, `status`, `lifecycle`, `metadata_quality`, `source`, `artifacts` und `evidence`.
3. Die Sortierung macht Status- und Projektlage scanbar.

### R3 - Consistent Project Boards

Die bestehenden Projektboards fuer DanielsVault RAG, Nebenkostenabrechnung und NCG / CheckBuild muessen eine einheitliche Mindeststruktur haben.

Akzeptanzkriterien:

1. Jedes Projektboard hat einen `Specs`-Abschnitt.
2. Jedes Projektboard hat einen `Backlog`-Abschnitt.
3. Jedes Projektboard hat einen `Metadata Quality`- oder `Missing Metadata`-Abschnitt.
4. Artifact-Sichten werden nur dort angezeigt, wo sie ueber bestehende Entity Notes sinnvoll sind.
5. Die Boards nutzen Dataview-Queries statt handgeschriebener Statuslisten.

### R4 - Backlog Discipline

Der Slice darf keine neue Idee direkt implementieren, wenn sie nicht ueber ein Backlog-Item oder diese Spec gedeckt ist.

Akzeptanzkriterien:

1. `project-dashboard-expansion` ist mit dieser Spec verlinkt.
2. Neue Out-of-Scope-Funde werden als Backlog-Items erfasst oder explizit im Implementation Evidence als nicht umgesetzt benannt.
3. Neue Slice-Bezeichnungen werden nur aus bestehenden Backlog-Feldern abgeleitet oder vor Umsetzung als neues Backlog-Item angelegt.

## Decision Freeze Pack

### Zielbild und Scope

Dieser Slice erweitert die vorhandenen SpecOps-Dashboards zu einer konsistenteren Portfolio- und Projektansicht. Er veraendert nur Markdown-Dashboard-Dateien und das zugehoerige SpecOps-Backlog-Metadatum fuer `project-dashboard-expansion`.

### Betroffene Vault-Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/projects/`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/project-dashboard-expansion.md`
5. Diese Child-Spec unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/`

### Secret-/Config-Contract

Keine Secrets. Dataview bleibt die lokale Anzeigevoraussetzung.

### Datenmigration/Fallback

Keine Datenmigration. Bestehende Entity Notes bleiben Quelle der Wahrheit. Falls ein Projekt keine passenden Entity Notes hat, wird es nicht kuenstlich mit Platzhalterdaten aufgefuellt.

### Externe Integrationen

Keine externen Integrationen. Kein OpenProject, Backstage oder GitHub Projects.

### Sicherheits-/Exposure-Entscheidungen

Alle Daten bleiben lokal im DanielsVault.

### Abnahmekriterien Go/No-Go

Go:

1. Root-Dashboard referenziert das Global Spec Board.
2. Global Spec Board existiert und enthaelt eine Dataview-Query ueber alle Spec-Entities.
3. Die drei bestehenden Projektboards enthalten `Specs`, `Backlog` und Metadata-Quality/Missing-Metadata-Sichten.
4. Backlog-Item `project-dashboard-expansion` ist mit dieser Spec verlinkt.
5. Keine neue nicht gedeckte Slice-Bezeichnung wurde eingefuehrt.
6. Verification Commands laufen mit Exit-Code `0`.

No-Go:

1. Dashboard-Erweiterung besteht nur aus Prosa ohne Dataview-Sichten.
2. Projektboards haben unterschiedliche Mindestlogik ohne erkennbaren Grund.
3. Neue Scope-Ideen werden direkt umgesetzt statt als Backlog sichtbar gemacht.
4. Der Slice veraendert Entity-Schema, Release-Modell, Environment-Modell oder Skill-Verhalten.

### Owner fuer offene Risiken

1. User: Obsidian-Review, ob die Views praktisch lesbar sind.
2. Codex: Markdown-/Dataview-Struktur, Backlog-Verknuepfung und Shell-Verifikation.

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Shell-/Plattformvertrag:

1. Zielplattform ist macOS.
2. Shell ist `zsh`.
3. `rg` ist installiert und wird fuer Textchecks verwendet.
4. Negative Scope-Guard-Checks werden ohne Shell-Negation formuliert: der angegebene `rg`-Befehl muss Exit-Code `1` liefern, weil kein Treffer erlaubt ist.

Pflichtchecks:

1. `test -f _shared/SpecOps/Dashboard.md`
2. `test -f _shared/SpecOps/Dashboards/global-spec-board.md`
3. `test -f _shared/SpecOps/Dashboards/projects/danielsvault-rag.md`
4. `test -f _shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md`
5. `test -f _shared/SpecOps/Dashboards/projects/ncg-checkbuild.md`
6. `rg -n 'Dashboards/global-spec-board|Global Spec Board|Backlog|Missing Metadata' _shared/SpecOps/Dashboard.md`
7. `rg -n 'FROM "_shared/SpecOps/Entities/specs"' _shared/SpecOps/Dashboards/global-spec-board.md`
8. `rg -n 'WHERE type = "spec"' _shared/SpecOps/Dashboards/global-spec-board.md`
9. `rg -n 'TABLE .*project' _shared/SpecOps/Dashboards/global-spec-board.md`
10. `rg -n 'TABLE .*status' _shared/SpecOps/Dashboards/global-spec-board.md`
11. `rg -n 'TABLE .*lifecycle' _shared/SpecOps/Dashboards/global-spec-board.md`
12. `rg -n 'TABLE .*metadata_quality' _shared/SpecOps/Dashboards/global-spec-board.md`
13. `rg -n 'TABLE .*source' _shared/SpecOps/Dashboards/global-spec-board.md`
14. `rg -n 'TABLE .*artifacts' _shared/SpecOps/Dashboards/global-spec-board.md`
15. `rg -n 'TABLE .*evidence' _shared/SpecOps/Dashboards/global-spec-board.md`
16. `rg -n '^## Specs' _shared/SpecOps/Dashboards/projects/danielsvault-rag.md`
17. `rg -n '^## Backlog' _shared/SpecOps/Dashboards/projects/danielsvault-rag.md`
18. `rg -n 'Metadata Quality|Missing Metadata' _shared/SpecOps/Dashboards/projects/danielsvault-rag.md`
19. `rg -n '^## Specs' _shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md`
20. `rg -n '^## Backlog' _shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md`
21. `rg -n 'Metadata Quality|Missing Metadata' _shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md`
22. `rg -n '^## Specs' _shared/SpecOps/Dashboards/projects/ncg-checkbuild.md`
23. `rg -n '^## Backlog' _shared/SpecOps/Dashboards/projects/ncg-checkbuild.md`
24. `rg -n 'Metadata Quality|Missing Metadata' _shared/SpecOps/Dashboards/projects/ncg-checkbuild.md`
25. `rg -n 'status: promoted' _shared/SpecOps/Entities/backlog/project-dashboard-expansion.md`
26. `rg -n 'promoted_to: .+2026-05-05 SpecOps Project Dashboard Expansion.md' _shared/SpecOps/Entities/backlog/project-dashboard-expansion.md`
27. `rg -n 'title: Visual Board UX Pilot|candidate_slice: Visual Board UX Pilot' _shared/SpecOps/Entities/backlog`

Success Criteria:

1. Alle positiven Checks geben Exit-Code `0` zurueck.
2. Check 27 ist der negative Scope-Guard-Check und muss Exit-Code `1` liefern.
3. Obsidian-/Dataview-Renderpruefung bleibt ein manuelles Review-Signal und wird nach Umsetzung im Evidence-Abschnitt dokumentiert.

## Backlog Handling

1. Vor Erstellung dieser Child-Spec stand `project-dashboard-expansion` auf `ready_for_spec`.
2. Nach Erstellung dieser Child-Spec steht `project-dashboard-expansion` auf `promoted` und verweist mit `promoted_to` auf diese Datei.
3. Nach Umsetzung und erfolgreicher Verifikation darf das Backlog-Item auf `done` gesetzt werden.
4. Out-of-scope-Funde bleiben als Backlog sichtbar.

## Implementation Readiness

Diese Spec ist bereit fuer einen anschliessenden Scope-Contract-/Delivery-Run, wenn:

1. die Backlog-Verknuepfung auf diese Spec gesetzt ist,
2. keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker offen sind,
3. die Verification Commands vor Umsetzung unveraendert als DoD-Basis akzeptiert werden.

Aktueller Stand: bereit fuer Planung/Delivery, aber noch nicht implementiert.

## Implementation Evidence

Noch nicht umgesetzt.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | Erstellung der Child-Spec fuer den naechsten SpecOps-Slice freigegeben. |
| 2026-05-05 | Codex | Child-Spec fuer `project-dashboard-expansion` / `SpecOps Portfolio Views` erstellt. |
| 2026-05-05 | Codex | Review-Findings zu Verification-Strength und Shell-/Plattformvertrag autonom behoben. |

SessionId: codex-desktop-current-thread
