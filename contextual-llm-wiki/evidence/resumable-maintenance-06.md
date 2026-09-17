# Ticket 06 – endliche Automation und getrennte Aktivierungsabnahme

Status: Code nach `main` gemergt und bestehende Automation produktiv aktiviert. Kontrollierter manueller Lauf mit frischem Originalindex und endlichem unvollständigem Ergebnis belegt; formale Ticketabnahme abgeschlossen. Tatsächlicher späterer Schedulerlauf und vollständiger Erstimport/No-op bleiben offen. Die ursprünglichen Abschnitte dokumentieren die isolierte Codephase; der abschließende Abschnitt dokumentiert die tatsächliche Aktivierung.

## Soll und beobachtetes Verhalten

| Anforderung | Isoliertes Ist | Evidenz |
| --- | --- | --- |
| Genau ein Start, fehlender Abschluss endlich | Runner bewahrt einen Helper, stdout/stderr/Exit; ein gehaltener Helper ohne Bericht endet bei 0,5 Sekunden Beobachtungsgrenze mit Nicht-Erfolg, Prozess-/Restarbeitnachweis. Sofortiger Exit0 ohne Report ist ebenfalls Fehler. | `test_maintenance_observation.py`; dauerhafte `missing-report-*/observation.json` und `diagnosis.json` |
| Index unabhängig von Wiki | Gemeinsamer503 stoppt nach einem Extraktionsrequest; sechs aktuelle Originale sind bereits im echten QMD-Index. WikiQuery liefert nur den explizit ausgewählten aktuellen Alphabeleg als gekennzeichneten Fallback. | `activation-acceptance.json`, `provider-stop/maintenance/report.json`, tatsächliche Queryrequests |
| Tagespriorität, Drift, Wiederaufnahme | Nach erstem Zweierpaket kommt Alpha/new hinzu; dessen Request startet vor Initialrückstand. Beta ändert sich während Verarbeitung. Beta bleibt unvollständig, Indexstatus wird stale; die aktuelle Alphaquellseite bleibt über WikiQuery erreichbar. Neue Prozesse reparieren Beta und vollenden den kleinen Bestand. | sechs öffentliche Runnerläufe in derselben isolierten Fixture, Inventar, Query und Requests |
| Ehrlicher Abschluss und No-op | Providerstop2133ms, erstes Paket4023ms, Drift3590ms, Wiederaufnahmen3345/3773ms, No-op2950ms. Erst letzter Reparaturlauf hat globalComplete:true; No-op verursacht keine weitere Modellanfrage. | initiale integrierte Messung `wiki-behavior-08QCut/activation-acceptance.json` |
| Unveränderte Betriebsparameter | Kanonischer Prompt, Wartungsreferenz und Operations nennen1200s Helper,10s Grace,30s Marge,180s Stillstandsdiagnose, maximal22 Beobachtungen und20 neue Extraktionen. Configparallelität8 bleibt erhalten. | `automation-prompt.md`, `OPERATIONS.md`, QMD-Wartungsreferenz |

Dauerhafte rohe Messdaten und Review-/Testlogs liegen unter `/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket06/`. Die integrierte Fixture verwendet echte QMD-SQLite-Speicherung, Indexierung und lexikalische WikiQuery-Suche. Externe Modellantworten und Embeddingerzeugung sind kontrolliert; der äußere update/status-Adapter führt echte QMD-SDK-Operationen aus. Dies ist kein Nachweis produktiver Embeddings oder semantischer Suche. Quellen- und Antwortfakten stammen ausschließlich aus dem tatsächlich übergebenen Material, ohne generischen „BeideRepos“-Zusatz.

## Gewählte Grenzen und Einschränkungen

Isolierte integrierte Läufe:15s Helper,0,5s Grace,2s Beobachtungsmarge,5s Diagnose,2 neue Extraktionen. Die beobachteten abgeschlossenen Schritte lagen zwischen2,1 und4,1s. Der gezielt fehlende Abschluss wurde zusätzlich unter0,5s Beobachtungsfrist geprüft. Die produktiven Sicherheitsgrenzen übernehmen die bereits eingeführten20min und20 Quellen pro Aufruf mit zusätzlicher endlicher äußerer Beobachtung. Sie sind keine aus den kleinen Fixtures abgeleitete Zusage zur Tageskapazität von ungefähr2000 Produktivquellen. Überfällige Tagesarbeit und unzureichende Kapazität bleiben sichtbar.

