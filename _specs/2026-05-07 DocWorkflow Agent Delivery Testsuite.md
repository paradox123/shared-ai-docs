**Date:** 2026-05-07  
**Status:** 🟢 Accepted
**Scope:** Beweiskraeftige Testsuite fuer den shared-ai-docs Parent-/Child-Spec-Delivery-Workflow.

---

## Review Control Surface

- Spec-Variante: Parent/Master Spec fuer eine Testsuite mit Child-Slices.
- Goldstandard Status: accepted.
- Ziel: Die Testsuite soll nachweisbar pruefen, ob Codex eine grosse Parent/Master Spec automatisch als zu gross erkennt, die Parent Spec als Kontrollschicht erhaelt, Child Specs/Skeletons mit Child Index erzeugt, jeden Child streng hardenet, frische Child-Delivery-Handoffs nutzt, nach Closeout Parent/Index/Evidence/OpenSpec synchronisiert und erst dann kontrolliert den naechsten Child freigibt.
- In Scope: Testlevel L0-L3, Skill-Unit-Tests, Skill-Chain-/Teil-E2E-Tests, Runtime-E2E-Pfade in Temp-Repos, Style-/Usability-Gates, Effizienz-/Telemetry-Gates, Automation-first Harness-Anforderungen, Framework-first-Research, Fixture- und Testisolation, Parent-only Orchestration-Fixtures, Spec-Sizing-Gate, Parent-Control-Layer-Erhalt, Child-Schnitt, operativer Child Index, Child-Hardening-Gates, persistierte Child Session Handoffs, Single-Child-Delivery-Gates, Closeout-Sync, Next-Child-Abbruch, Evidence-Artefakte, klare Automatisierungsgrenzen.
- Out of Scope: Aenderungen an KI-fuer-KMU-Originalspecs, pauschale Legacy-Migrationen, Runtime-Implementierung ausserhalb von Temp-Repos, vollstaendige Agent-Runner-Implementierung in dieser Spec, agentische Vollausfuehrung der gesamten Testsuite als Standardpfad.
- Wichtigste Test-/Harness-Cases: Child-Slices `DWT-S0` bis `DWT-S5`; Skill-Unit-Tests fuer `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout`; `TC1D oversized parent does not enter direct implementation`, `TC1A Parent-only orchestration produces child control surface`, `TC1B plausible child skeleton cannot become ready`, `TC1C ready child requires validator and high-risk command rehearsal`, `TC1E orchestration plus hardening produces readiness matrix`, `TC2A ready child delivery kickoff is temp-repo only`, `TC2B after S3 closeout DWT-S5 remains blocked`, `TC2C stale next handoff blocks`, `TC2D parent coverage cannot disappear during closeout`, `DWT-S5-L3A` through `DWT-S5-L3F` runtime-temp-repo pilot gates, Style-/Usability-Gates und Effizienz-/Telemetry-Gates.
- Wichtigste Verification Commands: `bash -n tests/docworkflow-agent-delivery/scripts/*.sh`; `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all`; `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all --keep`; `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh all --keep`; `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh all --keep`; `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all --keep`; retained DWT-S5 post-archive `ran-target` evidence assertion; `openspec validate docworkflow-agent-delivery-testsuite --strict`; `git diff --check`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen fuer die Spec. Framework-ADR wurde durch `DWT-S0` mit `ADOPT_WITH_LIMITATIONS` re-evaluiert; Promptfoo bleibt primaerer Agent-/Coding-Agent-Eval-Rahmen, braucht aber explizite Codex-Auth-Provisionierung und stabile npm-/Registry-Connectivity. Inspect AI bleibt strategischer Fallback, wird aber nicht als naechster Pfad aktiviert. .NET 10 file-based Apps bleiben eine bevorzugte Option fuer kleine deterministische Harness-Hilfen.
- Readiness Status: Parent Spec accepted and closed as the completed control layer for `DWT-S0` through `DWT-S5`. All child slices are accepted, archived, evidence-synchronized, and no descendant child or follow-up scope is released by this parent closeout.

## Session Briefing

- Modus/Skill: `doc-coauthoring` mit anschliessendem `doc-review-autoresolve`.
- Source of Truth: diese Spec, `docs/doc-workflow.md`, `skills-repo/skills/spec-orchestrator/SKILL.md`, `skills-repo/skills/child-spec-hardening/SKILL.md`, `skills-repo/skills/spec-change-delivery/SKILL.md`, `skills-repo/skills/spec-closeout/SKILL.md`, bestehende Harness-Artefakte unter `tests/docworkflow-agent-delivery/`.
- Ziel: Anforderungen fuer eine mehrstufige Testsuite buendeln, die einzelne Skills, Skill-Folgen, Teil-Ende-zu-Ende-Prozesse, Output-Style und Agent-Effizienz prueft.
- Nicht-Ziele: keine Runtime-Delivery im echten KI-fuer-KMU-Repo, keine Migration historischer Specs, keine stillen positiven Fixture-Normalisierungen als Beweis, kein Agent-only-Testlauf als Default.
- In Scope: Testlevel, Testcases, Assertions, Evidence, Dry-Run-Grenzen, negative Fixtures und spaetere Automatisierungsstrategie.
- Erwarteter Output: eine accepted/closed Parent Testsuite-Spec im shared-ai-docs `_specs`-Ordner.
- Verification/Review: Parent closeout replay gegen die zwei Kernfragen, Child evidence/archive sync und die DocWorkflow-Gates.
- Offene Entscheidungen: Keine fuer den Parent-Abschluss. DWT-S0 bestaetigt Promptfoo mit Limitierungen als primaeren Eval-Rahmen; Inspect AI bleibt strategischer Fallback, wird aber nicht als neuer Scope freigegeben.

## 1. Workflow Vision

Wenn Codex eine grosse Parent/Master Spec erhaelt, soll Codex automatisch erkennen, dass sie zu gross fuer eine stabile Single-Session-Umsetzung ist. Der Workflow darf dann nicht versuchen, die Parent Spec in einem Rutsch zu implementieren. Er muss stattdessen diesen Ablauf erzwingen:

1. Parent Spec als Scope- und Kontrollschicht erhalten.
2. Child Specs oder Child-Skeletons schneiden.
3. Operativen Child Index fuehren.
4. Jeden Child bis zu einem strengen `IMPLEMENTATION READY` hardenen.
5. Pro Child eine frische Implementierungs-Session mit persistiertem Child Session Handoff ermoeglichen.
6. Nach Implementierung/Closeout Parent Coverage, Child Index, Backlog/Re-entry, Evidence Links und OpenSpec Status synchronisieren.
7. Danach den naechsten Child kontrolliert freigeben.

Diese Spec definiert Tests nicht als reine Dokument-/Schema-Pruefung, sondern als Evidence-System fuer diese Vision. Ein Test ist nur dann beweiskraeftig, wenn er zwischen "vorhandene Artefakte sehen plausibel aus" und "der Workflow hat den erlaubten naechsten Schritt tatsaechlich korrekt erzeugt oder blockiert" unterscheidet.

## 2. Problem

Die aktuelle Testsuite unter `tests/docworkflow-agent-delivery/` ist als erster Contract-Smoke-Test nuetzlich, beantwortet aber die zwei wichtigsten Erkenntnisfragen noch nicht belastbar:

1. Entsteht aus einem Parent-only-Start wirklich ein Child-Schnitt mit Child Specs, Child Index, Coverage Matrix, Hardening Queue und mindestens einem implementation-ready Child?
2. Bricht der Workflow nach einer abgeschlossenen Child-Delivery wirklich ab, wenn der naechste Child noch nicht implementation-ready ist?

Der aktuelle Harness bestaetigt vor allem bereits vorhandene KI-fuer-KMU-Artefakte. Das ist als Regression Gate wertvoll, darf aber nicht als Beweis fuer Agent-Orchestration oder post-closeout Next-Child-Gating gelten.

## 3. Zielbild

Die Testsuite wird in Level geschnitten:

| Level | Name | Zweck | Beweiskraft |
|---|---|---|---|
| L0 | Static Contract Smoke | Bestehende Specs, Index, Handoffs und Skills auf harte Contract-Regeln pruefen. | Niedrig bis mittel; Regression gegen bekannte Artefakte. |
| L1 | Fixture Transformation Checks | Aus minimalen oder absichtlich defekten Fixtures erwartete Gate-Ergebnisse maschinell pruefen. | Mittel; beweist negative und positive Gate-Logik ohne Agent-Runner. |
| L2 | Agentic Dry-Run Harness | Agent erzeugt Orchestration-/Hardening-/Closeout-Artefakte; Harness validiert diese Outputs. | Hoch fuer Workflow-Verhalten, solange Runtime nicht im Scope ist. |
| L3 | Runtime Temp-Repo Delivery | Eine Child-Delivery laeuft gegen eine Temp-Repo-Kopie mit lokalen und Container-/Harness-Gates. | Hoch fuer End-to-End-Delivery, teuer und nur fuer ausgewaehlte Slices. |

Die vorhandene Suite wird als L0 eingeordnet. Die naechste Ausbaustufe soll als Child-Slices geplant werden: zuerst Framework-Spike und L1 deterministische Gates, danach L2 Agentic Dry-Run und zuletzt ausgewaehlte L3 Runtime-Temp-Repo-Delivery. L3 bleibt bewusst spaeter, weil dafuer Runtime-Fixtures und echte Delivery-Gates stabil sein muessen.

Die L0-L3-Level beschreiben Beweiskraft und Automatisierungstiefe. Zusaetzlich braucht die Testsuite fachliche Testarten, damit ein schneller Skill-Unit-Test nicht mit einem Teil-E2E-Prozesstest oder einem Style-/Effizienz-Gate verwechselt wird.

## 4. Delivery Orchestration Pack

Das Spec Sizing Gate feuert fuer die Umsetzung dieser Testsuite: Die Spec umfasst Framework-Spike, deterministische Validatoren, agentische Dry-Runs, Runtime-Temp-Repos, Evidence-/Telemetry-Vertraege und Style-/Usability-Gates. Diese Parent Spec bleibt deshalb die Kontrollschicht. Die Umsetzung darf nicht als ein einzelner breiter Change geplant oder implementiert werden.

### Parent Requirements

