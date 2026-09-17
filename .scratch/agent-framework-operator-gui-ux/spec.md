# Gemeinsame Run-Ansicht: Spezifikationseinstieg

Die Ticketaufteilung und ihre Abhängigkeiten sind am 14.09.2026 vom Nutzer freigegeben. Diese Ergänzung bleibt im bestehenden Change `add-agent-framework-operator-gui`; sie plant die UX-Verbesserung der vorhandenen Aufnahme, Hintergrundanalyse und Run-Beobachtung.

## Maßgebliche Quellen

- [Bestätigte UX-Entscheidungen und Anforderungszuordnung](../../openspec/changes/add-agent-framework-operator-gui/ux-ticket-plan.md)
- [Kanonische Anforderungen zu Aufnahme und Hintergrundstart](../../openspec/specs/agent-framework-operator-gui/spec.md)
- [Aktive Anforderungen zur Workflow- und Run-Beobachtung](../../openspec/changes/add-agent-framework-operator-gui/specs/agent-framework-operator-gui/spec.md)
- [Vorhandene Designentscheidungen und UI-Begriff „Anforderungen“](../../openspec/changes/add-agent-framework-operator-gui/design.md)
- [Domänenbegriffe](../../CONTEXT.md), [Operator Client und zentrale Run History](../../docs/adr/0002-operator-clients-instead-of-human-agent-sessions.md), [Repository Authorization](../../docs/adr/0007-derive-operator-access-from-repository-permissions.md)
- [UX/UI-Kritik mit überprüften Befunden](../../.impeccable/critique/2026-09-14T15-15-44Z__index-html.md)
- [Geprüfter Entwurf und Zugang zur interaktiven Designreferenz](../../.impeccable/designs/2026-09-14-gemeinsame-run-ansicht.md)
- [Tickets und Bearbeitungsfolge](README.md)

## Umsetzung und Abnahme

Die Tickets liefern jeweils ein benutzbares Verhalten von der Benutzeraktion über die vorhandenen öffentlichen Antworten bis zur sichtbaren Darstellung. Vertrags- oder Datenanpassungen erfolgen nur, soweit das jeweilige Verhalten sie benötigt. Es gibt kein eigenständiges horizontales UI-, API- oder Testticket und keinen begründeten Bedarf für ein breites vorgeschaltetes Refactoring.

Bei der Umsetzung gelten TDD beziehungsweise ein zunächst reproduzierbarer Fehlercheck, die Pflege der zugehörigen Szenarien im aktiven Change und die direkten Verhaltensnachweise des Repositories. Bestehende Ticket-03-Nachweise und lesbare Renderer sind Ausgangspunkt; bereits erfülltes Verhalten wird erhalten, statt nochmals als neue Fähigkeit implementiert.

Jedes Ticket prüft Desktop, Mobil und Tastaturbedienung an seinem eigenen Benutzerweg. Kontrast, Fokus und Beschriftungen müssen insbesondere im ausgewählten und aktualisierten Zustand verständlich bleiben. Die Abnahme hält erwartetes Verhalten, beobachtetes Ergebnis und Beleg fest. Ein simulierter Entwurf, ein erfolgreicher HTTP-Aufruf oder ein Screenshot ohne Vergleich mit gespeicherten Inhalten genügt nicht als Verhaltensnachweis.

Die Beispieldaten und lokalen Zustandswechsel des Entwurfs begründen weder feste Erkenntniszahlen noch zusätzliche Produktfunktionen. Handover, Retry/Cancel, Control Lease, PRD-Zerlegung und die vollständige Implementierungskette bleiben bei den ursprünglichen Tickets 04–16. Deren offene verteilte Nachweise werden durch diese UX-Tickets nicht geschlossen.
