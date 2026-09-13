## Why

Das akzeptierte Wiki kompiliert nur auf ausdrücklichen Aufruf. Die tägliche QMD-Wartung aktualisiert Suchdaten, aber keine Wiki-Aussagen. Der Mac braucht einen bestehenden, nachvollziehbaren Auslöser und einen Katalog der künftigen Agent-Einstiege.

## What Changes

- Bestehende lokale Automation `update-qmd-index-daily` um Wiki-Pflege vor QMD update/embed erweitern; Zeitplan und Modell beibehalten.
- Allgemeine und private Quellen in einem gemeinsamen Wiki zusammenführen; „privat“ als Tätigkeitsbereich statt Zugriffsgrenze behandeln und Synthesen nach fachlicher Relevanz bilden.
- Begrenzte Pflegefehler isolieren und unabhängige Arbeit mit sichtbarem Teilfehlerbericht fortsetzen.
- Einen ausführbaren Wartungshelfer mit expliziten Kontextkonfigurationen, serieller Ausführung, überprüften Ergebnissen und dauerhaften Laufartefakten bereitstellen.
- Betriebsanleitung und priorisierten Katalog tatsächlich vorhandener Skills, Repo-Einstiege und Kontextdateien liefern. Die flächendeckende Einführung der Retrieval-Verweise bleibt ein separater Umsetzungsschritt.

## Capabilities

### New Capabilities
- `contextual-wiki-operations`: Wiederkehrende lokale Pflege und überprüfbarer Einführungsplan.

### Modified Capabilities

- `contextual-llm-wiki`: Gemeinsamer Quellenbestand ohne Privatpartition, kontextbezogene repoübergreifende Synthesen und entsprechende Query-Nutzung. Der bestehende Compiler bleibt gesetzt.

## Impact

Bestehende Codex-Automation, `contextual-llm-wiki/scripts`, QMD-Wartungsreferenz und Betriebsdokumentation. Generierte Dateien bleiben außerhalb versionierter Fachquellen. Bestehende Fachautomationen werden nicht verändert. Quellenfilter, gemeinsame Ausgabe, vorhandene gespeicherte Synthesen und QMD-Routing müssen migriert werden. Der gemeinsame Gesamtbestand benötigt eine Erstkompilierung; Abnahmebestände dürfen nicht als Vollimport dargestellt werden.
