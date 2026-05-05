**Date:** 2026-05-05
**Status:** 🟢 Accepted
**Scope:** SpecOps Document Entity Support Pilot fuer reale ADRs als `type: document` Entity Notes

---

## Kontext

Die SpecOps Parent-Spec definiert Dokumente und ADRs als eigene Entity-Klasse:

1. ADRs, Runbooks, Architekturuebersichten und andere Projektdokumente sind keine Specs.
2. Sie sollen nicht in Spec-Lifecycle-Spalten einsortiert werden.
3. Sie sollen als `type: document` gefuehrt werden, damit SpecOps sie mit Specs, Artefakten, Releases und Entscheidungen verknuepfen kann.

Das bestehende Backlog-Item `document-entity-support-for-adrs` ist dafuer bereits triaged. Der Trigger ist jetzt erfuellt, weil im Vault echte ADR-Quellen fuer `Mittelstand KI Startbahn` existieren:

`/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/adr/`

Aktuelle Pilotquellen:

1. `001-repo-access-and-ip-protection.md`
2. `002-starter-wizard-runner-technology-stack.md`
3. `003-survey-delivery-and-answer-handoff.md`

ADR-Discovery-Konvention: ADRs werden in ADR-Verzeichnissen gesucht. Fuer diesen Pilot ist der konkrete Ordner `docs/adr/` massgeblich; spaetere Discovery kann zusaetzlich Projektordner mit `.adr/`-Konvention beruecksichtigen.

Dieser Slice ist kein UX-Slice und ignoriert die parallel bearbeitete Spec `SpecOps Dashboard UX Overview`. Er promoted ausschliesslich das bestehende Backlog-Item `document-entity-support-for-adrs` mit `candidate_slice: SpecOps Entity Schema`.

## Ziel

SpecOps soll Dokumente sichtbar machen, ohne sie als Specs falsch zu klassifizieren.

Nach diesem Slice soll beantwortbar sein:

1. Welche relevanten Decision-/ADR-/Dokumentquellen sind als Dokument-Entities erfasst?
2. Zu welchem Projekt gehoeren sie?
3. Welche Specs oder Artefakte haengen daran?
4. Welche Dokument-Metadaten sind explizit, rekonstruiert oder fehlen noch?
5. Bleiben Dokumente aus Spec-Lifecycle-Boards heraus und werden stattdessen ueber eigene Dokument-/Trace-Sichten sichtbar?

## In Scope

1. Nutzung des bestehenden Entity-Typs `type: document`.
2. Mindestens eine reale Document Entity unter `_shared/SpecOps/Entities/documents/`.
3. Pilotquelle:
   - `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/adr/`
4. Drei reale ADR-Dateien aus der Pilotquelle werden als Document Entities erfasst.
5. Falls `Mittelstand KI Startbahn` noch nicht in SpecOps-Projekt-Taxonomie und Project Entities existiert, darf dieser Slice genau diesen Projekt-Eintrag minimal ergaenzen.
6. Ein Dokument-Dashboard unter `_shared/SpecOps/Dashboards/`, das `type: document` Entities zeigt.
7. Root-Dashboard-Verweis auf die Dokument-Sicht.
8. Backlog-Item `document-entity-support-for-adrs` mit dieser Child-Spec verknuepfen.
9. Defensive Metadatenqualitaet:
   - `metadata_quality: explicit`, wenn Status/Projekt/Quelle klar aus der Quelle oder bestehenden SpecOps-Feldern ableitbar sind.
   - `metadata_quality: inferred`, wenn Projekt- oder Statuszuordnung rekonstruiert wird.
   - `metadata_quality: missing` oder `conflict`, wenn Zuordnung nicht belastbar ist.

## Out of Scope

1. Kein Full Historical Document Backfill.
2. Keine Migration aller ADRs, Runbooks, Evidence-Dateien oder Architekturdocs.
3. Keine Aenderung am Spec-Lifecycle.
4. Keine Release-Entity-Implementierung.
5. Keine Environment-Tracking-Semantik.
6. Keine Skill-/Agent-/RAG-Learning-Integration.
7. Keine Dashboard-UX-Umgestaltung; die parallel bearbeitete UX-Spec bleibt ausserhalb dieses Slices.
8. Keine neuen Pflichtfelder fuer alle bestehenden Entities.

## Requirements

### R1 - Document Entity Model

Dokumente muessen als `type: document` Entity Notes modelliert werden, nicht als Specs.

Akzeptanzkriterien:

1. Eine Document Entity hat mindestens `type`, `id`, `title`, `project`, `status`, `source`, `doc_type` und `metadata_quality`.
2. `doc_type` unterscheidet mindestens `adr`, `decision`, `runbook`, `architecture`, `guide` oder `evidence`.
3. `decision_status` darf fuer ADRs und Decision Docs gesetzt werden.
4. `related_specs` und `related_artifacts` duerfen leer sein, muessen aber als Felder nutzbar bleiben.

### R2 - Real ADR Document Pilot

Der Slice muss die drei realen ADRs aus `ki-fuer-kmu/v2/docs/adr/` als Document Entities erfassen.

Akzeptanzkriterien:

1. `001-repo-access-and-ip-protection.md` wird als `type: document` Entity erfasst.
2. `002-starter-wizard-runner-technology-stack.md` wird als `type: document` Entity erfasst.
3. `003-survey-delivery-and-answer-handoff.md` wird als `type: document` Entity erfasst.
4. Alle drei Entities verwenden `doc_type: adr`.
5. Alle drei Entities verwenden `decision_status: accepted`, weil die Quellen `Status: Angenommen` enthalten.
6. Alle drei Entities verlinken auf die reale Quelle mit absolutem lokalem Pfad.
7. Projektzuordnung und Metadata Quality sind nachvollziehbar dokumentiert.

### R2a - Project Taxonomy Fit

Die ADRs muessen einem SpecOps-Projekt zugeordnet werden koennen.

Akzeptanzkriterien:

1. Wenn `Mittelstand KI Startbahn` noch nicht als kontrollierter Projektname existiert, wird dieser Projektname in `Reference/project-taxonomy.md` ergaenzt.
2. Wenn noch keine Project Entity existiert, wird `_shared/SpecOps/Entities/projects/mittelstand-ki-startbahn.md` angelegt.
3. Die drei ADR-Entities verwenden exakt denselben Projektwert.

### R3 - Document Dashboard

SpecOps muss Dokument-Entities sichtbar machen, ohne sie in Spec-Boards zu vermischen.

Akzeptanzkriterien:

1. Ein Dashboard unter `_shared/SpecOps/Dashboards/documents.md` zeigt Document Entities.
2. Die View zeigt mindestens `doc_type`, `project`, `status`, `decision_status`, `metadata_quality`, `source`, `related_specs` und `related_artifacts`.
3. Das Root-Dashboard verlinkt oder embedded die Dokument-Sicht.
4. Projektboards duerfen spaeter Dokument-Sichten referenzieren, aber dieser Slice muss keine Projektboard-Umgestaltung leisten.

### R4 - Backlog Discipline

Der Slice bleibt an das bestehende Backlog-Item gebunden.

Akzeptanzkriterien:

1. `document-entity-support-for-adrs` ist mit dieser Spec verlinkt.
2. Neue Out-of-Scope-Dokumentthemen werden als Backlog sichtbar gemacht oder explizit nicht umgesetzt dokumentiert.
3. Keine neue Slice-Bezeichnung wird eingefuehrt, wenn sie nicht aus `title` oder `candidate_slice` eines Backlog-Items stammt.

## Decision Freeze Pack

### Zielbild und Scope

Dieser Slice fuehrt einen minimalen Document-Entity-Pilot ein. Er bestaetigt, dass SpecOps Entscheidungen und Dokumente verfolgen kann, ohne den Spec-Lifecycle zu verfaelschen.

### Betroffene Vault-Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/documents/`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/projects/`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/project-taxonomy.md`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/`
5. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
6. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/document-entity-support-for-adrs.md`
7. Diese Child-Spec unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/`

### Secret-/Config-Contract

Keine Secrets. Alle Quellen bleiben lokal im DanielsVault.

### Datenmigration/Fallback

Keine Big-Bang-Migration. Nur die drei ADRs aus der Pilotquelle werden als Document Entities erfasst. Weitere Dokumentquellen bleiben Backlog oder spaetere Slices.

### Externe Integrationen

Keine externen Integrationen.

### Sicherheits-/Exposure-Entscheidungen

Alle Daten bleiben lokal im Vault. Es wird nichts publiziert oder synchronisiert.

### Abnahmekriterien Go/No-Go

Go:

1. Drei ADR Document Entities existieren.
2. Alle drei ADRs aus `ki-fuer-kmu/v2/docs/adr/` sind als Document Entities erfasst.
3. `Mittelstand KI Startbahn` ist als Projektwert verwendbar.
4. Document Dashboard existiert und nutzt Dataview.
5. Root-Dashboard referenziert die Document View.
6. Backlog-Item `document-entity-support-for-adrs` ist mit dieser Spec verlinkt.
7. Keine Document Entity wird als `type: spec` modelliert.

