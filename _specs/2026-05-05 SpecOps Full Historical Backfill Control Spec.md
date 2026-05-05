**Date:** 2026-05-05
**Status:** 🟡 Implementation-ready fuer neuen Delivery-Plan
**Scope:** Control Spec fuer den vollstaendigen historischen SpecOps-Backfill aus Inventar, mit Scope-Contract-Planung statt einzelner Batch-Child-Specs

---

## Kontext

Der Slice `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Full Historical Spec Backfill.md` ist als `historical-001` akzeptiert. Er hat geliefert:

1. ein erstes Spec-Source-Inventar unter `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`,
2. Klassifikationsregeln fuer narrative Specs, completed narrative specs, OpenSpec canonical specs, OpenSpec change artifacts und Plan-/Evidence-Artefakte,
3. ein Backfill-Coverage-Dashboard,
4. fuenf erste historische Spec-Entities im Batch `historical-001`.

Der Name des Backlog-Items `full-historical-spec-backfill` beschreibt aber weiterhin das groessere Ziel: perspektivisch sollen alle relevanten historischen Specs, Dokumente und OpenSpec-Beziehungen im SpecOps-Control-Plane-Modell auffindbar, klassifiziert und kontrolliert abgearbeitet werden.

Diese Control Spec ersetzt nicht das akzeptierte `historical-001`-Artefakt. Sie baut darauf auf und definiert den naechsten Ordnungsrahmen: aus dem Inventar soll ein neuer Scope-Contract-basierter Implementierungsplan entstehen, der die verbleibenden Quellen in Phasen abarbeitbar macht, ohne fuer jede 5er- oder 20er-Gruppe eine neue Child-Spec zu schreiben.

## Ziel

SpecOps soll einen steuerbaren Full-Backfill-Prozess bekommen, der aus dem vorhandenen Inventar einen konkreten Abarbeitungsplan mit wiederholbaren Scope Contracts erzeugt.

Nach dieser Spec soll klar sein:

1. welche Quellgruppen aus dem Inventar in welcher Reihenfolge in den Full Backfill gehen,
2. welche Artefakte Primaer-Entities werden duerfen,
3. welche OpenSpec-Artefakte nur als Evidence, Relationship oder Plan-Historie verlinkt werden,
4. wie Dokumente von Specs getrennt oder bewusst als `type: document` modelliert werden,
5. welche Acceptance Gates pro Quellgruppe gelten,
6. wie verhindert wird, dass OpenSpec-Planartefakte und narrative User-Specs doppelt als konkurrierende Specs entstehen.

## In Scope

1. Definition eines neuen Delivery-Control-Plans fuer den restlichen Full Historical Backfill.
2. Ableitung der Delivery-Tasks aus `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`.
3. Phasierung nach Quellgruppen:
   - shared-ai-docs `_specs/Completed`
   - shared-ai-docs aktive `_specs`
   - private `_specs`
   - NCG `docs/Specs`
   - DanielsVault RAG OpenSpec-Beziehungen
   - Nebenkostenabrechnung OpenSpec-Beziehungen
   - Mittelstand KI Startbahn Legacy OpenSpec-Beziehungen
   - historische Dokument-Entities, soweit sie aus den Spec-Quellen klar als Dokumente/ADRs/Guides erkennbar sind
4. Definition von Entity-Regeln fuer:
   - `type: spec`
   - `type: document`
   - related OpenSpec evidence
   - metadata quality
   - source relationship fields
5. Definition einer Acceptance-Matrix pro Quellgruppe.
6. Definition eines wiederholbaren Delivery-Modus: ein Scope Contract pro Abarbeitungs-Run, aber keine neue Child-Spec pro Batch.
7. Sichtbare Fortfuehrung des Backlog-Items `full-historical-spec-backfill`.

## Out of Scope

