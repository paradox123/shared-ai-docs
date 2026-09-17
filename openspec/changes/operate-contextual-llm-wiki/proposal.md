## Why

Das akzeptierte Wiki kompiliert nur auf ausdrücklichen Aufruf. Die tägliche QMD-Wartung aktualisiert Suchdaten, aber keine Wiki-Aussagen. Der Mac braucht einen bestehenden, nachvollziehbaren Auslöser und einen Katalog der künftigen Agent-Einstiege.

Ergaenzung vom 17.09.2026: Der inzwischen aktivierte gemeinsame Erstimport kann mehrere Stunden laufen und wurde noch nicht vollstaendig abgeschlossen. Die Kopplung an seinen Erfolg blockiert auch die Fachquellen-Indexpflege. Das bestaetigte Ziel trennt die Aktualitaet der Originalquellensuche von der Wiki-Aufbereitung und priorisiert laufende Aenderungen vor dem Erstimport-Rueckstand; siehe [ADR 0016](../../../docs/adr/0016-decouple-source-index-freshness-from-wiki-compilation.md).

Die umsetzbare [Tracker-Spec zur wiederaufnehmbaren Wiki-Pflege](../../../.scratch/resumable-wiki-maintenance/spec.md) ist mit `Status: ready-for-agent` veroeffentlicht. Sie konkretisiert dieses Betriebs-Delta mit User Stories, Umsetzungsannahmen und Abnahme ueber Wartungshelper und WikiQuery; die Ticketzerlegung steht noch aus.

## What Changes

- Bestehende lokale Automation `update-qmd-index-daily` fuer unabhaengige Fachquellen-Indexpflege und schrittweise Wiki-Pflege weiterentwickeln; Zeitplan und Modell beibehalten. Neue und geaenderte Quellen erhalten Vorrang und sollen spaetestens am naechsten Tag im Wiki verarbeitet sein; der Erstimport darf mehrere Tage dauern.
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
