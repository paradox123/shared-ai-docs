# Make-or-Buy-Entscheidungsvorlage: Work Package Control Plane

| Metadatum | Wert |
| --- | --- |
| Status | Desk Research und Vorbewertung abgeschlossen; Spike- und TCO-Nachweise offen |
| Bezugs-Spec | [`spec.md`](./spec.md) |
| Entscheidungs-ID | `MOB-WPCP-2026-01` |
| Decision Owner | Daniel |
| Technischer Owner | Daniel |
| Entscheidungsgremium | Daniel; vor Produktionsfreigabe zusätzlich Architecture, Security/Datenschutz und Operations |
| Bewertungsstand | 2026-09-05 |
| Betrachtungszeitraum für TCO | `3 Jahre` |
| Zielgröße | `zunächst ca. 20 Entwicklerinnen und Entwickler` |

> Diese Vorlage bewertet nicht, ob Codex als Agent-Harness ersetzt werden soll. Codex ist gemäß Spec gesetzt. Bewertet wird, welche Bestandteile der zentralen Work Package Control Plane selbst entwickelt, aus Open Source übernommen, als Managed Service bezogen oder hybrid zusammengesetzt werden.

## 1. Entscheidung in Kürze

### Entscheidungssatz

Für den nächsten lokalen Architektur-Spike wird **Microsoft Agent Framework für .NET mit Durable Extension und selbst gehosteten/BYO-Compute-Workern (C)** priorisiert. Vor jedem größeren Semantik-Spike muss Gate 0 einen produktionsfähigen, selbst hostbaren Open-Source-Backendpfad ohne verpflichtende zusätzliche Framework- oder Managed-Workflow-Service-Lizenzkosten belegen. Der lokale DTS-Emulator ist dafür nicht ausreichend.

MAF wird bevorzugte Implementierungsbasis, wenn Gate 0 sowie die offenen Gates G03, G06, G07 und G08 ohne Framework-Fork erfüllt werden, Codex als Harness erhalten bleibt und der notwendige Eigenbau beherrschbar ist. Temporal und kostenpflichtige Managed-Workflow-Dienste sind ausgeschlossen. Der vorhandene LangGraph-Pilot bleibt unverändert, unabhängig ausführbar, Verhaltensbaseline und sichere Rückfalloption.

### Gewählte Sourcing-Aufteilung

Die folgende Zielaufteilung gilt für Kandidat C und bleibt bis zum Spike vorläufig.

| Baustein | Make | Adopt/Open Source | Buy/Managed | Begründung |
| --- | :---: | :---: | :---: | --- |
| Fachliches Work-Package-Domainmodell und Zustandsübergänge | ✓ |  |  | Die Spec-Semantik ist anwendungsspezifisch und darf nicht vom Frameworkmodell bestimmt werden. |
| Durable Workflow, Timer, Signals und Recovery |  | ✓ |  | MAF/Durable Extension und ein in Gate 0 praktisch belegter selbst hostbarer Open-Source-Backendpfad werden übernommen. |
| Versionierter Codex Agent-Session-Adapter | ✓ |  |  | Kein Kandidat liefert die geforderte Codex-Session-Semantik fertig. |
| Geordnete Run History und Event-Projektion | ✓ |  | ✓ | Kanonisches Schema und Projektion bleiben eigen; persistente Standarddienste dürfen bezogen werden. |
| Artefaktspeicher und Retention | ✓ |  | ✓ | Referenzmodell und Redaction eigen; Blob/Object Storage als Infrastrukturservice. |
| Operator Client/Cockpit und Streaming | ✓ |  |  | DTS-Dashboard ist Betriebsoberfläche, nicht der fachliche Operator Client. |
| Repository-Authorization-Adapter | ✓ |  |  | Providerneutrale GitHub-/GitLab-/Azure-DevOps-Semantik ist fachlicher Anwendungscode. |
| Control Lease, Transfer und Forced Takeover | ✓ |  |  | Für keinen Kandidaten als fertiger Fachvertrag belegt. |
| Redaction, Audit und Compliance-Funktionen | ✓ |  | ✓ | Policy und Vor-Persistenz-Redaction eigen; Infrastruktur- und Auditdienste können managed sein. |
| Agent Evolution Loop | ✓ |  |  | Projektspezifische Logik mit externer Repository-Governance. |

### Entscheidergebnis

- Entscheidung: `ADOPT/MAKE – MAF BYO Compute für zusätzlichen lokalen Spike priorisiert; nur mit bestandenem OSS-Backend-Gate`
- Freigegebenes Budget: `noch offen; zunächst nur lokaler, zeitlich begrenzter Spike ohne bezahlte Cloud-Ressourcen`
- Erwarteter produktiver Pilot: `nach bestandenem Spike, belastbarer Aufwandsschätzung und Hostingentscheidung festzulegen`
- Re-Evaluation: `nach Spike sowie nach tatsächlichem GA-/Lifecycle-Nachweis der Durable Extension`
- Wesentliche Auflagen: `Gate 0 und G03/G06/G07/G08 bestehen; Codex bleibt Harness; LangGraph bleibt unverändert; Exportpfad und Security Review werden nachgewiesen`

## 2. Gegenstand und Grenze der Entscheidung

### Zu lösendes Problem

Ein langlebiger, issuegebundener Implementierungslauf soll viele kontextisolierte Codex-Aktivitäten koordinieren. Mehrere autorisierte Personen müssen denselben Lauf von verschiedenen Work Machines beobachten und nacheinander steuern können, ohne dass die Ausführung an einen Client oder Worker gebunden bleibt. Ausführung, kausale Historie, Artefakte, Recovery, Leases und Freigaben werden deshalb zentral verwaltet. Die Make-or-Buy-Entscheidung bestimmt, welcher Durable-Workflow-Kern übernommen oder bezogen wird und welche fachlichen Control-Plane-Bestandteile bewusst Eigenbau bleiben.

### In Scope

- zentraler, langlebiger Implementierungslauf pro freigegebenem Issue;
- getrennte Codex-Sessions für Implementierung, Reviews, Repair und weitere Agentenaktivitäten;
- deterministische Tests und Gates außerhalb des Sprachmodells;
- persistente, vollständig beobachtbare Run History mit Artefaktverweisen;
- Remote-Inspektion und Remote-Steuerung durch mehrere autorisierte Personen;
- Resume, Fork, Fresh Retry, Takeover, Cancel und Approval;
- Live Control über `interrupt` und `queue`;
- Durable Recovery, Idempotenz und Adoption bereits eingetretener externer Wirkungen;
- Repository-basierte Autorisierung für GitHub, später GitLab und Azure DevOps;
- Agent Evolution Loop mit externer menschlicher Freigabe über Repository Governance.

### Nicht Gegenstand dieser Entscheidung

- Ersatz von Codex durch einen anderen primären Agent-Harness;
- automatischer Merge, Deployment, Release oder autonome Produktfreigabe;
- eigenes Mitglieder-, Gruppen- oder ACL-System der Control Plane;
- endgültige Multi-Region-, SLO- oder Enterprise-Capacity-Architektur;
- Verwaltung von Branch Protection oder Reviewergruppen;
- Speicherung oder Anzeige privater interner Gedankengänge eines Modells.

### Feststehende Architekturentscheidungen

Diese Punkte dürfen durch eine vermeintlich attraktive Kaufoption nicht stillschweigend verändert werden:

