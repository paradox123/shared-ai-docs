# CodeGraph vs. `rg`: Tool-Routing für den NCG-Quellbestand

Stand: 2026-09-10 · Untersuchungsumfang: `care-api`, `pimcore`, `ncg-frontend`, `ncg-backend/backend` und `ncg-security-token`. Es wurden keine Indizes oder Konfigurationen angelegt oder geändert.

## Entscheidung

**CodeGraph ersetzt `rg` nicht vollständig.** Es soll `rg` als Standard für die *strukturelle Navigation von indexiertem Programmcode* ersetzen: Symbolsuche, Aufrufpfade, Caller/Callee, Impact und das Lesen des dabei relevanten Quellcodes. `rg` bleibt ein bewusst enger Fallback für exakte Text-, Regex- und Pfadsuchen in nicht oder nur oberflächlich indexierten Dateien. QMD bleibt der Retriever für Markdown, Wiki und Dokumentation.

Das ist keine vorsichtige Annahme, sondern die von CodeGraph selbst dokumentierte Grenze: Sein MCP-Playbook verlangt `codegraph_explore` vor Read/Grep für indexierten Code, nennt aber ausdrücklich Konfiguration und Dokumente als Fälle für Raw Read/Grep. Die Auflösung über Dateien hinweg ist zudem best-effort und keine Laufzeitvalidierung. [CodeGraph MCP-Instruktionen](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/src/mcp/server-instructions.ts#L34-L76)

## Befund: Was der NCG-Bestand tatsächlich enthält

Die folgenden Zahlen sind ein lokaler, reproduzierbarer Inventur-Snapshot: `git -C <repo> ls-files` über die fünf genannten Git-Wurzeln. Sie beschreiben getrackte Dateien, nicht die spätere Größe eines CodeGraph-Index. Die Quellwurzeln sind [`care-api`](/Users/dh/Documents/Dev/NCG/care-api), [`pimcore`](/Users/dh/Documents/Dev/NCG/pimcore), [`ncg-frontend`](/Users/dh/Documents/Dev/NCG/ncg-frontend), [`backend`](/Users/dh/Documents/Dev/NCG/ncg-backend/backend) und [`ncg-security-token`](/Users/dh/Documents/Dev/NCG/ncg-security-token).

| Inhalt | Lokale Menge | CodeGraph-Abdeckung | Richtiger Standardweg |
|---|---:|---|---|
| C# (`.cs`), Java (`.java`), PHP (`.php`), JavaScript (`.js`), TypeScript (`.ts`) | 4.914 / 203 / 4.522 / 3.764 / 2.210 | Volle Sprachunterstützung für diese Kernsprachen; `codegraph_explore` liefert Symbolquelltext, Beziehungen und Blast Radius. [Sprachliste](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/site/src/content/docs/reference/languages.md#L6-L33), [MCP-Verhalten](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/site/src/content/docs/reference/mcp-server.md#L14-L46) | **CodeGraph zuerst** |
| Razor (`.cshtml`: 113) | 113 | Eigener Extractor verbindet `@model`, `@inject` und Komponenten mit C#-Typen. [Extension-/Extractor-Zuordnung](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/src/extraction/grammars.ts#L87-L102) | **CodeGraph zuerst**, bei markup-spezifischen Details direkte Datei-Lektüre |
| Twig (`.twig`: 53) | 53 | Nur Datei-Tracking, keine Symbol-Extraktion. [Extension-Zuordnung](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/src/extraction/grammars.ts#L98-L102) | Bekannte Datei: **direkt lesen**; unbekannter String/Pfad: **`rg`** |
| JSON | 921 | Allgemeines JSON ist nicht in der Extension-Map. Die einzige JSON-Ausnahme sind Shopify-`templates/`/`sections/`; im lokalen Bestand trifft sie auf 0 getrackte JSON-Dateien zu. [CodeGraph-Selector](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/src/extraction/grammars.ts#L175-L202) | Bekannte Datei: **direkt lesen**; Suche nach Route, Key oder Literal: **`rg`** |
| YAML (`.yml`/`.yaml`: 93) | 93 | Datei-Level-Tracking, **keine** Symbol-Extraktion. [CodeGraph-Selector](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/src/extraction/grammars.ts#L98-L100) | **`rg`** für Discovery; danach direkt lesen |
| XML (`.xml`: 14), `.properties`: 2 | 16 | XML ist Datei-Level; nur MyBatis-Mapper erzeugen SQL-Knoten. Properties erzeugen Leaf-Key-Knoten für Spring-`@Value`-Referenzen. [XML/Properties-Implementierung](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/src/extraction/grammars.ts#L144-L168) | XML/Projektdateien: **`rg`**; Spring-Property-Beziehung: CodeGraph kann helfen |
| `.csproj`: 98, `.sln`: 3, Shell: 77, extensionlose Dateien: 200 | 378 | Nicht in CodeGraphs allgemeiner Extension-Map; ein paar fremdsprachenspezifische Ausnahmen ändern nichts an dieser NCG-Klasse. [Selector-Regel](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/src/extraction/grammars.ts#L175-L191) | Bekannte Datei: **direkt lesen**; Discovery bzw. Regex: **`rg`** |
| Build-/Vendor-/Cache-Bäume | 8.444 getrackte Pfade unter u. a. `node_modules`, `vendor`, `dist`, `build`, `bin`, `obj`, `target` | Standardmäßig aus dem Graph ausgeschlossen; ebenso gitignorierte Dateien und Dateien über 1 MB. [CodeGraph-Indexregeln](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/site/src/content/docs/getting-started/configuration.md#L8-L18) | Nicht normal durchsuchen; nur bei explizitem Bedarf, eng begrenzt |

**Folgerung:** Die Aussage „CodeGraph kann alles, was `rg` kann, besser“ ist für die erste Zeile zutreffend, für die übrigen nicht. CodeGraph ist ein vorab berechneter Symbol- und Beziehungsindex, kein allgemeiner Literal-/Regex-Index für den gesamten Textbestand. `rg` durchsucht hingegen zeilenorientiert beliebige Textdateien per Literal oder Regex und kann Pfade per Glob begrenzen. [ripgrep-Grundmodell](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/GUIDE.md#L67-L155), [Globs und Dateitypen](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/GUIDE.md#L258-L420)

## Dauerhafte Routing-Regel für Agents

| Absicht | Werkzeug | Präzise Regel |
|---|---|---|
| „Wo ist Symbol X?“, „Wer ruft X?“, „Wie erreicht Service A B?“, Architektur, gemeinsame Bibliothek, Änderungsfolgen | **CodeGraph** | Zuerst `codegraph_explore` im richtigen, aktuellen NCG-Index. Nicht parallel mit `rg` bestätigen, sofern der relevante Code indexiert und frisch ist. |
| Wiki, Markdown, ADR, Spec, Runbook, Meeting- oder Vault-Wissen | **QMD** | QMD bleibt der Suchweg für DanielsVault- und Markdown-Wissen; CodeGraph ist kein Ersatz dafür. |
| Bekannte Konfigurations-, Build-, XML-, JSON-, YAML-, Shell- oder sonstige nicht indexierte Datei | **Direktes Datei-Lesen** | Es gibt nichts mehr zu entdecken; die Datei gezielt öffnen. |
| Unbekannte Stelle für einen Key, eine URL, einen Ocelot-/DI-/Docker-/CI-Wert, eine Fehlermeldung oder ein Regex-Muster | **`rg`** | Nur auf die passende(n) Quelle(n) und Dateiglob(s) begrenzen; dann die Treffer direkt lesen. Keine breite Suche über Geheimnis- oder Zertifikatspfade. |
| Index fehlt, CodeGraph meldet Staleness oder die Quelle wurde gerade verändert | **Direktes Datei-Lesen**, danach bei Discovery ggf. `rg` | CodeGraph selbst fordert für die konkret als stale gemeldete Datei Read. [Freshness-Verhalten](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/site/src/content/docs/guides/indexing.md#L25-L87) |
| Korrektheit, Compilerfehler, Tests, Lint oder Laufzeitverhalten | **Build/Test/Linter** | Weder CodeGraph noch `rg` validieren Verhalten. CodeGraphs eigene Limitation nennt Compiler/Test/Linter als zuständig. [Limitation](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/src/mcp/server-instructions.ts#L71-L76) |

`rg` hat dabei echte Zusatzfähigkeiten, die nicht Teil des CodeGraph-Graphen sind: Multiline-/PCRE2-Regex, beliebige Globs, nicht-UTF-8-Text, optionale Binär-/komprimierte Dateisuche und Preprocessor. Das rechtfertigt den Fallback, aber nicht seine Nutzung zur üblichen Code-Navigation. [ripgrep-Funktionsumfang](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/README.md#L122-L155), [weitere Optionen](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/GUIDE.md#L988-L1025)

## Index-Topologie und Sicherheitsgrenzen

**Fakt:** CodeGraph speichert den Index projektweise in `<Projekt>/.codegraph/codegraph.db`; sein MCP kann verschiedene Projekte mit `projectPath` abfragen. Es dokumentiert auch die Indexierung verschachtelter Git-Repositories in einem „super-repo“-Layout. [Projektindex](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/site/src/content/docs/getting-started/configuration.md#L73-L97), [Mehrprojekt-MCP](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/src/mcp/server-instructions.ts#L91-L109)

**Inference:** Für echte graphbasierte Beziehungen *zwischen* NCG-Repositories ist ein gemeinsamer, kontrollierter NCG-Root-Index nötig; getrennte Einzelindizes können in einer einzelnen Graphabfrage keine repoübergreifenden Kanten bilden. `/Users/dh/Documents/Dev/NCG` ist derzeit selbst kein Git-Root und hat keine Root-`.gitignore`; deshalb darf die automatische Erkennung der Child-Repositories nicht einfach vorausgesetzt werden. Vor einem Rollout muss `codegraph_status` bestätigen, dass genau die fünf in Scope befindlichen Repositories erfasst sind.

Ein gemeinsamer Index darf **nicht** pauschal den ganzen NCG-Ordner einschließen. Vor dem Init wären mindestens `.worktrees/`, `ncg-certs/`, `ncg-keys/`, alle `**/secrets/**`, `**/certs/**`, `.env*` sowie Schlüssel-/Zertifikatsformate explizit auszuschließen. CodeGraphs `exclude`-Patterns gelten auch für getrackte Dateien und für Full-Index, Sync und Watcher. [Exclude-Semantik](https://github.com/colbymchenry/codegraph/blob/3ed73bc127323e63153bf6ec8354afa82ce36aaf/site/src/content/docs/getting-started/configuration.md#L20-L32)

## Abnahmekriterien für den späteren Pilot

1. `codegraph_status` zeigt nur die erlaubten Quellwurzeln, keine Pending-Sync-Dateien und plausible Datei-/Knoten-Zahlen.
2. Je ein repräsentativer gemeinsamer Typ, ein Frontend-API-Einstieg und ein Backend-Servicepfad lassen sich mit `codegraph_explore` nachvollziehen. Statische Unklarheiten bzw. HTTP-/Konfigurationsgrenzen werden als solche markiert, nicht erfunden.
3. Ein bekannter JSON- oder Ocelot-/CI-Konfigurationskey wird gezielt mit `rg` gefunden und direkt gelesen. Das bestätigt den absichtlichen Fallback.
4. Ein Edit an einer indexierten Datei erzeugt entweder einen frischen Graph-Treffer oder die dokumentierte Staleness-Warnung; im zweiten Fall liest der Agent genau diese Datei direkt.

Erst wenn diese vier Checks bestehen, ist die Agentenregel belastbar: **CodeGraph zuerst für indexierten Programmcode; QMD für Markdown/Wissen; direkte Reads für bekannte unindexierte oder stale Dateien; `rg` nur für präzise Text-/Regex-/Pfad-Discovery außerhalb des CodeGraph-Scope.**