Ein laufender Prozess bedeutet keinen dauerhaften Fortschritt. Nach180s ohne Fortschrittsänderung entsteht einmal eine Diagnose; das absolute Zeitbudget läuft unverändert weiter. Bei Ende ohne gültigen Report bleibt das Ergebnis unvollständig, auch wenn der Prozess zuvor lebte oder Exit0 liefert. Der äußere Notfall kann höchstens11s eigene Beendigung über1240s hinaus benötigen. Guards behalten ihre bestehende Besitzsicherung; eine ungeklärte/live Besitzlage verbietet einen weiteren Lauf.

## Vorabplan für produktive Aktivierung und Rückkehr

Vor Umschaltung werden zwei frische sichere Besitzerbeobachtungen sowie geprüfte Sicherungen verlangt. Der Originalcheckout enthält eigenen unveröffentlichten Commit7cab83d. Ein konfliktfreier normaler Merge erhält ihn als Vorfahr; kein Reset/Rebase/Push dieses Commits. Compilerpin und Dependencydateien bleiben unverändert; nur die fünf vorhandenen Integrationspatches werden übernommen. Bestehende gültige Wiki-/Antwortbytes, gemeinsame Konfiguration, Automationdefinition/Memory und QMD-Datenbank werden vorab gesichert und die Rückkopie isoliert geprüft.

Der konkrete ausführbare Ablauf mit Pfaden und Rückkehrbedingungen liegt im dauerhaften `deployment-plan.md`. Ein vorhandener Besitzer blockiert die Aktivierung; kein fremder Prozess wird beendet. Erst nach Code-Merge werden Prompt über das bestehende Codex-Automationtool gespeichert/zurückgelesen und ein kontrollierter Produktivlauf ausgewertet. Ein eigener120s Aktivierungslauf darf die Ausführungsgrenze verkürzen; der tägliche Routinevertrag bleibt1200s. Keine Quellen-, Modell-, TCC- oder Dependencyänderung.

Zum Zeitpunkt der isolierten Codephase offene Abnahmepunkte (aktuelle Einordnung unten):

- Tatsächliche produktive Aktivierung samt unverändertem Zeitplan/Modell/Projekt/Notifications, Sicherungs-/Rollbackprüfung und kontrolliertem Produktivlauf.
- Erster tatsächlicher späterer Lauf der bestehenden täglichen Automation mit seinen eigenen Artefakten. Konfiguration und manueller Lauf ersetzen diesen Nachweis nicht.
- Vollständiger mehrtägiger Erstimport und anschließender No-op. Ein frischer Originalindex oder ein begrenztes Tagespaket ersetzt diesen Nachweis nicht.

Es entsteht kein zusätzlicher Scheduler/Watcher. Für spätere Ereignisse wird weder stundenlang gewartet noch Erfolg vorweggenommen; der aktive OpenSpec bleibt erhalten.


## Reviewreparaturen und Rückkehrprobe

Die Standardsachse fand eine Umgehung des gemeinsamen Locks durch `--lock-file=PATH` und fehlenden JSON-Fallback bei Artefaktfehlern; beide haben gezielte Prozessgegenproben. Der Standardbefehl `test:operations` entdeckt nun auch alle Observationtests. Die Specachse verlangte zusätzlich, den bereits gestarteten eigenen Helper auch beim Observerfehler begrenzt abzuwickeln sowie beide Schreibsperren während des Rollouts zu halten. `rollout-locks.test.ts` hält die reale Kombination und weist Ablehnung sowohl eines öffentlichen Helpers als auch eines direkten Wiki-Maintain ohne Providerrequest nach.

