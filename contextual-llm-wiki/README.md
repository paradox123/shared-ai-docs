# Kontextabhängiges LLM-Wiki

Diese lokale CLI verbindet bestehende Markdown-Fachrepos mit Atomicstratas Compiler am Commit `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb`. Sie erzeugt eine gemeinsame Markdown-Wissensschicht, verfolgt Quellen- und Antwortabhängigkeiten und verwendet ausschließlich QMD für persistiertes Retrieval.

Originalrepos werden gelesen, einschließlich nicht committeter Markdown-Änderungen. Pflege erfolgt ausdrücklich. Es werden keine Automationen, Watcher, Git-Repos für das Wiki oder Cloud-Dienste angelegt.

## Einrichtung

Voraussetzungen: npm/Git, das vorhandene QMD mit funktionierender eigener Runtime und ein angemeldeter Codex-/Claude-Zugang oder ein OpenAI-kompatibler Provider. Node 24.16.0 und der Compiler werden lokal installiert:

```bash
cd contextual-llm-wiki
./scripts/bootstrap.sh
export LLMWIKI_PROVIDER=codex-agent
./wiki preflight
./wiki setup
```

`preflight` prüft Runtime, Compiler-Pin und vorhandene Providerkonfiguration ohne Inhaltsänderungen. `setup` führt zusätzlich eine tatsächliche Completion-Anfrage aus. `LLMWIKI_MODEL` ist optional; Zugangsdaten bleiben in der vorhandenen Providerkonfiguration beziehungsweise Umgebung. Alternativen: `claude-agent` oder `openai` mit `OPENAI_API_KEY` und gegebenenfalls `OPENAI_BASE_URL`. Der bei der Abnahme getestete Provider steht in [Evidence](evidence/acceptance.md). Die Compiler-Ausgabe ist standardmäßig deutsch.

```bash
export DANIELSVAULT_ROOT=/Users/dh/Documents/DanielsVault
mkdir -p .local
./wiki init-config --vault "$DANIELSVAULT_ROOT" \
  --output "$DANIELSVAULT_ROOT/_shared/contextual-llm-wiki/general" > .local/general.json
./wiki init-config --vault "$DANIELSVAULT_ROOT" --private \
  --output "$DANIELSVAULT_ROOT/_shared/contextual-llm-wiki/private" > .local/private.json
./wiki inventory --config .local/general.json
```

Die Startkonfiguration registriert die acht verbindlichen Repo-IDs aus [input-repositories.md](../.scratch/contextual-llm-wiki/input-repositories.md). Meetings und Projects werden rekursiv aufgenommen; `Projects/Private` und das private Repo gehören ausschließlich zum ausdrücklich gewählten privaten Kontext. Allgemeiner und privater Output haben getrennte Verzeichnisse und QMD-Collections. Die Inventur liest keine Privattexte für den allgemeinen Bericht. Die Quelle ist jeweils der konfigurierte Originalcheckout; zusätzliche Worktrees und verschachtelte Git-Repos werden nicht verfolgt.

`include` und `exclude` sind rekursive Markdown-Globs, unabhängig von der Groß-/Kleinschreibung. `privateInclude` ordnet private Teilzonen derselben Repo-Identität zu. Neue Repos werden durch explizite Konfiguration ergänzt. Die technischen Ausschlüsse und tatsächlich ausgelassenen Verzeichnisse stehen im Inventurbericht. Versteckte Agent-Dokumentation und Vendor-Markdown sind grundsätzlich enthalten; Symlink-Aliase werden ausgelassen. Der Ausgabepfad ist unabhängig von seiner Position stets vom Eingang ausgeschlossen. Er muss außerhalb getrackter Fachquellen liegen und in einem Git-Arbeitsbaum bereits ignoriert sein; der vorhandene Vault ignoriert `_shared/`.

## Pflege und Abfrage

```bash
./wiki maintain --config .local/general.json
./wiki status --config .local/general.json
./wiki lint --config .local/general.json
./wiki search --config .local/general.json --question 'QMD'
./wiki query --config .local/general.json --question 'Welche Rolle hat QMD?'
./wiki query --config .local/general.json --question 'Welche Rolle hat QMD?' --save qmd-rolle
```

`maintain` inventarisiert vollständig, meldet direkte und indirekte Prüfgründe, zieht ungültige Seiten zurück, kompiliert mit dem echten SDK ohne Embeddings, prüft gespeicherte Antworten und aktualisiert nur die eigene QMD-Collection. Ein unveränderter erfolgreicher Lauf benötigt keine neue Modellarbeit. Status und Fehler sind JSON; ein Fehler oder offener erforderlicher Arbeitsschritt liefert einen Exitcode ungleich null.

`query` verwendet QMD-Treffer nur mit gültigen Seiten- und Originalquellenständen. Bei fehlender aktueller Wiki-Evidenz liest es passende aktuelle Fachquellen als vorübergehenden Fallback. Ohne `--save` entsteht keine dauerhafte Antwortseite. Die Antwort enthält die tatsächlich übergebene Evidenzmenge einschließlich IDs, Versionen und transitiver Quellenstände. Diese Menge ist bewusst konservativ: Alle übergebenen Belege zählen als Abhängigkeit. Private Abfragen verwenden ausdrücklich `.local/private.json`.

Ein vorhandener Agent kann einen eigenen Entwurf speichern. Der Entwurf benennt die von der verwalteten Query gelieferten Evidenz-IDs und Hashes:

```json
{
  "slug": "meine-synthese",
  "question": "Was folgt daraus?",
  "answer": "Belegter Antworttext ...",
  "evidence": [{"id": "concepts/beispiel", "hash": "SHA-256-aus-query"}]
}
```

```bash
./wiki save --config .local/general.json --draft .local/entwurf.json
./wiki source --config .local/general.json --id 'shared-ai-docs/docs/rag/operating-model-rag-qmd.md'
```

Save weist fehlende oder geänderte Evidenz sowie direkte und indirekte Abhängigkeitszyklen zurück. Abhängigkeiten zu gespeicherten Antworten werden ebenso verfolgt wie Konzeptseiten. `source` zeigt den tatsächlich verarbeiteten Text mit Originalpfad, Hash und Zeilenoffset null. Die Fachquelle bleibt maßgeblich; eine Synthese ersetzt keine ADR oder Fachregel.

## Kontextänderung und Fehler

Eine Repo-Abwahl in der Konfiguration oder ein bestätigt fehlender Originalclone zieht abhängige aktive Seiten und Antworten zurück. Gemischte Konzepte werden aus verbliebenen Quellen neu erzeugt. Unabhängiges Wissen bleibt erhalten. Ein später wieder vorhandenes ausgewähltes Repo wird aus seinem aktuellen Inhalt neu verarbeitet; zuvor entzogene Antworten werden nicht automatisch wiederbelebt.

Ein Scanfehler ist kein Entzug. Provider-, Versions- und Indexfehler lassen erforderliche Restarbeit sichtbar. Nach Behebung denselben `maintain`-Aufruf wiederholen. Die Quellen werden dabei erneut gelesen. Ein abgebrochener Schreibprozess hinterlässt eine PID-Sperre; ein nachweislich beendeter Eigentümer wird beim nächsten Aufruf erkannt. Eine unlesbare Sperre muss nach Prüfung ihres Eigentümers manuell behoben werden. Keine pauschale Prozessbeendigung verwenden.

Der Wiki-Einstieg zeigt den letzten abgeschlossenen Pflegezeitpunkt. Ohne Pflegeaufruf wird keine Echtzeitaktualität in Obsidian versprochen; die verwaltete Query prüft Originalstände vor Benutzung. Ein Indexfehler bedeutet unvollständige Pflege. Unverwaltete direkte QMD-Abfragen können bis zur erfolgreichen Indexwiederholung den vorherigen Indexstand enthalten.

## Ablage und QMD

- `<output>/wiki/`: aktive Seiten und Obsidian-Einstieg `index.md`.
- `<output>/.state/compiler/`: unterstützter Quellenpfad, Compilerzustand und dessen Markdown-Inhaltsübersicht.
- `<output>/.state/state.json`: Seitenregister, Versionen, Abhängigkeiten und Restarbeit.
- `<output>/.state/staging/`: vor Veröffentlichung vorbereitete Ergebnisse.
- `<output>/.state/qmd-collections.json`: ausschließlich Wiki-eigene Collection-Zuordnung.

Die bestehende zuständige Reconciliation verarbeitet dieses Teilmanifest über `QMD_COLLECTION_MANIFEST`. Fremde Collections werden nicht umgehängt oder entfernt. Der QMD-SDK aktualisiert ausschließlich die gewählte Wiki-Collection. Private Wiki-Collections werden aus unbeschränkten Standardabfragen ausgeschlossen. Die Integration verwendet den vorhandenen QMD-Index; sie erzeugt keinen Compiler-Vektorstore. QMD-Embeddings können durch die vorhandene QMD-Wartung ergänzt werden. Lexikalisches QMD-Retrieval funktioniert bereits ohne neue Embeddings.

Falls die lokale Runtime anders installiert ist, erlaubt das optionale `qmd`-Objekt `module` (installiertes `dist/index.js`), `node`, `dbPath`, `reconcileScript` und `python`. `isolated:true` ist für reproduzierbare Tests mit einer ausdrücklich separaten QMD-Testdatenbank vorgesehen.

## Sicherung und Wiederherstellung

```bash
./wiki backup --config .local/general.json --destination /lokale/sicherung/wiki-2026-09-12
./wiki restore --config .local/general.json --backup /lokale/sicherung/wiki-2026-09-12
```

Das neue Sicherungsverzeichnis muss außerhalb der Fachrepos und aktiven Ausgabe liegen. Die Sicherung enthält Originalkopien, generierte Texte, Compilerzustand und Antwortabhängigkeiten. Sie ist entsprechend dem Kontext privat zu behandeln und nicht einzuchecken. Restore prüft zuerst Runtime und Provider, anschließend Hashes und den aktuellen Kontext, bevor gesicherte Seiten aktiv werden. Bei einem kleineren Kontext wird entzogene Antwort-Evidenz nicht veröffentlicht; gemischte Konzepte werden neu erzeugt. Ein Rohquellen-Neubau kann einzigartige Gesprächsformulierungen nicht identisch reproduzieren.

## Verifikation

```bash
npm run check
```

Die Tests benutzen die öffentliche CLI, den echten gepinnten Compiler und echte isolierte QMD-Datenbanken. Nur die Modellprovidergrenze wird deterministisch kontrolliert. [Abnahme](evidence/acceptance.md), [initiale Inventur](evidence/initial-inventory.json), [Integrationsentscheidungen](evidence/implementation-notes.md) und [Upstream-Patch](patches/0001-host-completion-without-embeddings.patch) dokumentieren Nachweise und Grenzen.
