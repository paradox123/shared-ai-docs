# Gemeinsames LLM-Wiki auf Daniels Mac

Die bestehende Automation `update-qmd-index-daily` ist der einzige tägliche Pflegeauslöser, um 07:00 Uhr Europe/Berlin im bisherigen lokalen Projekt `codex-global`. Die gemeinsame Produktionskonfiguration ist `contextual-llm-wiki/.local/common.json`; sie umfasst alle acht Originalrepos sowie die rekursiven Zonen Meetings und Projects einschließlich Projects/Private. `private` bezeichnet einen Tätigkeitsbereich, keine Zugriffsgrenze. [ADR 0010](../docs/adr/0010-shared-wiki-across-personal-and-professional-domains.md).

Der aktuelle Aktivierungs-, Import- und Abnahmestand steht im [Ticket-06-Nachweis](evidence/resumable-maintenance-06.md); [Ticket 04](evidence/production-04.md) hält den früheren Stand fest. Ein gestarteter Lauf oder ein aktiver Zeitplan beweist keinen abgeschlossenen Vollimport. Ein manueller Produktionslauf und ein späterer automatischer Schedulerlauf werden dort getrennt ausgewiesen.

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
LLMWIKI_PROVIDER=codex-agent python3 scripts/run-maintenance.py \
  --config "$PWD/.local/common.json" \
  --artifacts "$WIKI_RUN_DIR" \
  --lock-file "$PWD/.local/operations-runs/maintenance.lock" \
  --qmd "$(command -v qmd)" \
  --reconcile "$PWD/../../danielsvault-rag/scripts/sync-qmd-collections.py"
