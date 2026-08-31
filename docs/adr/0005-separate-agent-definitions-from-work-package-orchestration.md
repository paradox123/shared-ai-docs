# Separate agent definitions from work package orchestration

Agentenfähigkeiten und Work-Package-Orchestrierung sind getrennte Verantwortungsbereiche. Ein Agent Definition Repository gehört zu einem Agenten oder einer Agentenrolle und versioniert dessen Prompts, Skills, Tools, Policies, Integrationen und Zugriffe. Die Work Package Control Plane orchestriert dagegen Implementierungsläufe, Aktivitäten, Agentensessions, Run History und menschliche Steuerung und referenziert dafür konkrete Agent-Definition-Revisionen. Diese Trennung verhindert den überladenen Begriff „Platform“, erlaubt unabhängige Evolution mehrerer Agenten und hält die zentrale Orchestrierung frei von agentenspezifischen Capability-Details.

## Consequences

- Mehrere Agent Definition Repositories können unabhängig versioniert und von derselben Work Package Control Plane verwendet werden.
- Ein Implementierungslauf kann bei einem späteren Agentenaufruf eine inzwischen menschlich freigegebene neuere Agent-Definition-Revision verwenden, ohne eine laufende Operation umzuschreiben.
- Source-Code-Typen, Events und APIs verwenden ausschließlich die englischen Canonical Names `AgentDefinitionRepository`, `WorkPackageControlPlane` und `AgentEvolutionLoop` oder daraus konsistent abgeleitete Namen.
