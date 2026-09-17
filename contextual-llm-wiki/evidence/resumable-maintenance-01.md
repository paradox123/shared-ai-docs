# Ticket 01: Unabhängiger Fachquellenindex

Stand: 17.09.2026. Implementierung in `codex/wiki-maintenance-01`, Ausgangsstand `834a6d3d760e290a26d1365ec1e99f2222c7593f`, Ziel `main`. Isolierte Abnahme; keine Live-Automation und keine Produktivdaten verändert. Der aktive OpenSpec-Change bleibt für die übrigen Tickets und die spätere Produktivabnahme offen.

## Verhalten und Messungen

| Anforderung / Soll | Beobachtetes Ist |
| --- | --- |
| Neuer Inhalt vor gescheiterter Erstkompilierung auffindbar | Öffentlicher Python-Helper indiziert zwei Originale mit dem echten QMD-SDK; die kontrollierte Extraktion scheitert. Bericht: `sourceIndex.ok=true`, `wiki.ok=false`, Exit 1. WikiQuery liefert zwei QMD-Quellentreffer und zwei aktuelle Originalverweise, `fallback=true`, `sourceRetrieval=qmd-source-index`; `lastCompleted=null`. |
| Geänderte Quelle ohne alte Wiki-Aussage | QMD meldet ein aktualisiertes und ein unverändertes Original. Wiki-Suche liefert keine alte Freigabeseite. Die begrenzte Query liefert „vier Freigaben“, nicht die vorherigen „zwei“, und nur `alpha/README.md`. Vollständiger Pflegezeitpunkt bleibt unverändert. |
| Gemeinsamer Umfang, explizite Grenzen, Aktualität | `--repo private` liefert ausschließlich `private/README.md`, `--source alpha/README.md` ausschließlich Alpha. Ein Edit nach Indexierung liefert den aktuellen Stand über `current-source-scan`, ohne den alten Indexhash als aktuellen Treffer auszugeben. |
| Relevante neue Quelle bei bestehender Synthese | Auch bei fünf relevanten aktuellen Wiki-Seiten erscheint das neue Original in der begrenzten Evidenzmenge. Nicht abgedeckte relevante Originale erhalten Platz vor bereits synthetisierten Belegen. |
| Provider-Authentifizierung unabhängig | Fehlender API-Key: null Provideranfragen, Quellenindex erfolgreich, Wiki und Gesamtlauf unvollständig. Der äußere Helper zieht die Providerprüfung nicht mehr vor die unabhängige Indexpflege. |
| Unvollständiger Scan versus bestätigte Entfernung | Nicht verfügbarer Repo-Root: Indexstatus blockiert; nach Rückkehr ist der zuvor indexierte Alpha-Beleg unverändert auffindbar. Bestätigtes Löschen einer Datei reduziert den Quellenindex von zwei auf eine Quelle. |
| Indexfehler blockiert abhängige Modellarbeit | Nicht ladbares QMD-Modul: Quellenindex und Wiki nicht erfolgreich, null Modellanfragen, kein vollständiger Pflegezeitpunkt. Wiederholung nach Reparatur führt die noch ausstehende Kompilierung aus. |
| Serialisierte konkurrierende Pflege | Der erste reale Helper hält den bestehenden Pflege-Lock. Während seine Providerantwort angehalten ist, existieren bereits zwei echte QMD-SDK-Treffer. Ein zweiter Helper bricht vor jedem Mutationsschritt ab (`steps=[]`). Nach dem kontrollierten Providerfehler liefert WikiQuery dieselben zwei aktuellen Originale. |
| Erfolgreicher unveränderter Folgelauf | `noop=true`, `sourceIndex.status=unchanged`, keine neuen Modellaufrufe; Wiki-Synthese bleibt suchbar. |
| Bestehende QMD-Registrierung erhalten | Reale Manifest-Reconciliation registriert Wiki und Quellen in der isolierten Datenbank; eine fremde Collection bleibt unverändert und suchbar. |

