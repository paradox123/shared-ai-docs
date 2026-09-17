# 05: Quellenänderungen waehrend der Pflege gezielt abfangen

Status: closed

**Parent:** [Wiederaufnehmbare Wiki-Pflege](../spec.md)

**What to build:** Aendert sich eine Fachquelle waehrend eines laufenden Arbeitspakets, bleiben die betroffenen Aussagen bis zur Nachpruefung gesperrt. Belegbar unabhaengige erfolgreiche Arbeit und Veroeffentlichungen gehen weiter und bleiben fuer Folgelaeufe erhalten. Gemeinsame Konzepte und Antwortketten verlieren dabei keine Abhaengigkeiten.

**Blocked by:** 04 — Tagesaenderungen vor dem Erstimport verarbeiten.

**Spec coverage:** User Stories 4, 12–16, 20, 24–25; Implementation Decisions 5–7, 9, 13.

- [ ] Der Vergleich relevanter Quellenversionen erfolgt vor Wiederverwendung und Veroeffentlichung des in Ticket 04 eingefuehrten Arbeitspakets. Drift entwertet betroffene Ergebnisse und ihre abhaengigen Aussagen.
- [ ] Eine gezielt waehrend der Generierung geaenderte Quelle verhindert nicht die Veroeffentlichung eines nachweisbar unabhaengigen Kontrollthemas. Der Bericht nennt die gesperrte Arbeit und behaelt ein Nicht-Erfolgsergebnis fuer offene angeforderte Arbeit.
- [ ] Ein gemeinsames Konzept aus mehreren Quellen und darauf beruhende gespeicherte Antworten werden transitiv geprueft. Die geaenderte Quelle darf nicht durch das ungeaenderte Fragment einer anderen Quelle scheinbar abgedeckt werden.
- [ ] Bei unbekannter Abhaengigkeit wird keine unabhaengige Veroeffentlichung behauptet. Sicher verwendbare Extraktionen bleiben dennoch gesichert; der naechste Prozess prueft deren Gueltigkeit erneut.
- [ ] Nach Korrektur verarbeitet ein Folgelauf nur fehlende, invalidierte oder fehlgeschlagene Arbeit samt benoetigter Abhaengigkeiten. Unbetroffene erfolgreiche Extraktionen werden nicht erneut beim Modell angefordert.
- [ ] Ein Quellenfehler, eine bestaetigte Entfernung und ein unvollstaendiger Scan erzeugen jeweils das passende Verhalten; keine stille Massenentfernung oder Wiederfreigabe alter Aussagen.
- [ ] Ein isolierter Antwortfehler sperrt dessen abhaengige Antwortkette; eine nicht betroffene gespeicherte Antwort bleibt inhaltlich unveraendert und auffindbar.
- [ ] Wiederaufnahme nach einem spaeteren Indexfehler behaelt gueltige gesicherte Arbeit, meldet den Index nicht faelschlich aktuell und fuehrt nach erfolgreicher Reparatur zum No-op ohne neue Modellaufrufe.
- [ ] WikiQuery liefert zu keinem Zeitpunkt eine als aktuell bestaetigte Aussage mit veralteten benoetigten Quellenstaenden. Fortschritt, Tagesfristen und Gesamtabschluss bleiben nach den Vertraegen der Vorgaengertickets unterscheidbar.

**Verification:** Den echten Helper in einem isolierten Test gezielt am kontrollierten Provider halten, eine Testquelle aendern und den Provider innerhalb einer kurzen Frist freigeben. Aktuelle Aussagen, gesperrte Abhaengigkeiten und unveraenderte Kontrollinhalte ueber WikiQuery pruefen. Danach einen neuen Prozess starten und Wiederverwendung ueber Provideranfragen nachweisen. Keine Last- oder Fehlerexperimente gegen Produktion.

**Boundary:** Baut auf der Veroeffentlichungs- und Prioritaetseinheit aus Ticket 04 auf; kein zweites Abhaengigkeitsmodell einfuehren. Konservative Sperren sind bei fehlender Evidenz korrekt. Originalquellen werden ausschliesslich innerhalb eigener Testfixtures geaendert. Live-Automation bleibt unveraendert.

## Abschluss

Implementierung und separate kritische Verifikation sind abgenommen und über [PR #10](https://github.com/paradox123/shared-ai-docs/pull/10) nach `main` gemergt. Merge: `6d0269840045cd67427f7cb051111ded1920c047`; geprüfter Code-Head: `7b59ed585db28414317c639145ed63e296184a94`.

[Abnahme, Nachweise und Grenzen](../../../contextual-llm-wiki/evidence/resumable-maintenance-05.md). Akzeptiertes 12-Datei-Manifest: SHA256 `2fc078677c49799c6c6180bcd3c0d2c55ca05a9289e784d4082250f8fc8ab740`; alle Inhalte auf dem Remote-Ziel nach dem Merge verifiziert. Dauerhafte Rohmessungen und Manifest: `/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket05/`.

Der aktive OpenSpec-Change bleibt für Ticket 06 und die ausdrücklich ausstehenden produktiven Nachweise offen. Dieser Ticketabschluss behauptet keine Live-Aktivierung oder abgeschlossene produktive Gesamtabnahme.
