## Context

Die ursprüngliche Integration ist archiviert. Der erste Betriebsstand verwendet den bestehenden täglichen QMD-Job, einen seriellen Wartungshelfer und getrennte allgemeine/private Wiki-Konfigurationen. Der Live-Job pflegt bisher nur den allgemeinen Bestand. Dieser frühere Code partitionierte Quellen nach Scope. Ticket 01 hat die gemeinsame CLI inzwischen implementiert und isoliert verifiziert; bestehende produktive Bestände und der Live-Job sind noch nicht migriert.

Daniel hat im Interview klargestellt: „privat“ bezeichnet seinen persönlichen Tätigkeitsbereich, keine Schutzklasse. Die bisherige Architektur leitete daraus eine nicht beabsichtigte Wissensgrenze ab. [ADR 0010](../../../docs/adr/0010-shared-wiki-across-personal-and-professional-domains.md) korrigiert diese Annahme.

## Goals / Non-Goals

Ein gemeinsamer, automatisch gepflegter Wissensbestand über alle ausgewählten Fachrepos einschließlich `private`, `Projects/Private`, Meetings und Projects. Repoübergreifende Erkenntnisse werden bei fachlicher Relevanz erzeugt und genutzt. Es gibt keine pauschale Privatklassifizierung und keinen gesonderten Freigabeaufruf aufgrund des Ordnernamens.

Keine weitere Retrieval-Engine, kein zusätzlicher Scheduler/Watcher, keine Fachquellenänderung und keine automatische externe Veröffentlichung. Quellenherkunft, Abhängigkeiten, Aktualitätsprüfung sowie ausdrücklich vorgegebene Aufgabengrenzen bleiben erhalten. Die flächendeckende Einführung der Kontextverweise bleibt zunächst katalogisiert.

## Decisions

### Gemeinsame Wissensbildung und kontextbezogene Nutzung

Alle ausgewählten Fachquellen fließen in dieselbe Wissensschicht. Tätigkeitsbereiche sind fachliche Zuordnungen und keine separaten Wiki-Produkte. Die konkrete Frage und ihr Aufgabenbezug bestimmen passende Evidenz und sinnvolle Synthesen; gleiche Begriffe allein begründen noch keinen fachlichen Zusammenhang. Private Quellen dürfen dabei ohne besondere Freigabe verwendet werden. Explizite Nutzerbegrenzungen auf bestimmte Quellen oder Repos gelten weiterhin.

### Automatische Pflege

Der bestehende lokale Job bleibt täglich um 07:00 mit den vorhandenen Modell-, Projekt- und Benachrichtigungseinstellungen aktiv. Er pflegt den vollständigen gemeinsamen Bestand und danach QMD. Merge und Query sind keine zusätzlichen Auslöser. Ein unveränderter erfolgreicher Lauf vermeidet neue Modellkompilierung.

### Fehlerisolation und sichtbare Teilergebnisse

Daniel hat die Fortsetzung unabhängiger Arbeit bei begrenzten Fehlern grundsätzlich bestätigt. Ein Fehler sperrt die betroffenen Aussagen und davon abhängige Schritte; unabhängige Pflege und sicher ausführbare QMD-Wartung können weiterlaufen. Der Gesamtbericht meldet Teilfehler mit offenem Arbeitsumfang, niemals vollständigen Erfolg. Ein Scanfehler ist kein bestätigter Quellenentzug; gemeinsame Runtime-/Indexfehler oder unbestimmbare Abhängigkeiten blockieren die davon betroffenen Arbeiten.

### Umsetzung der Teilfehlerfortsetzung (Ticket 03)

Der gepinnte Compiler erhält einen optionalen Host-Callback für Fehler an den Providergrenzen der Quellenextraktion und Seitengenerierung. Validierungsfehler nennen ebenfalls ihre Quellen; gemeinsame Dateisystem-/Runtime-Fehler werden weiterhin geworfen. Die verwaltete Pflege kompiliert aus aktuellen Fachquellen ohne frühere Wiki-Seiten als unprotokollierten Modellkontext. Gemeinsame Quellenbesitzer und gespeicherte Seitenabhängigkeiten bestimmen konservativ den gesperrten Zweig. Fehlt bei einer fehlgeschlagenen Extraktion die bisherige Zuordnung, wird keine unabhängige Veröffentlichung behauptet.

