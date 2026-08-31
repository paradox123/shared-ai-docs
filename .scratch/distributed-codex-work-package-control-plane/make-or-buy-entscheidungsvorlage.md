# Make-or-Buy-Entscheidungsvorlage: Work Package Control Plane

| Metadatum | Wert |
| --- | --- |
| Status | Entwurf zur Befüllung |
| Bezugs-Spec | [`spec.md`](./spec.md) |
| Entscheidungs-ID | `[MOB-WPCP-YYYY-NN]` |
| Decision Owner | `[Name/Rolle]` |
| Technischer Owner | `[Name/Rolle]` |
| Entscheidungsgremium | `[Personen/Rollen]` |
| Entscheidungstermin | `[YYYY-MM-DD]` |
| Betrachtungszeitraum für TCO | `3 Jahre` |
| Zielgröße | `zunächst ca. 20 Entwicklerinnen und Entwickler` |

> Diese Vorlage bewertet nicht, ob Codex als Agent-Harness ersetzt werden soll. Codex ist gemäß Spec gesetzt. Bewertet wird, welche Bestandteile der zentralen Work Package Control Plane selbst entwickelt, aus Open Source übernommen, als Managed Service bezogen oder hybrid zusammengesetzt werden.

## 1. Entscheidung in Kürze

### Entscheidungssatz

Wir entscheiden uns für **[Option und Kandidat]**, weil **[wichtigste belegte Gründe]**. Die Option erfüllt alle Muss-Kriterien und erreicht **[Punkte]/100** gewichtete Punkte. Gegenüber der nächstbesten Option **[Name]** bietet sie **[entscheidender Vorteil]** bei **[relevanter Nachteil/Trade-off]**.

### Gewählte Sourcing-Aufteilung

| Baustein | Make | Adopt/Open Source | Buy/Managed | Begründung |
| --- | :---: | :---: | :---: | --- |
| Fachliches Work-Package-Domainmodell und Zustandsübergänge | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |
| Durable Workflow, Timer, Signals und Recovery | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |
| Versionierter Codex Agent-Session-Adapter | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |
| Geordnete Run History und Event-Projektion | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |
| Artefaktspeicher und Retention | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |
| Operator Client/Cockpit und Streaming | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |
| Repository-Authorization-Adapter | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |
| Control Lease, Transfer und Forced Takeover | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |
| Redaction, Audit und Compliance-Funktionen | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |
| Agent Evolution Loop | `[ ]` | `[ ]` | `[ ]` | `[Begründung]` |

### Entscheidergebnis

- Entscheidung: `[MAKE | ADOPT | BUY | HYBRID | NO-GO/WEITERER SPIKE]`
- Freigegebenes Budget: `[EUR einmalig]` / `[EUR jährlich]`
- Erwarteter produktiver Pilot: `[Datum]`
- Befristung oder Re-Evaluation: `[Datum/Trigger]`
- Wesentliche Auflagen: `[z. B. erfolgreicher Security Review, Exit-Test, Kostenobergrenze]`

## 2. Gegenstand und Grenze der Entscheidung

### Zu lösendes Problem

`[In 3–5 Sätzen beschreiben: Ein langlebiger, issuegebundener Implementierungslauf koordiniert viele isolierte Codex-Aktivitäten; mehrere Menschen können ihn remote beobachten und nacheinander steuern; Ausführung, Historie, Recovery und Freigaben sind zentral und nicht an eine Work Machine gebunden.]`

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

## 3. Zu vergleichende Optionen

Alle Optionen müssen denselben fachlichen Scope und denselben produktionsnahen Spike erfüllen. Kandidaten dürfen keine höhere Punktzahl erhalten, indem schwierige Spec-Bestandteile aus ihrem Angebot ausgeklammert werden.

| ID | Option | Definition | Typische Ausprägung | Kandidat/Produkt |
| --- | --- | --- | --- | --- |
| A | MAKE | Control Plane und Durable Core überwiegend selbst entwickeln | eigener Service, Datenmodell, Worker, Event Stream und Cockpit | `[Name/Stack]` |
| B | ADOPT | Open-Source-Komponenten selbst betreiben und fachlich erweitern | z. B. Workflow-Engine plus eigene Domain- und UI-Schicht | `[Projekt/Version/Lizenz]` |
| C | BUY | Managed Plattform als wesentlichen Control-Plane-Kern beziehen | SaaS/Managed Workflow- oder Agent-Orchestrierung | `[Anbieter/Edition]` |
| D | HYBRID | Managed Durable Core, eigene Codex-, Domain- und Operator-Schicht | Managed Engine plus eigene Adapter und fachliche Services | `[Komponenten]` |
| E | STATUS QUO+ | Bestehenden Piloten evolutionär erweitern | bestehender LangGraph/GitHub-Pilot plus zentrale Dienste | `[Ausprägung]` |