| Requirement | Zusammenfassung | Fuehrende Evidence |
|---|---|---|
| `DWT-PR1` | Parent-first Orchestration: Grossspecs werden nicht direkt implementiert, sondern erzeugen Child-Schnitt, Child Index, Coverage Matrix, Dependencies und Hardening Queue. | `TC1D`, `TC1A`, `TC1E` |
| `DWT-PR2` | Child-Hardening-Gate: Kein Skeleton wird durch Plausibilitaet ready; `IMPLEMENTATION READY` braucht Parent Conformance, Write-Set, Handoff, Validator und Verification-/Rehearsal-Vertrag. | `TC1B`, `TC1C`, `TC1E` |
| `DWT-PR3` | Single-Child Delivery: Delivery nutzt nur aktuelles Handoff, gueltigen Index, eigenes Verdict, erlaubtes Write-Set und Temp-Repo. | `TC2A`, `TC2C` |
| `DWT-PR4` | Closeout und Next-Child-Gate: Closeout synchronisiert Parent/Index/Evidence/OpenSpec/Handoff; der naechste Child wird nur durch seinen eigenen Status freigegeben. | `TC2B`, `TC2D` |
| `DWT-PR5` | Evidence Integrity: Tests duerfen keine gruenen Ergebnisse durch statische Plausibilitaet, Fixture-Normalisierung, alte Outputs oder Workarounds erzeugen. | Harness-Artefaktvertrag, L2 Agent Output Contract, TC1E, TC2B |
| `DWT-PR6` | Framework Reuse: Promptfoo-first Spike validiert den Agent-/Coding-Agent-Eval-Rahmen; Inspect AI ist Fallback; Eigenbau bleibt blockiert, bis beide untragfaehig belegt sind. | ADR-Re-Evaluation-Artefakt |
| `DWT-PR7` | Style und Efficiency: Outputs muessen fuer Mensch/Folgeskill nutzbar sein und Command-/Tool-/Read-Drift sichtbar machen. | `TCQ1`, `TCE1`, `agent-run-manifest.json` |

### Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DWT-S0 | `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S0 Framework Spike.md` | `DWT-PR6`, supports `DWT-PR5` | `ACCEPTED`; was `IMPLEMENTATION READY`; result `ADOPT_WITH_LIMITATIONS` | `child-session-handoffs/dwt-s0-session-handoff.md` | `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/`; canonical `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` | ADR plus this Parent Spec | `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S0 Framework Spike.md`; `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`; `_specs/2026-05-07 DocWorkflow Agent Test Framework Evaluation ADR.md`; `_specs/child-session-handoffs/dwt-s0-session-handoff.md`; `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/**`; `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`; `tests/docworkflow-agent-delivery/spikes/dwt-s0/**`; `/tmp/docworkflow-agent-delivery-dwt-s0.*` | Closeout replay in `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/closeout-verification.txt`; Promptfoo `0.121.9` debug/config/eval; deterministic summary assertion; OpenSpec validate/archive; readiness validator | `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json`; ADR re-evaluation `ADOPT_WITH_LIMITATIONS`; OpenSpec archived | Later slices must explicitly provision Codex auth or equivalent credentials and account for intermittent npm registry/network connectivity; no Inspect fallback needed now | `spec-change-delivery` complete; DWT-S0 closed; harden `DWT-S1` next with Promptfoo primary and limitations |
| DWT-S1 | `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S1 L1 Deterministic Harness.md` | `DWT-PR1`, `DWT-PR2`, `DWT-PR5`; records `DWT-S0` `ADOPT_WITH_LIMITATIONS` as context only | `ACCEPTED`; was `IMPLEMENTATION READY` | `child-session-handoffs/dwt-s1-session-handoff.md` | `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness/`; canonical `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` | `DWT-S0` accepted with limitations; current L0 harness | `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S1 L1 Deterministic Harness.md`; `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`; `_specs/child-session-handoffs/dwt-s1-session-handoff.md`; `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness/**`; `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`; `tests/docworkflow-agent-delivery/l1/**`; `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh`; `tests/docworkflow-agent-delivery/README.md`; `tests/docworkflow-agent-delivery/testcases/tc1-parent-first-orchestration-child-hardening.md` | Closeout replay passed: L1 syntax; L1 all; L0 all; OpenSpec canonical validate; readiness validator; no agent runner required | Retained L1 summary `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.bMyVlu/evidence/l1-summary.json`; OpenSpec archived; canonical spec updated | Defers L2 agent execution to `DWT-S2`; S3/S5 remain dependency-blocked; DWT-S4 uses L1 summary schema baseline | `spec-change-delivery` complete; closed by `spec-closeout`; DWT-S4 is now hardened for reporting contract delivery; DWT-S2/S3/S5 remain unreleased |
| DWT-S2 | `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S2 L2 Parent-first Orchestration Agent Harness.md` | `DWT-PR1`, `DWT-PR2`, `DWT-PR5`, `DWT-PR7` | `IMPLEMENTATION READY`; accepted by closeout; real Promptfoo/Codex proof `ran-target` passed | `child-session-handoffs/dwt-s2-session-handoff.md` | `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness/`; canonical `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` | `DWT-S0` accepted `ADOPT_WITH_LIMITATIONS`; `DWT-S1` accepted deterministic L1 baseline; `DWT-S4` accepted reporting contract | `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S2 L2 Parent-first Orchestration Agent Harness.md`; `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`; `_specs/child-session-handoffs/dwt-s2-session-handoff.md`; `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness/**`; `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`; `tests/docworkflow-agent-delivery/l2/parent-first/**`; `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh`; `tests/docworkflow-agent-delivery/README.md`; `tests/docworkflow-agent-delivery/testcases/tc1-parent-first-orchestration-child-hardening.md` | Closeout replay passed: retained S0/S1/S4/S2 JSON; script syntax; bundled Node; DWT-S2 L2 `all --keep`; reporting all; L0 all; OpenSpec validates; readiness validator; `git diff --check` | Retained accepted L2 summary `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-l2-summary.json`; agent proof `runner_mode: promptfoo-codex`, `agent_execution_status: ran-target`, `overall_agent_proof_status: pass`; OpenSpec archived | Fallback artifact mode remains available for deterministic/blocker checks but cannot replace accepted agent proof; DWT-S3 and DWT-S5 were not released by DWT-S2; later child rows govern current release state | `spec-change-delivery` and `spec-closeout` complete for DWT-S2; DWT-S3 proceeded through its own child spec, handoff and verification gates; DWT-S5 state is governed by its own row |
| DWT-S3 | `_specs/2026-05-08 DocWorkflow Agent Delivery Testsuite DWT-S3 L2 Single-Child Delivery Closeout Gate Harness.md` | `DWT-PR3`, `DWT-PR4`, `DWT-PR5`, `DWT-PR7` | `ACCEPTED`; was `IMPLEMENTATION READY`; real Promptfoo/Codex proof `ran-target` passed | `child-session-handoffs/dwt-s3-session-handoff.md` | `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness/`; canonical `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` | `DWT-S0` accepted `ADOPT_WITH_LIMITATIONS`; `DWT-S1` accepted deterministic L1 baseline; `DWT-S2` accepted real Promptfoo/Codex `ran-target` proof; `DWT-S4` accepted reporting contract | `_specs/2026-05-08 DocWorkflow Agent Delivery Testsuite DWT-S3 L2 Single-Child Delivery Closeout Gate Harness.md`; `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`; `_specs/child-session-handoffs/dwt-s3-session-handoff.md`; `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness/**`; `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`; `tests/docworkflow-agent-delivery/l2/single-child-closeout/**`; `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh`; `tests/docworkflow-agent-delivery/README.md`; `tests/docworkflow-agent-delivery/testcases/tc2-single-child-delivery-next-handoff.md` | Closeout replay passed: retained DWT-S2 and DWT-S3 JSON/manifest assertions; script syntax for L0/L1/S2/S3/S4; bundled Node; DWT-S3 L2 fallback `all --keep`; DWT-S3 L2 Promptfoo/Codex `DWT_S3_ENABLE_AGENT=1 ... all --keep`; reporting all; L0 all; pre-archive DWT-S3 OpenSpec validate; OpenSpec archive; post-archive canonical OpenSpec validate; `git diff --check` | Retained accepted DWT-S2 summary `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-l2-summary.json`; retained accepted DWT-S3 summary `tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/dwt-s3-l2-summary.json`; DWT-S3 agent proof `runner_mode: promptfoo-codex`, `agent_execution_status: ran-target`, `overall_agent_proof_status: pass`; OpenSpec archived | Runtime proof belongs to `DWT-S5`; fallback artifact mode remains deterministic/blocker evidence only; DWT-S5 release is governed by its own child spec, handoff and validator gates | `spec-closeout` complete for DWT-S3; DWT-S5 has completed `child-spec-hardening`; start implementation only from the DWT-S5 row and handoff |
| DWT-S4 | `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S4 Summary Telemetry Style Reporting Contract.md` | `DWT-PR5`, `DWT-PR7` | `ACCEPTED`; was `IMPLEMENTATION READY` | `child-session-handoffs/dwt-s4-session-handoff.md` | `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s4-reporting-telemetry-contract/`; canonical `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` | `DWT-S1` accepted L1 summary schema baseline `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.bMyVlu/evidence/l1-summary.json`; no S2/S3/S5 release | `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S4 Summary Telemetry Style Reporting Contract.md`; `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`; `_specs/child-session-handoffs/dwt-s4-session-handoff.md`; `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s4-reporting-telemetry-contract/**`; `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`; `tests/docworkflow-agent-delivery/reporting/**`; `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh`; `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`; `tests/docworkflow-agent-delivery/README.md`; `tests/docworkflow-agent-delivery/testcases/tcq1-style-usability-gate.md`; `tests/docworkflow-agent-delivery/testcases/tce1-efficiency-telemetry-gate.md` | Closeout replay passed: retained baseline presence/JSON; reporting syntax; reporting all; L0 all with reporting; pre-archive OpenSpec change validate; post-archive canonical OpenSpec validate; pre-closeout readiness validator | Retained DWT-S1 summary baseline; DWT-S4 reporting fixtures/validator/runner implemented; retained reporting evidence `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-reporting.CA7ryD/evidence/dwt-s4-reporting-summary.json`; OpenSpec archived and canonical spec updated | Feed required report fields to S2/S3 only through later orchestrator or implementation sync; DWT-S2/DWT-S3/DWT-S5 remain unreleased by DWT-S4 | `spec-change-delivery` complete; closed by `spec-closeout`; next child still requires its own hardening/handoff |
| DWT-S5 | `_specs/2026-05-08 DocWorkflow Agent Delivery Testsuite DWT-S5 L3 Runtime Temp-Repo Delivery Pilot.md` | `DWT-PR3`, `DWT-PR4`, `DWT-PR5` | `ACCEPTED`; was `IMPLEMENTATION READY`; real Promptfoo/Codex proof `ran-target` passed | `child-session-handoffs/dwt-s5-session-handoff.md` | `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot/`; canonical `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` | `DWT-S3` accepted real Promptfoo/Codex `ran-target` proof; DWT-S5 synthetic runtime fixture and retained target proof complete | `_specs/2026-05-08 DocWorkflow Agent Delivery Testsuite DWT-S5 L3 Runtime Temp-Repo Delivery Pilot.md`; `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`; `_specs/child-session-handoffs/dwt-s5-session-handoff.md`; `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot/**`; `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`; `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/**`; `tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh`; `tests/docworkflow-agent-delivery/README.md`; `tests/docworkflow-agent-delivery/testcases/tc2-single-child-delivery-next-handoff.md` | Closeout replay passed: DWT-S5 syntax; DWT-S5 preflight; DWT-S5 fallback `all --keep`; retained DWT-S5 `ran-target` summary assertion; reporting all; L0 all; pre-archive active OpenSpec validate; OpenSpec archive; post-archive canonical OpenSpec validate; DWT-S5 readiness validator; `git diff --check`. | Retained DWT-S5 target evidence `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/evidence/2026-05-08-ran-target/dwt-s5-l3-summary.json`; retained blocked-runtime rehearsal evidence `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/evidence/2026-05-08-blocked-runtime/dwt-s5-l3-summary.json`; accepted predecessor evidence `tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/dwt-s3-l2-summary.json`; OpenSpec archived | Fallback/blocker mode remains available for deterministic regression checks but cannot replace target proof; no KI-fuer-KMU original repo may be named as runtime target or modified | `spec-change-delivery` and `spec-closeout` complete for DWT-S5; no descendant child is released |

