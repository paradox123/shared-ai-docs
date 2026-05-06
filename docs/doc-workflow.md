# Documentation & Planning Workflow

Dieser Workflow erweitert die bestehende Skill-Pipeline um klare Planungs- und Verifikations-Gates, um Nacharbeiten zu reduzieren.

## Ziel

1. Anforderungen sauber erfassen.
2. Entscheidungen vor Umsetzung einfrieren.
3. Umsetzung nur mit überprüfbaren Gates starten.
4. Abweichungen und Learnings systematisch in Skills/Workflow zurückführen.

## Shared Gate Source of Truth

Dieses Dokument ist die **kanonische Quelle** für die gemeinsamen Delivery-Gates in:
- `doc-coauthoring`
- `spec-orchestrator`
- `child-spec-hardening`
- `refine-plan`
- `spec-change-delivery`
- `spec-closeout`
- `doc-review-autoresolve`
- `retro-plan`

Hier werden die gemeinsamen Begriffe gepflegt:
- **Definition of Ready (DoR)**
- **Definition of Done (DoD)**
- **Decision Freeze Pack**
- **Session Briefing**
- **Review Control Surface**
- **Mini-Retro**

Die Skills dürfen diese Begriffe lokal kurz restaten, sollen aber **keine abweichenden Definitionen** einführen. Änderungen an der gemeinsamen Bedeutung werden zuerst hier gepflegt.

## Session Briefing Template (kurz)

Bei groesseren Arbeiten, neuen Sessions, Kontextkomprimierung oder Skill-Wechsel zuerst ein kurzes Briefing herstellen. Es darf aus dem vorhandenen Kontext abgeleitet werden; nur blockierende Luecken werden zurueckgefragt.

```md
## Session Briefing

- Modus/Skill:
- Source of Truth:
- Ziel:
- Nicht-Ziele:
- In Scope:
- Erwarteter Output:
- Verification/Review:
- Offene Entscheidungen:
```

Regeln:
1. `Modus/Skill` benennt den aktiven Workflow-Schritt, z. B. `doc-coauthoring`, `spec-orchestrator`, `child-spec-hardening`, `doc-review-autoresolve` oder `spec-change-delivery`.
2. `Source of Truth` nennt die fuehrenden Dateien/Specs/Artefakte; keine Hybrid-Steuerung ohne explizite Entscheidung.
3. `Ziel`, `Nicht-Ziele`, `In Scope` und `Erwarteter Output` muessen vor groesseren Edits oder Implementierung klar sein.
4. Ausgeschlossene Themen werden als Nicht-Ziele sichtbar gehalten, damit sie nicht nebenbei in den Scope rutschen.
5. Bei Review-/Spec-Arbeit wird zusaetzlich die `Review Control Surface` der betroffenen Spec geprueft oder angelegt.

## Mini-Retro Template (kurz)

Eine Mini-Retro ist ein leichtgewichtiges Kontrollritual gegen Kontextverlust und Rework. Sie ersetzt keine vollstaendige `retro-plan`-Analyse, sondern haelt den aktuellen Stand fest, bevor ein groesserer Arbeitsblock endet oder der naechste Schritt startet.

```md
## Mini-Retro

- Was wurde entschieden?
- Was wurde geaendert?
- Was bleibt offen?
- Welche Evidenz/Verification fehlt?
- Welche Skill-/Workflow-Reibung ist aufgefallen?
- Session-/Kontextzustand: weiterarbeiten oder neue Session starten?
```

Regeln:
1. Eine Mini-Retro entsteht nach groesseren Spec-, Review-, Hardening-, Delivery- oder Closeout-Schritten, wenn sonst relevanter Kontext verloren gehen koennte.
2. Eine Mini-Retro entsteht vor Session-Ende, Kontextkomprimierung, laengerem Pausieren, Handoff an einen anderen Skill oder Start des naechsten groesseren Workflow-Schritts.
3. Sie bleibt kurz: Stichpunkte reichen, keine Ursachenanalyse erzwingen, keine neue Methodik starten.
4. Offene Entscheidungen, fehlende Evidenz, Workflow-Reibung und Kontextqualitaet muessen sichtbar bleiben, damit sie im naechsten Schritt nicht neu entdeckt werden.
5. Wenn die Mini-Retro echte Planungsfehler, wiederkehrende Rework-Muster oder Skill-Luecken zeigt, kann daraus eine vollstaendige `retro-plan`-Retro oder ein `improve-skills`-Kandidat werden.

## Unterstützte Workflows

Beide Workflows sind offiziell unterstützt. Workflow 2 ist der aktuelle Default, Workflow 1 bleibt kompatibel nutzbar.

### Workflow 1 (Legacy-kompatibel)

```
Spec (`🟡 Spec`)
  v
refine-plan (iterativ, plan history)
  v
direct-mode implementation
  v
retro-plan (optional)
```

### Workflow 2 (Current)

