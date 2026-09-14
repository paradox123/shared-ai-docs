# 10: Bereitschaft zustellen und den aktuellen Head menschlich freigeben

**What to build:** Sobald ein Hintergrundrun einen qualifizierten Head erreicht, wird der zuständige Mensch über seinen lokalen Agenten darauf aufmerksam und kann genau diesen Head interaktiv in der GUI freigeben.

**Blocked by:** 04: Handover im lokalen Agenten öffnen und Diagnose zentral erfassen; 06: Control Lease zwischen Menschen in der GUI übergeben; 09: Eingereichtes Issue unbeaufsichtigt bis Intervention oder Review bearbeiten.

**Status:** ready-for-agent

- [ ] Ein serverseitig festgestellter qualifizierter Stand erzeugt eine dauerhafte Bereitschaftsanfrage, die in der Inbox und über den Workstation-Handover sichtbar wird; Routinefortschritt erzeugt keine ständig neuen Assistenzsessions.
- [ ] Der Mensch sieht exakten Head, deterministische Prüfungen, unabhängige Review-Ergebnisse und relevante Evidence vor der interaktiven Freigabe.
- [ ] Die Freigabe erfordert eine aktuell authentifizierte, berechtigte menschliche Aktion und die Control Lease; Worker, lokaler Diagnoseagent und Zustellclient dürfen diese Aktion nicht stellvertretend auslösen.
- [ ] Head-Wechsel während offener Freigabeansicht macht die angezeigte Qualifikation ungültig und verhindert die stale Freigabe. Wiederholte Übermittlung derselben menschlichen Entscheidung erzeugt kein zweites Approval.
- [ ] Freigabe und Ablehnung/ausstehende Entscheidung bleiben samt Identität und Head in der Historie; eine Freigabe startet weder Mark-ready noch Merge, Deployment oder Release.
- [ ] Die Abnahme zeigt eine reale interaktive Freigabe sowie einen abgelehnten Stale-Head-Fall; Besitz eines menschlichen Tokens allein wird nicht als Nachweis einer menschlichen Aktion ausgegeben.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
