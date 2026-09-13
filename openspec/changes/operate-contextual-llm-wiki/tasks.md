## 1. Betrieb
- [x] 1.1 Bestehende Session, Spec, Konfiguration und Automation prüfen.
- [x] 1.2 Wartungshelfer über öffentliche Prozessgrenze mit Rot→Grün-Slices implementieren.
- [x] 1.3 Echten begrenzten Wiki-/QMD-Lauf einschließlich No-op nachweisen.
- [x] 1.4 Bestehende Automation aktualisieren und gespeicherte Definition prüfen.
## 2. Einführung und Abnahme
- [x] 2.1 Tatsächliche Skills und Kontextdateien priorisiert katalogisieren.
- [x] 2.2 Betriebsanleitung und unmittelbare Wartungsreferenzen aktualisieren.
- [x] 2.3 Tests, strikte OpenSpec-Validierung und Abnahmeübersicht vervollständigen.

[Abnahme und Grenzen](acceptance.md): Ablauf real verifiziert, Automation aktiv. Vollständiger Erstimport und tatsächlicher nächster Schedulerlauf noch ausstehend; kein Archivieren.

## 3. Betriebsregeln nach Nutzerkorrektur schärfen
- [x] 3.1 `private` und `Projects/Private` als reguläre Fachquellen im gemeinsamen Pflegeumfang bestätigen.
- [x] 3.2 Interview abschließen: Tätigkeitsbereich statt Zugriffsgrenze, fachliche Relevanz und isolierte Teilfehler dokumentieren.
- [x] 3.3 Glossar, ADR 0010, bestehende Quellen-/Retrieval-Requirements und Einführungskatalog auf das gemeinsame Wiki ausrichten.

## 4. Bestätigtes Modell umsetzen
- [x] 4.1 Quellenpartition und bisherige Privacy-Szenarien durch gemeinsame Wissensbildung und explizite Aufgabenbegrenzung ersetzen; Rot→Grün über die öffentliche CLI.
- [x] 4.2 Bestehende Wissensseiten und gespeicherte Synthesen sichern und samt überprüfter Provenienz in gemeinsamen Zustand/Ausgabe überführen; keine stillen Überschreibungen oder Verluste.
- [x] 4.3 Gemeinsames QMD-Routing ohne aus dem Domainnamen abgeleitete Ausschlüsse herstellen; betroffene kanonische Retrieval-Regeln abgleichen.
- [x] 4.4 Begrenzte Pflegefehler isolieren, sichere unabhängige Arbeit fortsetzen und echte Teilfehlerberichte nachweisen.
- [x] 4.5 Live-Job und Betriebsreferenzen auf die gemeinsame Konfiguration umstellen; bisherigen Zeitplan beibehalten.
- [ ] 4.6 Echte gemeinsame Synthese aus persönlichem und anderem Tätigkeitsbereich, Relevanzkontrolle, Quelle–Antwort-Nachpflege, Vollimport und No-op prüfen; Abnahme aktualisieren.

[Ticket-01-Abnahme](../../../contextual-llm-wiki/evidence/shared-wiki-01.md): gemeinsame Quellen-/Query-Funktion und QMD-Routing isoliert verifiziert, einschließlich echter repoübergreifender Konzeptseite, Relevanzkontrolle, expliziter transitiver Grenzen, Aktualitätsprüfung und No-op. Damit ist der begrenzte Synthese-/Query-Anteil aus 4.6 nachgewiesen; 4.6 bleibt wegen Vollimport und produktiver Abnahme offen. 4.2 ist mit Ticket 02 und 4.4 mit Ticket 03 verifiziert; 4.5 und die produktive Abnahme gehören zu Ticket 04. Bestehende getrennte Ausgaben und Live-Job wurden nicht umgestellt; nicht archivieren.


## Akzeptierter Abschluss von Ticket 01

Daniel hat Ticket 01 am 13.09.2026 ausdrücklich akzeptiert und Abschluss, Commit und Push beauftragt. Sein Wiki-Delta wurde in [share-contextual-wiki-sources](../archive/2026-09-13-share-contextual-wiki-sources/proposal.md) separat abgeschlossen und kanonisch übernommen.