1. Der `ImplementationRun` ist die zentrale Arbeitseinheit, nicht eine Agentensession.
2. Codex bleibt der bevorzugte Agent-Harness und wird über einen versionierten Adapter integriert.
3. Run History und Modellkontext sind getrennt; Aktivitäten erhalten begrenzten, explizit materialisierten Kontext.
4. Menschen arbeiten über einen Operator Client, nicht über eine zusätzliche Supervisor-Agentensession.
5. Pro Implementierungslauf existiert genau eine menschliche Control Lease.
6. Repositoryberechtigungen bleiben die Autorität für menschlichen Zugriff.
7. GitHub bleibt zunächst die sichtbare Projektion für Issue, PR, Head-SHA, Checks, Reviews und Merge.
8. Jeder neue Writer-Head invalidiert frühere Qualification und verlangt frische Tests und Reviews.

### Vorentscheidung für den Architektur-Spike

Für den ersten lokalen Architektur-Spike wird **Microsoft Agent Framework für .NET zusammen mit der Durable Extension und Durable Task** bevorzugt. Die Präferenz beruht auf zwei belegten Passungen:

- Der graphbasierte `.NET`-Workflow-Layer mit typisierten Executors, Edges, Events, Fan-out/Fan-in, Checkpoints und Human-in-the-Loop ist ein plausibler Implementierungspeer zum bestehenden LangGraph-Workflow-Layer.
- Die Durable Extension ergänzt persistente Agentensessions, verteilte Worker, Recovery, langlebige Wartezustände und deterministische Orchestrierung; ihre Eignung mit einem selbst hostbaren Open-Source-Backend bleibt vorab zu beweisen.

Diese Vorentscheidung ist **keine ungeprüfte Gleichwertigkeitsbehauptung**. Microsoft Agent Framework wird zur bevorzugten Implementierungsbasis, wenn der gemeinsame lokale Spike alle Muss-Kriterien nachweislich erfüllt. Insbesondere bleiben Adoption externer Git-/GitHub-Wirkungen, vollständig beobachtbare Work-Package-History, Codex-Session-Semantik, `interrupt`/`queue`, Control Lease, Repository Authorization und Redaction eigenständig zu beweisen.

Die Vergleichsrollen sind damit festgelegt:

- Der bestehende LangGraph-Pilot ist die unveränderte fachliche und verhaltensbezogene Baseline und bleibt unabhängig ausführbar.
- Microsoft Agent Framework plus Durable Extension ist der bevorzugte .NET-Kandidat.
- Temporal und kostenpflichtige Managed-Workflow-Dienste sind als Kandidaten und Fallbacks ausgeschlossen.
- Gate 0 prüft vorab, ob ein produktionsfähiger selbst hostbarer Open-Source-Backendpfad mit der Durable Extension existiert.

Siehe [`ADR 0008`](../../docs/adr/0008-prefer-microsoft-agent-framework-for-dotnet-control-plane-spike.md).

## 3. Zu vergleichende Optionen

Alle Optionen müssen denselben fachlichen Scope und denselben produktionsnahen Spike erfüllen. Kandidaten dürfen keine höhere Punktzahl erhalten, indem schwierige Spec-Bestandteile aus ihrem Angebot ausgeklammert werden.

| ID | Kandidat | Sourcing | Übernommener Kern | Wesentlicher Eigenbau |
| --- | --- | --- | --- | --- |
| A | Vollständiger .NET-Eigenbau | MAKE | .NET-Runtime, Datenbank und Infrastrukturbausteine | Durable Engine, Zustandsmodell, Recovery, History, Live Control, Domain, Codex-Adapter, API und UI |
| B | Bestehenden LangGraph-/Python-Piloten zentralisieren | STATUS QUO+ | LangGraph-Workflowmodell und vorhandene Pilotlogik | Durable Produktionshärtung, gemeinsame History, Live Control, Leases, Autorisierung, Codex-Adapter, API und UI |
| C | Microsoft Agent Framework .NET + Durable Extension, eigene Worker + Managed Durable Task Scheduler | HYBRID | .NET-Workflowmodell, Checkpoints und Durable-Task-Ausführung | Domain, Codex-Adapter, Event-/Artefaktspeicher, Leases, Providerautorisierung, API und UI |
| D | Microsoft Agent Framework .NET + Azure Functions + Managed Durable Task Scheduler | HYBRID/BUY | wie C, zusätzlich Managed Compute und Scaling | wie C; Codex-Ausführung voraussichtlich als externer Worker/Adapter |
| E | Temporal Core selbst betreiben + eigene .NET-Anwendung | AUSGESCHLOSSEN | Historisch bewertete Alternative | Nicht weiterzuverfolgen |
| F | Temporal Cloud + eigene .NET-Anwendung | AUSGESCHLOSSEN | Historisch bewertete Alternative | Nicht weiterzuverfolgen |

### Longlist

Die Entscheidung vom 2026-09-05 reduziert die aktive Shortlist auf C unter dem vorgeschalteten Open-Source-Gate. B bleibt fachliche Baseline und Rückfalloption. Die übrigen Optionen bleiben ausschließlich als historische Vergleichsevidence in den Tabellen erhalten.

| Kandidat | Kategorie | Prüfhypothese | Status | Quelle/Stand |
| --- | --- | --- | --- | --- |
| A – vollständiger .NET-Eigenbau | MAKE | maximale fachliche Kontrolle, aber Nachbau verteilter Workflow-Grundlagen | **bewertet, nicht bevorzugt** | E-001, E-014 |
| B – LangGraph-/Python-Pilot zentralisieren | STATUS QUO+ | höchste Wiederverwendung und schnellster fachlicher Start | **Baseline/Rückfalloption** | E-002, E-014 |
| C – MAF .NET + Durable Extension, eigene Worker + DTS | HYBRID | LangGraph-artiges Workflowmodell in .NET mit Durable-Task-Unterbau; Team-Fit reduziert Integrationsrisiko | **bevorzugter lokaler Spike** | E-010 bis E-014 |
| D – MAF .NET + Azure Functions + DTS | HYBRID/BUY | gleicher fachlicher Kern mit Managed Compute; Passung zu Codex-/Git-Workern unbewiesen | **nachgelagerte Hosting-Variante** | E-012, E-014 |
| E – Temporal Core selbst betreiben | ADOPT/MAKE | historisch bewertete Alternative | **ausgeschlossen** | E-014 |
| F – Temporal Cloud | HYBRID/BUY | historisch bewertete Managed-Alternative | **ausgeschlossen** | E-014 |
| DBOS | ADOPT/HYBRID | kompakter Durable Core | **nicht Shortlist-fähig**: kein verifiziertes produktionsreifes natives .NET SDK | E-014 |
| Prefect/Windmill | ADOPT/HYBRID | vorhandene Orchestrierungs- und UI-Bausteine | **Longlist**: Python-/Job-Automation-Fit statt bevorzugtem .NET-Agentenmodell | E-014 |
| Spezialisierte Agent-Control-Plane | BUY | möglicher hoher Funktionsumfang | **RFI-Kategorie**, mangels konkretem Anbieter/Angebot nicht bewertbar | E-014 |

### Ausgeschlossene Kandidaten

| Kandidat | Ausschlussgrund | Beleg | Entscheider/Datum |
| --- | --- | --- | --- |
| Temporal Core und Temporal Cloud | Per Produktentscheidung ausgeschlossen; kein weiterer Spike oder Fallback | aktuelle Produktentscheidung | Daniel, 2026-09-05 |
| Kostenpflichtige Managed-Workflow-Dienste einschließlich produktivem Managed DTS | Verletzt den geforderten lizenzkostenfreien, selbst hostbaren Open-Source-Pfad | Gate 0 | Daniel, 2026-09-05 |
| DBOS | Kein verifiziertes produktionsreifes natives .NET SDK; verletzt den für diese Entscheidung relevanten Team-/Stack-Fit | E-014 | Daniel, 2026-09-05 |
| GitHub Actions/`gh-aw` als Control-Plane-Kern | Event-/CI-Unterbau ersetzt keine adressierbaren langlebigen Sessions, Leases und gemeinsame Run History | E-001, E-002, E-014 | Daniel, 2026-09-05 |

