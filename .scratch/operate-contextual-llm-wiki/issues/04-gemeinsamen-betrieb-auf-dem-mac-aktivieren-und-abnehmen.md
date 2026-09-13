# 04: Gemeinsamen Betrieb auf dem Mac aktivieren und abnehmen

**What to build:** Daniels bestehender täglicher Pflegejob hält den vollständigen gemeinsamen Wiki-Bestand und QMD aktuell. Übernommenes Wissen bleibt erhalten, passende persönliche und berufliche Quellen werden gemeinsam nutzbar, und Betrieb sowie offene Fehler sind nachvollziehbar dokumentiert.

**Blocked by:** 02 — Bestehende Wissensbestände verlustfrei zusammenführen; 03 — Pflege bei begrenzten Fehlern fortsetzen.

**Status:** ready-for-agent

## Grundlage und Ausgangslage

Maßgeblich sind der OpenSpec-Change [operate-contextual-llm-wiki](../../../openspec/changes/operate-contextual-llm-wiki/proposal.md), sein [Design](../../../openspec/changes/operate-contextual-llm-wiki/design.md), die [Betriebs-Requirements](../../../openspec/changes/operate-contextual-llm-wiki/specs/contextual-wiki-operations/spec.md), die [kanonischen Wiki-Requirements](../../../openspec/specs/contextual-llm-wiki/spec.md) und [ADR 0010](../../../docs/adr/0010-shared-wiki-across-personal-and-professional-domains.md).

Die aktive Automation `update-qmd-index-daily` läuft lokal täglich um 07:00 Uhr mit den bereits konfigurierten Modell-, Projekt- und Benachrichtigungseinstellungen. Sie verwendet bisher nur die allgemeine Konfiguration. Die bisherigen echten Durchläufe betrafen einen begrenzten Abnahmebestand und belegen keinen Vollimport. Ticket 01 ist über die beiden direkten Vorgänger bereits Voraussetzung.

## Abnahmekriterien

- [ ] Die bisherige Definition und die abzulösenden Wissensbestände sind gesichert; der überprüfte Übernahmebericht aus Ticket 02 liegt vor. Gespeicherte Synthesen werden beim Erstimport nicht überschrieben oder verloren.
- [ ] Die bestehende Automation wird auf die gemeinsame Produktionskonfiguration umgestellt. Zeitplan, Modell, Projekt und Benachrichtigungseinstellungen bleiben erhalten; es entsteht kein zweiter Job oder Watcher.
- [ ] Der tatsächliche Produktionseingang umfasst alle acht ausgewählten Repo-Identitäten sowie Meetings und Projects einschließlich Projects/Private. Die Inventur weist vorhandene Quellen und Ausschlüsse aus; Abnahmefixtures ersetzen keinen Teil des Produktionsbestands.
- [ ] Ein vollständiger Produktionslauf mit echtem Provider, gepinntem Compiler und QMD wird abgeschlossen. Laufberichte, abgeschlossener Pflegezeitpunkt und offene Arbeit werden geprüft; Aktivierung oder erfolgreicher Start allein gelten nicht als Abnahme.
- [ ] Eine inhaltlich geprüfte Synthese verknüpft passende persönliche und andere Fachquellen, belegt diese und ist über die verwaltete Abfrage wiederverwendbar. Ein irrelevanter Kontrollbeleg wird nicht verwendet; ausdrücklich vorgegebene Aufgabengrenzen werden eingehalten.
- [ ] Eine nachvollziehbare Quellenänderung wird über Konzepte bis zu einer gespeicherten Antwort nachgepflegt. Ein anschließender unveränderter Lauf meldet No-op und benötigt keine neue Modellkompilierung.
- [ ] Der produktive Aufruf verwendet die in Ticket 03 verifizierte Teilfehlerbehandlung. Laufberichte und Automation-Memory unterscheiden vollständigen Erfolg von Teilfehlern; der genaue Artefaktpfad und verbleibende Arbeit sind auffindbar.
- [ ] Die Ausführung mit der tatsächlichen lokalen Runtime, vorhandener Provideranmeldung und reduziertem Scheduler-PATH ist überprüft. Fehlende Mac-/Runtime-Verfügbarkeit wird sichtbar gemeldet, ohne automatisierte Installations- oder TCC-Reparatur.
- [ ] Der gemeinsame Bestand ist über QMD und den vorhandenen menschlichen Wiki-Einstieg erreichbar. Frühere Wiki-Einstiege beziehungsweise Collections werden erst nach überprüfter Übernahme kontrolliert abgelöst, ohne fremde Collections anzutasten oder doppelte aktive Wissensbestände zu hinterlassen.
- [ ] Die unmittelbar betroffenen Betriebs- und kanonischen Retrieval-Anweisungen beschreiben den gemeinsamen Bestand und leiten aus `private` keine Zugriffssonderregel mehr ab. Der bestehende Einführungskatalog bleibt die Planung für weitere Repo-Einstiege; diese werden nicht pauschal ausgerollt.
- [ ] Eine neue Abnahmeübersicht dokumentiert je Requirement Erwartung, beobachtetes Verhalten und Evidence. Der tatsächliche manuelle Produktionsnachweis und ein eventuell noch ausstehender automatischer Schedulerlauf werden ausdrücklich unterschieden. Relevante Tests, strikte OpenSpec-Validierung und Diff-Prüfung bestehen.

## Umsetzung und Nachweis

Den vollständigen gemeinsamen Erstimport ausführen und bis zu einem überprüfbaren Abschluss verfolgen; seine Dauer ist kein Grund, ihn durch einen kleinen Testbestand zu ersetzen. Bei einem tatsächlichen Blocker die konkrete Ursache und den erreichten Stand dokumentieren, ohne eine vollständige Abnahme zu behaupten. Bereits bewiesene unveränderte Teilverhalten aus den Vorgängertickets gezielt wiederverwenden.

Dieser Auftrag umfasst die bestätigte lokale Betriebsumstellung. Fachquellen bleiben Eigentum ihrer Repos, QMD bleibt die einzige Retrieval-Engine und Merge oder Query lösen keine zusätzlichen Pflegejobs aus. Keine automatische externe Veröffentlichung, keine Änderungen an anderen Fachautomationen und keine vorzeitige Archivierung des Changes.

## Comments

- 13.09.2026: Aufteilung und Abhängigkeiten von Daniel bestätigt. Dieses Ticket aktiviert den korrigierten gemeinsamen Betrieb und liefert dessen neue Abnahme.
