# Kontextabhängiges LLM-Wiki

Diese lokale CLI verbindet bestehende Markdown-Fachrepos mit Atomicstratas Compiler am Commit `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb`. Sie erzeugt eine gemeinsame Markdown-Wissensschicht, verfolgt Quellen- und Antwortabhängigkeiten und verwendet ausschließlich QMD für persistiertes Retrieval.

Originalrepos werden gelesen, einschließlich nicht committeter Markdown-Änderungen. Die CLI pflegt über `maintain`; auf Daniels Mac ruft die bestehende tägliche QMD-Automation diesen Befehl auf. [Betrieb, Protokolle und manueller Start](OPERATIONS.md). Ein Merge oder eine Query löst selbst keine Pflege aus. Das Wiki erhält keinen eigenen Watcher, Git-Repo oder Cloud-Dienst.

## Einrichtung

Voraussetzungen: npm/Git, das vorhandene QMD mit funktionierender eigener Runtime und ein angemeldeter Codex-/Claude-Zugang oder ein OpenAI-kompatibler Provider. Node 24.16.0 und der Compiler werden lokal installiert:

```bash
cd contextual-llm-wiki
./scripts/bootstrap.sh
export LLMWIKI_PROVIDER=codex-agent
./wiki preflight
./wiki setup
```

`preflight` prüft Runtime, Compiler-Pin und vorhandene Providerkonfiguration ohne Inhaltsänderungen. `setup` führt zusätzlich eine tatsächliche Completion-Anfrage aus. `LLMWIKI_MODEL` ist optional; Zugangsdaten bleiben in der vorhandenen Providerkonfiguration beziehungsweise Umgebung. Alternativen: `claude-agent` oder `openai` mit `OPENAI_API_KEY` und gegebenenfalls `OPENAI_BASE_URL`. Der bei der Abnahme getestete Provider steht in [Evidence](evidence/acceptance.md). Die Compiler-Ausgabe ist standardmäßig deutsch.

Die gemeinsame Produktion verwendet `.local/common.json`. Aktivierungs- und Importstatus: [Ticket 04](evidence/production-04.md). Für einen neuen Bestand (vorhandene Konfiguration nicht überschreiben):

```bash
export DANIELSVAULT_ROOT=/Users/dh/Documents/DanielsVault
mkdir -p .local
./wiki init-config --vault "$DANIELSVAULT_ROOT" \
  --output "$DANIELSVAULT_ROOT/_shared/contextual-llm-wiki/common" > .local/common.json
./wiki inventory --config .local/common.json
```

Die Startkonfiguration registriert die acht Repo-IDs und Quellzonen aus [input-repositories.md](../.scratch/contextual-llm-wiki/input-repositories.md), mit der durch [ADR 0010](../docs/adr/0010-shared-wiki-across-personal-and-professional-domains.md) korrigierten gemeinsamen Auswahl. Meetings, Projects einschließlich Projects/Private und das private Repo gehören zur selben Wissensschicht. Die Inventur liefert `repositories` mit Identität, Originalroot, Anzahl, Zonen und Ausschlüssen für alle acht Einträge.

`include` und `exclude` sind rekursive Markdown-Globs, unabhängig von der Groß-/Kleinschreibung. Neue Repos werden explizit konfiguriert. Frühere repo-interne `scope`-Labels sind keine Zugriffsgrenze; `privateInclude` ergänzt die Einschlussmuster, explizite Ausschlüsse gelten weiter. Neue Konfigurationen benötigen diese Altattribute nicht. `scope: common` bezeichnet den gemeinsamen Vertrag; alte Top-Level-Scopes `general`/`private` und `init-config --private` werden mit einem Migrationshinweis abgewiesen. Ein fremder oder alter Ausgabezustand kann nicht durch bloßes Umbenennen der Konfiguration übernommen werden.

