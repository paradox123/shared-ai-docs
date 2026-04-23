**Date:** 2026-04-13  
**Status:** 🟢 Accepted  
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
2. `01` Ingestion Scope und Metadaten
3. `02` Strukturierte Projektionen
4. `03` Embeddings, Index und hybrides Retrieval
5. `04` Evaluation und Qualitaetsgates
6. `05` Agent-Integration fuer `research-for-review` und `spec-closeout`

Empfehlung:

- zuerst Child-Spec `01` umsetzen, weil dadurch der spaetere Index sauber und domain-treu bleibt

## Wiederverwendungsregel fuer Child-Specs und Runtime-Pakete

Normative Regel:

- Die Child-Specs `01..05` definieren den fachlichen und verifikatorischen Vertrag.
- Das konkret eingesetzte Runtime-Paket ist ein Implementierungsdetail, solange CLI-Contract, Scope-Regeln, Metadatenpflichten und Qualitaetsgates unveraendert erfuellt werden.
- Ein Paketwechsel (z. B. auf `qmd`) ist in Phase 1 zulaessig, wenn die gleiche Verifikationsmatrix ohne Abschwaechung besteht.

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

### Implementierungsprofil (tool-agnostisch)

Verbindlich ist der Runtime-Contract, nicht ein einzelner Technologie-Stack.

Normative Anforderungen:

- Es existiert ein stabiler `rag` CLI-Contract fuer die in `01..05` definierten Commands.
- Scope-Grenzen, Ignore-Regeln, Metadatenminimum, strukturierte Filtersemantik und Eval-Gates bleiben unveraendert.
- Ergebnisse sind maschinell lesbar und reproduzierbar.
- Ein Backend darf intern ersetzt werden, wenn keine Breaking-Aenderung am Contract entsteht.

### Moegliche Runtime-Backends (nicht exklusiv)

Beispielhafte Optionen fuer die Umsetzung:

- Python-basierte Eigenimplementierung
- `qmd`-basierter Runtime-Adapter
- lokale Such-/Index-Komponenten in anderen Sprachen

Normative Regel:

- Kein Vendor-/Package-Lock-in auf Parent-Spec-Ebene; die Abnahme erfolgt ueber Command-Evidenz und Qualitaetsmetriken, nicht ueber Stack-Wahl.

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

Verbindliche CLI-basierte Verifikationsstrecke:

- Normative Gate-Quelle ist die vollstaendige Command- und Assertion-Checklist in Child-Specs `01..05`.
- Alle dort definierten Commands inklusive Assertions sind fuer Abnahme vollstaendig auszufuehren; Teillisten im Parent sind nur orientierend.
- Vor den Child-Commandstrecken ist ein harter CLI-Preflight verpflichtend (`command -v rag`, `rag --version`, non-empty Versionsnachweisdatei).
- Jeder Verifikationsschritt gilt nur bei realer Ausfuehrung mit Exit-Code `0` als bestanden; Status `blocked` oder `failed` ist ein Gate-Fehler und nicht DoD-faehig.

Orientierende Beispielkommandos (nicht vollstaendige Gate-Liste):

1. `command -v rag >/dev/null`
2. `rag --version > .rag/runs/00-rag-version.txt && test -s .rag/runs/00-rag-version.txt`
3. `rag ingest run --scope ncg/ncg-docs`
4. `rag records project --scope ncg/ncg-docs --record-type ci_setting_fact`
5. `rag retrieve semantic --scope ncg/ncg-docs --query "Wo ist die Migration zu Hetzner-Dev dokumentiert?"`
6. `rag retrieve structured --scope ncg/ncg-docs --record-type ci_setting_fact --filter "setting_name=DEPLOY_TARGET"`
7. `rag retrieve hybrid --scope ncg/ncg-docs --record-type ci_setting_fact --query "Welche CI-Variable steuert das Deployment-Target?"`
8. `rag workflow research-for-review --scope ncg/ncg-docs --query "Welche Dokumente sind fuer den Docker BaseUrl Fix relevant?" --top-k 5 --format json`
9. `rag workflow spec-closeout --scope ncg/ncg-docs --change "Docker BaseUrl Fix" --top-k 5 --format json`
10. `rag eval run --set /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.v0.jsonl --top-k 5`
11. `rag eval report --metrics domain_hit_rate,file_hit_rate,cross_domain_leakage`

