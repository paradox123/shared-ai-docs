# 03: Repositoryzugriff und exklusive Steuerung durchsetzen

**What to build:** Repositoryberechtigte Menschen können denselben Run beobachten, während genau ein Contributor die laufweite Control Lease besitzt und mutierende Operator-Aktionen ausführen darf.

**Blocked by:** 02: Ein autorisiertes Issue als beobachtbaren Run annehmen

**Status:** resolved

- [x] Eine Identität mit effektivem Repository-Lesezugriff kann den Run beobachten, aber keine Control Lease beanspruchen oder Mutation auslösen.
- [x] Eine Contributor-Identität kann genau eine laufweite Control Lease beanspruchen; eine konkurrierende Beanspruchung erhält eine eindeutige Ablehnung.
- [x] Die Lease ist an die menschliche Provideridentität und nicht an Browser, Terminal oder Rechner gebunden und überlebt einen Clientabbruch.
- [x] Jede Mutation prüft aktuelle Repositoryberechtigung, Zielversuch, erwartete Run-Version, erwartete Head-SHA und Lease-Epoche.
- [x] Veraltete oder unberechtigte Mutationen erzeugen keine Nebenwirkung und liefern den aktuellen Entscheidungszustand zurück.
- [x] Entzogene Providerrechte wirken bei einer neuen Verbindung und spätestens vor der nächsten sicherheitsrelevanten Mutation.
- [x] Menschliche Identitäten und Worker-/Integrationsidentitäten bleiben in History und Audit unterscheidbar; eine zweite Mitgliederliste entsteht nicht.

## Session lesson

Die frühere Oversight-Task besaß weitreichende technische Providerrechte. Dieses Ticket trennt menschliche Steuerungsentscheidungen und Servicewirkungen von Beginn an.

## Outcome

**Completed (2026-09-10).** Der isolierte Pilot authentifiziert Operator-Zugriffe
über den GitHub-Adapter und leitet Lese-/Contributor-Rechte bei jeder Anfrage neu
ab. Es gibt keine lokale Mitgliederliste und keine Autorisierung durch eine
übermittelte Actor-ID. Repositorybindung und menschliche Provider-ID bleiben
stabil; Claim/Release, Versions-/Attempt-/Head-/Epochenprüfung sowie Security Audit
sind dauerhaft und laufweit. Ein erkannter Rechteentzug invalidiert die Lease;
Clientabbruch und Tokenwechsel desselben Menschen tun dies nicht.

Verifikation: 34 Tests grün, darunter neun öffentliche Control-Plane-Tests mit
getrennten API-/CLI-/Worker-Prozessen und Wegwerf-PostgreSQL; Locked Restore,
Build ohne Warnungen, OpenSpec Strict Validation und Diff-Check erfolgreich.
Der externe GitHub-HTTP-Endpunkt ist kontrolliert simuliert. Ein Live-Nachweis
mit drei echten Accounts gehört zu Ticket 14. Head und Zielkontext entsprechen
weiterhin Ticket 02 (kein Writer-Head, abgeschlossener Admission-Versuch).

Belege:

- [OpenSpec-Change und Nachweise](../../../../openspec/changes/archive/2026-09-11-enforce-repository-control-lease/implementation-evidence.md)
- [Öffentliche Verhaltenstests](../../../../microsoft-agent-framework-work-package-pilot/tests/test_control_plane_black_box.py)
- [Betrieb und CLI](../../../../microsoft-agent-framework-work-package-pilot/README.md)

## Comments

- 2026-09-11: Vom Benutzer nach dem öffentlichen HTTP-/CLI-Nachweis akzeptiert.
  Ticket bleibt abgeschlossen (`resolved`); der zugehörige OpenSpec-Change ist
  archiviert und seine Anforderungen sind in die kanonischen Specs übernommen.
  [Akzeptierter Laufnachweis](../../evidence/ticket-03-2026-09-11/proof.log),
  [originale HTTP-/CLI-Antworten](../../evidence/ticket-03-2026-09-11/http-cli-responses.jsonl).
