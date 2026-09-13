## 1. Gepinnter Compiler und erste öffentliche Slice

- [x] 1.1 Isolierte Node-Umgebung und gepinnten Atomicstrata-Stand einrichten; Integrations-CLI mit Runtime-/Provider-Preflight und Versionsausgabe durch Black-Box-Test absichern (A12).
- [x] 1.2 Zwei temporäre Markdown-Repos über den echten Compiler bis zur gemeinsamen Wiki-Seite verarbeiten; Compile ohne Embeddings und ohne Wiki-Git-Initialisierung nachweisen (A2, A8, A10).
- [x] 1.3 Kleinsten QMD-/Query-/Save-Anschluss anhand des gepinnten SDK dokumentieren: schmaler Upstream-Hook oder vorhandener Agent mit geprüftem Save-Vertrag. Kein Ersatzcompiler oder ungeprüfter nativer Embedding-Pfad.

## 2. Quellen und Kontext

- [x] 2.0 Die acht Wurzeln und Inhaltszonen aus der initialen Repo-Liste als Startkonfiguration übernehmen; reine Inventur mit Scope, Ein-/Ausschlüssen und fehlenden Quellen ausgeben. Zweiten Shared-AI-Checkout und Test-Repos nachweislich ausschliessen; privaten Umfang separat ausweisen.
- [x] 2.1 Kontextkonfiguration, stabile Repo-/Quellenidentitäten und gerichteten Markdown-Abgleich testgetrieben implementieren; gleiche Dateinamen, rekursive Filter, uncommitted Änderungen und unveränderte Originale nachweisen (A1).
- [x] 2.2 Originalverweise und zeilenerhaltende Quellenzuordnung umsetzen; überlange Eingaben ohne stillen Inhaltsverlust behandeln und Scan-Fehler von bestätigtem Entzug unterscheiden (A1, A7).
- [x] 2.3 Allgemeine und explizit private Kontexte trennen; unselektierte Quellen und generierte Ausgabe aus Input und allgemeiner Suche ausschliessen (A9).
- [x] 2.4 Meetings und Projects rekursiv als initiale Markdown-Quellen aufnehmen; Ingestion und Originalbelege je einer Datei aus Meetings, Projects und Projects/Private im passenden Kontext nachweisen (A0).

## 3. Konzeptnachpflege

- [x] 3.1 Source-Ownership und Quellenstände zu einer beobachtbaren Prüfliste verbinden; Quellenkorrektur auf die betroffene Konzeptseite propagieren, unabhängige Kontrollseite erhalten (A3).
- [x] 3.2 Quellen-/Seitenversionen vor Veröffentlichung prüfen und unveränderte Wiederholung ohne zusätzliche Modellarbeit sicherstellen (A6, A7).

## 4. Query Save und QMD

- [x] 4.1 Wiki-eigenen QMD-Collection-Abgleich über die zuständige Konfiguration implementieren; reale Wiki-Suche ohne Compiler-Embedding-Store, Spiegel-Duplikate oder fremde Collection-Mutationen nachweisen (A8).
- [x] 4.2 QMD-basierten Agent-/Query-Zugriff über die öffentliche Integration und den Anschluss aus 1.3 umsetzen; aktive Wiki-Evidenz bevorzugen, Quellen-Fallback und sichtbaren Prüfbedarf verifizieren (A2, A12).
- [x] 4.3 Explizites Speichern von Antworten mit verwendeten Page-IDs, Versionen und transitiven Quellenständen implementieren; fehlende Provenienz nicht als frisch veröffentlichen (A11).
- [x] 4.4 Quellenkorrektur über Konzept und gespeicherte Antwort sowie Antwort-auf-Antwort weiterverfolgen; geänderte Aussagen nachprüfen und unabhängige Ausgaben erhalten (A3).

## 5. Entzug Fehler und Wiederaufnahme

- [x] 5.1 Repo-/Quellentzug durch aktive Dateien, gemischte Konzeptseiten, gespeicherte Antworten, Navigation und echte QMD-Treffer durchführen; reine Orphan-Markierung als Negativfall testen (A4).
- [x] 5.2 Wiederaufnahme eines entfernten Repos mit aktuellem Input und erneuter Kompilierung belegen (A5).
- [x] 5.3 Provider-, Scan- und Indexfehler sowie konkurrierende Schreiber und Änderungen während eines Laufs prüfen; Restarbeit und sichere Fortsetzung implementieren (A7).

## 6. Obsidian und Betrieb

- [x] 6.1 Git-freien aktiven Wiki-Bereich, Einstieg, Originalquellenlinks und Status/Lint-Bericht im vorhandenen Vault einrichten; verwaltete Agent-Nutzung dokumentieren (A10, A12).
- [x] 6.2 Lokale Sicherung und Wiederherstellung mit Antwortabhängigkeiten und kleinerem aktuellem Repo-Kontext nachweisen (A11).
- [x] 6.3 Betriebsanleitung für Setup, ausdrückliche Pflege, Query/Save, Kontextänderung und Fehlerbehebung verfassen; laufende Fachautomationen unverändert lassen.

## 7. Abnahme und Abschluss

- [x] 7.1 Deterministische Verhaltenssuite und relevante Upstream-Tests ausführen; mindestens einen fachlich geprüften Lauf mit echtem Modellprovider und repräsentativen Fachquellen belegen (A1–A9, A11–A12).
- [x] 7.2 Obsidian-Einstieg, gemeinsame Erkenntnis und Originalverweis sichtbar prüfen und Screenshots als Evidence ablegen (A10).
- [x] 7.3 Abnahmeübersicht pro Requirement mit Erwartung, Beobachtung, Evidence und offenen Grenzen ausfüllen; keine ungetestete Funktion als bestanden kennzeichnen.
- [x] 7.4 Implementierung, schmale Upstream-Anpassungen und Spezifikation auf DRY/SOLID/KISS prüfen; relevante Tests und `openspec validate integrate-contextual-llm-wiki --strict` erneut ausführen. Archivierung erst nach tatsächlicher Verhaltensabnahme.

Abnahmestand 12.09.2026: [28 öffentliche Tests, 59 Upstream-Tests, echter Provider- und QMD-Lauf](../../../../contextual-llm-wiki/evidence/acceptance.md) bestanden. Task 7.2 ebenfalls bestanden: Einstieg, Synthese und Originalverweis in Obsidian sichtbar geprüft; [drei echte Screenshots](../../../../contextual-llm-wiki/evidence/obsidian/README.md) vorhanden. Alle 24 Tasks abgeschlossen. Am 13.09.2026 ausdrücklich akzeptiert und über die OpenSpec-CLI archiviert.
