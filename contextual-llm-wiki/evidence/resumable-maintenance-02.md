# Wiederaufnehmbare Pflege – Ticket 02

Stand: 17.09.2026. Isolierte Umsetzung; produktive Daten und Live-Automation unverändert. Der aktive Change `operate-contextual-llm-wiki` bleibt offen.

## Verhalten

Der öffentliche Wartungshelper verwendet den weiterhin gepinnten Compiler `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb` mit zusätzlichem Patch `0003-durable-extraction-boundary.patch`. Die kleine optionale Extraktionsgrenze übergibt den tatsächlich gerenderten Prompt, Toolvertrag und aufgelösten Modellwert an den Hostcache. Speicherung liegt außerhalb des Publikations-Stagings; vollständig geschriebene Antworten werden mit Prüfsumme, atomarem Rename und Dateisystem-Synchronisierung gesichert. Unvollständige temporäre Dateien zählen nicht als Erfolg.

Der Wiederverwendungsschlüssel enthält Originalidentität und Inhalt, Kontextzuordnung, vollständige Requestbytes einschließlich übergebenem Konzeptkontext, aufgelösten Modellwert, relevante Providerparameter, installierten Compiler-Code und seine Lockdatei. Diagnoseflags entwerten keine fachlich unveränderte Extraktion. Kein Dependency-Upgrade, zusätzlicher Scheduler oder Retrievalspeicher wurde eingeführt.

## Gemessene Abnahme

Alle Prüfungen verwenden öffentliche CLI-/Helperprozesse, den echten integrierten Compiler und echte isolierte QMD-Datenbanken. Ausschließlich die Modellprovidergrenze ist deterministisch kontrolliert. Der Helpertest benutzt nach den realen Wiki-/QMD-Schritten absichtlich `/usr/bin/false` für globale QMD-Wartung; er behauptet deshalb keinen erfolgreichen globalen Job. Der Kontextbericht bestätigt Wikiabschluss und die nachfolgende WikiQuery bestätigt tatsächliche Suchbarkeit. Produktionsreconciliation wird durch einen lokalen erfolgreichen Preflight ersetzt.

| Kriterium | Soll | Beobachtetes Ergebnis |
| --- | --- | --- |
| Prozessabbruch | Dauerhafte Erfolge nach frischem Prozess wiederverwenden | Vor SIGKILL zwei vollständige Cacheeinträge; nach Neustart insgesamt zwei statt zuvor vier Extraktionsrequests. Beide Quellen in gemeinsamer WikiQuery-Synthese, kein Fallback. |
| Einzelkorruption | Nur betroffenen Eintrag neu berechnen | Cachedatei einer Quelle durch `null` ersetzt; drei Requests insgesamt, ein Cachetreffer, eine lokale Invalidierung; Query erfolgreich. |
| Quellversion | Geänderte Quelle erneut extrahieren | Zwei Erstrequests, danach nur ein zusätzlicher Request; andere Quelle wiederverwendet. Query enthält vier statt zwei Alpha-Freigaben. |
| Aufgelöstes Modell | Anderer Modellvertrag darf Cache nicht übernehmen | Entfernen des expliziten Testmodells führt tatsächlich zum Providerdefault; Requestzahl von drei auf fünf. |
| Tatsächlicher Prompt | Anderer Sprach-/Promptinhalt neu berechnen | Gemessene Promptbytes ändern sich; fünf auf sieben Requests. Reparatur anschließend ohne weitere Extraktionen. |
| Tool-/Compilervertrag | Änderung trotz gleichen Upstream-Pins entwertet Cache | Getrennte Installation mit geändertem Tool-Schema bei unverändertem Pin: zwei auf vier Requests, anschließend WikiQuery erfolgreich. |
| Drift und Indexfehler | Gültige Extraktionen behalten, Vollerfolg nicht vorziehen | Drift sperrt Publikation; Folgeaufruf verwendet unabhängige Quelle wieder. Echter QMD-Dateiöffnungsfehler meldet Nicht-Erfolg und `lastCompleted: null`; Reparatur bleibt bei insgesamt drei Extraktionsrequests. |
| Leere/teildefekte Antworten | Keine erfolgreiche Teilpublikation | Leere Extraktion sowie gemischte valide/defekte Konzepte bleiben unvollständig; Reparatur fordert nur die fehlerhafte Quelle neu an. |
| Alte Zustände | Keine gültigen Seiten/Antworten verlieren | Vollständig aufgebauter Zustand ohne Cache bleibt No-op; gespeicherte Antwort ist bytegleich und weiterhin abfragbar. |
| No-op | Keine neuen Modellrequests | Unveränderter vollständig erfolgreicher Folgelauf ohne weitere Requests. |

