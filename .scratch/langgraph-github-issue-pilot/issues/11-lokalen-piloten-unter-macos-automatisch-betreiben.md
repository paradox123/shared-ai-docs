# 11: Den lokalen Piloten unter macOS automatisch betreiben

**What to build:** Nach Daniels macOS-Anmeldung startet der lokale Pilot ohne manuellen Eingriff, stellt seine Verbindung nach aussen her und erholt sich innerhalb seiner Betriebsgrenzen von abgestuerzten Prozessen.

**Blocked by:** 10: Nach laengerer Mac-Abwesenheit einmalig reconciliieren

**Covers:** US 27-28, 68-69

**Status:** ready-for-agent

- [ ] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [ ] Ein benutzerspezifischer LaunchAgent startet nach Daniels Anmeldung den benoetigten lokalen Stack einschliesslich Tunnel, Receiver und Workflow-Worker.
- [ ] Unerwartet beendete lokale Prozesse werden kontrolliert neu gestartet, ohne eine neue Boot-Session, einen zweiten Reconciliation-Lauf oder doppelte Issue-Verarbeitung zu erzeugen.
- [ ] Betriebsstatus und redigierte, korrelierbare Fehler sind lokal nachvollziehbar; Secrets, Tokens und private Payloads werden weder versioniert noch in Logs ausgegeben.
- [ ] Der Betrieb benoetigt keine eingehende Router-Freigabe und bleibt auf den benannten ausgehenden Tunnel und den vorgesehenen lokalen Receiver begrenzt.
- [ ] Ein Startnachweis zeigt, dass der Stack nach Anmeldung ohne manuellen Prozessstart eine gueltige Delivery verarbeiten kann.
- [ ] Ein Recovery-Nachweis beendet mindestens einen verwalteten Prozess und beweist danach ueber die oeffentliche Workflow-Wirkung, dass er neu gestartet und eine Delivery genau einmal verarbeitet wurde.
- [ ] Installations- und Betriebsanweisungen benennen die kostenlose 24-Stunden-Grenze, Startup-Reconciliation, lokale Diagnoseoberflaechen und die ausserhalb der Automatisierung verbleibenden menschlichen Schritte.
