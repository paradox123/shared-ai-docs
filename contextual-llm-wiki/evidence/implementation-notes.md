# Integrationsentscheidungen und TDD-Nachweise

Der Entwicklungs-Worktree liegt außerhalb des Vaults. 13 aktuelle Spezifikationsdateien wurden bytegleich kopiert. Der ursprüngliche Git-Zustand ist separat zur Abschlussprüfung gesichert; sachfremde Änderungen wurden nicht übernommen.

Die öffentliche CLI ist die Testgrenze. `node --test test/*.test.ts` startet sie als eigene Prozesse. Der echte Compiler läuft am festgelegten Commit; ausschließlich seine HTTP-Providergrenze wird deterministisch bedient. Rot→Grün bislang: fehlender Providerbericht; Zwei-Repo-Compile; rekursive Inventur mit versteckten Dokumenten und Ausschlüssen; Quellenkorrektur/Status; Completion-Preflight; QMD/Save.

SDK-Eingriff: `completeText({system,prompt,maxTokens})` nutzt die bestehende Provider- und Retrylogik ohne Retrieval oder Speicherung. Der Provider-Guard berücksichtigt nun den bereits vorhandenen Compile-Schalter `embeddings:false`, auch bei Codex. Native Query, Refresh und Remove mit Embedding-Nebenwirkungen werden nicht aufgerufen. Der Patch verändert weder Compilerprompts noch Wissensextraktion und Seitengenerierung.

Quellen sind echte rekursive Dateien unter `sources/<repo-id>/<relativer-pfad>`; Inhalt und Zeilenzählung bleiben unverändert. Dieser vom Compiler unterstützte Dateipfad umgeht die begrenzte ingestText-Konvertierung ohne Abschneiden. Source-Ownership wird am gepinnten Format aus `.llmwiki/state.json` gelesen. Aktive Markdown-Dateien erhalten Originalbelege; Metadaten und Spiegel liegen außerhalb der aktiven QMD-Collection.

QMD: Die bestehende zuständige Reconciliation kann über `QMD_COLLECTION_MANIFEST` ein ausschließlich Wiki-eigenes Manifest lesen. Daher ist kein Eingriff in das andere Repository notwendig. Der QMD-SDK-Aufruf `update({collections:[name]})` aktualisiert nur diese Collection und führt keine fremden Update-Kommandos aus. Deterministische Tests verwenden echte, isolierte QMD-Datenbanken; der Vault-Betrieb verwendet den vorhandenen QMD-Index. Embeddings bleiben optional innerhalb QMD; BM25-Retrieval ist bereits voll funktionsfähig.

## Abschließende Integrationslücken und Verifikation

Der echte Codex-Lauf hat gezeigt, dass sein striktes Structured-Output-Schema für jedes Objekt `additionalProperties:false` und vollständige `required`-Listen verlangt. Der Compiler verwendete bislang sein unverändertes Tool-Schema. Ein neuer Upstream-Test an der tatsächlichen Codex-Prozessgrenze reproduziert den Fehler; die Normalisierung erfolgt ausschließlich im Codex-Provideradapter. Die originale fachliche Schema-Validierung bleibt erhalten. Der Patch berücksichtigt außerdem `.MD` ebenso wie `.md` im unterstützten Source-Dateipfad; der öffentliche Integrationstest deckt diesen Fall ab.

Die Rohgenerierung erzeugte 127 Wiki-Linkvorschläge ohne vorhandenes Ziel. Die aktive Veröffentlichung löst bekannte IDs/Titel in relative Markdown-Links auf und belässt unbekannte Begriffe als Klartext. Sie erfindet keine Zielseiten. Originalbelege verwenden die Obsidian-URI auf die unveränderte Quelldatei; Zeilenspannen stehen im Label. Gespeicherte Synthesen verlinken ihre Seitenbelege und Originalquellen ebenfalls. Rohcompiler-Lint und aktive Linkprüfung bleiben getrennt sichtbar.

QMDs vollständige lexikalische Frage lieferte bei natürlichen Sätzen zunächst keine Treffer. Der Anschluss sucht bei fehlendem Volltreffer zusätzlich begrenzte Fragebegriffe über dieselbe QMD-Engine. Ein Verhaltenstest zeigte zuerst den unerwünschten Quellen-Fallback und besteht nach dieser Änderung. Der echte Folgedialog verwendet die gespeicherte gemeinsame Synthese als ersten Treffer.

Weitere Rot→Grün-Slices decken die Quelle–Konzept–Antwort–Antwort-Kette, physischen Kontextentzug, Rückkehr, privaten Scope, unterbrochene Schreiber, Provider-/Scan-/Indexfehler, unveränderte Indexwiederholung, laufende Quellen-/Konfigurationsänderungen, Save-Provenienz sowie Backup/Restore ab. Die Abschlussprüfung ergänzte vier zunächst fehlschlagende Fälle: unabhängige gespeicherte Seitenänderung invalidiert Folgeantworten; indirekte Save-Zyklen werden abgewiesen; Restore prüft Provider vor Inhaltsmutation; verschachtelte Output-Symlinks dürfen Schreibzugriffe nicht in Originalrepos umleiten.

## DRY, SOLID und KISS

Quelleninventur, Zustandsprüfung, Veröffentlichung, Providercompletion und QMD-Prozessgrenze sind getrennte Module. Maintain und Query/Save verwenden dieselben Hash-, Provenienz- und Rendering-Helfer. Der Compilerzustand wird am dokumentierten Pin gelesen; eine alternative Wissensextraktion wurde nicht gebaut. Die Compiler-Baseline wird aus einem fertig vorbereiteten Staging-Verzeichnis übernommen, statt eine teilweise kopierte Baseline als abgeschlossen zu behandeln. Gespeicherte Antworten werden in Abhängigkeitsreihenfolge geprüft; ein neuer generischer Workflow- oder Graphdienst wäre für diesen Vertrag unnötig.

Die Formatierung wurde vereinheitlicht und ungenutzte Imports entfernt. Nach den letzten Änderungen: 28 öffentliche Verhaltenstests, 59 relevante Upstream-Tests und TypeScript ohne Fehler. `scripts/verify-upstream.sh` isoliert allein den Claude-Settings-Fallback der Provider-Guard-Tests; der Host hat sonst einen angemeldeten Provider, wodurch deren absichtlicher Negativfall falsch positiv würde. Produktionskonfiguration und Zugangsdaten bleiben unverändert.

Die Abschlussprüfung betrachtet auch die bestehenden Specs; zwei konkrete Szenarien für Seitenversionsänderung/Zyklen und Restore-Preflight präzisieren den vorhandenen Vertrag. Es wurde kein sachfremder Change angelegt. Die Obsidian-Prüfung war zunächst durch den gesperrten Mac blockiert. Nach Daniels Entsperren wurde der echte Klickweg erfolgreich geprüft und mit drei Screenshots belegt. Es waren keine weiteren Codeänderungen erforderlich.