Die Quelle ist jeweils der konfigurierte Originalcheckout. Zusätzliche Worktrees, verschachtelte Git-Repos, Runtime-Daten und Symlink-Aliase werden ausgelassen. Versteckte Agent-Dokumentation und Vendor-Markdown sind grundsätzlich enthalten. Der Ausgabepfad ist unabhängig von seiner Position vom Eingang ausgeschlossen. Er muss außerhalb getrackter Fachquellen liegen und in einem Git-Arbeitsbaum bereits ignoriert sein; der vorhandene Vault ignoriert `_shared/`.

## Pflege und Abfrage

```bash
./wiki maintain --config .local/common.json
./wiki status --config .local/common.json
./wiki lint --config .local/common.json
./wiki search --config .local/common.json --question 'QMD'
./wiki query --config .local/common.json --question 'Welche Rolle hat QMD?'
./wiki query --config .local/common.json --question 'Welche Rolle hat QMD?' --save qmd-rolle
```

`maintain` inventarisiert vollständig, meldet direkte und indirekte Prüfgründe, zieht ungültige Seiten zurück, kompiliert mit dem echten SDK ohne Embeddings, prüft gespeicherte Antworten und aktualisiert nur die eigene QMD-Collection. Ein unveränderter erfolgreicher Lauf benötigt keine neue Modellarbeit. WikiQuery liefert unter `originals` direkt lesbare Originalpfade und Obsidian-URIs mit geprüftem Hash und Aktualitätsstatus. Kontextfragen beginnen mit dieser Schnittstelle; QMD arbeitet intern.

Die Fachquellen werden vor der Modellarbeit in derselben QMD-Datenbank in `contextual-wiki-<context>-sources` indexiert. Die Collection enthält ausschließlich die vollständig gescannten ausgewählten Originale; ein Versionsmanifest bindet Treffer an aktuelle Originalhashes. Veraltete Wiki-Dateien werden vor der Indexpflege zurückgezogen. Ein unvollständiger Scan verändert den Quellenindex nicht. Auch bei Authentifizierungs- oder Compilerfehlern kann `sourceIndex.ok` daher bereits wahr sein, während `wiki.ok` und der gesamte Lauf falsch bleiben. Nur vollständig erfolgreiche Wiki-Pflege aktualisiert `lastCompleted`.

WikiQuery ergänzt relevante, noch nicht von gültiger Wiki-Evidenz abgedeckte Originale. `fallback` kennzeichnet diese Evidenz; `sourceMatches` enthält ihre tatsächlich geprüften QMD-Treffer und `sourceRetrieval` unterscheidet Quellenindex, aktuellen Direktscan und beide gemeinsam. Zwischen Pflege und Abfrage geänderte Originale werden weiterhin direkt geprüft und niemals mit einem veralteten Indexhash zertifiziert. Explizite `--repo`-/`--source`-Grenzen gelten auf beiden Wegen. [Isolierte Abnahme von Ticket 01](evidence/resumable-maintenance-01.md).

Ändert sich eine Quelle während eines Pakets, wird ihre neueste Konzeptzuordnung nicht aus der alten Fassung erraten. Die Pflege veröffentlicht dann nur noch explizit quellgebundene Aussagen mit erneut geprüften Originalhashes. Gemeinsame Konzepte und ihre Antwortketten bleiben offen; aktuelle reine Quellantworten bleiben bytegleich erhalten. Der Bericht kennzeichnet die inzwischen überholte Quellenindex-Momentaufnahme mit `sourceIndex.ok: false, status: stale`. Vor einem wartenden Extraktions-Cachetreffer werden die Originalbytes erneut geprüft. Ein Folgelauf entdeckt die aktuellen Abhängigkeiten und stellt die gemeinsame Synthese wieder her, ohne kompatible unbetroffene Extraktionen erneut anzufordern. [Driftisolation und Grenzen](evidence/resumable-maintenance-05.md).

Status und Fehler sind JSON; ein Fehler oder offener erforderlicher Arbeitsschritt liefert einen Exitcode ungleich null.

