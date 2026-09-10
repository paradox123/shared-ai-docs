# 02: Kanonischen Run, History und Operator-Read-back bauen

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Ein autorisierter synthetischer Issue-Command erzeugt genau einen dauerhaften `ImplementationRun`, dessen Aktivitäten, Versuche, Ereignisse, Fehler und Artefaktverweise über eine öffentliche Operator-Oberfläche und einen bestätigten Event-Cursor lesbar sind.

**Blocked by:** 01: OSS-Backend-Gate beweisen und getrennten Piloten bootstrapen

**Covers:** US 1-8, 15, 19-35, 45-48, 51, 57, 63-65, 69, 76-83, 114-121, 129-130

**LangGraph baseline:** Issue 01 und 08 sowie `test_workflow_interface.py` und `test_startup_reconciliation.py`, Verhalten/Fixtures only.

**Status:** needs-triage

- [ ] Doppelte identische Start-Commands konvergieren zu einem Run; widersprüchliche Wiederverwendung einer Command-ID wird öffentlich abgelehnt.
- [ ] Domain-History bleibt kanonisch und unabhängig von Agent-Framework-Session- oder Durable-Orchestration-History exportier- und wiederherstellbar.
- [ ] Ein zweiter Client liest denselben Run ohne Zugriff auf den ursprünglichen Prozess oder Worktree.
- [ ] Reconnect ab bestätigtem Cursor liefert auch nach API-/Worker-Neustart und fehlgeschlagenem Run jedes Ereignis genau einmal in stabiler Reihenfolge.
- [ ] Run-, Attempt-, Prozess- und Heartbeat-Zeit werden getrennt angezeigt; Host-Schlaf oder altes Run-Alter gilt nicht als Prozess-Timeout.
- [ ] Eine gültige redigierte Worker-Antwort bleibt als Originalbeobachtung erhalten, auch wenn spätere Interpretation oder Qualifikation scheitert.
- [ ] Logs und Framework-Dashboard sind nur korrelierte Zusatzbelege; die Abnahme erfolgt über öffentliche Run-/Event-/Export-Seams.

## Session lesson

Beim ProBara-Piloten wurde ein gültiges `outcome: blocked` durch `InvalidWorkerResult` ersetzt und Monitoring verwechselte verschiedene Zeitachsen. Beide Fälle sind Black-Box-Regressionsfixtures dieses Tickets.
