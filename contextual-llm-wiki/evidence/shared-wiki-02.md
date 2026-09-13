# Ticket 02: Wissensbestände verlustfrei zusammenführen

Implementierung auf `codex/shared-wiki-02`, im von Daniel bestätigten isolierten Worktree. Owning Repository: `_shared/shared-ai-docs`; Basis ist der akzeptierte Ticket-01-Commit `1c13f089b559441e887a124c7ee63c41c568610f`. Der bereits laufende Change `operate-contextual-llm-wiki`, Aufgabe 4.2, ist zuständig. `main` und die parallelen Änderungen dort wurden nicht bearbeitet.

## Reale Abnahme am 13.09.2026

Die neue CLI hat sechs tatsächliche Eingänge inventarisiert und **211 Dateien** mit SHA-256-Prüfsummen gesichert. Die beiden Produktionsausgaben `general` und `private` sind noch nicht vorhanden. Der allgemeine Abnahmebestand enthält 22 Seiten einschließlich einer gespeicherten Antwort, der persönliche acht Konzeptseiten. Zwei ältere Backups enthalten jeweils 27 Seiten einschließlich zweier Antworten. Damit werden aktuelle Bestände und historische Abnahmezahlen ausdrücklich unterschieden.

Die Migration hat **30 gültige Seiten** übernommen, **36 identische historische Revisionen** denselben Zielseiten zugeordnet und **18 veraltete Revisionen** zurückgestellt. Das gemeinsame Ziel enthält **eine gespeicherte Antwort und acht Seiten aus `Projects/Private`**. Die nur noch in alten Backups vorhandene `answers/qmd-synthese` hängt von einer inzwischen geänderten Quelle ab: Sie bleibt samt ihrer damaligen Abhängigkeiten im verifizierten Snapshot, wird aber nicht als aktuelles Wissen veröffentlicht. Sie wurde weder gelöscht noch durch einen neu erzeugten Text ersetzt.

Die echte Abfrage über `codex-agent` hat ausschließlich die importierte `answers/qmd-gemeinsame-erkenntnis` als Evidenz ausgewählt, `fallback:false`. Ihr Hash ist vor und nach der Übernahme identisch: `b1b27a7075cc69c7a50e7eeff1cbe7d295cc99b744116b2085ce8393720266be`. Die Antwort beschreibt die dokumentierte Rolle von QMD als einziger persistierter Retrieval-Engine und führt ihre Originalquellen mit. Die unveränderte historische Formulierung beschreibt den jeweiligen QMD/RAG-Quellstand; daraus wird keine Privatpartition der gemeinsamen Wiki-Collection abgeleitet. Die Suche nach dem persönlichen Bereich liefert alle acht übernommenen Seiten.

[Maschinenlesbare Zusammenfassung](migration-real-summary.json) mit Herkunft, Prüfsummen, Mengen, echter Query-Evidenz, No-op und Lint. Aktive Linkprüfung, Quellen-/Seitenprüfung und Suche bestehen. Alle 211 bisherigen Eingangsdateien und die verwendeten Originalquellen sind nach dem Lauf unverändert. Sowohl erneute Migration desselben Snapshots als auch unveränderte Pflege melden `noop:true`.

## Kriterienweise Abnahme

| Kriterium | Erwartung | Beobachtung und Beleg |
|---|---|---|
| Tatsächliche Inventur | Leere Produktion, befüllte Ausgaben, alte Antworten und Abhängigkeiten unterscheiden. | Sechs Eingänge mit 0/0/22/8/27/27 Seiten; gespeicherte Antworten und Versionen einzeln erfasst. Reale Zusammenfassung; CLI-Test „migration inventory distinguishes …“. |
| Überprüfbare Sicherung | Texte und erforderlichen Zustand vor Ablösung erhalten. | 211 Snapshot-Dateien, null Hashabweichungen; Originalausgaben/Backups unverändert. Compilerzustand und unverwaltete Notizen werden mitgesichert. Reale Zusammenfassung und Inventurtest. |
| Gültige Antworten übernehmen | Einzigartige Texte auffindbar und auf Originale zurückführbar erhalten. | Aktuelle echte Antwort bytegleich, echte verwaltete Query verwendet genau diese Antwort ohne Fallback. Zusätzlicher Test prüft ausdrücklich eine einzigartige Gesprächsformulierung. |
| Antwortabhängigkeiten | Konzept → Antwort → Folgeantwort gültig überführen. | CLI-Test „migration preserves unique answer text …“ prüft umgesetzte Versionsreferenzen, zwei statt vier aktiver Antworten aus Ausgabe plus Backup, Query und Lint. |
| Namenskollisionen | Verschiedene Aussagen/Quellen nicht überschreiben. | Zwei alte `concepts/freigabe` und `answers/entscheidung` bleiben getrennt und jeweils nur ihrem Originalrepo zugeordnet. Gegenseitige Navigationslinks zeigen auf die übernommenen Revisionen. |
| Ungültige Altstände | Nicht als aktuelles Wissen veröffentlichen, Gründe und Originalbytes erhalten. | Real 18 zurückgestellte Revisionen wegen geänderter Quelle. Tests prüfen manipulierte Seiten, transitive Beleglücken, defektes JSON und Null-Datensätze; historische Links zeigen ausdrücklich auf den Snapshot. |
| Nachpflege | Quellenänderung erreicht abhängige Antwortkette; unabhängige Antwort bleibt stabil. | Echte Compiler-CLI mit deterministischem HTTP-Provider: Alpha von zwei auf vier Freigaben korrigiert, importiertes Konzept und beide Antworten enthalten vier; Beta-Antwort bytegleich. Vor Pflege wird Alpha-Evidenz durch die Query zurückgewiesen. |
| Wiederholbarkeit | Fehler/Unterbrechung ohne Duplikate oder Verlust wiederaufnehmen. | Tests für QMD-Ausfall mit späterer Quellenänderung, reine Indexwiederholung ohne Modell, Quelländerung während Veröffentlichung und beschädigten Snapshot. Reale Vorbereitung nach SIGTERM aus demselben Snapshot wiederaufgenommen, Migration und Pflege danach No-op. |
| Gemeinsames QMD | Persönliche Inhalte auffindbar, fremde Collections unverändert. | Reale gemeinsame Collection liefert alle acht persönlichen Seiten. Separater QMD-Abnahmedatenbestand; öffentlicher CLI-Test bestätigt unveränderte Pfade, Hashes und Texte einer fremden Collection nach Import in derselben Testdatenbank. |

