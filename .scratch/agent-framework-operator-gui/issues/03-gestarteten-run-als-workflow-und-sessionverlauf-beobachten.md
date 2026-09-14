# 03: Selbst gestarteten Run als Workflow und Sessionverlauf beobachten

**What to build:** Ein Mensch öffnet seinen über die GUI gestarteten Run von einem berechtigten Client und verfolgt die tatsächlichen Aktivitäten sowie die vollständigen gespeicherten Sessiondetails in einer schmalen Workflow-Ansicht.

**Blocked by:** 02: Eingereichtes Issue als erste Hintergrundaktivität starten.

**Status:** resolved

- [x] Die Run-Liste und Workflow-Ansicht verwenden die über den Eingabe-/Startweg erzeugten Runs. Kein Benutzer muss einen Run vorab in die Datenbank schreiben oder ein Fixture laden.
- [x] Der erste Graph zeigt gestartete Aktivitäten, Versuche, Sessions und deren beobachteten Zustand; die Auswahl öffnet zugeordnete Benutzer-/Agentennachrichten, Aufträge/Kontext, Toolparameter/-ergebnisse mit Dauer/Fehlern, Erkenntnisse und Artefakte.
- [x] Live-Ereignisse und paginiertes Nachladen folgen bestätigten Positionen und stabilen Identitäten. Browser-/API-Neustart erhält Zuordnung und Reihenfolge ohne doppelte Anzeige; fehlende oder redigierte Inhalte bleiben explizit.
- [x] Ein anderer authentifizierter Browserclient kann denselben berechtigten Run ohne Zugriff auf den ursprünglichen Rechner untersuchen. Rechteentzug verhindert weiteren unberechtigten Zugriff; sensible Daten werden nicht durch Filterwechsel oder Artefaktlinks zugänglich.
- [x] Die Abnahme beginnt mit Eingabe und Start eines echten kontrollierten Issues und verfolgt denselben Run über zwei Clients bis zum Ergebnis oder konkreten Fehler. Browserprüfung und Vergleich mit öffentlichen History-/Artifact-Antworten beweisen den fachlichen Inhalt; die vollständige verschachtelte PRD-Graphnavigation folgt später.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.

### 2026-09-14 — Implementierung und direkte lokale Verifikation

Implementiert auf `codex/operator-gui-issue-03` aus `dded7d4` innerhalb des aktiven
OpenSpec-Changes `add-agent-framework-operator-gui`. Die bestehende GUI verbindet
gestartete Anforderungen mit der Run-Liste, dem beobachteten Aktivitäts-/Versuchs-/
Sessiongraphen und vollständigen gespeicherten History-/Artefaktinhalten.

Der reale Nachweis startet `paradox123/probare-crm#4` über die GUI und vergleicht
zwei authentifizierte Browserkontexte mit den öffentlichen History- und
Artifact-Antworten. Nach API-Neustart bleiben Run, Session und Inhalt identisch.
Fünf kontrollierte Browserprüfungen belegen Pagination, Live-Wiederaufnahme,
Rechteentzug ohne Filterrückweg, explizit fehlende Artefakte sowie Wiederholung
eines fehlgeschlagenen Graph-Updates ohne spätere Ereignisse. Nachrichtentext
kann keine Stream-Steuerung auslösen.

Gesamtregression: 223 Tests, 198 bestanden, 25 optionale Prüfungen übersprungen;
der währenddessen ergänzte Race-Test ist separat grün. Der echte GitHub-/Codex-
Test wurde separat aktiviert und bestanden. Standards-Review: 0 offene Befunde;
Spec-Review: 0 offene Befunde. Build und strikte OpenSpec-Validierung sind grün.

[Abnahmeübersicht und Belege](../../../openspec/changes/add-agent-framework-operator-gui/issue-03-evidence.md)
und [getrennte Reviewberichte](../../../openspec/changes/add-agent-framework-operator-gui/issue-03-review.md)
dokumentieren auch Korrekturen und Grenzen. `resolved` bezeichnet Implementierung
und lokale Verifikation; eine Nutzerabnahme oder Archivierung ist nicht vorweggenommen.
Die physische Mehrrechner-Abnahme bleibt Ticket 16, der vollständige PRD-Graph
Ticket 15. Der bestehende Portalstil wird verwendet; die Prototyp-Runtime wurde
für diese begrenzte Ansicht nicht übernommen.
