# 03: Selbst gestarteten Run als Workflow und Sessionverlauf beobachten

**What to build:** Ein Mensch öffnet seinen über die GUI gestarteten Run von einem berechtigten Client und verfolgt die tatsächlichen Aktivitäten sowie die vollständigen gespeicherten Sessiondetails in einer schmalen Workflow-Ansicht.

**Blocked by:** 02: Eingereichtes Issue als erste Hintergrundaktivität starten.

**Status:** ready-for-agent

- [ ] Die Run-Liste und Workflow-Ansicht verwenden die über den Eingabe-/Startweg erzeugten Runs. Kein Benutzer muss einen Run vorab in die Datenbank schreiben oder ein Fixture laden.
- [ ] Der erste Graph zeigt gestartete Aktivitäten, Versuche, Sessions und deren beobachteten Zustand; die Auswahl öffnet zugeordnete Benutzer-/Agentennachrichten, Aufträge/Kontext, Toolparameter/-ergebnisse mit Dauer/Fehlern, Erkenntnisse und Artefakte.
- [ ] Live-Ereignisse und paginiertes Nachladen folgen bestätigten Positionen und stabilen Identitäten. Browser-/API-Neustart erhält Zuordnung und Reihenfolge ohne doppelte Anzeige; fehlende oder redigierte Inhalte bleiben explizit.
- [ ] Ein anderer authentifizierter Browserclient kann denselben berechtigten Run ohne Zugriff auf den ursprünglichen Rechner untersuchen. Rechteentzug verhindert weiteren unberechtigten Zugriff; sensible Daten werden nicht durch Filterwechsel oder Artefaktlinks zugänglich.
- [ ] Die Abnahme beginnt mit Eingabe und Start eines echten kontrollierten Issues und verfolgt denselben Run über zwei Clients bis zum Ergebnis oder konkreten Fehler. Browserprüfung und Vergleich mit öffentlichen History-/Artifact-Antworten beweisen den fachlichen Inhalt; die vollständige verschachtelte PRD-Graphnavigation folgt später.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
