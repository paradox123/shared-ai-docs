---
status: superseded by ADR-0018
---

# Fachquellenindex unabhängig von der Wiki-Aufbereitung pflegen

Daniel entschied am 17.09.2026, die Indexpflege aktueller Fachquellen von erfolgreicher Wiki-Kompilierung zu entkoppeln. Die vorherige Reihenfolge hielt bei mehrstündigen oder abgebrochenen Erstimporten auch die Recherche in bereits vorhandenen Originalen auf. Indexerfolg und fachliche Wiki-Pflege müssen deshalb getrennt ausgewiesen werden.

WikiQuery, Vollimportpflicht und damalige Wiki-Tagesfrist wurden am 02.10.2026 durch [ADR 0018](0018-agent-managed-markdown-wiki.md) ersetzt. Die unabhängige tägliche QMD-Indexpflege gilt weiter; sie prüft keinen Wiki-Inhalt und setzt kein Prüfdatum. Der aktuelle Vertrag steht in der [kanonischen Betriebs-Spec](../../openspec/specs/contextual-wiki-operations/spec.md) und in [Direkte Wiki-Pflege](../rag/llm-wiki.md).
