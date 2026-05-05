**Date:** 2026-05-05
**Status:** 🔵 Implemented
**Scope:** Control Spec fuer den vollstaendigen historischen SpecOps-Backfill aus Inventar, mit OpenSpec-Planung statt einzelner Batch-Child-Specs

---

## Kontext

Der Slice `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Full Historical Spec Backfill.md` ist als `historical-001` akzeptiert. Er hat geliefert:

1. ein erstes Spec-Source-Inventar unter `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`,
2. Klassifikationsregeln fuer narrative Specs, completed narrative specs, OpenSpec canonical specs, OpenSpec change artifacts und Plan-/Evidence-Artefakte,
3. ein Backfill-Coverage-Dashboard,
4. fuenf erste historische Spec-Entities im Batch `historical-001`.

Der Name des Backlog-Items `full-historical-spec-backfill` beschreibt aber weiterhin das groessere Ziel: perspektivisch sollen alle relevanten historischen Specs, Dokumente und OpenSpec-Beziehungen im SpecOps-Control-Plane-Modell auffindbar, klassifiziert und kontrolliert abgearbeitet werden.

Diese Control Spec ersetzt nicht das akzeptierte `historical-001`-Artefakt. Sie baut darauf auf und definiert den naechsten Ordnungsrahmen: aus dem Inventar soll ein OpenSpec Change beziehungsweise Implementierungsplan entstehen, der die verbleibenden Quellen in Phasen abarbeitbar macht, ohne fuer jede 5er- oder 20er-Gruppe eine neue Child-Spec zu schreiben.

## Ziel

SpecOps soll einen steuerbaren Full-Backfill-Prozess bekommen, der aus dem vorhandenen Inventar einen OpenSpec-basierten Abarbeitungsplan erzeugt.

Nach dieser Spec soll klar sein:

1. welche Quellgruppen aus dem Inventar in welcher Reihenfolge in den Full Backfill gehen,
2. welche Artefakte Primaer-Entities werden duerfen,
3. welche OpenSpec-Artefakte nur als Evidence, Relationship oder Plan-Historie verlinkt werden,
4. wie Dokumente von Specs getrennt oder bewusst als `type: document` modelliert werden,
5. welche Acceptance Gates pro Quellgruppe gelten,
6. wie verhindert wird, dass OpenSpec-Planartefakte und narrative User-Specs doppelt als konkurrierende Specs entstehen.

## In Scope

1. Definition eines OpenSpec-Change-Artefakts fuer den restlichen Full Historical Backfill.
2. Ableitung der OpenSpec-Tasks aus `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`.
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

1. Das OpenSpec-Planartefakt referenziert `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`.
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

### R3 - OpenSpec Control Change

Aus dieser Control Spec soll ein OpenSpec Change fuer die Abarbeitung entstehen.

Akzeptanzkriterien:

1. Der OpenSpec Change enthaelt mindestens `proposal.md`, `design.md`, `tasks.md`, `acceptance-criteria-matrix.md` und `implementation-evidence.md`.
2. `tasks.md` ist nach Quellgruppen und Phasen strukturiert.
3. Tasks sind abarbeitbar, ohne fuer jede Gruppe eine neue Child-Spec zu erstellen.
4. Jeder Delivery-Run darf ueber einen Scope Contract einen Teil der Tasks abarbeiten.
5. `implementation-evidence.md` sammelt pro Run die erzeugten Entities, Guards und Verification-Ergebnisse.

### R4 - Coverage And Verification Model

Der Full Backfill braucht eine messbare Coverage-Logik.

Akzeptanzkriterien:

1. Die Acceptance-Matrix enthaelt pro Quellgruppe mindestens:
   - source path
   - expected source count
   - source_type
   - intended entity type
   - current imported count
   - skipped/linked-only count
   - metadata_quality summary
   - status
2. Die SpecOps-Coverage-Dashboard-Struktur bleibt der sichtbare Vault-Ort fuer Fortschritt.
3. Negative Guards verhindern, dass `source_type: openspec_change_artifact` als primaere Spec-Entity entsteht.
4. Der Plan definiert, wie bereits importierte Entities erkannt und nicht doppelt erzeugt werden.

### R5 - Backlog Discipline

Das bestehende Backlog-Item bleibt der Anker fuer das Gesamtziel.

Akzeptanzkriterien:

1. `full-historical-spec-backfill` bleibt sichtbar und verweist auf den akzeptierten `historical-001`-Slice und diese Control Spec.
2. `automated-metadata-reconstruction` bleibt separat.
3. Neue Scope-Erweiterungen werden entweder als Task im OpenSpec Change oder als eigenes Backlog-Item sichtbar gemacht.
4. Ein Delivery-Run ohne Scope Contract ist nicht erlaubt.

## Decision Freeze Pack

### Zielbild und Scope

Diese Control Spec definiert den Ordnungsrahmen fuer den restlichen Full Historical Backfill. Die Umsetzung soll danach ueber einen OpenSpec Change mit Phasen/Tasks laufen, nicht ueber viele kleine neue Child-Specs.