Komplett vorbereitete unabhängige Seiten werden veröffentlicht. Gesperrte Seiten behalten ihre Metadaten für die Wiederaufnahme; ihre Dateien werden aus der aktiven Ausgabe entfernt. Fehlgeschlagene Quellen erhalten Retry-Marker im Compilerzustand. Antworten werden in Abhängigkeitsreihenfolge erneuert; ein Antwortfehler sperrt seine Nachfolger. Bei einer bekannten Quellenentfernung dürfen nicht mehr belegte Antworten wie bisher entfallen; fehlende Abhängigkeitsdatensätze sind dagegen offene Fehler.

`publicationVersion: 2` kennzeichnet den aus vollständigen Fachquellen abgeleiteten Zustand ohne versteckte Nachbarseitenabhängigkeiten. Ältere veröffentlichte Zustände werden einmal neu aufgebaut, bevor unabhängige Wiederverwendung zugesichert wird. Das führt keine Migration zwischen den bisherigen getrennten Ausgaben durch.

Jeder Wiki-Aufruf behält einen lokalen JSON-Laufbericht, der Compiler zusätzlich sein Rohresultat und begrenzte Fehler. Der Helper bewahrt Prozess-stdout, stderr und Exitcode und prüft die Übereinstimmung mit dem lokalen Wiki-Bericht. Teilfehler erlauben QMD nur mit expliziter Eignung und passenden Status-/Lint-Audits; vollständiger Erfolg und `lastCompleted` werden erst ohne offene Arbeit ausgewiesen. Der Live-Job bleibt Ticket 04 vorbehalten.

### Quellenautorität und Kontextdateien

Originalrepos bleiben Fachquellen an ihren bestehenden Orten. Generated Wiki-Seiten sind abgeleitete Evidenz, keine neuen Agent-Anweisungen und kein Ersatz für gültige Anforderungen oder ADRs. Die verwaltete Query prüft relevante Originalstände, nutzt passende aktuelle Wiki-Evidenz und fällt bei Lücken auf aktuelle Quellen zurück. Skills und Repo-Einstiege erhalten später kurze Verweise gemäß dem aktualisierten Katalog.

## Implementation Assumptions

Quellen-IDs und Hash-/Abhängigkeitsverfolgung werden beibehalten. Der bestehende Compiler und QMD bleiben gesetzt. Gemeinsame Konfiguration, genaue Ausgabepfade, Collection-Migration und sichere Arbeitseinheiten bei Teilfehlern werden in der Umsetzung bestimmt; das sind keine weiteren Interviewfragen.

Bestehende generierte Seiten und gespeicherte Gesprächssynthesen werden vor Migration gesichert. Beim Zusammenführen werden Provenienz und aktuelle Quellenstände geprüft; alte Bestände dürfen erst nach verifizierter Übernahme ihrer erhaltenswerten Inhalte abgelöst werden. Gleichnamige Seiten sind anhand ihrer Belege zu behandeln, nicht still zu überschreiben. Das erfordert kein erneutes Produktmandat.

## Risks / Trade-offs

Der Vollimport kann lange dauern und wurde noch nicht ausgeführt. Die gemeinsame CLI samt ersetzten Privacy-Szenarien ist mit Ticket 01 akzeptiert; die Übernahme bestehender Ausgaben steht aus. Die sichere Fortsetzung nach Teilfehlern ist mit Ticket 03 isoliert implementiert und verifiziert; die produktive Aktivierung bleibt offen. Mac-Verfügbarkeit und Provider-Anmeldung begrenzen die lokale Ausführung. Gemeinsame Wissensbildung bedeutet keine automatische fachliche Relevanz jeder Quelle für jede Frage.

## Migration Plan

1. Gemeinsamen Quellen-/Query-Vertrag mit Verhaltenstests umsetzen, einschließlich einer belegten Synthese aus `private` und einem anderen Repo sowie eines irrelevanten Kontrollbelegs.
2. Bestehende Zustände sichern, gemeinsame Ausgabe/QMD-Anbindung vorbereiten und gespeicherte Synthesen samt Abhängigkeiten verifiziert übernehmen.
3. Fehlerisolation und echte Teilfehlerberichte im Pflegeablauf implementieren; gültige unabhängige Inhalte und sichere QMD-Pflege nachweisen.
4. Live-Job, Betriebsreferenzen und notwendige Retrieval-Regeln auf den gemeinsamen Bestand umstellen. Den Einführungskatalog als Plan für weitere Repo-Dateien beibehalten.
5. Echten gemeinsamen Erstimport, anschließenden No-op und Herkunft/Aktualität der erzeugten Synthesen prüfen. Erst dann neue Abnahme ausweisen.

