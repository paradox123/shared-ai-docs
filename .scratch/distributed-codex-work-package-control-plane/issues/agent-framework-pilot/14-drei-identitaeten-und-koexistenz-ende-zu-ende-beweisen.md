# 14: Drei Identitäten und Koexistenz Ende-zu-Ende beweisen

**What to build:** Drei menschliche Identitäten durchlaufen einen vollständigen Fehler-, Codex-Übergabe-, Fortsetzungs-, Qualification- und Approval-Fall im zusätzlichen Agent-Framework-Piloten, während der bestehende LangGraph-Pilot unverändert und unabhängig ausführbar bleibt.

**Blocked by:** 07: Eine aktive Agentenoperation gezielt steuern; 08: Steuerung atomar übertragen oder übernehmen; 09: Nach einem Abbruch sicher reconnecten und den Run exportieren; 12: Unvollständige Evidence korrigieren und den Run konvergieren; 13: Einen Head durch Reviews und begrenzte Reparatur qualifizieren

**Status:** ready-for-agent

- [ ] Identität A startet einen autorisierten synthetischen Issue-Run; der Agent führt mehrere sichtbare Schritte und einen adoptierbaren externen Effekt aus und scheitert anschließend kontrolliert.
- [ ] Identität B öffnet denselben Run von einem anderen Client, übernimmt atomar die Control Lease und öffnet den konkreten fehlgeschlagenen Attempt in Codex.
- [ ] Der Codex-Übergabenachweis verwendet dieselbe Session, wenn unterstützt, oder nach expliziter Bestätigung einen gekennzeichneten Handoff-Fork; alle Folgeereignisse erscheinen im ursprünglichen Run.
- [ ] Identität B setzt den Lauf bewusst fort, erzeugt einen neuen Head und durchläuft Evidence, gegebenenfalls Evidence-Correction, deterministische Verifikation und drei isolierte Reviews.
- [ ] Identität C erteilt für exakt den qualifizierten Head über eine interaktive authentifizierte Aktion genau ein menschliches Approval.
- [ ] Ein Hintergrundmonitor erkennt und meldet Bereitschaft, kann aber weder Approval noch Mark-ready, Merge, Deployment oder Release im Namen eines Menschen ausführen.
- [ ] Jeder Agentenaufruf weist seine extern freigegebene Agent-Definition-Revision aus; eine ungeprüfte Revision wird nicht verwendet und die Agent Evolution Loop kann ihr eigenes Approval weder erzeugen noch simulieren.
- [ ] Abbruch-/Neustart-, Cursor-, Stale-Head-, Fencing-, Redaction-, Artefakt- und Exportnachweise bleiben über öffentliche Oberflächen korreliert.
- [ ] Vorher-/Nachher-Prüfung zeigt keine Änderung an LangGraph-Code, Cloudflare, macOS-Diensten, LangGraph-Laufzeitdaten oder -Worktrees, GitHub-Konfiguration und ProBara CRM.
- [ ] Der Abschluss dokumentiert eine Go-/Stop-Entscheidung für den Microsoft-Kandidaten; bei Stop bleibt LangGraph bestehen und es wird kein nicht freigegebener Ersatz begonnen.

## Session lesson

Die frühere Oversight-Automation konnte den nominell menschlichen PR-Gate übernehmen. Dieser Test verlangt eine echte dritte Person und beweist zugleich, dass `Open in Codex` keine neue unkontrollierte Agenten- oder Merge-Strecke eröffnet.
