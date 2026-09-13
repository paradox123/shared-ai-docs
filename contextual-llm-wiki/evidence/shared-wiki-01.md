# Ticket 01: gemeinsames Wiki erzeugen und abfragen

Stand: 13.09.2026. Umsetzung auf `codex/shared-wiki-01` im isolierten Worktree `shared-ai-docs-wiki-01`; Git-Root beim Auftrag: `shared-ai-docs`, Ausgangsbranch `main` bei `599d750`. Daniel bestätigte den Zielbranch ausdrücklich. Die vorhandenen Wiki-Vorarbeiten wurden separat als `0b1e678` übernommen. Andere laufende Agent-Pilot-Änderungen wurden nicht übernommen.

Der bestehende Change `operate-contextual-llm-wiki` deckt die Änderung ab. Ticket 01 umfasst die gemeinsame CLI, explizite Aufgabenbegrenzung und QMD-Anbindung. Bestandsmigration, Fehlerisolation und Live-Aktivierung/Vollimport gehören zu Tickets 02–04. Der Live-Job und bestehende Ausgaben wurden nicht geändert.

## Abnahme über die öffentliche Schnittstelle

| Erwartetes Verhalten | Beobachtetes Ergebnis | Beleg |
|---|---|---|
| Acht Originalrepo-Identitäten; Meetings, Projects und Projects/Private rekursiv | Reale lesende Inventur: alle acht vorhanden, 1.888 Markdown-Dateien; vault-root 105 (Meetings 69, Projects 1, Projects/Private 1), meeting-assistant 240, shared-ai-docs 680, ki-fuer-kmu 551, ncg-docs 85, private 217, probare-crm 7, sparkle 3 | [Inventur](common-inventory.json); `initial common inventory` in [CLI-Tests](../test/shared-wiki.test.ts) |
| Gemeinsame Auswahl ohne Änderungen an Originalen, zusätzliche Worktrees/Runtime/Output ausgeschlossen | 11 erwartete Fixture-Quellen über acht Roots; verschachtelte Repos, Worktree-Gitmarker, Runtime und Ausgabe fehlen. Vorher waren es 9: private/README und Projects/Private fehlten | Inventurtest, [Lebenszyklustests](../test/lifecycle.test.ts) |
| Pflege erzeugt eine belegte gemeinsame Aussage | Echter gepinnter Compiler erzeugt `concepts/liquiditaetsreserve`: 2.000 Euro heutige Reserve und 5.000 Euro erst im Oktober erwartete Projekteinnahmen. Schluss: erwartete Einnahmen sind noch keine heutige Liquidität. Beide Original-IDs und Hashes sind verzeichnet | `common maintenance synthesizes...` in [CLI-Tests](../test/shared-wiki.test.ts); nur HTTP-Modellprovider deterministisch |
| Query verwendet Synthese ohne Privatmodus und verwirft irrelevanten Kontrollbeleg | QMD liefert auch den gleichlautenden Portfolio-Designkatalog. Query übernimmt nach fachlicher Auswahl nur die Liquiditätsreserve, ohne `control.md` | Derselbe CLI-Test; ursprüngliches Rot: `concepts/projektportfolio` fälschlich in Evidenz |
| Explizite Aufgabenbegrenzungen wirken transitiv und auf Fallbacks | `--repo private` verwirft gemischtes Konzept und zwei gespeicherte Folgeantworten, verwendet nur private/README; 5.000-Euro-Projektbeleg gelangt nicht zum Provider. `--source probare-crm/README.md` erlaubt ausschließlich diesen Originalbeleg. Search und Draft-Save respektieren dieselbe Grenze; unbekannte/leere Grenzen schlagen fehl | `explicit repository and exact-source limits...`; ursprüngliches Rot: gemischte Konzeptantwort statt begrenztem Fallback |
| Quellenänderung entwertet abhängige Seite vor Synchronisierung | Änderung von 2.000 auf 800 Euro: Query meldet Prüfbedarf, verwendet aktuelle Originale, gibt nicht den alten Betrag aus; nach Pflege wird wieder Wiki-Evidenz genutzt | `common queries reuse...`; zusätzliche Quelle–Konzept–Antwort–Antwort-Prüfung in Lebenszyklustests |
| Gültiges Wissen wiederverwenden, ohne implizite Speicherung oder Kompilierung | Zwei Queries lassen Seitenregister und Extraktionsanzahl unverändert; unveränderte Pflege ist ein No-op ohne Provideraufruf | `common queries reuse...` |
| QMD bleibt einzige Retrieval-Engine; gemeinsame Collection regulär sichtbar; fremde Collections unverändert | Echter Manifest-Abgleich in separater QMD-Datenbank; Standardsuche findet Liquiditätsreserve, Manifest hat `private:false`; fremde Collection bleibt bei Pfad/Pattern/Inhalt unverändert | `common QMD registration...`; [Prüfprotokoll](shared-wiki-verification.txt) |

## Prüfungen und Grenzen

`npm run check`: 33 öffentliche CLI-Verhaltenstests, 59 Compiler-Tests, 6 Betriebstests erfolgreich; TypeScript erfolgreich. `openspec validate operate-contextual-llm-wiki --strict` und `git diff --check` erfolgreich. Die ursprünglichen Privacy-Partitionstests sind durch gemeinsame Auswahl und explizite Evidenzgrenzen ersetzt.

Die Inhalts- und Relevanzauswahl bleibt Modellverhalten, kein mathematischer Relevanzbeweis. Modellantworten zur Auswahl dürfen nur tatsächlich angebotene IDs enthalten; ungültige Antworten brechen ab. Repo-/Quellenbegrenzung und Originalhash-Prüfung sind deterministisch. QMD liefert Kandidaten, keine ungeprüft autorisierte Evidenz.

Die gemeinsame Produktionsausgabe wurde noch nicht übernommen oder vollständig kompiliert. Die reale Inventur ist kein Vollimport. Bestehende alte Top-Level-Konfigurationen `general`/`private` werden mit Migrationshinweis abgewiesen, bestehende Ausgabestände nicht still konvertiert. Das Review und die ergänzende echte Provider-Abnahme werden nach Abschluss unten dokumentiert.
