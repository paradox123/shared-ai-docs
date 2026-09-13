# Gemeinsame Integration auf main — 2026-09-13

Auf Benutzerauftrag werden Issue 11 und die Wiki-Tickets 01, 02 und 03 gemeinsam
in `main` integriert. Lokale uncommittete Entwürfe sind im Stash
`f3175e13a2ea3fd28797b89751d7bf378e1410cd` gesichert und werden mit den aktuellen
Abschlussständen abgeglichen; sie gehören nicht zu den hier akzeptierten Features.

## Konfliktauflösung

- Die Pflege übernimmt Migrationsidentitäten, Journale und Titel/Fallback-Fragen
  aus Ticket 02 sowie Fehlerisolation und Publikationsversion 2 aus Ticket 03.
- Die erste gemeinsame Regression zeigte, dass frische Migrationen noch Version 1
  markierten. Die folgende Pflege erzeugte dadurch unabhängige importierte
  Antworten unnötig neu. Frische Ziele haben keinen alten Compiler-Kontext und
  erhalten nach Abhängigkeitsprüfung Version 2. Alter Compiler-Kontext wird
  weiterhin einmal neu aufgebaut.
- Der Reparaturtest prüft, dass eine Antwort nicht zurückgezogen ist; sowohl ein
  fehlendes Flag als auch `withdrawn:false` erfüllen dieses öffentliche Verhalten.
- Der Parallelitätstest hält die kontrollierte HTTP-Providerantwort bis nach
  konkurrierendem Schreibversuch und Quellenänderung zurück. Damit hängt der
  Nachweis nicht mehr von einem 500-ms-Zeitfenster ab.
- OpenSpec-Aufgaben und Abnahmevermerke behalten die abgeschlossenen Tickets 02
  und 03 sowie die weiterhin offene Produktionsaktivierung aus Ticket 04.

## Verhalten und Verifikation

Die vier zunächst fehlgeschlagenen Fälle bestehen nach der Korrektur über die
öffentliche CLI: importierte unabhängige Antwort bleibt bytegleich; frische
Migration erfordert keine Modellkompilierung; fehlerhafte Antwort wird repariert;
paralleler Schreiber wird abgelehnt und geänderte Quelle bleibt bis zur Wiederholung
offen. [Gezielte Regression](main-integration-recheck.txt).

Die vollständigen abschließenden Prüfläufe sind in den begleitenden Protokollen
festgehalten. Die vorhandenen Upstream-Patchdateien enthalten formatbedingt leere
Kontextzeilen mit einem einzelnen Leerzeichen; der Diff-Whitespace-Check lässt
Patchdateien deshalb aus. Ihre tatsächliche Anwendung und Compiler-Tests werden
separat geprüft. Es wird kein Produktivimport oder Schedulerwechsel durchgeführt.

## Abschließendes Ergebnis

- [Wiki-Check](main-integration-wiki-check.txt): TypeScript erfolgreich; 59 CLI-
  Verhaltenstests, 59 Upstream-Tests und acht Betriebs-Tests bestanden.
- [Publication-Regression](main-integration-publication-check.txt): alle 25 Tests
  nach der Integration auf main bestanden.
- [OpenSpec](main-integration-openspec-check.txt): alle 48 Specs/Changes bestanden.
- Der begrenzte Diff-Check ist grün; die tatsächliche Patch-Anwendung wurde beim
  Bootstrap und über die Upstream-Tests geprüft.
