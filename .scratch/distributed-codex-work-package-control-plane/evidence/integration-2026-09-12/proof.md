# Integration der Agent-Framework-Tickets 06–09

Am 2026-09-12 auf ausdrücklichen Auftrag zur Integration und anschließenden
Branch-Bereinigung geprüft. Die Issues bleiben lokale Markdown-Dateien unter
`issues/agent-framework-pilot`; es wurden keine GitHub-Issues oder PRs angelegt.

## Git-Ausgangslage

| Stand | Commit | Inhalt |
| --- | --- | --- |
| `origin/main` vor Integration | `d9c9c1c` | Bis einschließlich Ticket 05 |
| `codex/transfer-run-control` | `fb660cf` | Gemeinsame Tickets 06/07 plus Ticket 08 |
| `codex/continue-human-requests-in-codex` | `9fc08f0` | Gemeinsame Tickets 06/07 plus Ticket 09 |

Der erste Merge (`51bcf87`) integriert den Stand bis Ticket 08. Der zweite Merge
führt Ticket 09 hinzu. Drei Konflikte betrafen die Pilot-README,
`RunControl.cs` und `PostgresHumanRequestContinuations.cs`.

## Verhalten des zusammengeführten Stands

| Erwartung | Beobachtung und Nachweis |
| --- | --- |
| Session-Fortsetzung und aktive Steuerung bleiben erhalten. | Die öffentlichen HTTP-/CLI-Prozesstests für Tickets 06/07 bestehen, einschließlich Session-Herkunft, FIFO, Prozessstopp und Wiederaufnahme nach SIGKILL. |
| Kontrollübernahme bleibt atomar und übernimmt vorhandene Effekte genau einmal. | Ticket-08-Tests mit konkurrierenden Übernahmen über zwei API-Prozesse, Adapter-Erfolgslücken und Repository-Recovery bestehen. Receipt-Abschluss, Artefaktbereinigung und Übernahmeentscheidung behalten ihre gemeinsame Transaktionsgrenze. |
| Restaurierte Dossiers erlauben keinerlei Steuerung. | Ein neuer HTTP-Test exportiert einen Run mit Lease-Inhaber und wartender Transfer-Anfrage, restauriert ihn und prüft beide Contributor. Zunächst schlug `canForceTakeover` fehl. Nach Ergänzung des historischen Schreibschutzes sind alle fünf Kontrollfähigkeiten deaktiviert; alle vier Transfer-/Takeover-Aktionen liefern `409 restored-dossier-read-only`, und Prüfsummen bleiben unverändert. |
| Reconnect und Restore erhalten die vollständige öffentliche Evidence. | 10.015 Events, davon 9.765 nach Wiederverbindung und 12.027.403 Stream-Bytes; der Test bestätigt lückenlose Reihenfolge und identische History-/Projection-/Artefakt-Prüfsummen nach frischem Restore. Auf 35 geprüften Oberflächen wurden keine rohen kontrollierten Canaries gefunden. |
| Lokaler Ticketstatus entspricht der vorhandenen Umsetzung. | Ticket 06 wurde anhand des bereits archivierten Changes von `ready-for-agent` auf `resolved` korrigiert und mit dessen Nachweisen verlinkt. Die mitgemergten Tickets 08/09 enthalten ihre jeweiligen Abschlussstände. |

## Ausgeführte Prüfungen

Aus `microsoft-agent-framework-work-package-pilot`:

- `dotnet restore --locked-mode Wpcp.WorkPackageControlPlane.sln`: erfolgreich.
- `dotnet build Wpcp.WorkPackageControlPlane.sln --no-restore`: erfolgreich, keine Warnungen oder Fehler.
- `python3 -m unittest tests.test_run_dossier.RunDossierTests.test_restored_holder_and_pending_transfer_do_not_enable_control -v`: erst erwarteter Verhaltensfehler, anschließend erfolgreich.
- `python3 -m unittest discover -s tests -v`: **120 Tests erfolgreich**, 407,276 Sekunden.

Aus dem Repository-Root:

- `openspec validate --all --strict --no-interactive`: **43 erfolgreich, 0 fehlgeschlagen**.
- `git diff --check` und `git diff --cached --check`: erfolgreich.

Die Prüfung verwendet echte lokale API-/CLI-/Worker-Prozesse, Git und
Wegwerf-PostgreSQL mit kontrollierten externen Adaptern. Live-Codex,
reale Provideridentitäten und automatische Managed-DTS-Zustellung wurden nicht
neu geprüft; dafür gelten weiterhin die späteren Tickets 10/14.
