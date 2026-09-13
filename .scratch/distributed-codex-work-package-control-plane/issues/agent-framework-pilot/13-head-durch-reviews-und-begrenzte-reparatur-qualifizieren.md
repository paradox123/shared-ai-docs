# 13: Einen Head durch Reviews und begrenzte Reparatur qualifizieren

**What to build:** Ein evidence-bereiter Draft-PR wird für genau eine Head-SHA deterministisch geprüft, von drei isolierten Codex-Sessions unabhängig reviewed und bei Findings höchstens drei Mal repariert, bis Qualification oder eine menschliche Übergabe erreicht ist.

**Blocked by:** 11: Einen Draft-PR mit ausführbarer Evidence erzeugen

**Status:** resolved

- [x] Deterministische Verifikation prüft den unveränderten erwarteten Head und lehnt eine während des Checks erfolgte Mutation ab.
- [x] Requirements-, Code- und Architekturreview starten in drei frischen, peer-blinden Sessions mit derselben Head-SHA und ohne gegenseitige Verdicts.
- [x] Qualification gelingt nur, wenn alle anwendbaren Achsen und deterministischen Checks für exakt diesen Head erfolgreich sind.
- [x] Ein neuer Writer-Head invalidiert sämtliche früheren Evidence-, Check- und Review-Verdicts.
- [x] Actionable Findings gehen an denselben Writer und Worktree und können höchstens drei nummerierte Repair-Runden auslösen.
- [x] Nach jeder Repair-Runde werden Evidence, deterministische Verifikation und alle drei Reviews für den neuen Head frisch ausgeführt.
- [x] Nach drei erfolglosen Runden startet keine vierte; der Run erzeugt eine konkrete Human Request und bewahrt Branch, PR, Evidence und Findings.
- [x] Qualification markiert nur Bereitschaft für menschliches Review und erzeugt weder menschliches Approval noch Merge, Deployment oder Release.

## Session lesson

Die alten LangGraph-Verträge für drei Reviewachsen und begrenzte Reparatur bleiben Verhaltensbaseline; neue Heads dürfen keine alten Verdicts erben.


## Implementation — 2026-09-13

Auf dem angeforderten `main` implementiert. Der aktive OpenSpec-Change
[qualify-agent-framework-head](../../../../openspec/changes/qualify-agent-framework-head/proposal.md)
trägt die Anforderungen, Tasks und [Abnahmeübersicht](../../../../openspec/changes/qualify-agent-framework-head/implementation-evidence.md).
Die [Operator-Anleitung](../../../../microsoft-agent-framework-work-package-pilot/QUALIFICATION.md)
erklärt Plan-Konfiguration, Qualification, Human Requests und Wiederaufnahme.

Die gezielten Nachweise bestehen: zehn Worker-/HTTP-Tests, zwölf Adapter-/Publication-Tests
und zwei Durchstiche mit realer gepinnter Codex-Runtime und den tatsächlichen Repository-Skills.
Der reale Reparaturfall verwendet die ursprüngliche Writer-Session und sechs frische
Reviewer-Sessions über zwei Heads. GitHub bleibt in diesen Nachweisen eine kontrollierte
Provider-Grenze mit echtem lokalem/barem Git; kein Live-GitHub-PR oder menschliches Approval
wird behauptet. Standards- und Spec-Review haben nach Korrekturen keine offenen Befunde.
Die Gesamtregression ist grün: 196 Tests, davon 176 bestanden und 20 explizite
Runtime-/Live-Provider-Probes übersprungen. Die beiden neuen nativen Qualification-Probes
wurden zusätzlich separat bestanden. Auch der 10.015-Event-Abbruch-/Wiederherstellungstest
ist erfolgreich. Build, strikte OpenSpec-Validierung und Diff-Prüfung bestehen.

Der Change bleibt zur Benutzerabnahme aktiv und ist nicht archiviert.
