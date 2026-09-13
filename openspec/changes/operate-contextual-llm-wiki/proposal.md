## Why

Das akzeptierte Wiki kompiliert nur auf ausdrücklichen Aufruf. Die tägliche QMD-Wartung aktualisiert Suchdaten, aber keine Wiki-Aussagen. Der Mac braucht einen bestehenden, nachvollziehbaren Auslöser und einen Katalog der künftigen Agent-Einstiege.

## What Changes

- Bestehende lokale Automation `update-qmd-index-daily` um Wiki-Pflege vor QMD update/embed erweitern; Zeitplan und Modell beibehalten.
- Bestehende allgemeine/private Wissensbestände in den mit Ticket 01 bereitgestellten gemeinsamen Wiki-Vertrag migrieren.
- Den mit Ticket 03 akzeptierten Vertrag für begrenzte Pflegefehler im produktiven Betrieb aktivieren; die Implementierung selbst ist separat abgeschlossen.
- Einen ausführbaren Wartungshelfer mit expliziten Kontextkonfigurationen, serieller Ausführung, überprüften Ergebnissen und dauerhaften Laufartefakten bereitstellen.
- Betriebsanleitung und priorisierten Katalog tatsächlich vorhandener Skills, Repo-Einstiege und Kontextdateien liefern. Die flächendeckende Einführung der Retrieval-Verweise bleibt ein separater Umsetzungsschritt.

## Capabilities

### Modified Capabilities
- `contextual-wiki-operations`: Produktive Aktivierung der wiederkehrenden lokalen Pflege und überprüfbarer Einführungsplan. Der Ticket-03-Vertrag wird separat kanonisch abgeschlossen.

### Bereits abgeschlossene Voraussetzung

Der Ticket-01-Anteil `contextual-llm-wiki` ist unter [share-contextual-wiki-sources](../archive/2026-09-13-share-contextual-wiki-sources/proposal.md) abgeschlossen und in die kanonische Wiki-Spec übernommen. Dieser aktive Change besitzt ausschließlich das verbleibende Betriebs-Delta.

## Impact

Bestehende Codex-Automation, `contextual-llm-wiki/scripts`, QMD-Wartungsreferenz und Betriebsdokumentation. Generierte Dateien bleiben außerhalb versionierter Fachquellen. Bestehende Fachautomationen werden nicht verändert. Quellenfilter, gemeinsame Ausgabe, vorhandene gespeicherte Synthesen und QMD-Routing müssen migriert werden. Der gemeinsame Gesamtbestand benötigt eine Erstkompilierung; Abnahmebestände dürfen nicht als Vollimport dargestellt werden.


### Bereits abgeschlossener Ticket-03-Anteil

Der akzeptierte Fehler-/Wiederaufnahmevertrag ist unter [continue-contextual-wiki-maintenance](../archive/2026-09-13-continue-contextual-wiki-maintenance/proposal.md) abgeschlossen. Dieser aktive Change behält Migration, Live-Aktivierung und Vollimport; kein Ticket-03-Requirement bleibt hier als unerfülltes Delta dupliziert.

### Bereits abgeschlossener Release-Ticket-01-Anteil

Die akzeptierte Kandidateninstallation/-qualifikation ist unter [qualify-upstream-wiki-releases](../archive/2026-09-13-qualify-upstream-wiki-releases/proposal.md) abgeschlossen und in `contextual-wiki-operations` kanonisch übernommen. Dieser Change behält automatische Release-Erkennung und die offenen Wissenspflegeaufgaben.

### Bereits abgeschlossener Release-Ticket-02-Anteil

Aktivierung/Rollback ist unter [activate-qualified-wiki-releases](../archive/2026-09-13-activate-qualified-wiki-releases/proposal.md) abgeschlossen und in `contextual-wiki-operations` kanonisch übernommen.