## 4. Muss-Kriterien und Knock-out-Gates

### Bewertungslogik

Jedes Gate wird für die **Gesamtlösung** bewertet, nicht nur für das Produkt. Zulässige Erfüllungsarten:

- `N` – nativ vorhanden;
- `K` – durch dokumentierte Konfiguration vorhanden;
- `E` – durch klar abgegrenzte eigene Erweiterung erreichbar;
- `U` – unklar oder nur durch unbewiesene Annahme;
- `X` – nicht erreichbar oder widerspricht dem Produktmodell.

`U` und `X` bedeuten bis zum Gegenbeweis **No-Go**. Bei `E` müssen Aufwand, Betriebsverantwortung und Spike-Evidence ausgewiesen werden; ein großer Eigenbauanteil wird zusätzlich in TCO, Time-to-Value und Integrationsrisiko bewertet.

| ID | Muss-Kriterium | A | B | C | D | E | F | Geforderter Beleg |
| --- | --- | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| G01 | Codex bleibt Agent-Harness; kein erzwungener Austausch gegen proprietären Harness | E | N | E | U | E | E | realer Codex-Lauf über Adapter |
| G02 | Ein Implementierungslauf bleibt zentral, issuegebunden und überlebt Client-, Worker- und Serverwechsel | E | E | K | K | K | K | Restart-/Reconnect-Test |
| G03 | Sessions können erstellt, gelesen, resumiert, geforkt und gestoppt werden; Session-IDs bleiben stabil | U | U | U | U | U | U | Codex-Adapter-Spike |
| G04 | Viele kontextisolierte Aktivitäten werden unter einer gemeinsamen Run History korreliert | E | E | N | N | N | N | UI/API-Evidence |
| G05 | Nachrichten, Toolaufrufe, Ergebnisse, Fehler, Diffs, Tests und Artefakte sind beobachtbar und kausal geordnet | E | E | E | E | E | E | Event-Stream-Demo |
| G06 | Live Control unterstützt adressiertes `interrupt` und dauerhaft geordnetes `queue` | U | U | U | U | U | U | Ausfall- und Zustellungstest |
| G07 | Resume, Fork und Fresh Retry besitzen die in der Spec definierten unterschiedlichen Semantiken | U | U | U | U | U | U | Identitäts-/History-Test |
| G08 | Crash-Recovery erzeugt keine doppelten externen Wirkungen; vorhandene Wirkungen werden adoptiert | U | U | U | U | U | U | Fault-Injection-Test |
| G09 | Genau eine Control Lease pro Lauf; CAS/Fencing verhindert konkurrierende Mutationen | E | E | E | E | E | E | Concurrency-Test |
| G10 | Control Transfer und auditierter Forced Takeover funktionieren atomar | E | E | E | E | E | E | Drei-Benutzer-Test |
| G11 | Repository Authorization statt eigener Mitglieder-/ACL-Liste | E | E | E | E | E | E | Provider-Contract-Test |
| G12 | Entzogene Rechte werden bei Verbindung und sicherheitsrelevanter Mutation hinreichend aktuell wirksam | E | E | E | E | E | E | Revocation-Test |
| G13 | Secrets und sensible Daten werden vor persistenter History, Artefakten und UI redigiert | E | E | E | E | E | E | kontrollierter Leak-Test |
| G14 | Drei unabhängige Reviews prüfen dieselbe Head-SHA ohne gegenseitigen aktiven Kontext | E | N | E | E | E | E | Context-Isolation-Test |
| G15 | Operator Client setzt einen Event-Stream nach Reconnect lücken- und duplikatfrei fort | E | E | E | E | E | E | Cursor-/Reconnect-Test |
| G16 | Menschliche Identitäten und Service-Identitäten bleiben getrennt und auditierbar | E | E | E | E | E | E | Audit-Evidence |
| G17 | Kein automatischer Merge, Release oder selbstgenehmigte Agent-Definition-Änderung | K | N | K | K | K | K | Policy-/End-to-End-Test |
| G18 | Export- und Exit-Pfad für History, Artefakte, Zustände und Korrelationen ist praktikabel | E | K | E | E | K | E | Restore/Exit-Probe |

### Ergebnis der Gate-Prüfung

| Option | Alle Gates erfüllt? | Offene `U` | Eigenbau-Erweiterungen `E` | Ergebnis |
| --- | :---: | ---: | ---: | --- |
| A | Nein | 4 | 13 | nur Referenz für maximale Eigenkontrolle; kein Spike vorgesehen |
| B | Nein | 4 | 10 | Baseline und Rückfalloption; vorhandene Pilot-Evidence weiterverwenden |
| C | Nein | 4 | 11 | **Shortlist; bevorzugter Spike** zur Schließung von G03/G06/G07/G08 |
| D | Nein | 5 | 10 | erst nach C betrachten; zusätzlich G01 für Functions-Hosting offen |
| E | Nein | 4 | 10 | historischer Vergleich; per Produktentscheidung ausgeschlossen |
| F | Nein | 4 | 11 | historischer Vergleich; per Produktentscheidung ausgeschlossen |

Die vielen `E` sind kein Produktmangel, sondern zeigen die eigentliche Systemgrenze: Kein Kandidat liefert die fachliche Control Plane, den Codex-Adapter oder die Repository-Governance fertig. G03, G06, G07 und G08 sind für alle Kandidaten unbewiesen und dürfen erst nach dem gemeinsamen Spike von `U` auf `N`, `K` oder `E` gesetzt werden.

## 5. Gewichtete Nutzwertanalyse

### Skala und Berechnung

- `0` = nicht erfüllt;
- `1` = nur mit grundlegendem Umbau/hohem Risiko;
- `2` = erhebliche Lücken;
- `3` = ausreichend, relevante Zusatzarbeit;
- `4` = gut, geringe beherrschbare Lücken;
- `5` = vollständig und belastbar nachgewiesen.

Halbe Punkte sind zulässig, wenn die Evidence zwischen zwei Stufen liegt. Die Desk-Research-Werte besitzen bis zum Spike eine Unsicherheit von ungefähr ±3–5 Gesamtpunkten; Unterschiede innerhalb dieses Korridors sind keine belastbare Rangentscheidung.

Gewichtete Punkte je Kriterium:

```text
gewichtete Punkte = Gewicht × Bewertung / 5
Gesamtergebnis = Summe der gewichteten Punkte (maximal 100)
```

Eine hohe Gesamtpunktzahl kann ein nicht erfülltes Muss-Kriterium nicht kompensieren.

### Empfohlene Kriterien und Gewichte

| ID | Kriterium | Gewicht | Leitfrage |
| --- | --- | ---: | --- |
| N01 | Fachliche Spec-Abdeckung | 18 | Wie viel der Work-Package-Semantik ist ohne Umgehung oder Modellbruch umsetzbar? |
| N02 | Durable Correctness und Recovery | 12 | Wie belastbar sind Replay, Idempotenz, Timer, Signals, Adoption und Crash-Recovery? |
| N03 | Codex- und Session-Integration | 10 | Wie sauber lassen sich Codex-Ereignisse, Resume, Fork, Stop und Versionierung integrieren? |
| N04 | Observability und Run History | 10 | Wie vollständig, geordnet, filterbar und exportierbar ist die beobachtbare Ausführung? |
| N05 | Menschliche Remote-Steuerung | 8 | Wie gut passen Control Lease, Live Commands, Rollenwechsel und mehrere Clients? |
| N06 | Security, Datenschutz und Audit | 10 | Wie gut sind Redaction, Identitätstrennung, Autorisierung, Audit und Retention abgedeckt? |
| N07 | Erweiterbarkeit und Providerneutralität | 7 | Wie leicht sind neue Aktivitäten sowie GitLab/Azure-DevOps-Adapter anschließbar? |
| N08 | Betrieb, Reife, Team-Fit und Support | 7 | Wie hoch sind Reife, Diagnosefähigkeit, Upgrade-Sicherheit, vorhandene Technologiekompetenz und verfügbare Unterstützung? |
| N09 | Time-to-Value | 5 | Wie schnell ist der verifizierte vertikale Pilot und danach ein nutzbarer Betrieb erreichbar? |
| N10 | Drei-Jahres-TCO | 8 | Wie hoch sind Vollkosten inklusive Eigenentwicklung, Betrieb und Exit? |
| N11 | Lock-in und Reversibilität | 5 | Wie portabel sind Daten, Workflows, Adapter und Betriebswissen? |
|  | **Summe** | **100** |  |

