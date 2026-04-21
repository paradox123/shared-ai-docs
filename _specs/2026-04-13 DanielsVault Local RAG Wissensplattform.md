**Date:** 2026-04-13  
**Status:** 🟡 Spec  
**Scope:** Lokale DanielsVault-RAG-Wissensplattform mit CLI-first Agentenzugriff, Default-Scope `ncg/ncg-docs` plus eingeschlossenem `private`

---

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
- lokales Embedding-Modell
- CLI oder kleine HTTP-API fuer Retrieval-Tests
- kleine Query-Schicht fuer strukturierte Projektionen

### Offene Anforderungsentscheidungen fuer Phase 1

Bereits festgelegt:

- Agentenzugriff erfolgt in Phase 1 CLI-first (lokale Kommandozeile als verbindlicher Zugangsweg), weitere Interfaces sind optional.
- Phase 1 stellt nur vorhandene lokale Informationen bereit; es werden keine externen Inhaltsquellen angebunden.
- API-basierte Embeddings sind fuer Phase 1 nicht erforderlich.
- Mindestqualitaetsziele fuer Phase 1 sind festgelegt:
  - `domain_hit_rate >= 0.90`
  - `file_hit_rate >= 0.70`
  - `cross_domain_leakage <= 0.10`

Weiterhin offen auf Anforderungsniveau:

- keine blockierenden Open Items in diesem Abschnitt

## Use Cases

### Use Case 1 - Dokumente zu einem Thema finden

Ein Nutzer fragt nach einem technischen oder organisatorischen Thema und erhaelt relevante Dokumente mit Quellenpfaden.

### Use Case 2 - Domain-spezifischen Kontext sammeln

Ein Agent soll vor einer Aufgabe standardmaessig in `ncg/ncg-docs` suchen, zusaetzlich aber auch auf `private` zugreifen koennen. Eine Vollsuche ueber den gesamten Vault bleibt ein expliziter Opt-in und erfolgt nicht unkontrolliert als Default.

### Use Case 3 - Strukturierte Datensaetze gezielt finden

Ein Agent soll gezielt nach exakten Datensaetzen fragen koennen, zum Beispiel nach einem bestimmten Jahr, einer Entity-ID oder einem Record-Typ, ohne zuerst manuell Pfade durchsuchen zu muessen.

### Use Case 4 - Hybride Agent-Antworten

Ein Agent soll bei gemischten Aufgaben erst strukturierte Treffer ermitteln und danach semantischen Dokumentkontext nachladen koennen.

### Use Case 5 - Research for Review

Ein `research-for-review`-Skill soll fuer Spec- und Implementierungsreviews gezielt Zusatzkontext aus `ncg/ncg-docs` holen koennen, ohne breite manuelle Dateisuche.

### Use Case 6 - Spec Closeout Dokumentationsrouting

`spec-closeout` soll die wahrscheinlich betroffenen Dokumentationsziele priorisiert vorgeschlagen bekommen, damit notwendige Doku-Updates schnell auffindbar sind.

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

Vorschlag fuer eine verbindliche CLI-basierte Verifikationsstrecke:

1. `rag ingest run --domain ncg/ncg-docs`
2. `rag records project --record-type <phase1-record-type>`
3. `rag retrieve semantic --domain ncg/ncg-docs --query "<frage>"`
4. `rag retrieve structured --record-type <phase1-record-type> --filter "<fachfilter>"`
5. `rag eval run --set /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.v0.jsonl --top-k 5`
6. `rag eval report --metrics domain_hit_rate,file_hit_rate,source_precision,cross_domain_leakage`

Anforderung an den Eval-Lauf:

- Die Fragen aus `evaluation-set.v0.jsonl` muessen gegen den Retriever laufen.
- Das Ergebnis muss pro Frage mindestens Top-5 Treffer, Domain-Treffer, Datei-Treffer und Quellenpraezision enthalten.

Kommando-/Parameterkonvention wird in Change A als CLI-Contract fixiert und bleibt fuer Phase 1 stabil.

## Risiken und offene Punkte

Bereits festgelegt durch aktuelle Nutzerentscheidung:

