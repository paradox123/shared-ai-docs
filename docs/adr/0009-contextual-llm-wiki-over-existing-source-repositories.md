---
status: accepted
---

# Kontextabhängiges LLM-Wiki über bestehenden Fachrepos

Das gewählte Konzept ist Andrej Karpathys [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f); als Implementierung hat Daniel anschliessend Atomicstratas LLM-Wiki-Compiler am geprüften Commit `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb` gewählt. Daniel hat diese Trennung am 12.09.2026 ausdrücklich klargestellt. Der Mensch kuratiert Quellen und steuert die Analyse, das LLM schreibt und pflegt das Wiki; ein technisches Verbot menschlicher Wiki-Edits wird daraus nicht abgeleitet. Die [Originalquellenprüfung](../rag/2026-09-12-karpathy-llm-wiki-konzeptpruefung.md) grenzt Konzeptaussagen und lokale Anpassungen ab.

Die bestehenden Markdown-Repositories im Obsidian-Vault bleiben erhalten und liefern die Fachquellen für eine übergeordnete LLM-Wiki-Schicht. Diese Schicht ist kein eigenes Git-Repository, entsteht passend zum jeweiligen Kontext geklonter Repos und bildet den ersten Einstieg für Mensch und Agent in Obsidian, damit repoübergreifende Synthesen wiederverwendbar werden und Quellenänderungen den Prüfbedarf gemeinsamer Aussagen erkennen lassen.

Die Entscheidung folgt Daniels Klarstellung vom 11.09.2026: Die vorherige Empfehlung eines gemeinsamen Prozesses, der auch Fachseiten in den Repos besitzt und pflegt, ist keine Vorgabe für diese Schicht. „Input/raw“ beschreibt hier die Rolle bestehender Dokumente gegenüber dem Wiki, nicht deren mangelnde Aufbereitung; ihre fachliche Autorität wird dadurch nicht aufgehoben.

Erkenntnisse bleiben über Fragen und Sessions hinweg nutzbar, solange ihre benötigten Repo-Inputs zum Kontext gehören. Entfällt ein solcher Input, verschwindet die abhängige Erkenntnis; bei seiner Rückkehr kann sie neu entstehen. Damit bestimmt der vorhandene Quellenkontext den Wissensbestand, und das Wiki führt kein unabhängiges Gedächtnis ausgeschiedener Repos.

Die frühere Formulierung eines noch zu wählenden Konzepts ist damit korrigiert. Nachpflege folgt Karpathys Ingest-, Query- und Lint-Abläufen; Auslöser und technische Umsetzung sind in der [Umsetzungsspec](../../.scratch/contextual-llm-wiki/spec.md) und im [OpenSpec-Change](../../openspec/changes/archive/2026-09-13-integrate-contextual-llm-wiki/proposal.md) konkretisiert. Kein eigenes Wiki-Git-Repo, veränderliche externe Fachrepos und das Entfernen abhängiger Erkenntnisse bei Kontextverlust sind Daniels lokale Anpassungen, keine behaupteten Vorgaben des Originals. Insbesondere verändert der Wiki-Pflegeprozess seine Fachquellen nicht; deren vorhandene Pflege bleibt ausserhalb dieser Rolle möglich. Die ADR hält das Zielbild fest. Die lokale Integration wurde am 13.09.2026 akzeptiert; [ausgeführte Abnahme](../../contextual-llm-wiki/evidence/acceptance.md) und kanonische OpenSpec-Requirements dokumentieren den implementierten Umfang.