### Betroffene Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/backfill-coverage.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/documents/`
5. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/full-historical-spec-backfill.md`
6. OpenSpec Change unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/changes/`

### Secret-/Config-Contract

Keine Secrets. Alle Quellen bleiben lokal im DanielsVault.

### Datenmigration/Fallback

Kein Big-Bang. Der OpenSpec Change steuert Phasen und Teilruns. Jeder Teilrun muss bereits vorhandene Entities erkennen und Duplikate vermeiden. Historische Source-Dateien bleiben unveraendert.

### Externe Integrationen

Keine externen Integrationen.

### Sicherheits-/Exposure-Entscheidungen

Keine externe Synchronisierung. Private Spec-Pfade duerfen lokal in SpecOps referenziert werden, bleiben aber Vault-lokal.

### Abnahmekriterien Go/No-Go

Go:

1. Control Spec ist erstellt und mit `full-historical-spec-backfill` verknuepft.
2. OpenSpec Change kann aus dem Inventar erstellt werden.
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
2. Codex: erstellt daraus den OpenSpec Change, sobald die Control Spec akzeptiert oder zur Umsetzung freigegeben wird.

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

Success Criteria:

1. Checks 1-4 geben Exit-Code `0` zurueck.
2. Manuelles Review bestaetigt, dass die Control Spec keine direkte Entity-Erstellung fordert und den OpenSpec Change als naechsten Steuerungsschritt beschreibt.

## Implementation Readiness

Diese Spec ist bereit fuer den naechsten Schritt, wenn:

1. der User bestaetigt, dass der restliche Full Backfill ueber einen OpenSpec Change statt ueber viele Batch-Child-Specs laufen soll,
2. keine blockierenden MISSING- oder DECISION-Marker offen sind,
3. die OpenSpec-Planung als naechster Artefakttyp akzeptiert ist.

Aktueller Stand: implementation-ready als Control Spec, vorbehaltlich User-Akzeptanz des Steuerungswegs.

## Implementation Evidence

Umgesetzt am 2026-05-05 im OpenSpec Mode.

OpenSpec Change:

`/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/changes/specops-full-historical-backfill-control/`

Erstellte OpenSpec-Artefakte:

1. `scope-contract.md`
2. `proposal.md`
3. `design.md`
4. `specs/specops-historical-backfill-control/spec.md`
5. `tasks.md`
6. `acceptance-criteria-matrix.md`
7. `spec-deltas.md`
8. `implementation-evidence.md`

Scope-Ergebnis:

1. Der OpenSpec Change steuert den restlichen Full Historical Backfill.
2. `historical-001` bleibt akzeptierte Baseline und wird nicht erneut importiert.
3. Die eigentlichen Backfill-Phasen sind als Folgeausfuehrung definiert, nicht in diesem Change importiert.
4. Future Runs muessen jeweils einen Scope Contract gegen den OpenSpec-Plan nutzen.

Verification vom 2026-05-05:

| Check | Status | Evidence |
|---|---|---|
| Control Spec Check 1 | ran | Control Spec Datei existiert. |
| Control Spec Check 2 | ran | `spec-source-inventory`, `historical-001`, `OpenSpec` und `full-historical-spec-backfill` sind auffindbar. |
| Control Spec Check 3 | ran | `type: spec`, `type: document`, `openspec_change_artifact` und `metadata_quality` sind auffindbar. |
| Control Spec Check 4 | ran | Backlog-Item verweist auf akzeptierten Slice und Control Spec. |
| OpenSpec validate | ran | `openspec validate specops-full-historical-backfill-control --strict --json` meldete `valid: true`. |
| OpenSpec status | ran | `openspec status --change specops-full-historical-backfill-control --json` meldete alle Kernartefakte als `done`. |
| Marker sanity | ran | Kein formaler missing/decision/blocked Marker in Control Spec oder OpenSpec Change. |
| Task sanity | ran | Keine offenen Checkbox-Tasks und kein blocked-as-done Pattern in `tasks.md`. |

Runtime-Validierung:

Nicht anwendbar. Dieser Change erzeugt OpenSpec-Planungs- und Steuerartefakte fuer SpecOps und aendert keine lauffaehige Anwendung, kein Docker-Compose-Target und keinen NCG-Backend-Buildpfad. `check-build-watcher` wurde deshalb nicht armiert.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | Nach Akzeptanz von `historical-001` vorgeschlagen, den restlichen Full Backfill ueber ein OpenSpec-Steuerartefakt aus dem Inventar abzuarbeiten. |
| 2026-05-05 | Codex | Control Spec fuer den restlichen Full Historical Backfill erstellt. |
| 2026-05-05 | Codex | OpenSpec Scope Contract fixiert und Change `specops-full-historical-backfill-control` erstellt. |
| 2026-05-05 | Codex | OpenSpec-Artefakte, Acceptance Matrix und Evidence erstellt, verifiziert und Control Spec auf Implemented gesetzt. |

SessionId: codex-desktop-current-thread
