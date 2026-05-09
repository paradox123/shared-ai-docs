**Date:** 2026-05-09
**Status:** 🟡 Spec
**Scope:** Mockdaten und Ende-zu-Ende-Harness fuer den Agent Delivery Workflow ohne reale Produkt-Specs

---

## Review Control Surface

- Spec-Variante: Child-/Ergaenzungsspec zur DocWorkflow Agent Delivery Testsuite.
- Goldstandard Status: hardened draft, ready for implementation planning.
- Ziel: Die Testsuite soll den Agent Delivery Workflow mit synthetischen Mock-Specs Ende-zu-Ende pruefen: ein kleiner Mock fuer den Large-Spec-Pfad muss automatisch in Parent/Child-Delivery mit Folgesessions gehen und am Ende die Datei `count.txt` mit `1` bis `5` erzeugen; kleine Direct-Specs muessen direkt geliefert werden, ohne kuenstlichen Split.
- In Scope: source-controlled Mockdaten, kleine Large-Path Mock-Parent-Spec mit Mock-Sizing-Directive, kleine Mock-Direct-Spec, Anpassung bestehender Tests an diese Mockdaten, neue Assertions und neue Mock-E2E-Tests, erwartete triviale Runtime-Ergebnisse, automatische Session-Start-/Queue-Evidence, Parent/Child-Orchestration, Child-Hardening, Single-Child-Delivery, Closeout, Next-Session-Handoff, negative Guards gegen echte Projektfixtures.
- Out of Scope: KI-fuer-KMU oder andere reale Produkt-Specs als Testdatenquelle, produktive Runtime-Features, echte externe Infrastruktur, Docker als Pflicht fuer den Mock-E2E-Basispfad, vollstaendige App-Entwicklung.
- Wichtigste Test-/Harness-Cases: `MOCK-LARGE-E2E` fuer den vollstaendigen Pfad von Mock-Parent-Spec bis fertiger `count.txt`; `MOCK-SMALL-E2E` fuer kleine Direct-Spec ohne Split; `MOCK-MIGRATE-EXISTING-TESTS` fuer Umstellung vorhandener L0/L1/L2/L3/Reporting-Checks auf Mockdaten; `MOCK-FORBID-REAL-FIXTURE` gegen KI-fuer-KMU-/Realprojekt-Testdaten; `MOCK-SESSION-CHAIN` fuer Session-Launch-Evidence und Handoff-Kette.
- Wichtigste Verification Commands: `bash -n tests/docworkflow-agent-delivery/scripts/*.sh`; zukuenftig `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep`; zukuenftig `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh small --keep`; zukuenftig `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`; `openspec validate docworkflow-agent-delivery-testsuite --strict`; `git diff --check`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen. Docker bleibt fuer diese Mock-E2E-Basis optional; der akzeptierte E2E-Pfad nutzt einen lokalen Mock Session Runner, der echte Session-Grenzen, Handoffs, Resume-Schritte und Evidence deterministisch materialisiert, ohne externe Infrastruktur zu brauchen.
- Readiness Status: READY WITH NON-BLOCKING NOTES for implementation planning. The local Mock Session Runner command cannot be rehearsed before it exists; the implementing slice must create it first, then run the declared verification commands before closeout.

## Session Briefing

- Modus/Skill: `doc-coauthoring`.
- Source of Truth: diese Spec, `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`, `docs/doc-workflow.md`, Agent Delivery Session Launch/Queue Evidence Regeln.
- Ziel: Die Testdatenstrategie der Agent Delivery Testsuite von realen Produktartefakten auf synthetische, validierbare Mock-Specs umstellen, vorhandene Tests samt Assertions auf diese Daten migrieren und neue echte Workflow-E2E-Tests ermoeglichen.
- Nicht-Ziele: keine Migration oder weitere Nutzung von KI-fuer-KMU-Testdaten; keine echte Anwendung als Nebeneffekt der Tests; keine manuelle Agenten-Kette als akzeptierter Standardbeweis.
- In Scope: Mock-Specs, Manifest-/Expected-Output-Vertraege, Migration vorhandener Harnesses und Assertions, neue Mock-E2E-Testfaelle, Session-Chain-Evidence, Harness-Erweiterung und klare Akzeptanzkriterien fuer grosse und kleine Spec-Pfade.
- Erwarteter Output: eine Spec, die als Grundlage fuer einen Folge-Change zur Implementierung der Mockdaten und E2E-Harnesses dient.
- Verification/Review: Content Review gegen Scope, Testbarkeit, Isolation, Session-Automation und Verbot realer Produktfixtures.
- Offene Entscheidungen: Keine fuer die Spec-Autorenschaft.

## Parent Scope Conformance

Normative Parent Source:

- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`

| Parent Requirement / Intent | Conformance | Umsetzung in dieser Spec |
|---|---|---|
| Parent-first Orchestration und Sizing Gate | extends | Large-Path Mock Parent nutzt eine explizite Test-only Mock-Sizing-Directive, um den Parent/Child-Pfad ohne grosse echte Spec-Datei zu triggern. |
| Child-Hardening-Gate | preserves | Fuenf Mock-Childs brauchen eigene Child Specs, Handoffs, Write-Sets, Session-Evidence und `ran-target` Delivery, bevor der E2E pass melden darf. |
| Single-Child Delivery | preserves | Jede Child-Delivery darf nur die eigene Zahl in `mock-target/output/count.txt` setzen und nur im isolierten Mock-Target schreiben. |
| Closeout und Next-Child-Gate | extends | Der Runner muss nach jedem Child Closeout die naechste Session automatisch starten/resumen und darf den naechsten Child nicht vor Vorgaenger-Closeout ausfuehren. |
| Evidence Integrity | extends | Mock-Manifeste, Session-Evidence, Output-Evidence und Forbidden-Real-Fixture-Checks ersetzen reale Produktfixtures als Beweisquelle. |
| Style / Efficiency / Telemetry | preserves | Summary und Session-Evidence muessen Status, Pfade, Forbidden Checks und Output-Evidence maschinenlesbar machen. |

Diese Spec widerspricht dem Parent nur dort bewusst, wo alte KI-fuer-KMU-basierte Testdaten aus dem Standard-Gate entfernt werden. Das ist eine Korrektur der Testdatenstrategie, kein Produkt-Scope.

## 1. Problem

Die bestehende Agent Delivery Testsuite hat reale Projektartefakte als Testdaten verwendet. Das macht Ende-zu-Ende- oder Teil-Ende-zu-Ende-Tests unscharf:

- Eine reale grosse Produkt-Spec erzeugt den Druck, eine echte Anwendung oder grosse Domain-Slices zu entwickeln.
- Testergebnisse vermischen Workflow-Verhalten mit Produktdomäne, Legacy-Status, Archivierungszustand, Runtime-Komplexitaet und externer Fixture-Drift.
- Ein roter oder gruener Test sagt dann nicht eindeutig, ob der Agent Delivery Workflow korrekt ist.
- KI-fuer-KMU-Testdaten haben in diesem Kontext mehr geschadet als geholfen und duerfen nicht weiter als Harness-Quelle verwendet werden.

Der Workflow braucht stattdessen synthetische Testdaten, die genau den Delivery-Prozess provozieren, aber fachlich trivial bleiben.

## 2. Zielbild

Die Testsuite bekommt eine eigene Mockdaten-Familie fuer Workflow-E2E-Tests:

1. Eine kleine Mock-Parent-Spec fuer den Large-Spec-Pfad, die per expliziter Mock-Sizing-Directive als zu gross fuer Direct Delivery behandelt wird und den Parent/Child-Agent-Delivery-Workflow erzwingen muss.
2. Eine kleine Mock-Direct-Spec, die absichtlich klein genug fuer direkte Umsetzung ist und nicht aufgeteilt werden darf.
3. Erwartete Outputs, die trivial und deterministisch validierbar sind.
4. Session-Launch-/Queue-Evidence, die beweist, dass Folge-Sessions automatisch und mit dem richtigen Handoff gestartet oder vorbereitet wurden.
5. Negative Guards, die jede Verwendung von KI-fuer-KMU oder anderen realen Produktfixtures als E2E-Testdaten blockieren.
6. Eine Migration der bestehenden L0/L1/L2/L3/Reporting-Harnesses auf die neuen Mockdaten, soweit sie weiterhin Bestandteil der Standard-Regression bleiben.
7. Neue Tests und Assertions, die den vollstaendigen Large-Spec-Workflow bis zur fertigen `count.txt` beweisen.

Der Testgegenstand ist der Workflow:

- Sizing-Entscheidung,
- Parent-Control-Layer,
- Child-Schnitt,
- Child-Hardening,
- Handoff-Erzeugung,
- automatischer Folge-Session-Start,
- Delivery gegen isolierte Mock-Targets,
- Closeout-Sync,
- kontrollierte Freigabe oder Blockade des naechsten Schritts.

Die Mock-Domaene selbst darf keine echte fachliche Komplexitaet enthalten.

## 2.1 Scope Clarification: Mehr als Testdaten

Diese Spec umfasst nicht nur die Erzeugung der Mockdaten. Sie umfasst auch die Umstellung der vorhandenen Testsuite und den Ausbau neuer Tests:

- vorhandene Tests duerfen nicht weiter still gegen KI-fuer-KMU oder andere reale Produktfixtures laufen,
- bestehende Harnesses muessen entweder auf Mockdaten migriert, aus der Standard-Regression entfernt oder als historische Retro-Artefakte markiert werden,
- vorhandene Assertions muessen auf die neuen Mock-Manifeste, Mock-Outputs und Session-Evidence zeigen,
- neue Assertions muessen den Large-Path-Endzustand `count.txt == "1\n2\n3\n4\n5\n"` beweisen,
- neue Assertions muessen den Small-Direct-Pfad ohne Child-Artefakte beweisen,
- neue Guards muessen echte Produktpfade als Testdatenquelle blockieren.

Der fuehrende Large-E2E-Test muss wirklich gehbar sein: Er startet bei der Mock-Parent-Spec und endet erst dann erfolgreich, wenn alle fuenf Child-Deliveries gelaufen sind und die finale Artefaktdatei validiert wurde. Queue- oder Blocker-Zustaende duerfen fuer Teiltests sichtbar sein, ersetzen aber nicht den akzeptierten Ende-zu-Ende-Beweis.

## 2.2 Execution Model: Local Mock Session Runner

Der fuehrende Mock-E2E darf nicht von externen Agent-Providern, echter Codex-Auth, Docker, Netzwerk oder manuellen Starts abhaengen. Er nutzt deshalb einen lokalen Mock Session Runner als akzeptierten Basispfad.

Der Mock Session Runner ist kein Fake fuer die Assertions. Er materialisiert den Workflow deterministisch:

1. liest `mock-large-parent-spec.md` oder `mock-small-direct-spec.md`,
2. trifft die Sizing-Entscheidung aus dem Testmanifest,
3. erzeugt fuer den Large-Pfad Parent Control Output, Child Index, fuenf Child Specs und fuenf Handoffs,
4. erzeugt pro Child einen eigenen Session-Step-Ordner mit Start-/Resume-/Closeout-Evidence,
5. fuehrt jede Child Delivery in einem separaten isolierten Schritt aus,
6. schreibt nur die erlaubte eigene Zahl in `mock-target/output/count.txt`,
7. validiert nach jedem Schritt die Session-Reihenfolge und Write-Boundary,
8. validiert am Ende die fertige `count.txt`.

Der Live-Agent-/Codex-Pfad darf spaeter als zusaetzlicher optionaler Harness dazukommen, ist aber nicht Voraussetzung fuer den ersten akzeptierten Mock-E2E. Ein optionaler Live-Pfad darf den lokalen Mock Session Runner nicht ersetzen, solange er Auth-, Provider-, Netzwerk- oder manuelle Startabhaengigkeiten hat.

Erlaubte Session-Endzustaende im akzeptierten Basispfad:

| Status | Bedeutung | E2E-Akzeptanz |
|---|---|---|
| `started` | Session-Step wurde automatisch begonnen. | Zwischenstatus. |
| `resumed` | Ein queued Step wurde automatisch aufgenommen. | Zwischenstatus. |
| `ran-target` | Step hat sein Zielartefakt im Mock-Target erzeugt. | Erforderlicher Endstatus fuer jeden Large-Child. |
| `closed` | Closeout fuer den Step ist synchronisiert. | Erforderlich vor Start des naechsten Large-Child. |
| `queued` | Step wartet auf automatisches Resume. | Nur Zwischenstatus. |
| `manual_start_required` | Menschlicher Start waere noetig. | Fehler im fuehrenden E2E. |
| `blocked` | Erwarteter negativer Testblocker. | Nur in expliziten Negativtests erlaubt. |
| `failed` | Unerwarteter Fehler. | Immer Fehler. |

## 3. Mockdaten-Familie

### 3.1 Large-Path Mock Parent Spec

Pfad:

- `tests/docworkflow-agent-delivery/mock-data/large-parent/mock-large-parent-spec.md`

Zweck:

- Loest das Spec Sizing Gate ueber eine explizite Mock-Sizing-Directive aus, nicht ueber physisch grosse Dateigroesse.
- Muss als Parent-Control-Layer erhalten bleiben.
- Muss in genau fuenf Child-Slices geschnitten werden.
- Muss fuer diese fuenf Childs automatische Folge-Sessions erzeugen oder eindeutig in die Launch Queue stellen.
- Muss sehr klein bleiben; der Test darf keine grosse Spec-Datei, keine grossen Artefakte und keine vielen Output-Dateien erzeugen.

Inhaltliche Domaene:

- Eine absichtlich triviale "Mock Counter" oder gleichwertige Fake-Domaene.
- Die Parent-Spec enthaelt z. B. `Mock Sizing Directive: force_parent_child`.
- Die Mock-Sizing-Directive ist test-only. Sie darf nur von Mock-E2E-Harnesses ausgewertet werden und darf die produktive Spec-Sizing-Logik nicht als allgemeinen Bypass veraendern.
- Keine externen APIs.
- Keine echten Secrets.
- Keine Docker- oder Infrastrukturpflicht.
- Keine Abhaengigkeit von realen Repositories ausser dem isolierten Testziel.

Erwartete Parent Requirements:

| Requirement | Beschreibung | Erwarteter Child |
|---|---|---|
| `ML-PR1` | Mock-Sizing-Directive erzwingt `parent_child` und blockiert Direct Delivery. | Orchestrator/Parent |
| `ML-PR2` | Child 1 schreibt die Zahl `1` in die gemeinsame Zaehldatei. | `ML-C1` |
| `ML-PR3` | Child 2 schreibt die Zahl `2` in die gemeinsame Zaehldatei. | `ML-C2` |
| `ML-PR4` | Child 3 schreibt die Zahl `3` in die gemeinsame Zaehldatei. | `ML-C3` |
| `ML-PR5` | Child 4 schreibt die Zahl `4` in die gemeinsame Zaehldatei. | `ML-C4` |
| `ML-PR6` | Child 5 schreibt die Zahl `5` in die gemeinsame Zaehldatei. | `ML-C5` |
| `ML-PR7` | Closeout synchronisiert Parent, Child Index, Evidence und Session-Status nach jedem Child. | Closeout |

Erwartete triviale Runtime-Outputs:

- `mock-target/output/count.txt`

Erwarteter Endinhalt:

```text
1
2
3
4
5
```

Jeder Child darf nur seinen eigenen naechsten Zahlenwert setzen. `ML-C3` darf z. B. nicht die Zahlen `1`, `2`, `4` oder `5` schreiben oder korrigieren. Dadurch bleibt der Output klein, aber die Session-Reihenfolge und Child-Verantwortung werden validierbar.

### 3.2 Small Mock Direct Spec

Pfad:

- `tests/docworkflow-agent-delivery/mock-data/small-direct/mock-small-direct-spec.md`

Zweck:

- Beweist, dass der Workflow nicht pauschal jede Spec in Parent/Child aufteilt.
- Muss Direct Delivery erlauben.
- Darf keinen Child Index, keine Child Specs und keine Child Session Handoffs erzeugen.

Inhaltliche Domaene:

- Eine einzelne triviale Aufgabe, z. B. "schreibe eine statische Statusdatei".
- Keine Abhaengigkeiten.
- Kein Split-Potential.

Erwarteter Runtime-Output:

- `mock-target/output/small-direct-result.json`

Beispielinhalt:

```json
{
  "mode": "direct",
  "result": "ok",
  "source": "mock-small-direct"
}
```

### 3.3 Mock Manifest Contract

Jede Mockdaten-Familie muss ein Manifest enthalten:

- `fixture_id`
- `fixture_version`
- `spec_type`: `large-parent` oder `small-direct`
- `expected_delivery_mode`: `parent_child` oder `direct`
- `source_spec`
- `target_repo`
- `expected_outputs`
- `forbidden_outputs`
- `expected_sessions`
- `expected_closeout_state`
- `forbidden_source_paths`
- `runner_mode`
- `session_strategy`

Beispiel fuer grosse Spec:

```json
{
  "fixture_id": "mock-large-parent-v1",
  "fixture_version": "1.0.0",
  "spec_type": "large-parent",
  "expected_delivery_mode": "parent_child",
  "runner_mode": "local-mock-session-runner",
  "session_strategy": "auto-start-and-resume",
  "source_spec": "mock-large-parent-spec.md",
  "target_repo": "mock-target",
  "mock_sizing_directive": "force_parent_child",
  "expected_children": ["ML-C1", "ML-C2", "ML-C3", "ML-C4", "ML-C5"],
  "expected_outputs": [
    "mock-target/output/count.txt"
  ],
  "expected_output_content": "1\n2\n3\n4\n5\n",
  "child_output_contract": {
    "ML-C1": "append_or_set_line:1",
    "ML-C2": "append_or_set_line:2",
    "ML-C3": "append_or_set_line:3",
    "ML-C4": "append_or_set_line:4",
    "ML-C5": "append_or_set_line:5"
  },
  "expected_sessions": [
    {
      "child_id": "ML-C1",
      "launch_status": "queued_or_started",
      "expected_final_status": "ran-target",
      "handoff_required": true
    },
    {
      "child_id": "ML-C2",
      "launch_status": "queued_or_started_after_ml_c1_closeout",
      "expected_final_status": "ran-target",
      "handoff_required": true
    },
    {
      "child_id": "ML-C3",
      "launch_status": "queued_or_started_after_ml_c2_closeout",
      "expected_final_status": "ran-target",
      "handoff_required": true
    },
    {
      "child_id": "ML-C4",
      "launch_status": "queued_or_started_after_ml_c3_closeout",
      "expected_final_status": "ran-target",
      "handoff_required": true
    },
    {
      "child_id": "ML-C5",
      "launch_status": "queued_or_started_after_ml_c4_closeout",
      "expected_final_status": "ran-target",
      "handoff_required": true
    }
  ],
  "forbidden_source_paths": [
    "/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**",
    "ki-fuer-kmu/**"
  ]
}
```

Beispiel fuer kleine Spec:

```json
{
  "fixture_id": "mock-small-direct-v1",
  "fixture_version": "1.0.0",
  "spec_type": "small-direct",
  "expected_delivery_mode": "direct",
  "runner_mode": "local-mock-session-runner",
  "session_strategy": "direct-no-child-session",
  "source_spec": "mock-small-direct-spec.md",
  "target_repo": "mock-target",
  "expected_children": [],
  "expected_outputs": [
    "mock-target/output/small-direct-result.json"
  ],
  "forbidden_outputs": [
    "child-index.md",
    "child-session-handoffs/**",
    "child-specs/**"
  ],
  "forbidden_source_paths": [
    "/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**",
    "ki-fuer-kmu/**"
  ]
}
```

## 4. E2E Harness Requirements

### 4.1 Large Spec E2E

Der Large-Spec-Harness muss den Workflow von Sizing bis Closeout pruefen.

Mindestablauf:

1. Isoliertes Mock-Target-Repo erzeugen.
2. Large-Path Mock Parent Spec als Startinput bereitstellen.
3. Agent Delivery Workflow starten.
4. Sizing Gate muss `parent_child` statt `direct` entscheiden.
5. Parent-Control-Layer, Child Index, fuenf Child Specs und fuenf Child Session Handoffs muessen erzeugt werden.
6. Automatischer Start oder Queue-Eintrag fuer die erste Child-Session muss mit Evidence belegt werden.
7. Queue-Zustaende muessen im fuehrenden E2E-Lauf automatisch verarbeitet werden; ein dauerhaftes `queued` oder `manual_start_required` ist kein erfolgreicher Endzustand.
8. Jede Child Delivery muss nur im Mock-Target schreiben.
9. Jeder Child Closeout muss Parent/Index/Evidence/OpenSpec-/Ledger-Status synchronisieren.
10. Die naechste Child-Session muss nach dem Closeout des Vorgaengers automatisch gestartet oder aus der Queue aufgenommen werden.
11. Nach allen fuenf Childs muss `mock-target/output/count.txt` exakt die Zahlen `1` bis `5` in Reihenfolge enthalten.

Erfolg:

- `overall_workflow_status: pass`
- `sizing_decision: parent_child`
- alle fuenf erwarteten Childs haben `ran-target`
- alle fuenf Session-Schritte haben positiven Start-/Resume-Nachweis; dauerhaftes `queued`, `manual_start_required`, `blocked` oder `failed` ist im fuehrenden Large-E2E ein Fehler
- `mock-target/output/count.txt` existiert und entspricht exakt dem erwarteten Inhalt
- keine realen Produktpfade wurden gelesen oder geschrieben, ausser explizit erlaubten shared-ai-docs Workflow-Dateien

Der fuehrende Large-E2E muss im Modus `local-mock-session-runner` mit `evidence_truth: ran-target` laufen. Ein Live-Agent-Modus darf zusaetzlich existieren, darf aber fuer diese Akzeptanz nicht als einzige Beweisquelle erforderlich sein.

### 4.2 Small Spec E2E

Der Small-Spec-Harness muss beweisen, dass kleine Specs direkt geliefert werden.

Mindestablauf:

1. Isoliertes Mock-Target-Repo erzeugen.
2. Small Mock Direct Spec als Startinput bereitstellen.
3. Agent Delivery Workflow starten.
4. Sizing Gate muss `direct` entscheiden.
5. Keine Child-Control-Artefakte duerfen erzeugt werden.
6. Direct Delivery schreibt genau die erwartete Mock-Ausgabedatei.
7. Closeout oder Abschluss-Evidence markiert die Spec als direkt erledigt.

Erfolg:

- `overall_workflow_status: pass`
- `sizing_decision: direct`
- `child_index_created: false`
- `child_specs_created: false`
- `child_handoffs_created: false`
- erwarteter Direct Output existiert
- keine Session-Queue fuer Child Delivery wird erzeugt

### 4.3 Session Launch / Queue Evidence

Automatische Folge-Sessions sind Teil des Testgegenstands.

Jeder relevante Session-Schritt muss ein Evidence-Artefakt erzeugen, z. B. unter:

- `tests/docworkflow-agent-delivery/e2e/evidence/<run-id>/sessions/`

Mindestfelder:

| Feld | Bedeutung |
|---|---|
| `session_step_id` | Stabiler Schritt, z. B. `ML-C1-delivery`. |
| `source_handoff` | Pfad zum Handoff, das die Session starten darf. |
| `target_child_id` | Child oder Direct-Delivery-ID. |
| `launch_status` | `started`, `queued`, `manual_start_required`, `blocked`, `failed`. |
| `launch_mechanism` | Verwendeter Launcher, Queue, Automation oder Fallback. |
| `target_workspace` | Isolierter Mock-Target-Pfad. |
| `allowed_write_set` | Schreibgrenzen der Session. |
| `forbidden_paths_checked` | Liste gepruefter verbotener Pfade. |
| `result_evidence` | Pfade zu Output, Summary und Logs. |
| `final_status` | `ran-target`, `closed`, `blocked` oder `failed`; fuer Large-Childs muss `ran-target` plus Closeout-Evidence vorliegen. |
| `sequence_index` | 1-basierte Reihenfolge fuer `ML-C1` bis `ML-C5`. |

Akzeptanz fuer E2E:

- `started` ist positive Session-Automation-Evidence; `queued` ist nur dann positiv, wenn ein spaeteres automatisches Resume-/Completion-Evidence denselben Schritt abschliesst oder der Test explizit nur Queue-Verhalten prueft.
- `manual_start_required` ist fuer diese Spec kein positives E2E-Ergebnis, sondern hoechstens ein blockierter Zwischenstand.
- `blocked` ist nur positiv, wenn der Testfall explizit einen Blocker erwartet.
- `failed` ist immer ein Testfehler.
- Fuer `MOCK-LARGE-E2E` darf `queued` nur ein Zwischenstatus sein. Der Endzustand muss fuer jeden Child `started` plus `ran-target` oder ein gleichwertiges automatisches Resume-/Completion-Evidence enthalten.

## 4.4 Existing Test Migration Requirements

Die vorhandene Testsuite muss an die Mockdaten angepasst werden. Die Migration ist Teil dieses Scopes.

Vorschlag fuer die Umstellung:

| Bestehender Bereich | Anpassung | Neue fuehrende Assertion |
|---|---|---|
| `run-contract-checks.sh` / L0 | KI-fuer-KMU-Quelle entfernen oder aus Standardpfad deaktivieren; L0 gegen Mock-Manifeste und verbotene Pfade laufen lassen. | Kein Realprojekt-Pfad; Mock-Manifeste vollstaendig; Small/Large Sizing-Erwartung parsebar. |
| `setup-fixture.sh` | Keine Default-Quelle ausser `tests/docworkflow-agent-delivery/mock-data/**`; keine absolute KI-fuer-KMU-Quelle. | Fixture stammt aus Mockdaten und dokumentiert alle Kopien/Normalisierungen. |
| L1 deterministic fixtures | Bestehende negative Fixture-Logik behalten, aber auf Mock Child Index, Mock Handoffs und Mock Manifests mappen. | Thin Child bleibt blocked; fehlende Rehearsal-/Handoff-Evidence blockiert; keine reale Source. |
| L2 parent-first | Input wird `mock-large-parent-spec.md`; Output muss fuenf Childs, Child Index, Coverage, Handoffs und erste Session Launch/Queue Evidence erzeugen. | `ML-C1` bis `ML-C5` existieren und Direct Delivery ist blockiert. |
| L2 single-child closeout | Auf `ML-C1` bis `ML-C5` sequenzieren; jeder Closeout gibt nur den naechsten Child frei. | `ML-C(n+1)` startet erst nach `ML-Cn` Closeout. |
| L3 runtime-temp-repo | Runtime-Ziel ist nur `mock-target`; Childs schreiben gemeinsam `output/count.txt`. | Endinhalt exakt `1\n2\n3\n4\n5\n`; jeder Child nur eigene Zahl. |
| Reporting / Telemetry | Summary-Schema um Mock-E2E-Felder erweitern oder eigenes Mock-E2E-Summary-Schema validieren. | `sizing_decision`, `session_chain_status`, `expected_outputs_status`, `forbidden_fixture_status` sind korrekt. |

Nicht migrierte alte Tests duerfen nicht mehr im Standard-`all` der Agent Delivery Testsuite laufen. Wenn ein alter Test nur historische Erkenntnis hat, muss er als archiviert, retro-only oder non-gating markiert werden.

## 4.5 Write-Set, Shared Files und Closeout Sync

Implementation Write-Set:

- `tests/docworkflow-agent-delivery/mock-data/**`
- `tests/docworkflow-agent-delivery/e2e/**`
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`, nur soweit noetig, um KI-fuer-KMU als Default-Quelle zu entfernen oder Mockdaten als Default zu setzen.
- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`, nur soweit noetig, um den Standardpfad auf Mockdaten oder non-gating Legacy umzulenken.
- `tests/docworkflow-agent-delivery/README.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`, nur fuer Parent-Index-/Strategie-Sync nach Implementierung.
- `openspec/changes/**` und `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`, falls der Folge-Change OpenSpec nutzt.

Shared / Read-only Files:

- KI-fuer-KMU und andere reale Produkt-Repositories sind read-only und forbidden als Testfixture.
- Bestehende retained Evidence unter `tests/docworkflow-agent-delivery/**/evidence/2026-05-08-*` ist read-only historische Evidence, ausser ein Folge-Change archiviert oder markiert sie ausdruecklich als non-gating.
- Bestehende Parent Testsuite Spec ist Sync-Ziel, nicht freie Rewrite-Fläche.

Closeout Sync Targets:

- README muss den Mock-E2E als fuehrenden Workflow-E2E-Regressionstest dokumentieren.
- Parent Testsuite Spec oder Nachfolger muss KI-fuer-KMU-Ausschluss, Mockdatenstrategie und `run-mock-e2e-checks.sh all --keep` als fuehrenden E2E-Gate aufnehmen.
- Alte KI-fuer-KMU-basierte Standardbefehle muessen entfernt, ersetzt oder als non-gating/historical markiert werden.
- Retained Evidence muss zwischen historischer Evidence und neuer Mock-E2E-Evidence unterscheiden.

## 4.6 Delivery Slices

Der Folge-Change darf als ein bounded delivery slice umgesetzt werden, solange der Scope auf Mockdaten und Harness-Anpassung beschraenkt bleibt. Falls die automatische Session-Launcher-Integration in echte Codex-/App-Automation ausweitet, muss sie als eigener Child-/Follow-up-Slice behandelt werden.

Empfohlene Umsetzungsslices:

| Slice | Inhalt | Darf parallel? | Done-Signal |
|---|---|---|---|
| `MD-E2E-1` | Mockdaten, Manifeste, Mock Target Fixture und Forbidden-Path Validator. | Ja, vor Runner-Integration. | Manifest-Schema und Forbidden-Real-Fixture-Test gruen. |
| `MD-E2E-2` | Local Mock Session Runner und `run-mock-e2e-checks.sh large/small/all`. | Nach `MD-E2E-1`. | Large und Small E2E erzeugen erwartete Artefakte. |
| `MD-E2E-3` | Migration/Deaktivierung alter Standard-Gates und README/Parent-Sync. | Nach Runner-Vertrag stabil. | Standard-`all` nutzt Mockdaten und keine KI-fuer-KMU-Quelle. |
| `MD-E2E-4` | Optionaler Live-Agent-/Codex-Session-Pfad. | Separater Follow-up. | Live-Pfad schreibt kompatible Evidence, ersetzt aber nicht den lokalen Basispfad. |

Der erste akzeptierte Implementation-Ready Scope umfasst `MD-E2E-1` bis `MD-E2E-3`. `MD-E2E-4` ist optionaler spaeterer Ausbau.

## 4.7 New Test Proposals

Die Umsetzung soll mindestens diese neuen Tests anlegen:

| Neuer Test | Zweck | Fuehrende Assertions |
|---|---|---|
| `mock-data-manifest-schema` | Validiert Large-/Small-Manifeste vor Agent-Ausfuehrung. | Pflichtfelder vorhanden; verbotene Pfade deklariert; erwartete Outputs parsebar. |
| `mock-large-sizing` | Prueft die Sizing-Entscheidung fuer die Large-Path Mock Parent Spec. | `force_parent_child` fuehrt zu `parent_child`; Direct Delivery ist verboten. |
| `mock-small-sizing` | Prueft die Sizing-Entscheidung fuer die Small Direct Spec. | Sizing bleibt `direct`; keine Child-Control-Artefakte. |
| `mock-large-session-chain` | Prueft automatische Child-Session-Kette. | `ML-C1` bis `ML-C5` starten/resumen sequenziell mit Handoff-Evidence. |
| `mock-large-artifact-e2e` | Prueft das echte Endartefakt. | `count.txt` existiert und enthaelt exakt `1\n2\n3\n4\n5\n`. |
| `mock-child-write-boundary` | Prueft Child-Verantwortung. | Jeder Child schreibt nur seine eigene Zahl und nur im Mock-Target. |
| `mock-small-direct-artifact` | Prueft den Direct-Pfad bis Artefakt. | `small-direct-result.json` existiert; keine Child Artefakte. |
| `mock-forbid-real-fixtures` | Verhindert Rueckfall auf reale Produktdaten. | KI-fuer-KMU-/Realprojekt-Pfade in Input, Output, Evidence oder Write-Set fuehren zu `fail`. |

## 5. Forbidden Real Fixture Policy

KI-fuer-KMU und andere reale Produkt-Specs duerfen fuer diese Mock-E2E-Suite nicht mehr verwendet werden.

Verboten:

- Default-Quelle `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs`.
- Kopieren realer KI-fuer-KMU-Specs in Mock-Fixtures.
- Positive Assertions gegen KI-fuer-KMU Child Index, Handoffs, Runtime-Dateien oder OpenSpec-Historie.
- Realprojekt-Pfade als Runtime-Target.
- "Compatibility mode" als Ersatz fuer Mock-E2E.

Erlaubt:

- Historische Docs duerfen in Retros erwaehnt werden.
- Alte KI-fuer-KMU-bezogene Runner duerfen nur noch entfernt, deaktiviert oder in explizit historische Archiv-/Retro-Dokumente verschoben werden.

Harness-Anforderung:

- Jeder Mock-E2E-Lauf muss `forbidden_source_paths` pruefen.
- Wenn ein verbotener Pfad in Fixture-Manifests, Agent Outputs, Evidence, Runtime-Targets oder Write-Sets auftaucht, muss der Test `fail` melden.

## 6. Testcase-Katalog

### MOCK-LARGE-E2E: Large-Spec-Pfad erzwingt Parent/Child Workflow

Zweck:

- Beweisen, dass der Workflow beim Large-Spec-Pfad vom Mock-Parent bis zum fertigen Artefakt laeuft: automatisch splitten, fuenf Child-Sessions sequenziell starten, jeden Child liefern und am Ende die gemeinsame Zaehldatei validieren.

Assertions:

- Mock-Sizing-Directive fuehrt zur Sizing-Entscheidung `parent_child`.
- Parent bleibt Control Layer.
- Child Index enthaelt genau `ML-C1` bis `ML-C5`.
- Alle fuenf Childs haben eigene Handoffs.
- `ML-C1` wird zuerst gestartet oder queued und im selben E2E-Lauf automatisch bis `ran-target` fortgesetzt.
- `ML-C2` bis `ML-C5` werden jeweils erst nach Closeout des Vorgaengers automatisch gestartet oder aus der Queue aufgenommen.
- Alle fuenf Child Deliveries enden mit `ran-target`.
- `mock-target/output/count.txt` enthaelt exakt `1\n2\n3\n4\n5\n`.
- Jeder Child schreibt nur seine eigene Zahl.
- Closeout-Evidence ist synchron.

### MOCK-SMALL-E2E: kleine Spec bleibt Direct Delivery

Zweck:

- Beweisen, dass der Workflow kleine Specs nicht unnoetig in Child Delivery zwingt.

Assertions:

- Sizing Gate entscheidet `direct`.
- Kein Child Index wird erzeugt.
- Keine Child Specs werden erzeugt.
- Keine Child Session Handoffs werden erzeugt.
- Keine Child Session wird gestartet oder queued.
- Erwarteter Direct Output stimmt mit Manifest.

### MOCK-FORBID-REAL-FIXTURE: reale Produktfixtures sind blockiert

Zweck:

- Beweisen, dass die Testsuite nicht wieder auf KI-fuer-KMU oder andere reale Produktartefakte zurueckfaellt.

Assertions:

- Verbotene Pfade in Source-Manifests fuehren zu `fail`.
- Verbotene Pfade in Agent Output fuehren zu `fail`.
- Verbotene Pfade in Target Workspace oder Write-Set fuehren zu `fail`.
- Der Default-Harness nutzt ausschliesslich `tests/docworkflow-agent-delivery/mock-data/**`.

### MOCK-MIGRATE-EXISTING-TESTS: vorhandene Tests laufen gegen Mockdaten

Zweck:

- Beweisen, dass die bestehende Agent Delivery Testsuite nicht nur neue Mockdaten erzeugt, sondern ihre bisherigen Standard-Gates auf die neue Testdatenbasis umgestellt hat.

Assertions:

- Standard-`all`-Runner verwenden keine KI-fuer-KMU-Quelle.
- L0/L1/L2/L3/Reporting-Checks referenzieren Mock-Manifeste, Mock-Handoffs, Mock-Summaries oder sind explizit non-gating/archiviert.
- Assertions pruefen die neuen erwarteten Outputs und Session-Evidence statt alter Realprojekt-Artefakte.
- Kein bestehender Standard-Gate kann gruen werden, wenn `forbidden_source_paths` verletzt wird.

### MOCK-SESSION-CHAIN: automatische Folge-Sessions sind beweisbar

Zweck:

- Beweisen, dass der Workflow nicht nur Handoff-Text erzeugt, sondern die naechsten Sessions automatisch startet oder in eine nachvollziehbare Queue stellt.

Assertions:

- Jede Folge-Session hat ein Launch-/Queue-Evidence-Artefakt.
- Handoff-Pfad und Target Child stimmen ueberein.
- Target Workspace ist isoliert.
- `manual_start_required` zaehlt nicht als positives E2E.
- Bei blockierten Starts ist der Blocker maschinenlesbar und verhindert Folge-Delivery.

## 7. Summary Artifact Contract

Jeder Mock-E2E-Lauf schreibt ein Summary-Artefakt:

- `tests/docworkflow-agent-delivery/e2e/evidence/<run-id>/mock-e2e-summary.json`

Mindestfelder:

| Feld | Erlaubte Werte / Bedeutung |
|---|---|
| `schema_id` | `docworkflow-agent-delivery-mock-e2e-summary.v1` |
| `fixture_id` | Mock-Fixture-ID |
| `spec_type` | `large-parent`, `small-direct` |
| `sizing_decision` | `parent_child`, `direct`, `blocked`, `failed` |
| `overall_workflow_status` | `pass`, `fail`, `blocked` |
| `session_chain_status` | `pass`, `fail`, `blocked`, `not_applicable` |
| `expected_outputs_status` | `pass`, `fail`, `blocked` |
| `forbidden_fixture_status` | `pass`, `fail` |
| `evidence_truth` | `ran-target`, `ran-rehearsal`, `blocked`, `failed` |
| `mock_target_root` | Absoluter Pfad im isolierten Run-Dir |
| `runner_mode` | `local-mock-session-runner` fuer den akzeptierten Basispfad, optional `live-agent` fuer spaetere Zusatzpfade |
| `session_strategy` | `auto-start-and-resume`, `direct-no-child-session` oder `negative-blocker` |
| `session_evidence` | Liste der Launch-/Queue-Evidence-Artefakte |
| `output_evidence` | Liste der validierten Output-Dateien |
| `forbidden_paths_checked` | Liste der geprueften verbotenen Pfade |

Ein Summary darf nur `overall_workflow_status: pass` melden, wenn:

- die erwartete Sizing-Entscheidung stimmt,
- die erwarteten Outputs validiert wurden,
- verbotene reale Fixtures nicht verwendet wurden,
- fuer `large-parent` alle fuenf Session-Schritte bis `ran-target` abgeschlossen sind,
- Blocker nur in expliziten negativen Testfaellen als erwartetes Ergebnis auftreten,
- keine nicht deklarierte Runtime- oder externe Infrastruktur verwendet wurde.

## 8. Verification Commands

Ausfuehrungskontext:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `zsh` oder `bash`; Skripte selbst deklarieren `#!/usr/bin/env bash`.
- Plattform: macOS primaer, Linux-kompatible Shell-/Node-Kommandos bevorzugt.
- Network: nicht erforderlich fuer deterministische Mock-Validatoren; Agent-Session-Starts duerfen eigene Auth-/Provider-Blocker maschinenlesbar melden.

Preflight nach Implementierung:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/*.sh
```

Zukuenftige Mock-E2E-Gates:

```sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh small --keep
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep
```

OpenSpec / Hygiene:

```sh
openspec validate docworkflow-agent-delivery-testsuite --strict
git diff --check
```

Command Contract:

- `run-mock-e2e-checks.sh large` muss die automatische Session-Launch-/Queue-Evidence pruefen.
- `run-mock-e2e-checks.sh small` muss pruefen, dass keine Child-Control-Artefakte entstehen.
- `run-mock-e2e-checks.sh all` darf nicht auf KI-fuer-KMU oder andere reale Produktfixtures zugreifen.
- `run-mock-e2e-checks.sh all --keep` muss im lokalen Mock Session Runner ohne Netzwerk, Docker oder Codex-Auth laufen.
- High-risk Live-Agent-Launcher-Kommandos sind nicht Teil des ersten akzeptierten Basispfads. Wenn sie spaeter dazukommen, muessen sie vor Implementation-Ready des Live-Slices durch `child-spec-hardening` rehearsed oder als blockierend markiert werden.

## 9. Decision Freeze Pack

Fuer den Folge-Change gelten diese Entscheidungen als eingefroren:

| Entscheidung | Wert | Darf im Folge-Change geaendert werden? |
|---|---|---|
| Fuehrende Testdatenquelle | `tests/docworkflow-agent-delivery/mock-data/**` | Nein, nicht ohne neue Spec. |
| KI-fuer-KMU als Fixture | verboten | Nein. |
| Large-Path Trigger | test-only `Mock Sizing Directive: force_parent_child` | Nur innerhalb Mock-E2E-Harnesses. |
| Large-Path Child-Anzahl | genau 5 Childs: `ML-C1` bis `ML-C5` | Nein. |
| Large-Path Endartefakt | `mock-target/output/count.txt` mit exakt `1\n2\n3\n4\n5\n` | Nein. |
| Small-Path Mode | `direct`, keine Child-Artefakte | Nein. |
| Akzeptierter Basispfad | `local-mock-session-runner` | Nein, Live-Agent nur zusaetzlich. |
| Externe Abhaengigkeiten | kein Netzwerk, kein Docker, keine Codex-Auth, kein manueller Session-Start fuer den Basispfad | Nein. |
| Standard-Gate-Ziel | `run-mock-e2e-checks.sh all --keep` | Nur wenn ein gleichwertiger Mock-E2E-Gate dokumentiert wird. |

Nicht eingefroren:

- interne Implementierungsdetails des lokalen Runners,
- JSON-Feldreihenfolge,
- genaue Run-ID- und Temp-Dir-Namen,
- ob einzelne vorgeschlagene Tests als separate Dateien oder gebuendelte Runner-Cases umgesetzt werden, solange die Assertions nachweisbar bleiben.

## 10. Acceptance Criteria

Die Mockdaten- und E2E-Harness-Erweiterung gilt als akzeptiert, wenn:

1. KI-fuer-KMU und andere reale Produkt-Specs nicht mehr als Testsuite-Fixtures verwendet werden.
2. Large-Path Mock Parent Spec und Small Mock Direct Spec source-controlled unter `tests/docworkflow-agent-delivery/mock-data/**` existieren.
3. Beide Mock-Specs haben Manifestdateien mit erwarteter Sizing-Entscheidung, erwarteten Outputs, verbotenen Pfaden und Session-Erwartungen.
4. Vorhandene Standard-Harnesses und Assertions sind auf Mockdaten migriert oder explizit aus dem Standard-Gate entfernt.
5. Neue Tests fuer Manifest-Schema, Large-Sizing, Small-Sizing, Session-Chain, Artefakt-E2E, Child-Write-Boundary, Small-Direct-Artefakt und Forbidden-Real-Fixtures existieren oder sind als bewusst gebuendelte Runner-Cases abgedeckt.
6. Der Large-Spec-E2E-Test beweist den kompletten Workflow von `mock-large-parent-spec.md` bis `mock-target/output/count.txt`.
7. Der Large-Spec-E2E-Test beweist `parent_child` Sizing per Mock-Sizing-Directive, Child Index, genau fuenf Child Specs, Handoffs, automatische Session Starts/Resumes, fuenf `ran-target` Child Deliveries, Closeout und die gemeinsame Zaehldatei mit `1` bis `5`.
8. Der Large-Spec-E2E-Test darf nicht erfolgreich sein, wenn irgendein Child dauerhaft `queued`, `manual_start_required`, `blocked`, `failed` oder nur `dry-run` bleibt.
9. Der Small-Spec-E2E-Test beweist `direct` Sizing, keine Child-Control-Artefakte, keine Child-Session und erwarteten Direct Output.
10. Session Launch/Queue Evidence ist maschinenlesbar und unterscheidet `started`, `queued`, `manual_start_required`, `blocked` und `failed`.
11. `manual_start_required` zaehlt nicht als positives E2E-Ergebnis.
12. Jeder E2E-Lauf schreibt ein Summary-Artefakt nach `docworkflow-agent-delivery-mock-e2e-summary.v1`.
13. Forbidden-Real-Fixture-Checks schlagen fehl, sobald KI-fuer-KMU-Pfade in Fixtures, Agent Output, Evidence, Target Workspace oder Write-Set erscheinen.
14. Alte KI-fuer-KMU-basierte Standard-Gates werden entfernt, ersetzt oder so deaktiviert, dass sie nicht mehr als Testsuite-Erfolgskriterium gelten.
15. `run-mock-e2e-checks.sh all --keep` ist der fuehrende reproduzierbare Workflow-E2E-Regressionstest.
16. Die Parent Testsuite Spec oder ihr Nachfolger dokumentiert die neue Mockdatenstrategie, die Migration bestehender Tests und den vollstaendigen Ausschluss realer Produktfixtures.
17. Der akzeptierte Basispfad nutzt `runner_mode: local-mock-session-runner` und braucht keine externe Agent-Auth, kein Netzwerk, kein Docker und keinen manuellen Session-Start.
18. Optionaler Live-Agent-/Codex-Pfad ist als Follow-up getrennt und darf die lokale Mock-E2E-Akzeptanz nicht blockieren.

## 11. Content Quality Review

Review-Ergebnis:

- Correctness/domain fit: Pass. Die Spec verschiebt den Testgegenstand weg von Produktdomäne und hin zum Agent Delivery Workflow.
- Necessity/scope: Pass. Mockdaten sind notwendig, damit E2E-Tests billig, reproduzierbar und eindeutig bleiben.
- Completeness: Pass fuer Spec-Ebene. Grosse und kleine Spec-Pfade, Migration bestehender Tests, neue Testvorschlaege, Session-Automation, Expected Outputs, forbidden real fixtures und Summary-Vertrag sind abgedeckt.
- Consistency: Pass. Die Spec widerspricht der bisherigen Testsuite nur bewusst dort, wo KI-fuer-KMU-Testdaten entfernt werden sollen.
- Testability: Pass. Die Akzeptanzkriterien sind ueber Mock-Manifeste, Output-Dateien, Session-Evidence, migrierte Assertions und Summary-Artefakte validierbar.
- Implementation planning readiness: Pass fuer `MD-E2E-1` bis `MD-E2E-3`. Der neue Runner-Command kann erst nach Implementierung rehearsed werden; dieses Rehearsal ist ein Closeout-Gate des Implementierungsslices, keine offene Produktentscheidung. Live-Agent-Integration bleibt expliziter Follow-up.
- Blocking Marker: Keine.

## 12. Mini-Retro

- Was wurde entschieden? Reale Produkt-Specs, insbesondere KI-fuer-KMU, duerfen nicht mehr als E2E-Testdatenquelle fuer den Agent Delivery Workflow dienen.
- Was wurde geaendert? Eine neue Mockdaten-Spec definiert grosse und kleine synthetische Specs, Migration vorhandener Tests, neue Mock-E2E-Tests, erwartete Outputs, Session-Automation-Evidence und forbidden-real-fixture Guards.
- Was bleibt offen? Die konkrete Implementierung der Mockdaten, des lokalen Mock Session Runners und der Standard-Gate-Migration erfolgt in einem Folge-Change; Live-Agent-Integration ist optionaler spaeterer Ausbau.
- Welche Evidenz/Verification fehlt? Functional Verification fehlt bis zur Implementierung; diese Spec definiert die spaeteren Gates.
- Welche Skill-/Workflow-Reibung ist aufgefallen? E2E-Tests brauchen bewusst langweilige Mock-Domaenen, sonst kippen sie in Produktentwicklung statt Workflow-Validierung.
- Session-/Kontextzustand: Spec authored; ready for review and later planning.

## 13. Delivery Orchestration Pack

Diese Spec ist ab 2026-05-09 als Parent-/Control-Spec fuer den Agent Delivery Workflow zu behandeln. Sie darf nicht direkt als ein einzelner `spec-change-delivery`-Slice umgesetzt werden, auch wenn Abschnitt 4.6 urspruenglich `MD-E2E-1` bis `MD-E2E-3` als zusammenhaengenden Folge-Change beschrieben hat. Das Spec Sizing Gate ist fuer diesen Scope aktiv: Mockdaten, Runner, Legacy-Gate-Migration, Dokumentationssync und optionaler Live-Agent-Pfad muessen getrennt orchestriert, gehaertet und erst danach einzeln geliefert werden.

Fuehrendes Orchestrierungsartefakt:

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`

Child Specs:

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-1 Mock Fixtures.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-2 Local Mock Session Runner.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-4 Documentation Sync.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-5 Live Agent Follow-up.md` bleibt optionaler Follow-up und ist nicht Teil des ersten lokalen Mock-E2E-Basispfads.

Operational rule:

- Jeder Child startet mit `child-spec-hardening`.
- `MD-E2E-1` und `MD-E2E-2` sind akzeptiert; ihre OpenSpec-Archive und Evidence-Pfade sind im Orchestration Pack verlinkt.
- `MD-E2E-3` ist der naechste fuehrende Child fuer `child-spec-hardening`.
- `spec-change-delivery` darf erst nach dokumentiertem Hardening-Verdict `IMPLEMENTATION READY` oder `READY WITH NON-BLOCKING NOTES` fuer genau einen weiteren Child starten.
- KI-fuer-KMU faellt vollstaendig aus den Standard-Testdaten heraus und darf nicht als Compatibility Fixture erhalten bleiben.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-09 | Codex | Initial spec drafted for mock data based Agent Delivery Workflow E2E harness and removal of real product fixtures. |
| 2026-05-09 | Codex | Refined large-path mock fixture to stay small, use a force-parent-child directive, create five child specs, and validate one shared count output from 1 to 5. |
| 2026-05-09 | Codex | Expanded scope to include migration of existing tests, new assertions, new mock-based test cases, and a full E2E path from parent spec to final count artifact. |
| 2026-05-09 | Codex | Hardened the spec with parent conformance, local mock session runner execution model, write-set boundaries, delivery slices, decision freeze pack, and stricter E2E acceptance gates. |
| 2026-05-09 | Codex | Added spec-orchestrator control layer, child spec pointers and explicit block against implementing this Parent Spec as one bounded delivery slice. |
| 2026-05-09 | Codex | Synchronized parent orchestration status after accepting and archiving MD-E2E-2 local mock runner evidence. |

SessionId: 2026-05-09-docworkflow-agent-delivery-mock-data-e2e-harness
