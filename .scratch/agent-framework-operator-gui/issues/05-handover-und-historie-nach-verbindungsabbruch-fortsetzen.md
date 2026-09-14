# 05: Handover und lokale Historie nach Verbindungsabbruch fortsetzen

**What to build:** Ein zeitweise ausgeschalteter oder getrennter Workstation Client erhält weiterhin offene Handovers und synchronisiert seine bereits entstandene Agentenhistorie nachvollziehbar nach.

**Blocked by:** 04: Handover im lokalen Agenten öffnen und Diagnose zentral erfassen.

**Status:** ready-for-agent

- [ ] Ein offline adressierter Handover bleibt zentral als ausstehend sichtbar; nach Wiederverbindung werden Aktualität der Anfrage und aktuelle Zugriffsberechtigung geprüft, bevor die Session geöffnet wird.
- [ ] Abbruch nach erfolgreichem Öffnen, aber vor Empfangsbestätigung, wird durch Abgleich der vorhandenen Session behoben. Wiederholte Trigger oder mehrere Clientverbindungen erzeugen keine unabhängigen Duplikatsessions.
- [ ] Bereits beobachtete, noch nicht bestätigte Chat-/Toolereignisse werden unter der geltenden Redaktionsregel dauerhaft gepuffert und nach Client-/Server-Neustart genau einmal zentral übernommen.
- [ ] Stabile Ereignisidentitäten, Reihenfolge innerhalb einer Quellsession sowie kausale Verknüpfungen bleiben erhalten; die Anzeige behauptet keine erfundene globale Echtzeitreihenfolge über getrennte Geräte.
- [ ] Die GUI unterscheidet ausstehende Zustellung, fehlgeschlagenes Öffnen und ausstehende Historiensynchronisierung. Eine Aktivität mit bekannten Erfassungslücken wird nicht als vollständig dokumentiert bezeichnet.
- [ ] Öffnungsfehler bieten einen unterstützten erneuten Zustellversuch; eine inzwischen beantwortete oder widerrufene Anfrage startet beim Reconnect keine veraltete Assistenz.
- [ ] Öffentliche Tests unterbrechen Verbindung und Prozesse an Zustellungs-/Bestätigungsgrenzen und vergleichen Quellereignisse, zentrale Historie, Sessionidentitäten und gerenderte Zustände.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
