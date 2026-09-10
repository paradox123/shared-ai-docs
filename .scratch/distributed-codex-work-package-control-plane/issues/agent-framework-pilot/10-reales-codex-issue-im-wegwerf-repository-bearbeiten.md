# 10: Ein reales Codex-Issue im Wegwerf-Repository bearbeiten

**What to build:** Die echte gepinnte Codex-Runtime bearbeitet einen begrenzten Auftrag in einem wegwerfbaren Repository, bleibt vollständig im Run beobachtbar und unterstützt das gezielte Öffnen der Background-Session in Codex oder einen ausdrücklich bestätigten Handoff-Fork.

**Blocked by:** 05: Repository-Base und externe Wirkungen sicher reconciliieren; 06: Eine Human Request beantworten und die Session in Codex fortsetzen; 07: Eine aktive Agentenoperation gezielt steuern; 09: Nach einem Abbruch sicher reconnecten und den Run exportieren

**Status:** ready-for-agent

- [ ] Der Lauf verwendet ausschließlich ein wegwerfbares lokales Repository und erzeugt keine irreversible Remote-Wirkung.
- [ ] Vor Agentenstart prüft der Adapter Runtime-, Vertrags-, Tool-, Dependency-, Sandbox- und Sessionfähigkeiten sowie das tatsächlich unterstützte Output-Schema.
- [ ] Das kanonische Ergebnisschema bleibt vollständig; eine getrennte Endpoint-Probe verhindert die Übergabe nicht unterstützter Schema-Konstruktionen.
- [ ] StartFresh, Read, Resume, Fork, Interrupt/Stop und `Open in Codex` werden gegen die echte gepinnte Runtime ausgeführt und mit Sessionidentitäten belegt.
- [ ] Same-Session-Öffnung verwendet exakt die Background-Session. Wo dies nicht sicher möglich ist, zeigt der Operator die Einschränkung und verlangt vor einem Handoff-Fork eine explizite Entscheidung.
- [ ] Beobachtbare Interaktionen aus der in Codex geöffneten oder geforkten Session erscheinen wieder unter demselben Run und unterliegen Lease und Fencing.
- [ ] Ein Crash nach Sessionstart und vor gespeicherter Zuordnung adoptiert genau die bestehende Session oder endet explizit unsicher; er startet nicht still eine zweite.
- [ ] Prozessbesitz, Timeout, Prozessgruppenstopp und verspätete Ausgabe bleiben öffentlich mit Attempt und Session korreliert.
- [ ] Fehlende stabile Codex-Semantik stoppt den Kandidaten sichtbar und verändert den LangGraph-Piloten nicht.

## Session lesson

Stale Runtime, Codex-inkompatibles `allOf`, unklare Timeouts und unsichtbare Headless-Sessions werden gegen den echten Prozess geprüft, bevor ein Produktrepository angebunden wird.
