# 04: Einen Fake-Codex-Versuch transparent scheitern und wiederherstellen

**What to build:** Ein kontrollierter Fake-Codex-Versuch führt mehrere sichtbare Schritte aus, scheitert und bleibt für einen anderen Operator nach Workerwechsel vollständig diagnostizierbar, ohne still eine zweite Session zu starten.

**Blocked by:** 02: Ein autorisiertes Issue als beobachtbaren Run annehmen

**Status:** ready-for-agent

- [ ] Der Run startet eine externe Fake-Agentensession mit stabiler Session-, Aktivitäts- und Attempt-Korrelation; regelbasierte Arbeit wird nicht an einen Modellagenten delegiert.
- [ ] Nummerierte Nachrichten, Toolaufrufe, Ergebnisse, Artefaktverweise und ein kontrollierter Fehler erscheinen redigiert und kausal geordnet in der Run History.
- [ ] Ein Workerabbruch nach Sessionstart und vor Aktivitätsergebnis wird von einem zweiten Worker übernommen, ohne eine zweite Session oder doppelte Aktivität zu erzeugen.
- [ ] Ein gültiges redigiertes `blocked`-Ergebnis bleibt als Originalbeobachtung erhalten, auch wenn nachgelagerte Verarbeitung es ablehnt; Ablehnung und Original werden getrennt dargestellt.
- [ ] Prozessfehler, Timeout, Transportfehler, Vertragsinkompatibilität, Schemafehler, gültiger Blockzustand und Infrastrukturfehler sind öffentlich unterscheidbar.
- [ ] Der Operator kann den konkreten Attempt auswählen und sieht dessen Sessionstatus sowie die verfügbare `Open in Codex`-Semantik; ein Adapter darf eine nicht unterstützte Same-Session-Öffnung nicht vortäuschen.
- [ ] App-Task-Sichtbarkeit ist keine Voraussetzung für die gemeinsame History, aber fehlende direkte Öffnungsfähigkeit wird als konkrete Capability ausgewiesen.

## Session lesson

Im LangGraph-Piloten waren Headless-Sessions nicht regulär als Codex-App-Tasks sichtbar und ein gültiges Worker-Ergebnis ging hinter einem generischen Fehler verloren. Beide Fälle werden hier als öffentliche Produktzustände reproduziert.
