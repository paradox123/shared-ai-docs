# 03: Pflegelaeufe begrenzen und Fortschritt sichtbar machen

Status: ready-for-agent

**Parent:** [Wiederaufnehmbare Wiki-Pflege](../spec.md)

**What to build:** Ein Pflegeaufruf hat ein endliches Arbeits- oder Zeitbudget, meldet waehrend der Ausfuehrung dauerhaften Fortschritt und endet kontrolliert mit wiederaufnehmbarer Restarbeit. Gemeinsame Providerfehler stoppen weitere abhaengige Anfragen. Der Operator kann Zustand und Ergebnis beurteilen, ohne auf einen moeglicherweise nie erscheinenden Endbericht zu warten.

**Blocked by:** 02 — Erfolgreiche Extraktionen nach Neustart wiederverwenden.

**Spec coverage:** User Stories 17–19, 21–22; Implementation Decisions 8–12.

- [ ] Der oeffentliche Wartungshelper fuehrt Modellarbeit mit expliziten endlichen Ausfuehrungsgrenzen und einer endlichen Beendigungsfrist aus. Parameter und gemessene Begruendung sind dokumentiert; die Beispielwerte aus der Spec sind keine zwingenden Vorgaben.
- [ ] Phase, aktive Arbeit, Erfolge, Fehler, Wiederverwendung, Restarbeit und letzter Fortschritt werden waehrend der Verarbeitung dauerhaft lesbar. Ein zurueckgehaltener Modellaufruf verhindert diese Sicht nicht.
- [ ] Bei Budgetende werden keine neuen Modellauftraege gestartet. Eigene laufende Unterprozesse werden innerhalb der Beendigungsfrist abgeschlossen oder gezielt beendet; benoetigte Sperren werden danach kontrolliert freigegeben.
- [ ] Ein frischer Prozess setzt nach Budgetende anhand der Ergebnisse aus Ticket 02 fort. Bereits gesicherte kompatible Erfolge werden nicht erneut angefordert.
- [ ] Ein budgetbedingt unvollstaendiger Lauf hat einen parsebaren Abschlussbericht mit Restarbeit und wird von bestehenden Verbrauchern nicht als vollstaendiger Erfolg interpretiert. Exit-/Ergebnisvertrag und Parser werden gemeinsam aktualisiert und geprueft.
- [ ] Ein gemeinsamer Authentifizierungs- oder Providerfehler stoppt weitere davon abhaengige Queue-Eintraege; er wird nicht fuer jede Quelle erneut als isolierter Fehler abgearbeitet. Bereits laufende Auftraege werden begrenzt abgewickelt.
- [ ] Begrenzte Quellenfehler bleiben von gemeinsamen Fehlern unterscheidbar. Gueltige unabhängige Arbeit bleibt gesichert; keine ungepruefte Veroeffentlichung wird dadurch erlaubt.
- [ ] Ein zweiter Pflegeaufruf waehrend Besitz des ersten Laufs meldet den Konflikt ohne ueberlappende Mutation; nach kontrollierter Freigabe kann der Folgeaufruf starten.
- [ ] Fortschrittsdaten verraten keine Zugangsdaten und enthalten keine unnoetigen Dokumentinhalte. Die bestehende strukturierte CLI-Endausgabe bleibt parsebar.
- [ ] Ein erfolgreicher unveraenderter Folgelauf bleibt No-op; ein Teilfortschritt zieht den vollstaendigen Pflegezeitpunkt nicht vor.

**Verification:** Den echten Wartungshelper mit kurzen Testbudgets, kontrolliert gehaltenem Provider und frischen Folgeprozessen pruefen. Behauptungen betreffen sichtbaren Fortschritt vor Ende, endliche Prozessdauer, keine neue abhaengige Provideranfrage nach erkanntem gemeinsamen Fehler, korrekten Endbericht und erfolgreiche Wiederaufnahme. Die Tests haben unabhaengige harte Fristen und verwenden keine Produktionsprozesse.

**Boundary:** Keine Abhaengigkeit von Ticket 01: Begrenzung und Wiederaufnahme sind am bestehenden Pflegepfad separat nachweisbar. Fachquellen-Indexpflege wird bei gemeinsamer Integration nach dem Vertrag von Ticket 01 behandelt. Tagesprioritaet und Veroeffentlichung begrenzter Tagespakete folgen in Ticket 04. Der gespeicherte Automationsprompt wird erst in Ticket 06 aktiviert.
