# 05: Repository-Base und externe Wirkungen sicher reconciliieren

**What to build:** Ein sequenzieller Run beginnt auf der provider-autoritativen Base und übernimmt nach einem Crash bereits eingetretene Git-, Provider- oder Sessionwirkungen, statt sie zu wiederholen oder den Repositorybetrieb dauerhaft zu blockieren.

**Blocked by:** 04: Einen Fake-Codex-Versuch transparent scheitern und wiederherstellen

**Status:** resolved

- [x] Nach Abschluss eines Vorgängers startet der Nachfolger erst, wenn aufgezeichnete erwartete Base und lokal verfügbare Base exakt dem aktuellen Provider-Head entsprechen.
- [x] Eine absichtlich veraltete lokale Referenz erzeugt einen sichtbaren Preflight-Blocker und keinen Agentenstart.
- [x] Jeder kontrollierte externe Effekt besitzt eine stabile Operation-ID, einen nachlesbaren Receipt und einen deterministischen Reconciliation-Pfad.
- [x] Ein Crash unmittelbar nach erfolgreichem Effekt und vor gespeichertem Aktivitätsergebnis führt zur Adoption genau dieses Effekts; dessen Zähler bleibt eins.
- [x] Mehrdeutige oder widersprüchliche Effekte werden nicht geraten, sondern als konkreter menschlicher Entscheidungsfall sichtbar.
- [x] Retry, Retire, Reconcile und Adopt sind über die öffentliche Operator-Oberfläche verfügbar; manuelle Laufzeitdatenbankänderungen sind kein Abnahmeweg.
- [x] Ein terminaler oder retirierter Run entfernt aktive Projektionen und gibt die Repository-Serialisierung entsprechend der Policy frei.

## Session lesson

ProBara Issue #3 startete vom veralteten lokalen `main`; später waren SQLite-Eingriffe nötig, um den blockierten Lauf zu retiren. Beide Fehler werden in diesem Slice geschlossen.


## Outcome

2026-09-11: Auf `main` implementiert, OpenSpec `reconcile-repository-effects`.
59/59 lokale Regressionstests, Build ohne Warnungen/Fehler, strikte OpenSpec-Validierung und beide unabhängigen Reviews grün.

Reale SIGKILLs nach Git-, Provider- und Sessionwirkung ergeben jeweils genau einen externen Effekt. Stale Base blockiert vor dem Agentenstart. Retry, Reconcile, Adopt und Retire sind über HTTP/CLI belegt; aktive Projektionen und Repository-Ownership werden sicher freigegeben. Historische Standalone-Sessions können keine spätere Base-Provenance erhalten.

- [Kompakter Beweis mit Receipts und SHA-Verlauf](../../evidence/ticket-05-proof-2026-09-11/proof.md)
- [OpenSpec-Evidence und Grenzen](../../../../openspec/changes/reconcile-repository-effects/implementation-evidence.md)

Kontrollierter Provider/Fake-Codex, echtes Git/PostgreSQL und explizite lokale Worker-Zustellung. Der Change bleibt bis zur Abnahme unarchiviert.