### Hardening Queue and Execution Order

1. `DWT-S0` is accepted and archived with `ADOPT_WITH_LIMITATIONS`; Promptfoo remains the primary framework path with explicit auth and network/connectivity limitations.
2. `DWT-S1` follows to make deterministic artifact checks real before agent outputs can claim workflow proof.
3. `DWT-S2` and `DWT-S3` must stay separate: parent-first orchestration proof and post-closeout next-child proof answer different questions and have different fixture states.
4. `DWT-S4` can be implemented in parallel with `DWT-S2` only inside its reporting/schema/style/telemetry write-set, and only if one integration owner owns shared summary/output contracts before S2 consumes those fields.
5. `DWT-S5` may start only after its own child spec, handoff, concrete write-set, OpenSpec change, readiness validator and retained DWT-S3 evidence checks pass. Runtime and Docker/container proof are DWT-S5 delivery obligations, not hardening proof.

`DWT-S0`, `DWT-S1`, `DWT-S2`, `DWT-S3`, `DWT-S4` and `DWT-S5` are accepted and closed. `DWT-S2` supplies the accepted L2 parent-first orchestration proof with real Promptfoo/Codex `ran-target` evidence. `DWT-S3` supplies the accepted L2 single-child delivery/closeout proof with retained Promptfoo/Codex `ran-target` evidence. `DWT-S5` supplies the accepted L3 runtime temp-repo proof with retained Promptfoo/Codex `ran-target` evidence and no descendant child release.

## 5. Testarten und Ausbau-Stufen

| Testart | Zweck | Typische Frage | Erste Umsetzung |
|---|---|---|---|
| Skill Unit | Einen einzelnen Skill isoliert gegen ein Input-Fixture pruefen. | Produziert der Skill fuer diesen Input das erwartete Ergebnis und blockiert er falsche Ergebnisse? | L1 mit statischen oder agent-output-basierten Assertions, danach L2 mit Runner. |
| Skill Chain / Integration | Zwei oder mehr Skills in definierter Reihenfolge pruefen. | Baut der Output des ersten Skills korrekt auf den Input des Folgeskills auf? | L2 mit Agent Output Contract. |
| Teil-E2E Workflow | Einen laengeren Workflow ohne echte Runtime-Implementation pruefen. | Laeuft Parent-Orchestration -> Hardening -> Delivery-Kickoff/Closeout-Gate korrekt? | L2 mit synthetischer Evidence und Temp-Fixtures. |
| Runtime E2E | Eine echte Child-Delivery in Temp-Repo/-Worktree pruefen. | Funktioniert die Implementation plus lokale und Container-/Harness-Verifikation? | L3, nur fuer ausgewaehlte Slices. |
| Style / Usability Gate | Output auf Nutzbarkeit fuer Mensch und Folgeskill pruefen. | Kann der User oder naechste Skill den Output schnell und sicher verwenden? | Quer-Gate fuer Skill Unit, Chain und E2E. |
| Efficiency / Telemetry Gate | Agent-Verhalten auf unnoetige Kommandos, Umwege und Token-/Tool-Budget pruefen. | Kommt der Agent mit angemessenem Tooling und ohne Such-/Token-Drift zum Ergebnis? | Erst warnend, spaeter budgetiert failend. |

### Skill Unit Test Contract

Ein Skill-Unit-Test hat genau einen fuehrenden Skill und einen klaren erwarteten Output. Er darf nicht still auf spaetere Skills ausweichen.

Mindestfelder:

| Feld | Bedeutung |
|---|---|
| `skill_under_test` | z. B. `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout`. |
| `input_fixture` | Temp-Fixture oder synthetisches Fixture mit manifestiertem Startzustand. |
| `prompt_contract` | Der genaue Arbeitsauftrag, inklusive erlaubter und verbotener Aktionen. |
| `expected_output_contract` | Erwartete Artefakte, Statuswerte, Tabellen, Handoffs, Blocker oder Next Action. |
| `forbidden_outputs` | Dinge, die nicht passieren duerfen, z. B. Runtime-Edit, Parent-as-Child-Delivery, stilles Ready. |
| `assertions` | Maschinenlesbare Checks gegen Output und Artefakte. |
| `style_gate` | Lesbarkeit, Review Control Surface, Handoff-Nutzbarkeit und Struktur. |
| `efficiency_gate` | Command-/Tool-/Token-Budget und Umweg-Indikatoren. |

Erste Skill-Unit-Tests:

| Skill | Input | Erwartetes Ergebnis |
|---|---|---|
| `spec-orchestrator` | Parent-only Grossspec | Spec Sizing Gate feuert, Child-Schnitt/Index/Coverage/Hardening Queue entstehen, keine Runtime-Implementation. |
| `child-spec-hardening` | duenner Child-Skeleton | `NEEDS HARDENING` oder sync/blocking Verdict, kein stilles `IMPLEMENTATION READY`. |
| `child-spec-hardening` | hardenbarer Child plus Parent/Index | Readiness Matrix, konkreter Verdict, Handoff/Index-Sync oder klarer Blocker. |
| `spec-change-delivery` | not-ready Child mit Handoff-Versuch | `NOT READY`, keine Runtime-Edits. |
| `spec-closeout` | synthetische S3-Evidence plus not-ready next-child fixture | S3-Sync wird erzeugt, der not-ready Folge-Child bleibt blockiert. |

### Skill Chain / Teil-E2E Contract

Skill-Chain-Tests pruefen Reihenfolge und Artefaktuebergabe:

1. `spec-orchestrator` erzeugt Child-Schnitt, Child Index, Coverage Matrix, Dependencies und Hardening Queue.
2. `child-spec-hardening` nutzt diese Artefakte und erzeugt Readiness Matrix plus Handoff-/Index-Sync.
3. `spec-change-delivery` akzeptiert nur implementation-ready Children und blockiert alle anderen.
4. `spec-closeout` synchronisiert Parent Coverage, Child Index, Backlog/Re-entry, Evidence Links, OpenSpec Status und naechstes Handoff.

Ein Chain-Test ist nur bestanden, wenn der Folgeschritt nicht aus alten Fixtures liest, sondern nachweisbar den Output des vorherigen Schritts als Input verwendet. Das Evidence-Artefakt muss die Input-/Output-Pfade pro Schritt nennen.

### Style / Usability Gate

Style ist hier kein kosmetisches Gate. Es prueft, ob Output fuer den User und fuer Folgeskills praktisch nutzbar ist.

Mindestchecks:

- Review Control Surface oder passendes Kurzbriefing ist vorhanden und synchron mit Details.
- Next Action ist eindeutig und nennt genau einen fuehrenden Skill oder einen klaren Blocker.
- Blocker, offene Entscheidungen und nicht ausgefuehrte Verification sind oben sichtbar, nicht nur tief im Dokument.
- Child Index, Handoff und Evidence Links sind auffindbar und konsistent benannt.
- Output enthaelt keine grossen unstrukturierten Textbloecke, wenn Tabellen, JSON oder Checklisten erwartet werden.
- Handoff ist frisch genug, dass eine neue Session ohne Chat-Kontext starten kann.
- Fuer Mensch und Folgeskill sind Scope, Non-Goals, Allowed Write-Set, Shared/Read-only Files, Verification Commands und Evidence getrennt lesbar.

Style-Gates koennen initial als `warn` laufen, muessen fuer Handoff- und Child-Index-Artefakte aber spaeter failend werden.

### Efficiency / Telemetry Gate

Effizienztests pruefen nicht, ob der Agent "maximal billig" arbeitet. Sie pruefen, ob der Agent ohne vermeidbare Umwege arbeitet und sich nicht in Tooling oder Kontextsuche verliert.

Jeder L2/L3-Lauf soll ein `agent-run-manifest.json` oder gleichwertiges Evidence-Artefakt erzeugen:

| Feld | Zweck |
|---|---|
| `tool_calls_total` | Grobe Tool-Aktivitaet. |
| `shell_commands` | Liste der ausgefuehrten Shell-Kommandos. |
| `files_read` | Gelesene Dateien oder Pfadmuster. |
| `files_written` | Geschriebene Artefakte. |
| `repeated_reads` | Wiederholte Reads derselben Datei ohne neuen Grund. |
| `broad_scans` | Breite Scans wie repo-weites `find`/`rg` mit Zweckangabe. |
| `blocked_or_failed_commands` | Fehlgeschlagene oder blockierte Commands mit Grund. |
| `approx_input_tokens` und `approx_output_tokens` | Optional, wenn Runner diese Werte liefern kann. |
| `efficiency_verdict` | `pass`, `warn` oder `fail`. |

