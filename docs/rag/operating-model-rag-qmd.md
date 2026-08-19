# Operating Model: QMD as the Single Engine

## Entscheid in einem Satz

QMD ist fuer DanielsVault die einzige persistierte Index-, Embedding- und Retrieval-Engine; `rag` bleibt nur als kompatible CLI- und Workflow-Huelle fuer bestehende Aufrufer erhalten.

## Verantwortlichkeiten

| Bereich | Verantwortlich |
|---|---|
| Collections und Pfade | `qmd-collections.json` |
| Lexikalischer Index | `qmd update` |
| Embeddings | `qmd embed` |
| Ranked Retrieval | `qmd search` und `qmd query` |
| Bestehende JSON-/Workflow-Contracts | QMD-backed `rag` CLI |
| Exakte Fallback-Suche | gezieltes `rg` |

Es gibt keinen zweiten `.rag/store`. Strukturierte `rag`-Abfragen lassen QMD zuerst relevante Quelldokumente bestimmen und extrahieren Fakten danach transient aus diesen Dateien.

## Collection-Konfiguration

Die eingecheckte Manifestdatei liegt unter:

```text
/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/qmd-collections.json
```

Abgleich und kontrolliertes Hinzufuegen fehlender Collections:

```bash
cd /Users/dh/Documents/DanielsVault/_shared/danielsvault-rag
python3 scripts/sync-qmd-collections.py
python3 scripts/sync-qmd-collections.py --apply
```

Der Helper veraendert keine bestehende Collection mit abweichendem Pfad oder Pattern. Ein Konflikt blockiert die Wartung und muss bewusst geloest werden. Die private Collection ist nur ueber expliziten Private-Scope erreichbar und gehoert nicht zum generischen `all`-Scope.

Jedes echte verschachtelte Git-Repository wird von seinem Repository-Root mit `**/*.md` indexiert. Dadurch sind README-, OpenSpec-, Skill-, Docs- und ADR-Markdown gemeinsam abgedeckt. Fuer von QMD standardmaessig uebersprungene versteckte Verzeichnisse und `vendor`-Verzeichnisse gibt es bei vorhandenem getracktem Markdown explizite Zusatz-Collections. Der Vault-Root selbst verwendet eine nicht-rekursive Top-Level-Collection plus explizite Collections fuer seine eigenen Inhaltszonen, damit verschachtelte Repositories nicht doppelt indexiert werden und `private` nicht in den generischen `all`-Scope gelangt.

## Standard-Retrieval

Agenten verwenden QMD direkt:

```bash
qmd status
qmd search "STS_BASE_URL" -c ncg-docs -n 10 --files
qmd query "Welche ADR beschreibt den agent-based development workflow?" -c ki-fuer-kmu-docs -n 5
```

Bestehende Prompts duerfen die kompatiblen Workflows weiterhin verwenden:

```bash
cd /Users/dh/Documents/DanielsVault/_shared/danielsvault-rag
export PATH="$PWD/.venv/bin:$PATH"
rag runtime health
rag retrieve semantic --scope ncg/ncg-docs --query "Migration Hetzner Dev" --top-k 5 --format json
rag retrieve structured --scope ncg/ncg-docs --record-type ci_setting_fact --filter "setting_name~BASE_URL" --top-k 5 --format json
rag workflow research-for-review --scope ncg/ncg-docs --query "deployment documentation" --top-k 5 --format json
```

Diese Befehle schreiben keinen eigenen Index und melden `qmd` als Engine.

## Taegliche Wartung

Die aktive Codex-Automation `Update QMD Index Daily` fuehrt in dieser Reihenfolge aus:

1. Collection-Manifest mit `scripts/sync-qmd-collections.py --apply` abgleichen.
2. Bei konfliktfreiem Abgleich `qmd update` ausfuehren.
3. Nur nach erfolgreichem Update `qmd embed` ausfuehren.
4. `qmd status` erfassen und Collection-, Dokument- und Vektoranzahl in der Automation-Memory dokumentieren.

Bei fehlendem Runtime-Binary, Collection-Konflikten oder Berechtigungsfehlern wird fail-closed abgebrochen. Projekt-Repositories werden von der Wartungsautomation nicht editiert.

## Troubleshooting

1. `qmd: command not found`: QMD installieren bzw. den QMD-Skill-Preflight ausfuehren.
2. Collection fehlt: Manifest-Check ausfuehren und danach kontrolliert `--apply` verwenden.
3. Collection-Konflikt: Pfad und Pattern bewusst korrigieren; der Helper repointet nicht automatisch.
4. Ergebnisse wirken veraltet: `qmd update`, danach `qmd embed` und `qmd status` ausfuehren.
5. Kompatibilitaets-CLI fehlt: virtuelle Umgebung aktivieren; direktes QMD-Retrieval bleibt davon unberuehrt.