No-Go:

1. Dokumente werden in Spec Lifecycle Boards einsortiert.
2. Der Slice startet einen historischen Dokument-Backfill.
3. Release-, Environment- oder Learning-Modelle werden nebenbei veraendert.
4. Die parallel bearbeitete UX-Spec wird beruehrt.

### Owner fuer offene Risiken

1. User: Review, ob die drei Mittelstand-KI-Startbahn-ADRs als Pilotquelle passen.
2. Codex: Entity Note, Dashboard, Backlog-Verknuepfung und Shell-Verifikation.

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Shell-/Plattformvertrag:

1. Zielplattform ist macOS.
2. Shell ist `zsh`.
3. `rg` ist installiert und wird fuer Textchecks verwendet.

Pflichtchecks fuer einen spaeteren Implementation-Slice:

1. `test -f _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-001-repo-access-and-ip-protection.md`
2. `test -f _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-002-starter-wizard-runner-technology-stack.md`
3. `test -f _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-003-survey-delivery-and-answer-handoff.md`
4. `test -f _shared/SpecOps/Entities/projects/mittelstand-ki-startbahn.md`
5. `test -f _shared/SpecOps/Dashboards/documents.md`
6. `rg -n 'Mittelstand KI Startbahn' _shared/SpecOps/Reference/project-taxonomy.md _shared/SpecOps/Entities/projects/mittelstand-ki-startbahn.md`
7. `rg -n 'type: document|doc_type: adr|decision_status: accepted|metadata_quality: explicit' _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-001-repo-access-and-ip-protection.md _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-002-starter-wizard-runner-technology-stack.md _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-003-survey-delivery-and-answer-handoff.md`
8. `rg -n '001-repo-access-and-ip-protection.md|002-starter-wizard-runner-technology-stack.md|003-survey-delivery-and-answer-handoff.md' _shared/SpecOps/Entities/documents`
9. `rg -n 'FROM "_shared/SpecOps/Entities/documents"|doc_type|decision_status|related_specs|related_artifacts' _shared/SpecOps/Dashboards/documents.md`
10. `rg -n 'Dashboards/documents|Documents|Document' _shared/SpecOps/Dashboard.md`
11. `rg -n 'status: done|promoted_to: .+2026-05-05 SpecOps Document Entity Support for ADRs.md' _shared/SpecOps/Entities/backlog/document-entity-support-for-adrs.md`
12. `rg -n 'type: spec' _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-001-repo-access-and-ip-protection.md _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-002-starter-wizard-runner-technology-stack.md _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-003-survey-delivery-and-answer-handoff.md`

Success Criteria:

1. Checks 1-11 geben Exit-Code `0` zurueck.
2. Check 12 ist ein negativer Guard und muss Exit-Code `1` liefern.
3. Manuelles Obsidian-/Dataview-Review bestaetigt, dass die Document View sichtbar ist.

## Backlog Handling

1. Vor Erstellung dieser Child-Spec stand `document-entity-support-for-adrs` auf `triaged`.
2. Nach Erstellung dieser Child-Spec steht `document-entity-support-for-adrs` auf `promoted`.
3. Nach Umsetzung und erfolgreicher Verifikation darf das Backlog-Item auf `done` gesetzt werden.

## Implementation Readiness

Diese Spec ist bereit fuer einen anschliessenden Scope-Contract-/Delivery-Run, wenn:

1. der User die Pilotquelle `ki-fuer-kmu/v2/docs/adr/` akzeptiert,
2. keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker offen sind,
3. die Verification Commands als DoD-Basis akzeptiert werden.

Aktueller Stand: umgesetzt und mit den Pflichtchecks verifiziert.

## Implementation Evidence

Target runtime: lokaler DanielsVault unter `/Users/dh/Documents/DanielsVault`.

Execution mode: direct, ohne OpenSpec Change.