[Ticket-02-Abnahme](../../../contextual-llm-wiki/evidence/shared-wiki-02.md): sechs reale Altbestände inventarisiert, 211 Dateien gesichert und geprüft; 30 gültige Seiten einschließlich einer bytegleichen gespeicherten Antwort gemeinsam übernommen, 36 identische Revisionen zugeordnet und 18 veraltete Revisionen zurückgestellt. Echte Query, gemeinsames QMD inklusive acht persönlichen Seiten und No-op verifiziert. Antwortketten, Quellenkorrektur, Namenskollisionen und sichere Wiederaufnahme über die öffentliche CLI geprüft. Task 4.2 ist umgesetzt.

[Ticket-03-Abnahme](../../../contextual-llm-wiki/evidence/bounded-failures-03.md): Begrenzte Fehler, transitive Sperren, unabhängige Veröffentlichung/QMD-Aktualisierung, strikte Helper-Verträge, Reparatur und No-op über die öffentliche CLI verifiziert. Task 4.4 ist umgesetzt. Der Live-Job wurde nicht umgestellt; Aufgabe 4.5 und der Produktionsanteil von 4.6 bleiben offen.

## Akzeptierter Abschluss von Ticket 03

Daniel hat Ticket 03 am 13.09.2026 ausdrücklich akzeptiert und Abschluss, Commit und Push beauftragt. Das erfüllte Requirement ist in [continue-contextual-wiki-maintenance](../archive/2026-09-13-continue-contextual-wiki-maintenance/proposal.md) separat archiviert und kanonisch übernommen. Live-Aktivierung und Vollimport bleiben in diesem Change offen.

## 4.7 Ergänzung zum Agentenzugang
- [x] WikiQuery als Standard-Kontextzugang zentral verankern und im Agentenablauf nachweisen; vorhandene Quellenbegrenzung und Primärquellenprüfung beibehalten.


## 5. Ergänzung: Upstream-Stand lokal übernehmen
- [x] 5.1 Umfang korrigieren: LLM Wiki als Ganzes mit seinen upstream festgelegten Abhängigkeiten übernehmen; keine eigenständigen Library-Updates. Automatische Übernahme nach erfolgreichem Build und erforderlichen Tests bleibt bestätigt.
- [ ] 5.2 Veröffentlichte Releases erkennen und samt Integrationsprüfung übernehmen; falls Renovate verwendet wird, ausschließlich die Upstream-Referenz aktualisieren und automatisch mergen. Unveränderte Upstream-Revision trotz neuer Library-Version sowie Blockade bei fehlenden oder fehlgeschlagenen Prüfungen verifizieren.
- [ ] 5.3 Reproduzierbare lokale Installation der Upstream-Revision mit ihrer Lockdatei einschließlich Aktivierungsprüfung und Rückkehr zur bisherigen Installation umsetzen.

Wissenspflege und Schedulerwechsel sind auf Nutzerwunsch für eine andere Session zurückgestellt. Offene Punkte aus Abschnitt 4 bleiben erhalten und werden in dieser Session nicht weiter umgesetzt. Die Live-Pflegeautomation bleibt unverändert.

- [x] 5.4 Kanal „veröffentlichte Releases“ bestätigen und drei freigegebene [Umsetzungstickets](../../../.scratch/update-llm-wiki-releases/spec.md) mit Abhängigkeiten 01 → 02 → 03 veröffentlichen.

[Ticket-04-Zwischenstand](../../../contextual-llm-wiki/evidence/production-04.md): bestehender Live-Job auf gemeinsame Konfiguration umgestellt, Einstellungen erhalten; WikiQuery-first in zentralen Skills und tatsächlichem Agentenablauf samt aktuellem Quellen-Fallback nachgewiesen. Vollimport und produktive Gesamtabnahme (4.6) sind wegen wiederholter paralleler Originalquellenänderungen blockiert; Meetings-Verbleib ist offen. Keine Archivierung.

## 6. Release-Ticket 01: Kandidat installieren und prüfen
- [x] 6.1 Compiler-Release-Definition vereinheitlichen und bisherige CLI-Prüfung nachweisen.
- [x] 6.2 Öffentlichen Kandidatenaufruf mit Release-Nachweis, exaktem Commit, unveränderten Lock-Eingängen und isolierter Installation testgetrieben umsetzen.
- [x] 6.3 Build-/Integrationspflichtprüfungen und nicht erfolgreiche Fehlerberichte an den Kandidaten binden.
- [ ] 6.4 Echten erfolgreichen und gezielt fehlschlagenden Aufruf nachweisen; Abnahme, Tests und Review dokumentieren.

5.2/5.3 bleiben wegen Erkennung, Aktivierung und Rollback der Folgetickets offen.
