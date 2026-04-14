# Iteration 0

Ein neues lokales RAG-Projekt fuer DanielsVault soll gestartet werden.

Die Dokumentation soll unter

- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs`

liegen, mit einem eigenen Dokuordner fuer das Projekt.

Zusaetzlich soll eine erste Spec in

- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs`

entstehen.

Das Projekt soll als spaeter nutzbare lokale Wissensschicht fuer den Vault dienen.

## Zweck

Diese Parent-Spec definiert das Zielbild fuer eine lokale RAG-Wissensplattform auf Basis von DanielsVault.

Sie soll:

1. die inhaltlichen Ziele des Projekts fixieren
2. die Domain- und Repository-Grenzen respektieren
3. die spaeteren bounded delivery changes vorbereiten
4. einen Rahmen fuer Architektur-, Evaluations- und Integrationsentscheidungen geben

## Bezug

Massgebliche Referenzen:

- `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
- `/Users/dh/Documents/DanielsVault/AGENTS.md`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md`

## Scope

In Scope:

- Definition eines lokalen RAG-Zielbilds fuer DanielsVault
- Abgrenzung der relevanten Datenquellen und Ignore-Zonen
- Definition der funktionalen Kernfaehigkeiten fuer Phase 1
- Festlegung der benoetigten Metadaten pro Dokument/Chunk
- Definition eines strukturierten Retrieval-Layers fuer ausgewaehlte maschinenlesbare Artefakte
- Definition von Qualitaets- und Evaluationszielen
- Vorbereitung spaeterer bounded changes fuer Implementierung

Out of Scope:

- vollstaendige Implementierung in dieser Spec
- Entscheidung und Aufbau einer Cloud-Produktionsplattform
- Indexierung aller Dateitypen im Vault
- Aufbau einer generischen Volltext- oder SQL-Ersatzschicht fuer beliebige Daten
- globale Cross-Domain-Suche ohne Repository-Grenzen
- unmittelbare Integration in alle Agents und IDEs

## Scope Pressure Check

Dieses Vorhaben ist fuer eine einzelne Delivery-Change zu gross.

Empfohlene Aufteilung:

1. Parent-Spec und Zielbild
2. Change A: Datenquellen, Ignore-Regeln, Chunking-Strategie
3. Change B: Embeddings, Vector Store, Retrieval API
4. Change C: Evaluation Harness und Qualitaetsmetriken
5. Change D: Agent-/MCP-Integration

Empfehlung:

- zuerst Change A umsetzen, weil dadurch der spaetere Index sauber und domain-treu bleibt

## Decision Freeze Pack

### Zielbild und Scope in 1-2 Saetzen

Es soll ein lokales, domain-bewusstes Retrieval-System entstehen, das DanielsVault-Dokumente semantisch erschliessbar macht und fuer ausgewaehlte strukturierte Artefakte exakte Feld- und Datensatzabfragen erlaubt. Phase 1 priorisiert klare Repository-Grenzen, nachvollziehbare Metadaten und messbare Retrieval-Qualitaet.

### Betroffene Repositories und Wissensraeume

- `/Users/dh/Documents/DanielsVault`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- `/Users/dh/Documents/DanielsVault/ncg/ncg-docs`
- `/Users/dh/Documents/DanielsVault/private`
- `/Users/dh/Documents/DanielsVault/sparkle`

Normative Regel:

- Git-Roots bleiben logische Retrieval-Grenzen

### Referenz-Baseline

Die fachliche Baseline fuer Domain-Grenzen und Routing ist:

- `VAULT_AGENT_STRUCTURE.md`
- `AGENTS.md`

### Nachweisformat

Spaetere Implementierungschanges muessen mindestens liefern:

- Retrieval-Demo
- konkrete Verifikationskommandos
- Evaluationsreport oder messbare Retrieval-Evidenz

### Go/No-Go

Go:

- das System kann relevante Dokumente fuer definierte Fragen aus dem Vault reproduzierbar finden
- Quellen bleiben domain- und pfadbezogen nachvollziehbar
- Retrieval-Qualitaet wird ueber ein explizites Eval-Set gemessen

No-Go:

- das System indexiert unkontrolliert irrelevante oder generierte Dateien
- Antworten verlieren den Bezug zu konkreten Quelldokumenten
- Domain-Grenzen des Vault werden ignoriert

