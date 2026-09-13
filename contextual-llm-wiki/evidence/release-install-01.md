# Release-Ticket 01: reproduzierbarer Kandidat

Stand: 13.09.2026. Implementiert auf `codex/update-llm-wiki-releases`, Ausgangs-/Review-Commit `dbb6df2030f26543099eb34d3bb6b7ff38963dbc`. Isolierter Worktree `../shared-ai-docs-update-llm-wiki-releases`; bestehende Änderungen auf `main` bleiben außerhalb dieses Branches. Der Checkout-Hook stellte globale Skill-Aliase automatisch um; sie wurden unmittelbar auf den ursprünglichen Checkout zurückgestellt.

## Abnahme über den öffentlichen Aufruf

`python3 test/accept-release.py --release v1.3.0` ruft ausschließlich `scripts/install-release.py` als Prozess auf. [Maschinenlesbare Ergebnisse](release-install-01-results.json) enthalten beide Kandidatenberichte und Vorher-/Nachher-Prüfsummen der aktiven Installation im Worktree. Die lokalen Kandidaten enthalten die vollständigen Logs und künstlichen Testbestände; ihre absoluten Pfade stehen im Ergebnis.

| Ticketanforderung | Erwartung und beobachtetes Verhalten | Evidenz |
| --- | --- | --- |
| Gemeinsame Versionsdefinition | Bootstrap und Runtime lesen `compiler-release.json`; bisheriger Commit und v1.3.0 bleiben erhalten. Bootstrap einschließlich Build und bestehender CLI-Preflight-Test bestanden. | `compiler-release.json`, `scripts/bootstrap.sh`, `src/runtime.ts`, `test/cli.test.ts` |
| Reguläres Release → exakter Commit | GitHub Release-ID **386878086**, v1.3.0, veröffentlicht 11.09.2026; Git-Fetch löst den Tag auf **34ca1df97b3e60a6700048c48c7cf70c92a9bfdb** auf. Drafts, Vorabversionen, fehlende Metadaten und bloße Tags ohne Release werden abgewiesen. | Ergebnisfelder `release`/`commit`; öffentliche Installer-Verhaltenstests |
| Upstream-Abhängigkeiten beibehalten | Eigene frische Installation durch `npm ci`, kein Library-Update und keine Lock-Neuauflösung. Manifest und Lockdatei vor/nach Patch, Installation und Prüfungen bytegleich. Beide realen Kandidaten haben identische Dependency-Eingänge. | `dependencyInputs` in beiden Berichten; ungültige Release-Lockdatei scheitert unverändert |
| Patch-/Runtime-/Installationsfehler | Beide bestehenden Patches lassen sich auf dem echten Commit anwenden. Konfliktfixture, fehlende/inkompatible Runtime und ungültige Lockdatei liefern Fehler und offene Folgeschritte. Bestehende Ziele und Pfade innerhalb der aktiven Installation werden nicht überschrieben. | `patches` mit SHA-256; `test/test_release_install.py` |
| Build und öffentliche Integration | Echter Release-Build, Typecheck, **59 Upstream-Tests** und **29 Integrationstests** bestanden. Query liefert belegte Antworten und navigierbare Originale; eine Quellenänderung sperrt veraltete Evidenz, nutzt aktuelle Quellen und wird durch Nachpflege übernommen. Gespeicherte Antworten und No-op funktionieren. | `checks`; Kandidatenlogs; `test/release-compatibility.test.ts` plus Lifecycle-, Integrity- und Fehlerfortsetzungstests |
| Kandidatengebundene Eignung | Erfolgreicher Kandidat: Exit 0, `eligible:true`, alle zehn Schritte bestanden. Fehlerkandidat mit entferntem Pflicht-Test: Installation/Build bestanden, Integrationsprüfung fehlgeschlagen, Integrity ausstehend, Exit 1 und `eligible:false`. | Beide Kandidatenberichte; `wrapperSha256`, `compilerBuildSha256`, Runtime-Hash |
| Bestehenden Stand erhalten | Release-Definition, Einstiegsskripte, aktiver Commit, Patch-Diff, Manifest, Lockdatei und aktiver Build im Worktree vor/nach beiden Aufrufen identisch. Keine produktive Konfiguration wurde übergeben. | `activeInstallationUnchanged`, `activeBefore`, `activeAfter` |

Der echte Release- und Git-Nachweis kommt vom bestätigten Projekt: [Release v1.3.0](https://github.com/atomicstrata/llm-wiki-compiler/releases/tag/v1.3.0). Die Transportwahl folgt der [GitHub Release-API](https://docs.github.com/en/rest/releases/releases#get-a-release-by-tag-name), die Installation dem eingefrorenen Vertrag von [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/).

## TDD und Verifikation

Öffentliche Prozessgrenze: Installer-Exitcode, JSON-Bericht, Kandidatendateien. Nachgewiesene Rot→Grün-Slices: Vorabversionsablehnung, fehlende Runtime, exakter annotierter Release-Commit mit Patchkonflikt und Schutz der aktiven Installation. Der echte Aufruf lieferte vor der Installer-Erweiterung nach erfolgreichem Release-/Patch-Nachweis ausstehende Installations-/Build-/Testschritte und keine Eignung; anschließend bestand der reale Kandidat. Der CLI-Kompatibilitätstest wurde zunächst gegen die vorhandene Integration grün geprüft.

Gesamttests und abschließender zweigeteilter Review laufen noch; Ergebnisse werden vor Abschluss ergänzt.

## Grenzen und Folgetickets

Der Modellprovider wird lokal deterministisch beantwortet; GitHub, Git, npm, Compiler-Build und QMD sind echt. Es wurden künstliche, begrenzte Quellen und getrennte Datenbanken verwendet. Diese Abnahme behauptet keinen produktiven Vollimport oder Schedulerlauf. Ein echtes neues Release mit höherer Node-Anforderung wurde nicht angeboten; der Installationsaufruf weist fehlende/inkompatible Runtime sichtbar ab und verändert den aktiven Node nicht.

Das Release ist auf GitHub veränderbar. Jeder Aufruf löst den dann vorhandenen Tag erneut auf und dokumentiert den geprüften Commit; der lokale Kandidat behält diesen Commit. Bericht und Hashes beschreiben den geprüften Zustand, keine dauerhafte Unveränderlichkeit nach manuellen Eingriffen. Ein Aktivierer muss den Kandidaten vor Übernahme erneut gegen seine Identität prüfen. Aktivierung/Rollback (Ticket 02), automatische Erkennung (Ticket 03) und offene Wissenspflegeaufgaben bleiben offen. Der gemeinsame Betriebs-Change wird nicht archiviert.
