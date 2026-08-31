# Operator Clients instead of human agent sessions

Menschen greifen auf einen zentral laufenden Implementierungslauf über einen Operator Client zu und erhalten keine eigene Supervisor- oder Agentensession. Die Control Plane persistiert eine gemeinsame Run History über alle von ihr gestarteten Codex-Sessions und streamt diese an beliebig viele verbundene Clients. Genau ein Mensch kann die Control Lease für den gesamten Implementierungslauf einschließlich aller parallelen Aktivitäten beanspruchen und mutierende Commands senden; alle anderen Clients bleiben vollständig lesend. Der Command Router ordnet einen Command anhand des aktuellen Workflow-Zustands der zuständigen Aktivität und Agentensession zu. Diese Trennung bewahrt die gewünschte gemeinsame Beobachtung und Remote-Steuerung, ohne Agentenhistorien in einen weiteren Modellkontext zu kopieren oder eine verteilte Multi-Agent-Chat-Synchronisation einzuführen.

## Consequences

- Ein Operator Client kann zustandsarm bleiben, nach Verbindungsabbruch ab einer Eventposition wieder anknüpfen und muss keinen Agentenprozess lokal besitzen.
- Ein Verbindungsabbruch gibt die Control Lease nicht frei. Sie bleibt der menschlichen Provideridentität zugeordnet, bis sie ausdrücklich freigegeben, per Control Transfer übertragen, per Forced Takeover übernommen oder durch Entzug der erforderlichen Repository Authorization ungültig wird.
- Agentenseitige Interventionsanfragen erscheinen als Ereignisse in derselben Run History und werden dem steuernden Client hervorgehoben; sie erzeugen keine zusätzliche menschliche Codex-Task.
- Die Control Plane benötigt einen geordneten Event-Stream, einen dauerhaften Command-Kanal, eine exklusive Control Lease und einen zentralen Command Router.
- Parallele Aktivitäten eines Implementierungslaufs können nicht von unterschiedlichen Menschen gleichzeitig gesteuert werden; ein Wechsel der steuernden Person ist immer ein Wechsel für den gesamten Lauf.
- Ein freiwilliger Control Transfer beginnt mit der Übernahmeanfrage eines lesenden Beobachters und wird erst durch die Bewilligung des aktuellen Inhabers wirksam. Die Control Plane überträgt die Control Lease atomar und zeichnet Anfrage, Bewilligung und neue Inhaberschaft in der Run History auf.
- Wenn diese Bewilligung nicht abgewartet werden soll oder kann, steht jedem zugriffsberechtigten Menschen ein gesondert auditierter Forced Takeover ohne Administratorrolle offen.
- Die Entscheidung für LangGraph, Temporal oder eine andere Durable-Workflow-Technologie bleibt von der menschlichen Oberfläche entkoppelt.
