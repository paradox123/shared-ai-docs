# Operating Model: WikiQuery mit QMD als einziger Engine

Wissenskontextsuche beginnt mit der verwalteten WikiQuery des gemeinsamen DanielsVault-Wikis. Sie prüft relevante Originalstände, liefert belegte Erkenntnisse und navigierbare Primärquellenverweise. QMD bleibt intern die einzige persistierte Index-, Embedding- und Retrieval-Engine; `rag` ist eine Kompatibilitätshülle für ausdrücklich bestehende Aufrufer. Es gibt keinen zweiten `.rag/store`.

## Verantwortlichkeiten

| Bereich | Zuständig |
|---|---|
| Standardzugang für Agenten-Kontextfragen | WikiQuery: `wiki query --config .local/common.json` |
| Originalquellenprüfung und explizite Aufgabengrenzen | WikiQuery mit `--repo` / `--source` |
| Wissenspflege und Antwortabhängigkeiten | `wiki maintain` |
| Quell-Collections und Pfade | Bestehendes `danielsvault-rag/qmd-collections.json` |
| Gemeinsame Wiki-Collection | Wiki-eigenes Teilmanifest, `contextual-wiki-common` |
| Index, Embeddings und Diagnose | QMD |
| Historische JSON-/Workflow-Verträge | QMD-backed `rag` CLI |

## Kontextrecherche

Dem [zentralen Recherche-Skill](../../skills-repo/skills/rag-documentation-research/SKILL.md) folgen. `originals` liefert aktuelle Originalpfade und URIs. Relevante Abschnitte direkt lesen; OpenSpec, ADRs und Repo-Anweisungen behalten ihre Autorität. `review` macht veraltete Evidenz sichtbar. WikiQuery verwendet bei Lücken geeignete aktuelle Quellen im selben Zugang. Ist WikiQuery nicht verfügbar, wird das gemeldet; direkte QMD-Kontextsuche ist kein stiller Ersatz.

`private` und `Projects/Private` sind persönliche Fachbereiche des gemeinsamen Wissensbestands. Fachliche Relevanz und ausdrücklich gesetzte Aufgabengrenzen entscheiden über Evidenz, nicht der Verzeichnisname. Alte Scope-Labels der Kompatibilitätshülle definieren keine Zugriffspolitik für WikiQuery. Eine gewöhnliche Query löst keine Pflege und keine dauerhafte Speicherung aus.

## Indexbetrieb

Das Manifest unter `_shared/danielsvault-rag/qmd-collections.json` beschreibt Quellindexabdeckung. Sein Reconciler fügt fehlende Collections hinzu und meldet abweichende Pfade oder Muster als Konflikt; fremde Collections werden nicht automatisch umgebogen. Repo- und Zusatz-Collections halten auch relevante versteckte Markdown-Bereiche erreichbar. Die gemeinsame Wiki-Collection wird separat von der Wiki-CLI verwaltet.

Die bestehende tägliche Automation pflegt den vollständigen gemeinsamen Eingang vor der anschließenden QMD-Pflege. Begrenzte Fehler erlauben nur nachweislich unabhängige Arbeit; Gesamtergebnis und Memory bleiben bei Teilfehlern erfolglos. Quellen werden nicht editiert. Zeitplan, Modell, Projekt und Benachrichtigungseinstellungen bleiben erhalten. Ablauf, Runtime, Sperren, genaue Artefakte und Abnahmestand stehen in [OPERATIONS.md](../../contextual-llm-wiki/OPERATIONS.md).

Direktes `qmd status`, Collection-Inspektion, `update` und `embed` sind Betriebs- und Diagnosewerkzeuge. Sie ersetzen keine queryzeitige Quellenprüfung. Bei Runtime-, Datenbank- oder Berechtigungsfehlern den konkreten Blocker protokollieren; keine automatisierte Installations- oder TCC-Reparatur.
