# Agent-Wiki und DanielsVault: Strukturvergleich und Einführung

Stand: 09.09.2026. Analyse und Vorschlag, keine eingeführte Architekturentscheidung.

## Empfehlung

Das Agent-Wiki-Prinzip passt zu DanielsVault, wenn Wissen weiterhin in seinem fachlich zuständigen Repository gepflegt wird. Die vorhandenen Repos müssen weder zusammengelegt noch in neue Obsidian-Vaults aufgeteilt werden. Empfohlen ist eine kleine, pro Repo gepflegte Wissensschicht auf Basis vorhandener Themenseiten, mit Quellenbelegen, Aktualisierungsregeln und gezieltem QMD-Retrieval.

Der Vault ist bereits agententauglich und in Teilen ein kuratiertes Wiki. Es fehlt vor allem ein durchgängiger Ablauf, der neue Erkenntnisse in bestehende Seiten einarbeitet, abgeleitete Übersichten nachzieht und überholte Aussagen kenntlich macht. Eine vollständige Übernahme von `Ar9av/obsidian-wiki` wäre ein separates Integrationsvorhaben und ist für den ersten Nutzen nicht erforderlich.

## Untersuchungsbasis und Grenzen

- Navigation zunächst über `VAULT_AGENT_STRUCTURE.md`, anschließend im Bereich `_shared`; weitere Bereiche einschließlich `private` wegen der ausdrücklich vaultweiten Fragestellung.
- Acht Git-Wurzeln anhand der Dateistruktur gefunden und mit `git rev-parse --show-toplevel` bestätigt: Vault-Root, `_shared/shared-ai-docs`, `_ops/meeting-assistant`, `ncg/ncg-docs`, `ki-fuer-kmu`, `private`, `probare-crm`, `sparkle`.
- Strukturinventar: 1.959 Markdown-Dateien ohne Symlinks, Dependencies, Build-Ausgaben, Worktrees, übliche Caches und Obsidian-Plugin-Dateien. Darunter 799 Dateien in Verzeichnissen namens `archive`, `Completed` oder `_legacy` (Groß-/Kleinschreibung ignoriert). Dies ist eine mechanische Inhaltsklassifikation, kein Qualitätsurteil oder vollständiger Linkaudit.
- Inhaltliche Stichproben: Repo-READMEs und Agent-Regeln, RAG-Betriebsdokumentation und Adaptercode, SpecOps-Schema und Entity-Notes, private Dokumentationsregeln und Dashboard, NCG-Operations und Service-Abhängigkeiten, KI-Produktindex und ADR, Meeting-Projektkontexte. Keine vollständige fachliche Prüfung aller Notizen oder externer Originalbelege.
- QMD live geprüft: Version `2.1.0 (08e85c4e42)`, 25 Collections, 1.982 indexierte Dateien, 9.528 eingebettete Vektoren, letzter Indexstand laut Status vor etwa 23 Stunden. Dateiscan und Indexzählung haben verschiedene Auswahlregeln; ihre Differenz belegt für sich keine Indexlücke.
- Lexikalische Suchen in gezielten Collections und eine hybride Abfrage ausgeführt; ausgewählte Quellen direkt gelesen. Keine repräsentative Qualitäts- oder Geschwindigkeitsmessung.
- Externe Grundlage: [gesonderte Primärquellen-Recherche](2026-09-09-agent-wiki-primary-sources.md) zum Framework mit unveränderlichen Quellcode-Verweisen. Die folgenden Integrationsrisiken stammen aus statischer Untersuchung, nicht aus einer Installation im Vault.

## Was das Konzept ist

Ein Agent-Wiki macht aus Rohmaterial dauerhaft gepflegte Wissensseiten. Ein Agent liest beispielsweise Dokumente, Gesprächsergebnisse oder Code, extrahiert relevante Aussagen, ordnet sie vorhandenen Themen zu und aktualisiert deren Seiten. Er ergänzt Quellen und Beziehungen, unterscheidet belegte Aussagen von Schlussfolgerungen und markiert Konflikte. Ein späterer Dialog beginnt mit diesem bereits aufbereiteten Wissen; bei Bedarf liest er die Originalquelle nach.

Der typische Ablauf lautet:

`Originalquelle → Extraktion → bestehende Themenseite aktualisieren → Quellen und Links prüfen → später gezielt abfragen`

