# LLM-Wiki: Umstellung und Bereinigung vom 02.10.2026

## Ergebnis und aktueller Vertrag

Der frühere Compiler-Vollimport wurde nicht erfolgreich abgeschlossen. Die akzeptierte [Entscheidung](../adr/0018-agent-managed-markdown-wiki.md) ersetzt ihn durch ausdrückliche ausgewählte Markdown-Pflege. Maßgeblich sind die [Wiki-Spec](../../openspec/specs/contextual-llm-wiki/spec.md), [Betriebs-Spec](../../openspec/specs/contextual-wiki-operations/spec.md) und [Betriebsanleitung](llm-wiki.md).

Aktiver Bestand: `_shared/contextual-llm-wiki/common/wiki`, mit einer geprüften [QMD/rag/Wiki-Synthese](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/common/wiki/notes/qmd-rag-wiki.md), Index, Log und lokalen Agenten-Anweisungen. Der kanonische Skill `maintain-llm-wiki` und sein stdlib-Quellenhelper bleiben verfügbar. Sie benötigen keinen Compiler, Importzustand, Provideradapter oder transitiven Antwortgraph.

## Erhaltung historischer Kenntnisse

Vor Umstellung wurde der vollständige alte Wiki-Bestand mit erforderlichem Zustand außerhalb indexierter Wurzeln gesichert. 52.409 reguläre Archivdateien wurden erneut gelesen und mit den Originalhashes verglichen. Archiv: `/Users/dh/.local/state/contextual-llm-wiki/backups/agent-managed-20261002T184159Z/legacy.tar.gz`, 104.793.194 Bytes, SHA-256 `063c4400aac86e62fa26e4ca2cad77c5dfc2e01d67a1c8af0be04c993fdaef04`. Das Manifest liegt daneben. Historische Synthesen bleiben wiederherstellbar; nur gegen heutige Originale geprüfte Inhalte werden als aktuelle Seiten übernommen.

## Öffentliche Schnittstellen und tatsächliche Inhaltsprüfung

| Anforderung | Beobachtetes Ergebnis |
|---|---|
| Direkte Quellenprüfung ohne Mutation | Öffentliche Subprozess-Tests prüfen unveränderte, geänderte und fehlende Originale, feste SHA-256, Seitenauswahl und unveränderte Pagebytes. |
| Sichere Metadatenpflege | `record` erhält Prosa und fremde Metadaten; fehlende Originale, Wiki als Quelle, technische Spiegel und Pfad-/Symlink-Ausbrüche werden ohne Seitenschreibzugriff abgewiesen. |
| Ungültige Metadaten sichtbar | Fehlendes/malformed Frontmatter oder Prüfdatum und nicht existierendes Wiki liefern JSON-Fehler und Exit 1. Persistierte absolute Pfade sind ungültig, `~` wird als relativer Pfad behandelt. |
| Fachliche ausgewählte Synthese | Ein Agent erstellte die reale Rollen-Synthese gegen zwei aktuelle Originale. Direkte Belege, technische Private-Scope-Grenze und unbelegte historische Detailaussagen wurden inhaltlich geprüft. |
| Nachpflege bei geänderter Quelle | Ein zweiter Agent revidierte eine isolierte Kopie inhaltlich nach geändertem Original. Er benannte Quellenwiderspruch, zukünftiges Datum und unbewiesenen Migrationsstand. Erst danach führte `record` zu `unchanged`. |
| Aktuelle Seite nach Bereinigung | Der Quellencheck erkannte den verschobenen Anleitungslink im Betriebsmodell als Änderung. Beide Originale und Aussagen wurden erneut geprüft; nur dieser Link war verändert. Prosa blieb korrekt und unverändert, danach wurde der Quellenstand erneuert. |
| QMD bleibt unabhängig | QMD-only-Runner, Automationsdefinition, Originalmanifest und aktive Collectiondefinitionen bleiben erhalten. 25 Originalcollections und `contextual-wiki-common` bilden den bestehenden Umfang. |

