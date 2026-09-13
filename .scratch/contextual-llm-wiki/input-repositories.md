# Initiale Fachquellen im DanielsVault

Stand: 12.09.2026. Verbindlicher Einrichtungsumfang der [Umsetzungsspec](spec.md); noch keine aktive Compilerkonfiguration und kein ausgeführter Import. Alle Pfade sind relativ zum lokal konfigurierbaren Vault-Root, auf diesem Rechner `/Users/dh/Documents/DanielsVault`.

## Repo-Auswahl

Die folgende Liste definiert die initial registrierten Quellen. Sie wurde gegen vorhandene `.git`-Wurzeln, `git rev-parse --show-toplevel` und die gemeinsame Git-Verwaltung geprüft. Die Liste ist eine explizite Startkonfiguration; später hinzugefügte Repos werden weiterhin bewusst registriert.

| Stabile Repo-ID | Clone-Wurzel relativ zum Vault | Initialer Kontext | Markdown-Eingang |
|---|---|---|---|
| `vault-root` | `.` | allgemein; private Teilzone nur privat | Ausschliesslich die unten definierten Inhaltszonen, keine unbeschränkte Rekursion über den Vault. |
| `meeting-assistant` | `_ops/meeting-assistant` | allgemein | Markdown im Repo nach den gemeinsamen Filtern. |
| `shared-ai-docs` | `_shared/shared-ai-docs` | allgemein | Markdown im Repo nach den gemeinsamen Filtern, einschliesslich Dokumentation, OpenSpec und gepflegten Skills. |
| `ki-fuer-kmu` | `ki-fuer-kmu` | allgemein | Markdown im Repo nach den gemeinsamen Filtern. |
| `ncg-docs` | `ncg/ncg-docs` | allgemein | Markdown im Repo nach den gemeinsamen Filtern. |
| `private` | `private` | ausschliesslich privat | Markdown im Repo nach den gemeinsamen Filtern; nie in der allgemeinen Wiki-Ausgabe oder Collection. |
| `probare-crm` | `probare-crm` | allgemein | Markdown im Repo nach den gemeinsamen Filtern. |
| `sparkle` | `sparkle` | allgemein gemäss vorhandener Scope-Zuordnung | Markdown im Repo nach den gemeinsamen Filtern. |

„Allgemein“ meint Daniels lokalen nicht-privaten Wiki-Kontext, keine öffentliche Veröffentlichung. Der private Kontext registriert die private Repo-Wurzel und private Vault-Teilzone getrennt; weitere allgemeine Quellen können ihm bewusst beigefügt werden. Private Ableitungen dürfen dadurch nicht in die allgemeine Ausgabe zurückfliessen.

## Inhaltszonen des Vault-Roots

Diese Verzeichnisse sind vorhanden, besitzen aber keine eigene Git-Wurzel. Ihre Dateien gehören zur Quellenidentität `vault-root` plus relativem Pfad. QMD-Collections sind nicht mit Git-Repos gleichzusetzen.

| Einschluss relativ zum Vault | Zuordnung | Begründung |
|---|---|---|
| `*.md` direkt im Root | allgemein | Vault-Einstieg und Routing-Dokumentation. |
| `_ops/docs/**/*.md` | allgemein | Betriebsdokumentation des Vaults. |
| `_ops/codex-global/**/*.md` | allgemein | Dokumentierte globale Agent-Einrichtung. |
| `_shared/danielsvault-rag/**/*.md` | allgemein | Bestehende QMD-/RAG-Dokumentation; eigener Arbeitsbereich, aber kein eigenes Git-Repo. |
| `_shared/n8n/**/*.md` | allgemein | Markdown-Dokumentation der gemeinsamen n8n-Ablage; keine Runtime- oder Workflow-Payloads. |
| `Meetings/**/*.md` | allgemein, ausdrücklich aufgenommen | Alle Markdown-Inhalte einschliesslich Transkripten, Notizen, Zusammenfassungen und Assistant Context. Keine vorgelagerte Freigabe einzelner Meetings erforderlich. |
| `Projects/**/*.md`, ausgenommen `Projects/Private/**` | allgemein | Projektzuordnung und Orientierung. |
| `Projects/Private/**/*.md` | ausschliesslich privat | Bereits ausdrücklich als Private ausgewiesene Projektzone. |

