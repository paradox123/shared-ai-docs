# 11: Den lokalen Piloten unter macOS automatisch betreiben

**What to build:** Nach Daniels macOS-Anmeldung startet der lokale Pilot ohne manuellen Eingriff, stellt seine Verbindung nach aussen her und erholt sich innerhalb seiner Betriebsgrenzen von abgestuerzten Prozessen.

**Blocked by:** 10: Nach laengerer Mac-Abwesenheit einmalig reconciliieren

**Covers:** US 27-28, 68-69

**Status:** resolved

- [x] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [x] Ein benutzerspezifischer LaunchAgent startet nach Daniels Anmeldung den benoetigten lokalen Stack einschliesslich Tunnel, Receiver und Workflow-Worker.
- [x] Unerwartet beendete lokale Prozesse werden kontrolliert neu gestartet, ohne eine neue Boot-Session, einen zweiten Reconciliation-Lauf oder doppelte Issue-Verarbeitung zu erzeugen.
- [x] Betriebsstatus und redigierte, korrelierbare Fehler sind lokal nachvollziehbar; Secrets, Tokens und private Payloads werden weder versioniert noch in Logs ausgegeben.
- [x] Der Betrieb benoetigt keine eingehende Router-Freigabe und bleibt auf den benannten ausgehenden Tunnel und den vorgesehenen lokalen Receiver begrenzt.
- [x] Ein Startnachweis zeigt, dass der Stack nach Anmeldung ohne manuellen Prozessstart eine gueltige Delivery verarbeiten kann.
- [x] Ein Recovery-Nachweis beendet mindestens einen verwalteten Prozess und beweist danach ueber die oeffentliche Workflow-Wirkung, dass er neu gestartet und eine Delivery genau einmal verarbeitet wurde.
- [x] Installations- und Betriebsanweisungen benennen die kostenlose 24-Stunden-Grenze, Startup-Reconciliation, lokale Diagnoseoberflaechen und die ausserhalb der Automatisierung verbleibenden menschlichen Schritte.

Accepted and archived through OpenSpec change `2026-08-23-operate-local-pilot-with-launchd`; criterion-level evidence is recorded in `openspec/changes/archive/2026-08-23-operate-local-pilot-with-launchd/implementation-evidence.md`.

## Answer

The pilot now ships one repeatable per-user LaunchAgent that starts one receiver/workflow-worker and one named outbound Tunnel after GUI login. Its supervisor replaces the whole stack after an unexpected child exit while the existing SQLite, LangGraph, boot-reconciliation, and command-idempotency identities make restart convergent. Private declarative configuration, loopback/exact-route validation, discarded child output, fixed-schema private state/logs, and public status/read-back provide the bounded operating surface. Real temporary launchd acceptance proved signed-delivery startup and pilot `SIGKILL` recovery with one run and one controlled GitHub effect; real credentials, Cloudflare/GitHub activation, and a physical logout/login observation remain documented human steps before Issue 12 goes live.