Dauerhafte Rohbelege: `/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/`. `acceptance.json` in den dortigen `wiki-behavior-*`-Ordnern enthält Berichte, Requests und Query-Ergebnisse. `red-restart.txt` zeigt den ursprünglichen Fehler (vier statt zwei Requests); `red-corrupt.txt` und `red-review.txt` dokumentieren zusätzlich reproduzierte Gegenfälle. `patch-replay.json` bestätigt die bytegleiche Anwendung aller drei Patches auf den unveränderten Pin.

## Konkrete dauerhafte Messartefakte

- [SIGKILL und frischer Helper](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/restart/acceptance.json)
- [Lokale Einzelkorruption](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/corruption/acceptance.json)
- [Quell-, Modell- und Promptvertrag](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/contracts/acceptance.json)
- [Installiertes Schema und Compiler](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/schema-compiler/acceptance.json)
- [Quellendrift und echter Indexfehler](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/drift-index/acceptance.json)
- [Bestehende Antwort bytegleich erhalten](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/legacy/acceptance.json)
- [Leere Extraktion und unvollständige Datei](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/empty-incomplete/acceptance.json)

## Review und Grenzen

Das getrennte Standardsreview fand keine dokumentierte Verletzung und keine handlungsrelevanten Baseline-Smells. Eine unnötige Invalidierung durch `LLMWIKI_DEBUG` wurde entfernt und durch Rot→Grün geprüft. Das Specreview fand die upstream-seitige Filterung teilweise defekter Konzepte als echte Lücke: Ein solcher Versuch konnte erfolgreich publiziert werden, obwohl nicht vollständig cachefähig. Die neue Integration behandelt die ganze ungültige Antwort als begrenzten Fehler. Der Reviewer hat die gezielte Reparatur über die öffentliche CLI bestätigt; keine weiteren bestätigten Specbefunde.

Leere Extraktionen sind bereits im bestehenden verwalteten Compilervertrag Fehler (`No concepts extracted`), keine erfolgreichen fachlichen Leerbefunde. Sie werden deshalb nicht als Erfolge gesichert. Bei impliziter Codex-Auswahl ist der tatsächlich verfügbare lokale Vertrag `codex-cli-default` plus CLI-Version; unsichtbare Backendänderungen hinter unveränderter Modellkennung sind lokal nicht erkennbar. Cacheeinträge werden derzeit aufbewahrt; automatisches Bereinigen alter Vertragsversionen ist nicht Teil dieses Tickets.

Die Testprozesse besitzen eigene Abbruchfristen und beenden ausschließlich ihren eigenen Prozessbaum. Ein vollständig beendeter Eigentümer erlaubt Wiederaufnahme über die bestehenden Locks. SIGKILL wurde isoliert geprüft, kein Stromausfalltest. Produktionsbudget, laufende Fortschrittsberichte, Priorisierung und Aktivierung gehören den nachfolgenden Tickets.

## Separate kritische Verifikation

Die gesonderte Nachprüfung des Ausgangsmanifests `f6b7c0ff1d3518e3e6a0ad9bd734d9dd898b947b477ef5997cf3ded812af043e` fand einen weiteren bestätigten Gegenfall: Der bisherige Upstream-Parser ignorierte schemawidrige optionale Felder (`confidence: "certain"`, `tags: [42]`). Eine solche Antwort galt trotzdem als Erfolg. Die Integration validiert jetzt vor Speicherung und Publikation das vollständige tatsächlich verwendete Tool-JSON-Schema mit dem bereits vorhandenen Ajv. Der öffentliche Rot-Nachweis steht in [critical-red-schema.txt](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-red-schema.txt). Das Specreview hat die Reparatur erneut bestätigt; keine weitere bestätigte Lücke.