```
Spec (`🟡 Spec`)
  v
spec-change-delivery (direct oder OpenSpec) -> Scope Contract (`🟠 Plan`)
  v
Implementierung + Verifikation (`🔵 Implemented`)
  v
retro-plan (optional)
  v
spec-closeout (optional, für formalen Abschluss) (`🟢 Accepted`)
```

### Large Spec / Child Spec Pipeline

For Parent-/Master-Specs with multiple delivery slices:

```md
doc-coauthoring -> Parent Spec (`🟡 Spec`)
  v
spec-orchestrator -> Child Schnitt, Coverage, Hardening Queue
  v
child-spec-hardening -> implementation-ready Child Spec
  v
doc-review-autoresolve -> autonomous cleanup + readiness verdict
  v
spec-change-delivery -> one child implementation (`🟠 Plan` -> `🔵 Implemented`)
```

`spec-orchestrator` and `child-spec-hardening` normally keep specs in `🟡 Spec`; `spec-change-delivery` owns the transition to `🟠 Plan` once the implementation scope contract is locked.

## Workflow Selection (ohne Zwangsumstellung)

1. Wenn der User explizit Workflow 1 oder Workflow 2 nennt, diesem Pfad folgen.
2. Wenn ein bestehendes Artefakt bereits klar einen Pfad nutzt, auf demselben Pfad bleiben.
3. Ohne klare Vorgabe:
   - für neue Deliveries Workflow 2 bevorzugen,
   - für laufende ältere Threads Workflow 1 beibehalten.
4. Ein Wechsel ist nur bei expliziter User-Entscheidung sinnvoll.

## Spec Header Contract (verpflichtend)

Jede Spec muss mit diesem Header starten:

```md
**Date:** 2026-03-03  
**Status:** 🟡 Spec
**Scope:** Automated deployment validation and self-healing for NCG backend on Hetzner infrastructure

---
```

Regeln:
1. `Date` im Format `YYYY-MM-DD` (Erstellungsdatum der Spec).
2. `Scope` als prägnanter Einzeiler.
3. `Status` nur aus dieser Liste:
   - `🟡 Spec` - Spec wird erstellt/verfeinert (`doc-coauthoring`)
   - `🟠 Plan` - umsetzbarer Plan existiert (aus `refine-plan` oder `spec-change-delivery`)
   - `🔵 Implemented` - Umsetzung plus Artefakte/Evidenz liegt vor
   - `🟢 Accepted` - formaler Abschluss erfolgt (typisch via `spec-closeout`)

## Review Control Surface (verpflichtend fuer Specs)

Jede Spec, Parent Spec und Child Spec muss direkt nach Header/Einleitung eine kurze Kontrollflaeche haben, die ein schnelles Review ermoeglicht. Sie ersetzt keine Detailsektionen, sondern spiegelt deren wichtigste Aussagen.

```md
## Review Control Surface

- Ziel:
- In Scope:
- Out of Scope:
- Wichtigste Test-/Harness-Cases:
- Wichtigste Verification Commands:
- Offene Entscheidungen:
- Readiness Status:
```

Regeln:
1. `Ziel` beschreibt die konkrete Verhaltens- oder Dokumentationsaenderung, nicht nur den Projektnamen.
2. `In Scope` und `Out of Scope` muessen die Delivery-Grenze ohne Detaillekture verstaendlich machen.
3. Test-/Harness-Cases und Verification Commands listen die wichtigsten Proof Points, inklusive Negativ-, Fehler- oder Secret-/Redaction-Cases, wenn relevant.
4. `Offene Entscheidungen` nennt blockierende `[MISSING ...]`, `[DECISION ...]` oder blockierende `[REVIEW ...]` Marker; wenn keine offen sind, explizit `Keine blockierenden Entscheidungen`.
5. `Readiness Status` verwendet das passende Skill-Verdict, z. B. `NOT READY`, `READY FOR ORCHESTRATION`, `READY FOR PLANNING`, `IMPLEMENTATION READY`, `READY WITH NON-BLOCKING NOTES`, `NEEDS USER DECISION`, `NEEDS PARENT/ORCHESTRATOR SYNC` oder `NEEDS HARDENING`.
6. Wenn Detailsektionen geaendert werden, muss die Kontrollflaeche mitgezogen werden. Widerspruch zwischen Kontrollflaeche und Detailvertrag ist ein blockierendes Review-Finding.

## Status Ownership by Workflow

1. In beiden Workflows:
   - `doc-coauthoring` erstellt Header (falls fehlend) und setzt `🟡 Spec`.
2. Workflow 1:
   - `refine-plan` kann auf `🟠 Plan` setzen, sobald ein umsetzbarer Plan vorliegt.
   - der ausführende Implementierungs-Run (direct mode) setzt auf `🔵 Implemented`, sobald Evidenz vorliegt.
   - `spec-closeout` ist optional; bei erfolgreichem formalem Abschluss wird `🟢 Accepted` gesetzt.