## Prüfgrenzen und Reproduktion

Die Tests verwenden temporäre Git-Fachrepos, getrennte Ausgaben, lokale HTTP-Provider auf dynamischen Ports und je Fixture eine echte QMD-SQLite-Datenbank. Nur die externe Modellantwort wird kontrolliert. Die Core-Kompilierung, Quellenprüfung, QMD-Indexierung, Retrieval und WikiQuery sind real. In den gezielt fehlschlagenden Helperläufen kann kein globales `qmd update/embed` einen fehlenden Quellenindex kaschieren: dessen Befehl ist absichtlich `/usr/bin/false`, der Lauf endet vorher mit einem dokumentierten Wiki-Fehler. Eine zusätzliche direkte QMD-SDK-Abfrage beweist Treffer bereits vor dem Providerfehler.

Der Suchnachweis gilt für den bestehenden lexikalischen QMD-/WikiQuery-Pfad. Er behauptet keinen neuen semantischen Suchmodus und keinen abgeschlossenen Embedding-Lauf (`needsEmbedding` bleibt separat sichtbar). Keine Produktionshelfer wurden gestartet. Testfristen: Helperprozess 30 Sekunden, direkte QMD-Diagnose 10 Sekunden, Fehlerszenarien 15–45 Sekunden; der zusätzliche Fünf-Seiten-Aufbau hat eine 60-Sekunden-Testfrist.

```bash
cd contextual-llm-wiki
./wiki-node --test test/source-index.test.ts
WIKI_RECONCILE_SCRIPT=/path/to/danielsvault-rag/scripts/sync-qmd-collections.py npm test
npm run typecheck
npm run test:operations
npm run test:upstream
cd ..
openspec validate operate-contextual-llm-wiki --strict
```

`WIKI_RECONCILE_SCRIPT` ermöglicht dem vorhandenen Integrationstest die explizite Nutzung des bestehenden Reconciler-Skripts aus einem isolierten Worktree. Alle dessen QMD-Schreibzugriffe bleiben durch `INDEX_PATH` und `QMD_CONFIG_DIR` im Testbestand.

Finaler Gesamtlauf: **67/67** öffentliche TypeScript-Verhaltenstests erfolgreich (160,987 Sekunden), darin alle sieben neuen Abnahmefälle. Zusätzlich: **8/8** Python-Helpertests, **59/59** Upstreamtests, Typecheck, `git diff --check` und strikte OpenSpec-Validierung erfolgreich.

Dauerhafte Rohbelege dieses finalen Gesamtlaufs liegen unter `/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/`. Ausschließlich `ticket01-tests-accepted.log` bezeichnet den finalen grünen Gesamtlauf; frühere `*-final.log`-Dateien sind Entwicklungsläufe und keine Abnahmebasis.

- [Vollständiger finaler Testlauf](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-tests-accepted.log)
- [Erstimportfehler: Quellenindex und WikiQuery](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-final-fixtures/wiki-behavior-vSjoqH/acceptance.json)
- [Änderung, explizite Grenzen und No-op](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-final-fixtures/wiki-behavior-qKcWJF/acceptance.json)
- [QMD-Treffer vor Providerfehler, konkurrierender Helper und Treffer danach](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-final-fixtures/wiki-behavior-9uE4MU/acceptance.json)
- [Neues Original trotz fünf aktueller Wiki-Seiten](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-final-fixtures/wiki-behavior-ktTwSd/acceptance.json)
- [Authfehler bei erfolgreicher Quellenindexierung](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-final-fixtures/wiki-behavior-6KZOP4/acceptance.json)


## Review

Standards-Achse: keine harten Verstöße; doppelte Zurücknahme und wiederholter Quellenindexpfad wurden konsolidiert. Spec-Achse: Auth-Vorabprüfung und Verdrängung neuer Quellen durch vorhandene Wiki-Evidenz wurden als rote Tests reproduziert und behoben; der zusätzliche Fünf-Treffer-Grenzfall ebenfalls. Statische Nachprüfung meldet keine offenen Findings. Keine Änderung an den sechs bestätigten Ticketumfängen, keine Archivierung.

