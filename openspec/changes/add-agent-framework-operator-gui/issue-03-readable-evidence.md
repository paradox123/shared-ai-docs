# Ticket 03 — verständliche Agentenarbeit

Die Nutzerkorrektur betrifft den Zweck der Oberfläche: Fortschritt, Arbeit,
Ergebnis und Fehler eines Agenten nachvollziehen, ohne Protokoll-JSON zu lesen.
Die ursprüngliche Datenprüfung war dafür kein ausreichender Darstellungsnachweis.

| Erwartung | Beobachtetes Verhalten | Beleg |
| --- | --- | --- |
| Fortschritt und Ergebnis erkennen | Benannte Schritte mit Zustand und Dauer; der aktuelle Versuch ist ausgewählt, seine Ergebniszusammenfassung steht direkt oben. | [Desktop](evidence/issue-03-readable/live-workflow-desktop.png), [Mobil](evidence/issue-03-readable/live-workflow-mobile.png) |
| Agentenarbeit lesen | Auftrag und Anweisung lassen sich öffnen, Nachrichten erscheinen als Text, Erkenntnisse als Liste. Reine Protokollmeldungen und doppelte Darstellungen bleiben aus dem normalen Sessionverlauf heraus. | Öffentliche Browserprüfung vergleicht Ergebnistext und jede Erkenntnis mit den gespeicherten Antworten. |
| Werkzeuge und Fehler untersuchen | Werkzeugname, Parameter, Ausgabe, gemessene Dauer und Fehler sind lesbar. Der kontrollierte Terminalfall zeigt `git status --short`, 42 ms, Exit-Code 128 und `fatal: cannot open repository`; ein Laufzeitfehler bleibt im normalen Verlauf sichtbar. | [Browserprotokoll](evidence/issue-03-readable/browser.log) |
| Vollständige Inhalte behalten | „Alle Ereignisse“ und geschlossene technische Details erhalten jeden Originaldatensatz. Benannte Artefakte öffnen lesbare Inhalte und bieten zusätzlich den Originalinhalt. Fremde JSON-Strukturen unterbrechen den Verlauf nicht. | Exakter Vergleich sämtlicher ausgewählter Originalereignisse und Artefaktinhalte zwischen Browsern und öffentlicher API. |
| Zugriff und Wiederaufnahme erhalten | API-Neustart, Pagination, fehlgeschlagene Aktualisierung und Rechteentzug behalten ihre geprüfte Semantik; Filter können entzogene Inhalte nicht wieder anzeigen. | [Browserprotokoll](evidence/issue-03-readable/browser.log), [realer Run](evidence/issue-03-readable/live-workflow.json) |

## Reviews und Grenzen

Finale Browserprüfung: **9 bestanden, 133,824 s**. Der ausdrücklich aktivierte
reale GitHub-/Codex-Test bestand erneut in **144,539 s**. Run
`c8c55cd0-91bf-40f3-b685-f56b3e174a7e` enthält 22 kanonische Ereignisse, davon
18 in der ausgewählten Agentensession. Beide Browser lesen dieselben vollständigen
Originalereignisse; die sichtbare Zusammenfassung und jede Erkenntnis stimmen
mit der öffentlichen Antwort überein. Nach API-Neustart bleiben die Identitäten
und Inhalte gleich. Beide Artefakte (4.276 und 26.983 Bytes) stimmen mit ihren
Manifest-SHA-256 überein. Desktop und Mobilansicht wurden tatsächlich betrachtet;
die Standardansicht enthält keine offenen technischen JSON-Blöcke.

[Protokoll des echten Runs](evidence/issue-03-readable/live.log).

Die [Gesamtregression](evidence/issue-03-readable/full-regression.log) bestand:
**226 Fälle, 201 bestanden, 25 optionale Integrationen übersprungen, keine Fehler,
1.115,086 s**. Die zwei zusätzlichen Review-Regressionsfälle wurden nach Beginn
der Discovery ergänzt und sind in der separat ausgeführten finalen Neuner-
Browserprüfung enthalten. Die GUI-Fälle der Gesamtsuite liefen ebenfalls nach
dem korrigierten Build. Strikte OpenSpec-Validierung, JavaScript-Syntaxprüfung,
Diff-Prüfung, Artefaktprüfsummen und verlinkte Nachweise sind geprüft.

Reviewbasis der Korrektur: `8f944c7`; Implementierung `aeab6b9`, Korrektur `257ae17`.
Standards: zwei Befunde behoben (unbekannte JSON-Strukturen, native Werkzeuge),
erneute Originalreproduktionen ohne Befund. Spec: zwei Befunde behoben
(ausgeblendete Laufzeitfehler, Terminalparameter/-ausgabe), erneute Chrome-
Reproduktionen ohne Befund. DRY/SOLID/KISS-Nachprüfung ohne offene Befunde.

Der reale Vergleich verwendet ein tatsächliches GitHub-Issue und den tatsächlichen
Codex-Adapter. Zwei Browserkontexte laufen auf einem Mac; separate physische
Rechner bleiben Ticket 16. Die Änderung liegt im Implementierungsbranch;
eine Veröffentlichung auf Azure oder eine Nutzerabnahme wird nicht behauptet.

Die verhaltensbezogenen Rotprüfungen sind erhalten: [lesbarer Einstieg](evidence/issue-03-readable/red-readable.log),
[Artefaktdarstellung](evidence/issue-03-readable/red-artifact.log),
[unbekannte Inhalte](evidence/issue-03-readable/red-unknown-content.log),
[Laufzeitfehler](evidence/issue-03-readable/red-runtime-error.log).
