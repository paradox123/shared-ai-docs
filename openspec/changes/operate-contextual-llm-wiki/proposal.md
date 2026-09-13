## Why

Das akzeptierte Wiki kompiliert nur auf ausdrücklichen Aufruf. Die tägliche QMD-Wartung aktualisiert Suchdaten, aber keine Wiki-Aussagen. Der Mac braucht einen bestehenden, nachvollziehbaren Auslöser und einen Katalog der künftigen Agent-Einstiege.

## What Changes

- Bestehende lokale Automation `update-qmd-index-daily` um Wiki-Pflege vor QMD update/embed erweitern; Zeitplan und Modell beibehalten.
- Bestehende allgemeine/private Wissensbestände in den mit Ticket 01 bereitgestellten gemeinsamen Wiki-Vertrag migrieren.
- Begrenzte Pflegefehler isolieren und unabhängige Arbeit mit sichtbarem Teilfehlerbericht fortsetzen.
- Einen ausführbaren Wartungshelfer mit expliziten Kontextkonfigurationen, serieller Ausführung, überprüften Ergebnissen und dauerhaften Laufartefakten bereitstellen.
- Betriebsanleitung und priorisierten Katalog tatsächlich vorhandener Skills, Repo-Einstiege und Kontextdateien liefern. Die flächendeckende Einführung der Retrieval-Verweise bleibt ein separater Umsetzungsschritt.

## Capabilities

### New Capabilities
- `contextual-wiki-operations`: Wiederkehrende lokale Pflege und überprüfbarer Einführungsplan.

### Bereits abgeschlossene Voraussetzung

Der Ticket-01-Anteil `contextual-llm-wiki` ist unter [share-contextual-wiki-sources](../archive/2026-09-13-share-contextual-wiki-sources/proposal.md) abgeschlossen und in die kanonische Wiki-Spec übernommen. Dieser aktive Change besitzt ausschließlich das verbleibende Betriebs-Delta.

## Impact

Bestehende Codex-Automation, `contextual-llm-wiki/scripts`, QMD-Wartungsreferenz und Betriebsdokumentation. Generierte Dateien bleiben außerhalb versionierter Fachquellen. Bestehende Fachautomationen werden nicht verändert. Quellenfilter, gemeinsame Ausgabe, vorhandene gespeicherte Synthesen und QMD-Routing müssen migriert werden. Der gemeinsame Gesamtbestand benötigt eine Erstkompilierung; Abnahmebestände dürfen nicht als Vollimport dargestellt werden.
