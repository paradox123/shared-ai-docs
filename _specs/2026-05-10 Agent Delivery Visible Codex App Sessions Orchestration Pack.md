**Date:** 2026-05-10
**Status:** 🟢 Accepted S3 Sync
**Scope:** Parent/Child orchestration pack for `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`. Tracks child delivery status; `ADV-CAS-S3` / `MD-E2E-5` is now accepted with retained controller-backed live evidence.

---

## Review Control Surface

- Spec-Variante: Delivery Orchestration Pack for a contract-heavy workflow/tooling parent spec.
- Goldstandard Status: active control pack; S1 is delivered, and S2/S3/S4/S5 are accepted.
- Ziel: Split the visible Codex-App Agent Delivery change into bounded Child Slices with coverage, dependencies, hardening queue, allowed next actions and one leading next child.
- In Scope: Spec sizing verdict, Child Index, Coverage Matrix, Dependencies, Hardening Queue, Parallel Work Control Surface, delivery-pack skeletons and leading child handoff.
- Out of Scope for S3 closeout sync: new Launcher code edits, new test runner implementation, new live `MD-E2E-5` execution, `codex app-server` session launch, `codex exec` launch, app-server archive execution.
- Wichtigste Test-/Harness-Cases: visible-app positive app-server evidence; `codex exec`/`source='exec'` negative; wrong title; wrong cwd; missing thread; queued-only; final-output-correct-but-visible-evidence-missing; visible-evidence-pass-but-output-wrong; unarchived visible sessions.
- Wichtigste Verification Commands: accepted closeout replay includes the retained `run-visible-app-session-workflow-checks.sh --run-id 20260511T123609Z-md-e2e-5-controller-live --keep --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`, controller fixture replays, live S4/S5 validations, canonical OpenSpec spec validation, and `git diff --check`.
- Offene Entscheidungen: No blocking product decision for orchestration. UI/sidebar screenshot proof and long-lived app-server socket remain non-blocking follow-ups.
- Readiness Status: `ADV-CAS-S1` is `IMPLEMENTED`; `ADV-CAS-S2` is `ACCEPTED`; `ADV-CAS-S3` is `ACCEPTED`; `ADV-CAS-S4` is `ACCEPTED`; `ADV-CAS-S5` is `ACCEPTED`. `MD-E2E-5` live evidence is retained under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/`; the OpenSpec change is archived at `openspec/changes/archive/2026-05-11-agent-delivery-md-e2e-5-external-controller-integration/`.

## Session Briefing

- Modus/Skill: `spec-orchestrator`.
- Source of Truth: `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`; `skills-repo/tools/AgentDeliverySessionLauncher.cs`; `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`; `docs/doc-workflow.md`; `skills-repo/skills/spec-closeout/SKILL.md`; `tests/docworkflow-agent-delivery/README.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `tests/docworkflow-agent-delivery/e2e/mock-runner/run.js`.
- Ziel: Make the parent spec executable as separate Child Slices without starting runtime implementation.
- Nicht-Ziele: No MD-E2E-5 regression run in this session; no Launcher/app-server adapter implementation; no child delivery directly from this control/orchestration session.
- In Scope: Parent/Child slicing, delivery-pack skeletons, coverage/dependency/readiness control, leading handoff for the next skill.
- Erwarteter Output: this orchestration pack and `_specs/child-session-handoffs/adv-cas-s1-session-handoff.md`.
- Verification/Review: documentation-only sanity via source reads and `git diff --check` if desired; no runtime gates run in this session.
- Offene Entscheidungen: Parent identifier assigned for future title contract: `ADV-CAS-1` (`Agent Delivery Visible Codex App Sessions`, parent instance 1).

## Spec Sizing Verdict

**Verdict:** Gate fires; parent spec is too large for one delivery change.

Signals:

| Sizing Signal | Finding |
|---|---|
| Multiple capability domains | Launcher process/app-server adapter, evidence schema, validator negatives, testsuite integration, workflow boundary, closeout archive support. |
| Multiple systems/files | C# tools, shell/Node test suite, workflow docs, closeout skill, Codex app-server protocol/evidence. |
| Multiple verification cycles | Adapter unit/contract checks, validator fixtures, live visible-session workflow gate, closeout archive gate. |
| Natural delivery slices | The five expected child themes each have separate done signals and failure modes. |
| Context/session risk | Live visible-session regression must run later as a separate control/launcher workflow, not inside orchestration. |

