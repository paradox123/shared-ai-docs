# Abnahme: Wiki-Pflege auf Daniels Mac

> Historischer Zwischenstand vor der Betriebsklärung: Die nachfolgende Abnahme betrifft den bisherigen getrennten Betrieb. Für das bestätigte gemeinsame Wiki nach ADR 0010 ist eine neue Abnahme gemäß `tasks.md` Abschnitt 4 erforderlich.

Stand: 13.09.2026. Die bestehende Automation ist aktualisiert und aktiv. Der ausführbare Ablauf ist mit echtem Codex-Provider, Compiler und QMD geprüft. **Der vollständige produktive Erstimport ist noch nicht erfolgt**; die neue Automation wählt `.local/general.json` für den nächsten regulären Termin. Der Change bleibt offen und wird nicht archiviert.

| Requirement | Erwartung | Beobachtung / Nachweis |
|---|---|---|
| Scheduled wiki maintenance before global retrieval maintenance | Bestehenden Zeitplan und Ausführungsumgebung behalten; explizites Wiki vor QMD update/embed | Live-TOML gegen Sicherung verglichen: ausschließlich `prompt` und `updated_at` geändert. Aktiv, täglich 07:00 lokal, bestehendes Modell und Projekt. Gespeicherter Prompt stimmt bis auf abschließenden Zeilenumbruch mit [versioniertem Prompt](../../../contextual-llm-wiki/automation/prompt.md) überein. Private-Konfiguration ist nicht ausgewählt. |
| Scheduled wiki maintenance before global retrieval maintenance | Reale Quelländerung führt über denselben Helper zu gepflegtem Wiki und durchsuchbarer Ausgabe | Änderung an `docs/rag/operating-model-rag-qmd.md` erkannt; echter Codex-Provider kompilierte diese Quelle, übersprang drei unveränderte Quellen und prüfte neun betroffene Seiten. Resultat: 22 aktive Seiten einschließlich gespeicherter Synthese, kein pending/review/Lint-Fehler. Anschließend alle drei globalen QMD-Schritte erfolgreich. [Lauf 02](../../../contextual-llm-wiki/.local/operations-runs/20260913-acceptance-02/report.json). |
| Observable serialized fail-closed runs | Unveränderte Wiederholung vermeidet Modellkompilierung, führt QMD-Pflege aus | [Lauf 03](../../../contextual-llm-wiki/.local/operations-runs/20260913-acceptance-03/report.json): `noop:true`, 22 Seiten, vier Quellen, gleicher `lastCompleted`-Wert. Alle Schritte Exit 0. |
| Observable serialized fail-closed runs | Fehler, unvollständige Antworten und konkurrierende Läufe stoppen Folgeschritte und behalten Evidence | Sechs öffentliche Prozess-Verhaltenstests: Happy/no-op, ungültiger Erfolgsvertrag einschließlich pending, malformed JSON, echter nicht-null Prozess-Exit mit stderr, Betriebssystemsperre und bestehende Artefakte. Rot→Grün zuerst für fehlenden Ablauf und anschließend für fälschlich akzeptierte Erfolgsmeldungen nachgewiesen. [Tests](../../../contextual-llm-wiki/test/test_maintenance_job.py). |
| Observable serialized fail-closed runs | Betrieb benötigt keine interaktive Shell-Konfiguration | [Reduzierter PATH](../../../contextual-llm-wiki/.local/operations-runs/20260913-minimal-path/report.json): macOS-System-Python, bekannte QMD-/Node-Pfade und vorhandenes App-Codex-CLI; kompletter realer Lauf Exit 0. Reconciliation: 25 konfigurierte Collections unverändert, keine fehlenden/konfliktbehafteten; QMD insgesamt 2.164 Dokumente und 10.588 Vektoren zum Prüfzeitpunkt. |
| Verified context adoption catalog | Tatsächliche Einstiegspfade, Prioritäten und Umsetzungsstatus; keine vermeintlich schon installierte flächendeckende Nutzung | [Katalog mit 39 verifizierten Dateien](../../../docs/rag/llm-wiki-context-adoption-catalog.md). QMD-Recherche, Originaltextprüfung, Git-Inventar und kanonische Symlink-Ziele dokumentiert. Betriebsverweise umgesetzt; übrige Einträge geplant. Repo-Begrenzung und Private-Scope explizit. |

## Inhaltlicher Nachweis