Contract-Regel:

- Die Kommandos sind als stabile Capability-Schnittstelle zu verstehen.
- Ob intern eine Eigenimplementierung, ein Adapter oder ein Paket wie `qmd` ausgefuehrt wird, ist fuer die Spec-Erfuellung nachrangig.
- Nicht zulaessig ist ein Paketwechsel, der nur durch Abschwaechung von Acceptance/Verification gruen wird.

Anforderung an den Eval-Lauf:

- Die Fragen aus `evaluation-set.v0.jsonl` muessen gegen den Retriever laufen.
- Das Ergebnis muss pro Frage mindestens Top-5 Treffer, Domain-Treffer und Datei-Treffer enthalten.
- Blocking-Gates in Phase 1 sind `domain_hit_rate`, `file_hit_rate`, `cross_domain_leakage` gemaess Child-Spec `04`.
- `source_precision` darf optional als zusaetzliche Monitoring-Metrik reportet werden, ist aber kein Phase-1-Blocking-Gate.
- Die orientierende Parent-Kommandoliste und Report-Metriken duerfen diese Child-Gate-Definition nicht ueberschreiben.

Kommando-/Parameterkonvention ist in Child-Specs `01..05` als CLI-Contract fixiert und bleibt fuer Phase 1 stabil.

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
- `[REVIEW Scope-Split umgesetzt: Parent-Spec bleibt als Zielbild, Umsetzung erfolgt ueber nummerierte Child-Specs 01-05]`

## Archivierte Phase-1 Changes

1. [2026-04-21 01 DanielsVault RAG Ingestion Scope und Metadaten](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-21%2001%20DanielsVault%20RAG%20Ingestion%20Scope%20und%20Metadaten.md)
2. [2026-04-21 02 DanielsVault RAG Strukturierte Projektionen](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-21%2002%20DanielsVault%20RAG%20Strukturierte%20Projektionen.md)
3. [2026-04-21 03 DanielsVault RAG Embeddings Index und Hybrides Retrieval](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-21%2003%20DanielsVault%20RAG%20Embeddings%20Index%20und%20Hybrides%20Retrieval.md)
4. [2026-04-21 04 DanielsVault RAG Evaluation und Qualitaetsgates](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-21%2004%20DanielsVault%20RAG%20Evaluation%20und%20Qualitaetsgates.md)
5. [2026-04-21 05 DanielsVault RAG Agent Integration Research-for-Review und Spec-Closeout](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-21%2005%20DanielsVault%20RAG%20Agent%20Integration%20Research-for-Review%20und%20Spec-Closeout.md)

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
| 2026-04-21 | User + Codex | Scope-Risiko durch Split in nummerierte Child-Specs 01-05 reduziert und Implementierungsreihenfolge im Dateinamen verankert. |
| 2026-04-21 | Codex | CLI-Parameterkonvention auf `--scope` vereinheitlicht und Scope-Split-Hinweise konsolidiert. |
| 2026-04-22 | Codex | Verifikationsstrecke auf konkrete Commands ohne Platzhalter aktualisiert (`ci_setting_fact` fixiert). |
| 2026-04-23 | User + Codex | Parent-Spec geschaerft: Runtime-Paket als Implementierungsdetail festgelegt, Child-Spec-Contract als verbindliche Abnahmebasis beibehalten (u. a. `qmd` als zulaessige Option). |
| 2026-04-23 | User + Codex | Review-Findings eingearbeitet: Parent-Verifikation auf vollstaendige Child-Gates `01..05` harmonisiert, `source_precision` als optionales Monitoring praezisiert und veralteten `Change A`-Verweis entfernt. |
| 2026-04-23 | User + Codex | Metrik-Governance weiter gehaertet: Parent-Beispielliste explizit als nicht vollstaendig markiert und Child-Gate-Prioritaet bei `source_precision` nochmals klargestellt. |
| 2026-04-23 | User + Codex | Verifikationsgate gehaertet: harter `rag`-Install-Preflight und Regel ergaenzt, dass `blocked/failed` nicht als bestandene Abnahme gewertet werden duerfen. |
| 2026-04-23 | User + Codex | Status auf `🟢 Accepted` gesetzt: Child-Specs 01-05 wurden runtime-seitig umgesetzt, erneut gruen verifiziert und OpenSpec-Changes archiviert. |

SessionId: codex-desktop-current-thread
