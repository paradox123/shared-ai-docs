# Ticket 03: Pflege nach begrenzten Fehlern

Umgesetzt am 13.09.2026 im isolierten Worktree `shared-ai-docs-wiki-03`, Branch `codex/shared-wiki-03`, auf dem von Daniel bestätigten Ticket-01-Stand `1c13f08`. Der ursprüngliche Arbeitsbaum auf `main` enthielt fremde Änderungen und wurde nicht bearbeitet. Das bestehende Betriebs-OpenSpec besitzt diese Arbeit als Aufgabe 4.4; Ticket 02 ist keine Voraussetzung. Live-Job, Zeitplan und produktive Wissensbestände wurden nicht umgestellt.

## Beobachtetes Verhalten

Die Prüfung läuft über öffentliche `wiki maintain`, `status`, `lint`, `search`, `query`, `save` und den Helper-Prozess. Der gepinnte Atomicstrata-Compiler und eine isolierte echte QMD-Datenbank werden verwendet. Der lokale HTTP-Provider erzeugt deterministische Antworten und tatsächliche Fehler: eine leere, vom Compiler abgewiesene Seite sowie HTTP 400 bei Extraktion beziehungsweise Antwortbildung. Es werden keine Compiler-Gesamtergebnisse simuliert.

| Ticketkriterium / Erwartung | Beobachtetes Ergebnis und Evidence |
| --- | --- |
| Unabhängige Quelle wird trotz begrenzten Fehlers aktualisiert | Nach Änderung von Alpha und der Kontrollquelle schlägt die Freigabe-Seite tatsächlich an der Compiler-Validierung fehl. Die Kontrollseite enthält **„Kontrolle NEU“**; die verwaltete Query verwendet sie als Wiki-Evidenz ohne Quellen-Fallback. [Teilfehlerbericht](../.local/ticket03/acceptance/wiki-behavior-FYs8Ei/output/.state/runs/c22c4aca-81c8-4243-a328-3255f147e955/report.json), [erhaltene Kontrollseite](../.local/ticket03/acceptance/wiki-behavior-FYs8Ei/output/wiki/concepts/kontrollseite.md). |
| Direkte und transitive Abhängigkeiten werden gesperrt | Derselbe Lauf sperrt `concepts/freigabe`, `answers/direct` und `answers/transitive`; die verwaltete Suche liefert keine davon. Ein eigener Test für persistierte Konzeptabhängigkeiten sperrt zusätzlich eine zuvor als unabhängig erscheinende Kontrollseite. [Bericht des Konzeptgraph-Tests](../.local/ticket03/acceptance/wiki-behavior-s6x4F9/output/.state/runs/b7d34b09-1b16-4e9b-a9bd-9049d501d2ed/report.json). |
| Unvollständiger Scan erzeugt keinen Massenentzug | Ein konfigurierter Repo-Root wird tatsächlich umbenannt. Pflege und Query melden Unvollständigkeit; die bisherige Seite bleibt bytegleich erhalten. Nach Rückkehr des Roots ist die Pflege wieder No-op. Bestehende Recovery-Tests prüfen auch einen Root, der durch eine normale Datei ersetzt wurde. [Scanbericht](../.local/ticket03/acceptance/wiki-behavior-zBQkIs/output/.state/runs/d3ef8fb2-0fcb-4fef-b13b-fdd7c9e157fc/report.json). |
| Unbekannte Abhängigkeiten und gemeinsame Fehler blockieren abhängige Arbeit | Fehlgeschlagene Erstextraktion ohne bisherige Konzeptzuordnung veröffentlicht keine behaupteten unabhängigen Resultate. Eine Antwort mit fehlendem Abhängigkeitsdatensatz bleibt als zurückgezogene, offene Arbeit erhalten. Ein echtes nicht auflösbares QMD-Modul meldet abgeschlossene Inhaltsarbeit und offene Indexierung mit `qmdSafe: false`. [Indexfehler](../.local/ticket03/acceptance/wiki-behavior-09j1m7/output/.state/runs/769946e8-31a9-4128-b4eb-15c43704308f/report.json). |
| Sichere Retrieval-Pflege verdeckt keinen Wiki-Fehler | Tatsächlicher HTTP-400-Extraktionsfehler lässt die eigene echte QMD-Aktualisierung und Suche nach der unabhängigen Seite erfolgreich abschließen. Im Helper laufen anschließend die freigegebenen Retrieval-Schritte; Gesamt-Exit und `ok` bleiben erfolglos. [Helper-Teilfehlerbericht](../.local/ticket03/acceptance/wiki-behavior-7keQmP/partial-job/report.json). |
| Fertige, unveränderte, fehlgeschlagene und offene Arbeit sind unterscheidbar | Wiki-Berichte enthalten `completed`, `unchanged`, `failures`, `pending`; Helper-Schritte behalten zusätzlich `outcome` und den tatsächlichen `exitCode`. `lastCompleted` wird bei Teilfehlern nicht vorgezogen. Der Antwortfehler-Test veröffentlicht beide fertigen Konzepte und behält nur die Antwort als offen. [Antwortfehlerbericht](../.local/ticket03/acceptance/wiki-behavior-Epzwaa/output/.state/runs/03b7cae5-e871-4e29-b3ee-f639cdb9f784/report.json). |
| Rohdaten und Ergebnisverträge bleiben überprüfbar | Helper bewahrt `.stdout`, `.stderr`, `.exitcode` und `report.json` je Lauf. Die Wiki-CLI bewahrt zusätzlich `compiler-result.json`. Fehlende Felder oder Berichte, ungültiges JSON, Widersprüche und ausstehende Audits blockieren abhängige Schritte. [Echter stdout](../.local/ticket03/acceptance/wiki-behavior-7keQmP/partial-job/03-maintain-test.stdout), [Exitcode 1](../.local/ticket03/acceptance/wiki-behavior-7keQmP/partial-job/03-maintain-test.exitcode), [Vertragstests](../test/test_maintenance_job.py). |
| Reparatur vermeidet unnötige Wiederholung und Duplikate | Nach Behebung werden Freigabe und zwei Antworten erneuert; die Kontrollquelle wird nicht erneut extrahiert. Danach bestehen genau vier aktive Seiten, der nächste Lauf erzeugt keine Modellaufrufe. [Reparatur](../.local/ticket03/acceptance/wiki-behavior-FYs8Ei/output/.state/runs/c74d5569-fe8e-4e4c-8d3f-0ee9c403fb84/report.json), [Helper-No-op](../.local/ticket03/acceptance/wiki-behavior-7keQmP/noop-job/report.json). |
| Schreibsperren gelten weiterhin | Die bestehende öffentliche Recovery-Prüfung startet konkurrierende Wiki-Schreibaufrufe während laufender Generierung; nur der erste arbeitet. Der Helper-Test hält eine echte Betriebssystemsperre, der zweite Aufruf startet keinen mutierenden Prozess. [Recovery-Tests](../test/recovery.test.ts), [Helper-Tests](../test/test_maintenance_job.py). |