Routing: Parent/Child orchestration is required. Implementation is blocked until at least the leading child is hardened.

## Parent Requirements

| Requirement | Summary | Source |
|---|---|---|
| `ADV-PR1` | Distinguish `headless_cli_session`, `queued_manual_start`, `manual_visible_start`, `visible_codex_app_session` and `traceable_but_not_visible`. | Parent sections 3, 5, 6 |
| `ADV-PR2` | Visible-app launch path uses `codex app-server` with `thread/start`, `thread/name/set`, `turn/start`, then `thread/list` interactive-source proof. | Parent sections 2.4, 8 |
| `ADV-PR3` | Visible sessions open under the initiating Codex project cwd, while target workspace remains separately recorded. | Parent section 4.1 |
| `ADV-PR4` | Titles exactly follow `{ParentSpecAbbrevAndNumber}: {Hardening|Implementation} - {ChildSpecDesignation}`. | Parent section 4.2 |
| `ADV-PR5` | Evidence records execution channel, session visibility class, cwd/title/thread/source/proof fields and prompt/turn linkage. | Parent sections 5, 6 |
| `ADV-PR6` | Validator rejects `codex exec`, `source='exec'`, wrong title, wrong cwd, missing thread and queued-only false positives. | Parent sections 5, 6, 9 |
| `ADV-PR7` | `MD-E2E-5` is integrated into the Agent Delivery Workflow Test Suite and gates both final output and visible-session evidence. | Parent section 9 |
| `ADV-PR8` | Control session may only prepare input, start Launcher, observe evidence, stop own test processes and report. | Parent section 9 |
| `ADV-PR9` | `spec-closeout` archives visible app-server sessions through `thread/archive` or records explicit no-thread/not-app-visible states. | Parent section 7 |
| `ADV-PR10` | Docs/skills stop treating `status: launched` from `codex exec` as visible-app success. | Parent sections 5, 11 |

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADV-CAS-S1 | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S1 Launcher Visible App Adapter.md` | `ADV-PR2`, `ADV-PR3`, `ADV-PR4`, supports `ADV-PR1`, `ADV-PR5`, `ADV-PR10` | `IMPLEMENTED`; S1 delivered the app-server adapter, visible evidence fields, headless downgrade and S1-local validator cases | `child-session-handoffs/adv-cas-s1-session-handoff.md` | Active implementation ledger: `openspec/changes/agent-delivery-visible-app-launcher-adapter/`; not archived until post-acceptance closeout because canonical OpenSpec spec mutation is outside S1 write-set | Parent identifier `ADV-CAS-1` assigned; S1 evidence field names are frozen for S2/S3/S5; downstream children must resync to the implemented schema | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S1 Launcher Visible App Adapter.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `_specs/child-session-handoffs/adv-cas-s1-session-handoff.md`; `_specs/agent-delivery-session-launches/**`; `openspec/changes/agent-delivery-visible-app-launcher-adapter/**`; `skills-repo/tools/AgentDeliverySessionLauncher.cs`; `skills-repo/tools/AgentDeliveryCodexAppServerClient.cs`; `docs/doc-workflow.md`; `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-launcher-s1/**`; `tests/docworkflow-agent-delivery/e2e/validators/visible-app-launcher-s1.js` | Ran: `ValidateChildReadiness.cs`; `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help`; `codex app-server --help`; `codex app-server generate-ts --out /tmp/codex-app-schema-adv-cas-s1`; `openspec validate agent-delivery-visible-app-launcher-adapter --strict`; S1 fixture validator; S1-local app-server smoke; `git diff --check`. `MD-E2E-5` was not run | Retained smoke evidence: `_specs/agent-delivery-session-launches/20260510T081130Z-adv-cas-s1/evidence.json` and `app-server-transcript.jsonl`; S1 fixtures under `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-launcher-s1/` | S2/S3/S5 must consume S1 field names; archive support and `MD-E2E-5` remain downstream | Continue with `child-spec-hardening` for ADV-CAS-S2; do not run `MD-E2E-5` until downstream prerequisites are ready |
| ADV-CAS-S2 | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S2 Visible Evidence Validator.md` | `ADV-PR1`, `ADV-PR5`, `ADV-PR6`; supports `ADV-PR10` | `ACCEPTED`; closeout accepted visible evidence validator | `child-session-handoffs/adv-cas-s2-session-handoff.md` | `not_used`: no active `agent-delivery-visible-session-validator` change exists; proposed ledger was never created | S1 implemented; accepted S2 validator now unblocks S5/S3 validation use | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S2 Visible Evidence Validator.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `_specs/child-session-handoffs/adv-cas-s2-session-handoff.md`; `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`; `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`; `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/**`; `tests/docworkflow-agent-delivery/e2e/validators/visible-app-session-evidence.js` | Closeout replay ran: `ValidateAgentDeliveryLaunchEvidence.cs --help`; S1 visible fixture validator; `ValidateChildReadiness.cs`; `ValidateVisibleCodexAppSessionEvidence.cs --fixture`; setup-error fixture exit-code check; existing launch-evidence fixture regression; source `rg` check; `git diff --check`. `MD-E2E-5` was not run | Closeout accepted. Retained S2 validator fixture summary `RESULT: PASS (11 cases)`; setup-error fixture exits `2`; existing launch-evidence regression `RESULT: PASS (10 cases)`; no S2 `visible_codex_app_session` launch evidence found, so `archive_status: no_s2_visible_thread_created` | If S1 delivery changes evidence names, re-enter S2 hardening before S5/S3 | Start fresh `spec-change-delivery` for ADV-CAS-S2 only if S2 evidence must be replayed; otherwise continue with dependent S5/S3 work |
| ADV-CAS-S3 | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S3 MD-E2E-5 Integration.md` | `ADV-PR7`; consumes `ADV-PR2`, `ADV-PR5`, `ADV-PR6`, `ADV-PR8`, `ADV-PR9`, `ADV-PR10` | `ACCEPTED`; retained controller-backed live `MD-E2E-5` pass with parent plus five externally launched visible child sessions | `child-session-handoffs/adv-cas-s3-session-handoff.md` | Archived: `openspec/changes/archive/2026-05-11-agent-delivery-md-e2e-5-external-controller-integration/` | S1/S2/S4/S5 accepted; mock-only standard gate preserved | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S3 MD-E2E-5 Integration.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `_specs/child-session-handoffs/adv-cas-s3-session-handoff.md`; `tests/docworkflow-agent-delivery/testcases/md-e2e-5-visible-codex-app-sessions.md`; `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`; `tests/docworkflow-agent-delivery/README.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/**`; `tests/docworkflow-agent-delivery/e2e/fixtures/visible-session-controller-md-e2e-5/**` | Closeout replay ran: live `MD-E2E-5` runner pass; controller MVP fixture pass; controller MD-E2E-5 fixture pass; live S4 summary validation pass; live S5 archive summary validation pass; OpenSpec validation before archive; `git diff --check` | Accepted. Retained live evidence: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/visible-session-summary.json`; controller summary, S4 summary, S5 archive summary and final output hash are retained in the same run directory | If future S1/S2/S4/S5 contracts change, re-enter S3 regression validation | No further S3 action; parent `ADV-PR7` is done |
| ADV-CAS-S4 | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S4 Control Session Boundary.md` | `ADV-PR8`; supports `ADV-PR7` | `ACCEPTED`; S4 control-boundary fixture/validator slice accepted while preserving downstream S3 live-run ownership | `child-session-handoffs/adv-cas-s4-session-handoff.md` | `not_used`: no active `agent-delivery-visible-control-boundary` change exists; proposed ledger was never created | Accepted after S2/S5; S3 consumes final control-boundary status before live runner success | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S4 Control Session Boundary.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `_specs/child-session-handoffs/adv-cas-s4-session-handoff.md`; `tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary/**`; `tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js`; `tests/docworkflow-agent-delivery/testcases/md-e2e-5-visible-codex-app-sessions.md`; `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`; `tests/docworkflow-agent-delivery/README.md` | Closeout replay ran: `ValidateChildReadiness.cs`; `bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`; control-boundary fixture suite `RESULT: PASS (9 cases)`; targeted positive/direct-output fixture checks; embedded JSON parse; `git diff --check`. `MD-E2E-5` was not run | Accepted. S4 fixture/validator evidence retained in source fixtures and validator replay output; no visible Codex-App session was created for S4; no S4 OpenSpec archive exists because no active ledger was created | If S3 owns runner implementation entirely, consume S4 validator/status and avoid double-editing runner files | No further S4 action; continue S3 delivery |
| ADV-CAS-S5 | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S5 Closeout Archive Support.md` | `ADV-PR9`; supports `ADV-PR5`, `ADV-PR7`, `ADV-PR10` | `ACCEPTED`; closeout archived OpenSpec and retained S5 archive summary/tool support, S2 failure-class bridge, docs/skill wording and source-controlled closeout fixtures | `child-session-handoffs/adv-cas-s5-session-handoff.md` | Archived: `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-closeout-archive/` | S1 visible evidence fields implemented; S2/S4/S5 accepted; S3 is implementation-ready for final live pass delivery | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S5 Closeout Archive Support.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `_specs/child-session-handoffs/adv-cas-s5-session-handoff.md`; `skills-repo/skills/spec-closeout/SKILL.md`; `docs/doc-workflow.md`; `skills-repo/tools/ArchiveVisibleCodexAppSession.cs`; `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`; `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**`; `tests/docworkflow-agent-delivery/e2e/validators/visible-session-closeout-summary.js`; `tests/docworkflow-agent-delivery/README.md`; `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-closeout-archive/**` | Closeout replay ran: `codex app-server --help`; `codex app-server generate-ts`; generated protocol file checks; S5 archive fixture suite `RESULT: PASS (10 cases)`; S5/S2 closeout bridge `RESULT: PASS (10 cases)`; S2 visible evidence regression `RESULT: PASS (11 cases)`; source wording check; pre-acceptance `ValidateChildReadiness.cs`; `git diff --check`. `MD-E2E-5` and live `thread/archive` were not run by design | Accepted. Retained S5 fixture summaries prove visible archive positive, already archived, headless not app-visible, queued no-thread, archive failure, post-archive proof failure, mixed child run, unarchived-visible negative, manual-visible missing thread and retained-session acceptance | Live archive remains opt-in; S3 live `MD-E2E-5` now waits for S3 delivery execution | No further S5 action; continue with S3 delivery |

## Coverage Matrix

| Parent Requirement | Owning Child | Coverage Status | Notes |
|---|---|---|---|
| `ADV-PR1` | `ADV-CAS-S2` primary; S1/S5 consume | done_for_S2 | S2 validator enforces evidence classes and rejects non-visible false positives. |
| `ADV-PR2` | `ADV-CAS-S1` | implemented | Launcher app-server adapter delivered and smoke-proven via `thread/start`, `thread/name/set`, `turn/start` and `thread/list`. |
| `ADV-PR3` | `ADV-CAS-S1` | implemented | Evidence now records `initiating_project_cwd`, `target_workspace` and `project_cwd_source`; app-server smoke observed matching cwd. |
| `ADV-PR4` | `ADV-CAS-S1`, validated by S2 | implemented | Launcher derives `ADV-CAS-1: Implementation - ...` titles; S2 still owns downstream negative validation. |
| `ADV-PR5` | `ADV-CAS-S1`, `ADV-CAS-S2`, `ADV-CAS-S5` | partial | S1 freezes launcher evidence fields; S2 validates visible evidence and false positives; S5 now adds archive summary coupling. |
| `ADV-PR6` | `ADV-CAS-S2` | done | S2 fixtures cover headless exec, source exec, wrong title, wrong cwd, missing thread, queued-only, prompt mismatch, missing turn and unarchived visible closeout. |
| `ADV-PR7` | `ADV-CAS-S3` | done | `MD-E2E-5` passes in retained controller-backed live run `20260511T123609Z-md-e2e-5-controller-live`. |
| `ADV-PR8` | `ADV-CAS-S4`, consumed by S3 | done_for_S4 | S4 accepted control-boundary fixtures/validator; S3 must consume the accepted status before live MD-E2E-5 can pass. |
| `ADV-PR9` | `ADV-CAS-S5`, consumed by S3 | done_for_S5 | S5 accepted archive support; MD-E2E-5 can consume it after S3/S4 gates are ready. |
| `ADV-PR10` | S1/S2/S3/S5 plus docs sync | done | S3 README/testcase docs preserve mock/live distinction and point at retained live evidence. |

No parent requirement is missing; all are assigned to a child or explicit dependency.

## Dependencies

| From | To | Type | Rationale |
|---|---|---|---|
| S1 | S2 | schema/API | Validator needs final Launcher evidence fields and app-server transcript shape. |
| S1 | S3 | runtime capability | MD-E2E-5 cannot launch visible sessions until adapter exists. |
| S2 | S3 | gate | MD-E2E-5 must fail false positives through the validator. |
| S4 | S3 | control boundary | Runner must prove observed-only control behavior. |
| S1 + S2 | S5 | evidence/archive | Closeout needs visible thread ids/classes and validator semantics. |
| S5 | S3 | final pass | MD-E2E-5 success requires archive/no-thread evidence. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `ADV-PR2` | S1 owns only Launcher adapter and immediate app-server proof. | narrows_with_rationale | S2 validates false positives; S3 runs full workflow. |
| `ADV-PR6` | S2 owns evidence validation, not app-server launch implementation. | preserves | Freeze schema dependency on S1 before delivery. |
| `ADV-PR7` | S3 owns MD-E2E-5 suite integration and final live gate. | preserves | Do not run it in this orchestration session. |
| `ADV-PR8` | S4 owns control-session boundary contract. | preserves | S3 consumes the accepted S4 fixture/validator status during MD-E2E-5 hardening/delivery. |
| `ADV-PR9` | S5 owns archive tool/closeout skill support. | preserves | S3 final success depends on S5 capability. |

## Hardening Queue

| Order | Child | Hardening Need | Blocking Questions For Hardening |
|---|---|---|---|
| complete | `ADV-CAS-S1` | Hardened implementation-ready child spec for app-server adapter, initiating cwd and title/evidence contract. | Frozen default: explicit visible adapter state such as `--adapter codex-app-server`; per-run `codex app-server --listen stdio://`; no `MD-E2E-5` in S1. |
| complete | `ADV-CAS-S2` | Accepted reusable visible evidence validator and negative/positive fixture schema. | Validator is `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`; fixture root is `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/`. |
| complete | `ADV-CAS-S4` | Accepted control-session boundary fixture/validator slice. | Fixture root is `tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary/`; validator is `tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js`. |
| complete | `ADV-CAS-S5` | Accepted archive support and closeout skill/tool contract after accepted S2 validator delivery. | Frozen default: closeout companion tool `ArchiveVisibleCodexAppSession.cs`; no Launcher archive mode required for S5. |
| complete | `ADV-CAS-S3` | Accepted MD-E2E-5 suite integration after S1/S2/S4/S5 contracts. | Retained controller-backed live run proves parent plus five externally launched child visible sessions and exact final output. |

## Parallel Work Control Surface

| Work Block | Lane Mode | Allowed Parallelism | Shared / Read-only Files | Integration Owner |
|---|---|---|---|---|
| S1 delivery | implementation | Serial leading slice; ready for one fresh `spec-change-delivery` session. | Parent spec, app-server spike evidence, S2/S3/S4/S5 child drafts and downstream validator/runner/archive files stay read-only. | S1 delivery session. |
| S2 closeout | accepted child | Complete; downstream children may consume accepted validator evidence. | S2 implementation files stay stable unless S5/S3 explicitly require a follow-up validator extension. | S2 closeout session. |
| S4 closeout | accepted child | Complete; S3 can consume accepted control-boundary fixtures/status. | Live runner integration stays with S3. | S4 closeout session. |
| S5 delivery | accepted child | Complete; S3 can consume S5 archive behavior after S4/S3 gates are ready. | `AgentDeliverySessionLauncher.cs` and S3 runner files stayed read-only. | S5 closeout session. |
| S3 delivery | accepted child | Complete; retained live evidence is available for regression replay. | Mock runner baseline remains read-only and must not be replaced. | S3 integration owner. |

## Recommended Execution Order

1. S1 is implemented; S2, S3, S4 and S5 are accepted.
2. Use retained live `MD-E2E-5` evidence under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/` for regression replay.
3. Re-enter a fresh delivery only if a future dependency change invalidates the accepted live evidence contract.

## Delivery Pack: ADV-CAS-S1 Launcher Visible-App Adapter

- Goal: Implement the Launcher-visible app-server adapter contract from `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S1 Launcher Visible App Adapter.md` for `codex app-server`, `thread/start`, `thread/name/set`, `turn/start` and `thread/list`, with initiating-project cwd and title derivation.
- Non-Goals: Validator fixture implementation, MD-E2E-5 runner implementation, archive implementation, live regression execution.
- Implementation Write-Set: `skills-repo/tools/AgentDeliverySessionLauncher.cs`; `skills-repo/tools/AgentDeliveryCodexAppServerClient.cs`; `docs/doc-workflow.md`; S1 child spec, handoff, orchestration row, S1 fixtures/validator and S1 launch evidence paths listed in the Child Index row.
- Acceptance Signal: Launcher can create evidence with `execution_channel: app_server`, `session_visibility.class: visible_codex_app_session`, matching initiating cwd, exact title, thread id/source/path and prompt/turn proof; `codex exec` path remains headless.
- Next Skill: `spec-change-delivery`.

## Delivery Pack: ADV-CAS-S2 Visible Evidence Validator

- Goal: Define and implement validator behavior for positive visible-app evidence and false-positive negatives.
- Non-Goals: Creating visible sessions; changing test runner behavior beyond fixtures needed for validator.
- Implementation Write-Set To Harden: `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs` or `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`; visible evidence fixtures under `tests/docworkflow-agent-delivery/e2e/fixtures/**`.
- Acceptance Signal: Accepted. Positive app-server evidence passes; headless `codex exec`, `source='exec'`, wrong title, wrong cwd, missing thread, queued-only and unarchived closeout evidence fail with intended classes.
- Next Skill: S3 integration only after remaining dependencies are accepted.

## Delivery Pack: ADV-CAS-S3 Agent Delivery Workflow Test Suite Integration

- Goal: Add `MD-E2E-5` visible Codex-App session workflow testcase and runner contract.
- Non-Goals: replacing mock-only standard gate.
- Implementation Write-Set: test case markdown, visible runner script, README docs, live evidence output tree and summary schema.
- Acceptance Signal: Accepted. Controller-backed live run `20260511T123609Z-md-e2e-5-controller-live` passes final output, S2 visible evidence, S4 control boundary and S5 retained-session archive summary.
- Next Skill: no S3 action; parent closeout may consume accepted evidence.

## Delivery Pack: ADV-CAS-S4 Control Session Boundary

- Goal: Make the control/editing session boundary machine-checkable for MD-E2E-5.
- Non-Goals: Full visible runner implementation unless hardening merges it into S3.
- Implementation Write-Set: accepted changes in S4 child spec/handoff/orchestration row, control-boundary fixtures, `control-boundary-summary.js`, testcase/README sync and non-live `control-boundary` script selector.
- Acceptance Signal: Accepted. Fixture suite reports `RESULT: PASS (9 cases)` and fails direct orchestration, hardening, delivery, closeout, output, mock-substitute and indistinguishable-session false positives.
- Next Skill: no S4 action; continue with S3 delivery.

## Delivery Pack: ADV-CAS-S5 Closeout Archive Support

- Goal: Add closeout archive support for visible Codex-App sessions via app-server `thread/archive` and explicit statuses for non-visible/no-thread evidence.
- Non-Goals: Final MD-E2E-5 runner implementation.
- Implementation Write-Set: accepted changes in `skills-repo/skills/spec-closeout/SKILL.md`; `docs/doc-workflow.md`; `skills-repo/tools/ArchiveVisibleCodexAppSession.cs`; `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`; `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**`; `tests/docworkflow-agent-delivery/e2e/validators/visible-session-closeout-summary.js`; `tests/docworkflow-agent-delivery/README.md`; `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-closeout-archive/**`.
- Acceptance Signal: Accepted. Closeout rejects `READY` if visible sessions remain unarchived unless explicitly accepted; headless and queued/manual evidence get explicit no-archive statuses.
- Next Skill: no S5 action; continue with S3 delivery.

## Session Launch / Queue Evidence

S3 live session evidence is retained in `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/`.

Reason: the accepted external controller run is the operational session launch evidence for `MD-E2E-5`: the parent published `RSW-C1` through `RSW-C5` requests and the external controller launched all five visible child sessions. No further S3 queue handoff is required.

## Mini-Retro

- Was wurde entschieden? S3 is accepted after a retained controller-backed live `MD-E2E-5` pass.
- Was wurde geaendert? S3 Child Index, S3 handoff, child spec, testcase contract and README live-gate wording now point at accepted evidence.
- Was bleibt offen? No S3 work remains open; future re-entry only if accepted dependency contracts change.
- Welche Evidenz/Verification fehlt? None for S3 closeout.
- Welche Skill-/Workflow-Reibung ist aufgefallen? External controller evidence needed an explicit multi-child integration slice before the runner could accept live proof.
- Session-/Kontextzustand: S3 closeout complete; parent-level closeout can consume accepted S1/S2/S3/S4/S5 state.
