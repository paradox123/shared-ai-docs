**Date:** 2026-05-05
**Status:** 🟢 Accepted
**Scope:** SpecOps Full Historical Spec Backfill Inventarisierung und kontrollierter Backfill historischer User-Specs, Spec-Ordner und OpenSpec-Artefakte

---

## Kontext

SpecOps hat bisher nur einen kleinen Ausschnitt historischer Specs als Entity Notes erfasst. Der Mixed Backfill Pilot hat gezeigt, dass Rekonstruktion ueber mehrere Projekte funktioniert, aber noch keine vollstaendige Uebersicht ueber alle Spec-Quellen existiert.

Das bestehende Backlog-Item `full-historical-spec-backfill` ist dafuer triaged. Die wichtigste Erkenntnis fuer diesen Slice: Vor jedem weiteren Backfill muss zuerst inventarisiert werden, **welche Spec-Quellen ueberhaupt existieren**. Diese Inventarisierung ist aber nur der erste Arbeitsschritt, nicht das Ergebnis des Slice.

Dabei gibt es mindestens zwei verschiedene Quelltypen:

1. User-/Narrative Specs:
   - typischerweise in `_specs/`, `specs/` oder `Specs/`
   - oft vom User oder in direkter Zusammenarbeit erstellt
   - enthalten Anforderungen, Scope, Entscheidungen, Acceptance Criteria, Evidence oder Retros
2. OpenSpec-Artefakte:
   - typischerweise unter `openspec/specs/` und `openspec/changes/`
   - oft aus User-Specs oder Delivery-Slices hervorgegangen
   - sind eher formale Plan-/Change-/Delta-/Evidence-Artefakte als primaere narrative Specs

Eine erste lokale Discovery zeigt, dass relevante Spec-/OpenSpec-Pfade ueber mehrere Vault- und Projektbereiche verteilt sind, u. a.:

1. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/`
2. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/`
3. `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/openspec/`
4. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/`
5. `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/openspec/`
6. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_legacy/v1-node-prototype/openspec/`
7. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/specs/`
8. `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/`

Dieser Slice promoted ausschliesslich das bestehende Backlog-Item `full-historical-spec-backfill` mit `candidate_slice: SpecOps Backfill`.

## Ziel

SpecOps soll nicht nur wissen, wo historische Specs liegen, sondern einen ersten sichtbaren historischen Backfill liefern.

Das Ergebnis dieses Slice ist daher dreiteilig:

1. ein belastbares Inventar der relevanten Spec-Quellen,
2. klare Klassifikationsregeln fuer User-/Narrative Specs, completed Specs und OpenSpec-Artefakte,
3. ein erster kontrollierter Batch von 5-10 neuen historischen Spec-Entities, die in SpecOps sichtbar und ueber ein Coverage-Dashboard nachvollziehbar sind.

Nach diesem Slice soll beantwortbar sein:

1. Welche Spec-Quellorte existieren im DanielsVault?
2. Welche Quellen sind primaere User-/Narrative Specs?
3. Welche Quellen sind OpenSpec-Plan-/Change-/Evidence-Artefakte?
4. Welche Quellen sind bereits als SpecOps Entity Notes erfasst?
5. Welche Backfill-Kandidaten wurden in einem ersten kontrollierten Batch als `type: spec` Entity Notes erfasst?
6. Welche Quellen duerfen nicht als primaere Spec-Entities dupliziert werden, sondern werden nur als related evidence / openspec artifacts verlinkt?

Ein reines Inventar ohne neue Spec-Entities ist fuer diesen Slice nicht ausreichend.

## In Scope

1. Inventarisierung relevanter Spec-Quellorte im DanielsVault.
2. Klassifikation von Quellen in mindestens:
   - `narrative_spec`
   - `completed_narrative_spec`
   - `openspec_canonical_spec`
   - `openspec_change_artifact`
   - `plan_or_evidence_artifact`
3. Erstellung eines Backfill-Inventars als Markdown-Dashboard oder Reference-Datei unter `_shared/SpecOps/`.
4. Kontrollierter erster Backfill-Batch von 5-10 historischen **narrativen** Specs als `type: spec` Entity Notes.
5. OpenSpec-Artefakte werden im ersten Slice nur klassifiziert und verlinkbar gemacht, nicht pauschal als eigene Spec-Entities dupliziert.
6. Missing-/Conflict-Metadaten werden sichtbar gelassen.
7. Backlog-Item `full-historical-spec-backfill` mit dieser Child-Spec verknuepfen.

## Out of Scope

1. Kein automatisierter Backfill aller 200+ gefundenen Markdown-Dateien.
2. Keine automatische Metadatenrekonstruktion als Tooling.
3. Keine Veraenderung an OpenSpec-Artefakten.
4. Keine Migration oder Umbenennung historischer Specs.
5. Keine Release-/Environment-/Learning-Modelle.
6. Keine De-Duplizierung aller User-Spec/OpenSpec-Beziehungen im ersten Slice.
7. Keine Loeschung oder Korrektur historischer Quelltexte.

## Requirements

### R1 - Source Inventory

Der Slice muss zuerst ein Inventar relevanter Spec-Quellorte erstellen.

Akzeptanzkriterien:

1. Das Inventar nennt alle gefundenen `_specs/`, `specs/`, `Specs/` und `openspec/` Quellorte.
2. Das Inventar unterscheidet User-/Narrative Specs von OpenSpec-Artefakten.
3. Das Inventar enthaelt pro Quellort mindestens:
   - Pfad
   - Quelletyp
   - grobe Dateianzahl
   - Backfill-Prioritaet
   - Hinweise zu Duplikat-/Ableitungsrisiken

### R2 - Source Classification Rules

Der Slice muss festlegen, wie Quellen beim Backfill behandelt werden.

Akzeptanzkriterien:

1. Narrative Specs duerfen `type: spec` Entity Notes werden.
2. Completed narrative specs duerfen `status: accepted` oder `metadata_quality: inferred` erhalten, je nach Evidenz.
3. OpenSpec canonical specs duerfen als related source / openspec source verlinkt werden.
4. OpenSpec change artifacts wie `proposal.md`, `tasks.md`, `design.md`, `implementation-evidence.md`, `acceptance-criteria-matrix.md` werden nicht automatisch als primaere Specs dupliziert.
5. Wenn User-Spec und OpenSpec-Artefakt denselben Change beschreiben, muss die Entity-Beziehung sichtbar sein statt zwei konkurrierende Specs zu erzeugen.

### R3 - First Historical Backfill Batch

Der Slice muss einen ersten kontrollierten Backfill-Batch aus historischen narrativen Specs erstellen.

Akzeptanzkriterien:

1. 5-10 neue `type: spec` Entity Notes werden angelegt; die Inventarisierung allein erfuellt R3 nicht.
2. Die Auswahl kommt aus mindestens zwei verschiedenen Quellorten oder Projektkontexten.
3. Jede Entity hat mindestens `type`, `id`, `title`, `project`, `status`, `source`, `metadata_quality`.
4. Jede Entity dokumentiert, ob Metadaten `explicit`, `inferred`, `missing` oder `conflict` sind.
5. OpenSpec-Beziehungen werden als Felder oder Hinweise sichtbar, wenn sie sicher erkennbar sind.
6. Jede Entity des ersten Batches traegt `backfill_batch: historical-001`, damit der Slice deterministisch pruefbar bleibt.

### R4 - Backfill Coverage Dashboard

SpecOps muss Backfill-Fortschritt sichtbar machen.

Akzeptanzkriterien:

1. Ein Dashboard oder eine Reference-Datei zeigt Inventar und Backfill-Status.
2. Die View zeigt mindestens Source Path, Source Type, Count, Backfill Status und Notes.
3. Das Root-Dashboard verlinkt oder embedded die Backfill-Coverage-Sicht.
4. Missing Metadata bleibt separat sichtbar und wird nicht durch den Backfill versteckt.

### R5 - Backlog Discipline

Der Slice bleibt an das bestehende Backlog-Item gebunden.

Akzeptanzkriterien:

1. `full-historical-spec-backfill` ist mit dieser Spec verlinkt.
2. Automatisierung bleibt im Backlog-Item `automated-metadata-reconstruction`.
3. Release-, Environment- und Learning-Follow-ups bleiben eigene Backlog-Themen.
4. Neue Backfill-Probleme werden als Backlog sichtbar gemacht oder explizit im Evidence-Abschnitt dokumentiert.

## Decision Freeze Pack

### Zielbild und Scope

Dieser Slice schafft eine belastbare Inventar- und Backfill-Grundlage und setzt zwingend einen ersten kontrollierten Backfill-Batch um. Die Inventarisierung dient der sicheren Auswahl und Klassifikation; sie ist kein eigenstaendiger Done-Zustand.

### Betroffene Vault-Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
5. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/full-historical-spec-backfill.md`
6. Diese Child-Spec unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/`

### Secret-/Config-Contract

Keine Secrets. Alle Quellen bleiben lokal im DanielsVault.

### Datenmigration/Fallback

Kein Big-Bang. Inventarisierung zuerst, danach 5-10 kontrollierte Entity Notes im Batch `historical-001`. Nicht erfasste Quellen bleiben ueber Inventar, Dateisuche und RAG auffindbar.

### Externe Integrationen

Keine externen Integrationen.

### Sicherheits-/Exposure-Entscheidungen

Keine Exposure-Aenderung. Es werden keine Spec-Metadaten extern synchronisiert.

### Abnahmekriterien Go/No-Go

Go:

1. Inventar der relevanten Spec-Quellorte existiert.
2. Quelltypen und OpenSpec-Behandlungsregeln sind dokumentiert.
3. 5-10 neue historische narrative Spec-Entities existieren.
4. Backfill-Coverage ist in SpecOps sichtbar.
5. Backlog-Item `full-historical-spec-backfill` ist mit dieser Spec verlinkt.

No-Go:

1. OpenSpec-Artefakte werden pauschal als primaere Specs dupliziert.
2. Alle gefundenen Markdown-Dateien werden unkontrolliert backfilled.
3. Unsichere Metadaten werden als sicher dargestellt.
4. Automatisierung wird nebenbei gebaut.
5. Nur das Inventar wird erstellt, aber kein erster historischer Backfill-Batch.

### Owner fuer offene Risiken

1. User: Review der Quellklassifikation und Batch-Auswahl.
2. Codex: Inventar, Entity Notes, Dashboard, Backlog-Verknuepfung und Shell-Verifikation.

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Shell-/Plattformvertrag:

1. Zielplattform ist macOS.
2. Shell ist `zsh`.
3. `find`, `wc`, `tr` und `rg` sind verfuegbar.

Pflichtchecks fuer einen spaeteren Implementation-Slice:

1. `test -f _shared/SpecOps/Reference/spec-source-inventory.md`
2. `test -f _shared/SpecOps/Dashboards/backfill-coverage.md`
3. `rg -n 'narrative_spec|completed_narrative_spec|openspec_canonical_spec|openspec_change_artifact|plan_or_evidence_artifact' _shared/SpecOps/Reference/spec-source-inventory.md`
4. `rg -n '_specs/|/specs/|/Specs/|openspec/' _shared/SpecOps/Reference/spec-source-inventory.md`
5. `test "$(rg -l 'backfill_batch: historical-001' _shared/SpecOps/Entities/specs | wc -l | tr -d ' ')" -ge 5`
6. `test "$(rg -l 'backfill_batch: historical-001' _shared/SpecOps/Entities/specs | wc -l | tr -d ' ')" -le 10`
7. `test "$(find _shared/SpecOps/Entities/specs -type f -name '*.md' | wc -l | tr -d ' ')" -ge 10`
8. `rg -n 'backfill_batch: historical-001|source_type: narrative_spec|source_type: completed_narrative_spec|metadata_quality:' _shared/SpecOps/Entities/specs`
9. `rg -n 'FROM "_shared/SpecOps/Entities/specs"|backfill_batch|metadata_quality|source' _shared/SpecOps/Dashboards/backfill-coverage.md`
10. `rg -n 'Dashboards/backfill-coverage|Backfill Coverage' _shared/SpecOps/Dashboard.md`
11. `rg -n 'status: promoted|promoted_to: .+2026-05-05 SpecOps Full Historical Spec Backfill.md' _shared/SpecOps/Entities/backlog/full-historical-spec-backfill.md`
12. `rg -n 'source_type: openspec_change_artifact' _shared/SpecOps/Entities/specs`

Success Criteria:

1. Checks 1-11 geben Exit-Code `0` zurueck.
2. Checks 5 und 6 belegen direkt, dass der erste Backfill-Batch mindestens 5 und hoechstens 10 Spec-Entities enthaelt.
3. Check 12 ist ein negativer Guard und muss Exit-Code `1` liefern, weil OpenSpec Change Artifacts nicht als primaere Spec Entities backfilled werden duerfen.
4. Manuelles Review bestaetigt, dass das Inventar OpenSpec-Artefakte nicht mit User-/Narrative Specs verwechselt.

## Backlog Handling

1. Vor Erstellung dieser Child-Spec stand `full-historical-spec-backfill` auf `triaged`.
2. Nach Erstellung dieser Child-Spec steht `full-historical-spec-backfill` auf `promoted`.
3. Nach Umsetzung und erfolgreicher Verifikation darf das Backlog-Item auf `done` gesetzt werden, sofern der definierte erste Batch abgeschlossen ist.
4. Automatisierung bleibt in `automated-metadata-reconstruction`.

## Implementation Readiness

Diese Spec ist bereit fuer einen anschliessenden Scope-Contract-/Delivery-Run, wenn:

1. keine blockierenden MISSING- oder DECISION-Marker offen sind,
2. die Batch-Grenze 5-10 narrative Specs akzeptiert bleibt,
3. OpenSpec-Artefakte im ersten Slice nur inventarisiert oder verlinkt, aber nicht primaer dupliziert werden,
4. die Verification Commands als DoD-Basis akzeptiert werden.

Aktueller Stand: implementation-ready als Spec.

## Implementation Evidence

Umgesetzt am 2026-05-05 im Direct Mode ohne OpenSpec Change.

Closeout-Scope:

Diese Spec ist als `historical-001` Inventory- und erster Batch-Slice akzeptiert. Sie schliesst nicht den gesamten Full Historical Backfill ab. Die weitere Abarbeitung aller uebrigen Specs, Dokumente und OpenSpec-Beziehungen wird ueber eine separate Control Spec und daraus abgeleitete OpenSpec-Planung gesteuert.

Geaenderte Artefakte:

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/backfill-coverage.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/job-application-skill-2026-02-26.md`
5. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/ncg-readme-documentation-strategy-2026-03-01.md`
6. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/danielsvault-local-rag-wissensplattform-2026-04-13.md`
7. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/mittelstand-ki-startbahn-free-entry-v2-master-2026-05-04.md`
8. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/mittelstand-ki-startbahn-survey-delivery-answer-handoff-2026-05-05.md`

