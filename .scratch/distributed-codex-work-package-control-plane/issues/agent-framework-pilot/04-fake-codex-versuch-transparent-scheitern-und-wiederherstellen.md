# 04: Einen Fake-Codex-Versuch transparent scheitern und wiederherstellen

**What to build:** Ein kontrollierter Fake-Codex-Versuch führt mehrere sichtbare Schritte aus, scheitert und bleibt für einen anderen Operator nach Workerwechsel vollständig diagnostizierbar, ohne still eine zweite Session zu starten.

**Blocked by:** 02: Ein autorisiertes Issue als beobachtbaren Run annehmen

**Status:** resolved

- [x] Der Run startet eine externe Fake-Agentensession mit stabiler Session-, Aktivitäts- und Attempt-Korrelation; regelbasierte Arbeit wird nicht an einen Modellagenten delegiert.
- [x] Nummerierte Nachrichten, Toolaufrufe, Ergebnisse, Artefaktverweise und ein kontrollierter Fehler erscheinen redigiert und kausal geordnet in der Run History.
- [x] Ein Workerabbruch nach Sessionstart und vor Aktivitätsergebnis wird von einem zweiten Worker übernommen, ohne eine zweite Session oder doppelte Aktivität zu erzeugen.
- [x] Ein gültiges redigiertes `blocked`-Ergebnis bleibt als Originalbeobachtung erhalten, auch wenn nachgelagerte Verarbeitung es ablehnt; Ablehnung und Original werden getrennt dargestellt.
- [x] Prozessfehler, Timeout, Transportfehler, Vertragsinkompatibilität, Schemafehler, gültiger Blockzustand und Infrastrukturfehler sind öffentlich unterscheidbar.
- [x] Der Operator kann den konkreten Attempt auswählen und sieht dessen Sessionstatus sowie die verfügbare `Open in Codex`-Semantik; ein Adapter darf eine nicht unterstützte Same-Session-Öffnung nicht vortäuschen.
- [x] App-Task-Sichtbarkeit ist keine Voraussetzung für die gemeinsame History, aber fehlende direkte Öffnungsfähigkeit wird als konkrete Capability ausgewiesen.

## Session lesson

Im LangGraph-Piloten waren Headless-Sessions nicht regulär als Codex-App-Tasks sichtbar und ein gültiges Worker-Ergebnis ging hinter einem generischen Fehler verloren. Beide Fälle werden hier als öffentliche Produktzustände reproduziert.


## Outcome

**Completed (2026-09-11).** OpenSpec-Change `recover-fake-codex-attempt` implementiert
den kontrollierten externen Fake-Versuch über reguläre Agent-Framework-Executors,
dauerhafte Startabsicht, idempotente Session-Zuordnung und redigierte History.
Echte SIGKILL-Tests vor/nach Session-Mapping sowie nach Ergebniserfassung beweisen
den Wiederanlauf mit derselben Session und getrennt erhaltener Originalbeobachtung
und Ablehnung. HTTP/CLI erlauben die autorisierte Attempt-Auswahl; der Fake weist
Same-Session-Öffnung in Codex ausdrücklich als nicht unterstützt aus.

42 lokale Regressionstests und die strikte OpenSpec-Validierung sind grün. Die
Recovery wurde durch explizit gestartete Ersatz-Worker am lokalen MAF-Graphen
geprüft; eine neue automatische DTS-Orchestrierung oder echte Codex-App-Integration
ist nicht Bestandteil dieses Nachweises.

- [OpenSpec-Evidence](../../../../openspec/changes/archive/2026-09-11-recover-fake-codex-attempt/implementation-evidence.md)
- [Öffentliche Black-Box-Tests](../../../../microsoft-agent-framework-work-package-pilot/tests/test_fake_codex_attempt.py)


## Acceptance

2026-09-11: Vom Benutzer nach dem reproduzierten Prozessnachweis akzeptiert.
OpenSpec im Standardverfahren archiviert; die vier Anforderungen sind in der
[kanonischen Spec](../../../../openspec/specs/recoverable-fake-codex-attempt/spec.md)
übernommen. Der abschließende Regressionstest bestand erneut mit 42/42 Tests.
