# Ticket 04: Gemeinsamer Mac-Betrieb

In Arbeit am 13.09.2026. Owning Git-Root: `_shared/shared-ai-docs`; von Daniel bestätigter Zielbranch `main`, sauberer Ausgangspunkt `76f4c51`. Ticket 02 und 03 sind integriert. Zuständig ist `operate-contextual-llm-wiki`, Aufgaben 4.5–4.7. Andere parallele Änderungen werden nicht übernommen.

## Produktionsstand

Die neue Konfiguration `.local/common.json` umfasst alle acht Originalrepos und rekursive Meetings/Projects einschließlich Projects/Private. Erste Inventur: 1.853 Dateien; Meetings derzeit leer, Projects zwei Dateien einschließlich einer persönlichen. Die frühere Meetingquelle ist entfallen; keine Abnahmefixtures ersetzen sie. Die Klärung des geänderten Meetingbestands läuft.

Die bisherige Automationdefinition und Memory sind unter `.local/ticket04/automation.before.toml` und `memory.before.md` gesichert. Der produktive Migrationssnapshot liegt unter `/Users/dh/.local/state/contextual-llm-wiki/backups/production-ticket-04-20260913`; Rohinventur und Übernahmebericht unter `.local/ticket04/`. 46 Revisionen wurden erhalten, 30 identischen Zielrevisionen zugeordnet und 38 wegen inzwischen ungültiger Originalbelege zurückgestellt. Die gespeicherten Altantworten bleiben vollständig im Snapshot, sind aufgrund entfallener/geänderter Belege aktuell nicht publizierbar. Der frühere [Ticket-02-Nachweis](shared-wiki-02.md) wird dadurch nicht als heutige Quellenprüfung ausgegeben.

Vollimport, globale QMD-Pflege, No-op, produktive Synthese und menschlicher Einstieg werden erst nach überprüftem Abschluss als bestanden ausgewiesen. Ein tatsächlicher automatischer Schedulerlauf ist noch nicht nachgewiesen. Historische Collections/Einstiege sind noch nicht abgelöst.

## Implementierte Prüfung

Die öffentliche WikiQuery liefert zusätzlich geprüfte Originalpfade, Obsidian-URIs, Hashes und `freshness: checked-current`. Der CLI-Test wurde zunächst wegen fehlender `originals` rot; anschließend besteht er für die verwaltete Abfrage und den aktuellen Quellen-Fallback nach einer Änderung, jeweils mit expliziter Repo-Grenze. TypeScript besteht. Die bestehenden Migrationstests für einzigartige Antworten/Antwortketten und frische Übernahme bestehen auf dem zusammengeführten Stand.

Lokale Detailprotokolle: `.local/ticket04/query-red.txt`, `query-green.txt`, `typecheck.txt`, `integration-tests.txt` und `runtime.jsonl`. Der echte Codex-Providerprobe mit der vorhandenen Anmeldung und gepinnter Runtime war erfolgreich. Die reduzierte PATH-Prüfung zeigte, dass QMD zusätzlich den vorhandenen Node-22-Pfad benötigt; der Betriebsaufruf ergänzt ihn ausdrücklich.

## Verifizierte zentrale Einführung

Standards- und Spec-Review gegen `76f4c51` melden jeweils null offene Implementierungsbefunde. Der tatsächliche unabhängige Agentenablauf beginnt mit WikiQuery und folgt ausschließlich den zurückgegebenen Originalpfaden. Die persönliche Projektquelle wird mit `fallback:false` wiederverwendet, ihr Originalhash stimmt überein. Eine zweite Frage zum Betriebsmodell verwendet mangels gültiger Wiki-Evidenz `fallback:true` mit der aktuellen Originaldatei. Beide Aufrufe beachten die explizite Quellengrenze, erzeugen keine Antwortseite und führen keine parallele QMD-Kontextsuche aus. Eine veraltete Seitenfassung wurde in diesem realen Ablauf nicht verwendet; deren Zurückweisung und Nachpflege bleiben durch die CLI-Verhaltenstests belegt. Rohantworten und Ablauf: `.local/ticket04/agent-flow/`.

Der Gesamtcheck besteht: 60 öffentliche Wiki-CLI-Tests, 59 Compiler-Kompatibilitätstests, acht Helper-Tests und TypeScript. Beide geänderten Skills sind validiert, OpenSpec strikt gültig und Diff-Prüfung erfolgreich. Protokoll: `.local/ticket04/full-check.txt`.

Die produktive Automation ist auf `common.json` umgestellt. Ein Vergleich aller übrigen Definitionfelder außer Änderungszeitpunkt bestätigt unveränderte Einstellungen. Die Automation-Memory nennt ausdrücklich den laufenden, noch nicht akzeptierten Erstimport. Die gemeinsame Konfiguration verwendet die vorhandene Compileroption `concurrency: 8` für acht parallele Modellanfragen. Keine Änderung am Quellumfang oder zusätzlichen Scheduler.

Der erste volle Versuch `20260913-ticket04-production-01` wurde kontrolliert über den eindeutig zugeordneten Compiler-PID beendet, um diese unterstützte Parallelität zu verwenden. Sein Helperbericht bewahrt Exit 143 für den Compiler und erfolglosen Gesamtablauf; keine globale QMD-/Embedding-Abnahme wird daraus abgeleitet. Folgeversuch: `20260913-ticket04-production-02` im selben Operations-Verzeichnis und mit derselben Betriebssperre.
