# 09: Eingereichtes Issue unbeaufsichtigt bis Intervention oder Review bearbeiten

**What to build:** Nach einmaligem Start übernimmt der Hintergrundbetrieb den vorhandenen Implementierungs-, Evidence-, Review- und Reparaturpfad und erreicht selbstständig einen konkreten Blocker oder einen qualifizierten Stand.

**Blocked by:** 02: Eingereichtes Issue als erste Hintergrundaktivität starten.

**Status:** ready-for-agent

- [ ] Der über die GUI eingereichte Run wird vom ersten automatisch gestarteten Verarbeitungsschritt durch die vollständige Implementierungs-, Evidence-, Review- und begrenzte Reparaturkette weitergeführt; Browser, Terminal und startende Codex-Hauptsession bleiben geschlossen.
- [ ] Die vorhandenen Worktree-/Base-, Implementierungs-, Evidence-, deterministischen Prüf-, Review- und begrenzten Reparaturverträge werden durchgängig verbunden; nötige Aufträge entstehen aus Aufnahme und geprüfter Konfiguration.
- [ ] Die GUI zeigt tatsächlich beobachtete Aktivitäten und Sessions einschließlich ihrer vollständigen vorhandenen Nachrichten/Toolergebnisse; laufende, wartende, fehlgeschlagene und qualifizierte Zustände bleiben unterscheidbar.
- [ ] Überwachung erkennt Prozessverlust, konkrete blockierende Voraussetzungen und veränderte Heads; bestehende Wiederaufnahme-/Reconciliation-Regeln verhindern doppelte Agenten-/Git-/GitHub-Wirkungen.
- [ ] Nicht sicher auflösbare Zustände erzeugen dauerhafte beantwortbare Interventionen; ausgeschöpfte automatische Runden führen zu einem begrenzten sichtbaren Zustand. Eine neue Vordergrundsession implementiert oder koordiniert den Auftrag nicht ersatzweise.
- [ ] Ein kleines echtes Wegwerf-Issue erreicht bei geschlossenen Startclients einen qualifizierten Stand; ein kontrollierter Fehler erreicht eine konkrete Intervention. Neustart während eines bekannten Effekts beweist Adoption statt Wiederholung.
- [ ] Repository-Serialisierung sowie die Grenzen gegen automatisches menschliches Approval, Merge, Deployment und Release bleiben erhalten.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