## Anforderungen

### 1. Lokale Ausfuehrbarkeit

Das System muss lokal auf dem Entwicklerrechner lauffaehig sein.

Normative Anforderungen:

- keine Cloud-Pflicht fuer Phase 1
- lokale Entwicklung und lokaler Testlauf muessen moeglich sein
- externe APIs duerfen optional sein, aber nicht der einzige Ausfuehrungspfad fuer die Grundfunktion

### 2. Domain- und Repository-Bewusstsein

Das Retrieval muss die bestehenden Wissensraeume respektieren.

Normative Anforderungen:

- jeder Indexeintrag traegt mindestens `git_root`, `domain` und `path`
- Retrieval kann auf einen oder mehrere Wissensraeume begrenzt werden
- Cross-Domain-Retrieval erfolgt nur bewusst und nicht als einziger Default

### 3. Textzentrierte Ingestion in Phase 1

Phase 1 beginnt mit textnahen Quellen und gezielt ausgewaehlten maschinenlesbaren Artefakten.

In Phase 1 bevorzugt:

- `*.md`
- ausgewaehlte `*.txt`
- ausgewaehlte `*.json`
- ausgewaehlte `*.yaml`

Zusaetzlich erlaubt in Phase 1:

- ausgewaehlte strukturierte Projektartefakte mit stabilen Feldern, wenn daraus nachvollziehbare Records abgeleitet werden koennen

Nicht Teil von Phase 1:

- `node_modules`
- `.git`
- `.obsidian`
- Binaries
- grosse generierte Schemas
- Lockfiles

### 4. Nachvollziehbare Chunk-Metadaten

Jeder Chunk oder Indexeintrag muss nachvollziehbar sein.

Mindestens erforderlich:

- `document_id`
- `path`
- `git_root`
- `domain`
- `section_title`
- `chunk_index`
- `last_modified`

Optional spaeter:

- Frontmatter-Metadaten
- Obsidian-Tags
- manuelle Prioritaetslabels

### 5. Strukturierte Projektionen fuer exakte Datenabfragen

Das System soll fuer geeignete maschinenlesbare Quellen neben Chunks auch normalisierte Records ableiten koennen.

Normative Anforderungen:

- strukturierte Records behalten `git_root`, `domain` und `path`
- strukturierte Records enthalten einen `record_type` und mindestens einen fachlichen Schluessel
- exakte Fragen zu IDs, Jahreszahlen, Services oder Datensaetzen duerfen nicht ausschliesslich ueber semantische Suche beantwortet werden
- Antworten auf strukturierte Fragen muessen auf konkrete Record- oder Quelldateien zurueckfuehrbar bleiben

### 6. Retrieval mit Quellenbezug

Das System darf nicht nur "Antworten erzeugen", sondern muss fundierte Retrieval-Ergebnisse liefern.

Normative Anforderungen:

- zu jeder relevanten Antwort muessen Quellenpfade geliefert werden koennen
- Treffer muessen abschnittsnah oder chunk-nah referenzierbar sein
- reiner Chat ohne Quellenbezug gilt nicht als ausreichender Projekterfolg

### 7. Evaluation als Pflichtbestandteil

Evaluation ist kein spaeteres Extra, sondern Teil des Projektkerns.

Normative Anforderungen:

- es gibt ein kleines Eval-Set mit echten Fragen aus DanielsVault
- Retrieval-Ergebnisse werden gegen erwartete Dokumente oder Erwartungsbereiche geprueft
- Qualitaetsmetriken werden dokumentiert

## Architekturrahmen

### Empfohlener Startstack

Empfehlung fuer den ersten Implementierungszuschnitt:

- Python
- FastAPI
- Qdrant
- lokales oder API-basiertes Embedding-Modell
- CLI oder kleine HTTP-API fuer Retrieval-Tests
- kleine Query-Schicht fuer strukturierte Projektionen

### Nicht fest eingefrorene Entscheidungen

