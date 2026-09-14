# Operator Clients instead of human agent sessions

Menschen greifen auf einen zentral laufenden Implementierungslauf über einen Operator Client zu und erhalten keine eigene Supervisor- oder Agentensession. Die Control Plane persistiert eine gemeinsame Run History über alle von ihr gestarteten Codex-Sessions und streamt diese an beliebig viele verbundene Clients. Genau ein Mensch kann die Control Lease für den gesamten Implementierungslauf einschließlich aller parallelen Aktivitäten beanspruchen und mutierende Commands senden; alle anderen Clients bleiben vollständig lesend. Der Command Router ordnet einen Command anhand des aktuellen Workflow-Zustands der zuständigen Aktivität und Agentensession zu. Diese Trennung bewahrt die gewünschte gemeinsame Beobachtung und Remote-Steuerung, ohne Agentenhistorien in einen weiteren Modellkontext zu kopieren oder eine verteilte Multi-Agent-Chat-Synchronisation einzuführen.

## Consequences

- Ein Operator Client kann zustandsarm bleiben, nach Verbindungsabbruch ab einer Eventposition wieder anknüpfen und muss keinen Agentenprozess lokal besitzen.
- Ein Verbindungsabbruch gibt die Control Lease nicht frei. Sie bleibt der menschlichen Provideridentität zugeordnet, bis sie ausdrücklich freigegeben, per Control Transfer übertragen, per Forced Takeover übernommen oder durch Entzug der erforderlichen Repository Authorization ungültig wird.
- Agentenseitige Interventionsanfragen erscheinen als Ereignisse in derselben Run History und werden dem steuernden Client hervorgehoben; sie erzeugen keine zusätzliche menschliche Codex-Task.
  Diese letzte Einschränkung wird für gezielt zugestellte Handover-Aufträge durch [ADR 0013](0013-deliver-handover-through-a-workstation-client.md) erweitert: Ein Workstation Client öffnet dafür automatisch eine korrelierte lokale Assistenzsession. Die zentrale Workflow-Session bleibt bestehen.
- Die Control Plane benötigt einen geordneten Event-Stream, einen dauerhaften Command-Kanal, eine exklusive Control Lease und einen zentralen Command Router.
- Parallele Aktivitäten eines Implementierungslaufs können nicht von unterschiedlichen Menschen gleichzeitig gesteuert werden; ein Wechsel der steuernden Person ist immer ein Wechsel für den gesamten Lauf.
- Ein freiwilliger Control Transfer beginnt mit der Übernahmeanfrage eines lesenden Beobachters und wird erst durch die Bewilligung des aktuellen Inhabers wirksam. Die Control Plane überträgt die Control Lease atomar und zeichnet Anfrage, Bewilligung und neue Inhaberschaft in der Run History auf.
- Wenn diese Bewilligung nicht abgewartet werden soll oder kann, steht jedem zugriffsberechtigten Menschen ein gesondert auditierter Forced Takeover ohne Administratorrolle offen.
- Die Entscheidung für LangGraph, Temporal oder eine andere Durable-Workflow-Technologie bleibt von der menschlichen Oberfläche entkoppelt.

## Clarification: GUI and local-agent access

Die grafische Bedienoberfläche ergänzt die bestehenden Zugangswege. Ein Mensch darf seinen vorhandenen lokalen Agenten zur Diagnose und Unterstützung eines zentralen Runs einsetzen. Ein gezieltes Handover stellt ihm den zugeordneten Kontext und autorisierten Zugriff auf die gespeicherten Einreichungen, Historien und Artefakte bereit; dafür wird weder automatisch eine zusätzliche Supervisor-Session erzeugt noch die vollständige Run History in jeden Modellkontext kopiert.

Sessions und Workflow-Ausführung bleiben zentral verwaltet. Der lokale Agent greift über die kontrollierten Lese- und Steuerungsschnittstellen zu. Seine gesamte beobachtbare Arbeit innerhalb der zugeordneten Session wird als Workflow-Aktivität zentral erfasst: Benutzer- und Agentennachrichten, ausgegebene Erkenntnisse, Toolaufrufe mit Parametern, Ergebnissen, Dauer und Fehlern sowie Artefakte und Eingriffe. Das gilt auch für eine rein lesende Diagnose und erweitert keine Berechtigung zur Steuerung des Runs. Repository Authorization, Control Lease, Fencing und interaktive menschliche Freigaben gelten unabhängig vom Zugangsweg. Ein Handover verlagert weder den Worker noch dessen Arbeitsverzeichnis auf den Rechner des Menschen.

Diese vollständige Beobachtbarkeit über verschiedene Clients hinweg konkretisiert die bereits bestehende Pilot-PRD, insbesondere User Stories 27–35 und 77–78 sowie die Systemtests zur gemeinsamen Historie. Die GUI führt sie nicht als neue Produkteigenschaft ein. Die Zuordnung über Einreichung, abgeleitete Issues, Aktivitäten, Versuche, Sessions, Ausführungsrechner und Akteure macht den gesamten PRD-/Issue-Lebenszyklus nachvollziehbar.
