# Bestätigte UX-Ergänzung: gemeinsame Run-Ansicht

Am 14.09.2026 hat der Nutzer den Schwerpunkt „Gemeinsame Run-Ansicht mit Status und Ergebnis“ und den Umfang der vorhandenen Funktionen aus Tickets 01–03 gewählt. Anschließend hat er die vier Umsetzungstickets einschließlich ihrer Abhängigkeiten freigegeben und ihre Veröffentlichung im lokalen Tracker beauftragt.

Diese Planung konkretisiert den bestehenden GUI-Change. Sie ersetzt keine offene Anforderung und erweitert den Ausführungsumfang nicht um die späteren Workflowfähigkeiten aus Tickets 04–16. Der geprüfte [Entwurf](../../../.impeccable/designs/2026-09-14-gemeinsame-run-ansicht.md) erklärt die Informationsarchitektur; seine festen Beispieldaten und simulierten Startaktionen sind keine Implementierungsvorgabe.

## Bestätigte Entscheidungen

1. **UX-01 — Gemeinsame Run-Ansicht mit verlässlichem Status:** Titel, tatsächlicher Analysezustand und Ergebnis beziehungsweise Fehler bilden den Einstieg. Ergebnis, Verlauf, Dateien und Anforderungen bleiben unmittelbar erreichbar. Liste und Detail verwenden dieselbe bestätigte Zustandsbedeutung; abgeschlossene Analyse bedeutet weder Implementierung noch Gesamtabschluss. Blockiert durch das ursprüngliche GUI-Ticket 03.
2. **UX-02 — Analyseergebnis verständlich und vollständig lesen:** Lesbare Zusammenfassung und gezielt aufklappbare Erkenntnisse erhalten den gesamten gespeicherten Inhalt. Gruppierung erfolgt nur bei eindeutiger Grundlage in den Daten. Artefakte und unveränderte aufgenommene Anforderungsfassung bleiben nachvollziehbar; fehlende Inhalte werden explizit. Blockiert nur durch UX-01.
3. **UX-03 — Agentenarbeit verfolgen und Fehler gezielt untersuchen:** Auswählbare Schritte führen zu lesbarer Agentenarbeit und sämtlichen gespeicherten Beobachtungen. Fehler verweisen direkt auf den zugehörigen Versuch und vorhandene Belege. Auswahl und Tastaturfokus bleiben bei Live-Aktualisierung erhalten; mobile Schritte sind vollständig sichtbar. Blockiert nur durch UX-01.
4. **UX-04 — Anforderungen aufnehmen und direkt zur Analyse gelangen:** „Neu“, „Nur aufnehmen“ und „Aufnehmen und analysieren“ verwenden die existierenden öffentlichen Aufnahme- und Startverträge. Fehler bleiben verständlich und gespeicherte Identitäten bei Wiederholung und späterem Öffnen stabil. Blockiert nur durch UX-01.

## Veröffentlichung und Reihenfolge

Die [vier einzelnen Tickets](../../../.scratch/agent-framework-operator-gui-ux/README.md) tragen `ready-for-agent` unter ihren jeweiligen Blockern. UX-01 bis UX-04 sind eigene Kennungen; Nummern und Inhalte der ursprünglichen GUI-Tickets bleiben erhalten.

Empfohlene Priorität: **GUI-03 → UX-01 → UX-03 → UX-02 → UX-04 → GUI-04**, anschließend weiter nach dem bestehenden GUI-Backlog. UX-02 bis UX-04 haben untereinander keine Blocking-Kanten. Die Platzierung vor GUI-04 ist eine Priorisierung, keine zusätzliche fachliche Abhängigkeit dieses bestehenden Tickets.

Zum Veröffentlichungszeitpunkt liegt der lokal geprüfte Stand von GUI-03 in seinem separaten Arbeitszweig und noch nicht in `main`. UX-01 setzt dessen Abschluss und Verfügbarkeit in der gemeinsamen Implementierungsbasis voraus. Eine Planung ersetzt weder dessen Abnahme noch seine Integration.

## Anforderungszuordnung

| Ticket | Bestehende Anforderung | Direkter Nachweis |
| --- | --- | --- |
| UX-01 | Kanonisch: `GitHub submission starts a real background analysis`; aktiv: `Workflow and persisted run inspection` | Gespeicherten Run öffnen, Zustandswechsel beobachten und erneut öffnen; öffentliche Zustände mit Liste und Detail vergleichen |
| UX-02 | Kanonisch: unveränderliche Aufnahme und lesbares Analyseergebnis; aktiv: `Submissions and run relationships are database-backed`, `Workflow and persisted run inspection` | Alle Erkenntnisse, Artefakte und aufgenommene Fassung mit öffentlichen Antworten vergleichen, einschließlich fehlender Inhalte |
| UX-03 | Aktiv: `Workflow and persisted run inspection`, insbesondere `Inspect a background failure` | Nachrichten und Werkzeugergebnisse nachvollziehen, Fehler dem richtigen Versuch zuordnen, Live-/Nachladeverhalten und Tastaturfokus prüfen |
| UX-04 | Kanonisch: `GitHub submission intake precedes execution`, `GitHub submission starts a real background analysis` | Beide Aufnahmewege, abgewiesenen Start, Wiederholung und Wiederöffnen desselben realen Runs über die GUI zeigen |

Die zugehörigen Quellen sind die [kanonische Spec](../../specs/agent-framework-operator-gui/spec.md) und die [aktive GUI-Spec](specs/agent-framework-operator-gui/spec.md). Jede Umsetzung pflegt ihre präzisen Szenarien im aktiven Change, beginnt mit Verhaltenstest beziehungsweise reproduzierbarem Fehlercheck und ergänzt Desktop-, Mobil- und Tastaturnachweise. Die ursprünglichen verteilten Abnahmegates bleiben offen, bis sie in den dafür vorgesehenen Tickets belegt sind.