### Bewertungsmatrix

In die Bewertungsfelder kommt jeweils eine Punktzahl von 0 bis 5. Jede Punktzahl benötigt mindestens eine Evidence-ID oder eine ausdrücklich markierte Annahme.

| Kriterium | Gewicht | A | B | C | D | E | F | Evidence/Kommentar |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| N01 Fachliche Spec-Abdeckung | 18 | 4 | 4 | 4 | 4 | 3 | 3 | Alle benötigen Domain-Eigenbau; B besitzt Pilot-Prior-Art, C/D ein passendes Workflowmodell (E-001, E-002, E-011, E-014) |
| N02 Durable Correctness und Recovery | 12 | 2 | 3 | 4 | 4 | 5 | 5 | Temporal ist die Reife-Referenz; MAF nutzt Durable Task, bleibt aber spikepflichtig (E-012, E-014) |
| N03 Codex- und Session-Integration | 10 | 3 | 4 | 4 | 3 | 4 | 4 | B hat Pilotnähe; C erlaubt eigene langlebige Worker; D hat zusätzlichen Functions-Fit zu beweisen (E-002, E-014) |
| N04 Observability und Run History | 10 | 3 | 4 | 4 | 4 | 4 | 4 | Engine-History reicht nicht; kanonischer Event-/Artefaktspeicher bleibt Eigenbau (E-001, E-011, E-014) |
| N05 Menschliche Remote-Steuerung | 8 | 3 | 2 | 3 | 3 | 4 | 4 | Temporal Signals/Updates sind näher am Bedarf; adressiertes `interrupt`/`queue` bleibt überall offen (E-003, E-014) |
| N06 Security, Datenschutz und Audit | 10 | 3 | 4 | 4 | 4 | 4 | 4 | Bewertung beruht auf Architekturkontrolle, nicht auf abgeschlossener Vertragsprüfung (E-009, E-014) |
| N07 Erweiterbarkeit und Providerneutralität | 7 | 5 | 3 | 4 | 4 | 4 | 4 | Eigene Domain-/Providerports sichern Neutralität; B bringt Python-Bindung mit (E-007, E-014) |
| N08 Betrieb, Reife, Team-Fit und Support | 7 | 2 | 3 | 3.5 | 3 | 3 | 4 | C profitiert vom .NET-Team-Fit; F von höherer Engine-Reife und Managed Betrieb (E-010, E-013, E-014) |
| N09 Time-to-Value | 5 | 1 | 5 | 4 | 3 | 2 | 3 | B startet vom Pilot; C nutzt .NET-Kompetenz; Self-hosting kostet Anlaufzeit (E-002, E-010, E-014) |
| N10 Drei-Jahres-TCO | 8 | 1 | 3 | 3 | 3 | 2 | 3 | Nur relative Vorbewertung; belastbare Mengen, PT-Sätze und Angebote fehlen (E-014) |
| N11 Lock-in und Reversibilität | 5 | 5 | 4 | 3 | 2 | 3 | 2 | Managed Scheduler/Cloud senken Portabilität; eigene kanonische History ist Pflicht (E-014) |
| **Gewichtete Gesamtpunkte** | **100** | **59,4** | **71,0** | **75,1** | **70,4** | **71,2** | **74,2** | Desk Research, keine Produktionsfreigabe |

Interpretation: C und F liegen innerhalb der Unsicherheit praktisch gleichauf. C erhält den Vorzug für den lokalen Spike, weil die .NET-Nähe voraussichtlich Entwicklungs- und Ownership-Risiken senkt. F ist der stärkere Reife- und Durable-Correctness-Benchmark. Ein nicht bestandenes Gate beendet die jeweilige Option unabhängig von der Punktzahl.

### Sensitivitätsanalyse

Die Entscheidung muss stabil bleiben, wenn unsichere Annahmen oder strategische Prioritäten variieren.

| Szenario | Geänderte Annahme/Gewichte | Rang 1 | Rang 2 | Ändert sich die Entscheidung? |
| --- | --- | --- | --- | :---: |
| Baseline | Gewichte wie oben | C | F | Nein; Abstand nicht belastbar, Spike-Reihenfolge bleibt C vor F |
| Kostenfokus | TCO auf 15; Reduktion bei Spec-Abdeckung und Observability | B | C | Möglich; ohne Mengengerüst nur qualitative Tendenz |
| Risikofokus | Recovery + Security auf zusammen 35 | F | C | Nur historische Sensitivität; Temporal bleibt unabhängig vom Score ausgeschlossen |
| Speed-Fokus | Time-to-Value auf 15 | B | C | Ja; B gewinnt kurzfristig, trägt aber höhere langfristige Härtungsunsicherheit |
| Buy-Preis +30 % | DTS-/Functions-/historische Vergleichskosten steigen um 30 % | B | C | Nur historische Sensitivität; ausgeschlossene Kandidaten werden nicht reaktiviert |
| Nutzungsvolumen ×3 | Läufe, Events und Artefakte verdreifachen sich | C | F | Unklar; muss mit Referenzlast und konkreten Preisformeln gerechnet werden |
| Anbieter-/Projekt-Exit | Kandidat wird in 12 Monaten abgekündigt/inaktiv | B | A | Ja; Portabilität und vorhandener Pilot dominieren |

## 6. Vollkostenrechnung

### Gemeinsame Annahmen

| Annahme | Wert | Quelle | Sicherheit |
| --- | --- | --- | --- |
| Nutzerzahl Jahr 1 / Jahr 3 | 20 / offen | Spec/Planung | mittel |
| Implementierungsläufe pro Monat | nicht erhoben | Messung aus Pilot/Planung erforderlich | niedrig |
| Agentenaktivitäten pro Lauf | nicht erhoben | Referenzlauf im Spike | niedrig |
| Events/Artefaktvolumen pro Lauf | nicht erhoben | Telemetrie des Referenzlaufs | niedrig |
| Aufbewahrungsdauer | nicht festgelegt | Security-/Datenschutz-Policy erforderlich | niedrig |
| Vollkosten interner Personentag | nicht vorliegend | Controlling erforderlich | niedrig |
| Zielverfügbarkeit / Supportzeit | nicht festgelegt | Betriebsmodell erforderlich | niedrig |
| Preissteigerung pro Jahr | nicht festgelegt | Szenario/Angebot erforderlich | niedrig |
| Wechselkurs, falls relevant | nicht festgelegt | nur bei Nicht-EUR-Angebot | niedrig |

### Aufwand und Kosten je Option

Alle Werte ohne Umsatzsteuer; interne Aufwände werden mit dem Vollkostensatz bewertet. Anbieterpreise müssen Datum, Edition, Mindestabnahme und nutzungsabhängige Einheiten enthalten.

