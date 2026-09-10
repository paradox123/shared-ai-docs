# 04: Externe Effekte, Base-SHA und Recovery absichern

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Crash-Recovery setzt nur fehlende Arbeit fort, adoptiert bereits eingetretene Git-/Provider-/Session-Effekte und startet jeden sequenziellen Lauf von der provider-autoritativ bestätigten Base-SHA.

**Blocked by:** 03: MAF-Workflow und Fake-Codex-Adapter integrieren

**Covers:** US 11-12, 38, 43-45, 58, 64-69, 126

**LangGraph baseline:** Issue 07, 08 und 10; Worktree-, Publication- und Startup-Recovery-Contracttests. Die 24-Stunden-/macOS-Regel wird nicht portiert.

**Status:** needs-triage

- [ ] Jeder externe Effekt besitzt eine stabile Operation-ID, Receipt, Reconciliation und Adopt-or-fail-closed-Regel.
- [ ] Fault Injection unmittelbar nach externem Effekt und vor Ergebniscommit erzeugt keine Doppelwirkung.
- [ ] Ein Merge des Vorgängers gibt den Nachfolger erst frei, wenn lokale Git-Basis und aufgezeichnete erwartete Base exakt dem Provider-Head entsprechen.
- [ ] Worker/API-Prozessabbrüche an allen geplanten Grenzen erhalten Run-, Attempt-, Session-, Worktree-, Head- und Effect-Korrelation.
- [ ] Unsichere Zustände werden öffentlich als adoptierbar, konfliktbehaftet oder handlungsbedürftig sichtbar; kein generischer Retry rät den Zustand.
- [ ] Retry, Retire, Reconcile und Adopt sind unterstützte Operator-Commands; manuelle Datenbankänderungen sind kein Abnahmepfad.
- [ ] Der Nichtbeeinflussungsnachweis bestätigt erneut, dass LangGraph-Runtime und ProBara-CRM nicht verändert wurden.

## Session lesson

Issue #3 startete im LangGraph-Piloten auf einem stale lokalen `main`; rejected Runs mussten per SQLite-Eingriff retirert werden. Diese beiden Fehler sind verpflichtende Recovery-Szenarien.
