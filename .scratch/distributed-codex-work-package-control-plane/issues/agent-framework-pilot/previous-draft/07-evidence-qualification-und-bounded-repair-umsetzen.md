# 07: Evidence, Qualification und bounded Repair umsetzen

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Implementierung, direkte Evidence, deterministische Verifikation, drei unabhängige Reviews und höchstens drei Repair-Runden qualifizieren genau eine Head-SHA; unvollständige Evidence erhält einen eigenen begrenzten Korrekturpfad.

**Blocked by:** 04: Externe Effekte, Base-SHA und Recovery absichern; 06: Repository Authorization, Control Lease und Fencing beweisen

**Covers:** US 16-20, 30, 53-56, 64-69, 127-129

**LangGraph baseline:** Issues 03-06; Evidence-, Verification-, Review- und Repair-Contracts sowie Golden Fixtures.

**Status:** needs-triage

- [ ] Der Auftrag benennt je Akzeptanzkriterium Evidence-Art, erforderliche Phasen, ausführbare Oberfläche und erwarteten Read-back.
- [ ] Readiness lehnt einen Auftrag früh ab, wenn REST-, UI-, Idempotenz- oder Dokument-Evidence nicht ausführbar erfasst werden kann.
- [ ] Schema-valides, aber semantisch unvollständiges Evidence-Ergebnis startet eine begrenzte Evidence-Capture/Correction-Aktivität statt einer neuen Codeimplementierung.
- [ ] Ist Nacherfassung nicht möglich, konvergiert der Run zu einem expliziten Blockzustand, entfernt aktive Projektionen und gibt Repository-Serialisierung nach Policy frei.
- [ ] Deterministische Verifikation und drei frische peer-blinde Reviewer prüfen exakt denselben aktuellen Head.
- [ ] Ein neuer Head invalidiert alle alten Evidence- und Review-Verdicts; nach jeder Repair-Runde laufen alle erforderlichen Gates erneut.
- [ ] Nach drei erfolglosen Repair-Runden startet keine vierte und die erhaltene Arbeit bleibt für Menschen nutzbar.

## Session lesson

ProBara Issue #3 scheiterte nach fertiger Implementierung an fehlenden `request`, `response`, `repeat`, `read_back` und `screenshot`-Phasen; der Run blieb trotzdem aktiv. Das exakte Resultat dient als Regression.