## Umsetzung und Reproduzierbarkeit

Der optionale [Compiler-Patch](../patches/0002-bounded-provider-failures.patch) meldet begrenzte Provider-/Validierungsfehler mit betroffenen Quellen an die Pflege; Fehler an gemeinsam genutzten Dateisystem-/Runtime-Schritten bleiben Abbrüche. Die [Abhängigkeitsschließung](../src/failure-scope.ts) berücksichtigt alte und neue Konzeptbesitzer sowie persistierte Seitenkanten bis zum Fixpunkt. Fehlgeschlagene Quellen und zurückgezogene Antworten behalten Wiederaufnahmeinformationen.

Frühere Wiki-Seiten und der Compiler-Index werden nicht als unprotokollierter Modellkontext wiederverwendet. Ältere `publicationVersion: 1`-Bestände werden deshalb einmal vollständig aus aktuellen Quellen neu aufgebaut; die neue Version 2 erlaubt danach unabhängige Wiederverwendung. Ein öffentlicher Verhaltenstest prüft diesen einmaligen Übergang samt folgendem No-op. Die Migration zwischen alten getrennten Ausgaben bleibt Ticket 02.

Aus `contextual-llm-wiki/`:

```bash
npm run check
./wiki-node --test test/bounded-failures.test.ts
```

