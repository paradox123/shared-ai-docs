# 10: Drei Identitäten Ende-zu-Ende und Koexistenz beweisen

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Der zusätzliche Agent-Framework-Pilot beweist mit drei menschlichen Identitäten den vollständigen Fehler-, Übernahme-, Fortsetzungs-, Qualification- und Approval-Fall, ohne LangGraph zu ersetzen und ohne Merge, Deployment oder Release.

**Blocked by:** 06: Repository Authorization, Control Lease und Fencing beweisen; 08: Redaction, Artefakte und portablen Export beweisen; 09: Echten Codex-Adapter begrenzt integrieren

**Covers:** US 1-132; vollständiger vertikaler Abnahmefall

**LangGraph baseline:** Der umgesetzte ProBara-CRM-Live-Pilot bleibt parallel und unverändert; sein öffentlicher Verhaltensnachweis ist Vergleichsevidence, nicht Ziel einer Migration.

**Status:** needs-triage

- [ ] Identität A startet einen autorisierten synthetischen Issue-Run und der Agent scheitert nach mehreren sichtbaren Schritten und einem adoptierten externen Effekt.
- [ ] Identität B liest denselben Run von einem anderen Client, übernimmt atomar die Lease und wählt eine explizite Fortsetzung.
- [ ] Der fortgesetzte Lauf erzeugt einen neuen Head, deterministische Verifikation und drei isolierte Review-Verdicts.
- [ ] Identität C führt über eine interaktive authentifizierte Aktion genau ein Approval für den qualifizierten Head aus.
- [ ] Ein Hintergrundmonitor darf den Zustand erkennen und melden, führt aber weder Approval, Mark-ready, Merge, Deployment noch Release aus.
- [ ] Abbruch-/Neustart-, Cursor-, Stale-Head-, Fencing-, Redaction- und Exportnachweise sind über öffentliche Oberflächen korreliert.
- [ ] Vorher-/Nachher-Prüfung zeigt keine Änderung an LangGraph-Code, Cloudflare, launchd, dessen Runtime-Daten/Worktrees, GitHub-Konfiguration oder ProBara CRM.
- [ ] Der Pilot endet mit einer dokumentierten Go-/Stop-Entscheidung für den Microsoft-Kandidaten; bei Stop bleibt LangGraph bestehen und es wird kein nicht freigegebener Ersatz begonnen.

## Session lesson

Die frühere Oversight-Automation konnte den nominell menschlichen PR-Gate übernehmen. Dieser End-to-End-Test verlangt deshalb eine echte interaktive H3-Aktion und beweist explizit das Ausbleiben automatischer irreversibler Wirkungen.
