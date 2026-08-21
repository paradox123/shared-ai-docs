# 07: Den vollstaendigen probare-crm-Backlog sicher disponieren

**What to build:** Der Pilot waehlt aus allen geeigneten `probare-crm`-Issues nur fachlich autorisierte und unblocked Arbeit aus, serialisiert die Implementierung pro Repository und gibt Nachfolger erst nach abgeschlossenem Blocker frei.

**Blocked by:** 01: Ein autorisiertes Issue lokal annehmen und claimen

**Covers:** US 1-12, 70

**Status:** ready-for-agent

- [ ] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [ ] Die zentrale Control Plane und ihre Repository-unabhaengigen Regeln liegen in `shared-ai-docs`; Labels, erlaubte Events, Herkunfts- und Blocking-Beziehungen sowie GitHub-Projektionen werden hinter einem versionierten `RepositoryAdapter` gekapselt.
- [ ] `probare-crm` wird als erster Adapter beziehungsweise erste Konfiguration angebunden; der Workflow-Kern enthaelt keine `probare-crm`-spezifischen Verzweigungen.
- [ ] Ein Contract-Test bindet neben `probare-crm` einen minimalen zweiten Fake-Repository-Adapter an, ohne den Workflow-Kern zu aendern oder ein weiteres Live-Repository zu aktivieren.
- [ ] Alle Issue-Typen koennen den Piloten durchlaufen; es gibt keine pauschale Risikoklasse, die einen Typ ausschliesst.
- [ ] `ready-for-agent` ist zugleich Reifezustand und Implementierungsfreigabe; ein zweites Startsignal oder ein zusaetzlicher Arbeitsmandat-Pflichtabschnitt wird nicht verlangt.
- [ ] Der Agent darf `ready-for-agent` selbst setzen, wenn die Herkunft aus einem von Daniel eroeffneten Issue, einer verlinkten PRD oder einer nachvollziehbaren Parent-/Child-Kette belegt ist.
- [ ] Abgeleitete Issues duerfen geerbten Scope schneiden und praezisieren, aber nicht materiell erweitern; eine nicht belegbare Erweiterung wird als Produktentscheidung unterbrochen.
- [ ] Pro Repository ist hoechstens ein Implementierungslauf aktiv, und der Pilot erzeugt keine gestapelten Pull Requests.
- [ ] Offene `Blocked by`-Beziehungen verhindern den Claim; ein Nachfolger wird erst nach menschlichem Merge des Blocker-PRs und Abschluss des Blocker-Issues freigegeben.
- [ ] Gleichzeitig freigegebene Issues werden deterministisch als Frontier disponiert, ohne dass Events verloren gehen oder ein zweiter Worktree startet.
- [ ] Verhaltenstests decken Selbstautorisierung, ungueltige Herkunft, offene und erledigte Blocker sowie zwei gleichzeitig freigegebene Issues desselben Repositories ab.