| Kostenblock | A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- | --- |
| Discovery, Architektur und Spike | hoch | niedrig | mittel | mittel | mittel | mittel |
| Erstimplementierung Domain/Workflow | sehr hoch | hoch | mittel | mittel | mittel | mittel |
| Codex-Adapter | hoch | mittel | mittel | hoch | mittel | mittel |
| Operator Client und API | hoch | hoch | hoch | hoch | hoch | hoch |
| Provideradapter und Security | hoch | hoch | hoch | hoch | hoch | hoch |
| Migration/Parallelbetrieb | mittel | niedrig | mittel | mittel | mittel | mittel |
| Lizenzen/Subscription über 3 Jahre | keine Frameworklizenz | keine Frameworklizenz | DTS nutzungsabhängig | DTS + Functions nutzungsabhängig | keine Engine-Lizenz; Infrastruktur separat | Temporal-Cloud-Grundpreis + Nutzung |
| Infrastruktur über 3 Jahre | hoch | mittel bis hoch | Worker + Event-/Artefaktspeicher | Functions + Event-/Artefaktspeicher | sehr hoch | Anwendung + Event-/Artefaktspeicher |
| Betrieb/On-call über 3 Jahre | sehr hoch | hoch | mittel | niedrig bis mittel | sehr hoch | mittel |
| Wartung, Upgrades und Regressionstests | sehr hoch | hoch | mittel | mittel | hoch | mittel |
| Support/Professional Services | intern/optional | intern/optional | Azure-Vertrag abhängig | Azure-Vertrag abhängig | intern/Temporal-Angebot | Edition/Vertrag abhängig |
| Security, Datenschutz und Audit | hoch | hoch | hoch | hoch | hoch | hoch |
| Schulung und Enablement | mittel | mittel bis hoch | niedrig bis mittel | mittel | mittel | mittel |
| Exit-/Ablösungsvorsorge | mittel | niedrig bis mittel | mittel | hoch | mittel | hoch |
| Risikopuffer | hoch | mittel bis hoch | mittel | mittel bis hoch | hoch | mittel |
| **Drei-Jahres-TCO** | **offen; erwartbar hoch** | **offen; kurzfristig günstig** | **offen; plausibel mittleres Niveau** | **offen; stärker nutzungsabhängig** | **offen; erwartbar hoch** | **offen; Angebot erforderlich** |

Absolute TCO-Zahlen wären ohne Lastprofil, internen Vollkostensatz, Retention und Anbieterangebote Scheingenauigkeit. Für die spätere Rechnung gilt je Kandidat:

```text
3-Jahres-TCO = einmalige interne PT × PT-Satz
              + laufende interne PT × PT-Satz
              + Subscription/Nutzung + Infrastruktur + Support
              + Migration/Exit + Risikopuffer
```

Für C sind mindestens DTS-Orchestrationsaktionen, Work Items und Scheduler Units zu messen; für D zusätzlich Functions-Ausführung und Hosting; für F Temporal-Grundpreis, Actions, Storage und Support-Edition. Veröffentlichte Einstiegspreise sind nur Preisparameter, keine TCO-Aussage (E-014).

### Wirtschaftlicher Nutzen

| Nutzenhebel | Messgröße | Baseline | Ziel | Monetarisierung/Begründung |
| --- | --- | ---: | ---: | --- |
| weniger manuelle Laufüberwachung | Stunden pro Lauf | noch nicht gemessen | im Pilot messen | Monetarisierung nach gemessener Zeitersparnis |
| kürzere Recovery nach Fehlern | MTTR | noch nicht gemessen | im Fault-Injection-Test messen | vermiedene Entwickler- und Betriebszeit |
| weniger doppelte/externe Fehlwirkungen | Vorfälle pro Quartal | noch nicht gemessen | 0 unbehandelte Doppelwirkungen | vermiedene Reparatur- und Auditkosten |
| schnellere Durchlaufzeit Issue → verifizierter PR | Stunden/Tage | LangGraph-Pilot messen | C und F gegen Baseline messen | Wert der verkürzten Lead Time separat festlegen |
| weniger Kontextverlust bei Personenwechsel | Eskalationen/Nacharbeit | noch nicht gemessen | lückenlose Übernahme über Operator Client | vermiedene Rekonstruktion und Wiederholung |
| wiederverwendbare Agent- und Provideradapter | vermiedene PT | GitHub-Pilot als Ausgangspunkt | zweiter Provider ohne Domain-Umbau | vermiedener Parallelcode bei GitLab/Azure DevOps |

## 7. Produktionsnaher Architektur-Spike

### Gemeinsamer Spike-Scope

Jeder Shortlist-Kandidat muss denselben schwierigsten vertikalen Schnitt zeigen:

1. Benutzer A startet über ein autorisiertes GitHub Issue einen zentralen Implementierungslauf.
2. Ein zentraler Codex-Testworker führt mehrere beobachtbare Schritte aus und scheitert kontrolliert nach mindestens einer externen Wirkung.
3. Benutzer B öffnet den Lauf von einer anderen Work Machine und sieht Nachrichten, Toolaufrufe, Ergebnisse, Artefakte, Head-SHA und Fehlerursache.
4. Benutzer B übernimmt die Control Lease und wählt bewusst Resume, Fork oder Fresh Retry; der Spike dokumentiert die jeweils korrekte Sessionsemantik.
5. Ein `interrupt`- und ein `queue`-Command werden an einen expliziten Activity Attempt gesendet.
6. Ein erzwungener Neustart zwischen Persistierung und Zustellung beweist lückenfreie, genau einmal wirksame Fortsetzung oder Adoption.
7. Deterministische Tests und drei isolierte Reviews qualifizieren dieselbe neue Head-SHA.
8. Benutzer C gibt den verifizierten Head frei; automatischer Merge bleibt ausgeschlossen.
9. Ein konkurrierender oder veralteter mutierender Request wird ohne zweite Wirkung abgelehnt.
10. Der Operator Client verbindet sich neu und setzt den Stream ab bestätigter Eventposition ohne Lücke oder Duplikat fort.

### Spike-Messwerte

| Messwert | Ziel/Schwelle | A | B | C | D | E | F |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Muss-Tests bestanden | `18/18` | nicht geplant | Baseline offen | offen | nach C | nur bei Self-hosting-Vorgabe | nach C bei Bedarf |
| Unbehandelte Doppelwirkung nach Fault Injection | `0` | – | offen | offen | – | – | offen |
| Verlorene/duplizierte Events nach Reconnect | `0` | – | offen | offen | – | – | offen |
| Zeit bis zur Remote-Diagnose | Ziel im PRD festlegen | – | Baseline messen | messen | – | – | messen |
| Zeit bis zur korrekten Fortsetzung | Ziel im PRD festlegen | – | Baseline messen | messen | – | – | messen |
| Eigenbau-Code für den Spike | gegen B und F vergleichen | – | Baseline messen | messen | – | – | messen |
| Betriebs- und Deployment-Komponenten | minimieren; vollständig inventarisieren | – | Baseline messen | messen | – | – | messen |
| Gemessene Kosten pro Referenzlauf | transparent und hochrechenbar | – | Baseline messen | DTS-Emulator lokal; Cloud-Projektion separat | – | – | Cloud-Test/Angebot |
| Offene kritische Risiken | `0` vor Produktionsfreigabe | – | offen | offen | – | – | offen |

Spike-Reihenfolge: zuerst Gate 0 für C, danach C gegen die vorhandene B-Baseline. Schließt C ein hartes Gate nicht oder existiert kein produktionsfähiger selbst hostbarer Open-Source-Backendpfad, endet dieser Kandidat; B bleibt aktiv und eine andere Open-Source-Architektur benötigt eine neue Entscheidung. Dadurch wird die Make-or-Buy-Session nicht mit der Ausarbeitung des Spike-Plans vermischt; dafür existiert E-015.

### Abbruchkriterien für einen Spike