1. Keine direkte Entity-Erstellung in dieser Control Spec.
2. Keine automatische Massenmigration.
3. Keine Metadatenrekonstruktions-Automation.
4. Keine Umbenennung oder Veraenderung historischer Source-Dateien.
5. Keine pauschale Duplikation von OpenSpec `proposal.md`, `tasks.md`, `design.md`, `implementation-evidence.md` oder `acceptance-criteria-matrix.md` als primaere Spec-Entities.
6. Keine Modellentscheidung fuer Releases, Environments oder Skill-/Agent-Learnings.
7. Keine Abarbeitung der parallel bearbeiteten `SpecOps Dashboard UX Overview`-Spec.

## Requirements

### R1 - Inventory Baseline

Die Control Spec muss das bestehende Inventar als Baseline verwenden.

Akzeptanzkriterien:

1. Der neue Delivery-Plan referenziert `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`.
2. Jede Quellgruppe aus dem Inventar wird entweder einer Backfill-Phase zugeordnet oder bewusst als nicht vorhanden / nicht in Scope markiert.
3. Der akzeptierte Batch `historical-001` wird als bereits erledigte Baseline behandelt und nicht erneut importiert.

### R2 - Source-To-Entity Rules

Die Control Spec muss festlegen, welche Quellen zu welchen Entity-Typen werden duerfen.

Akzeptanzkriterien:

1. Narrative und completed narrative Specs duerfen primaere `type: spec` Entities werden.
2. Dokumente, ADRs, Guides und vergleichbare Wissensartefakte werden als `type: document` modelliert, nicht als Specs, sofern sie nicht selbst eine Spec sind.
3. OpenSpec canonical specs duerfen als canonical / related source verlinkt werden.
4. OpenSpec change artifacts duerfen nicht pauschal als primaere Spec-Entities entstehen.
5. Bei unklarer Abgrenzung muss `metadata_quality: inferred`, `missing` oder `conflict` sichtbar bleiben.

### R3 - Delivery Control Plan

Aus dieser Control Spec soll ein neuer Delivery-Control-Plan fuer die Abarbeitung entstehen. Ein frueherer, inzwischen archivierter OpenSpec-Change gilt fuer diese Spec nicht als gueltige Implementierungsbasis.

Akzeptanzkriterien:

1. Der neue Delivery-Plan enthaelt mindestens Scope Contract, Run-Tasks, Acceptance-Matrix und Implementation-Evidence.
2. Run-Tasks sind nach Quellgruppen, Phasen und konkreten Source-Subsets strukturiert.
3. Tasks sind abarbeitbar, ohne fuer jede Gruppe eine neue Child-Spec zu erstellen.
4. Jeder Delivery-Run muss ueber einen Scope Contract einen klar begrenzten Teil der Tasks abarbeiten.
5. Implementation-Evidence sammelt pro Run die erzeugten Entities, Guards und Verification-Ergebnisse.

### R4 - Coverage And Verification Model

Der Full Backfill braucht eine messbare Coverage-Logik.

Akzeptanzkriterien:

1. Die Acceptance-Matrix enthaelt pro Quellgruppe mindestens:
   - source path
   - expected source count
   - source_type
   - intended entity type
   - current imported count
   - remaining candidate count
   - skipped/linked-only count
   - metadata_quality summary
   - vorgeschlagene Run-Scale
   - status
2. Die SpecOps-Coverage-Dashboard-Struktur bleibt der sichtbare Vault-Ort fuer Fortschritt.
3. Negative Guards verhindern, dass `source_type: openspec_change_artifact` als primaere Spec-Entity entsteht.
4. Der Plan definiert, wie bereits importierte Entities erkannt und nicht doppelt erzeugt werden.
5. Jeder konkrete Delivery-Run muss mit exakten Source-Dateien oder einer exakten Source-Query starten; globale Platzhalter wie `included in 42 shared specs` oder `variable` reichen fuer Run-Akzeptanz nicht aus.

### R5 - Backlog Discipline

Das bestehende Backlog-Item bleibt der Anker fuer das Gesamtziel.

Akzeptanzkriterien:

1. `full-historical-spec-backfill` bleibt sichtbar und verweist auf den akzeptierten `historical-001`-Slice und diese Control Spec.
2. `automated-metadata-reconstruction` bleibt separat.
3. Neue Scope-Erweiterungen werden entweder als Task im Delivery-Plan oder als eigenes Backlog-Item sichtbar gemacht.
4. Ein Delivery-Run ohne Scope Contract ist nicht erlaubt.

## Decision Freeze Pack

### Zielbild und Scope

Diese Control Spec definiert den Ordnungsrahmen fuer den restlichen Full Historical Backfill. Die Umsetzung soll danach ueber einen neuen Delivery-Plan mit Phasen, Scope Contracts und Evidence laufen, nicht ueber viele kleine neue Child-Specs.

### Betroffene Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/backfill-coverage.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/documents/`
5. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/full-historical-spec-backfill.md`
6. Neuer Delivery-Plan / Scope Contract, der in dieser Session aus dieser Control Spec erstellt wird

### Secret-/Config-Contract

Keine Secrets. Alle Quellen bleiben lokal im DanielsVault.

### Datenmigration/Fallback

Kein Big-Bang. Scope Contracts steuern Phasen und Teilruns. Jeder Teilrun muss bereits vorhandene Entities erkennen und Duplikate vermeiden. Historische Source-Dateien bleiben unveraendert.

### Externe Integrationen

Keine externen Integrationen.

### Sicherheits-/Exposure-Entscheidungen

Keine externe Synchronisierung. Private Spec-Pfade duerfen lokal in SpecOps referenziert werden, bleiben aber Vault-lokal.

### Abnahmekriterien Go/No-Go

Go:

1. Control Spec ist erstellt und mit `full-historical-spec-backfill` verknuepft.
2. Neuer Delivery-Plan kann aus dem Inventar erstellt werden.
3. Quellgruppen, Entity-Regeln und negative OpenSpec-Dedupe-Guards sind definiert.
4. Abarbeitung kann ueber Scope Contracts erfolgen, ohne pro Batch neue Child-Specs zu schreiben.

No-Go:

1. OpenSpec-Artefakte werden unkontrolliert als Specs dupliziert.
2. Dokumente werden als Specs modelliert, obwohl `type: document` passender ist.
3. Automatisierung wird nebenbei gebaut.
4. Der akzeptierte Batch `historical-001` wird erneut importiert.
5. Tasks enthalten keine messbaren Acceptance Gates.

### Owner fuer offene Risiken

1. User: akzeptiert, ob diese Control Spec der richtige Ordnungsrahmen fuer den restlichen Full Backfill ist.
2. Codex: erstellt daraus den neuen Delivery-Plan beziehungsweise den ersten Scope Contract, sobald die Control Spec akzeptiert oder zur Umsetzung freigegeben wird.

## Delivery Run Scale Vorschlag

Die folgenden Skalen gelten fuer kuenftige Backfill-Runs. Sie ersetzen unklare Batch-Groessen und machen sichtbar, wann ein Run noch autonom kontrollierbar ist.

| Scale | Source Count | Geeignet fuer | Akzeptanz-Grenze |
|---|---:|---|---|
| S | 1-5 konkrete Source-Dateien | erster Run, unsichere Klassifikation, neue Entity-Regeln | alle Quellen einzeln gelistet; keine offenen Klassifikationsentscheidungen am Ende |
| M | 6-15 konkrete Source-Dateien | wiederholte narrative Specs mit bekanntem Muster | Duplicate-Guard und metadata_quality-Verteilung muessen dokumentiert sein |
| L | 16-30 konkrete Source-Dateien | ein vollstaendiger Ordnerabschnitt mit homogenem Typ | nur nach erfolgreichem S- oder M-Run; Review-Stichprobe verpflichtend |
| XL | mehr als 30 Source-Dateien | Inventar-/Coverage-Arbeit oder Automation | nicht als manueller Import-Run erlaubt; braucht eigenes Backlog-Item oder Automation-Spec |

Aktueller Source-Recount vom 2026-05-05:

| Phase | Source Path / Subset | Expected Source Count | source_type | Intended Entity Type | Current Imported Count | Remaining Candidate Count | Skipped / Linked-Only Count | metadata_quality Summary | Proposed Scale | Status |
|---:|---|---:|---|---|---:|---:|---:|---|---|---|
| 0 | `historical-001` batch | 5 | mixed narrative | `type: spec` | 5 | 0 | 0 | explicit/inferred/conflict | n/a | done |
| 1 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed/` | 32 | `completed_narrative_spec` plus support docs | `type: spec` or `type: document` by classification | 6 | 26 | 0 current | mixed | S first, then M | ready |
| 2 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/` active root files | 11 | `narrative_spec` | `type: spec` | 1 | 10 | 0 current | mixed | M | planned |
| 3 | `/Users/dh/Documents/DanielsVault/private/_specs/` | 19 | `narrative_spec` | `type: spec` | 2 | 17 | 0 current | explicit so far | M/L | planned |
| 4 | `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/` | 29 | `narrative_spec` / `completed_narrative_spec` | `type: spec` | 0 | 29 | 0 current | unknown | M then L | planned |
| 5 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/` | 19 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | relationship/evidence, not primary spec by default | 1 legacy OpenSpec-derived entity exists | 18 relationship candidates | tbd by narrative dedupe | explicit/unknown | S relationship audit | planned |
| 6 | `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/openspec/` | 17 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | relationship/evidence, not primary spec by default | 0 | 17 relationship candidates | tbd by narrative dedupe | unknown | S relationship audit | planned |
| 7 | `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/openspec/` | 87 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | relationship/evidence after narrative dedupe | 0 | 87 relationship candidates | tbd by narrative dedupe | unknown | XL blocked for manual import | planned |
| 8 | `/Users/dh/Documents/DanielsVault/private/mittelstand-ki-startbahn/_legacy/v1-node-prototype/openspec/` | 35 | `openspec_canonical_spec` / `openspec_change_artifact` / `plan_or_evidence_artifact` | legacy relationship/evidence | 0 | 35 relationship candidates | tbd by narrative dedupe | unknown | XL blocked for manual import | planned |
| 9 | Historical document-like sources discovered during narrative review | per-run exact list required | document-like | `type: document` | 3 current ADR documents | tbd per run | tbd per run | explicit so far | S | planned |