Aus dem Git-Root:

```bash
openspec validate operate-contextual-llm-wiki --strict
git diff --check
```

Verifikation: **45 Wiki-Verhaltenstests, 59 gepinnte Compiler-Kompatibilitätstests, 8 Helper-Tests**, Typecheck und strikte OpenSpec-Validierung erfolgreich. Beide Compiler-Patches wurden zusätzlich nacheinander auf einem frischen Archiv des Pins angewendet. [Gesamtprotokoll nach Reviewkorrektur](../.local/ticket03/review-check.txt), [zehn isolierte Ticket-03-Nachweise](../.local/ticket03/acceptance-check.txt). Rot→Grün wurde für unabhängige Veröffentlichung, Antwortfehler, fehlenden Root, fehlende Antwortabhängigkeit, transitive Konzeptabhängigkeit, Berichtsfelder, Provenienz-Upgrade und Index-Restarbeit beobachtet.

## Grenzen

Die eigene QMD-Indexierung und Suche sind real. Die globalen Reconciler-/QMD-/Embedding-Prozesse des Helper-Integrationstests sind isolierte Prozess-Doubles; deren Ausführungsfreigabe und Fehlerweitergabe sind verifiziert, ein neuer vollständiger Embedding-Lauf über Daniels produktiven Bestand wurde nicht ausgeführt. Die Providerfehler sind real ausgelöste HTTP-/Validierungsfehler an einer deterministischen lokalen Providergrenze; diese Prüfung behauptet keinen neuen Cloud-Providerlauf. Frühere echte Providerabnahmen bleiben in Ticket 01 dokumentiert.

Alle verlinkten Rohartefakte bleiben lokal und ignoriert. Produktive Aktivierung, Vollimport, Migration und Archivierung dieses Betriebs-Changes sind nicht Teil von Ticket 03.

## Review

### Standards

Keine Code-Standardverstöße oder materiellen neuen Code-Smells im Vergleich zu `1c13f08`. Die im ersten Durchgang noch fehlenden Evidence-/Task-Verweise sind ergänzt.

### Spec

Ein P1-Finding wurde mit `9359b47` behoben: Ein gleichzeitiger HTTP-400-Fehler und eine vom Compiler wegen ihrer Größe abgewiesene Seite konnten die zweite Quelle aus der offenen Arbeit verlieren. Der neue Regressionstest beobachtete zunächst den Fehler und anschließend korrekte Blockade mit `qmdSafe: false`, erhaltenen Quellenänderungen, erfolgreicher Wiederaufnahme beider Konzepte und folgendem No-op. Jeder Compilerfehler muss jetzt einer dokumentierten begrenzten Fehlerursache entsprechen; nicht zugeordnete Fehler blockieren die Veröffentlichung. [Regressionstest-Protokoll](../.local/ticket03/review-regression.txt). Der unabhängige Spec-Reviewer wiederholte seinen ursprünglichen Reproducer erfolgreich gegen die Korrektur und meldete keine weitere materielle Abweichung.

Ergebnis: Standards 0 offene Findings; Spec 1 behoben, 0 offen. Keine ausstehende höchste Schwere in beiden Achsen.


## Akzeptierter Abschluss

Daniel hat das Ergebnis am 13.09.2026 ausdrücklich akzeptiert und Spec-/OpenSpec-Abschluss, Commit und Push beauftragt. Das Ticket-03-Requirement wird im separaten Change [continue-contextual-wiki-maintenance](../../openspec/changes/archive/2026-09-13-continue-contextual-wiki-maintenance/proposal.md) kanonisch abgeschlossen. Die erneute DRY/SOLID/KISS-Prüfung vor Archivierung ergab keinen weiteren Codeänderungsbedarf. Der übergeordnete Betriebs-Change bleibt für Migration, Live-Aktivierung und Vollimport offen.

Der Abschluss wurde über `openspec archive -y continue-contextual-wiki-maintenance` durchgeführt; die CLI übernahm das Requirement nach `openspec/specs/contextual-wiki-operations/spec.md`. Vor Archivierung bestanden erneut Typecheck, alle elf Ticket-03-Verhaltenstests und acht Helper-Tests.