Batch `historical-001` enthaelt 5 Spec-Entities aus zwei Quellwurzeln und vier Projektkontexten:

1. `JobApplicationSkill`
2. `NCG Docs`
3. `DanielsVault RAG`
4. `Mittelstand KI Startbahn`

Verification vom 2026-05-05, Ausfuehrungskontext `/Users/dh/Documents/DanielsVault`, macOS/zsh:

| Check | Status | Evidence |
|---|---|---|
| 1 | ran-target | `spec-source-inventory.md` existiert. |
| 2 | ran-target | `backfill-coverage.md` existiert. |
| 3 | ran-target | Inventar enthaelt alle Klassifikationstokens. |
| 4 | ran-target | Inventar enthaelt `_specs/`, `/specs/`, `/Specs/` und `openspec/` Pfadsignale. |
| 5 | ran-target | `historical-001` hat mindestens 5 Entity Notes. |
| 6 | ran-target | `historical-001` hat hoechstens 10 Entity Notes. |
| 7 | ran-target | SpecOps hat mindestens 10 Spec-Entity-Dateien. |
| 8 | ran-target | Batch-Entities enthalten `backfill_batch`, `source_type` und `metadata_quality`. |
| 9 | ran-target | Coverage-Dashboard fragt Specs mit `backfill_batch`, `metadata_quality` und `source` ab. |
| 10 | ran-target | Root-Dashboard verlinkt `Dashboards/backfill-coverage`. |
| 11 | ran-target | Backlog-Item bleibt `promoted` und zeigt auf diese Child-Spec. |
| 12 | ran-target | Negativer Guard lieferte Exit-Code `1`; keine Spec-Entity nutzt `source_type: openspec_change_artifact`. |

