# LLM-Wiki: Katalog der Kontext-Einstiege

Stand: 02.10.2026. [ADR 0018](../adr/0018-agent-managed-markdown-wiki.md) definiert ein gemeinsam direkt gepflegtes Markdown-Wiki, QMD-Recherche und ausdrückliche ausgewählte Pflege. Die abgelösten Compiler- und WikiQuery-Pläne sind aus den aktiven Dokumentationspfaden entfernt.

## Aktuelles Routing

1. Repo-Startup und ausdrückliche Aufgabengrenzen beachten. Mit einem passenden Fachbereich beginnen; benannte Originale dürfen direkt gelesen werden.
2. QMD mit passenden Originalcollections nutzen und bei Bedarf `contextual-wiki-common` ergänzen. `qmd search` eignet sich für genaue Namen, `qmd query` für natürliche Fragen.
3. Vor Nutzung einer Wiki-Seite deren direkte Quellenstände prüfen und relevante Originalpassagen lesen. Bei Prüfbedarf aus aktuellen Originalen arbeiten und die Grenze der Note nennen. Gleiche Hashes allein zertifizieren keine Aussage.
4. Für ausdrücklich beauftragte Aufnahme, Aktualisierung oder Prüfung ausgewählter Wiki-Inhalte `maintain-llm-wiki` nutzen. Normale Recherche speichert und pflegt keine Seiten.
5. Fachlich relevante Synthesen über Repo-Grenzen einschließlich `private` sind erlaubt. Originale, OpenSpec, ADRs und Repo-Anweisungen behalten ihre Autorität.

[Betriebsbeispiele](llm-wiki.md) bleiben zentral; Repo-Einstiege erhalten kurze Verweise statt kopierter Abläufe.

## Zentrale Dateien

Die folgenden Pfade sind relativ zum `shared-ai-docs`-Gitroot. P0 bezeichnet zentrale Einstiege; P1 bezeichnet zusätzliche Orientierung.

| Priorität | Datei | Rolle / konkretes Routing | Status |
|---|---|---|---|
| P0 | `skills-repo/skills/rag-documentation-research/SKILL.md` | QMD, optionale kuratierte Notizen, Quellencheck und direkte Originalprüfung | aktualisiert |
| P0 | `skills-repo/skills/qmd/SKILL.md` | Recherche- und Indexoperation auswählen; keine implizite Wiki-Pflege | aktualisiert |
| P0 | `skills-repo/skills/maintain-llm-wiki/SKILL.md` | Gemeinsamer ausdrücklicher Pflegeauftrag mit direkten Originalen | implementiert und geprüft |
| P0 | `skills-repo/skills/qmd/references/scheduled-index-maintenance.md` | QMD-only-Tagesjob unabhängig von Wiki-Pflege | QMD-only; Konfiguration hier nicht geändert |
| P0 | `.github/copilot-instructions.md` | Zentralen Recherchefluss verlinken | aktualisiert |
| P0 | `README.md` | Direkte Wiki-Pflege und Betrieb verlinken | aktualisiert |
| P0 | `docs/rag/README.md`, `docs/rag/index.md`, `docs/rag/operating-model-rag-qmd.md` | QMD-Recherche und direkte Wiki-Pflege erklären | aktualisiert |
| P0 | `docs/rag/llm-wiki.md` | Aktiver Seiten-/Quellenvertrag mit ausführbaren Beispielen | aktualisiert |
| P1 | `CONTEXT.md`, `docs/adr/0018-agent-managed-markdown-wiki.md` | Begriffe und akzeptierte Entscheidung | aktualisiert |
| P1 | `AGENTS.md` | Startup und Requirement-Autorität; kurzer optionaler Rechercheverweis | weiterer Verweis geplant |

`~/.codex/skills/<name>` ist bei lokal gepflegten Skills der bestehende globale Symlink auf die kanonische Skilldatei. Aliase sind keine weiteren Pflegeziele. Vendor-Skills werden nicht mit Mac-spezifischem Routing überschrieben. Die tatsächliche Verfügbarkeit des neuen Skills wird in der [Umstellungsevidenz](llm-wiki-verification-2026-10-02.md) geprüft.

## Zusätzliche Einführung

Vault-, Fachrepo- und Projekt-Einstiege können bei passender Folgearbeit einen kurzen Verweis auf den zentralen Recherche-Skill und die direkte Pflege erhalten. Dazu gehören die `AGENTS.md`-/`README.md`-Dateien von Vault, Meeting Assistant, `ki-fuer-kmu`, `ncg-docs`, `probare-crm`, `sparkle`, `private` und Projektbindungen. Ihre aktuelle Einführung ist weiterhin geplant; in dieser Umstellung wird kein fremdes Repository oder generierter Meeting-Kontext pauschal umgeschrieben.

Das Originalcollection-Manifest beschreibt Indexabdeckung. Die aktive Wiki-Collection `contextual-wiki-common` enthält kuratierte Seiten am gemeinsamen Pfad; alte wiki-eigene Spiegel- und Abnahmecollections sind entfernt. Der tägliche QMD-Job behält seine Konfiguration. Die aktuelle Spezifikation und der Abschlussnachweis beschreiben den direkten Markdown-Ablauf.

## Nachweis und Grenzen

Zentrale Dateien wurden für die Umstellung direkt gelesen und ihr Routing abgeglichen. Eine flächendeckende Prüfung sämtlicher Fachrepo-Einstiege wird hier nicht behauptet. Erfolgskriterium für aktuelles Routing: eine gewöhnliche Suche prüft Originale ohne zu speichern; eine Wiki-Seite mit geändertem Original wird nicht als aktuell zertifiziert; ausdrückliche Quellenlimits gelten auch für gemeinsame Synthesen. Der konkrete Helper-, Backup- und aktive Seitennachweis liegt im [Umstellungsbericht](llm-wiki-verification-2026-10-02.md).