Begrenzte Provider- und Validierungsfehler sperren den betroffenen Quellen-/Seitenzweig einschließlich gespeicherter Antworten. Unabhängige gültige Seiten werden weiter gepflegt und indexiert. Der Lauf bleibt mit `ok: false` und Exitcode 1 unvollständig; `completed`, `unchanged`, `failures` und `pending` beschreiben den Arbeitsstand, `report` verweist auf den lokalen Laufbericht unter `<output>/.state/runs/`. Gemeinsame Runtime-/Indexfehler, unvollständige Scans und nicht bestimmbare Abhängigkeiten sperren abhängige Arbeit. Ein fehlender konfigurierter Repo-Root ist kein bestätigter Quellenentzug.

Gegen das vollständige Tool-Schema validierte Extraktionen werden vor der Seitengenerierung unter `<output>/.state/extractions/` atomar mit Prüfsumme gesichert und synchronisiert. Nach Abbruch, Quellenabweichung oder späterem Indexfehler verwendet ein neuer `maintain`-Prozess weiterhin kompatible Ergebnisse wieder. Der Schlüssel bindet Originalidentität und Inhaltsversion, tatsächliche Extraktionsprompt-/Toolbytes einschließlich Modellkontext, aufgelösten Modellvertrag, Providerparameter sowie installierten Compiler- und Lockdateistand. Beschädigte Einträge werden einzeln neu berechnet. Leere oder teilweise ungültige Extraktionen bleiben als Fehler zur erneuten Verarbeitung offen.

Der Laufbericht enthält `extractions.saved`, `extractions.reused` und `extractions.invalid`; diese zählen ausschließlich Extraktionsarbeit. Cachetreffer ändern weder Publikationsprüfung noch `lastCompleted`. Der optionale Cache erfordert keinen Reset bestehender Seiten oder Antworten. Bei implizitem Codex-Modell bindet der Schlüssel den Compilervertrag `codex-cli-default` zusätzlich an die lokale CLI-Version; eine vom Provider unsichtbar hinter derselben Modellkennung ausgetauschte Backendrevision kann lokal nicht erkannt werden. [Neustart- und Fehlernachweise](evidence/resumable-maintenance-02.md).

Die Kompilierung verwendet aktuelle Fachquellen ohne versteckten Kontext aus früheren Nachbarseiten. Bestände mit älterem Provenienzformat werden beim ersten Pflegeaufruf einmal neu geprüft und kompiliert; danach bleiben gültige unabhängige Ergebnisse bei Wiederholungen erhalten. `scripts/bootstrap.sh` wendet die versionierten Compiler-Patches an. [Verhalten, Nachweise und Grenzen von Ticket 03](evidence/bounded-failures-03.md).

`query` verwendet QMD-Treffer nur mit gültigen Seiten- und Originalquellenständen. Bei fehlender aktueller Wiki-Evidenz liest es passende aktuelle Fachquellen als vorübergehenden Fallback. Ohne `--save` entsteht keine dauerhafte Antwortseite. Die Antwort enthält die tatsächlich übergebene Evidenzmenge einschließlich IDs, Versionen und transitiver Quellenstände. Diese Menge ist bewusst konservativ: Alle übergebenen Belege zählen als Abhängigkeit. Die Relevanzauswahl bewertet QMD-Kandidaten vor der Antwortbildung anhand ihrer fachlichen Beziehung zur Frage; gleiche Begriffe oder Tätigkeitsbereiche allein genügen nicht. Bei ungeeigneten Wiki-Treffern werden passende aktuelle Originalquellen geprüft. Ungültige Provider-Auswahl wird als Fehler gemeldet. Die Relevanzprüfung verarbeitet höchstens zehn Kandidaten und 128.000 Textzeichen je Anfrage; die Antwort erhält höchstens fünf Belege mit zusammen 128.000 Textzeichen. Spätere Kandidaten werden bei fehlender Relevanz weiter geprüft. Einzelne zu große Belege werden mit explizitem Budgetfehler gemeldet und nicht still abgeschnitten.

Explizite Aufgabengrenzen werden mit wiederholbaren `--repo ID` oder `--source REPO/PFAD.md` bei `query`, `search` und `save` gesetzt:

```bash
./wiki query --config .local/common.json --question 'Liquiditätsplanung' --repo private
./wiki query --config .local/common.json --question 'Projektplanung' \
  --source private/planung.md --source probare-crm/projekt.md
```

Mehrere Werte desselben Flags bilden eine erlaubte Menge; beide Flagarten zusammen bilden deren Schnittmenge. Gemischte Seiten werden vollständig ausgeschlossen, sobald eine direkte oder transitive Quellen-/Seitenabhängigkeit außerhalb der Grenze liegt. Quellen-Fallbacks werden vor jedem Provideraufruf ebenso begrenzt. Unbekannte oder leere Grenzen sind Fehler. Eine Formulierung im Fragetext ersetzt diese Überprüfung nicht. `search` liefert aktuelle, zulässige QMD-Kandidaten; die fachliche Modellauswahl findet in `query` statt.

Ein vorhandener Agent kann einen eigenen Entwurf speichern. Der Entwurf benennt die von der verwalteten Query gelieferten Evidenz-IDs und Hashes:

```json
{
  "slug": "meine-synthese",
  "question": "Was folgt daraus?",
  "answer": "Belegter Antworttext ...",
  "evidence": [{"id": "concepts/beispiel", "hash": "SHA-256-aus-query"}]
}
```

```bash
./wiki save --config .local/common.json --draft .local/entwurf.json
./wiki source --config .local/common.json --id 'shared-ai-docs/docs/rag/operating-model-rag-qmd.md'
```

Save weist fehlende oder geänderte Evidenz sowie direkte und indirekte Abhängigkeitszyklen zurück. Abhängigkeiten zu gespeicherten Antworten werden ebenso verfolgt wie Konzeptseiten. `source` zeigt den tatsächlich verarbeiteten Text mit Originalpfad, Hash und Zeilenoffset null. Die Fachquelle bleibt maßgeblich; eine Synthese ersetzt keine ADR oder Fachregel.

## Kontextänderung und Fehler

Eine Repo-Abwahl in der Konfiguration oder ein bestätigt fehlender Originalclone zieht abhängige aktive Seiten und Antworten zurück. Gemischte Konzepte werden aus verbliebenen Quellen neu erzeugt. Unabhängiges Wissen bleibt erhalten. Ein später wieder vorhandenes ausgewähltes Repo wird aus seinem aktuellen Inhalt neu verarbeitet; zuvor entzogene Antworten werden nicht automatisch wiederbelebt.

Ein Scanfehler ist kein Entzug. Provider-, Versions- und Indexfehler lassen erforderliche Restarbeit sichtbar. Nach Behebung denselben `maintain`-Aufruf wiederholen. Die Quellen werden dabei erneut gelesen. Ein abgebrochener Schreibprozess hinterlässt eine PID-Sperre; ein nachweislich beendeter Eigentümer wird beim nächsten Aufruf erkannt. Eine unlesbare Sperre muss nach Prüfung ihres Eigentümers manuell behoben werden. Keine pauschale Prozessbeendigung verwenden.

Der Wiki-Einstieg zeigt den letzten abgeschlossenen Pflegezeitpunkt. Ohne Pflegeaufruf wird keine Echtzeitaktualität in Obsidian versprochen; die verwaltete Query prüft Originalstände vor Benutzung. Ein Indexfehler bedeutet unvollständige Pflege. Unverwaltete direkte QMD-Abfragen können bis zur erfolgreichen Indexwiederholung den vorherigen Indexstand enthalten.

## Ablage und QMD

- `<output>/wiki/`: aktive Seiten und Obsidian-Einstieg `index.md`.
- `<output>/.state/compiler/`: unterstützter Quellenpfad, Compilerzustand und dessen Markdown-Inhaltsübersicht.
- `<output>/.state/state.json`: Seitenregister, Versionen, Abhängigkeiten und Restarbeit.
- `<output>/.state/extractions/`: dauerhafte, abgeleitete Modellarbeit; kein Retrievalspeicher und keine Publikation.
- `<output>/.state/staging/`: vor Veröffentlichung vorbereitete Ergebnisse.
- `<output>/.state/qmd-collections.json`: ausschließlich Wiki-eigene Collection-Zuordnung.