### Longlist

Die Longlist ist vor der Bewertung auf Version, Lizenz, Hostingmodell, Reife und aktuelle Produktfähigkeit zu verifizieren.

| Kandidat | Kategorie | Prüfhypothese | Status | Quelle/Stand |
| --- | --- | --- | --- | --- |
| Eigenbau auf bestehendem Pilot | MAKE/STATUS QUO+ | maximale fachliche Kontrolle, höchster Eigenbau- und Betriebsanteil | `[offen]` | `[Link, Datum]` |
| Temporal Core, self-hosted | ADOPT/HYBRID | starke Durable Semantics; Domain, Codex und UI bleiben Eigenbau | `[offen]` | `[Link, Datum]` |
| Temporal Cloud | BUY/HYBRID | Durable Core als Service; Integrations-, Kosten- und Exit-Risiko prüfen | `[offen]` | `[Link, Datum]` |
| DBOS | ADOPT/HYBRID | kleinerer Durable Core; Eignung für verteilte Control Plane beweisen | `[offen]` | `[Link, Datum]` |
| Prefect/Windmill | ADOPT/HYBRID | vorhandene UI und HITL; Passung zu Agentensessions und Domain prüfen | `[offen]` | `[Link, Datum]` |
| GitHub Actions/`gh-aw` | ADOPT/HYBRID | guter Ereignis- und Worker-Unterbau; Live Control und gemeinsame History sind kritisch | `[offen]` | `[Link, Datum]` |
| Spezialisierte Agent-Control-Plane | BUY | Funktionsumfang möglicherweise hoch; Codex-Erhalt und Datenzugriff als frühes Gate | `[offen]` | `[Anbieter, Link, Datum]` |

### Ausgeschlossene Kandidaten

| Kandidat | Ausschlussgrund | Beleg | Entscheider/Datum |
| --- | --- | --- | --- |
| `[Name]` | `[verletztes Muss-Kriterium oder nicht beherrschbares Risiko]` | `[Evidence-ID]` | `[Name, Datum]` |

## 4. Muss-Kriterien und Knock-out-Gates

### Bewertungslogik

Jedes Gate wird für die **Gesamtlösung** bewertet, nicht nur für das Produkt. Zulässige Erfüllungsarten:

- `N` – nativ vorhanden;
- `K` – durch dokumentierte Konfiguration vorhanden;
- `E` – durch klar abgegrenzte eigene Erweiterung erreichbar;
- `U` – unklar oder nur durch unbewiesene Annahme;
- `X` – nicht erreichbar oder widerspricht dem Produktmodell.

`U` und `X` bedeuten bis zum Gegenbeweis **No-Go**. Bei `E` müssen Aufwand, Betriebsverantwortung und Spike-Evidence ausgewiesen werden; ein großer Eigenbauanteil wird zusätzlich in TCO, Time-to-Value und Integrationsrisiko bewertet.

