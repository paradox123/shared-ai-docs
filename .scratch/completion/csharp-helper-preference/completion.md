# Completion: persönliche Technologiepräferenz für technische Helfer

## Scope und Identität

- Repository: `~/Documents/DanielsVault/_shared/shared-ai-docs`.
- Feste Git-Basis: `42ad8fe2b42b383093839d1cc702624c0ad3e687`.
- Repo-Write-Set: `skills-repo/skills/build-codex-automations/SKILL.md`, SHA256 `813d5078f1ccb87f0a06f616e0c83c310564dcf67e5bc2a1a3f74d2f047b8f03`.
- Globale Konfiguration außerhalb Git: `~/.codex/AGENTS.md`, zuvor leer, jetzt SHA256 `53ad0fd3631ba6cb31f03079b68ba13891e2c1202c4112c65fdb32a6a7f20f31`.
- Ausgeschlossen: vorhandene Änderungen an `improve-skills/SKILL.md`, `improve-skills/references/codex-desktop-session-review.md`, `install-vendor-skills/SKILL.md` sowie sämtliche vorhandenen Private-Vault-Änderungen.
- Dieser Record ist abgeleitete Evidenz und gehört nicht zur geprüften Inhaltsidentität oder zum Commit-Write-Set.

## Anwendbarkeit

Substantiv: Die Texte ändern die wirksame Technologiewahl für neu implementierte Helfer und eine bisherige Python-Defaultregel. Deshalb vollständige getrennte DRY-, SOLID- und KISS-Prüfung. Kein OpenSpec-Change: eng begrenzte persönliche Präferenz und Skill-Anweisung; die Repo-Regeln erlauben Skill-Wording-/Workflow-Wartung ohne neuen Spec-Change.

## Anforderungen und Nachweis

Quelle: Daniels direkte Anforderung in Codex-Chat `01a1014e-fd9b-74e1-b80d-f8bae64b7413`, 03.10.2026; abschließende Autorisierung: „ok passt, commit und push“.

| Anforderung | Erwartet | Beobachtung und Grenze |
| --- | --- | --- |
| C#/.NET bei ähnlichem Aufwand und Güte | Verbindlicher Default für neue Helfer | Globale Datei sagt ausdrücklich „wähle C#“; Betrieb, Wartung und Nachvollziehbarkeit zählen zum Gesamtaufwand. Kürze/Verfügbarkeit allein ist keine Ausnahme. |
| Vertical Slices | Architekturpräferenz | Globale Datei beschreibt Organisation nach Anwendungsfall samt zusammengehöriger Verarbeitung/Validierung und grenzt das von bloßen Arbeitsschritten ab. |
| Bevorzugt File-based Apps | Kleine eigenständige `.cs`-Helfer | Globale Datei bevorzugt Apps ohne eigenes `.csproj`; SDK, Umfang und Abhängigkeiten erlauben normale .NET-Projekte. |
| Wesentliche Gründe erlauben Abweichungen | Begründete statt absolute Sprachpflicht | Zielstack, APIs/Packages und vorgeschriebene Runtime sind ausdrücklich berücksichtigt; Grund kurz vor Umsetzung, keine zusätzliche Freigabe. |
| Projekt-/Skill-/Automation-übergreifend | Zentrale aktive lokale Anweisung | Die Desktop-App hat die neue globale Datei nach dem Speichern bereits in die aktiven Anweisungen derselben Session übernommen. Globaler Standard gilt pro Codex-Home; andere Hosts/Cloud und projektspezifische Overrides wurden als Grenzen offengelegt. |
| Skills nicht widersprüchlich | Kein pauschaler Python-Default für freie Neuentwicklung | Einziger Skill-Diff ersetzt `python3`-Vorliebe durch bounded extractor, Wiederverwendung kanonischer Helfer und Beachtung globaler Sprach-/Architekturpräferenzen. |
| Bestehende Tools und fremde Arbeit erhalten | Keine Migration oder Nebenänderungen | Neun Automations lesend geprüft; feste Toolaufrufe bleiben unverändert. Private-Vault-Status unverändert; Repo-Diff betrifft nur den freigegebenen Skill. |

