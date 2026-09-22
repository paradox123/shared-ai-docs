# Korrektur der täglichen Wiki-Kapazität, 22.09.2026

## Ursache und Änderung

Der produktive Lauf `20260922T074617-56667` beendete die Pflege nach 1201,244 Sekunden mit `budget-exhausted`. Obwohl acht Anfragen konfiguriert waren, erzwang `maintenance.ts` bei einem größeren Inventar als dem Extraktionspaket eine Parallelität von eins. Das erhöhte Paketlimit von 250 allein änderte daran nichts: 49 Extraktionen wurden gespeichert, die anschließenden Veröffentlichungsschritte nicht abgeschlossen.

Begrenzte Pakete verwenden nun die konfigurierte Parallelität. Reservierte Plätze für priorisierte Tagesquellen und den Erstimport werden vor asynchronen Cachezugriffen festgelegt; Reparaturen früherer Extraktionen dürfen nur unreservierte Plätze nutzen. Das harte Paketmaximum und die vorhandenen Schreib-/Prozesssperren bleiben wirksam.

Die bestehende aktive tägliche Automation um 07:00 Uhr verwendet lokal maximal 2500 neue Extraktionen, acht parallele Modellanfragen und ein endliches Zeitbudget von drei Stunden. Modell, Projekt und vollständige Quellenauswahl bleiben erhalten. Bestehende Ergebnisse werden wiederverwendet. Die Anzahl früher zurückkehrender Prozessabfragen beendet die Beobachtung nicht mehr vor der absoluten Zeitgrenze.

## Nachweise

- Neue Regression über die öffentliche `maintain`-CLI: acht Testquellen, Paket vier, konfigurierte Parallelität drei. Vorher beobachtete Parallelität eins (rot); nachher drei, genau vier neue Anfragen und vier dauerhaft gespeicherte Ergebnisse. Nächster Prozess vervollständigt Synthese; unveränderter Folgelauf ist No-op ohne Modellanfragen.
- 30 gezielte Tests zu Budget, Priorität, Quellenänderungen und Veröffentlichung: 29 bestanden im gemeinsamen Lauf. Ein zeitabhängiger Test erreichte unter paralleler Last seine angehaltene QMD-Testphase nicht; der unveränderte Einzeltest bestand. Keine Abschwächung dieses Tests.
- TypeScript-Prüfung, 14 Python-Tests für Laufsteuerung, strikte OpenSpec-Validierung und Diff-Prüfung bestanden.
- Produktive Konfiguration unter beiden vorhandenen Sperren geschrieben. Automation über das App-Werkzeug aktualisiert und gegen den kanonischen Prompt zurückgelesen (bis auf abschließenden Zeilenumbruch identisch).

Die lokalen Detailnachweise einschließlich Inhaltsmanifest und unabhängiger Reviewbelege liegen in `.local/repair-20260922/`. Sie enthalten keine Freigabe für Commit, Push oder Archivierung.

## Offene Ergebnisprüfung

Die Tests verwenden den echten Compiler und isolierte echte QMD-Datenbanken mit einem kontrollierten Modellprovider. Sie beweisen keine abgeschlossene Verarbeitung des gesamten Produktivbestands. Produktiver Vollimport, gemeinsame Synthese, anschließender No-op sowie der nächste tatsächliche Schedulerlauf müssen anhand ihrer eigenen Laufartefakte bestätigt werden. Ein gestarteter Nachhollauf ist kein vollständiger Wiki-Erfolg.