Changed files:

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-001-repo-access-and-ip-protection.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-002-starter-wizard-runner-technology-stack.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-003-survey-delivery-and-answer-handoff.md`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/projects/mittelstand-ki-startbahn.md`
5. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/project-taxonomy.md`
6. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/documents.md`
7. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
8. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Document Entity Support for ADRs.md`

Runtime / watcher applicability:

1. Keine Runtime-Validierung mit `docker compose` erforderlich, weil dieser Slice ausschliesslich Markdown-/Dataview-Entity-Dateien aendert.
2. `check-build-watcher` ist fuer NCG-Backend-Build-Monitoring nicht anwendbar, weil kein NCG-Backend-Code, keine Pipeline und kein Build-Artefakt in Scope sind.
3. Obsidian-/Dataview-Renderpruefung bleibt gemaess Spec ein manuelles Review-Signal.

| Check | Status | Evidence |
|-------|--------|----------|
| 1. ADR-001 entity exists | ran-target | `test -f _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-001-repo-access-and-ip-protection.md` returned exit code `0`. |
| 2. ADR-002 entity exists | ran-target | `test -f _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-002-starter-wizard-runner-technology-stack.md` returned exit code `0`. |
| 3. ADR-003 entity exists | ran-target | `test -f _shared/SpecOps/Entities/documents/mittelstand-ki-startbahn-adr-003-survey-delivery-and-answer-handoff.md` returned exit code `0`. |
| 4. Project entity exists | ran-target | `test -f _shared/SpecOps/Entities/projects/mittelstand-ki-startbahn.md` returned exit code `0`. |
| 5. Documents dashboard exists | ran-target | `test -f _shared/SpecOps/Dashboards/documents.md` returned exit code `0`. |
| 6. Project taxonomy/entity contains project | ran-target | `rg -n 'Mittelstand KI Startbahn' _shared/SpecOps/Reference/project-taxonomy.md _shared/SpecOps/Entities/projects/mittelstand-ki-startbahn.md` found expected markers. |
| 7. ADR document fields exist | ran-target | `rg -n 'type: document\|doc_type: adr\|decision_status: accepted\|metadata_quality: explicit' ...` found expected fields across all three document entities. |
| 8. ADR source filenames linked | ran-target | `rg -n '001-repo-access-and-ip-protection.md\|002-starter-wizard-runner-technology-stack.md\|003-survey-delivery-and-answer-handoff.md' _shared/SpecOps/Entities/documents` found all three source links. |
| 9. Documents dashboard fields exist | ran-target | `rg -n 'FROM "_shared/SpecOps/Entities/documents"\|doc_type\|decision_status\|related_specs\|related_artifacts' _shared/SpecOps/Dashboards/documents.md` found expected query fields. |
| 10. Root dashboard links Documents | ran-target | `rg -n 'Dashboards/documents\|Documents\|Document' _shared/SpecOps/Dashboard.md` found the Documents section and embed. |
| 11. Backlog item closed as done and linked | ran-target | `rg -n 'status: done\|promoted_to: .+2026-05-05 SpecOps Document Entity Support for ADRs.md' _shared/SpecOps/Entities/backlog/document-entity-support-for-adrs.md` found expected markers. |
| 12. Documents are not specs | ran-target | `rg -n 'type: spec' ...` returned expected exit code `1`. |

Verdict: READY for Obsidian review.

## Closeout Evidence

Closeout date: 2026-05-05.

OpenSpec closure: not applicable; this change used Direct Mode without an OpenSpec change.

Documentation synchronization:

1. RAG source discovery ran successfully with `rag workflow spec-closeout --scope all --change "SpecOps Document Entity Support for ADRs" --top-k 7 --format json`.
2. RAG recommendations were generic NCG/documentation workflow references, not SpecOps-specific normative docs requiring update.
3. Local exact search found the stale `document-entity-support-for-adrs` row in the RAG Project Board Pilot backlog table; that table was synchronized.
4. The parallel `SpecOps Dashboard UX Overview` remained untouched.

Closeout verification replay:

1. All positive required checks returned exit code `0`.
2. Negative guard check 12 returned expected exit code `1`.
3. The `document-entity-support-for-adrs` backlog entity is closed as `done`.

Verdict: READY.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | UX-Spec als parallel bearbeitet markiert und anderen Backlog-/Hauptspec-Slice angefordert. |
| 2026-05-05 | Codex | Child-Spec fuer `document-entity-support-for-adrs` / `SpecOps Entity Schema` erstellt. |
| 2026-05-05 | User | Mittelstand-KI-Startbahn ADR-Ordner als bessere Pilotquelle benannt. |
| 2026-05-05 | Codex | Spec auf drei reale Mittelstand-KI-Startbahn ADRs umgestellt und Pilotquellen-Entscheidung geschlossen. |
| 2026-05-05 | Codex | Direct-Mode Scope Contract fixiert und Spec-Status auf Plan gesetzt. |
| 2026-05-05 | Codex | Document Entity Support direkt umgesetzt, verifiziert und Spec-Status auf Implemented gesetzt. |
| 2026-05-05 | User | Implementierten Change akzeptiert. |
| 2026-05-05 | Codex | Closeout-Verifikation replayed, Backlog/Doku synchronisiert und Spec-Status auf Accepted gesetzt. |

SessionId: codex-desktop-current-thread
