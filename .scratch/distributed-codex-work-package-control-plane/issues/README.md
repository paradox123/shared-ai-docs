# Pilot issue sets

Die beiden Piloten bleiben getrennt:

- [`langgraph-pilot/`](langgraph-pilot/README.md) ist der Index auf die 13 unveränderten, kanonischen und bereits umgesetzten LangGraph-Tickets. Die Dateien bleiben an ihrem ursprünglichen Ort, damit bestehende Verweise und Historie nicht brechen.
- [`agent-framework-pilot/`](agent-framework-pilot/01-oss-durability-gate-und-isolierten-piloten-beweisen.md) enthält den freigegebenen aktiven Backlog für den zusätzlichen Microsoft-Agent-Framework-Piloten.
- [`agent-framework-pilot/previous-draft/`](agent-framework-pilot/previous-draft/README.md) bewahrt die zehn vor der Anwendung von `to-tickets` erzeugten Entwürfe. Sie sind historische Planungsgrundlage und nicht zur Umsetzung freigegeben.

Nur Tickets mit `Status: ready-for-agent` im Ordner `agent-framework-pilot/` gehören zum neuen Implementierungs-Backlog. Die wiederhergestellten Entwürfe tragen `Status: needs-triage`, damit kein Agent sie mit dem freigegebenen Backlog verwechselt.
