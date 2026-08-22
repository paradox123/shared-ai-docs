# 07: Den vollstaendigen probare-crm-Backlog sicher disponieren

**What to build:** Der Pilot waehlt aus allen geeigneten `probare-crm`-Issues nur fachlich autorisierte und unblocked Arbeit aus, serialisiert die Implementierung pro Repository und gibt Nachfolger erst nach abgeschlossenem Blocker frei.

**Blocked by:** 01: Ein autorisiertes Issue lokal annehmen und claimen

**Covers:** US 1-12, 70

**Status:** resolved

- [x] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [x] Die zentrale Control Plane und ihre Repository-unabhaengigen Regeln liegen in `shared-ai-docs`; Labels, erlaubte Events, Herkunfts- und Blocking-Beziehungen sowie GitHub-Projektionen werden hinter einem versionierten `RepositoryAdapter` gekapselt.
- [x] `probare-crm` wird als erster Adapter beziehungsweise erste Konfiguration angebunden; der Workflow-Kern enthaelt keine `probare-crm`-spezifischen Verzweigungen.
- [x] Ein Contract-Test bindet neben `probare-crm` einen minimalen zweiten Fake-Repository-Adapter an, ohne den Workflow-Kern zu aendern oder ein weiteres Live-Repository zu aktivieren.
- [x] Alle Issue-Typen koennen den Piloten durchlaufen; es gibt keine pauschale Risikoklasse, die einen Typ ausschliesst.
- [x] `ready-for-agent` ist zugleich Reifezustand und Implementierungsfreigabe; ein zweites Startsignal oder ein zusaetzlicher Arbeitsmandat-Pflichtabschnitt wird nicht verlangt.
- [x] Der Agent darf `ready-for-agent` selbst setzen, wenn die Herkunft aus einem von Daniel eroeffneten Issue, einer verlinkten PRD oder einer nachvollziehbaren Parent-/Child-Kette belegt ist.
- [x] Abgeleitete Issues duerfen geerbten Scope schneiden und praezisieren, aber nicht materiell erweitern; eine nicht belegbare Erweiterung wird als Produktentscheidung unterbrochen.
- [x] Pro Repository ist hoechstens ein Implementierungslauf aktiv, und der Pilot erzeugt keine gestapelten Pull Requests.
- [x] Offene `Blocked by`-Beziehungen verhindern den Claim; ein Nachfolger wird erst nach menschlichem Merge des Blocker-PRs und Abschluss des Blocker-Issues freigegeben.
- [x] Gleichzeitig freigegebene Issues werden deterministisch als Frontier disponiert, ohne dass Events verloren gehen oder ein zweiter Worktree startet.
- [x] Verhaltenstests decken Selbstautorisierung, ungueltige Herkunft, offene und erledigte Blocker sowie zwei gleichzeitig freigegebene Issues desselben Repositories ab.

## Implementation Evidence

Accepted and archived through OpenSpec change `dispose-authorized-repository-backlog`. The criterion-by-criterion evidence is recorded in `openspec/changes/archive/2026-08-22-dispose-authorized-repository-backlog/implementation-evidence.md`.
