# Operator GUI: gemeinsame Run-Ansicht

Die vier UX-Tickets wurden am 14.09.2026 vom Nutzer einschließlich Granularität und Blockern freigegeben. Sie konkretisieren die gemeinsame Run-Ansicht für die Funktionen der ursprünglichen Operator-GUI-Tickets 01–03 im bestehenden Change `add-agent-framework-operator-gui`.

## Einstieg

- [Maßgebliche Anforderungen, Designreferenz und Abnahme](spec.md)
- [Bestätigter UX-Plan im aktiven OpenSpec-Change](../../openspec/changes/add-agent-framework-operator-gui/ux-ticket-plan.md)
- [Ursprüngliche Operator-GUI-Tickets 01–16](../agent-framework-operator-gui/README.md)

## Tickets

Die Bezeichnungen UX-01 bis UX-04 unterscheiden diese Ergänzung von den ursprünglichen GUI-Tickets. Die lokalen Dateien sind wie im Tracker vorgesehen von 01 an nummeriert.

| Kennung | Ticket | Blockiert durch |
| --- | --- | --- |
| UX-01 | [Gemeinsame Run-Ansicht mit verlässlichem Status](issues/01-gemeinsame-run-ansicht-mit-verlaesslichem-status.md) | ursprüngliches GUI-Ticket 03 |
| UX-02 | [Analyseergebnis verständlich und vollständig lesen](issues/02-analyseergebnis-verstaendlich-und-vollstaendig-lesen.md) | UX-01 |
| UX-03 | [Agentenarbeit verfolgen und Fehler gezielt untersuchen](issues/03-agentenarbeit-verfolgen-und-fehler-gezielt-untersuchen.md) | UX-01 |
| UX-04 | [Anforderungen aufnehmen und direkt zur Analyse gelangen](issues/04-anforderungen-aufnehmen-und-direkt-zur-analyse-gelangen.md) | UX-01 |

## Bearbeitungsfolge

Empfohlen: **GUI-03 → UX-01 → UX-03 → UX-02 → UX-04 → GUI-04**, danach nach den bestehenden Blockern und Prioritäten mit GUI-05–16 fortfahren. Der frühe Fehlerzugang aus UX-03 unterstützt die spätere Handover-Diagnose.

UX-02, UX-03 und UX-04 sind nach UX-01 fachlich unabhängig. Die empfohlene Reihenfolge erzeugt keine zusätzlichen Blocking-Kanten und verändert insbesondere die Blocker des ursprünglichen GUI-Tickets 04 nicht.

Bei Veröffentlichung ist GUI-03 im separaten Arbeitszweig lokal als `resolved` dokumentiert, in `main` aber noch nicht integriert. Vor Beginn von UX-01 dessen Abschluss und Verfügbarkeit in der gemeinsamen Implementierungsbasis prüfen. Danach sind jeweils nur Tickets ausführbar, deren Blocker abgeschlossen sind; `ready-for-agent` bezeichnet die ausreichende Spezifikation, nicht einen aufgehobenen Blocker.

Die Planungsfreigabe allein startete keine Implementierung und schloss weder bestehende Tickets noch den GUI-Change. Jedes Ticket wird anhand seiner eigenen öffentlichen Verhaltensnachweise und Browserprüfung abgenommen.

## Umsetzungsstand

UX-01 ist am 14.09.2026 auf `codex/operator-gui-ux-01`, basierend auf dem lokal
geprüften GUI-03-Stand `a46a133`, umgesetzt und technisch verifiziert.
[Öffentliche Verhaltensnachweise und Browserbilder](../../openspec/changes/add-agent-framework-operator-gui/ux-01-evidence.md)
dokumentieren den Abschluss. Menschliche Abnahme und Integration in `main` werden
damit nicht vorweggenommen. UX-02 bis UX-04 bleiben offen und können auf dieser
gemeinsamen Implementierungsbasis fortgesetzt werden.