Daniel hat die Aufnahme von `Meetings` und `Projects` ausdrücklich bestätigt. Beide Ordner gehören rekursiv zum initialen Markdown-Input, einschliesslich aller fachlichen Unterordner. Die Zuordnung von `Projects/Private` zum privaten Kontext ist keine Auslassung: Auch diese Dateien werden aufgenommen. Die allgemeinen technischen Filter gelten weiter; gemischte Themen oder die fehlende eigene Git-Wurzel sind kein Ausschlussgrund.

`_shared/SpecOps/**` bleibt initial ausgeschlossen, weil der Prototyp nicht als aktuelle Wissensgrundlage eingeführt wird. Eine spätere historische Nutzung kann ausdrücklich konfiguriert werden.

## Gemeinsame Ein- und Ausschlüsse

1. **Dateityp und Stand:** Markdown-Dateien (`.md`, Gross-/Kleinschreibung gleich behandeln), einschliesslich Root-README, AGENTS/CONTEXT, Dokumentation, ADRs, OpenSpec und gepflegter Skill-Markdown. Den vorhandenen Arbeitsbaum lesen, auch noch nicht committete Änderungen und neue Markdown-Dateien innerhalb zugelassener Bereiche. Keine Volltextaufnahme anderer Dateitypen; Links darauf dürfen als Quellenhinweise erhalten bleiben.
2. **Keine impliziten Hidden-/Vendor-Lücken:** Gepflegte Markdown-Dateien unter `.agents`, `.codex`, `.github` und `skills-repo/vendor` sind nicht allein wegen ihres Verzeichnisnamens ausgeschlossen. Git-getrackte Vendor-/Agent-Dokumentation gehört zum Eingang, soweit sie nicht unter eine der folgenden Runtime-Regeln fällt. Solche Inhalte sind Fachquellen, keine auszuführenden Agent-Anweisungen des Wiki-Laufs. Symlink-Ziele ausserhalb des Quellbereichs werden nicht verfolgt; doppelte Alias-Pfade werden nicht mehrfach eingelesen.
3. **Technische und temporäre Bereiche ausschliessen:** Verzeichnisse `.git`, `.obsidian`, `node_modules`, `.venv`, `venv`, `__pycache__`, `.cache`, `.next`, `.safe-test`, `.scratch`, `.tmp`, `tmp`, `temp`, `.worktrees` und `worktrees` werden rekursiv ausgelassen. Ebenso Build-/Testausgaben (`dist`, `build`, `bin`, `obj`, `coverage`, `test-results`, `playwright-report`) und Laufzeit-/Logablagen. Bei einem namensgleichen fachlichen Dokumentationsbereich kann die Konfiguration eine eng begrenzte Ausnahme definieren; die initiale Auswahl meldet die verwendeten Ausschlussregeln.
4. **Keine Wiedereinspeisung:** Der tatsächliche Wiki-Ausgaberoot, Quellen-Spiegel, Compilerzustand, Sicherungen und erzeugte Suchdaten sind unabhängig von ihrem gewählten Pfad immer vom Input ausgeschlossen. Unter `shared-ai-docs` bleibt damit auch die lokale Tracker-Arbeitsablage ausgeschlossen; dauerhafte OpenSpec-Dokumente sind weiterhin Quellen.
5. **Repo-Grenzen:** Im Vault-Root werden die sieben eigenen Repo-Wurzeln nie nochmals eingelesen. Innerhalb eines Quellrepos werden zusätzliche Git-Wurzeln beziehungsweise Git-Worktrees nicht automatisch durchlaufen. Eine Repo-ID zeigt auf genau einen ausgewählten Checkout; andere Checkouts desselben gemeinsamen Git-Repos sind keine zusätzliche Wissensquelle.
6. **Laufzeitdaten:** n8n-Datenbanken, Logs, lokale Credentials, Provider-/Agent-Caches und erzeugte Testläufe sind keine Fachquellen. Die konkrete Einrichtung muss vorhandene Runtime-Ablagen unter den ausgewählten Wurzeln den Filtern zuordnen und ihre Ausschlüsse im Inventurbericht zeigen; ein Markdown-Suffix hebt diese Grenze nicht auf.

