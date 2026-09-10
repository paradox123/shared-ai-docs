# 01: OSS-Durability-Gate und isolierten Piloten beweisen

**What to build:** Der Betreiber kann vor der eigentlichen Produktimplementierung nachvollziehbar entscheiden, ob der vorgesehene Agent-Framework-Stack einen produktionsfähigen, selbst hostbaren Open-Source-Pfad ohne verpflichtende zusätzliche Framework- oder Managed-Workflow-Service-Lizenzkosten besitzt und einen dauerhaften Lauf über einen Workerwechsel fortsetzen kann.

**Blocked by:** None (can start immediately)

**Status:** wontfix

- [x] Alle direkten und transitiven Workflow-/Backendkomponenten, ihre Versionen, Lizenzen und unvermeidbaren Servicekosten sind in einem reproduzierbaren Manifest erfasst.
- [ ] Der exakt gepinnte Agent-Framework-/Durability-Tuple kompiliert und läuft mit einem produktionsfähigen selbst verwalteten Open-Source-Backend; ein In-Memory-Emulator allein genügt nicht.
- [ ] Zwei getrennte Worker-Prozesse setzen denselben Testlauf nach einem kontrollierten Workerabbruch ohne Neustart oder Doppelwirkung fort.
- [x] Source-Revision, Paket-Lock, Runtime, Konfiguration und Vertragsversion sind im öffentlichen Prüfergebnis korreliert; eine inkompatible Kombination wird vor dem Start abgelehnt.
- [x] Erst nach bestandenem Gate wird die neue Schwesteranwendung mit eigenen Paketen, Prozessen, Zuständen, Ports, Worktrees und Cleanup-Grenzen begonnen.
- [x] Temporal und kostenpflichtige Managed-Workflow-Dienste werden weder eingebunden noch als Fallback vorbereitet.
- [x] Vorher-/Nachher-Evidence zeigt, dass LangGraph-Pilot, Cloudflare-Anbindung, macOS-Betrieb, Laufzeitdaten, Worktrees und ProBara CRM unverändert bleiben.
- [x] Scheitert das Gate, endet der Microsoft-Kandidat mit einem dokumentierten No-Go; kein nachfolgendes Ticket wird begonnen.

## Session lesson

Der installierte LangGraph-Pilot wich zeitweise vom getesteten Source- und Contract-Stand ab. Deshalb ist Runtime-Provenance Teil des ersten ausführbaren Gates.

## Outcome

**No-Go (2026-09-05).** Das exakt gesperrte Tuple aus
`Microsoft.Agents.AI.DurableTask` `1.16.0-preview.260730.1`, Workflows `1.16.0`
und Durable Task `1.18.0` restauriert und kompiliert mit 57 vollständig
inventarisierten NuGet-Komponenten. Der moderne Self-hosted-Durable-Task-SDK-Pfad,
den die Agent-Framework-Erweiterung verwendet, unterstützt produktiv jedoch
ausschließlich Azure Durable Task Scheduler. Dieser ist ein proprietärer,
separat abgerechneter Managed Service; der lokale In-Memory-Emulator ist nicht
produktionsfähig. Ein produktionsfähiger, selbst verwalteter OSS-Backend-Pfad
konnte daher nicht qualifiziert werden.

Der Gate-Runner brach vor dem Workflow-/Workerstart mit den Kriterien
`managed-service`, `not-self-managed`, `not-open-source` und
`unavoidable-service-cost` ab. Entsprechend der Ticketregel wurde die reale
Zwei-Worker-Probe nicht ausgeführt und die Schwesteranwendung nicht angelegt.

Belege:

- [`microsoft-agent-framework-oss-gate/manifest.json`](../../../../microsoft-agent-framework-oss-gate/manifest.json)
- [`microsoft-agent-framework-oss-gate/audit/backend-compatibility.md`](../../../../microsoft-agent-framework-oss-gate/audit/backend-compatibility.md)
- [`microsoft-agent-framework-oss-gate/evidence/gate-5da1cc60-3797-4cc2-a4e3-11ccdff38ec1/decision.json`](../../../../microsoft-agent-framework-oss-gate/evidence/gate-5da1cc60-3797-4cc2-a4e3-11ccdff38ec1/decision.json)
- [`microsoft-agent-framework-oss-gate/evidence/gate-5da1cc60-3797-4cc2-a4e3-11ccdff38ec1/report.md`](../../../../microsoft-agent-framework-oss-gate/evidence/gate-5da1cc60-3797-4cc2-a4e3-11ccdff38ec1/report.md)

## Managed exception outcome (completed)

**Go for the isolated managed pilot (2026-09-07).** Der historische OSS-No-Go
bleibt unverändert: Azure DTS ist weder selbst gehostet noch Open Source. Der
Betreiber hat anschließend ausdrücklich eine eng begrenzte Ausnahme für den
isolierten Agent-Framework-Piloten akzeptiert.

Die Ausnahme verwendet den Azure Durable Task Scheduler im Consumption-Tarif
unter dem aktiven Free-Trial-Spending-Limit, einem monatlichen Budget von 5 mit
Warnungen bei 50, 80 und 100 Prozent sowie `DefaultAzure` ohne gespeichertes
Client Secret. Der isolierte Task Hub lautet
`agent-framework-isolated-pilot-v1`.

Der reale Lauf `managed-gate-71d21049-4f6b-4b4a-9a20-bff0f1ac2642` wurde genau
einmal gestartet. Worker `48056` wurde nach Eintritt in Checkpoint 2 hart
beendet; Worker `48128` übernahm denselben Lauf und schloss ihn ab. Die Effekte
`checkpoint-one` und `checkpoint-two` wurden jeweils genau einmal committed.
Die Vorher-/Nachher-Fingerprints aller geschützten Grenzen sind identisch.

Belege:

- [`microsoft-agent-framework-work-package-pilot/evidence/managed-gate-27557adb-ac51-41b0-b479-05c4dfef1afb/decision.json`](../../../../microsoft-agent-framework-work-package-pilot/evidence/managed-gate-27557adb-ac51-41b0-b479-05c4dfef1afb/decision.json)
- [`microsoft-agent-framework-work-package-pilot/evidence/managed-gate-27557adb-ac51-41b0-b479-05c4dfef1afb/report.md`](../../../../microsoft-agent-framework-work-package-pilot/evidence/managed-gate-27557adb-ac51-41b0-b479-05c4dfef1afb/report.md)

Damit ist ausschließlich der isolierte Managed-Pilot freigegeben. Die beiden
ursprünglichen OSS-Kriterien bleiben bewusst unerfüllt und dürfen nicht als
Nachweis für einen selbst verwalteten Backend-Pfad gelesen werden.