Die bestehende zuständige Reconciliation verarbeitet dieses Teilmanifest über `QMD_COLLECTION_MANIFEST`. Fremde Collections werden nicht umgehängt oder entfernt. Der QMD-SDK aktualisiert ausschließlich die gewählte Wiki-Collection. Die gemeinsame Wiki-Collection bleibt in der Standardsuche enthalten; Tätigkeitsbereiche erzeugen keine ausgeblendeten Collections. Die Integration verwendet den vorhandenen QMD-Index; sie erzeugt keinen Compiler-Vektorstore. QMD-Embeddings können durch die vorhandene QMD-Wartung ergänzt werden. Lexikalisches QMD-Retrieval funktioniert bereits ohne neue Embeddings.

Falls die lokale Runtime anders installiert ist, erlaubt das optionale `qmd`-Objekt `module` (installiertes `dist/index.js`), `node`, `dbPath`, `reconcileScript` und `python`. `isolated:true` ist für reproduzierbare Tests mit einer ausdrücklich separaten QMD-Testdatenbank vorgesehen.

## Sicherung und Wiederherstellung

```bash
./wiki backup --config .local/common.json --destination /lokale/sicherung/wiki-2026-09-12
./wiki restore --config .local/common.json --backup /lokale/sicherung/wiki-2026-09-12
```

Das neue Sicherungsverzeichnis muss außerhalb der Fachrepos und aktiven Ausgabe liegen. Die Sicherung enthält Originalkopien, generierte Texte, Compilerzustand und Antwortabhängigkeiten. Sie ist eine lokale Betriebsablage und wird nicht eingecheckt. Restore prüft zuerst Runtime und Provider, anschließend Hashes und den aktuellen Kontext, bevor gesicherte Seiten aktiv werden. Bei einem kleineren Kontext wird entzogene Antwort-Evidenz nicht veröffentlicht; gemischte Konzepte werden neu erzeugt. Ein Rohquellen-Neubau kann einzigartige Gesprächsformulierungen nicht identisch reproduzieren.

## Verifikation

```bash
npm run check
# Optionaler echter Codex-Providerlauf mit künstlichen Quellen und isoliertem QMD:
./wiki-node test/accept-common.ts
```

Die Tests benutzen die öffentliche CLI, den echten gepinnten Compiler und echte isolierte QMD-Datenbanken. Nur die Modellprovidergrenze wird deterministisch kontrolliert. [Ticket-01-Abnahme](evidence/shared-wiki-01.md), [frühere Abnahme](evidence/acceptance.md), [initiale Inventur](evidence/initial-inventory.json), [Integrationsentscheidungen](evidence/implementation-notes.md) und [Upstream-Patch](patches/0001-host-completion-without-embeddings.patch) dokumentieren Nachweise und Grenzen.

## Bestehende Wissensbestände übernehmen

`migration-inventory` untersucht tatsächliche Ausgabeordner und bestehende lokale `backup.json`-Backups. Ein wiederholtes `--from` nimmt weitere Bestände auf. Die gemeinsame Zielkonfiguration enthält die Originalrepos und Quellenfilter, gegen die alle alten Belege geprüft werden. Alte `general`-/`private`-Labels begrenzen diesen Import nicht.

```bash
./wiki migration-inventory --config .local/common.json \
  --from "$OLD_GENERAL_OUTPUT" --from "$OLD_PRIVATE_OUTPUT" \
  --from "$OLD_BACKUP"
./wiki migrate --config .local/common.json \
  --from "$OLD_GENERAL_OUTPUT" --from "$OLD_PRIVATE_OUTPUT" \
  --from "$OLD_BACKUP" --snapshot "$MIGRATION_SNAPSHOT"
./wiki status --config .local/common.json
./wiki query --config .local/common.json --question 'Gespeicherte Entscheidung'
./wiki lint --config .local/common.json
```

