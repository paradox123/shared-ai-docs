# Unabhängiger Forward-Test: orchestrate-ticket-batch

Ergebnis: Die drei vorgegebenen Situationen ließen sich mit der öffentlichen CLI anhand von SKILL.md und Referenzen ausführen. Kein manuelles Ledger-Patching, keine erfundenen Request-IDs, Receipt-Hashes oder Event-Sequenzen, kein Lesen der Implementierung nötig. Dies ist ein begrenzter synthetischer Anwender-Test, keine formale Code-Review oder echte Delivery-Verifikation.

Alle erzeugten Dateien liegen unter `/tmp/scripted-flow-forward` (auf diesem macOS von der CLI teils als `/private/tmp/scripted-flow-forward` kanonisiert). Es gab keine echten Tasks, Nachrichten, Automationen, Subagenten, Git- oder Netzwerk-Aufrufe. Worker-Identitäten, Inhalte C1, Targets T0/T1/T2, Merge M1 und sämtliche externen Resultate sind ausdrücklich synthetische Fixtures. Nur die CLI-Zustandsübergänge und Ablehnungen wurden tatsächlich ausgeführt.

## Benutzte Dokumentation

- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/orchestrate-ticket-batch/SKILL.md`
- `references/local-helpers.md`, `efficient-execution.md`, `worker-events.md`, `parallel-delivery.md` aus diesem Skill
- Öffentliche CLI `--help`, `coordinate --help`, `report --help`

## Tatsächliche Aufrufe und Resultate

CLI: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/orchestrate-ticket-batch/scripts/batch_state.py`
Ledger: `/tmp/scripted-flow-forward/state.json`

Jede Tabellenzeile mit einem Operationsdateinamen wurde exakt als `python3 <CLI> coordinate --ledger /tmp/scripted-flow-forward/state.json --expect-revision <vorherige status-Revision> --input /tmp/scripted-flow-forward/<Datei>` ausgeführt. Vor jedem Folgeaufruf wurde die Revision über `python3 <CLI> status --ledger /tmp/scripted-flow-forward/state.json` gelesen. Die vollständigen ausgeschriebenen Kommandos, JSON-Eingaben, stdout/stderr und Exitcodes stehen in [transcript.md](transcript.md). Initialisierung separat:

```sh
python3 /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/orchestrate-ticket-batch/scripts/batch_state.py coordinate --ledger /tmp/scripted-flow-forward/state.json --expect-revision 0 --input /tmp/scripted-flow-forward/01-init.json
```

| Datei / Aktion | Tatsächliches Resultat |
| --- | --- |
| 01-init.json | Exit 0, Revision 1; Target release/demo, 2 Ticketplätze, 1 Unteragent, B depends_on A |
| 02-blocked-B.json | Exit 2, `prerequisite not delivered`; Revision bleibt 1 |
| 03-register-A.json | Exit 0, Revision 2; A reserviert 1 Ticket und 1 Unteragent; Paket generiert |
| 04-registration-confirmed.json | Exit 0, Revision 3; synthetische bestätigte Identität/Worktree/Branch/Base übernommen |
| 05-implement-A.json | Exit 0, Revision 4; gebundenes Implementierungspaket generiert |
| 06-implementation-dispatch-confirmed.json | Exit 0, Revision 5; pending gelöscht |
| report für Implementierung | Exit 0; CLI generiert Event 000001 und Callback mit Eventpfad |
| 07-ready-and-verify.json | Exit 0, Revision 6; nach Prüfung C1/erwartet 42/tatsächlich 42 delegierten change-accepted-Auftrag vorbereitet |
| 08-lost-tool-response.json | Exit 0, Revision 7; derselbe Request wird unknown, nächster Schritt reconcile-dispatch |
| 09-replayed-earlier-worker-event.json | Exit 0, `event_status: stale`; Revision 7 und unknown-Request unverändert; kein neuer Auftrag |
| 10-no-replacement-during-unknown.json | Exit 2, `reconcile pending dispatch before preparing another command`; kein Ersatzpaket |
| 11-reconciled-delivery.json | Exit 0, Revision 8; synthetischer Zielverlauf bestätigt exakt denselben Request, pending gelöscht |
| report für technische Verifikation | Exit 0; neuer Request-Stream erhält automatisch Event 000001 |
| 12-technical-acceptance.json | Exit 0, Revision 9; Abschlussbeleg C1 geprüft und awaiting-integration erreicht |
| 13-prepare-integration-T1.json | Exit 0, Revision 10; integration = A, Integrationsvorbereitung gegen T1 ohne Mergefreigabe |
| 14-integration-dispatch-confirmed.json | Exit 0, Revision 11 |
| report für Integration C1/T1 | Exit 0; Kandidat und getestetes Target im Event |
| 15-consume-integration-T1.json | Exit 0, Revision 12; inspect-evidence |
| 16-refuse-stale-target-grant.json | Exit 2, `merge grant requires held integration and current tested target`; getestetes T1 und beobachtetes T2 verhindern Freigabe |
| 17-revalidate-target-T2.json | Exit 0, Revision 13; neues integrating-Paket gegen T2, content_ref C1 und Evidenz der Targetbewegung; integration bleibt A |
| 18-revalidation-send-confirmed.json | Exit 0, Revision 14 |
| report für Integration C1/T2 | Exit 0; synthetische Kombinationsprüfung und unveränderter Inhalt bereitgestellt |
| 19-consume-and-grant.json | Exit 0, Revision 15; nach inhaltlicher Prüfung und separater frischer T2-Beobachtung exakte Freigabe C1/T2 vorbereitet |
| 20-grant-send-confirmed.json | Exit 0, Revision 16 |
| report für Delivery C1/T2 | Exit 0; synthetischer Merge M1, Mapping, Abschluss und Quieszenz gemeldet |
| 21-delivery-awaiting-confirmation.json | Exit 0, Revision 17; confirming, Reservierungen bleiben bestehen |
| 22-delivery-confirmed.json | Exit 0, Revision 18; Remote-Resultat/Mapping/Closure/Quieszenz als Fixtures bestätigt; A cleanup, integration null, 2 Tickets und 1 Unteragent frei |
| 23-B-now-eligible.json | Exit 0, Revision 19; B erstmals erfolgreich registrierungsfähig, reserviert den wieder freien Unteragenten |