| Kritisches Gegenbeispiel | Gemessenes Ergebnis | Rohbeleg |
| --- | --- | --- |
| Abbruch bei genau einer gespeicherten Quelle und einer offenen Extraktion | Ein Cacheeintrag vor SIGKILL; danach Alpha genau ein Request, Beta zwei Versuche. WikiQuery liefert beide Quellen als fertige Wiki-Evidenz; insgesamt drei Requests. | [Einzelner gesicherter Fortschritt](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/single-durable/acceptance.json) |
| Reale Dateisystemobstruktion nach valider Beta-Modellantwort | `ok:false`, `saved:1` ausschließlich für vorher vollständig gespeicherte Alpha-Extraktion, `lastCompleted:null`. Reparatur: `saved:1/reused:1`, insgesamt drei Requests. | [Speicherfehler](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/storage-failure/acceptance.json) |
| Schemawidrige optionale Modellfelder | Keine Speicherung/Publikation der defekten Quelle; nur die unabhängige Quelle gesichert. Reparatur: drei Requests insgesamt, ein wiederverwendeter Erfolg. | [Vollständige Schemavalidierung](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/schema-validation/acceptance.json) |
| Quellidentität ohne Inhaltsänderung | Umzug des Alpha-Originalrepos bei gleicher Repo-ID und gleichem Inhalt: ein neuer Alpha-Request, Beta wiederverwendet; Query verweist auf den neuen Originalpfad. | [Identität und Providerparameter](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/identity-options/acceptance.json) |
| Tatsächlich gesendete Provideroption | `temperature:0.25` im beobachteten Request: beide Extraktionen neu; anschließende Reparatur ohne neue Extraktion, insgesamt fünf Requests. | [Identität und Providerparameter](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/identity-options/acceptance.json) |
| Cacheloser alter Bestand | Gespeicherte Antwort mit 824 UTF-8-Bytes bleibt bytegleich; unveränderte Pflege ist No-op und WikiQuery erfolgreich. | [Bestandsschutz](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-evidence/legacy/acceptance.json) |

Alle bisherigen Cache-Gegenfälle wurden auf dem reparierten Stand erneut über die öffentliche Grenze geprüft: [13/13 Tests](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-final-tests.txt), [59/59 Compilerprüfungen](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-upstream.txt), Typecheck und bytegleicher [Patch-Replay](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/critical-patch-replay.json). Die bereits grüne gesamte Baselinesuite wurde nicht grundlos wiederholt.

Rohmessdaten wurden nicht umgeschrieben. Die [lesbare Herkunftszuordnung](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/evidence-path-map.md) und [vollständige Pfad-/Hashzuordnung](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/evidence-path-map.json) übersetzen eingebettete ursprüngliche Pfade auf dauerhafte Kopien. 648 ursprüngliche und neue Evidenzdateien wurden SHA-256-verglichen; alle Kopien sind bytegleich. Die Originale der kritischen Nachprüfung liegen zusätzlich bereits dauerhaft im Batchordner.

## Prüfstatus

Alle 79 Verhaltenstests sind erfolgreich nachgewiesen: erster Gesamtlauf 78 bestanden und ein Worktree-Harnessfehler wegen des fehlenden relativen Reconciliation-Scripts; dieser einzelne Test bestand mit explizitem kanonischem `WIKI_RECONCILE_SCRIPT`. Keine Produktänderung zur Reparatur des Testpfads. Dazu 59 Upstreamtests in sechs Dateien, acht Python-Operationschecks, Typecheck, strikte OpenSpec-Validierung und bytegleicher Patch-Replay. Die separate kritische Schemareparatur wurde anschließend mit allen 13 betroffenen Cachetests und den 59 Compilerprüfungen erneut verifiziert; die vollständige Tool-Schemavalidierung ist der einzige Produktcodeunterschied zur initialen Abnahme.

[Finaler Gesamtlog](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/final-full-check.txt) enthält den Erstbefund und die Nachprüfung ausdrücklich getrennt. [Inhaltsmanifest](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket02/content-manifest.json) bindet diesen Stand an den Basiscommit `48e2c848d211145197622d5942a3ae9322c26b08`; Integration gegen das inzwischen nur um Ticket-01-Abschlussdokumentation fortgeschriebene `main` erfolgt erst nach separater kritischer Abnahme.
