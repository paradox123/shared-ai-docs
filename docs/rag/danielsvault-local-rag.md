# DanielsVault Local RAG

## Ziel

Dieses Projekt beschreibt ein lokales RAG-System fuer DanielsVault als praktische Wissensschicht fuer lokale Dokumentation, Specs und Notes.

Es soll bewusst klein, lokal und nachvollziehbar starten, statt sofort eine grosse "AI-Plattform" ueber alle Inhalte zu werden.

## Warum dieses Projekt sinnvoll ist

Im Vault bestehen bereits mehrere klar getrennte Wissensraeume und Git-Grenzen:

- Vault Root
- `_shared/shared-ai-docs`
- `ncg/ncg-docs`
- `private`
- `sparkle`

Diese Struktur ist bereits in:

- `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
- `/Users/dh/Documents/DanielsVault/AGENTS.md`

dokumentiert.

Gerade diese klaren Grenzen machen ein lokales RAG sinnvoll:

1. Kontext kann repo- und domain-spezifisch gefiltert werden
2. Agents muessen nicht blind ueber alle Dokumente suchen
3. persoenliche, geteilte und technische Inhalte lassen sich sauber trennen

## Was das lokale RAG bezwecken soll

### 1. Praktischer Wissenszugriff

Das System soll spaeter Fragen wie diese unterstuetzen:

- Welche Docs beschreiben das lokale LiteLLM-Gateway?
- Welche Specs existieren zu einem Thema?
- Welche NCG-Dokumente sprechen ueber einen bestimmten Betriebsaspekt?
- Welche persoenlichen oder geteilten Notizen sind fuer ein Thema relevant?

### 2. Agent-Kontext

Das System soll nicht `rg` ersetzen, sondern semantische Vorkontext-Suche fuer:

- Codex
- GitHub Copilot
- Claude Code

ermoeglichen.

### 3. Strukturierter Datenzugriff

Das System soll Agents auch beim Zugriff auf strukturierte Daten unterstuetzen, ohne dafuer zuerst blind im Dateisystem suchen zu muessen.

Das ist besonders sinnvoll fuer:

- `json`-Artefakte mit stabilen Feldern
- reviewed artifacts
- Import- und Output-Dateien
- Konfigurations- und Mapping-Dateien
- spaeter optional `csv` oder andere tabellarische Quellen

Wichtig:

- fuer exakte Werte, IDs, Jahreszahlen oder Feldnamen ist semantische Suche allein meist nicht robust genug
- deshalb sollte das System neben dem Dokument-RAG einen kleinen strukturierten Retrieval-Layer haben
- der Agent kann dann zuerst gezielt nach Datensaetzen fragen und erst danach erklaerenden Dokumentkontext nachladen

## Was dieses Projekt nicht sein soll

- kein unkontrollierter Vollindex ueber alles
- kein Ersatz fuer praezise Code-Suche
- kein Cross-Domain-Mischsystem ohne Repository-Grenzen
- kein sofortiger Produktivdienst mit grossen Verfuegbarkeitsanspruechen
- kein Vorwand, exakte strukturierte Abfragen durch unscharfe Vektorsuche zu ersetzen

## Empfohlenes Zielbild

### Datenquellen der ersten Phase

Zunaechst textzentrierte Quellen plus gezielt ausgewaehlte strukturierte Artefakte:

- `DanielsVault/**/*.md`
- ausgewaehlte `*.json`, `*.yaml`, `*.txt` in Doku-Bereichen
- ausgewaehlte strukturierte Projektartefakte mit stabilen Feldern, zum Beispiel Output- oder Review-Dateien

Explizit nicht in Phase 1:

- `.git/`
- `.obsidian/`
- `node_modules/`
- Binaries
- grosse generierte Schema-Dateien
- Lockfiles

### Metadaten pro Chunk

Jeder Chunk sollte mindestens enthalten:

- `git_root`
- `domain`
- `path`
- `title`
- `section`
- `tags` oder abgeleitete Labels
- `last_modified`

### Strukturierte Projektionen

Fuer geeignete maschinenlesbare Quellen sollte das System zusaetzlich normalisierte Records ableiten.

Jeder Record sollte mindestens enthalten:

- `git_root`
- `domain`
- `path`
- `record_type`
- `entity_id` oder fachlicher Schluessel
- relevante Filterfelder wie zum Beispiel `year`, `service`, `status` oder `statement_id`

Beispielhafte Kandidaten in DanielsVault:

- Nebenkosten-Output-Dateien wie `einzelabrechnung.json`
- reviewed artifacts und Import-Manifest-Dateien
- spaeter Service- oder Konfigurations-Mappings aus NCG-Dokumentationsartefakten

### Suchstrategie

Empfohlen:

1. erst domain- oder git-root-basierter Filter
2. dann entweder strukturierte Abfrage oder semantische Suche, je nach Fragetyp
3. bei Bedarf beide Ergebnisse zusammenfuehren
4. optional spaeter Re-Ranking

Faustregel:

- dokumentorientierte "was/warum/welche Docs"-Fragen -> semantische Suche
- exakte "welcher Datensatz/welcher Wert/welche ID"-Fragen -> strukturierte Abfrage
- gemischte Aufgaben -> erst strukturierte Treffer, dann semantischen Kontext nachladen

## Ist das agentic RAG?

Nicht automatisch.

Es gibt hier drei Stufen:

1. klassisches Dokument-RAG:
   - Vektorindex ueber Dokumente
   - semantische Suche
2. hybrides Retrieval:
   - Dokument-RAG plus strukturierte Abfragen ueber projizierte Records
   - der Retrieval-Typ wird aber noch fest verdrahtet oder direkt vom Aufrufer gewaehlt
3. agentic RAG oder agentic retrieval:
   - ein Agent entscheidet selbst, ob er zuerst strukturierte Daten, semantische Treffer oder beide braucht
   - der Agent kann mehrstufig arbeiten, zum Beispiel erst `entity_id=ne3`, dann passende Erklaerungsdokumente, dann Antwort mit Quellen

Fuer DanielsVault ist die sinnvolle Zielrichtung:

- technisch zuerst hybrides Retrieval bauen
- spaeter fuer Codex, Claude oder Copilot agentische Orchestrierung darueberlegen

## Empfohlener technischer Start

### Phase 1

- Python
- FastAPI
- Qdrant
- lokales oder API-basiertes Embedding-Modell
- einfache CLI oder kleine API fuer Suche
- kleine strukturierte Query-Schicht fuer ausgewaehlte Records

### Phase 2

- Evaluation-Set mit echten Fragen aus DanielsVault
- Antwortqualitaet und Retrieval-Qualitaet messen
- strukturierte Retrieval-Faelle gegen Dokument-RAG abgrenzen
- optionale Agent-Integration

### Phase 3

- Re-Ranking
- Incremental re-indexing
- MCP- oder Agent-Anbindung
- agentische Auswahl zwischen semantischer und strukturierter Retrieval-Schicht

## Empfohlene erste bounded Changes

1. Datenquellen und Ignore-Regeln definieren
2. Ingestion + Chunking Pipeline fuer Dokumente
3. strukturierte Projektionen fuer ausgewaehlte Datentypen
4. Embeddings + Vector Store Index
5. hybride Retrieval API
6. Evaluation Harness
7. Agent-Integration

## Artefakte, die dieses Projekt spaeter liefern sollte

1. Repo mit lauffaehiger lokaler Demo
2. Architekturdiagramm
3. Evaluationsreport
4. Lessons Learned zu Retrieval-Qualitaet und Domain-Grenzen

## Verweis auf die Parent-Spec

Die erste Parent-Spec liegt unter:

- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13 DanielsVault Local RAG Wissensplattform.md`