## Interview-Abschluss

Feststehend sind gemeinsame Wissensbildung ohne Privat-Sondergrenze, fachliche Relevanz als Auswahlkriterium, tägliche Pflege und Fortsetzung unabhängiger Arbeit bei Teilfehlern. Es bleibt keine offene Produktentscheidung für diesen Plan. Technische Parameter werden während der Umsetzung entschieden. Ticket 01 ist akzeptiert und im separaten Change `share-contextual-wiki-sources` archiviert. Dieser aktive Betriebs-Change führt die offenen Tickets 02–04 fort; Live-Job und Bestände sind noch nicht entsprechend umgestellt.

## Ticket 02: bestätigter Implementierungsrahmen

Owning Git root: `_shared/shared-ai-docs`; Ausgangsbranch `main` mit parallelen Änderungen. Daniel bestätigte den isolierten Zielbranch `codex/shared-wiki-02` auf Ticket-01-Commit `1c13f089b559441e887a124c7ee63c41c568610f`. Review-Basis ist dieser feste Ausgangscommit. Task 4.2 gehört zum bestehenden Change; Produktion und Scheduler bleiben Ticket 04.

Die CLI erhält `migration-inventory --from PATH` für Ausgabeverzeichnisse oder bestehende `backup.json`-Backups und `migrate --from PATH --snapshot PATH` (jeweils wiederholbares `--from`). Inventur und Migration lesen historische Scopes ohne sie als aktive Konfiguration zuzulassen. Die Sicherung enthält alle Dateien und SHA-256-Prüfsummen; ein fehlendes Manifest bedeutet unvollständige Sicherung. Wiederholung mit demselben Snapshot verwendet dessen eingefrorene Eingänge. Ein offener Migrationslauf sperrt andere Schreiber bis zur Wiederaufnahme.

Importe erhalten deterministische Seitenidentitäten anhand ihrer Revision und Abhängigkeiten. Unterschiedliche gleichnamige Seiten bleiben getrennt; gleiche Revisionen samt Abhängigkeitsgraph können gemeinsam geführt werden. Originalbytes bleiben im Snapshot; aktive Kopien ändern ausschließlich aufgelöste lokale Verweise und Versionsreferenzen. Importierte Konzepte bleiben als eigene abgeleitete Seiten pflegbar, unabhängig von den Namen neuer Compilerkonzepte. Quellenkorrekturen durchlaufen die bestehende topologische Nachpflege. Unvollständig belegte Altstände werden nicht automatisch durch neue Modellformulierungen zu gültigen Importen erklärt.

Die Abnahme zeigte, dass eine Migration in ein frisches Ziel keinen Vollimport vorwegnehmen darf. Sie übernimmt deshalb nur belegte aktuelle Seiten und deren Quellspiegel ohne Modellaufruf; weitere ausgewählte Quellen bleiben für die spätere Erstpflege sichtbar offen. Ein bereits befülltes Ziel wird regulär abgeglichen. Die Quelländerungsprüfung importierter Konzepte verwendet weiterhin den echten Compiler und die normale abhängige Nachpflege. Defekte Metadaten werden samt Rohdateien gesichert; Navigation auf zurückgestellte Seiten führt ausdrücklich in den historischen Snapshot. Inventur, Snapshot, reine Importplanung und Schreibablauf sind getrennte Module.

## Gemeinsame Integration von Tickets 02 und 03

Frische Migrationsziele besitzen keinen wiederverwendeten Compiler-Kontext. Ihre
prüfsummen- und abhängigkeitsgeprüften Importe erhalten die aktuelle
Publikationsversion, damit unveränderte einzigartige Antworten beim nächsten
Pflegeaufruf erhalten bleiben. Bestehender alter Compiler-Kontext unterliegt
weiterhin dem einmaligen Neuaufbau aus Ticket 03. Die Pflege behält das
Migrationsjournal und behandelt Fehler importierter Antwortketten mit denselben
Abhängigkeitssperren wie andere gespeicherte Antworten.
