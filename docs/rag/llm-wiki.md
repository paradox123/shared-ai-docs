# LLM-Wiki direkt pflegen

Stand: 02.10.2026. Maßgeblich sind [ADR 0018](../adr/0018-agent-managed-markdown-wiki.md), die [Wiki-Spezifikation](../../openspec/specs/contextual-llm-wiki/spec.md) und [Betriebsspezifikation](../../openspec/specs/contextual-wiki-operations/spec.md) und [maintain-llm-wiki](../../skills-repo/skills/maintain-llm-wiki/SKILL.md).

## Einen Pflegeauftrag ausführen

1. Thema, Originalquellen oder Seiten aus dem ausdrücklichen Auftrag bestimmen und Repository-Startup lesen. Mit einem Fachbereich beginnen; passende weitere Repos nur für den gewählten Inhalt einbeziehen.
2. Gegenwärtige Originale direkt lesen. Eine bestehende Wiki-Seite kann Recherchehinweise liefern; ihre tatsächlich tragenden Originale müssen für die neue Seite selbst geprüft werden.
3. Ausgewählte Seiten unter `notes/` schreiben oder korrigieren. Originalbelege verlinken, eigene Schlussfolgerungen kennzeichnen, Widersprüche und Grenzen beschreiben. Die Fachquellen bleiben unverändert.
4. Aussagen und Links prüfen, dann direkte Quellenstände über `record` festhalten. `index.md` und `log.md` an den tatsächlich bearbeiteten Umfang anpassen.
5. Mit `check` den festgehaltenen Quellenstand prüfen. Abschluss pro ausgewählter Seite und verbleibende Lücken berichten; andere Vault-Inhalte haben keinen impliziten Pflegeauftrag.

Der aktive Bestand liegt unter `/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/common/wiki` und besitzt kein eigenes Git-Repository. Gleichzeitige Agenten koordinieren ihre Seiteneigentümerschaft vor Änderungen.

## Quellenstand prüfen und festhalten

Aus dem `shared-ai-docs`-Gitroot:

```bash
python3 skills-repo/skills/maintain-llm-wiki/scripts/wiki_sources.py check \
  --vault /Users/dh/Documents/DanielsVault \
  --wiki /Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/common/wiki
```

Ohne `--page` prüft der Helper Wissensseiten in `notes/`; `index.md` und `log.md` zählen nicht dazu. Wiederholbares `--page notes/name.md` begrenzt die Prüfung. Er meldet je Seite `unchanged`, `review` oder `invalid` und liefert Exit 1 bei geändertem oder fehlendem Original sowie bei ungültigen Metadaten oder Pfaden. Der Check ist rein lesend und löst keine Wiki-/Indexpflege aus. `unchanged` bedeutet ausschließlich gleiche Originalbytes.

Erst nachdem der Agent den Seiteninhalt gegen alle angegebenen gegenwärtigen Originale geprüft hat:

```bash
python3 skills-repo/skills/maintain-llm-wiki/scripts/wiki_sources.py record \
  --vault /Users/dh/Documents/DanielsVault \
  --wiki /Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/common/wiki \
  --page notes/name.md \
  --source _shared/shared-ai-docs/docs/rag/operating-model-rag-qmd.md
```

`--source` ist wiederholbar. Quellen sind Vault-relative Originaldateien; Wiki-Seiten, technische Spiegel und Pfade außerhalb des Vaults werden nicht als Originalbelege akzeptiert. Der Helper schreibt `wiki_sources` als eine JSON-belegte Frontmatter-Zeile mit `path` und `sha256` sowie `reviewed_at`. Er erhält den Seiteninhalt und verändert bei ungültigen Eingaben keine Metadaten. Seine Erfolgsmeldung ersetzt kein fachliches Review. Neue Hashes allein machen eine alte Aussage nicht aktuell.

## Recherchieren

Dem [Recherche-Skill](../../skills-repo/skills/rag-documentation-research/SKILL.md) folgen und passende Originalcollections aus `_shared/danielsvault-rag/qmd-collections.json` wählen. Bei Bedarf `contextual-wiki-common` ergänzen. Beispiel:

```bash
qmd search 'QMD' -c shared-ai-docs -c contextual-wiki-common --files
```

Vor Nutzung einer Wiki-Seite deren Quellenstand prüfen und relevante Originalpassagen lesen. Bei `review` oder `invalid` aus den aktuellen Originalen arbeiten und die Grenze der Wiki-Seite nennen. QMD-Suchergebnisse und Indexzahlen zertifizieren keine Wiki-Aussage. Gewöhnliche Recherche schreibt weder Seiten noch Prüfdatum; WikiQuery ist aus dem aktiven Routing entfernt.

## QMD-Tagesjob

`update-qmd-index-daily` führt weiterhin ausschließlich Manifest-Reconciliation, QMD update, embed und status aus; siehe [aktueller Prompt](qmd-daily-automation-prompt.md). Zeitplan und Jobeinstellungen werden durch die direkte Wiki-Pflege nicht verändert. Wiki-Inhaltsprüfung ist weder Teil dieses Jobs noch dessen Erfolgsvoraussetzung. Es gibt keine tägliche Wiki-Frist und keinen globalen Importabschluss.

## Bereinigter Bestand und Sicherung

Aktiv ist ausschließlich `common/wiki` unter `_shared/contextual-llm-wiki`. Der alte Compiler samt Wrappern, Patches, Node-Abhängigkeiten, Laufzeit, Release-Updater, Test-Wikis und Arbeits-Worktrees wurde auf ausdrücklichen Auftrag entfernt. Die Betriebsdokumentation liegt hier in `docs/rag`; ein zweiter Implementierungsordner besteht nicht.

Historisches Wissen wurde vor der Umstellung vollständig und geprüft außerhalb des Vaults und QMD-Indexes gesichert. Ausgewählte Synthesen werden nur nach Prüfung gegen aktuelle Originale übernommen. Wiederhergestellte historische Bytes gelten nicht allein dadurch als aktuelles Wissen. Der frühere Compiler-Vollimport blieb unvollständig; die direkte Pflege ersetzt diesen Auftrag.

[Verifikation und Abschluss](llm-wiki-verification-2026-10-02.md) nennen den überprüften Umfang, die externe Sicherung und die Grenzen des Nachweises.