Vorgeschlagener erster Run:

| Run | Scale | Source Subset | Expected Source Count | Intended Entity Type | Acceptance Gate |
|---|---|---|---:|---|---|
| Phase 1A | S | `2026-03-23 Nebenkostenabrechnung Einzelabrechnung.md`, `2026-03-24 Nebenkostenabrechnung Applikation.md`, `2026-03-26 Stromkosten-Datenkorrektur und Test-Oracle Alignment.md`, `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`, `2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md` | 5 | primary `type: spec` unless duplicate guard finds an existing primary entity | five sources classified, imported or explicitly skipped with duplicate/evidence reason; dashboard count updated |

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Shell-/Plattformvertrag:

1. Zielplattform ist macOS.
2. Shell ist `zsh`.
3. `test`, `rg` und `find` sind verfuegbar.

Pflichtchecks fuer diese Spec-Erstellung:

1. `test -f "_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Full Historical Backfill Control Spec.md"`
2. `rg -n 'spec-source-inventory|historical-001|OpenSpec|full-historical-spec-backfill' "_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Full Historical Backfill Control Spec.md"`
3. `rg -n 'type: spec|type: document|openspec_change_artifact|metadata_quality' "_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Full Historical Backfill Control Spec.md"`
4. `rg -n 'control_spec: .+2026-05-05 SpecOps Full Historical Backfill Control Spec.md|promoted_to: .+2026-05-05 SpecOps Full Historical Spec Backfill.md' _shared/SpecOps/Entities/backlog/full-historical-spec-backfill.md`
5. `find "_shared/shared-ai-docs/_specs/Completed" -type f -name "*.md" | wc -l`
6. `find "_shared/shared-ai-docs/_specs" -maxdepth 1 -type f -name "*.md" | wc -l`
7. `find "private/_specs" -type f -name "*.md" | wc -l`
8. `find "ncg/ncg-docs/docs/Specs" -type f -name "*.md" | wc -l`