Die isolierte Rückkehrprobe kopierte39 Dateien einschließlich `wiki/answers/stable-source-answer.md` und sämtlichem Zustand, sicherte die echte QMD-Datenbank über SQLitebackup und kopierte beides in ein drittes Wiederherstellungsziel. Alle39 SHA256 stimmen überein; `PRAGMA integrity_check` ergibt `ok`, elf Dokumente/Contents bleiben vorhanden, Eingänge unverändert. Rohbeleg: `ticket06/restore-rehearsal/restoration.json`; das reproduzierbare task-owned Skript `verify-restoration.py` wird für die spätere echte Sicherung wiederverwendet. Dies ist ausdrücklich keine Rücksetzung der Produktion.


Abschluss der isolierten Codephase:113/113 bestehende TypeScript-Verhaltenstests einschließlich des ersten integrierten Tests bestanden. Dieser Gesamtlauf begann vor den abschließenden Observer-/Rolloutreviewreparaturen und ist daher keine Behauptung byteidentischer Komplettprüfung. Der danach eingefrorene Stand bestand gezielt beide betroffenen End-to-End-Tests (22,6s) sowie alle13 Python-Operationstests (9,3s). Die unveränderte Compilerintegration bestand59 Tests; TypeScript und striktes OpenSpec sind grün. Endgültige rohe Integration: `wiki-behavior-vpjfov/activation-acceptance.json` (Providerstop1713ms, Paket4006ms, Drift3579ms, Wiederaufnahme3351/3758ms, No-op2971ms). Endgültiger Missing-Report-Fall: `missing-report-1789674397715669000/observation.json`,0,518s, ein gestarteter und beendeter Helper, Exit-15, konkrete offene Quelle. Dessen gemessene ursprüngliche Temp-Pfade sind in `path-map.json` auf erhaltene Kopien abgebildet.


## Separate kritische Verifikation

Ein erneuter Aufruf mit demselben Artefaktverzeichnis wird vor jedem Helperstart abgewiesen. Die Gegenprobe fand zunächst einen bloßen Traceback; der reparierte Runner liefert jetzt parsebares `ok:false`, `helper.starts:0`, `artifact-directory-unavailable`. Frühere Berichte und der tatsächliche Startzähler bleiben unverändert. Endgültige Prüfung:14 Pythonfälle grün, darunter bestehende vollständige, unvollständige, fehlende und widersprüchliche Abschlussdaten.

Ein weiterer echter Prozessfall beschädigt nach dem Start des öffentlichen Helpers gezielt nur den eigenen Observer-Diagnosepfad. Innerhalb rund0,64s folgt parsebares Nicht-Ergebnis mit einem gestarteten, beendeten Helper (Exit-15), Phase `reconcile` und explizit unbekannter Restarbeit. Seine eigenen Kind- und Enkelprozesse sind anschließend per Betriebssystemmessung beendet; ein neuer legitimer Rollout erhält beide Sperren. Rohbeleg: `wiki-behavior-NrFmCT/critical-observer-storage.json`.

Der Rollout-Abbruchfall hält den eigenen Guardian kurz an und beendet ausschließlich den selbst gestarteten Rollout-Elternprozess mit SIGKILL. Während Operation und Enkel nachweislich leben, lehnen der direkte Wiki-Schreiber und der öffentliche Helper den Zugriff ab. Nach Fortsetzung der eigenen Prozesssicherung sind beide Kindprozesse nachweislich beendet; neuer Rollout und echte Wiki-Pflege gelingen. Rohbeleg mit `during`/`after`-Messungen: `wiki-behavior-cJV9sJ/critical-rollout-crash.json`. Beide kritischen Prozessfälle benötigen zusammen4,2s. Keine Fremdprozesse wurden signalisiert.

Die vorhandene Rückkehrprobe wurde erneut geöffnet und alle39 Wiederherstellungshashes sowie SQLite-integrity/elf Dokumente geprüft. Prompt, Wartungsreferenz und Operations nennen weiterhin dieselben produktiven Werte und denselben endlichen Ausstieg. Keine neue Komplettsuite: gezielt14 Pythonfälle und2 neue Prozessfälle sowie TypeScript/OpenSpec/Diffprüfung. Der bisherige integrierte fachliche Nachweis bleibt unverändert; die einzige produktive Codeergänzung dieser kritischen Runde ist der strukturierte Fehler beim nicht neu anlegbaren Artefaktverzeichnis. Echte Produktionsfelder werden erst unmittelbar vor der späteren Liveumschaltung erneut gebunden.