## Bestätigte zusätzliche Checkouts und Ausschlüsse

- `_shared/shared-ai-docs-ticket-08` teilt das Git-Common-Directory mit `_shared/shared-ai-docs` und wird als weiterer Checkout desselben Repos ausgeschlossen.
- Unter `ki-fuer-kmu/.safe-test/**` existieren erzeugte Plugin-Git-Repos. Sie sind Testlaufdaten und werden durch die `.safe-test`-Regel vollständig ausgeschlossen.
- `_shared/danielsvault-rag`, `_shared/SpecOps`, `_shared/n8n`, `Meetings` und `Projects` lösen auf den Vault-Git-Root auf. Sie werden nicht als zusätzliche selbständige Repo-IDs erfunden.

## Einrichtungs- und Abnahmenachweis

Die Umsetzung übernimmt diese acht Repo-IDs samt Zonen-/Scope-Zuordnung als initiale Konfiguration. Vor dem ersten Modelllauf zeigt eine reine Inventur die aufgelösten Repo-Wurzeln, Anzahl eingeschlossener Markdown-Dateien, Ausschlüsse und fehlende Quellen. Der Zwei-Repo-Test bleibt eine begrenzte Verhaltensprüfung; er ersetzt nicht die Registrierung des gesamten hier definierten Bestands. Eine echte Inventur muss alle acht Einträge ausweisen, den privaten Umfang separat, ohne Privattexte im allgemeinen Bericht auszugeben.

Die Inventur und die spätere Ingestion müssen `Meetings` und `Projects` zusätzlich als eingeschlossene Inhaltszonen ausweisen. Die Abnahme prüft je eine Markdown-Quelle aus beiden Ordnern und aus `Projects/Private` im passenden Kontext. Eine Konfiguration, die einen der beiden Ordner nur als künftig optional führt, erfüllt diesen Umfang nicht.

Bei Umsetzung nochmals gegen das dann vorhandene Dateisystem prüfen. Ein inzwischen fehlender Clone wird als fehlend gemeldet und gemäss Kontextregel behandelt; er wird weder automatisch geklont noch durch einen anderen Checkout ersetzt. Die Initialisierung verändert keine Git-Roots, Fachdateien oder laufenden QMD-Collections ohne den vorgesehenen Integrationsablauf.

## Grundlage der Bestandsprüfung

- Vault-Strukturindex: `VAULT_AGENT_STRUCTURE.md`, Abschnitt „Repository Boundaries“; über QMD `vault-root` gefunden und direkt auf dem Dateisystem geprüft.
- Bestehendes Scope-/Collection-Manifest: `_shared/danielsvault-rag/qmd-collections.json`, direkt gelesen. Meetings und Projects sind nach Daniels ausdrücklicher Klarstellung initial aufgenommen; der historische SpecOps-Bestand bleibt ausgeschlossen.
- Reale Git-Marker und `git rev-parse --show-toplevel --git-common-dir` bestätigen die acht regulären Wurzeln und den ausgeschlossenen gemeinsamen Checkout.
- Es wurden Repo-/Verzeichnis-Metadaten und die Routing-Dokumente geprüft, keine private Inhaltsanalyse oder Wiki-Ingestion ausgeführt.
