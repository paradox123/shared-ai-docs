# 06: Eine Human Request beantworten und die Session in Codex fortsetzen

**What to build:** Ein zweiter berechtigter Mensch öffnet einen fehlgeschlagenen oder wartenden Activity Attempt im Operator Client, kann ihn gezielt in Codex öffnen und entscheidet nachvollziehbar zwischen derselben Session, einem Fork oder einem frischen Versuch.

**Blocked by:** 03: Repositoryzugriff und exklusive Steuerung durchsetzen; 05: Repository-Base und externe Wirkungen sicher reconciliieren

**Status:** resolved

- [x] Eine dauerhafte Human Request bleibt nach API-/Workerneustart mit Run, Attempt, Session, Head, Problem, Evidence und zulässigen Aktionen auffindbar.
- [x] Der Operator zeigt vor jeder Fortsetzung Zielattempt, Sessionidentität, Phase, erwartete Head-SHA, Lease-Inhaber und bereits eingetretene Wirkungen.
- [x] `Resume` verwendet dieselbe Session-ID; `Fork` erzeugt eine neue Session mit expliziter Herkunft; `Fresh Retry` erzeugt eine neue Session ohne automatische Übernahme der bisherigen Unterhaltung.
- [x] `Open in Codex` öffnet genau die zugeordnete Session, wenn der Adapter dies sicher unterstützt.
- [x] Kann die ursprüngliche Background-Session nicht direkt in Codex dargestellt werden, benennt der Operator die Einschränkung und erzeugt erst nach ausdrücklicher Bestätigung einen als Handoff gekennzeichneten Fork mit Herkunft.
- [x] Eine schreibende Interaktion in der geöffneten Codex-Session setzt die aktuelle Control Lease voraus; ihre beobachtbaren Nachrichten, Tools, Ergebnisse und Entscheidungen fließen in dieselbe Run History zurück.
- [x] Das Öffnen allein verändert weder Workflowphase, Head, externe Effekte noch Sessionidentität und erzeugt keinen unkorrelierten Nebenlauf.
- [x] Doppelte, veraltete oder falsch adressierte Antworten und Fortsetzungsentscheidungen werden ohne Nebenwirkung abgelehnt; eine gültige Entscheidung wirkt logisch genau einmal.

## Session lesson

Die LangGraph-Intervention eröffnete eine separate Zusammenfassungs-Task, während die eigentliche Background-Session schwer auffindbar blieb. Dieses Ticket macht die konkrete Session erreichbar, ohne die zentrale Run History aufzugeben.

## Outcome

Implementiert in `030e233` und als `2026-09-12-continue-human-requests-in-codex`
archiviert. Der damalige öffentliche Prozessnachweis umfasst 72 erfolgreiche
Tests mit getrennten API-, CLI-, Worker- und Fake-Provider-Prozessen sowie
Wegwerf-PostgreSQL. Er belegt dauerhafte Human Requests, Session-Herkunft,
expliziten Handoff, Lease-Fencing und Wiederaufnahme nach externen Erfolgslücken.

Die Nachweise gelten für den kontrollierten Adapter und explizite lokale
Zustellung. Echte Codex-App-Integration, reale Provideridentitäten und automatische
DTS-Orchestrierung sind damit nicht nachgewiesen; die Live-Grenzen bleiben bei
Tickets 10/14.

- [Implementierungsnachweis](../../../../openspec/changes/archive/2026-09-12-continue-human-requests-in-codex/implementation-evidence.md)
- [Abgeschlossene Aufgaben](../../../../openspec/changes/archive/2026-09-12-continue-human-requests-in-codex/tasks.md)
- [HTTP-/CLI-Verhaltenstests](../../../../microsoft-agent-framework-work-package-pilot/tests/test_fake_codex_attempt.py)

## Comments

- 2026-09-12: Bei der Integration der Feature-Branches den veralteten Ticketstatus
  anhand des vorhandenen archivierten Changes und seines Verhaltensnachweises
  korrigiert. Dies dokumentiert die bestehende Umsetzung und erweitert ihren
  kontrollierten Prüfungsumfang nicht.