Die tatsächlich ausgeführten Wrapper-Kommandos waren `python3 /tmp/scripted-flow-forward/drive.py`, `phase2.py`, `phase3.py`, `phase4.py`, `phase5.py`. Diese kleinen lokalen Testtreiber schreiben ausschließlich Operations-/Evidenz-Fixtures, rufen die öffentliche CLI auf und entnehmen Revision, Paket, Request-ID und Eventpfad deren JSON-Ausgabe. Sie lesen oder verändern keine Ledger-Interna. Sämtliche Inputs, Treiber und CLI-Pakete bleiben inspectierbar im Testverzeichnis.

## Entscheidung pro Situation

**A — fachliche und technische Fortgangsentscheidungen.** Der Koordinator prüfte den synthetischen Expected/Actual-Bericht und band die fachliche Freigabe an C1. Erst nach Vorlage und Lesen des aktuellen technischen Abschlussbelegs wurde awaiting-integration erreicht. Integration hielt die einzelne Reservierung bis zur bestätigten Lieferung. A wurde synthetisch bis bestätigter Integration/Lieferung durchgeführt. B war vor A gesperrt und nach bestätigter Lieferung trotz ausstehendem Cleanup von A zulässig. Die reservierte Unteragentenzahl überschritt zu keinem Zeitpunkt 1.

**B — unbekannter Versand und alte Worker-Meldung.** Die verlorene Toolantwort wurde als unknown am bestehenden Request gespeichert. Die erneut zugestellte alte Implementierungsmeldung wurde als stale erkannt und räumte den unbekannten Versand nicht auf. Auch ein expliziter negativer Ersatzauftragversuch scheiterte korrekt. Nächste fachlich richtige Aktion war die Prüfung des Zielverlaufs; nach einer synthetischen Bestätigung des exakten Requests wurde derselbe Request confirmed. Kein Resend und keine neu erfundene Sequenz erforderlich.

**C — T1 getestet, T2 aktuell.** Eine Freigabe mit T1/T2 wurde abgelehnt. Der sinnvolle nächste lokale Schritt war gemäß dokumentierter Tabelle ein erneutes `prepare` für `integrating`, mit `target_ref: T2`, `content_ref: C1` und Evidenz der Targetbewegung. Das erzeugte tatsächlich einen neuen Auftrag und hielt integration = A. Danach erlaubte der erfolgreiche C1/T2-Bericht mit frischer T2-Prüfung die gebundene Freigabe.

## Anwendersicht / Hindernisse

Keine blockierende Dokumentationslücke in diesen drei Abläufen gefunden. Die Tabellen liefern die nötigen Eingabefelder, und `report` übernimmt Sequenzen/Callbacks ohne Handarbeit. `consume` plus `next` funktioniert für fachliche Freigabe, technischen Abschluss und Integrationsfreigabe; `advance` funktioniert für die bestätigte Lieferung. Die Meldungen bei unknown und Targetbewegung waren unmittelbar verwertbar.

Kleine Bedienungsbeobachtung: `status` nennt für B anfangs `next: prepare-registering`, obwohl die Abhängigkeit den Aufruf blockiert. Die Dokumentation warnt ausdrücklich, dass ein Vorschlag keine Eligibility zusichert; der tatsächliche prepare-Aufruf blockierte korrekt. Kein Umweg nötig, aber ein direkter Abhängigkeitsgrund im Status wäre bequemer.

Grenzen: Keine realen Tooltransporte/Tasks, Remote-Rennen, Idle-Wake, Reviews, Git-Merges oder Cleanup-Operationen geprüft. Die Existenz von Fixture-Dateien beweist nur CLI-Buchhaltung, keine externen Fakten; das ist in der Dokumentation korrekt benannt. Endzustand Revision 19 ist absichtlich nicht batch-complete: A wartet auf Cleanup, B hat nur ein ungesendetes vorbereitetes Registrierungspaket. Der begrenzte Testauftrag verlangte keinen vollständigen Batchabschluss.
