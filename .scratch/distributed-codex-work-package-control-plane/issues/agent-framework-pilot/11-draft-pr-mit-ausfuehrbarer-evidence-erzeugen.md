# 11: Einen Draft-PR mit ausführbarer Evidence erzeugen

**What to build:** Ein vollständig vorbereiteter Codex-Auftrag erzeugt einen Draft-Pull-Request, dessen aktuelle Head-SHA jedes Akzeptanzkriterium mit direkt ausführbarer, redigierter und nachlesbarer Evidence belegt.

**Blocked by:** 10: Ein reales Codex-Issue im Wegwerf-Repository bearbeiten

**Status:** resolved

- [x] Vor Agentenstart benennt der Auftrag pro Akzeptanzkriterium Evidence-Art, erforderliche Phasen, ausführbare Oberfläche und erwarteten Read-back.
- [x] Readiness prüft Repository-Base, Verträge, Werkzeuge, Abhängigkeiten, Zugriffe, Sandbox-Rechte sowie REST-, UI-, Idempotenz- und Dokument-Evidence-Oberflächen.
- [x] Eine fehlende Voraussetzung startet keine teure Agentenarbeit, sondern erzeugt eine konkrete Human Request oder einen expliziten Blocker.
- [x] Ein erfolgreicher Auftrag veröffentlicht genau einen Draft-PR für den erwarteten Branch und Head und führt keinen Merge aus.
- [x] Der PR-Body ordnet jedem Akzeptanzkriterium direkte Evidence mit Request, Response, Repeat, Read-back, Screenshot oder dokumentenspezifischen Phasen zu, soweit fachlich erforderlich.
- [x] Evidence ist an Commit und Head-SHA gebunden, über die fachlich autoritative Oberfläche nachlesbar und vor Veröffentlichung redigiert.
- [x] Ein wiederholter Publication-Command adoptiert den vorhandenen passenden Draft-PR und erzeugt keinen zweiten.
- [x] Operational Logs, Agentenbehauptungen und Framework-Dashboard gelten allein nicht als fachlicher Verhaltensnachweis.

## Session lesson

ProBara Issue #3 implementierte die Änderung, konnte aber die geforderten REST-, Idempotenz- und UI-Phasen nicht liefern. Der Evidence-Plan wird deshalb vor dem Agentenstart ausführbar geprüft.


## Implementation status — 2026-09-13

Issue 10 ist abgeschlossen; sein früherer Runtime-Blocker ist überholt.
Die Umsetzung liegt auf `codex/agent-framework-issue-11` im Change
[`publish-agent-framework-evidence-draft`](../../../../openspec/changes/publish-agent-framework-evidence-draft/proposal.md).
Readiness, ausgeführte Evidence, persistierte Publication-Absicht und Adoption
bestehen über Worker/HTTP, PostgreSQL, reales lokales Git und einen kontrollierten
GitHub-Provider. Auch der Durchstich mit echter Codex-Runtime und nativer TUI besteht.
Die 25 Publication-Tests und alle 35 abschließenden Native-/Runtime-Tests bestehen.
Standards- und Spec-Review haben keine offenen Befunde. Die Gesamtregression
hat einen Fehler im bestehenden 10.000-Event-Stresstest; derselbe Fehler wurde
auf dem unveränderten Issue-10-Stand reproduziert. Die Abnahmeübersicht trennt
diesen Befund von den erfolgreichen Issue-11-Nachweisen.

Implementierung abgeschlossen; Benutzerabnahme und OpenSpec-Archivierung stehen
aus. Die GitHub-Grenze ist im Nachweis kontrolliert, Codex/TUI und lokales Git
sind real. Es wurde kein Live-GitHub-PR erzeugt.

[Abnahmeübersicht mit fachlichen Ergebnissen, Grenzen und Nachweisen](../../../../openspec/changes/publish-agent-framework-evidence-draft/implementation-evidence.md)

[Operator-Anleitung](../../../../microsoft-agent-framework-work-package-pilot/PUBLICATION.md)
