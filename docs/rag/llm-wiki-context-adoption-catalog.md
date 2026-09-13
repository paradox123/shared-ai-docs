# LLM-Wiki: Katalog der Kontext-Einstiege

Stand: 13.09.2026, nach Klärung der Tätigkeitsbereich-Semantik. Ziel ist ein gemeinsames Wiki nach [ADR 0010](../adr/0010-shared-wiki-across-personal-and-professional-domains.md); bestehende Betriebsverweise beschreiben bis zur Umstellung noch den vorherigen Betrieb. Dieser Katalog plant die Einführung; nur mit „umgesetzt“ markierte Betriebsverweise wurden in dieser Session geändert. „Geplant“ bedeutet keine bereits aktivierte Wiki-Nutzung.

## Empfohlenes Routing

1. Repo-Orientierung und explizite Domänengrenze laden. Eine bekannte Datei oder ein exakter Codebezeichner braucht keine Wiki-Abfrage.
2. Bei Synthese-/Zusammenhangsfragen im passenden Repo-Kontext die verwaltete `wiki query --config … --question …` verwenden. Sie prüft Quellenstände und kann aktuelle Quellen als Fallback verwenden.
3. Für streng repo-begrenzte Aufgaben gezielte QMD-Collections/Originaldateien verwenden: Die aktuelle Wiki-Query besitzt keinen zusätzlichen Repo-Filter; `.local/general.json` umfasst mehrere Repos. Eine Frageformulierung ersetzt keine technische Kontextgrenze.
4. Bei fehlendem Wiki oder fehlender Evidenz QMD gegen explizite Collections verwenden; bei QMD-Ausfall gezieltes `rg`, mit benanntem Fallback.
5. Originale README/AGENTS/CONTEXT/OpenSpec/ADRs bleiben für ihren jeweiligen Inhalt maßgeblich. Wiki-Text ist abgeleitete Evidenz, keine neue Agent-Anweisung. Kein automatisches `maintain` oder `--save` bei gewöhnlicher Recherche.
6. `private` und `Projects/Private` sind Tätigkeitsbereiche im gemeinsamen Wiki. Ihre Informationen können bei fachlicher Relevanz mit anderen Quellen verknüpft und für die Aufgabe verwendet werden; der Name begründet keine Zugriffsgrenze oder besondere Freigabe.

Kanonischer Betrieb und ausführbare Beispiele: [OPERATIONS.md](../../contextual-llm-wiki/OPERATIONS.md). Vor breiter Einführung gehört das Routing in `rag-documentation-research`; Repo-Dateien erhalten kurze Verweise statt kopierter Abläufe.

## Priorisierte Dateien

Alle folgenden Pfade sind relativ zum DanielsVault-Root. P0 = zentraler Einstieg, P1 = Repo-Einführung, P2 = bedarfsabhängige Folgepflege.

