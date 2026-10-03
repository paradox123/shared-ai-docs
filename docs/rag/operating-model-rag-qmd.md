# Operating Model: QMD als DanielsVault-Retrieval

DanielsVault-Dokumentationsrecherche beginnt mit dem bestehenden QMD-Index und passenden Originalquellen-Collections. Relevante Treffer werden anhand gegenwärtiger Originaldateien geprüft. Kuratierte Wiki-Seiten können als zusätzliche Wissenshinweise einbezogen werden; ihre Quellenstände sind vor Nutzung zu prüfen. `rag` bleibt eine Kompatibilitätshülle für ausdrücklich bestehende Aufrufer. Es gibt keinen zweiten `.rag/store`.

## Verantwortlichkeiten

| Bereich | Zuständig |
|---|---|
| Agenten-Kontextfragen | QMD: `qmd search` / `qmd query` mit aufgabenbezogener Collectionauswahl |
| Autorität und explizite Aufgabengrenzen | Originaldateien und Repository-Anweisungen |
| Ausdrücklich beauftragte Wiki-Pflege | [maintain-llm-wiki](../../skills-repo/skills/maintain-llm-wiki/SKILL.md), direkte Markdown-Bearbeitung |
| Quellenstand kuratierter Wiki-Seiten | Deterministischer `wiki_sources.py check`; fachliches Review durch den Agenten |
| Originalcollections und Pfade | Bestehendes `danielsvault-rag/qmd-collections.json` |
| Optionale kuratierte Wiki-Collection | `contextual-wiki-common` am aktiven `common/wiki`-Pfad |
| Index, Embeddings und Diagnose | QMD und bestehender QMD-only-Tagesjob |
| Historische JSON-/Workflow-Verträge | QMD-backed `rag` CLI |

## Kontextrecherche

Dem [Recherche-Skill](../../skills-repo/skills/rag-documentation-research/SKILL.md) folgen. Bei jeder Suche passende Originalcollections mit wiederholtem `-c` wählen; bei Nutzen die kuratierte `contextual-wiki-common` ergänzen. Bereits benannte Originale dürfen direkt geöffnet werden. Vor Nutzung einer Wiki-Seite ihre direkten Originalstände prüfen und relevante Originalpassagen lesen. `review` oder `invalid` bedeutet, mit aktuellen Originalen weiterzurecherchieren und die Grenze der Wiki-Seite zu nennen. Gleiche Hashes zertifizieren weder Aussagen noch Schlussfolgerungen. OpenSpec, ADRs und Repo-Anweisungen behalten ihre Autorität.

`private` und `Projects/Private` sind persönliche Fachbereiche des gemeinsamen Wissensbestands. Fachliche Relevanz und ausdrücklich gesetzte Aufgabengrenzen entscheiden über Evidenz. Eine normale Suche führt keine Indexpflege aus, schreibt keine Wiki-Seite und setzt kein Prüfdatum. Bei fehlenden Treffern gezielt in bekannten Quellen oder mit begrenzter Textsuche weiterarbeiten und Evidenzlücken benennen.

## Wiki-Pflege und Indexbetrieb

[ADR 0018](../adr/0018-agent-managed-markdown-wiki.md) ersetzt seit 02.10.2026 Compiler und WikiQuery durch ausgewählte direkte Seitenpflege. Wissensseiten unter `notes/` nennen die tatsächlich tragenden Originale; `index.md` und `log.md` halten Navigation und Ergebnisse fest. Erfolgreiche Pflege bezieht sich auf den gewählten Umfang. Es gibt keine globale Importpflicht, keinen transitiven Antwortgraph und keine tägliche Wiki-Frist. [Wiki-Betriebsanleitung](llm-wiki.md) enthält Beispiele.

Das Originalmanifest beschreibt Indexabdeckung. Reconciliation fügt fehlende Collections hinzu und meldet abweichende Pfade oder Muster als Konflikt; fremde Collections werden nicht umgebogen. Die gemeinsame Wiki-Collection bleibt als zusätzliche Sammlung kuratierter Seiten bestehen. Historische Compiler-Spiegel, Backups und Abnahmeausgaben sind keine aktiven Wissenscollections.

Der unveränderte tägliche QMD-Job aktualisiert Suchdaten und Embeddings unabhängig von Wiki-Pflege. Indexierte Bytes sind kein Inhaltsreview. `qmd status`, Collection-Inspektion, `update` und `embed` sind Betriebswerkzeuge. Bei Runtime-, Datenbank- oder Berechtigungsfehlern den konkreten Befund protokollieren; keine automatisierte Installations- oder TCC-Reparatur.