Quellen, abgeleitetes Wissen und Agent-Arbeitsregeln haben unterschiedliche Rollen. Originalquellen werden erhalten; neue Erkenntnisse sollen möglichst bestehende Seiten verbessern. Ein Index und ein Änderungsprotokoll helfen bei Navigation und Pflege. Das Framework ergänzt dafür Skills und Werkzeuge für Ingest, Capture, Query, Lint und Dublettenbehandlung. Obsidian dient als lesbare Oberfläche für Markdown und Verknüpfungen. Das Konzept erfordert weder eine Graphdatenbank noch einen ständig laufenden autonomen Agenten. [Framework-Architektur](https://github.com/Ar9av/obsidian-wiki/blob/main/docs/architecture.md)

Für DanielsVault kann diese Rolle auch eine vorhandene README, ein Runbook oder eine fachliche Übersichtsseite übernehmen. Ein neuer Ordner namens `wiki` und die Konvertierung jedes Dokuments sind keine fachlichen Voraussetzungen.

## Wie weit die Bereiche bereits sind

| Bereich | Beobachteter Bestand | Einordnung |
|---|---|---|
| Vault-Root | Routing-Matrix, acht explizite Repo-Grenzen, separate Meeting-Projektkontexte | Gute föderierte Navigation; keine gemeinsame Wissenssynthese erforderlich. |
| `_shared/shared-ai-docs` | 649 Markdown-Dateien im definierten Scan, darunter 320 unter `openspec`, 101 unter `_specs`, 38 unter `docs` | Viele Quellen, Skills und Entscheidungsstände; die kleine Betriebsdokumentation eignet sich als Einstieg in konsistente Wissenspflege. |
| `_shared/SpecOps` | 145 Dateien im Scan, 124 unter `Entities`; Schema mit IDs, Quellen, Evidenz und Beziehungen | Bereits strukturierte Projekt- und Spec-Sicht. Dies ist wertvolle Vorarbeit, aber kein universelles Themenwiki. |
| `ncg/ncg-docs` | 85 Dateien einschließlich Agent-Zusatz; Operations-Index, Runbooks, Service-Seiten und aus Code abgeleitete Abhängigkeitsübersicht | Inhaltlich schon deutliche Wiki-Eigenschaften; Quellenrevision und Nachpflege können verbindlicher werden. |
| `ki-fuer-kmu` | 551 Dateien einschließlich 184 unter `.agents`; Produktübersichten, ADRs, OpenSpec, Historie | Starke Trennung von fachlichem Wissen, Anforderungen und historischer Evidenz. Wiki-Seiten dürfen diese Autorität nicht überschreiben. |
| `private` | 216 Dateien; Sanierungsbereich mit 29 Seiten, Dashboard, fachlichen Unterseiten, Metadaten und Originalbeleg-Verweisen | Der Sanierungsbereich ist dem Konzept besonders nahe. Diese Einschätzung gilt nicht automatisch für sämtliche privaten Unterbereiche. |
| `Meetings` / `_ops/meeting-assistant` | 29 Meeting-Dateien: 9 Transkripte, 10 Notizen, 9 Kontextdateien, 1 Zusammenfassung; separates Code-Repo mit umfangreicher Spec-Historie | Quellen und Ableitungen sind bereits getrennt. Nachhaltiger Mehrwert entsteht, wenn geprüfte Ergebnisse in die zuständigen Fachseiten zurückfließen. |
| `probare-crm` / `sparkle` | 7 bzw. 3 Markdown-Dateien | Ein guter Einstiegspunkt und gelegentliche Pflege reichen zunächst; geringe Rechtfertigung für zusätzlichen Frameworkbetrieb. |

Wikilink-Anzahlen wären kein guter alleiniger Reifegrad: NCG benutzt normale Markdown-Links, SpecOps häufig YAML-Beziehungen. Beides kann fachlich wertvoll sein. Umgekehrt beweist vorhandenes Frontmatter noch keine aktuelle, richtige Wissensseite.

Belegende Einstiegspunkte: [Vault-Navigation](../../../../VAULT_AGENT_STRUCTURE.md), [Shared-Regeln](../../AGENTS.md), [SpecOps-Feldschema](../../../SpecOps/Reference/field-reference.md), [NCG-Ops](../../../../ncg/ncg-docs/docs/Ops/README.md), [NCG-Abhängigkeitsübersicht](../../../../ncg/ncg-docs/docs/Ops/Services/Service-Dependency-Graph.md), [KI-ADR zur Quellenautorität](../../../../ki-fuer-kmu/docs/adr/001-openspec-requirements-and-delivery-ledger.md), [private Pflegekonvention](../../../../private/Energetische%20Sanierung/DOKUMENTATIONSRICHTLINIEN.md).

## Konkreter Nutzen, der im Bestand sichtbar wird

**Eine aktuelle Seite genügt nicht, wenn ihre Wegweiser eine alte Aussage behalten.** Die [aktuelle QMD-Betriebsseite](operating-model-rag-qmd.md) bestimmt QMD zur einzigen Index- und Retrieval-Engine. [README](README.md) und [Index](index.md) empfehlen dagegen noch `rag` als Standard und QMD als optionalen Zusatz. Auch [SpecOps-Entity](../../../SpecOps/Entities/artifacts/rag-operating-model-documentation.md) beschreibt die alte Aussage. Die historische Entscheidung darf erhalten bleiben; ein aktueller Einstieg muss ihren historischen Status erklären und zur geltenden Regel führen.

Ein zweiter Fall: [Projects/Private/AGENTS.md](../../../../Projects/Private/AGENTS.md) empfiehlt Textsuche, weil Private angeblich nicht indexiert sei. `qmd collection show private` und erfolgreiche gezielte Suchen zeigen dagegen die aktive Collection mit 216 Dateien. Ein Pflegeablauf könnte bei geänderten Betriebsregeln diese betroffenen Einstiegspunkte zur Prüfung vorschlagen.

Eine hybride Stichprobe zur Abgrenzung QMD/OpenSpec/SpecOps lieferte überwiegend historische Backfill- und Archivdokumente. Das beweist keinen allgemeinen QMD-Fehler; es illustriert aber, warum eine kurze, aktuelle Themenseite helfen kann. Volltextsuche findet Relevanz, bestimmt jedoch nicht allein die heute geltende Autorität.

## Zusammenspiel mit lokalem QMD

| Aufgabe | Zuständige Schicht |
|---|---|
| Wo steht etwas Relevantes? | QMD: lexikalische/hybride Suche in ausgewählten Collections. |
| Was wissen wir dazu aktuell, und auf welcher Grundlage? | Gepflegte Themenseite mit Quellen und Gültigkeitsstand. |
| Welche Anforderung bzw. Entscheidung gilt? | Zuständige OpenSpec-Spec, ADR oder kanonische Fachdokumentation. |
| Welche Projekte, Specs und Evidenzen hängen zusammen? | Vorhandenes SpecOps-Modell; zusätzliche Themenlinks nach Bedarf. |
| Ist eine Änderung tatsächlich live? | Betriebs-/Test-/Meeting-Evidenz, nicht allein Wiki-Text. |

Empfohlen: Erst Domain bestimmen, dann mit QMD eine passende Wissensseite finden, ihre Quellen und bei Unsicherheit Originale nachlesen. Noch nicht kuratierte Inhalte bleiben direkt suchbar. Dadurch bleiben seltene Details und neue Erkenntnisse erreichbar. Eine Wissensseite wird nicht allein dadurch zur Primärquelle, dass sie gut formuliert ist.

Neue Markdown-Seiten in vorhandenen, offen sichtbaren Repo-Pfaden fallen grundsätzlich unter die bestehenden `**/*.md`-Collections und werden bei der nächsten erfolgreichen Aktualisierung aufgenommen. Es braucht dafür keinen zweiten Embedding-Index. Eine spezielle Wiki-Collection wäre nur für eine bewusst bevorzugte Suchstufe sinnvoll; überlappende Collections erzeugen sonst zusätzliche Treffer derselben Datei. Versteckte Wiki-Ordner würden die bereits bekannten Zusatz-Collection-Probleme aufwerfen. Die eigene Manifestverwaltung bleibt maßgeblich. [Runtime-Regeln](../../../danielsvault-rag/README.md), [Collection-Manifest](../../../danielsvault-rag/qmd-collections.json)

QMD meldet derzeit keine konfigurierten Collection-Kontexte. Kurze Bereichsbeschreibungen wären eine kleine ergänzende Verbesserung, ersetzen aber keine Seitenpflege und erzwingen keine Zugriffstrennung.

**Die Private-Abgrenzung ist heute nicht in allen Zugriffspfaden gleich:** Das DanielsVault-Manifest nimmt `private` nicht in den Adapter-Scope `all` auf; der [Adapter](../../../danielsvault-rag/src/rag_runtime/qmd_backend.py) übersetzt den Scope in explizite `-c`-Parameter. QMD selbst meldet für `private` jedoch `Include: yes (default)`. Im installierten QMD-Code werden bei fehlender expliziter Auswahl die standardmäßig eingeschlossenen Collections verwendet. Native, unbeschränkte Abfragen können Private deshalb einbeziehen. Dies ist eine konkrete Konfigurationsgrenze, kein Beleg für eine erfolgte Datenweitergabe. Wiki-Abfragen müssen die explizite Collection-Auswahl übernehmen. Unterschiedliche Git-Repos und lokale Speicherung sind für sich keine technische Berechtigungsgrenze; an einen Cloud-Agenten übergebene Auszüge unterliegen dessen Datenfluss.

## Einführung ohne Auflösung der Repo-Struktur

1. **Autorität je Repo behalten.** NCG-Wissen in `ncg/ncg-docs`, private Wissensseiten in `private`, KI-Produktwissen in `ki-fuer-kmu`; allgemeine, entsprechend geeignete Arbeitsweisen in `_shared/shared-ai-docs`.
2. **Bestehende kanonische Seiten weiterentwickeln.** Nur wo eine thematische Zusammenführung fehlt, eine neue Seite unter beispielsweise `docs/knowledge/` anlegen. Nicht neben jede gute README eine inhaltlich gleiche Wiki-Seite stellen.
3. **Root als Wegweiser nutzen.** `VAULT_AGENT_STRUCTURE.md` bleibt die Einstiegskarte. Bereichsübergreifende Links brauchen keine duplizierten Inhalte. Übertragbare Learnings werden bewusst abstrahiert; private oder kundenbezogene Fakten werden dadurch nicht automatisch Shared-Inhalt.
4. **Originalquellen am bisherigen Ort lassen.** Ein konzeptioneller Quellenbereich muss nicht physisch `_raw/` heißen. PDFs können in OneDrive bleiben, Specs im Repo und Transkripte im Meeting-Bereich. Ihre Referenzen und bei Bedarf extrahierte Texte gehören in den passenden Scope.
5. **Kleinen Pflegevertrag vereinbaren.** Neue Quelle prüfen → Thema und Repo bestimmen → bestehende Seite ändern → Quellenabschnitt ergänzen → betroffene Übersichten/Links prüfen → Diff überprüfen. Konflikte markieren; historische Archive und normative Anforderungen nicht still harmonisieren.
6. **Nur nötige Metadaten ergänzen.** Für neue Syntheseseiten etwa `type`, `domain`, `status`, `sources`, `reviewed_at`; für laufende Automation später Quellenrevision oder Hash sowie Quelle→Seite-Zuordnung. Bestehende deutsche Frontmatter-Felder erhalten statt überall ein zweites Schema einzuführen.
7. **Je Repo prüfen und versionieren.** Ein globaler Ingest darf nicht gleichzeitig beliebige Dateien mehrerer Git-Wurzeln ändern oder mitnehmen. Zunächst ein Repo und ein Thema pro Pflegevorgang.

## Konzeptübernahme gegenüber Frameworkinstallation

Das Framework unterstützt mehrere benannte Wiki-Ziele und normale Markdown-Links. Das bestätigt grundsätzliche Flexibilität, beweist aber keine reibungslose Behandlung eines einzigen Obsidian-Vaults mit acht verschachtelten Git-Wurzeln. Die Primärquellenprüfung hat folgende Anpassungspunkte ergeben; genaue Codebelege stehen in der [externen Recherche](2026-09-09-agent-wiki-primary-sources.md):

- Projektinstallation kann vorhandene Agent-Bootstrap-Dateien einschließlich `AGENTS.md` ersetzen. DanielsVault hat bereits detaillierte, voneinander abweichende Repo-Regeln.
- Der Graph verwendet normalisierte Dateistämme als Seitenkennung. Wiederholte Namen wie `README.md` aus verschiedenen Verzeichnissen können kollabieren. Das betrifft den Nutzen eines Gesamtvault-Graphen, nicht die grundsätzliche Markdown-Lesbarkeit.
- SpecOps-Beziehungen über Entity-IDs werden nicht automatisch als dieselben semantischen Beziehungen verstanden. Ein Linkparser ersetzt das bestehende Domänenmodell nicht.
- Git-Sync verwendet eine breite Staging-/Commit-/Push-Sequenz. Diese passt nicht unverändert zu getrennten Repo-Grenzen und bereits vorhandenen Arbeitsänderungen.
- Das Framework bringt optionale weitere Such-/Graphfunktionen mit. Sie sollten nicht beiläufig einen zweiten Verantwortlichen für die bestehende QMD-Konfiguration oder Retrievalarchitektur schaffen.

Deshalb: zuerst das Pflegeprinzip und einen begrenzten Workflow übernehmen. Später einzelne Framework-Funktionen auswählen und an einem isolierten Testbestand mit typischen Dateinamen, Links und Repo-Grenzen erproben. Eine blinde Initialisierung am Vault-Root ist nicht die empfohlene Einführungsvariante.

## Vor- und Nachteile

| Vorteil | Gegenkosten bzw. Grenze |
|---|---|
| Erkenntnisse aus mehreren Sessions bleiben in einer dauerhaften Erklärung nutzbar. | Auswahl und fachliche Prüfung brauchen Zeit; nicht jede Session verdient eine neue Seite. |
| Aktueller Wissensstand und historische Quellen werden verständlicher getrennt. | Ohne Quellenänderungs- und Nachpflegeprozess veraltet auch das Wiki. |
| Wiederkehrende Fragen können mit weniger wiederholtem Lesen beantwortet werden. | Ingest und Pflege verlagern Modellarbeit nach vorn; eine Kostensenkung ist nicht garantiert. |
| Zusammenhänge, Konflikte und offene Fragen werden explizit. | Ein LLM kann Unterschiede fälschlich vereinheitlichen oder unbelegte Schlüsse dauerhaft speichern. |
| QMD bekommt kompakte, hochwertige Suchziele. | Original und Zusammenfassung können Suchergebnisse doppeln; unkuratiertes Material muss weiter erreichbar bleiben. |
| Markdown bleibt für Mensch und Agent lesbar und versionierbar. | Die Automationsskills, Metadatenkonventionen und optionale Werkzeuge verursachen Wartung und Kopplung. |

Ein Linkgraph zeigt dokumentierte Beziehungen; er beweist weder Vollständigkeit noch Kausalität oder faktische Richtigkeit. `lint` kann strukturelle Fehler finden, aber keine allgemeine Wahrheitsgarantie liefern. Projektinterne kleine Benchmarks sind keine belastbare Prognose für DanielsVault oder einen Vergleich gegen das hier bereits vorhandene QMD.

## Aufwand und sinnvoller Pilot

Die folgenden Werte sind Planungsschätzungen für Agent-Unterstützung mit menschlicher Prüfung, keine gemessenen Projektzeiten. Ein Arbeitstag entspricht etwa acht Arbeitsstunden; Modellkosten sind nicht beziffert. Quellen bleiben an Ort und Stelle, bestehende Infrastruktur wird weiterverwendet.

| Umfang | Geschätzter Gesamtaufwand |
|---|---|
| Begrenzter Pilot: RAG/QMD-Thema, 5–10 vorhandene Seiten, Pflegevertrag, aktuelle Übersicht, Quellen-/Linkprüfung, etwa 10 Vergleichsfragen | 0,5–1,5 Arbeitstage |
| Konzept in 2–3 aktiven Bereichen: je 10–20 wichtige Seiten, abgestimmte Metadaten, Scope-Auswahl, bestehende Indexpflege nutzen | 3–7 Arbeitstage insgesamt, einschließlich Pilot |
| Wiederholbarer Betrieb mit Quellenänderungserkennung, Herkunftszuordnung, kontrollierten Änderungen und Fehlerbehandlung | 1–2 zusätzliche Wochen, abhängig von den Quellformaten |
| Breiter historischer Backfill über den Vault | grob 2–6+ Wochen; Genauigkeit gering, weil Lesetiefe, externe Belege und gewünschte Seitenqualität den Aufwand dominieren |

Für ein wöchentliches kleines Änderungspaket ist anfänglich etwa eine halbe bis eine Stunde fachliche Prüfung pro aktivem Bereich eine sinnvolle Arbeitsannahme. Das muss am Pilot gemessen werden. PDF-/OCR-Erschließung, Session-Massenimport, widersprüchliche Altstände und proprietäre Originalquellen sind eigene Aufwandstreiber. Eine vollständige Frameworkanpassung ist in den kleinen Konzeptschätzungen nicht enthalten.

**Empfohlener Pilot:** die bestehende RAG/QMD-Dokumentation in `_shared/shared-ai-docs/docs/rag`. Sie ist klein, unmittelbar nützlich und enthält bereits nachweisbare widersprüchliche Einstiegsaussagen. Erfolg bedeutet: zehn typische Fragen finden die richtige heutige Quelle; geänderte Betriebsregeln aktualisieren die zugehörigen Übersichten; keine Verwechslung historischer Evidenz mit aktuellem Stand; keine ungewollte Domain-Mischung. Für die Fragen kann das vorhandene [RAG-Eval-Set](evaluation-set.md) als Ausgangspunkt dienen, nachdem seine inzwischen historischen Quellenannahmen geprüft wurden.

Erst wenn dieser Versuch spürbar wiederholte Recherche oder Korrekturarbeit spart, lohnt sich die Ausdehnung auf NCG und weitere aktive Themen. Der Nutzen hängt stärker von wenigen verlässlich gepflegten Seiten ab als von der vollständigen Migration aller Markdown-Dateien.