Erste Effizienz-Heuristiken:

- Skill-Unit-Tests haben ein kleines Command-Budget und duerfen keine Runtime-/Docker-Commands ausfuehren, wenn der Skill nur Spec-Artefakte pruefen soll.
- Chain-/Teil-E2E-Tests duerfen breitere Reads verwenden, muessen aber Source-of-Truth-Dateien bevorzugen und Suchwege dokumentieren.
- Wiederholte identische Datei-Reads, breit gestreute Suche ohne Zweck, nicht benoetigte Docker-/Build-Commands oder Runtime-Edits in Spec-only-Tests erzeugen mindestens `warn`.
- Ein Test darf `fail` werden, wenn verbotene Commands ausgefuehrt wurden, z. B. Runtime-Implementation im Parent-Sizing-Test oder Docker im reinen Skill-Unit-Hardening-Test.

Solange kein Runner echte Tokenwerte liefert, nutzt das Gate Proxy-Metriken: Tool-Call-Anzahl, Shell-Command-Anzahl, Dateiread-Anzahl, wiederholte Reads und verbotene Command-Klassen.

## 6. Automation, Isolation und Framework Reuse

Die Testsuite soll nicht standardmaessig vollstaendig von einem Agenten manuell ausgefuehrt werden. Der Default ist automation-first:

1. Fixtures werden reproduzierbar aufgebaut.
2. Agenten werden nur dort eingesetzt, wo ihr Verhalten selbst Testgegenstand ist, z. B. L2 Agentic Dry-Run.
3. Agent-Outputs werden als Artefakte gespeichert.
4. Maschinenlesbare Harnesses pruefen die Artefakte deterministisch.
5. Evidence und Telemetry werden versionierbar oder mindestens pfadstabil abgelegt.

### Testisolation

Jeder Test muss isoliert laufen koennen:

- Originalspecs und Runtime-Repositories bleiben read-only.
- Jeder Test nutzt eine eigene Temp-Fixture oder einen eindeutig isolierten Fixture-Workspace.
- Fixture-Normalisierung muss im Fixture-Manifest sichtbar sein.
- Tests duerfen keine implizite Reihenfolge benoetigen, ausser ein Skill-Chain-Test dokumentiert seine Vorgaenger-Outputs explizit als Input.
- Testdaten, Evidence und Telemetry duerfen parallele oder wiederholte Testlaeufe nicht gegenseitig ueberschreiben.
- Ein Test muss nach Cleanup oder mit retained Fixture reproduzierbar wiederholbar sein.
- Runtime-E2E-Laeufe duerfen nur in Temp-Repos, Temp-Worktrees oder gleichwertig isolierten Umgebungen schreiben.

### Framework-first Decision

Die Framework-Recherche wurde in `_specs/2026-05-07 DocWorkflow Agent Test Framework Evaluation ADR.md` durchgefuehrt. Ergebnis: Promptfoo ist der primaere Rahmen fuer einen einmaligen Pre-Implementation-Spike; Inspect AI ist strategischer Fallback und Ergaenzungskandidat.

Die spaetere Planung muss deshalb nicht bei einer offenen Framework-Suche starten, sondern vor der eigentlichen Testsuite-Implementierung einen Promptfoo-first Spike als Vorbedingung durchfuehren:

1. Kann Promptfoo Codex-Skill-Ausfuehrung ueber OpenAI Codex SDK, Codex app-server/Desktop oder einen Adapter stabil treiben?
2. Sind Temp-Fixtures, read-only Source-Fixtures und gespeicherte Agent-Outputs reproduzierbar abbildbar?
3. Lassen sich Skill-Unit-, Skill-Chain-, Style- und Efficiency-Gates als Promptfoo-Assertions oder als integrierte nachgelagerte Validators auswerten?
4. Falls nein, wird Inspect AI als erster Fallback fuer Agent-/Sandbox-/External-Agent-Evals geprueft.

Rahmenentscheidung:

- Promptfoo-first fuer den Pre-Implementation-Framework-Spike und, bei erfolgreicher Re-Evaluation, fuer Agent-/Coding-Agent-Evals.
- Inspect-AI-Fallback, wenn Promptfoo fuer Codex-Skill-/Desktop-Anbindung blockiert.
- mcp-eval nur fuer zukuenftige MCP-spezifische Tests.
- Bestehende Frameworks haben Vorrang vor einem selbstgebauten Testing Framework.
- .NET 10 file-based Apps sind eine bevorzugte Option fuer kleine, reproduzierbare Harness-Hilfen, wenn das Framework Luecken bei deterministischen Artifact-/Fixture-Checks laesst.
- Konkrete Dateistruktur, Runner-Kommandos und Implementierungsschnitt werden im Plan entschieden, nicht in dieser Spec.

Der Promptfoo-first Spike ist eine einmalige Vorbedingung fuer die Testsuite-Implementierung, kein regulaerer Testsuite-Testcase. Er muss ein maschinenlesbares oder stabil parsebares Re-Evaluation-Artefakt erzeugen und darf die ADR-Empfehlung nur bestaetigen, wenn keine zentralen Ziele durch manuelle Schritte, statische Fake-Outputs oder nicht reproduzierbare Workarounds ersetzt wurden.

### Pre-Implementation Framework Spike

Der Framework-Spike ist eine einmalige Vorbedingung vor der Implementierung der wiederholbaren Testcases. Er darf nicht in den regulaeren Testsuite-Lauf aufgenommen werden, weil die Testsuite spaeter den Agent Delivery Workflow pruefen soll, nicht jedes Mal die Tool-Entscheidung neu validieren.

Der Spike muss mindestens pruefen:

- Promptfoo kann den Ziel-Agenten oder einen akzeptierten Adapter reproduzierbar starten, oder der Blocker ist konkret und reproduzierbar dokumentiert.
- Fixture- und Schreibisolation sind nachweisbar.
- Agent-Output ist gespeichert und fuer nachgelagerte Assertions verfuegbar.
- Mindestens ein deterministischer Check kann ueber Framework- oder nachgelagerte Validator-Mechanik laufen.
- Tool-/Command-/Cost-/Token-/Trace-Sichtbarkeit ist ausreichend beschrieben; fehlende Sichtbarkeit wird als Limitierung gewertet.
- Manuelle Schritte, statische Fake-Outputs oder nicht reproduzierbare Workarounds duerfen kein `ADOPT_PROMPTFOO` erzeugen.

Der Spike erzeugt eines dieser Re-Evaluation-Ergebnisse fuer ADR und Plan:

- `ADOPT_PROMPTFOO`
- `ADOPT_WITH_LIMITATIONS`
- `FALLBACK_TO_INSPECT`
- `REOPEN_EVALUATION`

### Reproduzierbarkeits-Vertrag

Jeder automatisierte Lauf soll ein Summary-Artefakt erzeugen. Das konkrete Format wird im Plan festgelegt, muss aber mindestens diese Informationen abdecken:

| Feld | Muss enthalten |
|---|---|
| `suite_version` | z. B. Spec-Datei plus Harness-Version oder Git-Commit. |
| `repo_root` | shared-ai-docs Pfad. |
| `repo_git_status` | clean/dirty und relevante Diff-Hinweise. |
| `source_fixture_root` | KI-fuer-KMU Fixture-Quelle oder synthetische Quelle. |
| `fixture_manifest` | Welche Dateien kopiert, entfernt, normalisiert oder synthetisch erzeugt wurden. |
| `test_results` | Status pro Test: `pass`, `fail`, `blocked`, `planned`, `warn`. |
| `evidence_links` | Pfade zu Logs, Assertions, Agent-Outputs, Diffs und Telemetry. |
| `runner_environment` | OS, Shell, dotnet version, SDK-Liste, Docker-Verfuegbarkeit falls relevant. |

## 7. Vision Traceability

| Workflow-Vision | Erforderliche Testabdeckung | Fuehrende Testcases |
|---|---|---|
| Automatische Groessenerkennung vor Schritt 1 | Parent/Master Spec triggert Spec Sizing Gate statt Single-Session-Implementation. | `TC1A`, `TC1D` |
| Parent Spec bleibt Kontrollschicht | Parent wird nicht in Childs aufgeloest oder als Implementierungsziel missbraucht; Coverage bleibt sichtbar. | `TC1A`, `TC2D` |
| Child Specs/Skeletons schneiden | Parent-only Fixture erzeugt Child-Schnitt und Child-Artefakte/Patches. | `TC1A` |
| Operativer Child Index | Index enthaelt exakte Mindestspalten, stabile Child IDs, Dependencies, Verdicts, Handoff-Pointer, Evidence und Next Action. | `TC0`, `TC1A`, `TC2B` |
| Strenges Child Hardening | Plausible Skeletons bleiben nicht ready; `IMPLEMENTATION READY` verlangt Parent Conformance, Write-Set, Handoff, Validator und Verification Contract. | `TC1B`, `TC1C`, `TC1E` |
| Frische Child Delivery Sessions | Delivery startet nur aus aktuellem persistiertem Handoff und nur gegen erlaubtes Temp-Repo/Write-Set. | `TC2A`, `TC2C` |
| Closeout Sync | S3-Delivery/Closeout aktualisiert Parent Coverage, Child Index, Backlog/Re-entry, Evidence Links und OpenSpec Status ohne Scope verschwinden zu lassen. | `TC2B`, `TC2D` |
| Kontrollierte Freigabe des naechsten Child | Ein Folge-Child wird nach S3 nur freigegeben, wenn er selbst implementation-ready ist; sonst blockiert Delivery. Historische S4-Beispiele muessen nach DWT-S4-Acceptance durch synthetische stale/not-ready Fixtures ersetzt werden. | `TC2B`, `TC2C` |

## 8. Nicht-Ziele und Guardrails

