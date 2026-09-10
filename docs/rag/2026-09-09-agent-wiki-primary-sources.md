# Agent-Wiki: Primärquellenanalyse

Stand: 9. September 2026. Untersucht wurde `Ar9av/obsidian-wiki` am Commit [`3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65`](https://github.com/Ar9av/obsidian-wiki/commit/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65), Commitdatum `2026-09-09T09:35:38Z`. Dokumentation und Quellcode wurden statisch gelesen; keine Installation, keine Ausführung fremden Codes, kein Import von Vault-Inhalten. Aussagen zur lokalen Eignung sind Architekturfolgerungen; diese Notiz ersetzt nicht die getrennte Bestandsaufnahme des Vaults.

## Konzept und Implementierung unterscheiden

Das ursprüngliche LLM-Wiki-Muster besteht aus drei Schichten: unveränderte Originalquellen; daraus gepflegte, thematisch organisierte Wissensseiten; Antworten und weitere Ausgaben auf Basis dieser Seiten. Ein Agent integriert neue Erkenntnisse in vorhandene Themen, verknüpft sie und hält Widersprüche fest. Der Mensch bestimmt Quellen, Fragen und Relevanz. Das Original beschreibt Verzeichnisstruktur, Schema und Werkzeuge ausdrücklich als optional und anpassbar. Eine Übernahme des Konzepts verlangt daher weder einen neuen Obsidian-Vault noch die Installation dieses Frameworks. [Karpathys Originalbeschreibung][gist]

`obsidian-wiki` konkretisiert dies mit Markdown-Skills und einem Python-CLI. Quellen können außerhalb des Wiki-Ziels bleiben. Im Wiki liegen Kategorien wie `concepts/`, `entities/`, `skills/`, `references/`, `synthesis/`, dazu `projects/`, `index.md`, `log.md`, eine kurze Momentaufnahme `hot.md` und ein Ingest-Protokoll `.manifest.json`. Seiten besitzen Frontmatter und Quellenbezüge. Das CLI benötigt Python ≥3.9, hat im Basispaket keine externen Runtime-Abhängigkeiten und bezeichnet sich als Beta; Zusatzpakete bieten unter anderem Graphverfahren und einen Server. Ein KI-Agent bleibt für die inhaltliche Verdichtung erforderlich. [Architektur][architecture], [Kernmuster][pattern], [Paketdefinition][package]

## Was die Arbeitsabläufe tun

| Ablauf | Tatsächlich beschriebene Funktion |
|---|---|
| Setup | Richtet Wiki-Verzeichnisse und zentrale Dateien ein; die CLI-Installation kann Skills global und projektspezifisch verteilen. [Setup-Skill][setup], [Installation][installation] |
| Ingest | Liest Quellen, extrahiert Wissen, ergänzt bestehende Seiten oder erzeugt neue. Hashes ermöglichen das Überspringen unveränderter Quellen. `_raw/` ist ein eigener Entwurfs-Eingang; verarbeitete Entwürfe werden laut Skill nach `_raw/_archived/` verschoben. [Ingest][ingest], [Cache][cache] |
| Update | Verdichtet Erkenntnisse des aktuellen Projekts: Entscheidungen, Begründungen und wiederverwendbare Muster. Nutzt den letzten synchronisierten Git-Commit für Änderungen; bei umgeschriebener Historie folgt ein vollständiger Scan. CodeGraph ist optional. [Update][update] |
| Query | Beginnt mit Graphabfrage und Metadaten; kann QMD verwenden und liest passende Seiten gezielt. Bearbeitet keine Wissensseiten, darf aber einen Eintrag in `log.md` ergänzen. [Query][query] |
| Lint | Prüft Struktur, Links, Metadaten und zusätzlich semantisch Aktualität/Widersprüche. Schreibende Konsolidierung verlangt Vorschau und Bestätigung. Confidence-Bewertungen können menschlich geprüfte Einträge im Trust-Ledger voraussetzen. [Lint-Skill][lint-skill], [Lint-Code][lint-code] |
| Dedup | Sucht vermeintlich gleiche Begriffe unter verschiedenen Namen. Standard ist ein Bericht; Merge integriert Inhalte und hinterlässt einen Redirect. `--auto` erlaubt automatische Zusammenführung als ausreichend sicher bewerteter Paare. [Dedup][dedup] |

Die Verfahren sind überwiegend Agentenanweisungen, keine Garantie semantischer Fehlerfreiheit. Beispielsweise erlaubt Dedup eine eingeschätzte statt exakt berechnete Ähnlichkeit. Die Dokumentation ist zudem nicht überall synchron: Die Konfigurationsseite spricht vom Entfernen verarbeiteter `_raw/`-Originale; der konkrete Ingest-Skill verlangt deren Archivierung. Für eine Integration sind die konkreten Skills und der Code maßgeblich zu prüfen. [Dedup][dedup], [Konfiguration][config], [Ingest][ingest]

## Mehrere Repos: grundsätzlich vereinbar, jedoch keine automatische Grenzerkennung

**Unterstützt:** Mehrere benannte Wiki-Ziele über `config.work`, `config.personal` etc.; `@name` wählt pro Auftrag ein Ziel, ohne den Standard zu ändern. Projektspezifische `.env`-Dateien können ebenfalls routen. Mehrere lokale Git-Repos sind als getrennte Quellen möglich; bei einem direkt angegebenen Repo-Root ermittelt der Batch-Code Dateien mit `git ls-files --cached --others --exclude-standard`. [Installation][installation], [Konfiguration][config], [Batch-Code][batch]

**Nicht gleichbedeutend:** Mehrere Wiki-Ziele sind keine Unterstützung eines einzigen Schreibbereichs über beliebige verschachtelte Git-Repos. Graph und Lint laufen rekursiv durch das gewählte Wiki-Ziel und kennen feste Ausschlussordner; eine allgemeine Grenze am nächsten Repo-Root wird nicht geprüft. [Graph-Code][graph], [Lint-Code][lint-code]

**Konkrete Einschränkung:** `graph_analysis._page_slug` und `graphrag.build_index` verwenden den normalisierten Dateistamm als Identität, ohne Verzeichnis. Mehrere `README.md`, `AGENTS.md` oder gleichnamige Themen werden damit in einem Graph zusammengelegt; der Query-Index überschreibt Metadaten früherer gleichnamiger Seiten. Pfade in Links werden ebenfalls auf den Dateinamen reduziert. Das macht einen umfassenden Graph über viele vorhandene Repos fachlich unzuverlässig. [Graph-Code][graph], [Query-Index-Code][graphrag]

**Folgerung für eine schon vorhandene Repo-Struktur:** Originaldokumente an ihren autoritativen Orten belassen und je Zuständigkeitsbereich einen kleinen Wiki-Schreibbereich führen. Ein solcher Bereich kann ein Unterordner im bestehenden Repo sein; das Konzept benötigt dort keinen neuen Git-Root. Repositoryübergreifende Seiten nur bewusst in einem gemeinsamen Bereich verfassen. Das sind Gestaltungsentscheidungen, keine zugesicherte automatische Frameworkfunktion.

## Markdown-Links, vorhandene Schemata und QMD

Normale Links `[Titel](pfad.md)` sind unterstützt: `OBSIDIAN_LINK_FORMAT=markdown` steuert neue Links; vorhandene Links werden nicht automatisch umgestellt. Graph und Lint erkennen sowohl Markdown- als auch Wikilinks. Ihr Abgleich bleibt jedoch auf Dateistämmen aufgebaut. YAML-IDs aus einem fremden Schema werden nicht automatisch zu Kanten: Lint versteht den eigenen `relationships:`-Block; der Graphparser sucht Linksyntax, auch wenn sie innerhalb von YAML vorkommt. Ein SpecOps-ID-Modell bräuchte deshalb eine explizite Abbildung, keine pauschale Migration zu Wikilinks. [Linkkonvention][pattern], [Graph-Code][graph], [Lint-Code][lint-code]

QMD ist eine optionale Suchintegration: `QMD_WIKI_COLLECTION` bezeichnet verdichtete Wiki-Seiten, `QMD_PAPERS_COLLECTION` Quellen. Query kann lexikalische und semantische Suche über MCP oder CLI verwenden; CLI-Modi wählen Reranking, kein Reranking oder Vektorsuche. Ingest sucht verwandte Quellen. Schreibende Skills sehen anschließend `qmd update`, bei fehlenden/veralteten Vektoren `qmd embed` und eine gezielte Sichtbarkeitskontrolle vor. Wiki-Schreiben wird bei einem QMD-Fehler nicht zurückgerollt. [Query][query], [Ingest][ingest], [Update][update]

Die Schichten sollen disjunkt indexiert werden: Entwürfe und bereits ersetzte Quellen dürfen nicht als kuratierte Aussagen zurückkommen. Die Beispielkonfiguration erwähnt `_raw/` und `log.md`; bei einer eigenen Einführung wären zusätzlich Review-Staging, Archive, doppelt indexierte Pfade und zulässige Tätigkeitsbereiche zu prüfen. Diese Erweiterung ist eine Integrationsfolgerung. [Konfiguration][config], [Query][query]

**QMD bleibt sinnvoll:** Es findet Informationen; die Wiki-Pflege entscheidet, welche Aussagen dauerhaft zusammengeführt und aktualisiert werden. Das Wiki verschiebt einen Teil der Synthese von jeder einzelnen Frage auf den Zeitpunkt der Pflege. Für seltene, neue oder detailreiche Fragen bleibt der Rückgriff auf Originalquellen nötig. Ein Hybrid kann gezielt zuerst kuratiertes Wissen suchen und bei Lücken Quellen hinzunehmen. Das ist die Folgerung aus den getrennten Suchschichten, kein gemessener Vorteil für DanielsVault.

**Für eine Regel „QMD ist die einzige Retrieval-Engine“:** Das vollständige Framework wäre nicht unverändert regelkonform. `graph-query` verwendet zusätzlich einen eigenen Metadaten-/Linkindex; `.manifest.json` ist außerdem eine zusätzliche Datenhaltung für Ingest-Historie, keine QMD-Collection. Bei einer Konzeptübernahme können QMD-Retrieval und bestehende Betriebsverantwortung erhalten bleiben; nur die Wissenspflege wird ergänzt. [Query][query], [Query-Index-Code][graphrag], [Cache][cache]

## Aufwand, Betrieb und Grenzen

Der technische Installationsaufwand ist nicht der eigentliche Migrationsaufwand. Zu entscheiden sind Schreibgrenzen, Quellenhoheit, Seitenschema, Namenskonflikte, Aktualisierungsregeln, QMD-Auswahl und Review. Auf einen kleinen Bereich begrenzte Konzeptübernahme vermeidet eine Vollmigration; eine belastbare Aufwandsschätzung benötigt Umfang und Qualität der lokalen Inhalte sowie einen Pilotversuch.

Vorteile, die sich aus dem Muster ergeben: wiederverwendbare Antworten und Begründungen, Verbindungen über einzelne Dokumente hinaus, sichtbare Quellen und Widersprüche sowie weniger wiederholte Synthese. Kosten und Risiken: anfängliche Modellarbeit, fortlaufende Reviews, Informationsverlust durch Verdichtung, falsch zusammengeführte Themen, veraltete Zusammenfassungen und zusätzlicher Pflegezustand. Quellenverweise und Inferenzmarker verbessern die Prüfbarkeit, beweisen aber nicht die Richtigkeit. Das Framework selbst benötigt für Confidence eine semantische Prüfung unabhängiger Belege und menschliche Freigaben; URL-Zählen genügt nicht. [Kernmuster][pattern], [Lint-Skill][lint-skill]

Parallelität ist begrenzt: Manifeständerungen über `cache-update` werden gesperrt und atomar geschrieben; Wiki-Seiten, `index.md` und `hot.md` haben laut Architektur keine solche Sperre. Mehrere Agenten können sich dort überschreiben. [Architektur][architecture]

**Vor Gesamtinstallation konkret beachten:** `install_project` ersetzt vorhandene Bootstrap-Dateien einschließlich `AGENTS.md` und Aliasdateien. `sync` führt für den Wiki-Git-Root `git add -A`, Commit und Push aus. Dedup/Lint können vor Änderungen ebenfalls alle ausstehenden Änderungen in einem Repo-Snapshot committen. Diese Voreinstellungen passen nicht automatisch zu laufender Arbeit und bereits vorhandenen Repo-Regeln. [Installer-Code][cli], [Sync-Code][sync], [Dedup][dedup], [Lint-Skill][lint-skill]

Staged Writes sind optional; ohne Einstellung wird direkt geschrieben. Selbst mit Staging werden Trackingdateien unmittelbar aktualisiert. Das ist eine Agentenkonvention und keine isolierende Dateisystemtransaktion. [Ingest][ingest], [Stage-Commit][stage]

## Aussagekraft von Leistungs- und Datenschutzversprechen

Die README berichtet rund 4,4-fache Geschwindigkeit und 83 % statt 44 % richtige Antworten. Grundlage sind vier strukturelle Fragen, zwei Wiederholungen je Bedingung, ein 38-Seiten-Vault und Claude Sonnet. Gemessen wurden Graphfragen, kein repräsentativer Vergleich gegen einen gut eingerichteten QMD-Workflow. API-Kosten waren im Beispiel ungefähr gleich. Die Autoren bezeichnen die Stichprobe selbst als klein. Daraus folgt kein belastbares Kosten- oder Qualitätsversprechen für diesen Vault. [README, Methodik][readme], [Benchmark-PR][benchmark]

„Lokal“ ist für Markdown, CLI und optional lokale Indizes plausibel; „nichts verlässt den Rechner“ ist für den gesamten Arbeitsablauf keine technische Zusicherung. Die Skills nutzen den jeweils gewählten KI-Agenten: Bei einem gehosteten Modell werden die eingelesenen Inhalte Teil seiner Verarbeitung. Optionaler Git-Push überträgt den Vault; PageIndex kann einen LLM-Dienst verwenden. `visibility/pii` ist lediglich eine optionale Abfragefilterung und standardmäßig werden alle Seiten berücksichtigt. Tätigkeits- und Vertraulichkeitsgrenzen müssen durch Zielwahl, Retrieval-Scope und Zugriffsrechte erhalten bleiben, nicht nur durch Tags. [Architektur][architecture], [Sync-Code][sync], [PageIndex-Konfiguration][config], [Query][query]

[gist]: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
[architecture]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/docs/architecture.md
[pattern]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/.skills/llm-wiki/SKILL.md
[package]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/pyproject.toml
[setup]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/.skills/wiki-setup/SKILL.md
[installation]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/docs/installation.md
[config]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/docs/configuration.md
[ingest]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/.skills/wiki-ingest/SKILL.md
[update]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/.skills/wiki-update/SKILL.md
[query]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/.skills/wiki-query/SKILL.md
[lint-skill]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/.skills/wiki-lint/SKILL.md
[dedup]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/.skills/wiki-dedup/SKILL.md
[stage]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/.skills/wiki-stage-commit/SKILL.md
[batch]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/obsidian_wiki/batch.py
[graph]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/obsidian_wiki/graph_analysis.py
[graphrag]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/obsidian_wiki/graphrag.py
[lint-code]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/obsidian_wiki/lint.py
[cache]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/obsidian_wiki/cache.py
[cli]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/obsidian_wiki/cli.py#L295-L335
[sync]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/obsidian_wiki/sync.py#L97-L124
[readme]: https://github.com/Ar9av/obsidian-wiki/blob/3e9e6abeaed46dc8242fa1f32b9d02615d6e2a65/README.md
[benchmark]: https://github.com/Ar9av/obsidian-wiki/pull/175
