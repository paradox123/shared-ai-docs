# 09: Echten Codex-Adapter begrenzt integrieren

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Nach bestandenen Fake-, Recovery-, Evidence- und Security-Slices wird derselbe Adaptervertrag mit einer realen gepinnten Codex-Runtime in einem wegwerfbaren lokalen Repository ausgeführt.

**Blocked by:** 05: Session-Fortsetzung und Live Control beweisen; 07: Evidence, Qualification und bounded Repair umsetzen; 08: Redaction, Artefakte und portablen Export beweisen

**Covers:** US 13-17, 21-32, 36-45, 70-75, 105-107, 127, 129-130

**LangGraph baseline:** Issue 02, 04, 05 und 13; Codex CLI Worker-/Review-Contracts. Keine ProBara-CRM-Live-Ausführung.

**Status:** needs-triage

- [ ] Der Lauf verwendet ein wegwerfbares lokales Git-Repository und erzeugt keine irreversible Remote-Wirkung.
- [ ] Capability Negotiation prüft StartFresh, Read, Resume, Fork, Interrupt/Stop und dokumentiert fehlende stabile Fähigkeiten als Fail-Closed-Ergebnis.
- [ ] Das tatsächlich an Codex gesendete Output-Schema wird gegen die unterstützte Endpoint-Menge geprüft; kanonische Nachvalidierung bleibt separat.
- [ ] Sessionstart, Prozessbesitz, Timeout, Prozessgruppen-Kill und verspätete Ausgabe sind öffentlich korreliert.
- [ ] Ein Crash nach `thread.started` und vor persistierter Zuordnung adoptiert exakt die bestehende Session oder endet explizit unsicher; er startet nicht still eine zweite.
- [ ] Alle beobachtbaren Nachrichten/Tools/Ergebnisse erscheinen redigiert in derselben Run History, unabhängig von Codex-App-Task-Sichtbarkeit.
- [ ] Fehlende produktionsgeeignete stabile Codex-Semantik stoppt den Kandidaten und verändert den LangGraph-Piloten nicht.

## Session lesson

Stale Runtime, unsupported Schema, unklare Timeouts und versteckte headless Sessions werden als getrennte Adapterfehler reproduziert, bevor eine reale Produktrepository-Anbindung erlaubt wird.