- KI-fuer-KMU-Originaldateien bleiben read-only.
- Legacy-Specs werden nicht pauschal migriert.
- Runtime-Implementierung und Verification laufen nur in Temp-Repos oder Temp-Worktrees.
- Positive Fixtures duerfen nicht durch stilles Umschreiben zu einem Beweis gemacht werden. Jede Normalisierung muss als Fixture-Setup sichtbar sein und darf nur Temp-Kopien betreffen.
- Ein bestehender `IMPLEMENTATION READY`-Verdict in einer Fixture beweist nur die Fixture, nicht die Agent-Orchestrierung.
- Ein statischer `NEEDS HARDENING`-Eintrag fuer den naechsten Child beweist nicht den post-closeout-Abbruch; dafuer braucht es einen Delivery-/Closeout- oder Delivery-Kickoff-Dry-Run.
- Die Parent Spec darf nie als Runtime-Implementationseinheit verwendet werden, wenn das Sizing Gate feuert.
- Childs duerfen nur ueber ihren eigenen Hardening Verdict und ihr eigenes Handoff in Delivery gehen; ein akzeptierter Vorgaenger-Child gibt den Nachfolger nicht automatisch frei.
- Skill-Unit-Tests duerfen nicht durch Teil-E2E-Erfolg ersetzt werden. Ein Skill muss isoliert gegen sein Input-/Output-Contract pruefbar bleiben.
- Style-/Usability- und Effizienz-Gates sind eigene Qualitaetsdimensionen und duerfen nicht als "nice to have" aus dem Ergebnis verschwinden.
- Agentische Vollausfuehrung ist nicht der Default fuer Regression. Wo Agenten noetig sind, muessen ihre Outputs gespeichert und danach maschinell validiert werden.
- Automatisierte Harnesses oder bestehende Testframeworks sind der bevorzugte Weg fuer reproduzierbare Checks; Promptfoo wird zuerst per Pre-Implementation-Spike validiert, die endgueltige Framework-, Tool- und Runtime-Auswahl wird nach Spike-Evidence im Plan bestaetigt oder angepasst.

## 9. Decision Freeze Pack

| Entscheidung | Freeze |
|---|---|
| Testlevel | L0-L3 werden als feste Suite-Schichten verwendet. |
| Testarten | Die Suite unterscheidet Skill Unit, Skill Chain/Integration, Teil-E2E, Runtime E2E, Style/Usability und Efficiency/Telemetry. |
| Automation First | Standard-Regression laeuft ueber automatisierte Harnesses oder Frameworks, nicht ueber vollmanuelle Agentenausfuehrung. |
| Framework First | Promptfoo ist nach ADR primaerer Rahmen fuer den Pre-Implementation-Spike; nach Spike-Evidence wird die ADR re-evaluiert. Inspect AI ist Fallback; Eigenbau ist nur nach dokumentiertem Framework-Blocker erlaubt. |
| .NET 10 Option | File-based .NET 10 Tools sind eine bevorzugte Option fuer kleine reproduzierbare Harness-Hilfen, falls bestehende Frameworks Luecken lassen. |
| Fixture Safety | Source-Fixtures werden nur gelesen; Tests arbeiten mit Temp-Kopien. |
| Test Isolation | Jeder Test muss isolierte Fixtures, Evidence und Telemetry verwenden und darf keine implizite Reihenfolge benoetigen, ausser diese ist Teil eines Chain-Tests. |
| Current Suite Classification | Die bestehende Suite ist L0 Contract Smoke. |
| Parent Control Layer | Parent Specs bleiben Kontroll- und Coverage-Schicht und duerfen bei Grossspecs nicht direkt implementiert werden. |
| Parent-Orchestration-Beweis | Muss aus Parent-only oder parent-minimal Fixture starten und neu erzeugte Agent-Outputs validieren. |
| Next-Child-Abbruch-Beweis | Muss einen post-S3-Closeout- oder S4-Delivery-Kickoff-Zustand erzeugen und den Block maschinell belegen. |
| Implementation Ready | Nur `IMPLEMENTATION READY` oder akzeptiertes `READY WITH NON-BLOCKING NOTES` plus Child Index, Handoff, Validator und Verification-Contract duerfen Delivery erlauben. |
| Next Child Release | Ein Child wird nur durch seinen eigenen aktuellen Verdict, Handoff, Index-Row und Dependency-Status freigegeben, nie nur durch Closeout des Vorgaengers. |
| High-risk Verification | High-risk Commands brauchen Rehearsal-Evidence oder blockierende Marker. |
| Style Gate | Handoff-, Index- und Agent-Output-Artefakte muessen fuer User und Folgeskill strukturiert nutzbar sein. |
| Efficiency Gate | L2/L3-Laeufe muessen Tool-/Command-/Read-Telemetry erfassen; Budgets starten warnend und koennen spaeter failend werden. |
| Reproducibility | Jeder automatisierte Lauf schreibt ein maschinenlesbares Summary-Artefakt mit Fixture-, Evidence-, Environment- und Statusdaten. |
| Evidence | Jeder Test schreibt ein Evidence-Artefakt mit Fixture-Setup, Workflow Action, Assertions, Result und Cleanup-Status. |

## 10. Testcase-Katalog

### TC0: L0 Static Contract Smoke

Zweck: Die bestehende Testsuite bleibt als schneller Regressionstest erhalten.

Startpunkt:

- aktuelle KI-fuer-KMU-Spec-Kopie,
- vorhandener Child Index,
- vorhandenes S3-Handoff,
- Temp-Repo-Target fuer positive Delivery-Kickoff-Checks.

Erwartung:

- Child Index hat exakte Mindestspalten.
- S3 kann in der Temp-Kopie den Readiness-Gate bestehen.
- Folge-Child-Fixtures ohne eigenes implementation-allowing Verdict sind nicht delivery-freigegeben.
- stale Handoff ohne Target Repository blockiert.

Einschraenkung:

- TC0 beweist keine Parent-first-Orchestration und keinen post-closeout-Abbruch.

### TC1D: oversized parent does not enter direct implementation

Zweck: Beweisen, dass Codex die Parent/Master Spec als zu gross erkennt und nicht als Single-Session-Implementation startet.

Fixture Setup:

- Parent-only oder parent-minimal Fixture.
- Keine Child Specs, kein Child Index, kein Handoff.
- Optional: absichtlich vorhandenes Temp-Repo, damit der Test beweist, dass die Runtime trotz verfuegbarem Repo nicht beruehrt wird.

Workflow Action:

- L2: Agentischer Dry-Run mit einem Implementierungs-Prompt gegen die Parent Spec.

Assertions:

- Spec Sizing Gate feuert.
- Parent bleibt Scope-/Kontrollschicht.
- `spec-orchestrator` wird als naechster Modus gewaehlt.
- Keine Runtime-Implementation und kein Parent-as-Child-Delivery-Plan entstehen.
- Evidence nennt die Child-Schnitt- und Hardening-Route als erlaubten naechsten Schritt.

### TC1A: Parent-only orchestration produces child control surface

Zweck: Beweisen, dass der Workflow aus einem Parent-only-Start einen Child-Schnitt und ein operationales Steuerpaket erzeugt.

Fixture Setup:

- Kopiere nur Parent Spec und minimal erforderliche normative Quellen in eine Temp-Fixture.
- Entferne Child Index, Child Specs und Child Handoffs aus dem Startzustand.
- Dokumentiere alle entfernten Artefakte in `fixture-manifest.json`.

Workflow Action:

- L2: Agentischer Dry-Run mit `spec-orchestrator`.
- Output muss in einem maschinenlesbaren oder stabil parsebaren Orchestration-Output liegen, z. B. `agent-output/tc1a/orchestration-pack.md` plus generierte Child-Dateien oder Patches.

Assertions:

- Spec Sizing Gate feuert.
- Child Index oder Child-Index-Patch wird neu erzeugt.
- Der erzeugte Child Index ist nicht aus einem bestehenden Source-Index uebernommen; `fixture-manifest.json` und Evidence zeigen, dass im Startzustand kein Child Index, keine Child Specs und keine Handoffs vorhanden waren.
- Child IDs sind stabil und nicht nur kombiniertes Label.
- Coverage Matrix referenziert Parent Requirements.
- Dependencies und Hardening Queue existieren.
- Mindestens ein Child wird als hardening-ready oder hardening-candidate markiert.
- Kein Child ist allein durch Skeleton/Name/Scope `IMPLEMENTATION READY`.

Evidence:

- `evidence/tc1a-orchestration-output.md`
- `evidence/tc1a-assertions.json`

### TC1B: plausible child skeleton cannot become ready

Zweck: Beweisen, dass ein plausibel geschnittener, aber duenner Child nicht als implementation-ready durchrutscht.

Fixture Setup:

- Parent Spec plus absichtlich duenner Child-Skeleton.
- Child hat Ziel, Scope und ein paar Cases, aber keine Parent Conformance, keinen konkreten Write-Set, keine Verification-Command-Rehearsal-Evidence und kein persistiertes Handoff.

Workflow Action:

- L1: statische Gate-Pruefung gegen den Skeleton.
- L2 optional: `child-spec-hardening` Dry-Run.

Assertions:

- Verdict ist `NEEDS HARDENING` oder `NEEDS PARENT/ORCHESTRATOR SYNC`.
- Validator blockiert.
- Keine Delivery-Next-Action wird gesetzt.
- Handoff fehlt oder wird als blocking erzeugt, nicht als implementation kickoff.

### TC1C: ready child requires validator and high-risk command rehearsal

Zweck: Beweisen, dass `IMPLEMENTATION READY` nur mit Validator und High-risk-Command-Contract-Rehearsal erlaubt ist.

Fixture Setup:

- Child Spec mit ansonsten vollstaendigem Contract.
- Verification Commands enthalten bewusst High-risk Commands, z. B. Docker, absolute Paths, SDK-Auswahl.
- Rehearsal-Evidence fehlt im negativen Fixture.

Assertions:

- Ohne Rehearsal oder blockierenden Marker: `NEEDS HARDENING`.
- Mit dokumentierter Rehearsal-Evidence oder bewusstem Blocking-Marker: kein stilles Ready.
- Der Validator muss laufen oder der Test muss `BLOCKED`, nicht `PASS`, melden.

### TC1E: orchestration plus hardening produces readiness matrix

Zweck: Die erste Kernfrage positiv beantworten: Nach Parent-only-Orchestration und Child-Hardening muss eine Implementation-Readiness-Matrix entstehen, die mindestens einen Child nur dann als `IMPLEMENTATION READY` ausweist, wenn alle harten Gates bestanden sind.

Fixture Setup:

- Start mit Parent-only oder parent-minimal Fixture.
- Agent-output aus `TC1A` ist Eingang fuer `child-spec-hardening`.
- Mindestens ein Child ist inhaltlich sinnvoll hardenbar; mindestens ein anderer Child bleibt absichtlich duenner Skeleton oder dependency-blocked.

Workflow Action:

- L2: `spec-orchestrator` erzeugt Child-Schnitt und Hardening Queue.
- L2: `child-spec-hardening` wird fuer alle sinnvoll hardenbaren Children in Dependency-Reihenfolge ausgefuehrt.

Beweiskraft-Regel:

- Fuer die Kernfrage "bringt Parent-first-Orchestration wirklich implementation-ready Child Specs hervor?" zaehlen nur frisch erzeugte Agent-Outputs aus `spec-orchestrator` und `child-spec-hardening`.
- Statische oder synthetische Output-Fixtures duerfen fuer L1-Validator-Regressionen verwendet werden, duerfen aber nicht als positiver Parent-first-Orchestration-Beweis gewertet werden.
- Der Test muss fuer jeden Schritt Input-Artefakt-Hashes oder gleichwertige Provenance nennen, damit ein alter Child Index oder ein vorhaerteter Child nicht unbemerkt als frisches Ergebnis zaehlt.
- Wenn kein Child ohne User-Entscheidung ready werden kann, ist `blocked` ein valides Ergebnis; ein solcher Lauf darf aber nicht als positiver Beweis fuer "mindestens ein Child wird implementation-ready" berichtet werden.

Assertions:

- Readiness Matrix enthaelt fuer jeden Child genau einen aktuellen Status aus `IMPLEMENTATION READY`, `READY WITH NON-BLOCKING NOTES`, `NEEDS HARDENING`, `NEEDS USER DECISION`, `NEEDS PARENT/ORCHESTRATOR SYNC` oder `BLOCKED BY DEPENDENCY`.
- Mindestens ein Child ist `IMPLEMENTATION READY` oder der Test meldet explizit `blocked` mit Grund, warum kein Child ohne User-Entscheidung hardenbar ist.
- Kein Child wird nur aufgrund von plausiblem Schnitt, Titel, Scope oder Skeleton-Text implementation-ready.
- Jeder ready Child hat Parent Conformance, konkretes Allowed Write-Set, persistiertes Handoff, Child-Index-Pointer, Validator-Pass und High-risk-Command-Rehearsal-Evidence oder einen blockierenden Marker.
- Dependencies werden beachtet; dependency-blocked Children werden nicht ready.
- Ready-Status muss Status-Provenance enthalten: welcher Skill-Lauf, welcher Input, welcher Output-Pfad, welcher Validator und welche Rehearsal-/Blocking-Evidence den Status erzeugt haben.

Evidence:

- `evidence/tc1e-readiness-matrix.md`
- `evidence/tc1e-hardening-verdicts.json`

### TC2A: ready child delivery kickoff is temp-repo only

Zweck: Beweisen, dass ein implementation-ready Child nur gegen ein Temp-Repo gestartet werden darf.

Fixture Setup:

- S3-Child mit Child Index und Handoff.
- Handoff Target Repository zeigt auf Temp-Repo.
- Original-Repo-Pfade duerfen im Delivery-Kickoff nicht als Schreibziel vorkommen.

Assertions:

- Child Index, Handoff, Hardening Verdict, Allowed Write-Set und Target Repository stimmen.
- Runtime-Write-Set liegt innerhalb des Temp-Repos oder ist als read-only Spec-/Evidence-Quelle markiert.
- Fehlendes oder stale Target Repository blockiert.

### TC2B: after S3 closeout not-ready next child blocks delivery

Zweck: Die zweite Kernfrage beantworten: Nach abgeschlossener S3-Delivery darf ein Folge-Child nicht automatisch implementiert werden, solange dieser Folge-Child im Fixture nicht implementation-ready ist. Historisch nutzt der Test S4 als not-ready Beispiel; nach DWT-S4-Hardening muss ein synthetischer stale/not-ready S4-Zustand oder ein anderer not-ready Folge-Child im Fixture verwendet werden.

Fixture Setup:

- Temp-Fixture mit S3 als implemented/closeout-ready simuliert.
- S3 Evidence-Artefakt existiert als kontrolliertes Fake-Evidence-Dokument.
- Child Index wird in einer Temp-Kopie so vorbereitet, als ob S3 closeout-synchronisiert werden soll.
- Der Folge-Child bleibt im Fixture `NEEDS HARDENING` oder `NEEDS PARENT/ORCHESTRATOR SYNC` und hat kein implementation-allowing Handoff.

Workflow Action:

- L2: `spec-closeout` Dry-Run oder Closeout-output-Fixture erzeugt Parent/Index/Evidence/Handoff-Sync.
- Danach wird ein Folge-Child-`spec-change-delivery` Kickoff gegen den synchronisierten Zustand versucht.
- Der Folge-Child-Kickoff muss den von `spec-closeout` erzeugten synchronisierten Zustand als Input verwenden; ein Kickoff gegen den urspruenglichen Fixture-Zustand ist kein gueltiger TC2B-Beweis.

Beweiskraft-Regel:

- Fuer die Kernfrage "bricht die Uebergabe nach Implementierung ab, wenn der naechste Child nicht implementation-ready ist?" muss mindestens ein post-closeout Folge-Child-Kickoff gegen einen synchronisierten stale/not-ready Zustand tatsaechlich ausgefuehrt oder als Agent-Dry-Run erzeugt werden.
- Eine rein statische S4-Index-Zeile mit `NEEDS HARDENING` reicht nicht.
- Ein L2-Test mit synthetischer S3-Closeout-Evidence beweist das Next-Child-Gate, aber keine Runtime-Implementation.
- Ein L3-Test mit echter S3-Temp-Repo-Delivery ist erforderlich, wenn die Aussage explizit "nach realer Implementierung" lauten soll.

Assertions:

- S3 darf als closed/accepted oder closeout-synced erscheinen, aber nur mit Evidence-Link.
- Parent Coverage verliert keine deferred oder offenen Requirements.
- Der not-ready Folge-Child wird hoechstens als naechster Hardening-Kandidat markiert.
- Der Folge-Child Delivery-Kickoff endet mit `NOT READY`, `NEEDS HARDENING` oder `NEEDS PARENT/ORCHESTRATOR SYNC`.
- Kein Folge-Child Runtime-Write-Set wird als freigegeben behandelt.
- Kein Folge-Child Temp-Repo-Implementation-Step wird ausgefuehrt.
- Evidence belegt die Reihenfolge `S3 closeout sync -> S4 kickoff attempt -> S4 block` mit Pfaden oder Hashes der Zwischenartefakte.

Evidence:

- `evidence/tc2b-s3-closeout-sync.md`
- `evidence/tc2b-s4-delivery-block.md`
- `evidence/tc2b-assertions.json`

Die S3-Evidence in diesem Test darf synthetisch sein, muss aber explizit als `SYNTHETIC CLOSEOUT FIXTURE` markiert werden. Sie beweist keine Runtime-Implementation. Sie dient nur dazu, den Closeout-/Next-Child-Gate-Zustand reproduzierbar herzustellen.

### TC2C: stale next handoff blocks

Zweck: Beweisen, dass ein Handoff nicht vertraut wird, wenn Target Repository, Child Spec, Child Index, Evidence/OpenSpec-Status oder Next Action auseinanderlaufen.

Fixture Setup:

- S4-Handoff zeigt auf alte Evidence, falschen Child Index oder fehlendes Target Repository.

Assertions:

- Handoff wird als stale erkannt.
- Delivery wird blockiert.
- Blocker nennt die konkrete Inkonsistenz.

### TC2D: parent coverage cannot disappear during closeout

Zweck: Beweisen, dass Closeout offene Parent-Anforderungen nicht durch Status- oder Index-Umschreiben verschwinden laesst.

Fixture Setup:

- Parent Coverage enthaelt eine offene oder deferred Requirement.
- S3 closeout deckt nur einen Teil ab.

Assertions:

- Offene Requirement bleibt sichtbar als `pending`, `blocked`, `partial`, `out_of_scope` oder Backlog/Re-entry.
- Kein Closeout darf den Parent als vollstaendig accepted markieren, wenn Child Coverage fehlt.
- Evidence Links muessen zur jeweiligen Coverage-Entscheidung passen.

### TCQ1: style and follow-skill usability gate

Zweck: Pruefen, ob ein Skill- oder Chain-Output fuer den User und den naechsten Skill direkt nutzbar ist.

Fixture Setup:

- Verwende Agent-Outputs aus Skill-Unit- oder Chain-Tests.

Assertions:

- Review Control Surface, Handoff oder Briefing ist vorhanden und synchron.
- Next Action ist eindeutig.
- Blocker und nicht ausgefuehrte Verification sind sichtbar.
- Child Index, Handoff und Evidence Links sind konsistent.
- Output ist tabellarisch/strukturiert, wenn Folgeskills ihn maschinell oder schnell menschlich lesen muessen.

### TCE1: efficiency and command-drift gate

Zweck: Pruefen, ob der Agent den Skill- oder Chain-Test ohne unnoetige Kommandos, Suchdrift oder verbotene Runtime-Aktionen bearbeitet.

Fixture Setup:

- Verwende `agent-run-manifest.json` oder Runner-Telemetry aus L2/L3.

Assertions:

- Keine verbotenen Command-Klassen fuer den Testtyp.
- Keine Runtime-/Docker-Commands in Spec-only Skill-Unit-Tests.
- Broad scans und repeated reads haben Zweck oder erzeugen `warn`.
- Command-/Tool-Budget ist eingehalten oder Abweichung ist begruendet.
- Efficiency Verdict ist `pass` oder bewusst akzeptiertes `warn`.

## 11. Harness-Artefaktvertrag

Jeder Test trennt seine Artefakte in:

| Bereich | Mindestinhalt |
|---|---|
| `fixture/` | Temp-Kopie oder synthetisches Fixture, niemals Originalquelle. |
| `workflow-action/` | Agent-Prompt, Runner-Aufruf oder dokumentierter Dry-Run-Schritt. |
| `assertions/` | maschinenlesbare Assertions oder Shell-Pruefungen. |
| `evidence/` | Result, Exit-Code, relevante Output-Auszuege, Diff-/Patch-Hinweise. |
| `cleanup/` | Cleanup-Status oder retained fixture path bei Debug-Laeufen. |
| `telemetry/` | Agent-run manifest, Tool-/Command-/Read-Zaehler, Efficiency Verdict. |
| Summary-Artefakt | Gesamtstatus, Harness-/Framework-Version, Fixture Manifest, Environment und Evidence Links. |