Runtime-Validierung:

Nicht anwendbar. Dieser Slice aendert nur lokale Obsidian-Markdown-Artefakte in SpecOps und keine lauffaehige Anwendung, kein Docker-Compose-Target und keinen NCG-Backend-Buildpfad. `check-build-watcher` wurde deshalb nicht armiert.

Closeout vom 2026-05-05:

1. Alle 12 Verifikationskommandos wurden erneut ausgefuehrt.
2. Checks 1-11 lieferten Exit-Code `0`.
3. Check 12 lieferte als negativer Guard erwartungsgemaess Exit-Code `1`.
4. OpenSpec-Archivierung war nicht anwendbar, weil dieser Slice im Direct Mode ohne OpenSpec Change umgesetzt wurde.
5. RAG-gestuetzte Dokumentationssuche fuer den Closeout fand keine zusaetzliche Projektdokumentation, die fuer diesen SpecOps-Markdown-Slice synchronisiert werden musste; relevante Treffer waren bestehende Workflow-Skills, NCG-Beispielspecs oder bereits betroffene SpecOps-Artefakte.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | Full Historical Spec Backfill als naechste Child-Spec angefordert und Inventarisierung verschiedener Spec-Orte hervorgehoben. |
| 2026-05-05 | Codex | Child-Spec fuer Inventarisierung und kontrollierten historischen Spec-Backfill erstellt. |
| 2026-05-05 | User | Ziel als zu duenn markiert: Inventarisierung soll nur Teil des Slice sein, nicht dessen Ergebnis. |
| 2026-05-05 | Codex | Ziel, R3, Go/No-Go und Verification auf verpflichtenden ersten Backfill-Batch von 5-10 Specs geschaerft. |
| 2026-05-05 | Codex | Direct-Mode Scope Contract fixiert und Spec auf Plan gesetzt. |
| 2026-05-05 | Codex | Direct-Mode Umsetzung abgeschlossen, Verification Evidence erfasst und Spec auf Implemented gesetzt. |
| 2026-05-05 | User | Implementierten Inventory- und historical-001-Slice akzeptiert und Closeout angefordert. |
| 2026-05-05 | Codex | Closeout-Verifikation erneut ausgefuehrt, Scope-Abgrenzung ergaenzt und Spec auf Accepted gesetzt. |

SessionId: codex-desktop-current-thread
