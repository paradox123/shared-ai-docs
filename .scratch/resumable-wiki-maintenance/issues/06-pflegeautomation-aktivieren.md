# 06: Neue Pflege in der bestehenden Automation aktivieren

Status: closed

**Parent:** [Wiederaufnehmbare Wiki-Pflege](../spec.md)

**What to build:** Die vorhandene taegliche Codex-Automation nutzt den vollstaendig integrierten Pflegeablauf: aktuelle Fachquellen unabhaengig indexieren, Wiki-Arbeit begrenzt und wiederaufnehmbar ausfuehren und Tagesaenderungen bevorzugen. Der Agent liest dauerhaften Fortschritt und verlaesst ausbleibende Fertigstellung ueber einen endlichen Diagnoseweg. Der produktive Betrieb wird anhand tatsaechlicher Ergebnisse abgenommen.

**Blocked by:** 01 — Aktuelle Fachquellen unabhaengig vom Wiki auffindbar machen; 05 — Quellenänderungen waehrend der Pflege gezielt abfangen.

**Spec coverage:** User Stories 17–19, 21–27; Integration aller User Stories 1–27; Implementation Decisions 8–13.

- [x] Die Ergebnisse aller Vorgaengertickets sind gemeinsam ueber Helper, echte isolierte QMD-Datenbank und WikiQuery verifiziert. Die integrierte Abnahme umfasst Indexerfolg bei ausstehender Wiki-Arbeit, Neustart, Tagesprioritaet, Quellenabweichung, gemeinsamen Providerfehler und anschliessenden No-op.
- [x] Konkrete Laufzeit-, Beendigungs-, Fortschrittsbeobachtungs- und Arbeitspaketgrenzen sind anhand der Messungen festgelegt und dokumentiert. Der Agent muss diese nicht bei jedem Tageslauf neu erraten.
- [x] Gespeicherter Prompt, Wartungsreferenz und Betriebsanleitung beschreiben dieselbe endliche Ausfuehrung: einen eigenen Lauf einmal starten, den ausgegebenen Artefaktort behalten, Fortschritt begrenzt beobachten und bei fehlendem Fortschritt begrenzt diagnostizieren. Kein zweiter Collector zur Ausgabewiedergewinnung und keine unendliche Polling-Schleife.
- [x] Ein isolierter Fall ohne Abschlussbericht fuehrt innerhalb der Beobachtungsgrenze zu einem expliziten unvollstaendigen oder fehlgeschlagenen Ergebnis. Prozesszustand und Restarbeit bleiben nachvollziehbar; die Dokumentation verwechselt laufenden Prozess und erfolgreichen Fortschritt nicht.
- [x] Vor der produktiven Umstellung sind aktuelle Definition, Zustand und vorhandene Laufbesitzer geprueft und erforderliche Sicherungen vorhanden. Es wird keine zweite Pflege neben einem bestehenden Besitzer gestartet und kein fremder Prozess pauschal beendet. Eine belegte aktive Pflege blockiert die Umschaltung sichtbar; auf deren Helper wird nicht unbegrenzt gewartet.
- [x] Die neue Definition ist ueber den vorgesehenen Codex-Automationsweg gespeichert und zurueckgelesen. Bestehender Zeitplan, Modell, Projekt, Benachrichtigungen und gemeinsamer Pflegeumfang bleiben erhalten; kein zusaetzlicher Scheduler oder Watcher entsteht.
- [x] Bestehende gueltige Wiki-Inhalte, gespeicherte Antworten und Quellenautoritaet bleiben bei Aktivierung erhalten. Gegebenenfalls notwendige Zustandsmigration und Rueckkehr zum vorigen Betriebsstand sind nachvollziehbar und geprueft.
- [x] Eine kontrollierte produktive Ausfuehrung belegt aktuelle Originalsuche und endliches Laufende mit wiederaufnehmbarer Arbeit; die Memory trennt Indexergebnis, laufende Nachpflege, Erstimport-Rueckstand, Fristverletzungen und Gesamtabschluss.
- [ ] Ein tatsaechlicher anschliessender Lauf der bestehenden taeglichen Automation wird separat anhand seiner Artefakte verifiziert. Konfigurationspruefung oder manueller Lauf gelten nicht als Schedulernachweis. Bis zum Ereignis bleibt dieser Abnahmepunkt offen; kein stundenlanges Agentenwarten und kein neuer Scheduler zur Nachweiserzeugung.
- [ ] Der mehrtaegige Erstimport wird erst mit belegtem vollstaendigem Abschluss und anschliessendem No-op abgenommen. Fehlender Abschluss bleibt als eigene offene Abnahme erhalten; ein begrenzter Tageslauf oder frischer Suchindex ersetzt ihn nicht.
- [x] Die Abnahme dokumentiert erwartetes und beobachtetes Verhalten samt Evidenz und verbleibenden Grenzen. Keine Tests allein als Beweis vollstaendiger Produktivabnahme ausgeben.

**Verification:** Zuerst die isolierte Ende-zu-Ende-Abnahme mit kurzen Fehler- und Prozessfristen. Danach gespeicherte Definition pruefen und einen kontrollierten Produktivlauf auswerten. Schedulerlauf und endgueltigen Erstimport-Abschluss ueber ihre bereits erzeugten Artefakte nachweisen, jeweils ohne fremde Helper erneut auszufuehren oder unendlich auf sie zu warten. Fehlende externe Ereignisse sind offene Abnahme, kein Erfolg.

**Boundary:** Keine eigenstaendigen Runtime-, Modell- oder Dependency-Updates und keine Reparatur von macOS-TCC oder Anmeldung. Der bestehende Automations-Skill und seine Payload-Regeln sind bei der Umstellung verbindlich. Die Parent-Spec bleibt erhalten; ihre Veroeffentlichung und diese Ticketanlage autorisieren fuer sich keinen jetzt gestarteten Produktionslauf.

## Abschluss und produktive Abnahme

Code über [PR #12](https://github.com/paradox123/shared-ai-docs/pull/12) als `c1801b3590ac90ebe2e8500a6e47bbdee26fa174` nach `main` gemergt. Isolierte Integration, unabhängige Reviews und kritische Prozessgegenfälle sind abgenommen. Die bestehende Automation wurde anschließend über das vorgesehene Tool aktiviert und unverändert bezüglich Zeitplan, Modell, Projekt, Benachrichtigungen und Quellenumfang zurückgelesen.

[Nachweise, Soll/Ist und Grenzen](../../../contextual-llm-wiki/evidence/resumable-maintenance-06.md): genau ein kontrollierter Produktivlauf endete nach 121,295s unvollständig, mit aktuellem Index für 2047 Originale und vier dauerhaft gesicherten Extraktionen. Tatsächliche WikiQuery-Suche aus diesem Index und Prozessende sind belegt; 2044 Initialeinheiten bleiben offen, Gesamtabschluss false. Die formale Produktivabnahme ist abgeschlossen; die gelieferte Implementierung und Aktivierung sind akzeptiert und das Ticket geschlossen.

Die beiden verbleibenden Checkboxen sind gemäß README eigene spätere Abnahmepunkte. Ein Ticketabschluss der gelieferten Implementierung/Aktivierung darf diese nicht als erledigt markieren. OpenSpec bleibt offen; weder manueller Lauf noch Konfiguration beweisen Schedulerlauf oder Vollimport/No-op. Dauerhafte Rohbelege: `/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket06/`.