Die erzeugte Seite [Wiki-Qualitätsprüfung vor der QMD-Aktualisierung](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/wiki-qualitätsprüfung-vor-der-qmd-aktualisierung.md) wurde gelesen. Sie beschreibt jetzt ausdrücklich Collection-Abgleich → `wiki maintain` → `wiki status`/`wiki lint` → QMD update/embed/status, nennt tägliche lokale Pflege, Quellen-Schreibgrenzen und fehlenden Merge-Trigger und belegt dies mit der geänderten Originaldatei samt Hash. `wiki search --question Wiki` liefert genau diese neue Seite als ersten gültigen Treffer über QMD. [Lokales Suchergebnis](../../../contextual-llm-wiki/.local/operations-search.json).

Damit ist nicht nur ein gestarteter Prozess, sondern die inhaltliche Übernahme der Quelländerung in die abgeleitete und durchsuchbare Wissensschicht nachgewiesen.

## Prüfungen und verbleibende Grenzen

- `npm run check`: TypeScript, 28 bestehende öffentliche Integrationstests, 59 Upstream-Tests und sechs neue Betriebs-Verhaltenstests erfolgreich. [Lokales Prüfprotokoll](../../../contextual-llm-wiki/.local/operations-check.txt).
- `openspec validate operate-contextual-llm-wiki --strict`, `git diff --check` und QMD-Skill-Validierung erfolgreich.
- Helper und angrenzenden Ablauf auf Duplikation und Verantwortungsgrenzen geprüft: vorhandene Compiler-/QMD-Logik bleibt in ihren bestehenden Schnittstellen; der neue Helper besitzt nur Reihenfolge, Sperre, Ergebnisprüfung und Protokollierung. Keine zusätzliche Retrieval-Engine oder Schedulerinstallation.
- Live-Definition gesichert unter `~/.codex/automations/update-qmd-index-daily/automation.before-llm-wiki-20260913.toml`; versionierter neuer Prompt ermöglicht Wiederinstallation. Keine Git-Commits, Pushes oder Archivierung.
- Produktives `wiki status` zeigte bei der letzten Bestandsprüfung 1.667 ausgewählte Quellen, `lastCompleted:null` und alle als hinzugefügt. Die Zahl wächst durch neue Markdown-Dokumentation dieser Session. Ein erfolgreicher Vollimport und der nächste tatsächliche Schedulerlauf sind **noch nicht nachgewiesen**. Die begrenzte echte Ausführung und die gespeicherte aktive Definition sind die hier möglichen unmittelbaren Nachweise; der Vollimport erfolgt über den regulären Job.
- Ausführung bei schlafendem/abgemeldetem Mac oder nicht verfügbarer Codex-Anmeldung wurde nicht geprüft. Der Zeitplan ist keine Echtzeitgarantie. Private Wiki-Pflege und flächendeckendes Agent-Routing sind nicht aktiviert.
- Vorhandene fremde Änderungen am Agent-Framework-Piloten sowie das unversionierte Wiki-Vergleichsdokument wurden nicht übernommen oder verändert. Rohprotokolle bleiben lokal/ignoriert.


## Ticket 01: gemeinsame Quellen-/Abfragefunktion (13.09.2026)

Die [gesonderte Ticket-01-Abnahme](../../../contextual-llm-wiki/evidence/shared-wiki-01.md) belegt die gemeinsame CLI anhand realer Inventur, echter Compiler-/QMD-Ausführung, echter Provider-Synthese und öffentlicher Verhaltenstests. Die frühere Betriebsabnahme oben beschreibt weiterhin den alten Live-Stand. Bestandsmigration, Fehlerisolation, Aktivierung und Vollimport sind noch offen; der Change bleibt aktiv.


## Akzeptierter Abschluss von Ticket 01

Daniel hat Ticket 01 am 13.09.2026 ausdrücklich akzeptiert und Abschluss, Commit und Push beauftragt. Sein Wiki-Delta wurde in [share-contextual-wiki-sources](../archive/2026-09-13-share-contextual-wiki-sources/proposal.md) separat abgeschlossen und kanonisch übernommen. Die hier noch offenen Aufgaben 4.2, 4.4, 4.5 und der Produktionsanteil von 4.6 bleiben unverändert den Tickets 02–04 zugeordnet.


## Ergänzung Ticket 03

[Abnahme begrenzter Pflegefehler](../../../contextual-llm-wiki/evidence/bounded-failures-03.md): unabhängige Inhalte werden trotz tatsächlicher Provider-/Validierungsfehler aktualisiert; betroffene Konzepte und Antworten bleiben gesperrt. Die dortigen Nachweise ergänzen die historische Betriebsabnahme oben und belegen keine produktive Umstellung oder vollständige Embedding-Pflege.
