# 06: Control Lease zwischen Menschen in der GUI übergeben

**What to build:** Berechtigte Menschen beanspruchen oder wechseln die Steuerung eines bestehenden Runs grafisch, während alle Beobachter denselben nachvollziehbaren Verantwortungsstand sehen.

**Blocked by:** 02: Eingereichtes Issue als erste Hintergrundaktivität starten.

**Status:** ready-for-agent

- [ ] Die GUI zeigt aktuelle menschliche Identität, Repository Authorization, Control-Lease-Inhaber und erlaubte Aktionen für den ausgewählten Run.
- [ ] Claim, Release, Übernahmeanfrage, Bewilligung oder Ablehnung einer freiwilligen Übergabe sowie expliziter Forced Takeover sind ohne manuelle CLI-Kommandos ausführbar.
- [ ] Jeder Wechsel bleibt atomar und mit bisherigem/neuem Inhaber in der zentralen Historie sichtbar; die Lease gilt für den ganzen Run einschließlich paralleler Aktivitäten.
- [ ] Nach einem Wechsel werden konkurrierende oder verspätete Mutationen des bisherigen Inhabers serverseitig gefenced; die GUI zeigt den aktuellen Zustand und den Ablehnungsgrund.
- [ ] Browserabbruch gibt die menschlich gebundene Lease nicht frei. Widerrufene Repositoryrechte können nicht über eine alte Clientverbindung weitergenutzt werden.
- [ ] Zwei unterschiedlich berechtigte authentifizierte Menschen und eine nur lesende Identität beweisen den Vorgang über öffentliche Schnittstellen und sichtbare GUI-Aktionen; Testidentitäten dürfen im kontrollierten Regressionstest simuliert werden, gelten aber nicht als Ticket-14-Identitätsnachweis.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
