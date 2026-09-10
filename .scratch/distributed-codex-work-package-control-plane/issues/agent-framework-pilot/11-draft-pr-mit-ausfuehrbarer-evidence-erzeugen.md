# 11: Einen Draft-PR mit ausführbarer Evidence erzeugen

**What to build:** Ein vollständig vorbereiteter Codex-Auftrag erzeugt einen Draft-Pull-Request, dessen aktuelle Head-SHA jedes Akzeptanzkriterium mit direkt ausführbarer, redigierter und nachlesbarer Evidence belegt.

**Blocked by:** 10: Ein reales Codex-Issue im Wegwerf-Repository bearbeiten

**Status:** ready-for-agent

- [ ] Vor Agentenstart benennt der Auftrag pro Akzeptanzkriterium Evidence-Art, erforderliche Phasen, ausführbare Oberfläche und erwarteten Read-back.
- [ ] Readiness prüft Repository-Base, Verträge, Werkzeuge, Abhängigkeiten, Zugriffe, Sandbox-Rechte sowie REST-, UI-, Idempotenz- und Dokument-Evidence-Oberflächen.
- [ ] Eine fehlende Voraussetzung startet keine teure Agentenarbeit, sondern erzeugt eine konkrete Human Request oder einen expliziten Blocker.
- [ ] Ein erfolgreicher Auftrag veröffentlicht genau einen Draft-PR für den erwarteten Branch und Head und führt keinen Merge aus.
- [ ] Der PR-Body ordnet jedem Akzeptanzkriterium direkte Evidence mit Request, Response, Repeat, Read-back, Screenshot oder dokumentenspezifischen Phasen zu, soweit fachlich erforderlich.
- [ ] Evidence ist an Commit und Head-SHA gebunden, über die fachlich autoritative Oberfläche nachlesbar und vor Veröffentlichung redigiert.
- [ ] Ein wiederholter Publication-Command adoptiert den vorhandenen passenden Draft-PR und erzeugt keinen zweiten.
- [ ] Operational Logs, Agentenbehauptungen und Framework-Dashboard gelten allein nicht als fachlicher Verhaltensnachweis.

## Session lesson

ProBara Issue #3 implementierte die Änderung, konnte aber die geforderten REST-, Idempotenz- und UI-Phasen nicht liefern. Der Evidence-Plan wird deshalb vor dem Agentenstart ausführbar geprüft.