| ID | Muss-Kriterium | A | B | C | D | E | Geforderter Beleg |
| --- | --- | :---: | :---: | :---: | :---: | :---: | --- |
| G01 | Codex bleibt Agent-Harness; kein erzwungener Austausch gegen proprietären Harness | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | realer Codex-Lauf über Adapter |
| G02 | Ein Implementierungslauf bleibt zentral, issuegebunden und überlebt Client-, Worker- und Serverwechsel | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Restart-/Reconnect-Test |
| G03 | Sessions können erstellt, gelesen, resumiert, geforkt und gestoppt werden; Session-IDs bleiben stabil | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Codex-Adapter-Spike |
| G04 | Viele kontextisolierte Aktivitäten werden unter einer gemeinsamen Run History korreliert | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | UI/API-Evidence |
| G05 | Nachrichten, Toolaufrufe, Ergebnisse, Fehler, Diffs, Tests und Artefakte sind beobachtbar und kausal geordnet | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Event-Stream-Demo |
| G06 | Live Control unterstützt adressiertes `interrupt` und dauerhaft geordnetes `queue` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Ausfall- und Zustellungstest |
| G07 | Resume, Fork und Fresh Retry besitzen die in der Spec definierten unterschiedlichen Semantiken | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Identitäts-/History-Test |
| G08 | Crash-Recovery erzeugt keine doppelten externen Wirkungen; vorhandene Wirkungen werden adoptiert | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Fault-Injection-Test |
| G09 | Genau eine Control Lease pro Lauf; CAS/Fencing verhindert konkurrierende Mutationen | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Concurrency-Test |
| G10 | Control Transfer und auditierter Forced Takeover funktionieren atomar | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Drei-Benutzer-Test |
| G11 | Repository Authorization statt eigener Mitglieder-/ACL-Liste | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Provider-Contract-Test |
| G12 | Entzogene Rechte werden bei Verbindung und sicherheitsrelevanter Mutation hinreichend aktuell wirksam | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Revocation-Test |
| G13 | Secrets und sensible Daten werden vor persistenter History, Artefakten und UI redigiert | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | kontrollierter Leak-Test |
| G14 | Drei unabhängige Reviews prüfen dieselbe Head-SHA ohne gegenseitigen aktiven Kontext | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Context-Isolation-Test |
| G15 | Operator Client setzt einen Event-Stream nach Reconnect lücken- und duplikatfrei fort | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Cursor-/Reconnect-Test |
| G16 | Menschliche Identitäten und Service-Identitäten bleiben getrennt und auditierbar | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Audit-Evidence |
| G17 | Kein automatischer Merge, Release oder selbstgenehmigte Agent-Definition-Änderung | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Policy-/End-to-End-Test |
| G18 | Export- und Exit-Pfad für History, Artefakte, Zustände und Korrelationen ist praktikabel | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | Restore/Exit-Probe |

### Ergebnis der Gate-Prüfung

| Option | Alle Gates erfüllt? | Offene `U` | Eigenbau-Erweiterungen `E` | Ergebnis |
| --- | :---: | ---: | ---: | --- |
| A | `[Ja/Nein]` | `[n]` | `[n]` | `[weiter / ausgeschlossen]` |
| B | `[Ja/Nein]` | `[n]` | `[n]` | `[weiter / ausgeschlossen]` |
| C | `[Ja/Nein]` | `[n]` | `[n]` | `[weiter / ausgeschlossen]` |
| D | `[Ja/Nein]` | `[n]` | `[n]` | `[weiter / ausgeschlossen]` |
| E | `[Ja/Nein]` | `[n]` | `[n]` | `[weiter / ausgeschlossen]` |

## 5. Gewichtete Nutzwertanalyse

### Skala und Berechnung

- `0` = nicht erfüllt;
- `1` = nur mit grundlegendem Umbau/hohem Risiko;
- `2` = erhebliche Lücken;
- `3` = ausreichend, relevante Zusatzarbeit;
- `4` = gut, geringe beherrschbare Lücken;
- `5` = vollständig und belastbar nachgewiesen.

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
| N08 | Betrieb, Reife und Support | 7 | Wie hoch sind Reife, Diagnosefähigkeit, Upgrade-Sicherheit und verfügbare Unterstützung? |
| N09 | Time-to-Value | 5 | Wie schnell ist der verifizierte vertikale Pilot und danach ein nutzbarer Betrieb erreichbar? |
| N10 | Drei-Jahres-TCO | 8 | Wie hoch sind Vollkosten inklusive Eigenentwicklung, Betrieb und Exit? |
| N11 | Lock-in und Reversibilität | 5 | Wie portabel sind Daten, Workflows, Adapter und Betriebswissen? |
|  | **Summe** | **100** |  |

### Bewertungsmatrix

In die Bewertungsfelder kommt jeweils eine Punktzahl von 0 bis 5. Jede Punktzahl benötigt mindestens eine Evidence-ID oder eine ausdrücklich markierte Annahme.