3. Workflow 2:
   - `spec-change-delivery` setzt auf `🟠 Plan` (Scope Contract fixiert) und später auf `🔵 Implemented` (Umsetzung + Evidenz).
   - `spec-closeout` setzt auf `🟢 Accepted`, wenn Verifikation/Closeout vollständig erfolgreich sind.

## Skills und Verantwortung

### `doc-coauthoring`

Purpose: Anforderungen, Scope, Constraints, Akzeptanzkriterien.

Lieferobjekt:
- belastbare Spec mit `[MISSING ...]`, `[DECISION ...]`, `[REVIEW ...]`
- klare Non-Goals
- Review Control Surface mit Ziel, Scope, Non-Goals, wichtigsten Cases/Commands, offenen Entscheidungen und Readiness

### `rag-documentation-research`

Purpose: Quellenorientierte Dokumentationssuche vor Plan/Umsetzung mit `rag` als Standard und optionalem `qmd`-Discovery-Zusatz.

Lieferobjekt:
- priorisierte Quellenpfade fuer die aktuelle Frage
- nachvollziehbare Trefferbegruendung pro Quelle
- explizite Kennzeichnung, ob Treffer aus `rag`, `qmd` oder kombiniert stammen

Trigger (beispielhaft):
- "durchsuche die dokumentation"
- "durchsuche docs"
- "research the documentation"
- "search the documentation"
- "find relevant docs"
- "welche dokumente sind relevant"

Routing-Regel:
- Bei solchen Suchanfragen zuerst `rag-documentation-research`, danach mit den Quellen im jeweiligen Workflow (`doc-coauthoring`, `refine-plan`, `spec-change-delivery`, `spec-closeout`) fortfahren.

### `refine-plan`

Purpose: Aus Spec einen ausführbaren Plan machen.

Lieferobjekt:
- status-bearing actions (`[DONE]`, `[PENDING]`, `[BLOCKED]`)
- konkrete Verification Cases pro Teilbereich
- offene Spec-Lücken explizit als `[MISSING SPEC ...]`/`[DECISION SPEC ...]`
- primärer Plan-Track für Workflow 1 (iterativ)

### `spec-orchestrator`

Purpose: Große Parent-/Master-Specs schneller in Child-Delivery-Packs, Coverage-Kontrolle und Hardening Queue übersetzen.

Lieferobjekt:
- Parent-/Child-Inventar und Coverage-Matrix
- Review Control Surface fuer Parent/Child-Set oder fehlende Control-Surface-Patches
- Child-Readiness-Matrix mit fehlenden Delivery-Pack-/Hardening-Bestandteilen
- Parallelisierungs-/Lane-Matrix mit Write-Sets und Integrations-Owner
- empfohlene nächste Slices plus Closeout-Sync-Checkliste
- Hardening Queue fuer Child Specs, die noch nicht implementation-ready sind

Routing-Regel:
- Nach `doc-coauthoring` nutzen, sobald ein Parent-Draft, eine Master-Spec, ein Slice-Plan oder Child Specs existieren und mehrere Slices orchestriert werden muessen.
- Vor `child-spec-hardening` nutzen, wenn mehrere Child Specs, ein großer Parent-Scope oder die Frage nach Parallelisierung/Nächstem Slice im Raum steht.
- Nicht als ersten Schritt fuer einen leeren Initialprompt nutzen; dafuer bleibt `doc-coauthoring` der Startpunkt.
- Nicht versuchen, alle Child Specs selbst bis zur vollen Vertragstiefe auszuarbeiten; dafuer `child-spec-hardening` nutzen.

### `child-spec-hardening`

Purpose: Aus Child-Spec-Drafts oder Orchestrator-Hardening-Queue-Eintraegen implementierungsreife Delivery Specs herstellen.

Lieferobjekt:
- aktualisierte Review Control Surface im Child
- Parent-/Master-Coverage und Parent-Scope-Conformance je Child
- Normative Contract mit Feldern, Statuswerten, Artefakten, Fehlerfaellen, Security-/Redaction-Regeln und Beispielen/Fixtures, soweit fuer den Child-Scope relevant
- konkrete Harness-/Verification-Cases mit Inputs, erwarteten Exit-/Statuswerten, Artefakten und Negativ-/Secret-Assertions
- Verification Commands im Stil akzeptierter Vorgaenger-Slices inklusive Execution Context, Preflight, Gate Verification, Runtime-Readiness und Anti-Loop-Regel
- Definition of Ready fuer Umsetzung und Definition of Done/Closeout Evidence
- Auto-Resolve-/Content-Quality-Review-Loop mit finalem Readiness Verdict

