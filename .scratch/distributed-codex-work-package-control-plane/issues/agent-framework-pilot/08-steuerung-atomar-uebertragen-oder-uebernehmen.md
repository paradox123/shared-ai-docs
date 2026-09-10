# 08: Steuerung atomar übertragen oder übernehmen

**What to build:** Zwei Contributor können die Verantwortung für einen laufenden Run freiwillig übertragen oder per Forced Takeover wechseln, ohne überlappende Schreibrechte und ohne die aktuelle Agentensession unbeabsichtigt zu verändern.

**Blocked by:** 03: Repositoryzugriff und exklusive Steuerung durchsetzen; 06: Eine Human Request beantworten und die Session in Codex fortsetzen

**Status:** ready-for-agent

- [ ] Ein Beobachter kann einen Transfer anfragen, erhält dadurch aber noch keine mutierenden Rechte.
- [ ] Nur der aktuelle Inhaber kann die aktuelle Anfrage bewilligen oder ablehnen; eine gültige Bewilligung wechselt die Lease atomar.
- [ ] Ein anderer Contributor kann ohne zusätzliche Administratorrolle einen ausdrücklich gekennzeichneten Forced Takeover ausführen.
- [ ] Transfer und Forced Takeover erhöhen die Lease-Epoche und machen alte Tokens, offene mutierende Requests und verspätete Commands des bisherigen Inhabers unwirksam.
- [ ] Bei mindestens 20 konkurrierenden Übernahmeversuchen wird pro erwarteter Epoche höchstens genau einer akzeptiert.
- [ ] Der Verantwortungswechsel verändert für sich allein weder Workflowphase, Activity Attempt, Codex-Session, Head noch bereits akzeptierte externe Wirkung.
- [ ] Der bisherige Inhaber bleibt bei fortbestehendem Repository-Lesezugriff Beobachter und sieht den Wechsel mit altem/neuem Inhaber, Zeitpunkt, Grund und Übergabeart.
- [ ] Eine bereits in Codex geöffnete schreibende Session des alten Inhabers wird gefenced und kann den Run nach dem Wechsel nicht weiter mutieren.

## Session lesson

„Eine Session übernehmen“ wird fachlich als Übernahme der Run-Steuerung modelliert. Der Prozess oder das Fenster selbst wechselt nicht den Besitzer; seine Schreibfähigkeit folgt der aktuellen Lease.