Alle genannten Verhaltenstests stehen in [migration.test.ts](../test/migration.test.ts). Compiler und QMD sind dabei echt; ausschließlich die Providerantworten der deterministischen Tests werden an der HTTP-Grenze ersetzt. Die reale Query nutzt den vorhandenen angemeldeten Codex-Provider.

## Lokale Laufartefakte und Betrieb

- Konfiguration: `contextual-llm-wiki/.local/migration-real.json` im Ticket-02-Worktree.
- Ziel: `/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/migration-ticket-02/wiki`.
- Snapshot: `/Users/dh/.local/state/contextual-llm-wiki/backups/migration-ticket-02-20260913`, einschließlich `manifest.json`, `inputs/0` bis `inputs/5` und gesichertem anfänglichen Zielzustand.
- Rohe Inventur, Migrationsbericht, Query, Suche, Status, Lint, No-op und Wiederholung: `.local/migration-*.json` im Wiki-Projekt. Sie bleiben lokal; die versionierte Zusammenfassung enthält keine kopierten Fachtexte.
- Wiederaufnahme: `./wiki migrate --config .local/migration-real.json --snapshot /Users/dh/.local/state/contextual-llm-wiki/backups/migration-ticket-02-20260913`.

Der erste Vorbereitungsversuch startete eine unnötige Kompilierung aller fünf ausgewählten Quellen. Er wurde nach fertiger Sicherung beendet. Ein anschließender Rot→Grün-Test entkoppelte die frische Migration vom Vollimport; die erfolgreiche Wiederaufnahme erhält die vorhandenen Texte ohne Modellkompilierung. Weitere Quellen außerhalb gültiger Importe bleiben in `status.changes.added` für die spätere Erstpflege sichtbar. Ein bereits befülltes Ziel wird bei Bedarf regulär abgeglichen.

Die Quellenkorrektur wurde gezielt in Testrepos geprüft; reale Fachdateien wurden nicht für Abnahmeänderungen bearbeitet. Der reale Lauf prüft echte Bestandsübernahme, Quellenherkunft, Query, QMD und Wiederholung. Dieser Nachweis ist kein Vollimport des DanielsVault und keine produktive Aktivierung. Tickets 03 und 04 sowie der bestehende Live-Job bleiben separat; der Gesamtchange wird nicht archiviert.

## Review und Prüfungen

Die beiden unabhängigen Reviewachsen bezogen sich auf den festen Ticket-01-Ausgangscommit. Das Standards-Review fand einen Navigationsrandfall und eine optionale Aufteilungsempfehlung; das Spec-Review fand den Umgang mit defekten Metadaten. Beide Verhaltensfehler wurden zunächst über die öffentliche CLI reproduziert und behoben. Inventur, Snapshot, reine Importplanung und Schreibablauf sind getrennt. Die anschließende Spec-Nachprüfung fand außerdem eine Veränderung von Markdown-Codebeispielen; Syntaxbaumpositionen schützen nun Codeblöcke und Inline-Code, und eine wörtliche Callback-Ersetzung erhält auch `$&`, `$$` und ähnliche Zeichenfolgen. Der entsprechende öffentliche CLI-Test wurde jeweils vor der Korrektur rot und anschließend grün. Standards- und Spec-Nachprüfung bestätigen am Code-Commit `4f36f66` jeweils **null offene Findings**.

[Abschließende Prüfausgabe](migration-verification.txt): TypeScript, 48 öffentliche CLI-Tests einschließlich 14 Migrationsfällen, 59 relevante Upstream-Tests und sechs Betriebshelfertests. Alle Tests und TypeScript sind bestanden. Strikte OpenSpec-Validierung und `git diff --check` sind ebenfalls erfolgreich.
