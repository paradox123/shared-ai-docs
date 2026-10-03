# RAG Docs Index

## Uebersicht

Diese Seite sammelt die Dokumentation fuer das lokale RAG-Projekt auf Basis von DanielsVault und den angrenzenden Dokumentations-Repositories.

## Seiten

- [DanielsVault Local RAG](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/danielsvault-local-rag.md)
  Zielbild, Nutzen, Domain-Grenzen und empfohlener Zuschnitt fuer ein lokales RAG-System fuer DanielsVault.
- [Evaluation Set v0](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.md)
  Erstes Eval-Set mit echten historischen Fragen aus Codex-, Claude- und Copilot-Sessions plus sinnvollen Folgefragen fuer kommende RAG-Slices.
- [Runtime Closeout 2026-04-23](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/2026-04-23-rag-runtime-closeout.md)
  Formales Closeout mit gruener 01-05-Verifikation, Runtime-Health/Smoke und archivierten OpenSpec-Changes.
- [Operating Model: QMD Retrieval](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/operating-model-rag-qmd.md)
  QMD ist der Standardzugang für Suche und Retrieval; Ergebnisse werden an Originaldateien geprüft. Kuratierte Wiki-Seiten sind optionale Hinweise mit Quellenprüfung; ausdrückliche Pflege nutzt `maintain-llm-wiki`.
- [Delivery Evidence 2026-04-26](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/2026-04-26-rag-qmd-operating-model-delivery-evidence.md)
  Command-by-command Nachweis des Direct-Mode-Changes inkl. `qmd`-Checks und Watcher-State.

## Empfohlene Lesereihenfolge

1. Zielbild und Nutzen lesen
2. Parent-Spec in `_specs/` lesen
3. Evaluation Set v0 lesen und als Gold-Set fuer Slice C vorbereiten
4. Operating Model lesen (QMD als Standardzugang)
5. Delivery Evidence 2026-04-26 lesen
6. Runtime Closeout lesen und Evidence/Archivpfade nachvollziehen

## Direkte Wiki-Pflege

- [Wiki-Betrieb und direkte Seitenpflege](llm-wiki.md)
- [Katalog für Skills und Repo-Kontextdateien](llm-wiki-context-adoption-catalog.md)

- [ADR 0018: Agentische Markdown-Pflege](../adr/0018-agent-managed-markdown-wiki.md)
