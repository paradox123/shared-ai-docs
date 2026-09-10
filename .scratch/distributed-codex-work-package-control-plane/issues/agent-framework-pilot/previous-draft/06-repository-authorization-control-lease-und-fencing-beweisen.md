# 06: Repository Authorization, Control Lease und Fencing beweisen

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Drei menschliche Testidentitäten und getrennte Service-Identitäten beobachten und steuern denselben Run nach Repositoryrechten, exklusiver Control Lease, Transfer, Forced Takeover und monotonem Fencing.

**Blocked by:** 05: Session-Fortsetzung und Live Control beweisen

**Covers:** US 2-3, 39-42, 47-61, 76-96, 113-125

**LangGraph baseline:** Kein vollständiges Pendant; bestehende Human-Feedback-/Intervention-Idempotenz bleibt Contract-Prior-Art.

**Status:** needs-triage

- [ ] Read-only darf History sehen, aber weder Lease noch Mutation erhalten; Contributor darf nur mit gültiger Lease mutieren.
- [ ] Genau eine Control Lease gilt für den gesamten Run und überlebt Clientabbruch.
- [ ] Transfer ist atomar; Forced Takeover benötigt keine Administratorrolle und fenced den alten Inhaber sofort.
- [ ] Stale Run-Version, Head, Attempt oder Lease-Epoche wird ohne Nebenwirkung und mit aktuellem Entscheidungszustand abgelehnt.
- [ ] Entzogene Providerrechte werden bei neuer Verbindung und sicherheitsrelevanter Mutation wirksam.
- [ ] Menschliche Identitäten, Worker und Integrationen bleiben in Events/Audit unterscheidbar.
- [ ] Concurrency-Tests beweisen keine überlappenden gültigen Mutationen bei mindestens 20 gleichzeitigen Versuchen.

## Session lesson

Die LangGraph-Oversight-Task besaß weitreichende GitHub-Rechte außerhalb der eigentlichen Workflow-Rolle. Der neue Pilot trennt deshalb menschliche Commands und Service-Wirkungen explizit und auditierbar.