Success Criteria:

1. Checks 1-8 geben Exit-Code `0` zurueck.
2. Count-Checks bestaetigen die in der Delivery Run Scale dokumentierten Quellgruppen-Zahlen oder die Spec wird vor dem Run aktualisiert.
3. Manuelles Review bestaetigt, dass die Control Spec keine direkte Entity-Erstellung fordert und den neuen Delivery-Plan als naechsten Steuerungsschritt beschreibt.

## Implementation Readiness

Diese Spec ist bereit fuer den naechsten Schritt, wenn:

1. keine blockierenden MISSING- oder DECISION-Marker offen sind,
2. die Delivery Run Scale konkrete Counts und einen ersten Source-Subset-Vorschlag enthaelt,
3. vor Entity-Erstellung ein finaler Scope Contract fuer genau einen Run fixiert wird.

Aktueller Stand: implementation-ready als Control Spec fuer einen neuen Delivery-Plan. Es wird kein bestehender OpenSpec-Change als gueltige Implementierungsbasis vorausgesetzt.

## Implementation Evidence

Autonomous Review Resolution vom 2026-05-05:

1. Der archivierte, zu enge OpenSpec-Change wird nicht mehr als gueltige Implementierungsbasis behandelt.
2. Nicht replaybare OpenSpec-Validation-Evidence wurde entfernt.
3. Coverage-Akzeptanz wurde von groben Platzhaltern auf aktuelle Source-Counts, Remaining Counts und Run-Scale-Vorschlaege umgestellt.
4. Der erste vorgeschlagene Delivery-Run ist als Scale-S-Run mit fuenf konkreten Source-Dateien definiert.

Verification vom 2026-05-05:

| Check | Status | Evidence |
|---|---|---|
| Control Spec Check 1 | ran | Control Spec Datei existiert. |
| Control Spec Check 2 | ran | `spec-source-inventory`, `historical-001`, `OpenSpec` und `full-historical-spec-backfill` sind auffindbar. |
| Control Spec Check 3 | ran | `type: spec`, `type: document`, `openspec_change_artifact` und `metadata_quality` sind auffindbar. |
| Control Spec Check 4 | ran | Backlog-Item verweist auf akzeptierten Slice und Control Spec. |
| Source Recount | ran | Completed `32`, shared active root `11`, private `_specs` `19`, NCG `docs/Specs` `29`. |
| Marker sanity | ran | Kein formaler missing/decision/blocked Marker in Control Spec. |
| Old OpenSpec Evidence | removed | Kein bestehender OpenSpec-Change wird als replaybare Evidence vorausgesetzt. |

Runtime-Validierung:

Nicht anwendbar. Diese Spec erzeugt Planungs- und Steuerartefakte fuer SpecOps und aendert keine lauffaehige Anwendung, kein Docker-Compose-Target und keinen NCG-Backend-Buildpfad. `check-build-watcher` wurde deshalb nicht armiert.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | Nach Akzeptanz von `historical-001` vorgeschlagen, den restlichen Full Backfill ueber ein Steuerartefakt aus dem Inventar abzuarbeiten. |
| 2026-05-05 | Codex | Control Spec fuer den restlichen Full Historical Backfill erstellt. |
| 2026-05-05 | Codex | Einen frueheren, zu engen Planungs-Change erstellt; dieser ist archiviert und gilt nicht als Implementierungsbasis. |
| 2026-05-05 | Codex | Review-Findings autonom aufgeloest: veraltete OpenSpec-Change-Evidence entfernt, Status auf neuen Delivery-Plan umgestellt und konkrete Run-Scale mit Source-Counts ergaenzt. |

SessionId: codex-desktop-current-thread
