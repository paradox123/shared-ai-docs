# 13: Einen Head durch Reviews und begrenzte Reparatur qualifizieren

**What to build:** Ein evidence-bereiter Draft-PR wird für genau eine Head-SHA deterministisch geprüft, von drei isolierten Codex-Sessions unabhängig reviewed und bei Findings höchstens drei Mal repariert, bis Qualification oder eine menschliche Übergabe erreicht ist.

**Blocked by:** 11: Einen Draft-PR mit ausführbarer Evidence erzeugen

**Status:** ready-for-agent

- [ ] Deterministische Verifikation prüft den unveränderten erwarteten Head und lehnt eine während des Checks erfolgte Mutation ab.
- [ ] Requirements-, Code- und Architekturreview starten in drei frischen, peer-blinden Sessions mit derselben Head-SHA und ohne gegenseitige Verdicts.
- [ ] Qualification gelingt nur, wenn alle anwendbaren Achsen und deterministischen Checks für exakt diesen Head erfolgreich sind.
- [ ] Ein neuer Writer-Head invalidiert sämtliche früheren Evidence-, Check- und Review-Verdicts.
- [ ] Actionable Findings gehen an denselben Writer und Worktree und können höchstens drei nummerierte Repair-Runden auslösen.
- [ ] Nach jeder Repair-Runde werden Evidence, deterministische Verifikation und alle drei Reviews für den neuen Head frisch ausgeführt.
- [ ] Nach drei erfolglosen Runden startet keine vierte; der Run erzeugt eine konkrete Human Request und bewahrt Branch, PR, Evidence und Findings.
- [ ] Qualification markiert nur Bereitschaft für menschliches Review und erzeugt weder menschliches Approval noch Merge, Deployment oder Release.

## Session lesson

Die alten LangGraph-Verträge für drei Reviewachsen und begrenzte Reparatur bleiben Verhaltensbaseline; neue Heads dürfen keine alten Verdicts erben.