Routing-Regel:
- Nach `spec-orchestrator` nutzen, wenn ein Child `needs_hardening`, `ready_candidate` oder eine Hardening Queue hat.
- Direkt nutzen, wenn ein einzelner Child-Spec-Draft existiert und implementation-ready gemacht werden soll.
- Intern die Schreibprinzipien von `doc-coauthoring` und den Review-/Fix-Zyklus von `doc-review-autoresolve` anwenden.
- Stoppen, wenn echte Produkt-, Scope-, Architektur-, Security-, Legal- oder Data-Contract-Entscheidungen fehlen.
- Erst nach `IMPLEMENTATION READY` an `spec-change-delivery` uebergeben.

### `spec-change-delivery`

Purpose: Einen klar abgegrenzten Change aus der Spec implementieren und verifizieren.

Lieferobjekt:
- Scope Contract (direct oder OpenSpec)
- umgesetzte Artefakte + Verifikationsnachweise
- primärer Delivery-Track für Workflow 2 inkl. Spec-Statusupdate auf `🟠 Plan` und später `🔵 Implemented`

### `spec-closeout`

Purpose: Akzeptierten Change formal abschließen und dokumentarisch synchronisieren.

Lieferobjekt:
- vollständiger Verifikations-Checklist-Report
- OpenSpec Close/Archivierung (falls genutzt)
- Spec-Statusupdate auf `🟢 Accepted`
- RAG-basierte Quellensuche fuer relevante Doku-Updates (RAG-first, `qmd` optional)

### `doc-review-autoresolve`

Purpose: Review-Findings in Specs/Dokus autonom auflösen und direkt gegenprüfen, um Rework-Schleifen zu verkürzen.

Lieferobjekt:
- Findings-first Review mit file/line Referenzen
- automatische Behebung aller sicher entscheidbaren Inkonsistenzen im selben Run
- unmittelbarer Re-Review nach Edits (Loop bis stabil)
- Kontrolle, dass die Review Control Surface mit Detailsektionen, Findings und Readiness-Verdict konsistent ist
- strenger inhaltlicher Review des gesamten Vorhabens: Korrektheit, Scope, Vollstaendigkeit, Konsistenz, Eindeutigkeit, Machbarkeit, Testbarkeit, Traceability, Abstraktionsniveau, operative/lifecycle-relevante Punkte sowie Daten-/Artefaktvertraege
- automatischer Readiness-Status nach Spec-Änderungen (`IMPLEMENTATION READY`, `READY WITH NON-BLOCKING NOTES`, `NOT IMPLEMENTATION READY`)
- Eskalation nur für echte Entscheidungs-/Informationslücken (`[MISSING ...]`, `[DECISION ...]`, blockierende `[REVIEW ...]`)

Zusammenspiel mit `doc-coauthoring`:
- `doc-coauthoring` erstellt und ergänzt Inhalte, Anforderungen, Testfälle und Verification Commands.
- `doc-review-autoresolve` darf direkt danach laufen, um Inkonsistenzen, Drift, Dopplungen, fehlende Querverweise und sicher inferierbare Vertragslücken zu bereinigen.
- `doc-review-autoresolve` trifft keine neuen Produkt-/Scope-/Architektur-/Security-/Legal-/Data-Contract-Entscheidungen. Bei solchen Lücken stoppt der Loop mit Entscheidungsmarker.

### `retro-plan`

Purpose: Ergebnis gegen Plan prüfen und Deltas erfassen.

Lieferobjekt:
- Mini-Retro nach groesseren Arbeitsbloecken oder vor Kontextwechseln
- Root-Cause-Analyse
- Follow-up-Deltas für Spec/Plan/Umsetzung

### `improve-skills`

Purpose: wiederkehrende Reibungsmuster identifizieren und dauerhaft reduzieren.

Im Kontext dieses Workflows:
- wiederholte Nacharbeiten klassifizieren
- fehlende/unklare Entscheidungspunkte dokumentieren
- Workflow-/Skill-Anpassungen ableiten

## OpenSpec Nutzung (optional)

OpenSpec ist **optional** und wird **vom User entschieden**.

OpenSpec ist typischerweise hilfreich bei:

1. größeren oder mehrstufigen Vorhaben,
2. mehreren beteiligten Teams/Repos,
3. Bedarf nach formalen Artefakten und Audit-Trace,
4. länger laufenden Changes mit Blockern und Teilfortschritt.

Für kleinere oder klar abgegrenzte Änderungen reicht oft der direkte Plan-Track ohne OpenSpec.

## Parent-/Child-Spec Orchestrierung

Wenn eine Spec wegen Scope-Druck in Child Specs aufgeteilt wird, muss die Parent Spec als Kontrollschicht erhalten bleiben. Child Specs duerfen den Scope nur schneiden, nicht verschwinden lassen.

Pflichtbestandteile:

1. Parent Spec oder Slice-Plan mit Coverage-Matrix: jede Parent-Anforderung ist `done`, `partial`, `pending`, `blocked` oder bewusst `out_of_scope`.
2. Child-Spec-Index mit Status, Abhaengigkeiten, naechstem empfohlenem Slice und Link auf Evidence/Closeout.
3. Jede Child Spec enthaelt vor Umsetzung mindestens eine Review Control Surface, Scope, Non-Goals, Master-/Parent-Abdeckung, Parent-Scope-Conformance, Decision Freeze Pack, konkrete Acceptance Criteria und Verification Commands.
4. Restscope wird nicht nur als "Next Step" in einer abgeschlossenen Spec abgelegt, sondern als Backlog-/Child-Spec-Eintrag mit Trigger, Done-Signal und Abhaengigkeit.
5. Closeout einer Child Spec synchronisiert Parent Spec, Slice-Plan/Index, Backlog und OpenSpec-Artefakte, bevor der naechste Slice als fuehrend gilt.

Parent-Scope-Conformance ist ein blockierendes Gate nach jeder Child-Spec-Nacharbeit:

1. Jede Parent-Anforderung, die der Child beruehrt, wird als `preserves`, `extends`, `narrows_with_rationale`, `defers_to_child`, `missing_from_child` oder `contradicts_parent` markiert.
2. `contradicts_parent` blockiert Implementierung.
3. `missing_from_child` blockiert Implementierung, wenn kein benannter Child-/Backlog-Reentry existiert.
4. Bewusste Scope-Verengung ist erlaubt, aber nur mit Rationale und Ziel fuer den Restscope.

Parallelisierung ist nur sinnvoll, wenn Child Specs unabhaengige Write-Sets und verifizierbare Done-Signale haben.

Parallel-Lane-Regeln:

1. Vor Start eine Lane-Matrix erstellen: Child Spec, Owner/Agent, erlaubte Dateien/Module, verbotene Shared Files, Abhaengigkeiten, Verification Commands.
2. Shared Control Files wie Parent Spec, Slice-Plan, Index, Backlog oder gemeinsame Helpers haben genau einen Integrations-Owner.
3. Parallel arbeitende Child Specs laufen in getrennten Branches/Worktrees oder klar getrennten OpenSpec Changes.
4. Kein paralleler Change darf denselben zentralen Contract still veraendern; Contract-Aenderungen laufen zuerst als eigener kleiner Slice.
5. Nach Rueckkehr aller Lanes fuehrt der Integrations-Owner Merge, Cross-Slice-Review, Parent-Coverage-Update und die gemeinsame Verification-Replay aus.

## Child-Spec-Hardening Pipeline

Die Zerlegung und die Tiefe sind getrennte Verantwortungen:

1. `doc-coauthoring` erstellt oder schaerft die Parent-Spec.
2. `spec-orchestrator` erzeugt Child-Schnitt, Coverage, Conformance, Dependencies, Parallel-Lanes und Hardening Queue.
3. `child-spec-hardening` arbeitet einzelne Child Specs oder Batches aus der Hardening Queue bis zur Implementierungsreife aus.
4. `doc-review-autoresolve` laeuft direkt im Anschluss oder innerhalb des Hardening-Schritts, um autonome Inkonsistenzen zu beheben und ein Readiness Verdict zu liefern.
5. `spec-change-delivery` implementiert genau einen Child, nachdem `child-spec-hardening` `IMPLEMENTATION READY` oder bewusst akzeptierte non-blocking Notes meldet.

Hardening Queue Beispiel:

| Child | Status | Required Hardening | Inputs |
|---|---|---|---|
| S3 | needs_hardening | Normative Contract, Canonical Examples/Fixtures, Pflicht-Cases, Verification nach S1/S2-Muster | Parent V2-FR-031/031a/031b, accepted S1/S2 |
| S4 | ready_candidate | Content-Freshness-Vertrag, Guide-Cases, Rendering ohne LLM | Parent Provider-Guide-Anforderungen |
| S6 | blocked | Dependency-Blocker erhalten, keine Fake-Inputs akzeptieren | S2/S3/S5 Evidence |

`spec-orchestrator` darf einen Child als `ready_candidate` markieren, wenn der Schnitt plausibel ist. `implementation-ready` ist erst erlaubt, wenn `child-spec-hardening` oder eine gleichwertige bestehende Spec die Tiefe belegt.

Child-Spec-Hardening-Pflichtgates:

1. Review Control Surface: Ziel, In/Out of Scope, wichtigste Cases/Commands, offene Entscheidungen und Readiness sind aktuell und widerspruchsfrei.
2. Status-Provenance: `done`, `accepted` oder `reference_done` nur mit Evidence/Closeout/Verification-Replay; sonst `parent_claims_done`.
3. Normative Contract: Felder, Statuswerte, Fehler-/Blockerpfade, Artefakte, Security/Redaction, Fallbacks und Beispiele/Fixtures soweit relevant.
4. Canonical Examples/Fixtures: contract-heavy Specs entscheiden explizit zwischen eingebetteten Beispielen, referenzierten Fixture-Dateien oder Hybrid; Pflichtpfade, normative Felder und Harness-Nachweis sind dokumentiert.
5. Harness-/Verification-Cases: positive, negative, fallback, blocked und secret/redaction cases mit erwarteten Exit-/Statuswerten und Artefakten.
6. Verification Commands: konkreter Execution Context, risk-based Preflight, Gate Verification, Runtime-Readiness, Success Criteria und Anti-Loop-Regel.
7. Content Quality Review: Korrektheit, Scope, Vollstaendigkeit, Konsistenz, Eindeutigkeit, Machbarkeit, Testbarkeit, Traceability, Abstraktionsniveau und Lifecycle-Fit.
8. DoR/DoD: Definition of Ready fuer Umsetzung und Definition of Done/Closeout Evidence sind vorhanden oder bewusst irrelevant.

## Definition of Ready (vor Implementierung)

Implementierung startet erst, wenn alle Punkte erfüllt sind:

1. Scope in 1-2 Sätzen fixiert.
2. Non-Goals explizit dokumentiert.
3. Review Control Surface aktuell und konsistent mit Detailsektionen.
4. Decision Freeze Pack ausgefüllt (siehe unten).
5. Referenz-Baseline benannt (**falls relevant**).
6. Testfälle/Abnahmeszenarien vorab definiert, die den späteren DoD nachweisbar machen.
7. Verifikationskommandos vorab definiert:
   - Unit/Integration Tests
   - Runtime/Compose Start
   - Health/Smoke Checks
   - Plattform-/Shell-Contract der Kommandos (z. B. macOS vs Linux) ist explizit.
   - Readiness-Strategie für timing-sensitive Runtime-Checks ist explizit (Poll/Retry/Wait).
   - Scope-Guard-Baseline ist explizit (Branch-History vs Working-Tree) inklusive Verhalten auf long-lived branches.
   - Risk-based Verification Preflight ist definiert (nur High-Risk-Kommandos; getrennte Statuslogik).
   - Anti-Loop-Regel ist definiert: kein rekursives "Verifikation der Verifikation".
   - Vereinfachungen/Anpassungen von Verification Commands sind als Vorschlagspfad mit User-Freigabe geregelt.
8. Offene Risiken, Abhängigkeiten und Blocker sind dokumentiert.
9. Bei Child Specs liegt ein `child-spec-hardening`-Readiness-Verdict vor oder die vorhandene Child Spec erfuellt nachweisbar dieselben Hardening-Pflichtgates.

## Decision Freeze Pack (kontextabhängige Checkliste)

Vor der Implementierung die **relevanten** Punkte fixieren:

1. Zielbild und Scope in 1-2 Sätzen.
2. betroffene Umgebungen/Branches (**falls relevant**).
3. Secret-/Config-Contract (**falls relevant**).
4. Datenmigration/Fallback (**falls relevant**).
5. externe Integrationsverträge zu anderen Systemen/Repos (**falls relevant**).
6. Sicherheits-/Exposure-Entscheidungen (**falls relevant**).
7. Abnahmekriterien (Go/No-Go).
8. Owner für offene Abhängigkeiten/Risiken.
9. Nachweisformat (welche Evidenzdatei, welche Kommandos).

## OpenSpec Artifact Contract (nur wenn OpenSpec aktiv)

Mindestens diese Artefakte müssen konsistent sein:

1. `proposal.md` - Why/What/Impact
2. `design.md` - Entscheidungen und Trade-offs
3. `tasks.md` - nur echte, überprüfbare Tasks; Blocker explizit offen lassen
4. `specs/*/spec.md` - Requirements + Scenarios
5. `acceptance-criteria-matrix.md` - `pass/fail/blocked`
6. `implementation-evidence.md` - konkrete Kommandos + Resultate

Regel:
- **`[BLOCKED]` ist nicht `done`**
- Teilweise Umsetzung nicht als abgeschlossen markieren

## Definition of Done (Release Gate)

Ein Change ist erst "done", wenn:

1. relevante Findings und Risiken geklärt, mitigiert oder explizit akzeptiert sind.
2. die in DoR definierten Testfälle ausgeführt und dokumentiert sind.
3. definierte Tests erfolgreich sind.
4. Runtime-Validierung erfolgreich ist (z. B. `docker compose up` + Health).
5. offene Blocker klar dokumentiert sind (inkl. Impact/Nächster Schritt).
6. Akzeptanzkriterien mit Evidenz belegt sind.
7. Specs/Plan/OpenSpec-Artefakte synchron sind (kein Drift).

## Anti-Rework Guardrails