- Codex kann nicht als gleichwertiger Harness integriert werden.
- Die Lösung kann aktive Sessions nicht stabil adressieren oder `interrupt`/`queue` nicht zuverlässig abbilden.
- Externe Wirkungen werden bei Restart oder Retry unkontrolliert wiederholt.
- Zentrale History ist nur eine flüchtige UI-Projektion und nicht vollständig exportierbar.
- Repository Authorization oder Identitätstrennung erfordert eine zweite dauerhafte Mitgliederverwaltung.
- Notwendige Telemetrie oder Artefakte verlassen unzulässig die definierte Daten- oder Vertrauensgrenze.
- Der Kandidat erfordert einen Framework-Fork oder einen unbeherrschbaren eigenen Durable Core.

## 8. Security, Datenschutz, Vertrag und Betrieb

### Prüffragen

| Bereich | Frage | A | B | C | D | E | F | Evidence |
| --- | --- | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| Datenstandort | Wo liegen Prompts, Toolresultate, Diffs, Logs und Artefakte? | intern definierbar | intern definierbar | geteilt; festzulegen | Azure; festzulegen | intern definierbar | Temporal Cloud; Region/Vertrag prüfen | E-014 |
| Modelltraining | Werden Inhalte für Training oder Produktverbesserung verwendet? Abschaltbar? | n. a. | n. a. für OSS-Kern | n. a. für Framework; angebundene Modelle separat | wie C | n. a. für OSS-Kern | Vertrag prüfen | E-014 |
| Redaction | Erfolgt Redaction vor dauerhafter Aufnahme und vor Export? | Eigenbau | Eigenbau | Eigenbau vor DTS/History | Eigenbau vor DTS/History | Eigenbau | Eigenbau vor Cloud/History | E-001, E-014 |
| Verschlüsselung | At rest, in transit, Schlüsselverwaltung, BYOK-Anforderung? | intern | intern | DTS/Storage-Konfiguration prüfen | Azure-Konfiguration prüfen | intern | Edition/Vertrag prüfen | E-014 |
| Mandantentrennung | Wie werden Repositories, Organisationen und Service-Identitäten getrennt? | Eigenbau | Eigenbau | Eigenbau + Scheduler-Isolation | Eigenbau + Azure-Isolation | Eigenbau + Namespace-Modell | Eigenbau + Namespace-/Account-Modell | E-001, E-014 |
| Audit | Sind menschliche und technische Aktionen unveränderlich korrelierbar? | Eigenbau | Eigenbau | Eigenbau auf Engine-Events | Eigenbau auf Engine-Events | Eigenbau auf Temporal-History | Eigenbau auf Temporal-History | E-001, E-014 |
| Retention/Löschung | Sind Aufbewahrung, Legal Hold, Löschung und Nachweis konfigurierbar? | intern | intern | Policy + DTS/Storage prüfen | Policy + Azure prüfen | intern | Cloud-Funktionen/Vertrag prüfen | E-014 |
| Zugriff | Unterstützt das Produkt providerabgeleitete Autorisierung ohne Schatten-ACL? | Eigenbau | Eigenbau | Eigenbau | Eigenbau | Eigenbau | Eigenbau | E-009 |
| Lieferkette | SBOM, Signaturen, CVE-Prozess und Patch-SLA vorhanden? | intern | OSS-Prozess prüfen | Microsoft OSS/Azure prüfen | Microsoft OSS/Azure prüfen | Temporal OSS + intern | Temporal-Vertrag prüfen | E-013, E-014 |
| Vertrag | DPA/AVV, Unterauftragsverarbeiter, Haftung und Exit-Unterstützung akzeptabel? | n. a. | n. a. für OSS-Kern | Azure-Vertrag nötig | Azure-Vertrag nötig | n. a. für OSS-Kern | Temporal-Vertrag nötig | E-014 |
| Verfügbarkeit | SLA/SLO, RPO/RTO, Backup/Restore und Support-Eskalation passend? | intern zu liefern | intern zu liefern | geteilt | primär Azure + Anwendung | intern zu liefern | geteilt | E-014 |
| Preismodell | Kosten für User, Runs, Events, Storage, Egress und Support prognostizierbar? | interne PT/Infra | interne PT/Infra | DTS-Nutzungsmodell; Last messen | DTS + Functions; Last messen | interne PT/Infra | Grundpreis + Nutzung; Angebot nötig | E-014 |

### Betriebsverantwortung

| Verantwortung | Intern | Anbieter | Geteilt | Konkreter Owner/Eskalationspfad |
| --- | :---: | :---: | :---: | --- |
| Workflow-Engine und Persistenz |  |  | X | Engineering für MAF/Worker; Microsoft für DTS-Plattform |
| Codex-Adapter und Kompatibilität | X |  |  | Engineering |
| Domainlogik und Zustandsmigrationen | X |  |  | Engineering/Product |
| Operator Client/API | X |  |  | Engineering |
| Event-/Artefaktspeicher | X |  |  | Engineering/Operations; nicht als Durable-Entity-Payload modellieren |
| Security Patches |  |  | X | Engineering für Anwendung/Dependencies; Microsoft für DTS |
| Backup, Restore und Disaster Recovery |  |  | X | Operations für eigene Stores; Microsoft gemäß DTS-Vertrag |
| Incident Response |  |  | X | Operations als Primary, Microsoft-Support für DTS-Eskalation |
| Support für Entwickler | X |  |  | Engineering Lead; Microsoft-Support optional |

## 9. Risiken und Gegenmaßnahmen

Bewertung: Eintrittswahrscheinlichkeit `1–5`, Auswirkung `1–5`, Risikowert `E × A`.

| ID | Option | Risiko | E | A | Wert | Gegenmaßnahme | Restrisiko | Owner |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| R01 | C/D/F | Anbieter-/Frameworkmodell ersetzt oder abstrahiert Codex unzureichend | 3 | 5 | 15 | versionierter Adapter; Codex bleibt eigener Port; G01/G03-Spike | mittel | Engineering |
| R02 | alle | Kandidat erfordert unerwartet viel Domain- und UI-Eigenbau | 4 | 4 | 16 | Spike misst Module/PT/LOC; Abbruchschwelle vor PRD festlegen | mittel | Engineering/Product |
| R03 | alle | Replay wiederholt Git-/GitHub-/Toolwirkungen | 3 | 5 | 15 | Idempotency Keys, Reconciliation, Adoption, Fault Injection | niedrig bis mittel | Engineering |
| R04 | alle | Zentrale History wird zum Secret-/Datenschutzrisiko | 3 | 5 | 15 | Redaction vor Persistierung, Least Privilege, Retention | mittel | Security/Engineering |
| R05 | C/D/F | Managed-Kosten skalieren mit Events/Storage unerwartet | 3 | 4 | 12 | Referenzlast, Preisformeln, Budgetalarm, Angebot | mittel | Finance/Operations |
| R06 | B/C/E | Open-Source-Projekt verliert Maintainer oder ändert Lizenz/API | 2 | 4 | 8 | Version Pinning, Upgrade-Probe, Fork-/Exit-Fähigkeit | mittel | Engineering |
| R07 | A/B/E | Eigenbetrieb bindet dauerhaft seltene Distributed-Systems-Kompetenz | 4 | 4 | 16 | Managed Kern bevorzugen, Runbooks, Ownership und Bus-Factor-Ziel | mittel | Engineering/Operations |
| R08 | C/D/F | Lock-in durch proprietäre History oder Workflowdefinitionen | 3 | 4 | 12 | kanonische Domain-History, Adaptergrenze, Restore-/Exit-Probe | mittel | Architecture |
| R09 | alle | Providerneutralität wird nur behauptet, aber GitHub hart codiert | 3 | 3 | 9 | Ports/Contracts für GitHub, GitLab und Azure DevOps | niedrig bis mittel | Engineering |
| R10 | alle | Control Lease oder Live Commands erzeugen Race Conditions | 3 | 5 | 15 | CAS/Fencing, adressierte Commands, Konkurrenztests | niedrig bis mittel | Engineering |

