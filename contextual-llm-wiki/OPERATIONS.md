# Gemeinsames LLM-Wiki auf Daniels Mac

Die bestehende Automation `update-qmd-index-daily` ist der einzige tägliche Pflegeauslöser, um 07:00 Uhr Europe/Berlin im bisherigen lokalen Projekt `codex-global`. Die gemeinsame Produktionskonfiguration ist `contextual-llm-wiki/.local/common.json`; sie umfasst alle acht Originalrepos sowie die rekursiven Zonen Meetings und Projects einschließlich Projects/Private. `private` bezeichnet einen Tätigkeitsbereich, keine Zugriffsgrenze. [ADR 0010](../docs/adr/0010-shared-wiki-across-personal-and-professional-domains.md).

Der aktuelle Aktivierungs-, Import- und Abnahmestand steht in [Ticket-04-Evidence](evidence/production-04.md). Ein gestarteter Lauf oder ein aktiver Zeitplan beweist keinen abgeschlossenen Vollimport. Ein manueller Produktionslauf und ein späterer automatischer Schedulerlauf werden dort getrennt ausgewiesen.

## Runtime und Aufruf

Die eingerichtete Wiki-Runtime verwendet Node 24.16.0 und den gepinnten Atomicstrata-Compiler. QMD verwendet seine vorhandene Node-22-Installation. Im reduzierten Scheduler-PATH liegt Node nicht automatisch auf PATH, auch nach Homebrew shellenv; deshalb wird die vorhandene Installation ausdrücklich ergänzt. Der Codex-Provider verwendet die bestehende Anmeldung. Die gemeinsame Konfiguration begrenzt den Compiler mit `concurrency: 8` auf acht gleichzeitige Modellanfragen.

Aus dem Wiki-Verzeichnis:

```bash
export PATH="/opt/homebrew/opt/node@22/bin:/opt/homebrew/bin:/Applications/ChatGPT.app/Contents/Resources:$PATH"
command -v node
command -v qmd
command -v codex
./wiki preflight
WIKI_RUN_DIR="$PWD/.local/operations-runs/$(date '+%Y%m%dT%H%M%S')-$$"
LLMWIKI_PROVIDER=codex-agent python3 scripts/maintain-index.py \
  --config "$PWD/.local/common.json" \
  --artifacts "$WIKI_RUN_DIR" \
  --lock-file "$PWD/.local/operations-runs/maintenance.lock" \
  --qmd "$(command -v qmd)" \
  --reconcile "$PWD/../../danielsvault-rag/scripts/sync-qmd-collections.py"
```

Vorher müssen Runtime-Binaries, Provider-Anmeldung, QMD-Datenbank und deren Verzeichnis verfügbar und schreibbar sein. Fehlende Mac-Verfügbarkeit, Anmeldung, Berechtigungen oder Runtime werden als Blocker gemeldet. Der Tagesjob installiert nichts und repariert keine TCC-Einstellungen.

## Pflege, Teilfehler und Protokolle

Der Helper gleicht Quell-Collections ab, prüft die Runtime und führt `wiki maintain`, `status` und `lint` aus. Er aktualisiert anschließend QMD inklusive Embeddings über gültige Ergebnisse. Begrenzte Fehler sperren betroffene und transitiv abhängige Aussagen; nachweislich unabhängige Arbeit darf weiterlaufen. Gemeinsame Runtime-/Indexfehler oder unbestimmbare Abhängigkeiten blockieren die davon abhängigen Schritte. Unvollständige Scans sind kein Quellenentzug.

Der erste JSON-Datensatz nennt das neue Laufverzeichnis. Den gleichen Prozesshandle bis zum Abschluss verfolgen; keinen zweiten Aufruf starten, um Ausgabe zurückzugewinnen. Jeder Schritt bewahrt stdout, stderr und Exitcode. `report.json` enthält Gesamtergebnis, `contexts`, `failures`, `pending` beziehungsweise `remaining` sowie den Wiki-Laufbericht. Fehlende oder widersprüchliche Ergebnisse sind kein Erfolg.

Vollständiger Erfolg verlangt Exit 0, `ok:true`, keine offene Arbeit und einen abgeschlossenen Pflegezeitpunkt. Teilfehler behalten einen erfolglosen Gesamtexit auch bei erfolgreichem QMD. Die Automation-Memory nennt das genaue Artefaktverzeichnis, abgeschlossene und offene Arbeit, Quellen-/Seitenzahlen, No-op und `lastCompleted`. Dieser Zeitpunkt wird durch Teilfehler nicht vorgezogen. Nach Behebung erfolgt ein neuer Lauf mit neuem Artefaktverzeichnis. Alle manuellen und automatischen Aufrufe teilen dieselbe Sperrdatei; zusätzlich schützt die Wiki-Schreibsperre den gemeinsamen Bestand.

Originalrepos und ihre Quellkonfiguration bleiben für den Tagesjob unverändert. Er schreibt nur generiertes Wiki samt Zustand, QMD-Daten, lokale ignorierte Laufartefakte und seine Memory. Keine weiteren Jobs, Watcher oder Fachautomationsänderungen. Query und Merge starten keine Pflege. Ein unveränderter erfolgreicher Folgelauf ist No-op ohne Modellkompilierung.

## Agenten und menschlicher Einstieg

Kontextfragen beginnen mit WikiQuery:

```bash
./wiki query --config .local/common.json --question 'Welche Rolle hat QMD im gemeinsamen Wiki?'
```

`originals` enthält geprüfte Originalpfade, navigierbare Obsidian-URIs, Hashes und Aktualitätsstatus. `review` meldet veraltete Seiten; `fallback:true` kennzeichnet aktuelle Primärquellen im selben Zugang. Explizite Grenzen werden mit `--repo` oder `--source` durchgesetzt, auch transitiv. Ohne Speicherauftrag kein `--save`. Bei Ausfall den Blocker melden; keine parallele direkte QMD-Kontextsuche starten. Der [Recherche-Skill](../skills-repo/skills/rag-documentation-research/SKILL.md) ist der zentrale Agentenablauf.

Menschlicher Einstieg: `_shared/contextual-llm-wiki/common/wiki/index.md` im DanielsVault. Wiki-Seiten sind abgeleitete Evidenz; ihre Originalverweise öffnen unveränderte Fachdateien. Direkte Anzeige in Obsidian oder ein QMD-Treffer allein garantiert keine Aktualität. Der [Einführungskatalog](../docs/rag/llm-wiki-context-adoption-catalog.md) bleibt der Plan für weitere Repo-Einstiege.

## Übernahme und Wiederherstellung

Vor der Umstellung wurden die alte Automationdefinition und alle tatsächlich befüllten Altbestände gesichert. [Ticket 02](evidence/shared-wiki-02.md) dokumentiert die geprüfte Migrationsfunktion. Der produktive Übernahmebericht und Snapshot liegen im Ticket-04-Nachweis. Alte gespeicherte Antworten mit inzwischen geänderten oder entfallenen Belegen bleiben im Snapshot erhalten und werden sichtbar zurückgestellt.

Frühere aktive Einstiege und Wiki-Collections dürfen erst nach überprüfter Übernahme kontrolliert abgelöst werden. Fremde QMD-Collections bleiben unangetastet. Abnahmebestände ersetzen keine Produktionsquelle. Die vollständige Konfiguration lässt sich mit `wiki init-config` gemäß [README](README.md) erzeugen; vorhandene Konfigurationen nicht blind überschreiben.
