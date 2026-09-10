# 03: Repositoryzugriff und exklusive Steuerung durchsetzen

**What to build:** Repositoryberechtigte Menschen können denselben Run beobachten, während genau ein Contributor die laufweite Control Lease besitzt und mutierende Operator-Aktionen ausführen darf.

**Blocked by:** 02: Ein autorisiertes Issue als beobachtbaren Run annehmen

**Status:** ready-for-agent

- [ ] Eine Identität mit effektivem Repository-Lesezugriff kann den Run beobachten, aber keine Control Lease beanspruchen oder Mutation auslösen.
- [ ] Eine Contributor-Identität kann genau eine laufweite Control Lease beanspruchen; eine konkurrierende Beanspruchung erhält eine eindeutige Ablehnung.
- [ ] Die Lease ist an die menschliche Provideridentität und nicht an Browser, Terminal oder Rechner gebunden und überlebt einen Clientabbruch.
- [ ] Jede Mutation prüft aktuelle Repositoryberechtigung, Zielversuch, erwartete Run-Version, erwartete Head-SHA und Lease-Epoche.
- [ ] Veraltete oder unberechtigte Mutationen erzeugen keine Nebenwirkung und liefern den aktuellen Entscheidungszustand zurück.
- [ ] Entzogene Providerrechte wirken bei einer neuen Verbindung und spätestens vor der nächsten sicherheitsrelevanten Mutation.
- [ ] Menschliche Identitäten und Worker-/Integrationsidentitäten bleiben in History und Audit unterscheidbar; eine zweite Mitgliederliste entsteht nicht.

## Session lesson

Die frühere Oversight-Task besaß weitreichende technische Providerrechte. Dieses Ticket trennt menschliche Steuerungsentscheidungen und Servicewirkungen von Beginn an.
