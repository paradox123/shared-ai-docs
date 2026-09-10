# 02: Ein autorisiertes Issue als beobachtbaren Run annehmen

**What to build:** Ein berechtigter Benutzer startet über den öffentlichen Eingang ein synthetisches Issue und sieht anschließend genau einen dauerhaften `ImplementationRun` mit Status und geordneter History in einem getrennten Operator Client.

**Blocked by:** 01: OSS-Durability-Gate und isolierten Piloten beweisen

**Status:** resolved

- [x] Ein autorisiertes Startkommando erzeugt genau einen Run mit stabiler Issue-, Run- und Repository-Korrelation.
- [x] Wiederholte identische Zustellung konvergiert ohne zusätzliche Runs oder externe Wirkungen; widersprüchliche Wiederverwendung derselben Kommandoidentität wird sichtbar abgelehnt.
- [x] Ein zweiter Client liest Run, aktuellen Zustand, Aktivitäten, Versuche und Ereignisse ausschließlich über die öffentliche Operator-Oberfläche.
- [x] API- und Worker-Neustart verändern weder Run-Identität noch bereits bestätigte History.
- [x] Run-, Attempt-, Prozess- und Heartbeat-Zeit sowie eingesetzte Source-, Paket-, Konfigurations- und Vertragsrevisionen sind getrennt sichtbar.
- [x] Agent-Framework- und Durability-History sind korrelierbare Betriebsbelege, aber nicht die einzige oder kanonische Produktoberfläche.
- [x] Kontrollierte Geheimnis-Canaries erscheinen weder in Run-Projektion noch History oder Operator-Ausgabe im Klartext.

## Session lesson

Die ProBara-Diagnose verwechselte Run-Alter, Recovery-Laufzeit und Host-Schlaf. Dieses Ticket etabliert getrennte Zeitachsen, bevor weitere Aktivitäten hinzukommen.

## Comments

- 2026-09-05: Nicht begonnen. Ticket 01 endete mit einem dokumentierten Gate-0-No-Go, weil der gepinnte Agent-Framework-/Durable-Task-SDK-Pfad produktiv ausschließlich den proprietären, separat abgerechneten Azure Durable Task Scheduler unterstützt. Dieser Microsoft-Kandidat und damit seine Folge-Tickets werden nicht fortgesetzt.
- 2026-09-07: Wieder freigegeben. Der Betreiber akzeptierte ausdrücklich die eng begrenzte Managed-DTS-Ausnahme. Ticket 01 bewies im isolierten Consumption-Task-Hub einen bestehenden Run über zwei Worker-Prozesse mit genau einmal committed Effekten; der historische OSS-No-Go bleibt bestehen.

## Outcome

**Completed (2026-09-09).** Der isolierte Control-Plane-Slice akzeptiert ein
synthetisches, capability-gebundenes Startkommando als genau einen dauerhaften
`ImplementationRun`. PostgreSQL besitzt Command-Inbox, kanonische geordnete
History und die lesbare Projektion; API- und Worker-Lebenszyklus sowie
Agent-Framework-/Durable-Task-IDs bleiben ausschließlich ergänzende Belege.

Der öffentliche Black-Box-Test startet drei getrennte Operator-CLI-Prozesse,
zwei Worker-Prozesse und eine ersetzte API gegen eine Wegwerf-PostgreSQL-Instanz.
Er beweist Idempotenz/Konflikt, getrennte Zeitachsen, API-/Worker-Prozesswechsel,
stabile Eventpositionen, Provenance und Redaction einschließlich eines Canarys,
der nur in Worker-Evidence vorkommt. Rohwerte erscheinen weder in Projection,
History noch CLI-Ausgabe.

Belege:

- [`openspec/changes/accept-authorized-issue-as-observable-run/implementation-evidence.md`](../../../../openspec/changes/accept-authorized-issue-as-observable-run/implementation-evidence.md)
- [`microsoft-agent-framework-work-package-pilot/tests/test_control_plane_black_box.py`](../../../../microsoft-agent-framework-work-package-pilot/tests/test_control_plane_black_box.py)
