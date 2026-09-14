# 07: Intervention per GUI oder lokalem Agenten beantworten

**What to build:** Der steuernde Mensch beantwortet eine konkrete Interventionsanfrage entweder grafisch oder mit Unterstützung seines lokalen Agenten; dieselbe zentrale Session verarbeitet die Antwort und der Run wird fortgesetzt.

**Blocked by:** 04: Handover im lokalen Agenten öffnen und Diagnose zentral erfassen; 06: Control Lease zwischen Menschen in der GUI übergeben.

**Status:** ready-for-agent

- [ ] Eine dauerhafte grafische Inbox zeigt die Anfrage mit Kontext, Zielaktivität/-versuch, Session, aktuellem Head und zuständigem Menschen.
- [ ] GUI und lokaler Agent verwenden denselben kontrollierten Antwort-/Resume-Vertrag. Der lokale Agent benötigt eine menschliche Anweisung für die mutierende Intervention.
- [ ] Die Antwort wird unter aktueller Repository Authorization, Control Lease und Zielversion genau einmal akzeptiert und an die zugehörige zentrale Session zugestellt; kein unkorrelierter Implementierungslauf entsteht.
- [ ] Die lokale Unterhaltung einschließlich Diagnose, menschlicher Anweisung, Toolaufrufen und Antwort bleibt vollständig beobachtbar; zentrale Antwortverarbeitung und anschließende Ausführung sind im selben Run verknüpft.
- [ ] Ein veralteter Head, inzwischen beantworteter Request, geändertes Ziel oder veraltete Lease erzeugt eine konkrete Ablehnung statt einer stillen Fortsetzung des falschen Versuchs.
- [ ] Nach Antwort kann ein bereits wartender zentraler Ablauf ohne manuelle Prozessauswahl weiterarbeiten. Ein Test mit geschlossener GUI beantwortet lokal und liest das Ergebnis danach über einen anderen autorisierten Client.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