- `[DECISION Embedding-Modell fuer Phase 1: lokal vs API-basiert]`
- `[DECISION Retrieval-Zugang zunaechst CLI-only oder HTTP-API]`
- `[DECISION Re-Ranking bereits in Phase 1 oder erst in Phase 2]`
- `[DECISION Speicherform fuer strukturierte Projektionen: JSONL, SQLite oder Qdrant payload-first]`
- `[DECISION Welche strukturierten Artefakte zuerst projiziert werden: Nebenkosten-Outputs, reviewed artifacts, NCG-Konfig-Artefakte oder andere]`

## Use Cases

### Use Case 1 - Dokumente zu einem Thema finden

Ein Nutzer fragt nach einem technischen oder organisatorischen Thema und erhaelt relevante Dokumente mit Quellenpfaden.

### Use Case 2 - Domain-spezifischen Kontext sammeln

Ein Agent soll vor einer Aufgabe nur in `_shared`, `ncg` oder `private` suchen und keine unkontrollierte Vollsuche ueber den gesamten Vault ausfuehren.

### Use Case 3 - Strukturierte Datensaetze gezielt finden

Ein Agent soll gezielt nach exakten Datensaetzen fragen koennen, zum Beispiel nach einem bestimmten Jahr, einer Entity-ID oder einem Record-Typ, ohne zuerst manuell Pfade durchsuchen zu muessen.

### Use Case 4 - Hybride Agent-Antworten

Ein Agent soll bei gemischten Aufgaben erst strukturierte Treffer ermitteln und danach semantischen Dokumentkontext nachladen koennen.

## Akzeptanzkriterien fuer die erste umsetzbare Projektphase

Diese Kriterien gelten fuer den ersten spaeteren bounded Change, nicht fuer diese Parent-Spec selbst.

1. Ein definierter Satz textbasierter Quellen kann lokal eingelesen werden.
2. Irrelevante Verzeichnisse wie `.git`, `.obsidian` und `node_modules` werden ausgeschlossen.
3. Indexeintraege enthalten die definierten Metadaten.
4. Fuer mindestens einen ausgewaehlten strukturierten Datentyp koennen normalisierte Records erzeugt werden.
5. Eine Suchanfrage liefert reproduzierbar relevante Dokumente oder strukturierte Treffer mit Quellenpfaden.
6. Es existiert ein erstes Eval-Set mit mindestens `10` realen Fragen.

## Verifikation fuer spaetere Implementierungschanges

Die spaeteren bounded Changes muessen konkrete Verifikationskommandos definieren. Erwartete Kategorien:

1. Ingestion-Lauf erfolgreich
2. Projektions-Lauf fuer strukturierte Artefakte erfolgreich
3. Index-Aufbau erfolgreich
4. Retrieval-Test gegen Beispielanfragen erfolgreich
5. Eval-Run mit dokumentierten Metriken erfolgreich

`[MISSING Konkrete Verifikationskommandos je Implementierungschange]`

## Risiken und offene Punkte

- `[DECISION Welche Wissensraeume standardmaessig indexiert werden: alle vs priorisierte Teilmenge]`
- `[DECISION Ob das Projekt in einem neuen Repo oder innerhalb eines bestehenden Repos startet]`
- `[MISSING Zielpfad fuer das eigentliche Implementierungsrepo]`
- `[MISSING Entscheidung zu lokalen Embeddings und Hardwarebudget]`
- `[REVIEW Scope risk accepted: Parent-Spec bleibt bewusst uebergeordnet und verlangt Folge-Changes]`

## Empfohlene naechste bounded Changes

1. Change A: Datenquellen, Ignore-Regeln, Chunking- und Metadatenkonzept
2. Change B: strukturierte Projektionen fuer ausgewaehlte Datentypen
3. Change C: lokaler Prototyp fuer Embeddings, Index und hybrides Retrieval
4. Change D: Evaluation Harness fuer reale DanielsVault-Fragen
5. Change E: Integration in Agent- oder MCP-Workflows

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-13 | 0 | User | Neues lokales RAG-Projekt gewuenscht, Dokuordner und erste Spec angefordert |
| 2026-04-13 | 1 | Codex | Parent-Spec, Zielbild, Scope-Grenzen und erste Folge-Changes formuliert |
| 2026-04-14 | 2 | Codex | Strukturierter Retrieval-Layer und Einordnung als hybrides bzw. spaeter agentisches Retrieval ergaenzt |

SessionId: codex-desktop-current-thread