Zwölf unveränderte öffentliche Quellenhelper-Tests bestanden nach Bereinigung mit der Repository-Pythonruntime. Der erste Versuch in der Task-Sandbox scheiterte ausschließlich am Testfixture-Schreibzugriff unter dem Benutzer-Home; die gleiche Suite bestand über die genehmigte lokale Ausführung. Vorher bestand sie auch mit macOS Python 3.9.6. Alte Retirementtests entfallen gemeinsam mit den entfernten Einstiegspunkten; sie sind keine aktuelle Testpflicht.

Die ursprüngliche Umsetzung wurde separat in DRY → SOLID → KISS geprüft. Frontmatter- und persistierte Quellenpfad-Funde wurden durch öffentliche Rot→Grün-Tests behoben. Reviewed manifest: `bb707310b522ae68e06442a753aba31dfa07416fd922903526fd379f6b53287a`. Helper-Code und dessen Tests bleiben gegenüber diesem Kandidaten unverändert; die Bereinigung erhält eigene begrenzte Requirements-/Review-Evidenz.

## Ausdrücklich beauftragte Bereinigung

- Vollständiger alter `shared-ai-docs/contextual-llm-wiki`-Implementierungsbaum entfernt: TypeScript, Wrapper, Patches, Compiler-Tests, Node-Abhängigkeiten, Runtime und lokale Arbeitsdaten.
- Drei alte Ausgaben `acceptance-general`, `acceptance-private`, `migration-ticket-02` entfernt; unter `_shared/contextual-llm-wiki` bleibt ausschließlich `common`.
- Vier compilerbezogene Scratch-/Ticket-Bäume, drei alte Compiler-OpenSpec-Archive, der überholte Release-Plan und vier überholte Planungs-/Integrationsdokumente entfernt. Aktuelle Anforderungen und kompakte Entscheidungshistorie bleiben erhalten.
- Registrierter Worktree `shared-wiki-resumable-generation-main` und fünf ausschließlich compilerbezogene lokale Branches entfernt. Die drei `shared-wiki-*`-Branches und der resumable Branch hatten keine eigenen Commits gegenüber dem Hauptcheckout; Release-Commits sind im verifizierten externen Git-Bundle wiederherstellbar.
- Zusätzlich den sauberen Vault-Worktree `wiki-resumable-generation/DanielsVault` samt leerem Wrapper entfernt: identischer HEAD zum Haupt-Vault, keine eigenen Commits oder lokalen Dateien.
- Verbliebener Ordner `shared-ai-docs-update-llm-wiki-releases` entfernt. Er enthielt nur zwei Scheduler-Logs; kein Git-Checkout und keine Wiki-Seiten.
- LaunchAgent `com.danielsvault.wiki-releases` entladen und seine Plist gelöscht. Der geladene, inaktive Job versuchte alle sechs Stunden das fehlende `check-releases.py` zu starten; 25 Versuche, letzter Exit 2. Der konkrete Dienst ist nach Entfernung nicht mehr geladen.

Zusätzliche Wiederherstellungssicherung: `/Users/dh/.local/state/contextual-llm-wiki/backups/compiler-cleanup-20261002/obsolete-files.tar.gz`. 5.275 reguläre Dateien erneut gelesen und per SHA-256 geprüft; 34.291.154 Bytes; SHA-256 `3eab3b0e892245d83f02b247d0b64b6d434b7fd1afcfc61887eb8ed4c4136aa0`. Wegwerfbare Caches, Dependencies und Laufzeitdateien sind aus dieser zusätzlichen Sicherung ausgenommen; ursprüngliche Wiki-Bytes bleiben im vollständigen früheren Archiv. `archive-manifest.json`, `cleanup-report.json`, Git-Bundle und aktuelle Prüfergebnisse liegen daneben außerhalb des QMD-Indexes.

## Grenzen und Indexnachweis

