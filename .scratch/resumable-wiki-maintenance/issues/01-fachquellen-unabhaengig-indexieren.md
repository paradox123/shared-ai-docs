# 01: Aktuelle Fachquellen unabhaengig vom Wiki auffindbar machen

Status: ready-for-agent

**Parent:** [Wiederaufnehmbare Wiki-Pflege](../spec.md)

**What to build:** Der bestehende Wartungshelper aktualisiert den Suchindex aktueller Fachquellen auch dann, wenn deren Wiki-Aufbereitung scheitert. WikiQuery liefert diese Originale mit geprueften Verweisen und gekennzeichnetem Fallback; veraltete Wiki-Aussagen werden nicht als aktuell ausgegeben. Damit erhalten Nutzer aktuelle Belege, ohne einen zweiten Recherchezugang oder einen abgeschlossenen Erstimport zu benoetigen.

**Blocked by:** None (can start immediately).

**Spec coverage:** User Stories 1–6, 16, 21–22; Implementation Decisions 1–2, 9, 11.

- [x] Die bestehende QMD-/Publikationsgrenze wird vor der Verhaltensaenderung nur soweit entflechtet, wie die getrennte Fachquellen-Indexpflege es benoetigt; keine eigenstaendige breite Refaktorierung.
- [x] Ein neuer Originalinhalt wird durch den echten Wartungshelper in eine isolierte QMD-Datenbank aufgenommen, obwohl der kontrollierte Wiki-Provider anschliessend fehlschlaegt. WikiQuery liefert den Inhalt mit einem gueltigen Originalverweis und explizitem Fallback.
- [x] Nach Aenderung einer bereits synthetisierten Quelle ist das aktuelle Original auffindbar; die alte abhaengige Wiki-Aussage wird weder neu indexiert noch als aktuelle Evidenz geliefert.
- [x] Explizite Abfrage- und Quellengrenzen sowie Aktualitaetspruefungen gelten auch fuer Originalquellen-Fallback. Private und berufliche Fachquellen bleiben im gemeinsamen Pflegeumfang.
- [x] Indexergebnis und Wiki-Ergebnis werden getrennt gemeldet. Ein Indexerfolg macht einen Wiki-Fehler oder offenen Erstimport nicht zum vollstaendigen Erfolg und zieht den vollstaendigen Pflegezeitpunkt nicht vor.
- [x] Bestaetigte Quellenentfernung und unvollstaendiger Scan bleiben unterscheidbar. Ein Scanfehler loest keine Massenentfernung aus; Speicher-/Indexfehler werden als Blocker der jeweils abhaengigen Arbeit gemeldet.
- [x] QMD-Schreibzugriffe bleiben serialisiert. Ein konkurrierender Pflegeaufruf ueberlappt keine Mutation und beschaedigt den vorhandenen Zustand nicht.
- [x] Der unveraenderte erfolgreiche Folgeaufruf erhaelt den bestehenden No-op-Vertrag und die bisherige Suchbarkeit.

**Verification:** Rot→Gruen ueber den oeffentlichen Wartungshelper und anschliessende WikiQuery-Abfrage, mit temporaeren Fachrepos, echter isolierter QMD-Datenbank und kontrollierten Modell-/Embeddingantworten. Eine Attrappe fuer globale Retrieval-Kommandos allein belegt die neue Suchbarkeit nicht. Fehlerpfade besitzen kurze harte Testfristen; keine Produktionshelfer zur Reproduktion starten.

**Boundary:** Kein Laufzeitbudget oder Extraktionscache voraussetzen. Fuer diese Abnahme einen deterministisch endenden Providerfehler verwenden. Live-Automation und Produktionsdaten bleiben bis Ticket 06 unveraendert. ADR 0010 und ADR 0016 sowie die in der Parent-Spec verlinkten kanonischen Regeln gelten.


## Implementierungsnachweis

Ticket 01 ist im isolierten Worktree implementiert; die separate kritische Verifikation ist abgeschlossen, die Koordinator-Abnahme steht vor der Lieferung. [Verhalten, gemessene Ergebnisse und Grenzen](../../../contextual-llm-wiki/evidence/resumable-maintenance-01.md). Der Ticketstatus wird erst nach bestätigter Lieferung nach `main` abgeschlossen. Die übrigen fünf Tickets und die produktive Aktivierung bleiben offen.
