# 08: Aktive Workflows nach Prozessabbruch zuverlaessig fortsetzen

**What to build:** Unterbrochene Implementierungs-, Review- und Feedbacklaeufe setzen nach einem Prozessneustart am letzten dauerhaften Zustand fort, ohne Arbeit, PRs oder GitHub-Projektionen zu duplizieren.

**Blocked by:** 06: Human-Feedback im bestehenden Run weiterbearbeiten; 07: Den vollstaendigen probare-crm-Backlog sicher disponieren

**Covers:** US 56-57, 61-62, 64-65, 67-69

**Status:** ready-for-agent

- [ ] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [ ] Inbox, LangGraph-Checkpoints, Versuche, Review-Batches, Feedback-Batches, Korrelationen und relevante GitHub-Referenzen sind dauerhaft und nach einem Neustart wiederherstellbar.
- [ ] Neustarts waehrend Claim, Implementierung, PR-Erzeugung, Review, Reparatur und menschlicher Wartephase erzeugen weder einen zweiten Lauf noch einen zweiten Worktree oder Pull Request.
- [ ] Eine bereits dauerhaft abgeschlossene Transition wird nach Wiederaufnahme nicht erneut extern ausgefuehrt; unsichere Zwischenzustaende werden idempotent aufgeloest.
- [ ] Der wiederaufgenommene Lauf behaelt Issue-, Delivery-, PR-Head-, Worker- und Review-Korrelationen und projiziert einen eindeutigen sichtbaren Status.
- [ ] Recovery wird durch echten Prozessabbruch, Neustart und erneute Beobachtung ueber das produktive Interface bewiesen, nicht nur durch Datenbankabfragen oder Logs.
- [ ] Checkpoints und Diagnoseevents enthalten keine Secrets, Tokens, personenbezogenen Daten oder unnoetigen Payload-Inhalte.
- [ ] Ein Abschlusszustand bleibt terminal: Ein bereits menschlich gemergter und beendeter Lauf wird nach Neustart nicht reaktiviert.
