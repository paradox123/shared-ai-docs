---
status: accepted
---

# Kontextabhängiges LLM-Wiki über bestehenden Fachrepos

Die bestehenden Markdown-Repositories im Obsidian-Vault bleiben erhalten und liefern die Fachquellen für eine übergeordnete LLM-Wiki-Schicht. Diese Schicht ist kein eigenes Git-Repository, entsteht passend zum jeweiligen Kontext geklonter Repos und bildet den ersten Einstieg für Mensch und Agent in Obsidian, damit repoübergreifende Synthesen wiederverwendbar werden und Quellenänderungen den Prüfbedarf gemeinsamer Aussagen erkennen lassen.

Die Entscheidung folgt Daniels Klarstellung vom 11.09.2026: Die vorherige Empfehlung eines gemeinsamen Prozesses, der auch Fachseiten in den Repos besitzt und pflegt, ist keine Vorgabe für diese Schicht. „Input/raw“ beschreibt hier die Rolle bestehender Dokumente gegenüber dem Wiki, nicht deren mangelnde Aufbereitung; ihre fachliche Autorität wird dadurch nicht aufgehoben.

Erkenntnisse bleiben über Fragen und Sessions hinweg nutzbar, solange ihre benötigten Repo-Inputs zum Kontext gehören. Entfällt ein solcher Input, verschwindet die abhängige Erkenntnis; bei seiner Rückkehr kann sie neu entstehen. Damit bestimmt der vorhandene Quellenkontext den Wissensbestand, und das Wiki führt kein unabhängiges Gedächtnis ausgeschiedener Repos.

Lokale Persistenz und der Umgang mit menschlichen Wiki-Ergänzungen werden im [Konzeptgespräch](../rag/2026-09-11-kontextabhaengiges-llm-wiki.md) weiter konkretisiert. Die ADR hält die Architekturgrenze fest, keine implementierte Betriebsänderung oder Frameworkauswahl.