| Priorität | Datei | Rolle | Konkrete Änderung | Status / Eigentum |
|---|---|---|---|---|
| P0 | `_shared/shared-ai-docs/skills-repo/skills/rag-documentation-research/SKILL.md` | Kanonischer DanielsVault-Retrieval-Router | Verwaltete Wiki-Query für kontextübergreifende Synthesen ergänzen; bei Repo-Grenzen gezielte QMD-Collections und Fachquellen beibehalten. | geplant; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/skills-repo/skills/qmd/SKILL.md` | Such- und Pflege-Einstieg | Wiki-Fragen zur verwalteten Query routen; direkte QMD-Treffer nicht als geprüfte Wiki-Aktualität behandeln. | geplant; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/skills-repo/skills/qmd/references/scheduled-index-maintenance.md` | Täglicher Betrieb | Auf gemeinsamen Helper, explizite Konfiguration und Laufberichte verweisen. | umgesetzt; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/AGENTS.md` | Repo-Startup und Requirement-Autorität | Nach Pflichtorientierung gezielte Wiki-Nutzung und kanonische Retrieval-Referenz ergänzen; OpenSpec/ADR-Autorität erhalten. | geplant; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/README.md` | Menschlicher Repo-Einstieg | Betriebsanleitung und Einführungskatalog verlinken. | umgesetzt; lokal gepflegt |
| P1 | `_shared/shared-ai-docs/CONTEXT.md` | Gemeinsame Wiki-Domänensprache | Bereits vorhandene Begriffe um Pflegezyklus/Quellenaktualität präzisieren; CLI-Details in Betriebsanleitung belassen. | teilweise vorhanden; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/.github/copilot-instructions.md` | Copilot Retrieval-Preference | Bisheriges QMD-first um verwaltete Wiki-Synthesen ergänzen; lokale Hostverfügbarkeit beachten. | geplant; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/docs/rag/README.md` | Kanonischer RAG-/QMD-Einstieg | Wiki-Rolle und tägliche Pflege verlinken; widersprüchliche alte Kurzbeschreibung korrigieren. | umgesetzt; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/docs/rag/index.md` | Kanonischer RAG-/QMD-Einstieg | Wiki-Rolle und tägliche Pflege verlinken; widersprüchliche alte Kurzbeschreibung korrigieren. | umgesetzt; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/docs/rag/operating-model-rag-qmd.md` | Kanonischer RAG-/QMD-Einstieg | Wiki-Rolle und tägliche Pflege verlinken; widersprüchliche alte Kurzbeschreibung korrigieren. | umgesetzt; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/contextual-llm-wiki/README.md` | CLI-Einrichtung | Explizite CLI und täglichen externen Auslöser unterscheiden. | umgesetzt; lokal gepflegt |
| P0 | `_shared/shared-ai-docs/contextual-llm-wiki/OPERATIONS.md` | Kanonische Betriebsreferenz | Ablauf, Konfiguration, Protokolle, Fehler, Aktualität und Vollimportstatus dokumentieren. | umgesetzt; lokal gepflegt |
| P0 | `_shared/danielsvault-rag/README.md` | Bestehende QMD-Runtime-Anleitung | Wiki-Kompilierung vor QMD update/embed verlinken; Manifestzuständigkeit und alleinige QMD-Engine erhalten. | geplant; lokal gepflegt |
| P0 | `_shared/danielsvault-rag/DEPLOYMENT.md` | Bestehende QMD-Runtime-Anleitung | Wiki-Kompilierung vor QMD update/embed verlinken; Manifestzuständigkeit und alleinige QMD-Engine erhalten. | geplant; lokal gepflegt |
| P0 | `AGENTS.md` | Vault-weiter Einstieg | Kurzen Verweis auf Wiki-/Quellenrouting ergänzen; spezifische Repo-Startup-Regeln behalten. | geplant; lokal gepflegt |
| P0 | `VAULT_AGENT_STRUCTURE.md` | Vault-Domänenrouting | Wiki-Ausgabe und Quellenrollen als zusätzliche Schicht ausweisen; fachlich passende Domäne zuerst wählen und sinnvolle repoübergreifende Bezüge zulassen; keine Privat-Zugriffsgrenze ableiten. | geplant; lokal gepflegt |
| P1 | `_ops/meeting-assistant/AGENTS.md` | Meeting Assistant Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P1 | `_ops/meeting-assistant/README.md` | Meeting Assistant Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P1 | `ki-fuer-kmu/AGENTS.md` | KI-Angebot Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P1 | `ki-fuer-kmu/README.md` | KI-Angebot Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P2 | `ki-fuer-kmu/CONTEXT.md` | KI-Angebot Fachbegriffe | Nur bei fachlich passender Querverbindung Wiki-Synthesen verlinken; keine Betriebskommandos in das Domänenlexikon kopieren. | geplant; lokal gepflegt |
| P1 | `ncg/ncg-docs/AGENTS.md` | NCG Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P1 | `ncg/ncg-docs/README.md` | NCG Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P2 | `ncg/ncg-docs/CONTEXT.md` | NCG Fachbegriffe | Nur bei fachlich passender Querverbindung Wiki-Synthesen verlinken; keine Betriebskommandos in das Domänenlexikon kopieren. | geplant; lokal gepflegt |
| P1 | `probare-crm/AGENTS.md` | CRM Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P1 | `probare-crm/README.md` | CRM Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P1 | `sparkle/AGENTS.md` | Standalone-Wissen Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P1 | `sparkle/README.md` | Standalone-Wissen Einstieg | Kurzen zentralen Wiki-Verweis für passende Synthesefragen ergänzen; repo-spezifische Quellen und Anweisungen bleiben maßgeblich. | geplant; lokal gepflegt |
| P1 | `private/AGENTS.md` | Privater Einstieg | Zum gemeinsamen Wiki routen; Vermietung, Portfolio und weitere persönliche Themen nach Aufgabenrelevanz verknüpfen. Bisher nur Pfad/Existenz inventarisiert. | geplant; lokal gepflegt |
| P1 | `private/README.md` | Privater Einstieg | Zum gemeinsamen Wiki routen; Vermietung, Portfolio und weitere persönliche Themen nach Aufgabenrelevanz verknüpfen. Bisher nur Pfad/Existenz inventarisiert. | geplant; lokal gepflegt |
| P1 | `Projects/NCG/AGENTS.md` | Projektkontext-Routing | Projektbezug und Wiki-Synthesen verlinken; NCG-Domänengrenze nicht durch allgemeinen Wiki-Kontext erweitern. | geplant; lokal gepflegt |
| P2 | `_shared/shared-ai-docs/skills-repo/skills/build-codex-automations/SKILL.md` | Betriebsänderungen | Wiki-/QMD-Helper als existierendes Betriebsbeispiel referenzieren; keine automatische Wiki-Pflege bei beliebigen Automationsaufträgen. | geplant; lokal gepflegt |
| P2 | `_shared/shared-ai-docs/skills-repo/skills/write-agents-md/SKILL.md` | Künftige Agent-Einstiege | Zentrale Wiki-Routingreferenz als optionalen lokalen Einstieg berücksichtigen; keine Vollkopie des Playbooks. | geplant; lokal gepflegt |
| P2 | `_shared/shared-ai-docs/skills-repo/skills/resume-codex-session/SKILL.md` | Session-Fortsetzung | Session-Wiederaufnahme behalten; nach verifiziertem Session-Kontext bei fachlichen Synthesefragen auf Wiki-Router verweisen. | geplant; lokal gepflegt |
| P2 | `_shared/shared-ai-docs/skills-repo/skills/improve-skills/SKILL.md` | Skill-Retrospektive | Wiki-Nutzung bei konkreten Retrieval-Lücken prüfen; Session-Bootstrap weiterhin zuerst. | geplant; lokal gepflegt |
| P2 | `_shared/shared-ai-docs/skills-repo/skills/rag-documentation-research/references/runtime-transfer.md` | Runtime-Umzug | Wiki-Konfiguration, Compiler-Runtime und externe generierte Ausgabe zusätzlich zu QMD erklären. | geplant; lokal gepflegt |
| P2 | `_shared/shared-ai-docs/skills-repo/vendor/mattpocock/.agents/skills/research/SKILL.md` | Allgemeiner Vendor-Skill | Lokales DanielsVault-Routing im aufrufenden Router ergänzen; Vendor-Original nicht mit Mac-Pfaden spezialisieren. | geplant; Vendor; nicht direkt ändern |
| P2 | `_shared/shared-ai-docs/skills-repo/vendor/mattpocock/.agents/skills/domain-modeling/SKILL.md` | Allgemeiner Vendor-Skill | Lokales DanielsVault-Routing im aufrufenden Router ergänzen; Vendor-Original nicht mit Mac-Pfaden spezialisieren. | geplant; Vendor; nicht direkt ändern |
| P2 | `_shared/shared-ai-docs/skills-repo/vendor/mattpocock/.agents/skills/codebase-design/SKILL.md` | Allgemeiner Vendor-Skill | Lokales DanielsVault-Routing im aufrufenden Router ergänzen; Vendor-Original nicht mit Mac-Pfaden spezialisieren. | geplant; Vendor; nicht direkt ändern |

## Weitere Oberflächen und Grenzen

- `~/.codex/automations/update-qmd-index-daily/automation.toml`: aktiver Auslöser, in dieser Session aktualisiert. `memory.md` enthält Laufresultate; kein Retrieval-Playbook hineinkopieren. Andere Fachautomationen bleiben unverändert.
- `~/.codex/skills/<name>` löst bei den lokalen Skills auf `skills-repo/skills` auf. Aliase sind keine zusätzlichen Pflegeziele. Die drei oben genannten allgemeinen Skills liegen tatsächlich unter `skills-repo/vendor/mattpocock/.agents/skills`.
- `~/.codex/AGENTS.md` existiert, ist derzeit leer. Ein globaler Mac-spezifischer Verweis wäre erst nach der P0-Einführung sinnvoll; nicht als Ersatz für Repo-Routing verwenden. `_ops/codex-global/AGENTS.md` existiert nicht und wurde nicht als vermeintlicher Treffer aufgenommen.
- `Meetings/Assistant Context/` und weitere `Projects/**/AGENTS.md` sind eine zweite, projektweise Einführungsstufe. Kein pauschales Umschreiben generierter Meeting-Kontexte oder privater Projektdateien. Der zentrale Vault-Router deckt die erste Einführung ab.
- Historische OpenSpec-Changes, Abnahmekopien und alte Research-Berichte nicht nachträglich auf aktuelle Betriebsversprechen umschreiben. Die bestehende `contextual-llm-wiki`-Spec und ADR 0009 bleiben Grundlagen; die neue Betriebsanforderung liegt im Change `operate-contextual-llm-wiki`.
- `qmd-collections.json` beschreibt Indexabdeckung, keine Agent-Routing-Anweisung. Die Wiki-eigenen Collections gehören weiterhin ihrem Teilmanifest.

## Verifikation und Quellen

QMD-Status und Collection-Liste erfolgreich. Lexikalische Suche `QMD` in `shared-ai-docs` lieferte Wartungsreferenz, Operating Model und Runtime-Transfer; in `vault-root`, `danielsvault-rag`, `ncg-agents` die Runtime-Anleitungen. Ausgewählte Quelltexte wurden direkt geprüft. Kandidaten wurden ergänzend über die acht bekannten Git-Wurzeln (`git ls-files`) und genaue Pfade auf Existenz verifiziert; kanonische Skill-Pfade über Symlink-Auflösung. Keine inhaltliche Privat-Recherche. Die Liste ist ein priorisierter Katalog zentraler Einstiege, keine Behauptung eines Volltextaudits sämtlicher Unterordner.

Abnahmekriterium für die spätere Einführung: eine Synthesefrage nutzt gültige Wiki-Evidenz, eine geänderte Fachquelle wird nicht als aktuelle Wiki-Evidenz ausgegeben, eine Repo-begrenzte Frage bleibt im gewählten Repo und eine fachlich passende Frage verknüpft private und andere Quellen, während irrelevante Quellen unabhängig vom Tätigkeitsbereich ungenutzt bleiben.