## 10. Entscheidungsbegründung

### Warum die gewählte Option gewinnt

**Vorläufig gewählt wird Option C für einen zusätzlichen lokalen Architektur-Spike:** Microsoft Agent Framework für .NET mit Durable Extension, eigenen langlebigen Workern und zunächst lokalem Durable-Task-Emulator. Der Emulator dient nur der Entwicklung. Eine Produktionseinführung setzt voraus, dass Gate 0 einen kompatiblen produktionsfähigen selbst hostbaren Open-Source-Backendpfad belegt.

C verbindet ein zu LangGraph vergleichbares graph-/eventbasiertes Workflowmodell mit Durable-Task-Ausführung und dem vorhandenen .NET-Team-Fit. Dadurch soll weder Codex als Harness ersetzt noch ein eigener Durable Core gebaut werden. Ausschlaggebend für die Spike-Reihenfolge sind Team-Fit, erwartete Time-to-Value, der nachzuweisende Open-Source-Betriebspfad und die Möglichkeit, die fachliche Control Plane als eigene, frameworkunabhängige .NET-Schicht zu halten.

Dies ist **keine Produktionsfreigabe**. C muss zuerst Gate 0 und anschließend insbesondere G03, G06, G07 und G08 praktisch schließen. Scheitert eines dieser Gates, erfordert C faktisch einen eigenen Durable Core oder ist der Reife-/Upgradepfad nicht akzeptabel, wird C gestoppt. Der bestehende LangGraph-Pilot bleibt unverändert; eine andere Open-Source-Architektur wird nur nach einer neuen Entscheidung untersucht.

### Warum die Alternativen nicht gewählt wurden

| Option | Stärkster Vorteil | Entscheidender Nachteil | Was müsste sich ändern? |
| --- | --- | --- | --- |
| A – vollständiger .NET-Eigenbau | maximale Kontrolle und Reversibilität | Nachbau von Durable Execution und höchster Entwicklungs-/Betriebsaufwand | nur wenn alle Engines zentrale Muss-Kriterien verletzen oder externe Plattformen ausgeschlossen werden |
| B – LangGraph-Pilot zentralisieren | vorhandene Evidence und schnellster Start | Python-/Pilotarchitektur benötigt umfangreiche Produktionshärtung; schwächere Live-Control-/Durable-Evidence | bleibt unveränderte Baseline, wenn C scheitert |
| C – MAF BYO Worker + DTS | .NET-Team-Fit, passendes Workflowmodell, Managed Durable Core | Durable Extension/Reife, Codex-Session-Semantik und DTS-Bindung noch zu beweisen | **gewählt für Spike; Produktion nur nach Gates, TCO und Security** |
| D – MAF Functions + DTS | geringerer Compute-Betrieb und elastisches Hosting | Functions-Modell kann schlecht zu langlebigen Codex-/Git-Workern passen; stärkere Azure-Bindung | wenn C fachlich besteht und ein separater Hosting-Spike die Worker-Passung belegt |
| E – Temporal Core self-hosted | historisch bewertete Durable Semantik | per Produktentscheidung ausgeschlossen | nicht weiterzuverfolgen |
| F – Temporal Cloud | historisch bewerteter Managed Service | per Produktentscheidung ausgeschlossen | nicht weiterzuverfolgen |

### Bewusst akzeptierte Nachteile

- Die begrenzte Reife-Evidence der MAF Durable Extension wird für den lokalen Spike akzeptiert, weil der .NET-Team-Fit einen relevanten Umsetzungsvorteil erwarten lässt; Gate 0 verhindert eine spätere Abhängigkeit von einem kostenpflichtigen Workflow-Service.
- Eine Bindung an produktives Managed DTS wird nicht akzeptiert. Domainmodell, Codex-Port und kanonische Run History bleiben außerdem außerhalb des Scheduler-spezifischen Modells und benötigen eine Export-/Restore-Probe.
- Der große fachliche Eigenbauanteil wird akzeptiert, weil er bei allen realistischen Kandidaten anfällt; nicht akzeptiert wird hingegen der Nachbau eines eigenen Durable Core.

### Offene Annahmen

| Annahme | Einfluss bei Irrtum | Validierung | Fällig | Owner |
| --- | --- | --- | --- | --- |
| MAF Durable Extension ist für den benötigten Produktionszeitpunkt ausreichend reif und upgradefähig | C wird gestoppt oder die Produktion verschoben | Release-/Supportstatus und Upgrade-Probe | vor Produktionsentscheid | Engineering |
| Codex lässt sich als langlebiger externer Worker mit stabilen Session-IDs anbinden | C/D scheiden aus | G01/G03 im Spike | Spike | Engineering |
| `interrupt`, `queue`, Resume, Fork und Fresh Retry lassen sich ohne Framework-Fork modellieren | C scheidet aus | G06/G07 im Spike | Spike | Engineering |
| Durable Recovery plus Adoption verhindert doppelte externe Wirkungen | C scheidet aus | G08 Fault Injection | Spike | Engineering |
| Kanonische History bleibt außerhalb begrenzter Durable-Entity-Zustände skalierbar | Architekturänderung und höhere TCO | Last-/Retention-Test | Spike/TCO | Engineering/Operations |
| Ein kompatibler produktionsfähiger selbst hostbarer Open-Source-Backendpfad existiert ohne verpflichtende Managed-Workflow-Kosten | C scheidet andernfalls vor dem Semantik-Spike aus | Gate-0-Lizenz-, Topologie- und Recovery-Probe | vor V0 | Engineering/Architecture |

## 11. Beschluss, Bedingungen und Exit-Plan

### Beschluss

- `[ ]` Freigabe wie empfohlen
- `[ ]` Freigabe mit Bedingungen
- `[x]` weiterer Spike erforderlich
- `[ ]` Entscheidung vertagt
- `[ ]` keine Umsetzung

### Bedingungen vor Umsetzung

1. Option C besteht den gemeinsamen vertikalen Spike mit `18/18` Gates oder dokumentiert jede verbleibende `E`-Erweiterung mit akzeptiertem Aufwand und Owner.
2. G03, G06, G07 und G08 werden durch automatisierbare Integrations- und Fault-Injection-Tests belegt; ein Framework-Fork oder eigener Durable Core ist nicht erforderlich.
3. Vor Produktionsfreigabe liegen der Gate-0-Nachweis, Mengengerüst, Security-/Datenschutzprüfung, Betriebsmodell und vollständige Kostenbetrachtung der selbst gehosteten Open-Source-Variante vor.

### Re-Evaluation-Trigger

- Drei-Jahres-TCO-Prognose steigt um mehr als `25 %` gegenüber dem freigegebenen Business Case.
- Eines der Muss-Kriterien G01–G18 kann im produktionsnahen Betrieb nicht gehalten werden.
- Codex-Schnittstelle oder Anbieterprodukt ändert sich inkompatibel.
- Projekt-/Anbieteraktivität, Lizenz oder Supportmodell verschlechtert sich wesentlich.
- Nutzerzahl oder Run-/Event-/Retention-Volumen überschreitet das freigegebene Mengengerüst um den Faktor `3`.
- Kritischer Security-, Datenschutz- oder Recovery-Befund bleibt länger als `30 Tage` offen.

### Exit-Plan