## Produktive Aktivierung am 17.09.2026

Der Code wurde mit [PR #12](https://github.com/paradox123/shared-ai-docs/pull/12), Head `b32c32afa1b4fefd02e4bf6de8907e0752085397`, als `c1801b3590ac90ebe2e8500a6e47bbdee26fa174` nach `main` gemergt. Die folgende Aktivierung ist ein separater tatsächlicher Nachweis; sie behauptet keinen vollständigen Erstimport.

| Soll | Tatsächlich beobachtet | Dauerhafte rohe Evidenz unter `ticket06/` |
| --- | --- | --- |
| Sichere Eigentümerschaft und geprüfte Rückkehr | Zwei frische freie Besitzerbeobachtungen vor jedem Umstellungsschritt; Maintenance-flock und Wiki-Schreibsperre während Sicherung, Installation und Definitionsänderung gehalten. 9503 generierte Dateien hashgleich isoliert wiederhergestellt; SQLitebackup/restaurierte DB mit `integrity_check=ok`, 2230 Dokumenten. | `live-owner-*.json`, `definition-custody.json`, `live-backup-location.json` und dort referenzierte `backup-manifest.json`/`state-rehearsal/restoration.json` |
| Fremden lokalen Stand bewahren | Normaler lokaler Merge `6d561906355d9011396ef47e05b14b191807224f` erhält eigenen Commit `7cab83dd918adb748157399050ce5e4129a7c7e6` und gelieferten Remotehead als Vorfahren. Sieben reine Dokumentationskonflikte einzeln geprüft und koordiniert aufgelöst; 114 fremde lokale Dateien und alle 14 akzeptierten Lieferdateien unverändert. Kein Reset/Rebase oder Push dieses lokalen main. | `local-merge-conflict/`, `local-preservation-verified.json` |
| Gleicher Runtime-/Quellenumfang | Compilerpin `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb`, fünf vorhandene Integrationspatches, unveränderte Lockdatei; 1408 tatsächliche Compilerdateien stimmen mit isoliert getestetem Stand überein, echter Build erfolgreich. Acht Repos und Parallelität 8 unverändert; Config-SHA256 `7e85ca023bc4807a292e3c2dc0f1b71241f9eadc2f3475a64c3075fcfcfa09e5`. | `live-installed.json`, `live-rollout-build/`, `production-preservation.json` |
| Bestehende Definition über Tool aktivieren | `update-qmd-index-daily` aktualisiert und zurückgelesen. Nur Prompt und Updatezeit ändern sich; ACTIVE, täglich 07:00, gpt-5.6-terra/xhigh, Projekt, lokale Umgebung und Benachrichtigungsverhalten bleiben erhalten. Das Tool entfernt nur den letzten Zeilenumbruch des kanonischen Prompts. Beide Sperren beim Speichern/Readback gehalten. | `live-update-payload.json`, `definition-readback.json`, `automation.after.toml` |
| Endlicher produktiver Lauf mit wiederaufnehmbarer Arbeit | Genau ein manueller Start, 120s Budget + 10s Grace + 30s Beobachtungsmarge, einmalige Diagnose nach 60s Stillstand. Ende nach 121,295s; Runner/Helper Exit 1, `ok:false`, `budget-exhausted`, Helper nicht mehr aktiv. Vier Extraktionen dauerhaft gesichert. | `production-run/observation.json`, `maintenance/report.json`, `production-runner.exitcode` |
| Aktuelle Originalsuche bei offenem Wiki | Quellenindex erfolgreich für 2047 Originale. Tatsächliche öffentliche WikiQuery in 14,200s/Exit 0: `sourceRetrieval=qmd-source-index`, gekennzeichneter Source-Fallback. Originalpfad und SHA256 `49abde398a7b2f638241c09ebe424fd092a3b8e2c811cc454f80d917358aff8e` von `contextual-llm-wiki/automation-prompt.md` geprüft; Antwort zitiert exakt dessen Anweisung, den ersten Artefaktpfad/Handle zu behalten. | `productive-indexed-query/`, `productive-query-verification.json` |
| Kein liegengebliebener eigener Prozess | Nach beiden lesenden Queries sind alle 14 aufgezeichneten eigenen PIDs abwesend, Maintenance-Sperre frei, Writerlock und Custodymarker fehlen. Gemeinsame Konfiguration unverändert, Originalcheckout sauber. | `live-owner-final.json` (22:16:47+02:00) |

Originaler Laufpfad: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/contextual-llm-wiki/.local/operations-runs/20260917-ticket06-production`. Alle 18 Artefakte wurden zusätzlich hashgleich unter dem dauerhaften Batch-Evidenzpfad in `production-run/` gesichert (`production-artifacts.json`). Die frühere breitere öffentliche Query benötigte 21,429s und nutzte transparent `current-source-scan`; erst die engere wörtliche Query belegt tatsächliche Indexverwendung. Beide prüften Originalfrische und speicherten keine Antwort; keine Query startete Pflege.

Die Produktionssicherung liegt unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/contextual-llm-wiki/.local/rollouts/resumable-06-20260917T2202`. Sie umfasst generierten Zustand, SQLitebackup, Compilerbestand, Automation samt Memory, gemeinsame Konfiguration und QMD-Konfiguration. Die isolierte Wiederherstellung wurde vor Liveänderungen verifiziert; kein Rücksetzen der echten Produktion zum Testen. Von 47 vorhandenen Wiki-Dateien blieben nach dem Lauf 46 bytegleich; ausschließlich die Navigationsdatei `wiki/index.md` änderte sich. Im aktuellen Bestand gab es keine Datei unter `wiki/answers/`; der Erhalt einer gültigen gespeicherten Antwort wurde zusätzlich in der oben beschriebenen isolierten Rückkehrprobe nachgewiesen. Die tatsächlich vorhandenen Inhalte wurden vollständig gesichert.

### Getrennte Ergebnisse und offene Abnahme

- **Originalindex:** erfolgreich, 2047 Quellen; `checkedAt=2026-09-17T20:08:56.759Z`. Aktuelle lexikalische Originalsuche belegt, keine Behauptung fertiger produktiver Vektoren oder globaler Synthese.
- **Tagesarbeit:** pending 0, keine gemeldeten überfälligen oder zeitlich unbekannten Änderungen. Das erste persistente Inventar beweist keine künftige Tageskapazität oder Einhaltung einer späteren Frist.
- **Erstimport:** 2044 pending, davon 2040 noch nicht extrahiert; vier validierte Extraktionen dauerhaft gespeichert. Wiederaufnahme bleibt erforderlich.
- **Gesamtabschluss:** `globalComplete:false`, Wiki unvollständig, `lastCompleted:null`. Offene Phasen: compile/pending, maintain-common, status-common, lint-common und äußeres QMD update/embed/status. Exit 1 ist ein ehrliches unvollständiges Ergebnis und kein Gesamterfolg.
- **Betriebsmemory:** neuer Eintrag vorn eingefügt nach frischem begrenztem Lesen; alle älteren Einträge erhalten (`memory-entry.md`, `memory-update.json`). Die obigen Dimensionen, Fristen, Grenzen und offenen Ereignisse sind getrennt dokumentiert.
- **Später offen:** tatsächlicher nachfolgender täglicher Schedulerlauf sowie vollständiger mehrtägiger Erstimport mit anschließendem No-op. Kein zusätzlicher Scheduler, kein zweiter Pflegeaufruf zur Nachweiserzeugung, keine Archivierung des aktiven OpenSpec.

Der Routinevertrag bleibt 1200s/10s/30s/180s mit höchstens 20 neuen Extraktionen und 22 Beobachtungen; die verkürzte 120s-Probe misst kontrolliertes Ende und persistente Arbeit. Sie verspricht keine Fertigstellung des vollständigen Bestands. Weitere Abnahme nutzt nur Artefakte tatsächlich erfolgter regulärer Läufe.