Wenn ein Test nur als agentischer Dry-Run moeglich ist, muss das Evidence-Artefakt explizit `DRY-RUN` und die nicht ausgefuehrten Runtime-/Closeout-Schritte nennen.

### Fixture and Provenance Contract

Jedes `fixture-manifest.json` oder gleichwertige Manifest muss mindestens enthalten:

| Feld | Bedeutung |
|---|---|
| `source_files` | Gelesene Original- oder synthetische Quellen mit Pfad und Hash oder stabiler Versionskennung. |
| `copied_files` | In die Temp-Fixture kopierte Dateien. |
| `removed_from_start_state` | Artefakte, die absichtlich aus dem Startzustand entfernt wurden, z. B. Child Index oder Handoffs fuer Parent-only Tests. |
| `normalizations` | Jede Ersetzung, Pfadumschreibung oder synthetische Ergaenzung mit Grund und Zielpfad. |
| `forbidden_source_paths` | Pfade, die im Output nicht als Schreibziel oder Runtime-Ziel erscheinen duerfen. |
| `retained_fixture_path` | Nur bei Debug-/`--keep`-Laeufen; sonst Cleanup-Status. |

Positive Assertions duerfen nur auf normalisierten Temp-Artefakten laufen, wenn die Normalisierung im Manifest steht. Ein Test muss `fail` oder `blocked` melden, wenn er eine Normalisierung braucht, die nicht manifestiert ist.

### L2 Agent Output Contract

Ein L2-Test darf nicht nur freie Prosa als Erfolg werten. Der Agent-Output muss mindestens eines dieser stabil pruefbaren Formate liefern:

1. eine Markdown-Datei mit festen Abschnittsueberschriften aus der jeweiligen Testcase-Spec,
2. ein JSON-Artefakt mit `testcase`, `workflow_action`, `result_status`, `input_artifacts`, `input_artifact_hashes`, `created_or_updated_artifacts`, `blocked_artifacts`, `next_allowed_mode`, `forbidden_actions_observed` und `evidence_links`,
3. oder einen Patch/Diff gegen die Temp-Fixture plus begleitendes `assertions.json`.

Erlaubte `result_status` Werte:

- `orchestrated`
- `hardened`
- `delivery_allowed`
- `delivery_blocked`
- `closeout_synced`
- `blocked`
- `failed`
- `dry-run`

L2-Erfolg verlangt, dass der Harness nicht nur Textstrings sucht, sondern die fuer den Testcase relevanten Felder prueft. Beispiel: `TC2B` muss `next_allowed_mode=child-spec-hardening` oder `delivery_blocked` fuer den not-ready Folge-Child belegen und darf `spec-change-delivery` fuer diesen Fixture-Child nicht als erlaubten naechsten Modus enthalten.

Zusaetzlich muss ein L2-Ergebnis erklaeren, ob es `ran-target`, `ran-rehearsal`, `dry-run`, `blocked` oder `failed` ist. Ein `dry-run` darf keine Runtime- oder Closeout-Ausfuehrung behaupten, und ein `blocked`-Ergebnis darf nicht als positiver Workflow-Beweis zusammengefasst werden.

## 12. Verification Commands

Ausfuehrungskontext:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `zsh` oder `bash`; Skripte selbst deklarieren `#!/usr/bin/env bash`.
- Plattform: macOS als primaerer Authoring-/Harness-Kontext; Linux-Kompatibilitaet fuer spaetere Container-/CI-Gates ist wuenschenswert, aber nicht L0-blockierend.

