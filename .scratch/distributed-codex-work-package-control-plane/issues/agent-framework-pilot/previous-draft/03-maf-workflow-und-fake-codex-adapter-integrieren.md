# 03: MAF-Workflow und Fake-Codex-Adapter integrieren

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Ein kleiner typisierter Agent-Framework-Workflow koordiniert deterministische Aktivitäten und eine externe Fake-Codex-Session hinter einem versionierten Adapter, ohne Codex durch einen frameworkeigenen Modellagenten zu ersetzen.

**Blocked by:** 02: Kanonischen Run, History und Operator-Read-back bauen

**Covers:** US 13-26, 97, 105-107, 125, 127, 129-130

**LangGraph baseline:** Issue 02, Worker-/Review-Adapter-Contracts und die vorhandenen JSON-Schemas.

**Status:** needs-triage

- [ ] Deterministische Vorbereitung und Routing verwenden keinen Modellagenten; die Fake-Session läuft als externe Aktivität.
- [ ] Vor Start prüft der Adapter Runtime-, Capability-, Contract-, Tool-, Dependency-, Sandbox- und Evidence-Voraussetzungen.
- [ ] Das kanonische Schema bleibt vollständig; eine separate Endpoint-Probe beweist den von Codex tatsächlich unterstützten Schema-Subset.
- [ ] Session-ID und redigierte nummerierte Nachrichten, Toolaufrufe, Ergebnisse und Fehler erscheinen in der gemeinsamen Run History.
- [ ] Worker-Wechsel nach Sessionstart erzeugt ohne explizite Retry-Entscheidung keine zweite Session.
- [ ] Schreibrechte und Effektverantwortung sind pro Aktivität eindeutig; ein Agent blockiert nicht deshalb, weil ein späterer Publisher den Commit verantwortet.
- [ ] Contract-Tests verwenden die bestehenden JSON-Fixtures, ohne den LangGraph-Code oder seine Laufzeitdaten zu ändern.

## Session lesson

Der ProBara-Worker erhielt ein lokal valides Schema mit Codex-inkompatiblem `allOf`; außerdem kollidierten Worker-Sandbox und Publisher-Verantwortung. Beide Integrationsgrenzen werden vor dem ersten echten Codex-Lauf bewiesen.