## Gesonderte kritische Verifikation

Nach der initialen Abnahmevorlage wurde das Ergebnis separat gegen zusätzliche Gegenbeispiele geprüft. **Vier gezielte Prüfungen erfolgreich**, drei davon neu, eine erweiterte Lock-Prüfung; 13,710 Sekunden Gesamtdauer. Keine Produktcodeänderung war erforderlich. Der bereits grüne Gesamtlauf wurde daher nicht ohne Anlass vollständig wiederholt. Typecheck, Diff-Prüfung und OpenSpec strict wurden für die ergänzten Tests erneut erfolgreich ausgeführt.

| Zusätzliche Gegenprobe | Gemessenes Ergebnis |
| --- | --- |
| Alter Inhalt noch roh in QMD, Authfehler nach Quellenindex | Zwei alte Wiki-QMD-Treffer vorhanden; WikiQuery liefert ausschließlich aktuelle Originale. Ein echter gezielter QMD-Update auf die zurückgezogenen Wiki-Dateien entfernt beide alten Treffer (2 → 0); der Originalquellenindex bleibt nutzbar. Ein roher Indexrest wird ausdrücklich nicht mit aktueller Wiki-Evidenz gleichgesetzt. |
| Tatsächlicher Dateisystemfehler im Quellen-Snapshot | Index und Wiki melden Nicht-Erfolg; exakt null zusätzliche Provideranfragen. Originaldatei und vorheriger vollständiger Pflegezeitpunkt bleiben erhalten. Nach Beseitigung des ausschließlich im Test erzeugten Hindernisses gelingt Wiederaufnahme. |
| Erlaubte neue Quelle noch unindexiert, andere Treffer außerhalb der Grenze | `--source beta/new.md` liefert ausschließlich den aktuellen neuen Beta-Beleg, `sourceMatches=[]`, `sourceRetrieval=current-source-scan`; kein fremder indizierter Treffer verdrängt oder erweitert diese Evidenz. |
| Konkurrent umgeht versehentlich den äußeren Helper-Lock durch anderes Artefaktverzeichnis | Der Kontext-Writer-Lock blockiert ihn bei `maintain-test` mit `Context locked by writer`. Der ursprüngliche Helper behält seinen Zustand; danach weiterhin zwei echte aktuelle Originaltreffer. Der zusätzliche Test ergänzt den bereits gemessenen äußeren Helper-Lock (`steps=[]`). |

Nachweise dieser gesonderten Runde:

- [Gezielter kritischer Prüflauf](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-critical-accepted.log)
- [Rohes stale Wiki-QMD und echter Reindex](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-critical-fixtures/wiki-behavior-LszQ7J/critical-acceptance.json)
- [Speicherfehler und Wiederaufnahme](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-critical-fixtures/wiki-behavior-uF4G0D/critical-acceptance.json)
- [Erlaubte unindexierte Quelle](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-critical-fixtures/wiki-behavior-falH4X/critical-acceptance.json)
- [Beide Lock-Grenzen und reale QMD-Treffer davor/danach](/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket01-critical-fixtures/wiki-behavior-lzDz1G/acceptance.json)

Die Serialisierungsnachweise gelten für die verwaltete Pflege mit gemeinsamem Helper-Lock beziehungsweise derselben Kontextausgabe. Sie behaupten keine Sperrung beliebiger außerhalb des Helpers gestarteter direkter QMD-CLI-Aufrufe. Die bestehende explizite gemeinsame Lock-Konfiguration bleibt erforderlich. Alle neuen Prüfungen verwenden eigene Datenbanken und Prozesse; bestehende Produktionslocks wurden weder entfernt noch umgangen.
