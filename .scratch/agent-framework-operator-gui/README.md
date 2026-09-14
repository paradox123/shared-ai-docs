# Agent Framework Operator GUI

Die vom Nutzer bestätigte Aufteilung ist als 16 einzelne lokale Tickets veröffentlicht. Ticket 01 ist implementiert und lokal einschließlich echter GitHub-Aufnahme geprüft; für die Abnahme auf getrennten Rechnern steht es auf `needs-info`. Die übrigen Tickets sind `ready-for-agent`; ausführbar ist jeweils nur ein Ticket, dessen Blocker abgeschlossen sind.

Die ersten drei Tickets liefern nacheinander Einreichung, ersten Hintergrundstart und Run-Beobachtung. Danach wird der lokale Handover-Pfad früh real geprüft. Server-/Client-Betrieb, vollständige zentrale Historie und die bisherigen Pilot-Zugangswege bleiben verbindlich.

## Einstieg

- [Maßgebliche Anforderungen und Quellen](spec.md)
- [Unverbindlicher Backstage-/React-Flow-Prototyp und Einstieg für Implementierungs-Sessions](prototype.md)
- [Bestätigte Aufteilung mit Anforderungsabdeckung](../../openspec/changes/add-agent-framework-operator-gui/ticket-plan.md)
- [Design und Implementierungsannahmen](../../openspec/changes/add-agent-framework-operator-gui/design.md)
- [Abnahme und Integrationsrisiken](../../openspec/changes/add-agent-framework-operator-gui/handoff.md)

## Tickets

| Nr. | Ticket | Blockiert durch |
| --- | --- | --- |
| 01 | [GitHub Issue eingeben und gespeicherte Einreichung wiederfinden](issues/01-github-issue-eingeben-und-einreichung-wiederfinden.md) | Keine |
| 02 | [Eingereichtes Issue als erste Hintergrundaktivität starten](issues/02-eingereichtes-issue-als-hintergrundaktivitaet-starten.md) | 01 |
| 03 | [Selbst gestarteten Run als Workflow und Sessionverlauf beobachten](issues/03-gestarteten-run-als-workflow-und-sessionverlauf-beobachten.md) | 02 |
| 04 | [Handover im lokalen Agenten öffnen und Diagnose zentral erfassen](issues/04-handover-im-lokalen-agenten-oeffnen-und-diagnose-erfassen.md) | 03 |
| 05 | [Handover und lokale Historie nach Verbindungsabbruch fortsetzen](issues/05-handover-und-historie-nach-verbindungsabbruch-fortsetzen.md) | 04 |
| 06 | [Control Lease zwischen Menschen in der GUI übergeben](issues/06-control-lease-in-der-gui-uebergeben.md) | 02 |
| 07 | [Intervention per GUI oder lokalem Agenten beantworten](issues/07-intervention-per-gui-oder-lokalem-agenten-beantworten.md) | 04, 06 |
| 08 | [Aktive und fehlgeschlagene Versuche gezielt steuern](issues/08-aktive-und-fehlgeschlagene-versuche-gezielt-steuern.md) | 07 |
| 09 | [Eingereichtes Issue unbeaufsichtigt bis Intervention oder Review bearbeiten](issues/09-eingereichtes-issue-unbeaufsichtigt-bis-intervention-oder-review-bearbeiten.md) | 02 |
| 10 | [Bereitschaft zustellen und den aktuellen Head menschlich freigeben](issues/10-bereitschaft-zustellen-und-aktuellen-head-menschlich-freigeben.md) | 04, 06, 09 |
| 11 | [Lokale Issue-Datei über die Workstation einreichen und bearbeiten](issues/11-lokale-issue-datei-ueber-die-workstation-einreichen.md) | 04, 09 |
| 12 | [GitHub-PRD in verknüpfte Issues zerlegen](issues/12-github-prd-in-verknuepfte-issues-zerlegen.md) | 07, 09 |
| 13 | [PRD-Datei in lokale Issue-Dateien zerlegen](issues/13-prd-datei-in-lokale-issue-dateien-zerlegen.md) | 11, 12 |
| 14 | [Abhängige Issues nach menschlichem Merge selbstständig fortsetzen](issues/14-abhaengige-issues-nach-menschlichem-merge-fortsetzen.md) | 13 |
| 15 | [Gesamten PRD-Lebenszyklus als Workflow erkunden](issues/15-gesamten-prd-lebenszyklus-als-workflow-erkunden.md) | 05, 13 |
| 16 | [Verteilten Gesamtfall und verbleibende Issue-14-Gates nachweisen](issues/16-verteilten-gesamtfall-und-issue-14-gates-nachweisen.md) | 08, 10, 14, 15 |

Initial ist nur Ticket 01 ohne Blocker. Die Blocker in den einzelnen Ticketdateien sind maßgeblich; Nummerierung allein bedeutet keine vollständig lineare Bearbeitungsreihenfolge.

Jedes Ticket wird in frischem Implementierungskontext mit den Quellen aus dem Feature-Einstieg bearbeitet. Die Repository-Regeln für TDD, öffentliche Verhaltensnachweise und Review gelten. Die bisherige Pilot-Abnahme zu Issue 14 und deren offener Change bleiben separat und unverändert.