```

Vorher müssen Runtime-Binaries, Provider-Anmeldung, QMD-Datenbank und deren Verzeichnis verfügbar und schreibbar sein. Fehlende Mac-Verfügbarkeit, Anmeldung, Berechtigungen oder Runtime werden als Blocker gemeldet. Der Tagesjob installiert nichts und repariert keine TCC-Einstellungen.

## Pflege, Teilfehler und Protokolle

Der Helper gleicht Quell-Collections ab. `wiki maintain` aktualisiert den Originalquellenindex vor modellabhängiger Wiki-Arbeit; danach folgen `status` und `lint`. Er aktualisiert anschließend QMD inklusive Embeddings über gültige Ergebnisse. Begrenzte Fehler sperren betroffene und transitiv abhängige Aussagen; nachweislich unabhängige Arbeit darf weiterlaufen. Gemeinsame Runtime-/Indexfehler oder unbestimmbare Abhängigkeiten blockieren die davon abhängigen Schritte. Unvollständige Scans sind kein Quellenentzug.

Der erste JSON-Datensatz nennt das neue Laufverzeichnis. Den gleichen Prozesshandle höchstens innerhalb der unten genannten Beobachtungsgrenze verfolgen; keinen zweiten Aufruf starten, um Ausgabe zurückzugewinnen. Jeder Schritt bewahrt stdout, stderr und Exitcode. `maintenance/report.json` enthält Gesamtergebnis, `contexts`, `failures`, `pending` beziehungsweise `remaining` sowie den Wiki-Laufbericht. Fehlende oder widersprüchliche Ergebnisse sind kein Erfolg.

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

### Endliche Helperläufe und Fortschritt

Der öffentliche Helper begrenzt jeden Aufruf mit `--budget-seconds 1200` und `--termination-grace-seconds 10` (Defaults; positive endliche Sekunden). Das Budget umfasst alle Schritte, nicht nur Modellantworten. Für isolierte Tests sind kürzere Werte zulässig. Das angekündigte Artefaktverzeichnis enthält sofort `progress.json`; dessen `detail` verweist während Wiki-Pflege auf `maintain-<context>.progress.json`. `modelResponses` zählt Antworten, `extractions.saved/reused` zählt dauerhaft verwendbare Extraktionen. Der letzte tatsächliche Fortschrittszeitpunkt bleibt bei einem gehaltenen Request stehen.

Budgetende oder ein gemeinsamer Providerfehler beendet eigene Arbeit begrenzt. `report.json` und die letzte stdout-JSON-Zeile melden `ok:false`, Exit 1, Restarbeit und einen getrennten Quellensuchindexstatus; dies ist kein vollständiger Pflegeerfolg. Ein frischer Helper mit einem neuen Artefaktverzeichnis verwendet kompatible Extraktionen weiter. Parallel gestartete Helper erhalten einen Lockkonflikt. Hintergründe und isolierte Messgrundlage: [Ticket-03-Nachweis](evidence/resumable-maintenance-03.md). Der [kanonische Automationsprompt](automation-prompt.md) legt denselben endlichen Ablauf fest.

Falls die Betriebssystemprüfung der eigenen Prozessidentität oder das gezielte Beenden scheitert, bleibt `<lock-file>.blocked.json` mit den nicht abschließend geklärten Besitzdaten zurück. Der Helper meldet Nicht-Erfolg; weitere Aufrufe stoppen vor neuer Mutation. Erst nach manueller Prüfung der dort genannten eigenen Prozesse darf diese konkrete Sperrdatei entfernt werden. Dies ist kein normaler Budgetabschluss.

Der Report trennt einen bereits abgeschlossenen inneren Wiki-Lauf (`wiki.ok`, wiki-bezogener `lastCompleted`) von einem unvollständigen äußeren Job. Bei späterem QMD-Budgetende bleiben die konkreten QMD-Schritte in `remaining`; nur der gesamte Helper mit Exit0 und `ok:true` ist erfolgreich. `completedAt` bedeutet lediglich Laufende. Schreibfehler an Fortschritts-/Reportartefakten liefern weiterhin strukturiertes Nicht-Erfolgs-JSON auf stdout mit `artifactErrors`; soweit möglich wird auch die verbleibend schreibbare Fortschrittsdatei auf Nicht-Erfolg aktualisiert.


## Einmaliger Start und endliche Beobachtung (Ticket 06)

`run-maintenance.py` startet den öffentlichen Helper genau einmal und bewahrt `helper.stdout`, `helper.stderr`, `helper.exitcode`, `process.json` und `observation.json` unter dem zuerst ausgegebenen Artefaktpfad. Die eigentlichen Helperdateien liegen darunter in `maintenance/`. Direkte manuelle Helperaufrufe bleiben unterstützt; die tägliche Automation verwendet den protokollierten Runner.

Produktionsgrenzen: 1200 Sekunden gesamter Helper, 10 Sekunden Beendigungsfrist, 30 Sekunden Beobachtungsmarge (1240 Sekunden), einmalige Diagnose nach 180 Sekunden ohne dauerhaften Fortschritt. Die äußere Notbeendigung beansprucht höchstens weitere 11 Sekunden und betrifft nur den selbst gestarteten, noch nicht abgeholten Helper; dessen bestehender Guardian behält die Kindprozesssicherung. Höchstens 22 Beobachtungen desselben Handles mit je maximal 60 Sekunden, kein Neustart des Zählers nach Kontextwechsel. Das bestehende Paketmaximum ist 20 neue Extraktionen, die produktive Parallelität bleibt 8. Diese Sicherheitsgrenzen versprechen keine Tageskapazität. Ein kontrollierter Aktivierungslauf darf ein ausdrücklich protokolliertes kürzeres Zeitbudget verwenden.

Fehlt danach der Abschlussbericht, folgt genau eine begrenzte Diagnose aus `process.json`, `diagnosis.json`, Fortschritt und höchstens 4000 Zeichen Fehlerausgabe. Der Runner liefert Nicht-Erfolg; der Agent hält Prozesszustand und unbekannte oder konkrete Restarbeit fest und beendet die Beobachtung. Lebende/ungeklärte Besitzer blockieren einen Folgestart. Niemals einen zweiten Collector zum Wiedergewinnen der Ausgabe starten, fremde Prozesse beenden oder Locks pauschal entfernen. Vollerfolg verlangt Runner- und Helperexit 0, `ok:true`, vollständige Kontexte und keine Restarbeit.

Die Memory trennt SourceIndex, Tagesnachpflege, überfällige Quellen, initialen Restbestand, Kapazitätsmodus, inneren Wikiabschluss und äußere QMD-Schritte. Erst ein tatsächlicher Schedulerlauf belegt den Scheduler; mehrtägiger Erstimport plus No-op bleiben eine eigene spätere Abnahme. [Ticket-06-Nachweis](evidence/resumable-maintenance-06.md) führt Messungen und Aktivierungsstatus.


Für eine explizite Installation oder Rückkehr hält `scripts/rollout-with-locks.py --config <common.json> --lock-file <gemeinsame-maintenance.lock> --artifacts <neuer-Pfad> -- <Operation>` beide vorhandenen Schreibsperren während der gesamten Operation. Der bestehende `withWriter` schützt auch direkte `wiki maintain/save/query --save`-Aufrufe; die vorherige Besitzerbeobachtung allein genügt nicht. Der Wrapper begrenzt die eine Installation auf300s plus10s Beendigungsfrist und verwendet die bestehende Prozesssicherung. Eine belegte Fremdsperre verhindert den Start der Operation. Dies ist ein manuelles Rolloutwerkzeug, kein Scheduler.