1. Keine Umsetzung starten, solange zentrale Entscheidungen noch "im Fluss" sind.
2. Größere Vorhaben in mehrere Changes/Arbeitspakete splitten (z. B. nach Themenclustern oder Risiko).
3. Referenz-Implementierung/Baseline früh festlegen und diffen (**falls relevant**).
4. Jede Arbeitsphase endet mit:
   - Was wurde entschieden?
   - Was wurde geaendert?
   - Was bleibt offen?
   - Welche Evidenz fehlt noch?
   - Welche Skill-/Workflow-Reibung ist aufgefallen?
   - Session-/Kontextzustand: weiterarbeiten oder neue Session starten?
5. Keine "Hybrid-Steuerung": entweder OpenSpec bewusst als SSOT oder bewusst ohne OpenSpec.
6. Review-Findings werden standardmäßig per `doc-review-autoresolve` erst **autonom behoben**, dann **erneut reviewed**; Rückfrage nur bei echten Entscheidungs-/Missing-Blockern.
7. Orchestrierung und Hardening nicht vermischen: `spec-orchestrator` schneidet und priorisiert; `child-spec-hardening` erzeugt die Vertragstiefe.

## Marker System

| Marker | Bedeutung | Verwendung |
|--------|-----------|-----------|
| `[MISSING ...]` | Fehlende Information | Spec/Plan |
| `[DECISION ...]` | Offene Wahl | Spec/Plan |
| `[REVIEW ...]` | Prüfen/Validieren | Spec |
| `[MISSING SPEC ...]` | Spezifikationslücke | Plan |
| `[DECISION SPEC ...]` | Spezifikationsentscheidung offen | Plan |
| `[BLOCKED ...]` | Externer Blocker | Plan/OpenSpec Tasks |

## Review-Findings Auto-Resolution Policy

Default bei Review-Arbeit:
1. Findings erfassen.
2. Alle sicher entscheidbaren Findings ohne Zusatzfreigabe direkt beheben.
3. Im gleichen Run re-reviewen.
4. Inhaltlichen Review ausführen: nicht nur Abschnitts-/DoR-Check, sondern strenge fachliche Prüfung des gesamten Vorhabens.
5. Nach jeder Spec-Änderung automatisch Readiness-Status melden; der User soll nicht separat fragen müssen, ob die Spec implementation-ready ist.
6. Wiederholen, bis keine autonomen Findings mehr offen sind.

Findings muessen fuer den tatsaechlichen Review-Stil des Users formuliert sein. Der User liest typischerweise zuerst Ziel, In Scope, Out of Scope, Verification Commands und Test-/Harness-Cases; er hat den mittleren Vertrags-/Detailteil oft nur ueberflogen. Deshalb muss jedes nicht-triviale Finding auch ohne vollstaendige Detaillekture verstaendlich sein.

Finding-Format fuer nicht-triviale Punkte:

1. Kurzbefund in Alltagssprache.
2. Warum das wichtig ist: welcher Implementierungs-/Review-Fehler sonst passieren kann.
3. Wo der User es pruefen soll: Ziel/Scope/Verification/Test-Cases nennen, nicht nur die tiefe Vertragsstelle.
4. Konkretes Beispiel: fehlendes Artefakt, Statuswert, Fixture, Kommando, Testfall oder Verhalten.
5. Noetige Aktion: autonomer Fix oder konkrete User-Entscheidung.

Terse technische Labels reichen nicht. Statt "Canonical Examples/Fixtures decision missing" erklaeren: "Diese Spec definiert ein Manifest. Damit der Implementierer nicht raet, braucht es entweder ein kleines Beispiel in der Spec oder benannte Fixture-Dateien, die die Harness spaeter ausfuehrt."

Inhaltliche Review-Fragen orientieren sich an etablierten Requirements-Qualitaetskriterien:

- Ist das beschriebene Verhalten fachlich korrekt fuer Problem, Nutzer und Kontext?
- Ist jede Anforderung notwendig und im Scope, oder versteckt sie Scope Creep bzw. ein Non-Goal?
- Sind Normalpfad, Edge Cases, Fehlerpfade, Abhaengigkeiten, Constraints und Annahmen ausreichend vollstaendig?
- Sind Anforderungen, Beispiele, Begriffe, Statuswerte, Parent-/Child-Scope, Akzeptanzkriterien und Verification Commands konsistent?
- Ist die Aussage eindeutig genug, dass keine materiell unterschiedlichen Implementierungen plausibel sind?
- Ist die Anforderung in der Zielumgebung machbar?
- Ist sie testbar/verifizierbar durch Test, Inspection, Analyse, Demonstration oder konkrete Abnahme-Evidenz?
- Ist sie traceable zu Intent, Parent Scope, Akzeptanzkriterien, Verification Commands und nachgelagerten Artefakten?
- Ist sie atomar und auf dem richtigen Abstraktionsniveau?
- Sind operative/lifecycle-relevante Themen wie Migration, Fallback, Rollback, Observability, Kompatibilitaet, Ownership und Closeout-Evidenz abgedeckt, falls relevant?

Inhaltliche P1-Beispiele:

- Datenartefakte ohne die fuer den eigenen nachgelagerten Flow notwendige Identitaet, Provenance oder Kontextbindung.
- Hash-/Signaturvertrag ohne kanonische Serialisierung.
- Manifest oder Run-Status ohne erlaubte Werte, Fehlerstatus oder Provenance.
- Akzeptanzkriterium kann formal grün werden, obwohl der intendierte Kontrollfluss übersprungen wurde.
- Anforderung ist mehrdeutig, fachlich widerspruechlich, technisch unmachbar oder nicht testbar.
- Wichtiger Fehler-/Edge-Case fehlt, obwohl die Implementierung ohne ihn nicht sicher oder sinnvoll abgeschlossen werden kann.

Use-Case-spezifische Beispiele sind keine globalen Pflichtfelder. Ein Survey braucht z. B. nur dann Frage-IDs im Antwortvertrag, wenn die Spec spaetere Interpretation nach Frage vorsieht.

Eskalation an den User nur wenn:
- mehrere fachlich unterschiedliche Lösungen möglich sind,
- Sicherheits-/Policy-Entscheidungen betroffen sind,
- oder Marker-basierte Entscheidungslücken bestehen (`[MISSING ...]`, `[DECISION ...]`, blockierende `[REVIEW ...]`).

## History und SessionId (verpflichtend)

History und SessionId bleiben verpflichtend, aber ohne Iterationssystem.

1. Jede Spec hat am Dateiende eine append-only History-Tabelle im Format:
   - `| Date | Author | Change |`
2. Jede History-Zeile beschreibt die jeweilige Anpassung in genau einem kurzen Satz.
3. Keine Iterationsspalte und keine Iterationsnummern verwenden.
4. Vorhandene Iterations-History bei Berührung auf das 3-Spalten-Format migrieren.
5. `SessionId` am Dateiende beibehalten; falls fehlend, ergänzen als `SessionId: <session-id>`.
6. Statuswechsel (`🟡 Spec` / `🟠 Plan` / `🔵 Implemented` / `🟢 Accepted`) müssen jeweils mit einer passenden neuen History-Zeile dokumentiert werden.

Hinweis:
- Diese History-Regel gilt für **Spec-Dateien**.
- Iterative History in **Plan-Dateien** (z. B. `refine-plan`) bleibt davon unberührt.

## File Conventions

| Typ | Ort | Muster |
|-----|-----|--------|
| Spezifikation (ohne OpenSpec) | `_specs/` | `YYYY-MM-DD <Titel>.md` |
| Plan | neben Spec oder Projektordner | `<name>-plan.md` |
| OpenSpec Change (optional) | `openspec/changes/<change>/` | Standard-Artefakte |
| Retro/Mini-Retro | inline im Plan/Spec/Handoff oder eigene Datei | `<name>-retro.md` |

## Übergänge

### Spec -> Plan
Workflow 1: `refine-plan` iterativ; bei implementierungsreifem Plan Status `🟠 Plan`.
Workflow 2: `spec-change-delivery` setzt Status `🟠 Plan`, sobald der Scope Contract fixiert ist.

### Plan -> Umsetzung
Nur bei erfüllter Definition of Ready. Nach ausgeführter Umsetzung mit Artefakten: Status `🔵 Implemented`.

### Umsetzung -> Accepted
In beiden Workflows optional über `spec-closeout`: Status `🟢 Accepted`, wenn Verifikation vollständig grün ist und (falls aktiv) OpenSpec archiviert wurde.

### Arbeitsblock -> Mini-Retro / Retro
Mini-Retro nach signifikanten Spec-, Review-, Delivery- oder Closeout-Bloecken sowie vor Session-Ende, Kontextwechsel oder Skill-Handoff. "retro the plan" nach signifikanten Meilensteinen, wenn Ursachenanalyse oder Planverbesserung noetig ist; "final retro the plan" vor Abschluss.

### Review Findings -> Auto-Resolve
Bei Findings aus Review-Runden zuerst `doc-review-autoresolve` ausführen (fix + re-review loop). Erst verbleibende Entscheidungs- oder Missing-Blocker an den User eskalieren.

### Retro -> Improve Skills
Wiederkehrende Probleme als `improve-skills`-Kandidaten erfassen und in Workflow/Skills einarbeiten.

## Lightweight Checkliste vor Umsetzung

1. Sind Modus/Skill und Source of Truth klar?
2. Sind Ziel, Nicht-Ziele, In Scope und erwarteter Output klar?
3. Ist die Review Control Surface aktuell?
4. Ist der Scope klar abgegrenzt?
5. Sind Entscheidungen eingefroren (Decision Freeze Pack)?
6. Sind Test- und Runtime-Gates vorab definiert?
7. Ist eine Referenz-Baseline nötig und benannt (falls relevant)?
8. Sind externe Abhängigkeiten/Owner dokumentiert?
9. Ist klar, was "done" konkret bedeutet?