Unabhängiger textlicher Gegenbeispielcheck durch `/root/preference_audit`: neuer eigenständiger JSON-Helfer -> C#; bestehender Python-Resolver -> Wiederverwendung; TypeScript-Zielprojekt und AppleScript-Mail.app-Adapter -> legitime Bindung; zu großer File-based-Helfer -> normales .NET-Projekt. Keine Lücken/Widersprüche. Das ist ein Regel-/Szenariocheck; zukünftige Modellbefolgung in beliebigen Umgebungen ist keine deterministische Laufzeitgarantie.

Aktuelle Prüfung ohne zwischenzeitliche Änderung: Skill-Creator `quick_validate.py` meldet `Skill is valid!`; `git diff --check` sauber in Shared- und Private-Repo; globale Datei ist bytegleich zum vorbereiteten Kandidaten und hat keine Whitespace-Fehler.

## Standardsabdeckung

- DRY: zentraler globaler Standard, kanonischer geteilter Skill, keine Promptkopien; keine Migrationsduplikate.
- SOLID: globale Präferenz vs. projektspezifische technische Bindung, Skill-Verantwortung, vorhandene Toolverträge, klare Ausnahmen.
- KISS: kleine gezielte Regeländerung, nachvollziehbare Sprache, kein unnötiges Framework/Abstraktions-/Freigabeverfahren, minimaler Umfang.
- Automatisierte Checks: Frontmatter/Naming/Scaffolding durch bestehenden Skill-Validator; Whitespace durch Git; Scope/Hashes/dirty work durch Root.
- Regelquellen: globale Nutzeranforderung, Shared-Repo `AGENTS.md`, `code-review/references/review-criteria.md`, Skill-Creator.

## Reviewer-Receipts

- DRY: `/root/preference_dry_review`, feste Basis und beide SHA256 wie oben geprüft. Zentraler Standard und kanonische Wiederverwendung ohne Wissensduplikate. Keine Findings; bestanden.
- SOLID: `/root/preference_solid_review`, feste Basis und beide SHA256 wie oben geprüft. Globale Neuimplementierungspräferenz, technische Bindungen, Wiederverwendung und begrenzter Skill-Extraktionsvertrag sind kohärent. Keine Findings; bestanden.
- KISS: `/root/preference_kiss_review`, feste Basis und beide SHA256 wie oben geprüft. Kleine klare zentrale Präferenz und gezielter Skill-Diff; keine unnötigen Schichten, Migrationen oder Freigabeverfahren. Sprache, Frontmatter, Referenzen und beschränkter Umfang erhalten. Keine Findings; bestanden.

Alle drei Reviews liefen getrennt, unabhängig und sequenziell gegen dieselbe unveränderte Kandidatenidentität. Keine Reparaturen erforderlich.

## Zustand und Delivery

Status: `technically-complete`.

Finale Prüfstichprobe am 03.10.2026: beide Hashes unverändert, `git diff --check` sauber, Index vor Delivery leer, HEAD und aktuell abgerufenes origin/main bei gleicher Basis. Vorhandene Validator- und Anforderungsnachweise bleiben für diese unveränderten Inhalte gültig.

Autorisierter Delivery-Umfang: ausschließlich Skill-Datei auf `origin/main` von `paradox123/shared-ai-docs` committen und pushen. Globale `~/.codex/AGENTS.md` bleibt außerhalb Git lokal gespeichert. Kein Commit oder Push bestehender Fremdänderungen, keine Änderung bestehender Automations.

Delivery durchgeführt und verifiziert: Commit `fc70c24fd7282516556040412bd098911c95f0df` (`fix(skills): honor global implementation preferences`) enthält genau die freigegebene Skill-Datei mit einer ersetzten Anweisung. Push auf `refs/heads/main` erfolgreich; `git ls-remote origin refs/heads/main` bestätigt exakt diesen Hash. Die drei vorher vorhandenen Shared-Skill-Änderungen bleiben uncommittet. Dieser lokale Record bleibt ebenfalls außerhalb des Commits; globale AGENTS.md bleibt unverändert lokal aktiv.