- Implementierungszielpfad fuer das neue RAG-Projekt: `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag`
- Priorisierte Start-Domain fuer Agenten-Retrieval: `/Users/dh/Documents/DanielsVault/ncg/ncg-docs`
- Zusaetzlich eingeschlossener Wissensraum in Phase 1: `/Users/dh/Documents/DanielsVault/private`
- Agentenzugriff in Phase 1 erfolgt CLI-first.
- Offline-Pflicht besteht nicht; Online/API-basierte Komponenten sind fuer Phase 1 zulaessig.
- Datenschutzanforderung in Phase 1: `vertraulich` (keine unkontrollierte Weitergabe ausserhalb explizit freigegebener Dienste).
- Zielhardware fuer lokale Ausfuehrung: vorhandener Apple-Laptop des Nutzers muss fuer Phase-1-Workloads ausreichen.
- RAG dient als lokaler Wissenszugriff auf vorhandene Dateien; externe Datenquellen werden in Phase 1 nicht abgefragt.
- API-Embeddings sind in Phase 1 nicht erforderlich, daher ist fuer RAG-internen Embedding-Betrieb kein externer API-Kostenrahmen noetig.
- Primaerer Nutzen in Phase 1:
  1. `research-for-review` kann gezielt Projektwissen aus `ncg/ncg-docs` fuer Specs und Implementierungsreviews nachladen.
  2. `spec-closeout` kann die zu aktualisierende Dokumentation gezielter bestimmen, ohne ungerichtete Vollsuche.
- Ein erweiterter Full-Vault-Modus (`/Users/dh/Documents/DanielsVault`) bleibt optional und erfolgt nur als expliziter Opt-in.
- Structured Retrieval in Phase 1 ist kein SQL-Ersatz, sondern ein kleiner praeziser Zusatzkanal fuer exakte Fragen (z. B. CI-Variablen/Settings) mit Quellenbezug.
- Mindest-Ausgabeformat fuer agentische Nutzung ist maschinell lesbar mit Quellenpflicht:
  1. `research-for-review`: pro Treffer mindestens `path`, `section_or_chunk`, `excerpt`, `why_relevant`.
  2. `spec-closeout`: pro vorgeschlagener Doku mindestens `path`, `update_reason`, `source_evidence`.
  3. zusaetzliche Felder sind erlaubt und duerfen je Agent-Fall flexibel erweitert werden.
- Vorschlag fuer ein einheitliches, aber schlankes CLI-Response-Envelope:
  1. Kopf: `query`, `mode` (`semantic|structured`), `domain`, `generated_at`.
  2. `hits[]` fuer Dokumenttreffer mit Quellenbezug (`path`, `section_or_chunk`, `excerpt`, `score`, `why_relevant`).
  3. optional `facts[]` fuer exakte Antworten (z. B. `name`, `value`, `source_path`, `source_anchor`).
  4. Freitextantworten bleiben erlaubt, solange die Pflichtfelder fuer Nachvollziehbarkeit enthalten sind.

Weiterhin offen:

- `[REVIEW Non-blocking: Full-Vault-Opt-in-Modus und Multi-Rechner-Betrieb werden nach Phase 1 erneut eingeplant]`
- `[REVIEW Scope risk accepted: Parent-Spec bleibt bewusst uebergeordnet und verlangt Folge-Changes]`

## Empfohlene naechste bounded Changes

1. Change A: Datenquellen, Ignore-Regeln, Chunking- und Metadatenkonzept
2. Change B: strukturierte Projektionen fuer ausgewaehlte Datentypen
3. Change C: lokaler Prototyp fuer Embeddings, Index und hybrides Retrieval
4. Change D: Evaluation Harness fuer reale DanielsVault-Fragen
5. Change E: Integration in Agent- oder MCP-Workflows

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-04-13 | User | Neues lokales RAG-Projekt gewuenscht, Dokuordner und erste Spec angefordert. |
| 2026-04-13 | Codex | Parent-Spec, Zielbild, Scope-Grenzen und erste Folge-Changes formuliert. |
| 2026-04-14 | Codex | Strukturierter Retrieval-Layer und Einordnung als hybrides bzw. spaeter agentisches Retrieval ergaenzt. |
| 2026-04-21 | User + Codex | Open-Items auf priorisierte `ncg/ncg-docs`-Nutzung, Zielpfad unter `_shared`, Skill-Use-Cases und Multi-Projekt-Perspektive aktualisiert. |
| 2026-04-21 | User + Codex | Open-Items auf Anforderungsniveau umgestellt, CLI-first fixiert und Verifikationsvorschlag inkl. Eval-Set-Lauf ergaenzt. |
| 2026-04-21 | User + Codex | Anforderungen fuer Online-Zulaessigkeit, Vertraulichkeit, Zielhardware und nicht-priorisierte Multi-Rechner-Erweiterung konkretisiert. |
| 2026-04-21 | User + Codex | Mindest-Ausgabeformat fuer research-for-review/spec-closeout mit Quellenpflicht festgelegt und verbleibende Open-Items weiter reduziert. |
| 2026-04-21 | User + Codex | Phase-1-Fokus auf lokale vorhandene Inhalte ohne externe Datenquellen/API-Embeddings fixiert, Eval-Mindestziele festgelegt und CLI-Response-Vorschlag ergaenzt. |
| 2026-04-21 | User + Codex | Domain-Scope praezisiert: `ncg/ncg-docs` als Default, `private` in Phase 1 eingeschlossen, Full-Vault nur als expliziter Opt-in. |

SessionId: codex-desktop-current-thread
