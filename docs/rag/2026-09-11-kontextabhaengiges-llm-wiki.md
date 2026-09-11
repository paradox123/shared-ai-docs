# Kontextabhängiges LLM-Wiki über dem Obsidian-Vault

Stand: 11.09.2026. Laufendes Konzeptgespräch mit `grill-with-docs`; keine Implementierung oder Änderung laufender Automationen.

## Ausgangspunkt und Korrektur

Grundlage sind die abrufbaren Gesprächsinhalte der Tasks „Analysiere Agent-Wiki für Vault“ (`01a086d8-cd4c-7083-b338-90884b83d83b`) und „Finde Agent-Wiki-Alternativen“ (`01a08b7d-c661-7682-a082-3f680efe27a9`) sowie Daniels neue Vorgaben vom 11.09.2026. Im Alternativen-Task liefert der jüngste abrufbare Turn keine Nachrichten; seine Inhalte sind daher nicht rekonstruierbar.

Das [bisherige Zielbild](2026-09-10-agent-wiki-zielbild-nach-automationspruefung.md) betrachtete einen gemeinsamen Pflegeprozess auch als Besitzer kuratierter Fachseiten. Die aktuelle Vorgabe setzt stattdessen eine darüberliegende Wissensschicht voraus. Die [Alternativenrecherche](2026-09-10-agent-wiki-alternativen.md) bleibt Recherchehistorie; ihre Auswahlpräferenz ist unter der neuen Grenze nicht automatisch eine Architekturentscheidung.

## Festgelegt

- Die bestehenden Markdown-Repos und das Arbeiten im Obsidian-Vault bleiben erhalten.
- Diese Dokumente liefern den Input des LLM-Wikis. „Raw“ ist eine relative Rolle; bereits kuratierte Dokumentation bleibt eine gültige Fachquelle.
- Das Wiki bildet eine übergeordnete Wissensschicht und den ersten Einstieg für Agent und Mensch über Obsidian.
- Es ist kein eigenes Git-Repo und entsteht dynamisch passend zum Kontext geklonter Repos.
- Wiederkehrende Vergleiche und übertragbare Erkenntnisse werden dauerhaft nutzbar, statt bei jeder Frage neu erarbeitet zu werden.
- Diese Dauerhaftigkeit gilt innerhalb des vorhandenen Repo-Kontexts: Entfällt ein benötigter Repo-Input, verschwindet die davon abhängige Erkenntnis aus dem Wiki. Bei erneuter Aufnahme des Inputs kann sie neu entstehen. Das Wiki bewahrt damit kein unabhängiges Gedächtnis ausgeschiedener Repos. Daniel hat dieses Verhalten im Gespräch ausdrücklich festgelegt.
- Bei Änderungen einer Fachquelle wird erkennbar, welche gemeinsame Aussage erneut geprüft werden muss. Änderungserkennung allein ist noch keine inhaltliche Nachprüfung.
- SpecOps ist nach Daniels früherer Klarstellung ein nicht weiterverfolgter Prototyp. Bestehende Automationen dürfen grundsätzlich ersetzt werden; diese Möglichkeit ist kein Auftrag, sie jetzt abzuschalten.

Die Architekturgrenze ist in [ADR-0009](../adr/0009-contextual-llm-wiki-over-existing-source-repositories.md) festgehalten; Begriffe stehen im [Glossar](../../CONTEXT.md#llm-wiki).

## Arbeitsannahmen, noch keine weiteren Entscheidungen

- Die Eingangsdokumente behalten ihre fachliche Autorität. Die Wissensschicht ergänzt belegte Synthesen und Orientierung.
- QMD bleibt entsprechend dem [bestehenden Betriebsmodell](operating-model-rag-qmd.md) der Suchweg. Wie Wiki-Einstieg, Quellenzugriff und Kontextauswahl zusammenspielen, wird später konkretisiert.
- Ohne eigenes Git-Repo ist lokale Persistenz möglich; daraus folgt weder zwingend ein flüchtiges Wiki noch eine Sicherung seiner Inhalte.

## Offene materielle Entscheidungen

1. Menschliche Ergänzungen: Werden Korrekturen und neue Erkenntnisse beim Lesen in Obsidian direkt im Wiki eingegeben oder in den Fachquellen gepflegt? Für direkte Wiki-Eingaben wäre ihr Erhalt bei einer Neuerzeugung zu klären.
2. Kontextauswahl: Welche vorhandenen Repos gehören zu einer Wissenssicht, und welche Grenzen gelten für ihre gemeinsame Nutzung?
3. Aktualität: Wie werden betroffene Aussagen bis zur Nachprüfung dargestellt und von Agenten verwendet, auch bei geänderten oder widersprüchlichen Quellen?

Diese Punkte werden einzeln anhand konkreter Nutzungssituationen geklärt. Framework, Speicherformat und Auslöser werden erst danach gewählt, sofern sie keine weitere Produktentscheidung benötigen.

## Dokumentationsumfang

Kein passender aktiver Wiki-Change wurde gefunden. Diese Runde dokumentiert Begriffe und Architekturentscheidungen; ein Implementierungs-Change wird erst bei einem entsprechenden Arbeitsauftrag oder der Ausarbeitung verbindlicher Verhaltensanforderungen angelegt. Bestehende Recherchedateien und fremde Änderungen bleiben erhalten.
