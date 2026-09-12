# 08: Steuerung atomar übertragen oder übernehmen

**What to build:** Zwei Contributor können die Verantwortung für einen laufenden Run freiwillig übertragen oder per Forced Takeover wechseln, ohne überlappende Schreibrechte und ohne die aktuelle Agentensession unbeabsichtigt zu verändern.

**Blocked by:** 03: Repositoryzugriff und exklusive Steuerung durchsetzen; 06: Eine Human Request beantworten und die Session in Codex fortsetzen

**Status:** resolved

- [x] Ein Beobachter kann einen Transfer anfragen, erhält dadurch aber noch keine mutierenden Rechte.
- [x] Nur der aktuelle Inhaber kann die aktuelle Anfrage bewilligen oder ablehnen; eine gültige Bewilligung wechselt die Lease atomar.
- [x] Ein anderer Contributor kann ohne zusätzliche Administratorrolle einen ausdrücklich gekennzeichneten Forced Takeover ausführen.
- [x] Transfer und Forced Takeover erhöhen die Lease-Epoche und machen alte Tokens, offene mutierende Requests und verspätete Commands des bisherigen Inhabers unwirksam.
- [x] Bei mindestens 20 konkurrierenden Übernahmeversuchen wird pro erwarteter Epoche höchstens genau einer akzeptiert.
- [x] Der Verantwortungswechsel verändert für sich allein weder Workflowphase, Activity Attempt, Codex-Session, Head noch bereits akzeptierte externe Wirkung.
- [x] Der bisherige Inhaber bleibt bei fortbestehendem Repository-Lesezugriff Beobachter und sieht den Wechsel mit altem/neuem Inhaber, Zeitpunkt, Grund und Übergabeart.
- [x] Eine bereits in Codex geöffnete schreibende Session des alten Inhabers wird gefenced und kann den Run nach dem Wechsel nicht weiter mutieren.

## Session lesson

„Eine Session übernehmen“ wird fachlich als Übernahme der Run-Steuerung modelliert. Der Prozess oder das Fenster selbst wechselt nicht den Besitzer; seine Schreibfähigkeit folgt der aktuellen Lease.


## Outcome

Implementiert am 2026-09-12 im isolierten .NET-Piloten mit OpenSpec-Change
`transfer-run-control-atomically`. HTTP/CLI bieten Transfer-Anfrage,
Bewilligung/Ablehnung und ausdrücklich begründeten Forced Takeover. Die
laufweite Lease wechselt atomar; Empfängerrechte werden bei Bewilligung erneut
geprüft. Alte Inhaber bleiben Beobachter und können auch aus einer bereits
geöffneten Session keine neue Schreibwirkung auslösen.

Öffentliche Prozessnachweise belegen zwei Runden mit jeweils 20 konkurrierenden
Übernahme-Requests über zwei API-Prozesse, einen echten API-SIGKILL während einer
Adapter-Schreibanfrage, unveränderte Sessions/Attempts/Heads/Git- und
Providerwirkungen sowie die einmalige Übernahme bereits akzeptierter externer
Receipts. Wartende Live-Kommandos werden gesperrt; bereits angenommene
Continuation-/Recovery-Entscheidungen müssen vor einem Verantwortungswechsel
ihre bestehende Wirkung klären. Solange dies aussteht, antwortet die API mit
einem konkreten Pending-Konflikt und behält die bisherige Lease.

Abschlussprüfung: 104 Tests grün, Build erfolgreich, OpenSpec Strict Validation
und Diff-Check grün. Standards- und Spec-Review nach Korrekturen ohne offene
Findings.

Die Nachweise verwenden kontrollierte externe GitHub-/Codex-Adapter sowie echtes
Wegwerf-PostgreSQL und lokale Git-Repositories. Realer Codex-App-/GitHub-Zugriff
bleibt Teil der Tickets 10/14. Der Change bleibt zur menschlichen Abnahme offen;
er wurde nicht archiviert.

- [Akzeptanzübersicht und getrennte Review-Ergebnisse](../../../../openspec/changes/transfer-run-control-atomically/implementation-evidence.md)
- [Gespeicherte öffentliche Nachweise](../../evidence/ticket-08-proof-2026-09-12/)
- [HTTP-/CLI-Verhaltenstests](../../../../microsoft-agent-framework-work-package-pilot/tests/test_control_transfer.py)
- [Operator-Bedienung und Recovery-Grenzen](../../../../microsoft-agent-framework-work-package-pilot/README.md)
