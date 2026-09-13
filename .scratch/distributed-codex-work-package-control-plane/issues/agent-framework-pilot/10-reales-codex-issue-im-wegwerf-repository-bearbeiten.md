# 10: Ein reales Codex-Issue im Wegwerf-Repository bearbeiten

**What to build:** Die echte gepinnte Codex-Runtime bearbeitet einen begrenzten Auftrag in einem wegwerfbaren Repository, bleibt vollständig im Run beobachtbar und unterstützt das gezielte Öffnen der Background-Session in Codex oder einen ausdrücklich bestätigten Handoff-Fork.

**Blocked by:** 05: Repository-Base und externe Wirkungen sicher reconciliieren; 06: Eine Human Request beantworten und die Session in Codex fortsetzen; 07: Eine aktive Agentenoperation gezielt steuern; 09: Nach einem Abbruch sicher reconnecten und den Run exportieren

**Status:** resolved

- [x] Der Lauf verwendet ausschließlich ein wegwerfbares lokales Repository und erzeugt keine irreversible Remote-Wirkung.
- [x] Vor Agentenstart prüft der Adapter Runtime-, Vertrags-, Tool-, Dependency-, Sandbox- und Sessionfähigkeiten sowie das tatsächlich unterstützte Output-Schema.
- [x] Das kanonische Ergebnisschema bleibt vollständig; eine getrennte Endpoint-Probe verhindert die Übergabe nicht unterstützter Schema-Konstruktionen.
- [x] StartFresh, Read, Resume, Fork, Interrupt/Stop und `Open in Codex` werden gegen die echte gepinnte Runtime ausgeführt und mit Sessionidentitäten belegt.
- [x] Same-Session-Öffnung verwendet exakt die Background-Session. Wo dies nicht sicher möglich ist, zeigt der Operator die Einschränkung und verlangt vor einem Handoff-Fork eine explizite Entscheidung.
- [x] Beobachtbare Interaktionen aus der in Codex geöffneten oder geforkten Session erscheinen wieder unter demselben Run und unterliegen Lease und Fencing.
- [x] Ein Crash nach Sessionstart und vor gespeicherter Zuordnung adoptiert genau die bestehende Session oder endet explizit unsicher; er startet nicht still eine zweite.
- [x] Prozessbesitz, Timeout, Prozessgruppenstopp und verspätete Ausgabe bleiben öffentlich mit Attempt und Session korreliert.
- [x] Fehlende stabile Codex-Semantik stoppt den Kandidaten sichtbar und verändert den LangGraph-Piloten nicht.

## Session lesson

Stale Runtime, Codex-inkompatibles `allOf`, unklare Timeouts und unsichtbare Headless-Sessions werden gegen den echten Prozess geprüft, bevor ein Produktrepository angebunden wird.

## Implementation status — 2026-09-13

**Implementiert und verifiziert.** Die echte gepinnte
Codex-Runtime bearbeitet das lokale Wegwerf-Issue jetzt über den Microsoft Agent
Framework Worker und die native Codex-TUI. Geöffnet wird exakt die ursprüngliche
Background-Session. Nachrichten, Tool-Prüfungen und Dateiausführung verwenden
aktuelle Repository-Berechtigungen, Control Lease und Fencing; ihre Beobachtungen
erscheinen unter demselben Run in PostgreSQL.

Die native Sitzung hat `greeting.py` korrigiert und die beiden gelieferten Tests
bestanden. Rechteentzug blockiert den tatsächlichen PreToolUse-Hook; verspätete
Ergebnisse werden als nicht qualifizierende Nachträge gespeichert. Übernahme,
Interrupt, Resume/Fork-Replay und Öffnen nach Adapter-Abbruch sind real geprüft.

Die Öffnung verwendet die offizielle **Codex-TUI**, keinen Desktop-Sidebar-Eintrag;
die Capability weist `appTaskVisible:false` ausdrücklich aus. Das frühere
Runtime-Gate bleibt eine separate Diagnose. Sein historischer No-go ist keine
Anforderungslücke und kein Blocker der nun implementierten Integration.

- [Abnahmeübersicht mit Nachweisen](../../../../openspec/changes/archive/2026-09-13-prove-real-codex-runtime/implementation-evidence.md)
- [Reales Issue, Ergebnis und gemeinsame Historie](../../../../openspec/changes/archive/2026-09-13-prove-real-codex-runtime/evidence/native/real-issue.json)
- [Ausführung und Öffnen](../../../../microsoft-agent-framework-work-package-pilot/README.md#real-codex-issue-and-native-continuation-ticket-10)

## Comments

### 2026-09-13 — Weiterarbeit im Microsoft Agent Framework Pilot

Der bisherige Gesamtstopp war voreilig. Die fehlende Integration war kein
Nachweis einer fehlenden Codex-Plattformfähigkeit. Ein gezielt vertrauter
`UserPromptSubmit`-Hook blockiert die synthetische Eingabe jetzt reproduzierbar
in der gepinnten Runtime. Das Gate liefert `promptHook.status: passed`,
`hookStatus: blocked` und dieselbe Session mit korrelierter Turn-ID.

Weiter offen ist die Anbindung an aktuelle Repository Authorization und Control
Lease, die Absicherung nativer Tool-Aktionen und das sichere Öffnen mit
Ereignisrückführung. Der Test behauptet ausdrücklich keine vollständige
Lease-Integration; die eigentliche Issue-Bearbeitung bleibt noch offen.
Die Arbeit gehört weiterhin zum Microsoft Agent Framework Pilot. Es ist
keine neue Framework-Entscheidung oder Freigabe des Nutzers erforderlich.

[Hook-Nachweis und verbleibende Arbeit](../../../../openspec/changes/archive/2026-09-13-prove-real-codex-runtime/preflight-history.md#follow-up-2026-09-13-trusted-prompt-hook)

### 2026-09-13 — Native Fortsetzung umgesetzt

Der oben dokumentierte Zwischenstand ist überholt. Die fehlende Integration ist
jetzt implementiert und über die echte native Codex-TUI geprüft. Maßgeblich
blieben PRD und bestehende Tickets; es war keine neue Entscheidung nötig.
Details stehen in der aktuellen Abnahmeübersicht.

### 2026-09-13 — Abschluss

143 Tests der Gesamtregression und drei ergänzende native Prüfungen bestehen
(144 unterschiedliche Tests insgesamt). Der zusätzliche Test beendet API und
Adapter hart und stellt die ausstehenden Ereignisse unter derselben Session in
der zentralen Historie wieder her. Locked Restore und Build ohne Warnungen,
strikte OpenSpec-Validierung und der begrenzte Diff-Check sind erfolgreich.
Ticket 10 ist damit umgesetzt und verifiziert. Es wurden weder eine PR
veröffentlicht noch der OpenSpec-Change archiviert.

## Acceptance

**Akzeptiert und abgeschlossen (2026-09-13).** Der Benutzer hat die Umsetzung
akzeptiert und die Archivierung von `prove-real-codex-runtime` einschließlich
Commit und Push beauftragt. Die 144 unterschiedlichen erfolgreichen Tests und
die öffentlichen Nachweise sind in der verlinkten Abnahmeübersicht dokumentiert.
