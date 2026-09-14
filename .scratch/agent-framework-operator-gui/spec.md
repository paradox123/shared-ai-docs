# Agent Framework Operator GUI: Spezifikationseinstieg

Status: ready-for-agent

Die Tickets dieses Features implementieren den bestätigten OpenSpec-Change `add-agent-framework-operator-gui`. Dieser Einstieg verweist auf die maßgeblichen Anforderungen und führt keine abweichende Kopie davon ein.

## Verbindliche Quellen

- [Vollständige Anforderungen und Szenarien](../../openspec/changes/add-agent-framework-operator-gui/specs/agent-framework-operator-gui/spec.md)
- [Ziel und Umfang](../../openspec/changes/add-agent-framework-operator-gui/proposal.md)
- [Entscheidungen und Implementierungsannahmen](../../openspec/changes/add-agent-framework-operator-gui/design.md)
- [Bestehende Pilot-PRD](../distributed-codex-work-package-control-plane/spec.md)
- [Domänenbegriffe](../../CONTEXT.md)
- [Operator Client und lokale Agenten](../../docs/adr/0002-operator-clients-instead-of-human-agent-sessions.md)
- [Quellenerhalt bei der Issue-Zerlegung](../../docs/adr/0012-preserve-submission-source-for-derived-issues.md)
- [Automatisches Handover über den Workstation Client](../../docs/adr/0013-deliver-handover-through-a-workstation-client.md)
- [Backend-Aufteilung und perspektivisch versionierte Workflows](../../docs/adr/0014-evolve-control-plane-backend-with-versioned-workflows.md) — Architekturziel; zusätzliche Workflows und Editor-Funktionen erweitern die aktuelle Ticket-Abnahme nicht automatisch.

## Umsetzung und Abnahme

- [Unverbindliche Designreferenz: Prototyp, Grenzen und Session-Einstieg](prototype.md) — Screens, Texte und simulierte Abläufe ergänzen keine Anforderungen.
- [Alle Tickets und ihre Blocker](README.md)
- [Anforderungsabdeckung und bestätigte Ticketaufteilung](../../openspec/changes/add-agent-framework-operator-gui/ticket-plan.md)
- [Abnahmeszenarien und verbleibende Integrationsrisiken](../../openspec/changes/add-agent-framework-operator-gui/handoff.md)

Zentrale Hintergrundarbeit, Workstation-Diagnosen und alle beteiligten beobachtbaren Sessions gehören zum gemeinsamen PRD-/Issue-Lebenszyklus. Die GUI ergänzt bestehende Zugangswege. Eine bestandene Teilprüfung oder die Veröffentlichung dieses Backlogs ersetzt keinen fehlenden Verhaltensnachweis und schließt das ursprüngliche Pilot-Issue 14 nicht automatisch.