| Kriterium | Gewicht | A | B | C | D | E | Evidence/Kommentar |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| N01 Fachliche Spec-Abdeckung | 18 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N02 Durable Correctness und Recovery | 12 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N03 Codex- und Session-Integration | 10 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N04 Observability und Run History | 10 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N05 Menschliche Remote-Steuerung | 8 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N06 Security, Datenschutz und Audit | 10 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N07 Erweiterbarkeit und Providerneutralität | 7 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N08 Betrieb, Reife und Support | 7 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N09 Time-to-Value | 5 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N10 Drei-Jahres-TCO | 8 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| N11 Lock-in und Reversibilität | 5 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[IDs]` |
| **Gewichtete Gesamtpunkte** | **100** | **`[ ]`** | **`[ ]`** | **`[ ]`** | **`[ ]`** | **`[ ]`** |  |

### Sensitivitätsanalyse

Die Entscheidung muss stabil bleiben, wenn unsichere Annahmen oder strategische Prioritäten variieren.

| Szenario | Geänderte Annahme/Gewichte | Rang 1 | Rang 2 | Ändert sich die Entscheidung? |
| --- | --- | --- | --- | :---: |
| Baseline | Gewichte wie oben | `[ ]` | `[ ]` | `[ ]` |
| Kostenfokus | TCO auf `[15]`, entsprechende Reduktion bei `[Kriterien]` | `[ ]` | `[ ]` | `[ ]` |
| Risikofokus | Recovery + Security auf zusammen `[35]` | `[ ]` | `[ ]` | `[ ]` |
| Speed-Fokus | Time-to-Value auf `[15]` | `[ ]` | `[ ]` | `[ ]` |
| Buy-Preis +30 % | Lizenz-/Nutzungskosten steigen um 30 % | `[ ]` | `[ ]` | `[ ]` |
| Nutzungsvolumen ×3 | Läufe, Events und Artefakte verdreifachen sich | `[ ]` | `[ ]` | `[ ]` |
| Anbieter-/Projekt-Exit | Kandidat wird in 12 Monaten abgekündigt/inaktiv | `[ ]` | `[ ]` | `[ ]` |

## 6. Vollkostenrechnung

### Gemeinsame Annahmen

| Annahme | Wert | Quelle | Sicherheit |
| --- | --- | --- | --- |
| Nutzerzahl Jahr 1 / Jahr 3 | `[20]` / `[ ]` | Spec/Planung | `[hoch/mittel/niedrig]` |
| Implementierungsläufe pro Monat | `[ ]` | `[Quelle]` | `[ ]` |
| Agentenaktivitäten pro Lauf | `[ ]` | `[Quelle]` | `[ ]` |
| Events/Artefaktvolumen pro Lauf | `[ ]` | `[Messung]` | `[ ]` |
| Aufbewahrungsdauer | `[ ]` | `[Policy]` | `[ ]` |
| Vollkosten interner Personentag | `[EUR]` | `[Controlling]` | `[ ]` |
| Zielverfügbarkeit / Supportzeit | `[ ]` | `[Betriebsmodell]` | `[ ]` |
| Preissteigerung pro Jahr | `[%]` | `[Annahme/Vertrag]` | `[ ]` |
| Wechselkurs, falls relevant | `[ ]` | `[Annahme]` | `[ ]` |

### Aufwand und Kosten je Option

Alle Werte ohne Umsatzsteuer; interne Aufwände werden mit dem Vollkostensatz bewertet. Anbieterpreise müssen Datum, Edition, Mindestabnahme und nutzungsabhängige Einheiten enthalten.

| Kostenblock | A | B | C | D | E |
| --- | ---: | ---: | ---: | ---: | ---: |
| Discovery, Architektur und Spike | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Erstimplementierung Domain/Workflow | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Codex-Adapter | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Operator Client und API | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Provideradapter und Security | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Migration/Parallelbetrieb | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Lizenzen/Subscription über 3 Jahre | `[EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Infrastruktur über 3 Jahre | `[EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Betrieb/On-call über 3 Jahre | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Wartung, Upgrades und Regressionstests | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Support/Professional Services | `[EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Security, Datenschutz und Audit | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Schulung und Enablement | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Exit-/Ablösungsvorsorge | `[PT/EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Risikopuffer | `[EUR/%]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| **Drei-Jahres-TCO** | **`[EUR]`** | **`[EUR]`** | **`[EUR]`** | **`[EUR]`** | **`[EUR]`** |

### Wirtschaftlicher Nutzen

| Nutzenhebel | Messgröße | Baseline | Ziel | Monetarisierung/Begründung |
| --- | --- | ---: | ---: | --- |
| weniger manuelle Laufüberwachung | Stunden pro Lauf | `[ ]` | `[ ]` | `[ ]` |
| kürzere Recovery nach Fehlern | MTTR | `[ ]` | `[ ]` | `[ ]` |
| weniger doppelte/externe Fehlwirkungen | Vorfälle pro Quartal | `[ ]` | `[ ]` | `[ ]` |
| schnellere Durchlaufzeit Issue → verifizierter PR | Stunden/Tage | `[ ]` | `[ ]` | `[ ]` |
| weniger Kontextverlust bei Personenwechsel | Eskalationen/Nacharbeit | `[ ]` | `[ ]` | `[ ]` |
| wiederverwendbare Agent- und Provideradapter | vermiedene PT | `[ ]` | `[ ]` | `[ ]` |

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

| Messwert | Ziel/Schwelle | A | B | C | D | E |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Muss-Tests bestanden | `18/18` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Unbehandelte Doppelwirkung nach Fault Injection | `0` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Verlorene/duplizierte Events nach Reconnect | `0` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Zeit bis zur Remote-Diagnose | `[Ziel]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Zeit bis zur korrekten Fortsetzung | `[Ziel]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Eigenbau-Code für den Spike | `[LOC/Module/PT]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Betriebs- und Deployment-Komponenten | `[Anzahl]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Gemessene Kosten pro Referenzlauf | `[EUR]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Offene kritische Risiken | `0` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

### Abbruchkriterien für einen Spike

- Codex kann nicht als gleichwertiger Harness integriert werden.
- Die Lösung kann aktive Sessions nicht stabil adressieren oder `interrupt`/`queue` nicht zuverlässig abbilden.
- Externe Wirkungen werden bei Restart oder Retry unkontrolliert wiederholt.
- Zentrale History ist nur eine flüchtige UI-Projektion und nicht vollständig exportierbar.
- Repository Authorization oder Identitätstrennung erfordert eine zweite dauerhafte Mitgliederverwaltung.
- Notwendige Telemetrie oder Artefakte verlassen unzulässig die definierte Daten- oder Vertrauensgrenze.
- Der notwendige Eigenbauanteil überschreitet `[PT/Module/Prozent]` und zerstört die Buy-Hypothese.

## 8. Security, Datenschutz, Vertrag und Betrieb

### Prüffragen

| Bereich | Frage | A | B | C | D | E | Evidence |
| --- | --- | :---: | :---: | :---: | :---: | :---: | --- |
| Datenstandort | Wo liegen Prompts, Toolresultate, Diffs, Logs und Artefakte? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Modelltraining | Werden Inhalte für Training oder Produktverbesserung verwendet? Abschaltbar? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Redaction | Erfolgt Redaction vor dauerhafter Aufnahme und vor Export? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Verschlüsselung | At rest, in transit, Schlüsselverwaltung, BYOK-Anforderung? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Mandantentrennung | Wie werden Repositories, Organisationen und Service-Identitäten getrennt? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Audit | Sind menschliche und technische Aktionen unveränderlich korrelierbar? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Retention/Löschung | Sind Aufbewahrung, Legal Hold, Löschung und Nachweis konfigurierbar? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Zugriff | Unterstützt das Produkt providerabgeleitete Autorisierung ohne Schatten-ACL? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Lieferkette | SBOM, Signaturen, CVE-Prozess und Patch-SLA vorhanden? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Vertrag | DPA/AVV, Unterauftragsverarbeiter, Haftung und Exit-Unterstützung akzeptabel? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Verfügbarkeit | SLA/SLO, RPO/RTO, Backup/Restore und Support-Eskalation passend? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Preismodell | Kosten für User, Runs, Events, Storage, Egress und Support prognostizierbar? | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

### Betriebsverantwortung

| Verantwortung | Intern | Anbieter | Geteilt | Konkreter Owner/Eskalationspfad |
| --- | :---: | :---: | :---: | --- |
| Workflow-Engine und Persistenz | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Codex-Adapter und Kompatibilität | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Domainlogik und Zustandsmigrationen | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Operator Client/API | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Event-/Artefaktspeicher | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Security Patches | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Backup, Restore und Disaster Recovery | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Incident Response | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Support für Entwickler | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

## 9. Risiken und Gegenmaßnahmen

Bewertung: Eintrittswahrscheinlichkeit `1–5`, Auswirkung `1–5`, Risikowert `E × A`.

| ID | Option | Risiko | E | A | Wert | Gegenmaßnahme | Restrisiko | Owner |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| R01 | `[ ]` | Anbieter ersetzt oder abstrahiert Codex unzureichend | `[ ]` | `[ ]` | `[ ]` | versionierter Adapter und Exit-Test | `[ ]` | `[ ]` |
| R02 | `[ ]` | Buy-Option erfordert unerwartet viel Domain- und UI-Eigenbau | `[ ]` | `[ ]` | `[ ]` | Spike misst Eigenbauanteil | `[ ]` | `[ ]` |
| R03 | `[ ]` | Replay wiederholt Git-/GitHub-/Toolwirkungen | `[ ]` | `[ ]` | `[ ]` | Idempotency Keys, Reconciliation, Fault Injection | `[ ]` | `[ ]` |
| R04 | `[ ]` | Zentrale History wird zum Secret-/Datenschutzrisiko | `[ ]` | `[ ]` | `[ ]` | Redaction vor Persistierung, Zugriff, Retention | `[ ]` | `[ ]` |
| R05 | `[ ]` | Managed-Kosten skalieren mit Events/Storage unerwartet | `[ ]` | `[ ]` | `[ ]` | Lastmodell, Preis-Cap, Sampling nur außerhalb Auditkern | `[ ]` | `[ ]` |
| R06 | `[ ]` | Open-Source-Projekt verliert Maintainer oder ändert Lizenz | `[ ]` | `[ ]` | `[ ]` | Pinning, Fork-Fähigkeit, Exit-Plan | `[ ]` | `[ ]` |
| R07 | `[ ]` | Eigenbau bindet dauerhaft seltene Workflow-/Distributed-Systems-Kompetenz | `[ ]` | `[ ]` | `[ ]` | Bus-Factor-Ziel, Runbooks, Ownership | `[ ]` | `[ ]` |
| R08 | `[ ]` | Vendor Lock-in durch proprietäre History/Workflowdefinitionen | `[ ]` | `[ ]` | `[ ]` | kanonischer Export, Adaptergrenze, Restore-Probe | `[ ]` | `[ ]` |
| R09 | `[ ]` | Providerneutralität wird nur behauptet, aber GitHub hart codiert | `[ ]` | `[ ]` | `[ ]` | Contract-Seams für GitHub/GitLab/Azure DevOps | `[ ]` | `[ ]` |
| R10 | `[ ]` | Control Lease oder Live Commands erzeugen Race Conditions | `[ ]` | `[ ]` | `[ ]` | CAS/Fencing, Konkurrenztests | `[ ]` | `[ ]` |

## 10. Entscheidungsbegründung

### Warum die gewählte Option gewinnt

`[Begründung anhand Muss-Kriterien, Spike-Evidence, Nutzwert, TCO und Risiken. Keine Marketingaussagen ohne Beleg.]`

### Warum die Alternativen nicht gewählt wurden

| Option | Stärkster Vorteil | Entscheidender Nachteil | Was müsste sich ändern? |
| --- | --- | --- | --- |
| A | `[ ]` | `[ ]` | `[ ]` |
| B | `[ ]` | `[ ]` | `[ ]` |
| C | `[ ]` | `[ ]` | `[ ]` |
| D | `[ ]` | `[ ]` | `[ ]` |
| E | `[ ]` | `[ ]` | `[ ]` |

### Bewusst akzeptierte Nachteile

- `[Nachteil]` wird akzeptiert, weil `[Begründung]`; Gegenmaßnahme: `[Maßnahme]`.
- `[Nachteil]` wird bis `[Datum/Meilenstein]` akzeptiert; danach gilt `[Exit-/Re-Evaluation-Trigger]`.

### Offene Annahmen

| Annahme | Einfluss bei Irrtum | Validierung | Fällig | Owner |
| --- | --- | --- | --- | --- |
| `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

## 11. Beschluss, Bedingungen und Exit-Plan

### Beschluss

- `[ ]` Freigabe wie empfohlen
- `[ ]` Freigabe mit Bedingungen
- `[ ]` weiterer Spike erforderlich
- `[ ]` Entscheidung vertagt
- `[ ]` keine Umsetzung

### Bedingungen vor Umsetzung

1. `[Bedingung mit messbarem Nachweis und Termin]`
2. `[Bedingung mit messbarem Nachweis und Termin]`
3. `[Bedingung mit messbarem Nachweis und Termin]`

### Re-Evaluation-Trigger

- Drei-Jahres-TCO-Prognose steigt um mehr als `[%]`.
- Muss-Kriterium `[ID]` kann im produktionsnahen Betrieb nicht gehalten werden.
- Codex-Schnittstelle oder Anbieterprodukt ändert sich inkompatibel.
- Projekt-/Anbieteraktivität, Lizenz oder Supportmodell verschlechtert sich wesentlich.
- Nutzerzahl, Run-Volumen oder Retention überschreitet `[Schwelle]`.
- Kritischer Security-, Datenschutz- oder Recovery-Befund bleibt länger als `[Frist]` offen.

### Exit-Plan

| Exit-Baustein | Geforderter Zustand | Nachweis | Aufwandsschätzung |
| --- | --- | --- | ---: |
| Workflow-/Domainzustand | vollständig in kanonischem Format exportierbar | `[Test/Artefakt]` | `[PT]` |
| Run History | geordnet, korreliert und unverändert exportierbar | `[Test/Artefakt]` | `[PT]` |
| Artefakte | inklusive Metadaten und Prüfsummen migrierbar | `[Test/Artefakt]` | `[PT]` |
| Identitäten/Audit | Provideridentitäten und Aktionen bleiben nachvollziehbar | `[Test/Artefakt]` | `[PT]` |
| Workflowdefinitionen | fachliche Semantik unabhängig dokumentiert | `[Dokument]` | `[PT]` |
| Offene Läufe | pausierbar, abschließbar oder kontrolliert migrierbar | `[Probe]` | `[PT]` |
| Datenlöschung beim Anbieter | vertraglich und technisch nachweisbar | `[Nachweis]` | `[PT]` |

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
| E-001 | Spec | fachliche Ziel- und Muss-Anforderungen | [`spec.md`](./spec.md) | `[ ]` | `[ ]` | `[ ]` |
| E-002 | Repository-Analyse | vorhandene Orchestrierungsoptionen und Prior Art | [`../../docs/langgraph-github-issue-pilot/open-source-orchestration-options.md`](../../docs/langgraph-github-issue-pilot/open-source-orchestration-options.md) | `[ ]` | `[ ]` | `[ ]` |
| E-003 | ADR | Live Control Commands | [`../../docs/adr/0001-live-control-commands-for-active-agent-runs.md`](../../docs/adr/0001-live-control-commands-for-active-agent-runs.md) | `[ ]` | `[ ]` | `[ ]` |
| E-004 | ADR | Operator Clients und gemeinsame Run History | [`../../docs/adr/0002-operator-clients-instead-of-human-agent-sessions.md`](../../docs/adr/0002-operator-clients-instead-of-human-agent-sessions.md) | `[ ]` | `[ ]` | `[ ]` |
| E-005 | ADR | Forced Takeover ohne Administratorrolle | [`../../docs/adr/0003-forced-takeover-without-admin-role.md`](../../docs/adr/0003-forced-takeover-without-admin-role.md) | `[ ]` | `[ ]` | `[ ]` |
| E-006 | ADR | Agent Definition Evolution und Approval | [`../../docs/adr/0004-human-approved-agent-definition-evolution.md`](../../docs/adr/0004-human-approved-agent-definition-evolution.md) | `[ ]` | `[ ]` | `[ ]` |
| E-007 | ADR | Trennung von Agent Definition und Orchestrierung | [`../../docs/adr/0005-separate-agent-definitions-from-work-package-orchestration.md`](../../docs/adr/0005-separate-agent-definitions-from-work-package-orchestration.md) | `[ ]` | `[ ]` | `[ ]` |
| E-008 | ADR | Externe Repository Governance | [`../../docs/adr/0006-externalize-agent-definition-approval-to-repository-governance.md`](../../docs/adr/0006-externalize-agent-definition-approval-to-repository-governance.md) | `[ ]` | `[ ]` | `[ ]` |
| E-009 | ADR | Repositorybasierte Operator-Autorisierung | [`../../docs/adr/0007-derive-operator-access-from-repository-permissions.md`](../../docs/adr/0007-derive-operator-access-from-repository-permissions.md) | `[ ]` | `[ ]` | `[ ]` |
| E-010 | Spike | `[Kandidat und belegte Aussage]` | `[Link/Datei]` | `[ ]` | `[ ]` | `[ ]` |
| E-011 | Angebot | `[Preis, Edition, Gültigkeit]` | `[vertraulicher Ablageort]` | `[ ]` | `[ ]` | `[ ]` |

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
