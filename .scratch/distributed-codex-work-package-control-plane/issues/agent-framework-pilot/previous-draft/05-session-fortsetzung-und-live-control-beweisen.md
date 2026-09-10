# 05: Session-Fortsetzung und Live Control beweisen

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Resume, Fork, Fresh Retry, `interrupt`, `queue`, Cancel und Human Requests werden für einen expliziten Activity Attempt dauerhaft, unterscheidbar und nach Neustart genau einmal logisch verarbeitet.

**Blocked by:** 04: Externe Effekte, Base-SHA und Recovery absichern

**Covers:** US 36-51, 70-75, 81-82, 125

**LangGraph baseline:** Issue 06, 08 und 13 sowie Intervention-/Feedback-Contracts; die separate Codex-App-Interventionssession wird nicht übernommen.

**Status:** needs-triage

- [ ] Resume behält die Session-ID; Fork erzeugt neue ID plus Herkunft; Fresh Retry erzeugt eine neue ID ohne automatische Gesprächsübernahme.
- [ ] Eine durable Human Request bleibt nach Prozesswechsel sichtbar und akzeptiert genau eine passende Antwort für Attempt, Head und Lease-Epoche.
- [ ] `interrupt` stoppt/fenced den adressierten Prozess, reconciled vorhandene Effekte und verarbeitet genau einen nächsten Command.
- [ ] Mehrere `queue`-Commands bleiben nach Neustart in stabiler Annahmereihenfolge.
- [ ] Commands ohne eindeutiges Ziel werden bei parallelen Aktivitäten abgelehnt.
- [ ] Headless Codex-Session-Sichtbarkeit in der Codex-App ist keine Voraussetzung; alle beobachtbaren Sessionevents erscheinen im Operator-Verlauf.
- [ ] Prozesskill, verspätete Ausgabe und doppelte externe Events sind als Fault-Injection-Fälle abgedeckt.

## Session lesson

Normale `codex exec`-Sessions waren nicht als App-Tasks sichtbar. Der neue Pilot löst das über die gemeinsame Run History, nicht über die Annahme, jeder Worker müsse in der Codex-App auftauchen.