| Exit-Baustein | Geforderter Zustand | Nachweis | Aufwandsschätzung |
| --- | --- | --- | ---: |
| Workflow-/Domainzustand | vollständig in kanonischem Format exportierbar | automatisierter JSON-/Schema-Exporttest | im Spike ermitteln |
| Run History | geordnet, korreliert und unverändert exportierbar | Eventexport mit Prüfsummen und Reimport | im Spike ermitteln |
| Artefakte | inklusive Metadaten und Prüfsummen migrierbar | Object-Store-Manifest und Restore-Test | im Spike ermitteln |
| Identitäten/Audit | Provideridentitäten und Aktionen bleiben nachvollziehbar | Auditexport und Stichprobenprüfung | im Spike ermitteln |
| Workflowdefinitionen | fachliche Semantik unabhängig dokumentiert | Domain-/Port-Dokumentation und Contract Tests | laufende Engineering-Aufgabe |
| Offene Läufe | pausierbar, abschließbar oder kontrolliert migrierbar | mindestens eine Exit-Probe mit Testlauf | im Spike ermitteln |
| Datenlöschung beim Anbieter | vertraglich und technisch nachweisbar | Löschtest plus DPA/AVV-/Vertragsnachweis | vor Produktionsfreigabe ermitteln |

### Unterschriften/Freigaben

| Rolle | Name | Entscheidung | Datum | Kommentar |
| --- | --- | --- | --- | --- |
| Product/Process Owner | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Architecture | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Engineering | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Security/Datenschutz | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Operations | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Finance/Procurement | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

## 12. Evidence-Verzeichnis

| Evidence-ID | Typ | Aussage | Quelle/Artefakt | Datum | Owner | Verifiziert durch |
| --- | --- | --- | --- | --- | --- | --- |
| E-001 | Spec | fachliche Ziel- und Muss-Anforderungen | [`spec.md`](./spec.md) | 2026-09-05 | Daniel | Desk Research 2026-09-05 |
| E-002 | Repository-Analyse | vorhandene Orchestrierungsoptionen und Prior Art | [`../../docs/langgraph-github-issue-pilot/open-source-orchestration-options.md`](../../docs/langgraph-github-issue-pilot/open-source-orchestration-options.md) | 2026-09-05 | Daniel | Desk Research 2026-09-05 |
| E-003 | ADR | Live Control Commands | [`../../docs/adr/0001-live-control-commands-for-active-agent-runs.md`](../../docs/adr/0001-live-control-commands-for-active-agent-runs.md) | 2026-09-05 | Daniel | Desk Research 2026-09-05 |
| E-004 | ADR | Operator Clients und gemeinsame Run History | [`../../docs/adr/0002-operator-clients-instead-of-human-agent-sessions.md`](../../docs/adr/0002-operator-clients-instead-of-human-agent-sessions.md) | 2026-09-05 | Daniel | Desk Research 2026-09-05 |
| E-005 | ADR | Forced Takeover ohne Administratorrolle | [`../../docs/adr/0003-forced-takeover-without-admin-role.md`](../../docs/adr/0003-forced-takeover-without-admin-role.md) | 2026-09-05 | Daniel | Desk Research 2026-09-05 |
| E-006 | ADR | Agent Definition Evolution und Approval | [`../../docs/adr/0004-human-approved-agent-definition-evolution.md`](../../docs/adr/0004-human-approved-agent-definition-evolution.md) | 2026-09-05 | Daniel | Desk Research 2026-09-05 |
| E-007 | ADR | Trennung von Agent Definition und Orchestrierung | [`../../docs/adr/0005-separate-agent-definitions-from-work-package-orchestration.md`](../../docs/adr/0005-separate-agent-definitions-from-work-package-orchestration.md) | 2026-09-05 | Daniel | Desk Research 2026-09-05 |
| E-008 | ADR | Externe Repository Governance | [`../../docs/adr/0006-externalize-agent-definition-approval-to-repository-governance.md`](../../docs/adr/0006-externalize-agent-definition-approval-to-repository-governance.md) | 2026-09-05 | Daniel | Desk Research 2026-09-05 |
| E-009 | ADR | Repositorybasierte Operator-Autorisierung | [`../../docs/adr/0007-derive-operator-access-from-repository-permissions.md`](../../docs/adr/0007-derive-operator-access-from-repository-permissions.md) | 2026-09-05 | Daniel | Desk Research 2026-09-05 |
| E-010 | ADR | Bevorzugter zusätzlicher Microsoft-Agent-Framework-Spike und Open-Source-Gate | [`../../docs/adr/0008-prefer-microsoft-agent-framework-for-dotnet-control-plane-spike.md`](../../docs/adr/0008-prefer-microsoft-agent-framework-for-dotnet-control-plane-spike.md) | 2026-09-05 | Daniel | aktualisiert 2026-09-05 |
| E-011 | Herstellerdokumentation | .NET-Workflow-Modell mit Executors, Events, Checkpoints und HITL | [Microsoft Agent Framework: Workflow concepts](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/) | 2026-09-05 | Microsoft | Desk Research 2026-09-05 |
| E-012 | Herstellerdokumentation | Durable Extension mit Recovery, verteilten Workern und zwei Hostingmodellen | [Microsoft Agent Framework: Durable Extension](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions) | 2026-09-05 | Microsoft | Desk Research 2026-09-05 |
| E-013 | Herstellerdokumentation | Framework-Lizenz, .NET-Unterstützung, Workflows und Observability | [Microsoft Agent Framework Repository](https://github.com/microsoft/agent-framework) | 2026-09-05 | Microsoft | Desk Research 2026-09-05 |
| E-014 | Lösungsrecherche | Primärquellenvergleich A–F, Gate-Einschätzung, Reife, Hosting, Lock-in und TCO-Treiber | [`make-or-buy-solution-research.md`](./make-or-buy-solution-research.md) | 2026-09-05 | Daniel | Codex Desk Research 2026-09-05 |
| E-015 | Historischer Arbeitsauftrag | ursprünglicher Startprompt; durch kanonische Spec, ADR 0008 und neuen Spike-Plan überholt | [`microsoft-agent-framework-prd-session-prompt.md`](./microsoft-agent-framework-prd-session-prompt.md) | 2026-09-05 | Daniel | superseded |
| E-020 | Spike | Gate 0 und Option C gegen unveränderte B-Baseline | [`microsoft-agent-framework-local-spike-plan.md`](./microsoft-agent-framework-local-spike-plan.md) | offen | Engineering | geplant |
| E-021 | Gate 0 | Lizenz-, Backend-, Topologie- und Recovery-Nachweis der selbst gehosteten Open-Source-Variante | noch zu erzeugendes Evidence-Artefakt | offen | Engineering/Architecture | offen |

## 13. Ausfüllregeln

1. Zuerst Scope, feste Entscheidungen und Gates gemeinsam bestätigen.
2. Nur Kandidaten mit identischem End-to-End-Scope vergleichen.
3. Produktfunktion und notwendige Eigenentwicklung getrennt ausweisen.
4. Marketing-Demos, Roadmap-Aussagen und ungeprüfte Dokumentation nicht als bestandenen Nachweis werten.
5. Preis-, Lizenz-, Release- und Supportangaben immer mit Datum und Quelle erfassen.
6. Punktzahlen erst nach der Gate-Prüfung und möglichst durch mindestens zwei Rollen vergeben.
7. Bei einer Bewertungsabweichung von mehr als einem Punkt den Grund dokumentieren und Evidence nachfordern.
8. Die finalen Gewichte vor Öffnung kommerzieller Angebote festschreiben, damit sie nicht nachträglich auf einen Favoriten zugeschnitten werden.
9. Die Entscheidung nur auf Basis des gemeinsamen vertikalen Spikes treffen.
10. Die ausgefüllte Vorlage als Decision Record versionieren; spätere Neubewertungen erhalten eine neue Entscheidungs-ID.
