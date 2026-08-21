# 01: Ein autorisiertes Issue lokal annehmen und claimen

**What to build:** Ein korrekt authentifiziertes GitHub-Ereignis fuer ein freigegebenes `probare-crm`-Issue wird dauerhaft angenommen, genau einem persistenten LangGraph-Lauf zugeordnet und in GitHub sichtbar als `agent-running` geclaimt.

**Blocked by:** None (can start immediately)

**Covers:** US 3, 9-10, 13-16, 19-20

**Status:** ready-for-agent

- [ ] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [ ] Eine korrekt signierte Delivery fuer eine erlaubte Repository-, Event- und Action-Kombination wird vor der positiven Antwort atomar in der lokalen Inbox persistiert.
- [ ] Ein unblocked Issue mit `ready-for-agent` erzeugt genau einen persistenten Lauf und projiziert `agent-running` nach GitHub.
- [ ] Eine wiederholte Delivery mit derselben `X-GitHub-Delivery` erzeugt weder einen zweiten Claim noch einen zweiten Lauf.
- [ ] Ungueltige Signaturen, zu grosse Requests sowie nicht erlaubte Repositories, Events oder Actions werden ohne Inbox- oder GitHub-Wirkung abgelehnt.
- [ ] Ein Prozessneustart nach der Annahme behaelt Delivery, Claim und Checkpoint bei; der Zustand ist ueber das produktive Workflow-Interface beobachtbar.
- [ ] Verhaltenstests verwenden reale Workflow-Persistenz sowie kontrollierbare GitHub-, Uhr- und Zustelladapter und koppeln sich nicht an interne Node-Reihenfolgen.
