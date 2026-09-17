## 1. Betrieb
- [x] 1.1 Bestehende Session, Spec, Konfiguration und Automation prüfen.
- [x] 1.2 Wartungshelfer über öffentliche Prozessgrenze mit Rot→Grün-Slices implementieren.
- [x] 1.3 Echten begrenzten Wiki-/QMD-Lauf einschließlich No-op nachweisen.
- [x] 1.4 Bestehende Automation aktualisieren und gespeicherte Definition prüfen.

## 1a. Pflegefortschreibung vom 17.09.2026

Dieser Abschnitt ergaenzt den bisherigen Betriebsstand; abgeschlossene Implementierungen unten belegen noch nicht das hier beschlossene Zielverhalten.

- [x] Aktualitaetsziel und unabhaengige Fachquellen-Indexpflege im Interview klaeren; Glossar, ADR 0016, Proposal, Design und Requirement-Delta abgleichen.
- [x] [Umsetzbare Spec](../../../.scratch/resumable-wiki-maintenance/spec.md) im lokalen Tracker als `ready-for-agent` veroeffentlichen, einschliesslich Testgrenzen, Abnahmeszenarien und Scope.
- [x] Fachquellen-Indexpflege von erfolgreicher Wiki-Generierung entkoppeln und ueber WikiQuery den gekennzeichneten Rueckgriff auf aktuelle Originale bei ausstehender oder fehlgeschlagener Generierung nachweisen.
- [x] Validierte Extraktionen außerhalb des Publikations-Stagings dauerhaft sichern; kompatible Arbeit nach echtem Prozessneustart wiederverwenden und lokale Invalidierung verifizieren (Ticket 02, Evidenz wird separat abgenommen).
- [x] Laufende Aenderungen vor Erstimport-Rueckstand priorisieren; dauerhaft wiederverwendbare Zwischenstaende und begrenzte Arbeitseinheiten umsetzen. Neustart darf unveraenderte erfolgreiche Extraktionen nicht erneut ausfuehren.
- [x] Fortschritt, Fehler, kontrolliertes Laufende und Wiederaufnahme ueber die oeffentliche Prozessgrenze pruefen; keine unbegrenzte agentische Warteschleife. Abhaengige Modellarbeit bei gemeinsamem Providerfehler stoppen (Ticket 03: isolierte Umsetzung; separate Batch-Abnahme vor Integration).
- [x] Quellenaenderung waehrend der Verarbeitung, stale Wiki-Evidenz, gemeinsam genutzte Konzepte, Indexfehler, verpasste Tagesfrist und anschliessenden No-op isoliert verifizieren; nur nachweislich gueltige Ergebnisse wiederverwenden oder veroeffentlichen.
- [ ] Live-Prompt, QMD-Wartungsreferenz und Betriebsanleitung nach Implementierung konsistent aktualisieren; Produktivabnahme mit separaten Ergebnissen fuer Suchindex, Tagesaenderungen und Erstimport dokumentieren.
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


[Abnahme Wiederaufnehmbare Pflege, Ticket 01](../../../contextual-llm-wiki/evidence/resumable-maintenance-01.md): unabhängiger Originalquellenindex, verifiziertes WikiQuery-Fallback, explizite Quellenbegrenzung, Scan-/Indexfehler und unveränderter No-op isoliert umgesetzt. Andere Schritte des neuen Sechs-Ticket-Batches sowie Live-Aktivierung und produktive Gesamtabnahme bleiben offen; Change nicht archivieren.

[Ticket 03: begrenzte Pflege](../../../contextual-llm-wiki/evidence/resumable-maintenance-03.md) ergänzt endlichen Helper-/Prozessbesitz, Fortschritt und Provider-Gates. Live-Aktivierung, Tagespriorität und produktive Gesamtabnahme bleiben offen; Change nicht archivieren.

[Ticket 04: Tagespakete](../../../contextual-llm-wiki/evidence/resumable-maintenance-04.md) ergänzt persistentes Ausgangsinventar, priorisierte begrenzte Extraktion, explizit quellgebundene Zwischenpublikation und getrennte Berliner Frist-/Rückstandsberichte. Globale Synthese bleibt bis zur gemeinsamen Abhängigkeitsprüfung offen. Isolierte Umsetzung und Gegenproben sind dokumentiert; separate Batch-Abnahme, Driftisolation (05), Live-Aktivierung und produktive Gesamtnachweise bleiben offen. Nicht archivieren.

[Ticket 05: Driftisolation](../../../contextual-llm-wiki/evidence/resumable-maintenance-05.md) prüft Originalversionen vor wartender Cachewiederverwendung und vor Publikation. Unbekannte aktuelle Konzeptzugehörigkeit sperrt gemeinsame Synthesen samt Antwortketten; die bestehende quellgebundene Einheit erhält nachweisbar unabhängige Veröffentlichung und unveränderte gültige Quellantworten. Wiederaufnahme, tatsächliche Providerrequests und Indexreparatur sind isoliert geprüft. Separate Batch-Abnahme und produktive Nachweise bleiben offen; nicht archivieren.


## Ticket06: zweistufige Aktivierung

- [x] Einmaligen Runner mit eigener endlicher Beobachtung, dauerhaften Prozess-/Exit-/Diagnoseartefakten und Nicht-Erfolg bei fehlendem Abschluss isoliert umsetzen.
- [x] Vorgängerverhalten gemeinsam über öffentlichen Helper, echte isolierte QMD-Suche und WikiQuery prüfen; Grenzen und kanonischen Prompt mit Betriebsreferenzen abgleichen.
- [ ] Nach Code-Merge gesicherte produktive Bereitstellung und unveränderte Automationdefinition über vorgesehenes Tool aktivieren/zurücklesen; kontrollierten Produktivlauf mit getrennten Dimensionen abnehmen.
- [ ] Tatsächlichen nachfolgenden täglichen Schedulerlauf anhand seiner Artefakte nachweisen (späteres externes Ereignis).
- [ ] Mehrtägigen produktiven Erstimport und anschließenden No-op separat nachweisen (späteres externes Ereignis).

[Ticket06-Nachweis](../../../contextual-llm-wiki/evidence/resumable-maintenance-06.md) trennt die Stufen. Kein Archiv vor tatsächlicher Gesamtabnahme.
