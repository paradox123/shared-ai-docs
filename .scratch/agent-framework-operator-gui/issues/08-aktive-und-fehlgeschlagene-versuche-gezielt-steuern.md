# 08: Aktive und fehlgeschlagene Versuche gezielt steuern

**What to build:** Ein Mensch greift aus der GUI oder über seinen lokalen Agenten gezielt in einen ausgewählten Aktivitätsversuch ein und nutzt die bestehenden Fortsetzungs- und Codex-Öffnungswege.

**Blocked by:** 07: Intervention per GUI oder lokalem Agenten beantworten.

**Status:** ready-for-agent

- [ ] Für geeignete Zustände sind Queue, Interrupt, Fork, Fresh Retry und Cancel mit explizitem Zielversuch verfügbar; die Oberfläche zeigt Zielsession, Head, Folgen und tatsächlich unterstützte Optionen.
- [ ] Queue erhält die akzeptierte Reihenfolge; Interrupt beendet und fenced die laufende Operation, gleicht bereits erfolgte Wirkungen ab und verarbeitet den akzeptierten Command anschließend genau einmal.
- [ ] Fork zeigt neue Session und Herkunft, Fresh Retry startet ohne automatischen Gesprächsübertrag, Cancel beendet den ausgewählten Umfang mit dokumentiertem Grund. Vorherige Historie bleibt lesbar.
- [ ] Open in Codex auf einem konkreten zentralen Versuch bewahrt die bestehende Same-Session-Semantik oder verlangt die vorgesehene explizite Bestätigung eines gekennzeichneten Handoff-Forks. Die automatisch geöffnete lokale Diagnose wird nicht als solche Same-Session-Öffnung ausgegeben.
- [ ] GUI und lokale Agentensteuerung beachten dieselben menschlichen Weisungen, Berechtigungen und Fencing-Grenzen; sämtliche beobachtbaren Folgeereignisse bleiben zugeordnet.
- [ ] Ein realer kontrollierter Agentenversuch sowie gezielte Fehler-/Race-Tests beweisen Zustellung und tatsächliche Sessionidentitäten. Nicht unterstützte Aktionen werden ehrlich abgelehnt statt nur als wirkungslose Schaltflächen angezeigt.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