Helper-Erfolg oder gleiche Quellenhashes ersetzen kein fachliches Review. Eine aktuelle ausgewählte Seite bestätigt weder Vollimport noch Aktualität sämtlicher Vault-Inhalte. Fremde Änderungen im Hauptcheckout bleiben erhalten. Die Bereinigung vom 02.10.2026 wurde ohne Veröffentlichung abgeschlossen; die Auslieferung auf `main` wurde am 03.10.2026 separat akzeptiert.

Die Wiki-Umsetzung änderte die tägliche QMD-Automationsdefinition nicht. Eine zuvor beobachtete externe Speicherung wechselte am 02.10.2026 um 19:06:34 UTC ins Heartbeat-Format. Aktuell sind QMD-only-Prompt und täglicher 07:00-Zeitplan verifiziert; Ursache und ehemalige Cron-Modell-/Projektfelder sind anhand dieser Datei nicht feststellbar. Es wurde keine Gegenänderung vorgenommen.

Der manuelle QMD-Abschlusslauf verwendet den bestehenden Runner und ein neues Report-Verzeichnis. Sein genaues Ergebnis wird in der externen `closeout.json` neben dem Bereinigungsbericht festgehalten. Vorheriger erfolgreicher Lauf: `/Users/dh/.codex/automations/update-qmd-index-daily/runs/20261002-agent-wiki-final-corrected/report.json`, alle fünf Schritte Exit 0, 25 Originalcollections unverändert, 2.509 Dokumente, 14.445 Vektoren und keine offenen Embeddings. Ein manueller Lauf beweist keinen zukünftigen Schedulerlauf und keine fachliche Wahrheit indexierter Seiten.

## Auslieferung vom 03.10.2026

Der Benutzer akzeptierte Commit, Push, Integration auf `main` und Entfernung der temporären Auslieferungsdateien. Unveränderte Wiki-Helper-, Inhalts- und Bereinigungsprüfungen werden übernommen; fremde Skill-Änderungen bleiben außerhalb des Commits. Der vollständige alte Compilerbaum wird auch gegenüber den zwei zusätzlich auf `main` vorhandenen historischen Compilerdateien entfernt.

Das begrenzte QMD-Review erkannte einen Timeout, bei dem ein untergeordneter QMD-Prozess nach dem Fehlerbericht weiterarbeiten konnte. Jeder Runner-Schritt besitzt nun seine eigene Prozessgruppe und beendet sie vor dem Timeout-Bericht. Der reale verzögerte Kindprozess-Test schlägt beim alten Runner fehl und besteht mit der Korrektur; zwei öffentliche CLI-Prüfungen bestätigen den normalen Ablauf und das Überspringen von Embeddings nach fehlgeschlagenem Update. Alle drei Tests bestehen. Die bestehende Betriebsanforderung und ihr archivierter Change halten diesen Ausführungsvertrag fest.

Der tatsächlich geplante Heartbeat-Lauf vom 03.10.2026, 08:16:24–08:16:35 MESZ, verwendete den vorherigen Runner erfolgreich: fünf Schritte Exit 0, 25 Originalcollections unverändert, 2.463 Dokumente, 14.610 Vektoren, keine ausstehenden Embeddings. Sein Report liegt unter `/Users/dh/.codex/automations/update-qmd-index-daily/runs/20261003T081624-75973/report.json`.

Die aktuellen Review-Identitäten, Git-Auslieferung, Worktree-Bereinigung und der zusätzliche manuelle QMD-Lauf mit korrigiertem Runner werden außerhalb des Indexes in `/Users/dh/.local/state/contextual-llm-wiki/backups/compiler-cleanup-20261002/delivery-main.json` festgehalten. Der manuelle Lauf erhält das eigene Report-Verzeichnis `/Users/dh/.codex/automations/update-qmd-index-daily/runs/20261003-wiki-main-final`. Die Automationsdefinition und ihr täglicher 07:00-Zeitplan bleiben erhalten.