Vor dem ersten Schreiben ins Wiki sichert der Lauf alle Dateien der Eingänge und des bisherigen Zielbestands einschließlich Compilerzustand und unverwalteter Notizen. `manifest.json` enthält SHA-256-Prüfsummen, Inventur und Herkunft; erst das vollständig geschriebene und geprüfte Manifest macht den Snapshot verwendbar. Der neue Snapshot muss außerhalb der Fachrepos und getrennt von Eingängen/Ziel liegen. Alte Ausgaben und Backups bleiben erhalten. Laufende Schreiber im Altbestand verhindern die Sicherung.

Der Bericht nennt für jede Seite `preserved`, `deduplicated` oder `quarantined` und gegebenenfalls Gründe. Unverwaltete Markdown-Dateien werden als `unmanaged` aufgelistet und vollständig gesichert, jedoch ohne belegte Abhängigkeiten nicht veröffentlicht. Leere Produktionsordner werden von befüllten Abnahmeausgaben unterschieden. Texte gültiger Seiten bleiben erhalten; ausschließlich lokale Seitenlinks und die zugehörigen Versionsverweise werden auf neue Identitäten umgesetzt. Unterschiedliche gleichnamige Seiten erhalten getrennte Identitäten. Navigationslinks auf zurückgestellte Seiten öffnen deren Snapshot mit dem Zusatz „historisch“; nicht auflösbare Altlinks bleiben als Text mit einem Berichtseintrag erhalten. Identische Revisionen samt Abhängigkeitsgraph werden zusammengeführt. Historische Quellenstände, fehlende Provenienz, manipulierte Seiten und ungültige Abhängigkeiten werden zurückgestellt.

Importierte Konzeptseiten und gespeicherte Antwortketten nehmen an der normalen Pflege teil. Die Migration in eine frische Ausgabe übernimmt vorhandenes Wissen ohne Modellkompilierung. Quellen, die keine gültigen importierten Seiten belegen, bleiben für die spätere Erstpflege offen. Ein bereits befüllter Zielbestand wird vor der Ergänzung bei Bedarf regulär gepflegt. Ein erfolgreicher Import wird im Zustand vermerkt, sodass Wiederholung auch nach späterer Pflege keine alten Texte zurückschreibt.

Nach einem Abbruch oder Indexfehler denselben geprüften Snapshot erneut verwenden:

```bash
./wiki migrate --config .local/common.json --snapshot "$MIGRATION_SNAPSHOT"
```

Die Wiederaufnahme benötigt die ursprünglichen Eingabeordner nicht mehr. Sie prüft sämtliche Snapshot-Dateien erneut und bearbeitet inzwischen geänderte Quellen. Andere Schreiboperationen melden bis dahin den offenen Migrationslauf und den Wiederaufnahmebefehl. Ein Snapshot ohne vollständiges Manifest wird nicht überschrieben: Ursache beheben und einen neuen Snapshot-Pfad verwenden; die unvollständige Sicherung bleibt überprüfbar erhalten. QMD-Collections anderer Bestände bleiben unverändert. Produktive Aktivierung und Ablösung alter Ausgaben gehören zu Ticket 04.

## Begrenzte Tagespakete und Erstimport

