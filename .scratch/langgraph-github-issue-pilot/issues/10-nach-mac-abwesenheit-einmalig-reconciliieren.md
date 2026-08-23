# 10: Nach laengerer Mac-Abwesenheit einmalig reconciliieren

**What to build:** War der lokale Stack mindestens 24 Stunden inaktiv, gleicht der Mac beim naechsten Boot genau einmal den aktuellen GitHub-Zustand ab und fuehrt verpasste Arbeit ohne Doppelverarbeitung in den normalen Workflow zurueck.

**Blocked by:** 08: Aktive Workflows nach Prozessabbruch zuverlaessig fortsetzen; 09: GitHub-Webhooks 24 Stunden ueber Cloudflare zustellen

**Covers:** US 23-26, 56-57, 69

**Status:** resolved

- [x] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [x] Der lokale Stack fuehrt einen dauerhaften `last_alive_at`-Zeitpunkt und eine Boot-Session-ID, ohne einen Prozessneustart mit einem neuen Mac-Boot zu verwechseln.
- [x] Nach mindestens 24 Stunden Inaktivitaet startet beim ersten Prozessstart des Boots genau ein Reconciliation-Lauf; bei kuerzerer Inaktivitaet startet keiner.
- [x] Weitere Prozessneustarts im selben Boot loesen keinen zweiten Reconciliation-Lauf aus.
- [x] Reconciliation liest den aktuellen Zustand freigegebener und laufender Issues sowie zugehoeriger Pull Requests und speist nur fehlende Transitionen als synthetische idempotente Kommandos in dieselbe Inbox ein.
- [x] Ein synthetisches Kommando und eine spaet eintreffende Queue-Delivery fuer denselben fachlichen Zustand erzeugen zusammen genau eine Wirkung.
- [x] Nach Abschluss kehrt der Pilot in den rein ereignisgetriebenen Betrieb zurueck; es gibt kein periodisches GitHub-Polling.
- [x] Verhaltenstests mit kontrollierbarer Uhr, Boot-ID und GitHub-Zustand sowie realer Persistenz beweisen die Zeitgrenze, Einmaligkeit pro Boot und beide Reihenfolgen der Queue-/Reconciliation-Konkurrenz.

Accepted and archived through OpenSpec change `2026-08-23-reconcile-after-mac-absence`; criterion-level evidence is recorded in `openspec/changes/archive/2026-08-23-reconcile-after-mac-absence/implementation-evidence.md`.

## Answer

The pilot now records durable liveness and one operating-system boot identity, reconciles exactly once after a measured absence of at least 24 hours, resumes an interrupted reconciliation within the same boot, and returns missed ready issues or human-merged active pull requests through the ordinary inbox and workflow dispatcher. Semantic command identities make delayed Queue deliveries and synthetic commands converge in either order, while the idle heartbeat writes only SQLite and normal GitHub operation remains event-driven.
