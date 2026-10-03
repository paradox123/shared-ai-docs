---
status: superseded by ADR-0018
---

# Kontextabhängiges LLM-Wiki über bestehenden Fachrepos

Daniel wählte im September 2026 Andrej Karpathys LLM-Wiki-Konzept und anschließend Atomicstratas Compiler als damalige Implementierung. Das Wiki sollte dauerhafte, repoübergreifende Synthesen aus vorhandenen Obsidian-Fachquellen ermöglichen. Die Quellen behalten ihre fachliche Autorität und werden durch Wiki-Pflege nicht verändert; „raw“ beschreibt ihre Rolle als Input. Der Wiki-Bestand erhält kein eigenes Git-Repository.

Die Compilerarchitektur und der damalige Wiki-Einstiegsvertrag wurden am 02.10.2026 durch [ADR 0018](0018-agent-managed-markdown-wiki.md) ersetzt. Quellenautorität und dauerhafte Synthese gelten weiter; aktuelle Anforderungen stehen in der [kanonischen Wiki-Spec](../../openspec/specs/contextual-llm-wiki/spec.md), der Ablauf in [Direkte Wiki-Pflege](../rag/llm-wiki.md). Die [Konzeptprüfung](../rag/2026-09-12-karpathy-llm-wiki-konzeptpruefung.md) unterscheidet Aussagen des Originals von Daniels lokalen Entscheidungen.