`maintenance.maxExtractionSources` begrenzt neue Extraktionsanfragen pro Lauf (Standard 20, ganze Zahl mindestens 2); Cachetreffer verbrauchen keinen Platz. Sobald das gemeinsame Quelleninventar größer als das Paket ist, erfolgt die Extraktion seriell in dieser Reihenfolge; kleine vollständige Läufe behalten die konfigurierte Parallelität. Die endliche Helper-Zeitgrenze gilt zusätzlich. Neue und geänderte Versionen erhalten die ersten Plätze, ein Platz bleibt für die älteste noch unextrahierte Erstimportquelle reserviert. Bei mehr Tagesarbeit als freien Plätzen meldet `maintenance.capacity.dailyOverCapacity` den Konflikt ausdrücklich. Ein vor Modellstart gespeicherter Versuch enthält die noch unextrahierten Initialversionen. Zwei aufeinanderfolgende Versuche ohne tatsächlich gesicherte Initialextraktion lösen einmal `capacity.mode: initial-recovery` aus: die älteste Initialquelle erhält den ersten Versuch, danach folgen wieder Tagesquellen. Schon der folgende Lauf kehrt zu `daily-first` zurück, auch wenn Recovery scheitert. Ein fehlender Abschlussbericht oder SIGKILL setzt diesen Verlauf nicht zurück. `missedInitialRounds` und `backlogStalled` zeigen den Rückstand; `insufficientTimeCapacity` meldet tatsächlich ausgeschöpftes Laufzeitbudget mit offener Arbeit. Das garantiert eine faire Gelegenheit, nicht den Erfolg eines hängenden Providers; Tagesrest und Tagesfrist bleiben sichtbar. `reservedInitialSlots` und `dailyAwaitingExtraction` zählen noch erforderliche Extraktionen, nicht bereits extrahierte Quellen mit noch offener Synthese. Ein einzelner sehr großer gemeinsamer Konzeptzweig kann weiterhin das Zeitbudget überschreiten; die bereits validierten Extraktionen bleiben wiederverwendbar. Die Mengen sind Grenzen, keine Durchsatzgarantie.

`.state/maintenance-inventory.json` hält das Ausgangsinventar, erste Beobachtung, aktuelle beobachtete Version und erfolgreiche Extraktions-/Quellseitenstände fest. Unveränderte Scans verändern deren Alter nicht. Auch eine bisher unkompilierte Initialquelle wird nach Inhaltsänderung Tagesarbeit. Ein unvollständiger Scan verändert das Inventar nicht; eine bestätigte Entfernung bleibt als solche protokolliert. Ohne bekannten fachlichen Änderungszeitpunkt bleibt `changedAt: null`; die Frist basiert transparent auf der ersten Beobachtung dieser Version, nicht einem erfundenen Änderungsdatum. Ziel ist das Ende des nächsten Kalendertags in `Europe/Berlin`, auch bei Zeitumstellung. Ein tatsächlicher früherer Änderungszeitpunkt kann unbekannt sein; der Bericht bescheinigt deshalb keine unbekannte historische Fristtreue.

Solange noch Quellen ohne bekannte Extraktion existieren, ist globale Konzeptvollständigkeit nicht bewiesen. Begrenzte Pakete veröffentlichen daher ausdrücklich **quellgebundene modellverarbeitete Aussagen** im gemeinsamen Wiki (`source-summary`), mit eigener geprüfter Originalreferenz. Das ist kein Rohquellen-Fallback und keine vollständige gemeinsame Synthese. Betroffene globale Konzepte und davon abhängige gespeicherte Antworten bleiben gesperrt. Sobald die gemeinsame Extraktionszuordnung vollständig ist, erzeugt derselbe Compiler die repoübergreifenden Konzepte mit allen Besitzern; vorhandene Antwortabhängigkeiten werden regulär geprüft. Die Ausgabe wird nicht nach Quellen oder Repos in Teilwikis zerlegt.

Der Bericht trennt `maintenance.daily` (offene Tagesarbeit, bereits verfügbare Quellaussagen, überfällige Identitäten), `maintenance.initial` (offener Erstimport und davon noch unextrahierte Quellen), Kapazität und `globalComplete`. Eine verfügbare Quellaussage allein schließt ihre noch offene globale Synthese nicht ab: Tagesfrist und Gesamtabschluss bleiben offen, `lastCompleted` bleibt unverändert. Der Helper kann ein sicheres Paket indexieren und endet trotzdem mit `ok: false`, solange erforderliche Restarbeit besteht. Tests dürfen den Beobachtungszeitpunkt über `WIKI_MAINTENANCE_NOW` ausschließlich mit einer ausdrücklich isolierten QMD-Konfiguration steuern; Produktion weist diese Testuhr zurück.
