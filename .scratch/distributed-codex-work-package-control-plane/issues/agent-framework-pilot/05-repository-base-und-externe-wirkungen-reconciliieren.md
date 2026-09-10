# 05: Repository-Base und externe Wirkungen sicher reconciliieren

**What to build:** Ein sequenzieller Run beginnt auf der provider-autoritativen Base und übernimmt nach einem Crash bereits eingetretene Git-, Provider- oder Sessionwirkungen, statt sie zu wiederholen oder den Repositorybetrieb dauerhaft zu blockieren.

**Blocked by:** 04: Einen Fake-Codex-Versuch transparent scheitern und wiederherstellen

**Status:** ready-for-agent

- [ ] Nach Abschluss eines Vorgängers startet der Nachfolger erst, wenn aufgezeichnete erwartete Base und lokal verfügbare Base exakt dem aktuellen Provider-Head entsprechen.
- [ ] Eine absichtlich veraltete lokale Referenz erzeugt einen sichtbaren Preflight-Blocker und keinen Agentenstart.
- [ ] Jeder kontrollierte externe Effekt besitzt eine stabile Operation-ID, einen nachlesbaren Receipt und einen deterministischen Reconciliation-Pfad.
- [ ] Ein Crash unmittelbar nach erfolgreichem Effekt und vor gespeichertem Aktivitätsergebnis führt zur Adoption genau dieses Effekts; dessen Zähler bleibt eins.
- [ ] Mehrdeutige oder widersprüchliche Effekte werden nicht geraten, sondern als konkreter menschlicher Entscheidungsfall sichtbar.
- [ ] Retry, Retire, Reconcile und Adopt sind über die öffentliche Operator-Oberfläche verfügbar; manuelle Laufzeitdatenbankänderungen sind kein Abnahmeweg.
- [ ] Ein terminaler oder retirierter Run entfernt aktive Projektionen und gibt die Repository-Serialisierung entsprechend der Policy frei.

## Session lesson

ProBara Issue #3 startete vom veralteten lokalen `main`; später waren SQLite-Eingriffe nötig, um den blockierten Lauf zu retiren. Beide Fehler werden in diesem Slice geschlossen.
