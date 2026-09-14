---
status: accepted
date: 2026-09-14
---

# Bestehende Control Plane als Backend mit versionierten Workflows weiterentwickeln

Der Microsoft-Agent-Framework-Pilot wird schrittweise zum Backend des Operator Clients ausgebaut. Seine bestehenden Run-, History-, Steuerungs- und Agentenverträge werden weiterverwendet und gezielt refaktoriert. Perspektivisch unterstützt die Work Package Control Plane unterschiedliche versionierte Workflow-Definitionen; ihre fachlichen Regeln bleiben unabhängig vom konkreten Ablauf. Das erhält die bereits erarbeiteten Berechtigungs-, Wiederaufnahme- und Nachweisgrenzen und vermeidet eine feste Kopplung aller Clients an die heutige Implementierungs-/Review-/Reparaturfolge.

## Zuständigkeiten und Zustand

- **Operator Client:** Eine Backstage-/React-Flow-Oberfläche dient der Einreichung, Beobachtung und autorisierten Steuerung. Fachliche Entscheidungen bleiben im Backend. CLI und lokale Agentenzugänge bleiben erhalten; der Workstation Client übernimmt die lokale Integration gemäß [ADR 0013](0013-deliver-handover-through-a-workstation-client.md).
- **API:** Nimmt autorisierte Aufträge dauerhaft an und stellt Lese- und Steuerungsschnittstellen bereit. Lang laufende Verarbeitung hängt nicht an einer HTTP-Verbindung. API-Prozesse sind hinsichtlich des notwendigen Fachzustands austauschbar; Verbindungen und temporäre Caches dürfen im Arbeitsspeicher liegen.
- **Hintergrundausführung:** Disposition und Workflow-Worker bearbeiten angenommene Aufträge unabhängig von Browser und API-Verbindung. Ein Workflow besitzt Fortschritt und Wartezustände; sein ausführender Prozess soll anhand dauerhafter Aufzeichnungen ersetzbar sein. Wiederaufnahme gleicht bereits eingetretene externe Wirkungen ab, statt sie blind zu wiederholen.
- **Speicherung:** PostgreSQL hält den maßgeblichen Fachzustand, angenommene Commands und die kanonische Run History samt Leseansichten. Technische Workflow-Checkpoints, Agentensessions, Arbeitsverzeichnisse und Artefaktinhalte können eigenen persistenten Zustand besitzen. Ihre Zuordnung und Wiederaufnahme sind explizit; Framework-Zustand ersetzt weder fachliche Identitäten noch Run History.

Diese Grenzen sind Verantwortungsbereiche. Sie verlangen weder je einen Microservice noch eine neue Queue-Technologie. Konkrete Prozessaufteilung und Deployment bleiben Umsetzungsentscheidungen innerhalb der bestehenden Betriebs- und Technologieentscheidungen.

## Fachlicher Auftrag, Definition und Ausführung

Ein **fachlicher Auftrag** bleibt durch Einreichung, Issue beziehungsweise Arbeitsmandat mit Scope, Repository Authorization und fachlichen Abschlussbedingungen beschrieben. Eine **Workflow-Definition** beschreibt einen versionierten Bearbeitungsablauf mit Schritten, Übergängen und erwarteten Eingaben und Ergebnissen. Eine **Workflow-Ausführung** ist dessen konkrete Instanz mit Aktivitäten, Versuchen und Wartezuständen; sie ist weder der Auftrag selbst noch eine einzelne Agentensession.

Für den bestehenden Implementierungspfad referenziert der `ImplementationRun` die verwendete Workflow-Definition und ihre Version. Änderungen an einer Definition schreiben laufende Ausführungen nicht stillschweigend um. Beispielsweise läuft ein bereits begonnener Run mit Version 1 weiter, wenn Version 2 veröffentlicht wird. Ein Wechsel laufender Ausführungen benötigt eine gesondert definierte Migration; diese ADR führt sie nicht ein. Die konkrete Abbildung von Workflow-Ausführung und `ImplementationRun` auf Typen und Tabellen bleibt zu klären und erhält den bestehenden issuegebundenen Run-Vertrag sowie die Mandatsbezüge.

Die Control Plane verantwortet gemeinsame Regeln: Repository Authorization, Control Lease und Fencing, Repository-Serialisierung, vollständige beobachtbare Historie sowie die für den Auftrag geltenden menschlichen Freigabe-, Merge- und Abschlussbedingungen. Der ausgewählte Workflow organisiert die Bearbeitung innerhalb dieser Grenzen. Eine alternative Schrittfolge darf diese Regeln nicht umgehen. Die gemeinsamen API- und Darstellungsverträge dürfen nicht voraussetzen, dass jeder Ablauf dieselben Schrittnamen oder dieselbe Reihenfolge hat; workflowspezifische Fähigkeiten und zulässige Aktionen bleiben explizit.

Der Graph wird aus der verwendeten Definition und dem beobachteten Ausführungszustand abgeleitet. Graphlayout und Bedienung bestimmen keine Backend-Übergänge. Workflow-Definitionen sind außerdem von Agent Definitions zu unterscheiden: Sie orchestrieren Schritte und referenzieren Agentenfähigkeiten; Prompts, Skills und Tools bleiben gemäß [ADR 0005](0005-separate-agent-definitions-from-work-package-orchestration.md) in Agent Definition Repositories. Die dort erlaubte Auswahl einer neueren freigegebenen Agent-Definition-Revision bei späteren Aufrufen wird durch die Bindung der Workflow-Version nicht aufgehoben.

## Umfang und Nachweisstand

Zunächst wird der vorhandene Workflow hinter einem klaren Erweiterungspunkt weiterentwickelt; die Zuordnung von Definition und Version wird beim Backend-Ausbau vorgesehen. Weitere ausführbare Workflows, Auswahl-/Freigaberegeln für Definitionen, ein visueller Editor, eine allgemeine Workflow-Sprache oder austauschbare Engines benötigen eigene konkretisierte Anforderungen. Sie werden durch diese perspektivische Entscheidung nicht automatisch zu zusätzlichen Akzeptanzkriterien der 16 GUI-Tickets.

Die ADR dokumentiert das beschlossene Zielbild, keine fertige Implementierung. Der [Pilot](../../microsoft-agent-framework-work-package-pilot/README.md) besitzt bereits getrennte API-/Worker-Prozesse und dauerhafte fachliche Speicherung; durchgängige autonome Disposition und der vollständige verteilte Ablauf sind im [GUI-Change](../../openspec/changes/add-agent-framework-operator-gui/design.md) noch zu liefern und nachzuweisen. Die Technologie- und Nachweisgrenzen aus [ADR 0008](0008-prefer-microsoft-agent-framework-for-dotnet-control-plane-spike.md) und dem dokumentierten Pilotstand werden hier nicht neu entschieden. Der unabhängige LangGraph-Pilot bleibt erhalten.

Die [Prototyp-Einordnung](../../.scratch/agent-framework-operator-gui/prototype.md) gilt weiter: Screens, Texte und simulierte Abläufe sind unverbindliche Designreferenzen und definieren keine zusätzlichen Anforderungen. Diese Architekturentscheidung stammt aus der ausdrücklichen Diskussion über Backend und variable Workflows, nicht aus dem Prototyp.