Aktuelle L0-Verifikation:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/setup-fixture.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all
```

Success Criteria:

- Syntaxchecks enden mit Exit `0`.
- `run-contract-checks.sh all` endet mit Exit `0`, solange Bash-L0 als bestehender Smoke-Harness existiert.
- Evidence zeigt L0 als Contract Smoke, nicht als E2E-Orchestration-Beweis.

Zukuenftige L1/L2-Verifikation:

Konkrete Commands fuer Skill-Unit-, Chain-/Teil-E2E-, Style- und Efficiency-Gates werden im Plan festgelegt, nachdem Framework- und Runner-Optionen bewertet wurden. Sie duerfen erst als Gate gelten, wenn die entsprechenden Harnesses existieren.

High-risk Command Contract:

- Agent-Runner-Commands fuer L2 sind high-risk, weil sie Modell-/Tooling-Verhalten und Output-Pfade betreffen.
- Docker-/Runtime-Commands fuer L3 sind high-risk und brauchen Preflight/Rehearsal.
- Solange kein stabiler L2-Agent-Runner existiert, bleiben L2-Commands dokumentierter Dry-Run und duerfen nicht als `ran-target` Evidence gewertet werden.

## 13. Acceptance Criteria

Die Testsuite gilt fuer die naechste Ausbaustufe als akzeptabel, wenn:

1. L0 weiterhin schnell und deterministisch laeuft.
2. Vor der Implementierung der wiederholbaren Testcases wird der Promptfoo-first Spike als einmalige Vorbedingung durchgefuehrt und erzeugt ein Re-Evaluation-Artefakt fuer die ADR; Inspect AI ist der erste Fallback, falls Promptfoo fuer Codex-Skill-/Desktop-Anbindung blockiert.
3. Agentische Tests sind nicht Default fuer Regression; Agent-Outputs werden gespeichert und maschinell validiert.
4. Testisolation ist fuer Fixtures, Evidence, Telemetry und Runtime-Schreiborte nachweisbar.
5. Fuer die fuehrenden Skills existiert mindestens je ein Skill-Unit-Test mit Input-Fixture, Prompt Contract, Expected Output Contract, Forbidden Outputs, Style Gate und Efficiency Gate.
6. TC1D beweist, dass eine grosse Parent/Master Spec nicht direkt implementiert wird, sondern in Parent/Child-Orchestration routed.
7. TC1A aus einem Parent-only Fixture startet und maschinell beweist, dass Child Control Surface neu entsteht.
8. TC1B beweist, dass ein plausibler Child-Skeleton nicht implementation-ready wird.
9. TC1C beweist, dass Validator und High-risk-Command-Rehearsal nicht optional gruen uebersprungen werden.
10. TC1E beweist, dass Orchestration plus Hardening eine Readiness Matrix erzeugt und mindestens einen Child nur mit harten Gates implementation-ready macht oder begruendet blockiert.
11. TC2B beweist den post-closeout-Abbruch fuer einen nicht-ready Next Child.
12. TC2D beweist, dass Parent Coverage, Backlog/Re-entry, Evidence Links und OpenSpec Status beim Closeout nicht auseinanderlaufen oder verschwinden.
13. TCQ1 prueft, ob Output fuer User und Folgeskill strukturiert nutzbar ist.
14. TCE1 prueft Tool-/Command-/Read-Telemetry und markiert unnoetige oder verbotene Aktionen mindestens als `warn`.
15. Jede positive Normalisierung im Fixture-Setup sichtbar dokumentiert ist und nicht als Quellevidence verkauft wird.
16. Evidence-Dateien klar zwischen `ran-target`, `ran-rehearsal`, `blocked`, `failed`, `planned` und `dry-run` unterscheiden.
17. Jeder automatisierte Lauf erzeugt ein maschinenlesbares Summary-Artefakt oder ein gleichwertiges Reporting-Artefakt.
18. Die Vision Traceability Matrix fuer das automatische Sizing Gate plus alle sieben Workflow-Schritte mindestens L1- oder L2-Testabdeckung nennt.
19. Die Child-Index-Slices `DWT-S0` bis `DWT-S5` bleiben in Parent Coverage, Dependencies, Evidence und Next Action synchron; kein Slice darf als implementation-ready geplant werden, bevor sein eigenes Handoff und sein eigener Verification Contract existieren.

## DWT-S1 Closeout Evidence

- Accepted child: `DWT-S1` deterministic L1 contract harness.
- OpenSpec archive: `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness/`.
- Canonical spec: `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`.
- Retained L1 summary: `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.bMyVlu/evidence/l1-summary.json`.
- Verification replay: `bash -n tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh`; `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all --keep`; `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all`; `openspec validate docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness --strict` before archive; `openspec validate docworkflow-agent-delivery-testsuite --strict`; `ValidateChildReadiness.cs` for `DWT-S1`.
- Next-child state after DWT-S1 closeout: `DWT-S4` is now independently hardened for reporting contract delivery; `DWT-S2`, `DWT-S3` and `DWT-S5` are not delivery-released by DWT-S1 closeout.

## Parent Closeout Evidence

- Closed scope: Parent control layer `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md` for `DWT-S0` through `DWT-S5`.
- Out of scope: no workflow retro, no descendant child creation, no new follow-up delivery release, no mutation of accepted child archives beyond the already archived DWT-S5 closeout state.
- OpenSpec status: all child changes are archived under `openspec/changes/archive/`; canonical spec `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` validates and contains accepted requirements through `DWT-S5`.
- Child Index sync: `DWT-S0`, `DWT-S1`, `DWT-S2`, `DWT-S3`, `DWT-S4` and `DWT-S5` rows all show accepted/closed child state, retained evidence, archived OpenSpec references, parent coverage, explicit backlog/re-entry notes and a non-release next action where applicable.
- Deferred scope: none hidden in the Parent. Fallback/blocker modes remain regression aids only and cannot replace retained `ran-target` evidence. Any future work requires a new explicit spec/change.

Verification checklist:

| Gate | Command / Check | Result | Evidence |
|---|---|---|---|
| Script syntax | `bash -n tests/docworkflow-agent-delivery/scripts/*.sh` | ran/pass | Exit `0`. |
| OpenSpec canonical | `openspec validate docworkflow-agent-delivery-testsuite --strict` | ran/pass | `Specification 'docworkflow-agent-delivery-testsuite' is valid`. |
| Child evidence/archive sync | Node retained evidence/archive assertion for `DWT-S0`, `DWT-S2`, `DWT-S3`, `DWT-S5` plus all child archive directories | ran/pass | Retained `ran-target` summaries and archive directories found. |
| L0 harness | `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all` | ran/pass | `RESULT: PASS`. |
| L1 harness | `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all --keep` | ran/pass | Retained replay summary at `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.xS6mnJ/evidence/l1-summary.json`. |
| L2 parent-first harness | `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh all --keep` | ran/pass | Retained replay summary at `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l2-parent-first.QzDI0N/evidence/dwt-s2-l2-summary.json`. |
| L2 single-child closeout harness | `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh all --keep` | ran/pass | Retained replay summary at `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l2-single-child-closeout.TclkAl/evidence/dwt-s3-l2-summary.json`. |
| Reporting harness | `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all --keep` | ran/pass | Retained replay summary at `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-reporting.OiICAA/evidence/dwt-s4-reporting-summary.json`. |
| L3 active-child harness command contract | `tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh all --keep` and `preflight --keep` | ran/failed as stale post-archive command | The runner still expects the pre-closeout active DWT-S5 row, active OpenSpec path and `IMPLEMENTATION READY` handoff; after accepted archive it correctly sees archived/accepted values instead. This is recorded as a command-contract finding, not as failed runtime evidence. |
| L3 post-archive evidence check | Node assertion against Parent DWT-S5 row, DWT-S5 handoff, archive path and retained DWT-S5 `ran-target` summary | ran/pass | Parent row and handoff point to `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot/`; retained summary has `runner_mode: promptfoo-codex`, `agent_execution_status: ran-target`, `overall_runtime_proof_status: pass`; no descendant child release. |
| Whitespace/diff hygiene | `git diff --check` | ran/pass | Exit `0`. |

Documentation sync:

- RAG source discovery ran with `rag workflow spec-closeout --scope all --change "DocWorkflow Agent Delivery Testsuite parent closeout DWT-S0 DWT-S5" --top-k 8 --format json` and `rag retrieve semantic --scope all --query "DocWorkflow Agent Delivery Testsuite parent child workflow DWT-S0 DWT-S5 closeout accepted archived documentation" --top-k 8 --format json`.
- Prioritized sources: this Parent Spec, `docs/doc-workflow.md`, `skills-repo/skills/spec-closeout/SKILL.md`, and `tests/docworkflow-agent-delivery/README.md`.
- Search evidence: repo search for `DocWorkflow Agent Delivery Testsuite`, `docworkflow-agent-delivery-testsuite`, `docworkflow-agent-testsuite-dwt`, `DWT-S0` through `DWT-S5`, and `tests/docworkflow-agent-delivery` found no stale public project docs requiring broad sync beyond this Parent closeout and the already synchronized harness README/testcase docs.
- Generated/noisy RAG hits such as unrelated historical specs and generic RAG docs were filtered out because they did not carry current DWT-S0 through DWT-S5 status.

Final parent closeout result: READY.

## 14. Content Quality Review

Review-Ergebnis:

- Correctness/domain fit: Pass. Die Spec adressiert die Workflow-Vision, die konkreten Erkenntnisfragen und trennt Smoke-Test von Beweis-Test.
- Necessity/scope: Pass. L0-L3 verhindern, dass ein grosser E2E-Anspruch in einen unehrlichen Schnelltest kippt.
- Completeness: Pass fuer Parent-Spec-/Harness-Ebene; Skill-Unit-, Chain-/Teil-E2E-, Style-, Efficiency-, Isolation-, Framework-first- und Automation-first-Anforderungen sind getrennt beschrieben. Das Sizing Gate plus die sieben Vision-Schritte sind tracebar, Promptfoo ist per ADR als fuehrender Spike-Rahmen festgelegt, und die Umsetzung ist in `DWT-S0` bis `DWT-S5` abgeschlossen.
- Consistency: Pass. Die Spec bleibt mit `docs/doc-workflow.md`, dem ADR-Bezug und den Child-/Handoff-Regeln konsistent; sie behauptet keine Implementation Readiness fuer den Gesamtscope.
- Testability: Pass. L0, L1, L2, L3 und Reporting haben deterministische Runner oder retained `ran-target` Evidence; post-archive Parent-Replay nutzt retained L3 evidence statt den pre-closeout active-child L3 command contract.
- Blocking Marker: Keine.

## 15. Mini-Retro

- Was wurde entschieden? Die Parent Spec ist als abgeschlossene Kontrollschicht fuer `DWT-S0` bis `DWT-S5` accepted/closed; kein Child oder Folgescope wird daraus implizit freigegeben.
- Was wurde geaendert? Header, Review Control Surface, Child Index, Parent Closeout Evidence, Documentation Sync, Content Review und History wurden auf den Gesamtabschluss synchronisiert.
- Was bleibt offen? Kein Parent-Closeout-Blocker. Ein separater zukuenftiger Change kann den L3-Runner um einen expliziten post-archive Selector erweitern, falls das als wiederholbarer Regression-Command gewuenscht ist.
- Welche Evidenz/Verification fehlt? Keine fuer den Parent-Abschluss. Der pre-closeout aktive DWT-S5 L3-Runner ist nach Archivierung absichtlich nicht mehr der fuehrende Parent-Replay-Command; retained L3 `ran-target` evidence und post-archive assertions sind gruen.
- Welche Skill-/Workflow-Reibung ist aufgefallen? Active-child Runner-Vertraege brauchen nach Archivierung einen eigenen post-archive Replay-Pfad, damit Parent-Closeout nicht gegen alte aktive Ledger-Erwartungen laeuft.
- Session-/Kontextzustand: Parent closeout ist abgeschlossen; kein Workflow-Retro wurde gestartet.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-07 | Codex | Initiale Testsuite-Spec mit L0-L3-Testleveln, Kern-Testcases und Evidence-Vertrag erstellt. |
| 2026-05-07 | Codex | Workflow-Vision, Vision Traceability, TC1D und erweiterte Acceptance Criteria ergaenzt. |
| 2026-05-07 | Codex | Auto-Resolve-Review: L2-Agent-Output-Vertrag, vollstaendige Soll-Commands und synthetische TC2B-Evidence-Regel ergaenzt. |
| 2026-05-07 | Codex | Auto-Resolve-Review: TC1E fuer positiven Orchestration-plus-Hardening-Readiness-Beweis ergaenzt und Kontrollflaechen synchronisiert. |
| 2026-05-07 | Codex | Auto-Resolve-Review: stale L2-Output-Format-Open-Items bereinigt. |
| 2026-05-07 | Codex | Mehrstufige Testarchitektur mit Skill-Unit-, Chain-/Teil-E2E-, Style-/Usability- und Efficiency-/Telemetry-Gates ergaenzt. |
| 2026-05-07 | Codex | Automation-first Rahmen mit Reproduzierbarkeitsvertrag ergaenzt. |
| 2026-05-07 | Codex | Spec von konkreten Runner-/Tool-Details bereinigt und Testisolation sowie Framework-first-Research als Anforderungen ergaenzt. |
| 2026-05-07 | Codex | Framework-ADR ausgewertet: Promptfoo als primaerer Agent-/Coding-Agent-Eval-Rahmen und Inspect AI als Fallback in die Spec aufgenommen. |
| 2026-05-07 | Codex | Beweiskraft-Regeln fuer TC1E und TC2B geschaerft: synthetische Fixtures duerfen Kernfragen nicht als positive Agent-/Runtime-Beweise ersetzen. |
| 2026-05-07 | Codex | Promptfoo-first Spike als einmalige Pre-Implementation-Vorbedingung statt regulaerem Testcase klargestellt. |
| 2026-05-07 | Codex | Kritisches Auto-Resolve-Review: Spec Sizing Gate angewendet, `DWT-S0` bis `DWT-S5` Child-Index ergaenzt und Evidence-/Provenance-Gates fuer TC1A, TC1E und TC2B geschaerft. |
| 2026-05-07 | Codex | Spec-Orchestrator: DWT-S0 als naechsten fuehrenden Slice bestaetigt, persistiertes Handoff und OpenSpec-Ledger angelegt, Parent Child Index synchronisiert. |
| 2026-05-07 | Codex | DWT-S4 Child Spec, Parent Child Index, Handoff und aktiven OpenSpec-Change fuer Summary-/Telemetry-/Style-/Reporting-Contract auf implementation-ready synchronisiert. |
| 2026-05-07 | Codex | Child-Spec-Hardening: DWT-S0 Child Spec ergaenzt, Promptfoo-Command-Vertrag rehearsed und DWT-S0 auf `IMPLEMENTATION READY` gesetzt. |
| 2026-05-07 | Codex | DWT-S0 accepted, Promptfoo mit Limitierungen bestaetigt und OpenSpec-Change archiviert. |
| 2026-05-08 | Codex | DWT-S4 reporting fixtures, validator, runner, README/testcases and verification evidence implemented; DWT-S2/DWT-S3/DWT-S5 remain unreleased. |
| 2026-05-08 | Codex | DWT-S4 accepted and archived; Parent Child Index and handoff synchronized to closeout evidence while DWT-S2/DWT-S3/DWT-S5 remain unreleased. |
| 2026-05-08 | Codex | DWT-S2 hardened to `IMPLEMENTATION READY` with child spec, Parent Child Index row, persisted handoff and active OpenSpec change; DWT-S3/DWT-S5 remain unreleased. |
| 2026-05-08 | Codex | DWT-S3 hardened to `IMPLEMENTATION READY` with child spec, Parent Child Index row, persisted handoff and active OpenSpec change; DWT-S5 remains blocked. |
| 2026-05-08 | Codex | DWT-S3 L2 single-child delivery/closeout harness implemented with retained Promptfoo/Codex `ran-target` evidence; DWT-S5 remains blocked pending its own gates. |
| 2026-05-08 | Codex | DWT-S3 accepted and OpenSpec archived; canonical testsuite spec updated while DWT-S5 remains blocked by dependency. |
| 2026-05-08 | Codex | DWT-S5 hardened to `IMPLEMENTATION READY` with child spec, Parent Child Index row, persisted handoff, active OpenSpec change, retained DWT-S3 dependency checks and runtime-temp-repo evidence contract; no runtime or Docker/container proof was run during hardening. |
| 2026-05-08 | Codex | DWT-S5 accepted and OpenSpec archived with retained Promptfoo/Codex `ran-target` L3 runtime temp-repo evidence; no descendant child was released. |
| 2026-05-08 | Codex | Parent Spec accepted/closed after DWT-S0 through DWT-S5 archive/evidence sync, full parent closeout verification replay and documentation sync; no descendant child or follow-up scope released. |

SessionId: 2026-05-07-docworkflow-agent-delivery-testsuite
