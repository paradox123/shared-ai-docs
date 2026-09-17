# 04: Tagesaenderungen vor dem Erstimport verarbeiten

Status: closed

**Parent:** [Wiederaufnehmbare Wiki-Pflege](../spec.md)

**What to build:** Neue und geaenderte Fachquellen werden waehrend eines mehrtaegigen Erstimports bevorzugt in vollstaendig geprueften Arbeitspaketen ins Wiki uebernommen. Der Operator erkennt Tagesfortschritt, alten Rueckstand und verpasste Aktualitaetsziele getrennt. Kleine Laeufe duerfen den gemeinsamen Wissensbestand nicht kuenstlich in unabhaengige Teilwikis zerlegen.

**Blocked by:** 03 — Pflegelaeufe begrenzen und Fortschritt sichtbar machen.

**Spec coverage:** User Stories 7–11, 15–16, 22–24; Implementation Decisions 3–4, 6, 8, 11.

- [ ] Ein persistiertes Ausgangsinventar unterscheidet Erstimport-Rueckstand von spaeter neu eintreffenden oder geaenderten Quellen. Ein unveraenderter erneuter Scan setzt weder Einordnung noch Alter offener Arbeit zurueck.
- [ ] Eine neue Tagesquelle wird bei bestehendem Erstimport-Rueckstand vorrangig verarbeitet. Eine geaenderte, bisher noch unkompilierte Erstimportquelle erhaelt dieselbe Tagesprioritaet.
- [ ] Ein begrenzter Lauf kann ein vollstaendig geprueftes Tagespaket veroeffentlichen, waehrend weiterer Erstimport offen bleibt. WikiQuery findet die neue aktuelle Aussage mit verifizierten Originalreferenzen.
- [ ] Quellenuebergreifende Konzepte und gespeicherte Antworten erhalten alle benoetigten Abhaengigkeitspruefungen. Unbekannte Abhaengigkeiten blockieren betroffene Veroeffentlichungen; Paketgrenzen rechtfertigen keine unvollstaendige Synthese.
- [ ] Die Arbeitspaketwahl erhaelt den gemeinsamen Pflegeumfang und verwendet die in Ticket 03 eingefuehrten Grenzen sowie die Wiederverwendung aus Ticket 02.
- [ ] Tagesprioritaet und Erstimport-Fortschritt sind gemeinsam nachgewiesen. Ein dokumentiertes Verfahren verhindert dauerhafte Verdraengung des Rueckstands; unzureichende Kapazitaet wird sichtbar und nicht durch stilles Aufgeben der Tagesprioritaet verdeckt.
- [ ] Neue und geaenderte Quellen haben das bestaetigte Ziel der Wiki-Verarbeitung spaetestens am naechsten Tag in Europe/Berlin. Eine kontrollierte Zeitpruefung weist offene ueberfaellige Aenderungen aus; unbekannte Aenderungszeiten werden nicht erfunden.
- [ ] Bestaetigte Entfernungen und unvollstaendige Scans behalten ihre bestehenden Sperr-/Fehlerregeln. Alte Aussagen werden nicht durch neue Statusmetadaten scheinbar aktuell.
- [ ] Der Bericht unterscheidet laufende Nachpflege, Fristverletzungen, Erstimport-Rueckstand und Gesamtabschluss. Tageserfolg allein setzt nicht den vollstaendigen Pflegezeitpunkt eines noch offenen Gesamtbestands.
- [ ] Nach mehreren kurzen Laeufen kann der begrenzte Testbestand vollstaendig abgeschlossen werden; ein unveraenderter Folgeaufruf benoetigt keine Modellarbeit.

**Verification:** Oeffentlichen Helper wiederholt gegen ein dauerhaftes isoliertes Testinventar ausfuehren, zwischen Laeufen neue/geaenderte Quellen einbringen und die Auswahl ueber beobachtete Provideranfragen sowie veroeffentlichte WikiQuery-Ergebnisse nachweisen. Gemeinsame Konzepte aus mindestens zwei Fachrepos, ein unabhaengiges Kontrollthema, Restarbeit und eine kontrollierte Fristverletzung abdecken.

**Boundary:** Dieses Ticket prueft Veroeffentlichung begrenzter Pakete bei stabilen Quellen. Das gezielte Verhalten bei Quellenabweichung waehrend eines laufenden Pakets folgt in Ticket 05. Bestehende Aktualitaetssperren bleiben bis dahin konservativ wirksam. Keine Aenderung an Tageszeit, Modell, Quellenumfang oder Live-Automation.

## Implementierungsnachweis

Ticket 04 wurde nach separater kritischer Verifikation und Koordinator-Abnahme am 17.09.2026 mit [PR #8](https://github.com/paradox123/shared-ai-docs/pull/8) nach `main` geliefert. Verifizierter Merge: [`e7cdde429ebc450edc24858ee7a8ab514088fc97`](https://github.com/paradox123/shared-ai-docs/commit/e7cdde429ebc450edc24858ee7a8ab514088fc97). Alle 17 akzeptierten Dateihashes des Inhaltsmanifests `c100ea0c3c9772b9da8e4f2e7351c70ba96347d6c0a963211a23029dce89e7d3` wurden am Remote-Merge bestätigt. [Gemessene Ergebnisse, kritische Gegenfälle, konkrete dauerhafte Rohbelege und Grenzen](../../../contextual-llm-wiki/evidence/resumable-maintenance-04.md). Tickets 05–06 und die produktive Aktivierung bleiben offen; der gemeinsame OpenSpec-Change wird nicht archiviert.
