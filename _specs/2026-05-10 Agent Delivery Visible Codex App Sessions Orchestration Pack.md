**Date:** 2026-05-10
**Status:** 🟡 Spec
**Scope:** Parent/Child orchestration pack for `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`. No runtime implementation, no live MD-E2E-5 execution.

---

## Review Control Surface

- Spec-Variante: Delivery Orchestration Pack for a contract-heavy workflow/tooling parent spec.
- Goldstandard Status: candidate control pack; child specs are generated as delivery-pack slices and require hardening before implementation.
- Ziel: Split the visible Codex-App Agent Delivery change into bounded Child Slices with coverage, dependencies, hardening queue, allowed next actions and one leading next child.
- In Scope: Spec sizing verdict, Child Index, Coverage Matrix, Dependencies, Hardening Queue, Parallel Work Control Surface, delivery-pack skeletons and leading child handoff.
- Out of Scope: Runtime implementation, Launcher code edits, validator code edits, test runner edits, live `MD-E2E-5` execution, `codex app-server` session launch, `codex exec` launch, app-server archive execution.
- Wichtigste Test-/Harness-Cases: visible-app positive app-server evidence; `codex exec`/`source='exec'` negative; wrong title; wrong cwd; missing thread; queued-only; final-output-correct-but-visible-evidence-missing; visible-evidence-pass-but-output-wrong; unarchived visible sessions.
- Wichtigste Verification Commands: child hardening may rehearse help/schema commands only; later implementation gates include visible-session validator cases, shell syntax checks, targeted tests, and `run-visible-app-session-workflow-checks.sh --run-id <id> --keep` only in a later launcher/control session.
- Offene Entscheidungen: No blocking product decision for orchestration. UI/sidebar screenshot proof and long-lived app-server socket remain non-blocking follow-ups.
- Readiness Status: `ADV-CAS-S1` is `IMPLEMENTATION READY` for one bounded Launcher adapter delivery. `ADV-CAS-S2` through `ADV-CAS-S5` remain `NEEDS HARDENING`; no `MD-E2E-5` live run is authorized by this pack.

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
| ADV-CAS-S2 | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S2 Visible Evidence Validator.md` | `ADV-PR1`, `ADV-PR5`, `ADV-PR6`; supports `ADV-PR10` | `IMPLEMENTATION READY`; re-hardened after S1 and synchronized to `agent-delivery.session-launch.v2` visible evidence fields | `child-session-handoffs/adv-cas-s2-session-handoff.md` | Proposed: `openspec/changes/agent-delivery-visible-session-validator/` | S1 implemented; S2 must precede S5/S3 validation use | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S2 Visible Evidence Validator.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `_specs/child-session-handoffs/adv-cas-s2-session-handoff.md`; `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`; `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`; `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/**`; `tests/docworkflow-agent-delivery/e2e/validators/visible-app-session-evidence.js`; `openspec/changes/agent-delivery-visible-session-validator/**` | Rehearsed: `ValidateAgentDeliveryLaunchEvidence.cs --help`; S1 visible fixture validator; `ValidateChildReadiness.cs`. Delivery: implement reusable visible evidence validator and fixture family; keep existing launch evidence fixture regression green; do not run MD-E2E-5 | Retain S2 validator fixture summaries; no live MD-E2E-5 evidence is created by S2 | If S1 delivery changes evidence names, re-enter S2 hardening before S5/S3 | Start fresh `spec-change-delivery` for ADV-CAS-S2 |
| ADV-CAS-S3 | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S3 MD-E2E-5 Integration.md` | `ADV-PR7`; consumes `ADV-PR2`, `ADV-PR5`, `ADV-PR6`, `ADV-PR8`, `ADV-PR9` | `NEEDS HARDENING`; serialized integration child, blocked until S1/S2/S4/S5 are delivered or promoted | `child-session-handoffs/adv-cas-s3-session-handoff.md` | Proposed: `openspec/changes/agent-delivery-visible-md-e2e-5-suite/` | Depends on S1 adapter, S2 validator, S4 control-boundary and S5 closeout archive contracts; must not replace mock-only standard gate | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S3 MD-E2E-5 Integration.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `_specs/child-session-handoffs/adv-cas-s3-session-handoff.md`; `tests/docworkflow-agent-delivery/testcases/md-e2e-5-visible-codex-app-sessions.md`; `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`; `tests/docworkflow-agent-delivery/README.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/**`; `tests/docworkflow-agent-delivery/e2e/evidence/*visible-app*` | Future only: `bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`; `run-visible-app-session-workflow-checks.sh --run-id <id> --keep` in launcher/control session; final output equals `1\n2\n3\n4\n5\n`. Do not run in this hardening session | MD-E2E-5 closeout must retain summary JSON, visible evidence and final output evidence | If live runner cannot prove control boundary or archive support, route to S4/S5 before S3 delivery | Continue `child-spec-hardening` only after S1/S2/S4/S5 readiness |
| ADV-CAS-S4 | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S4 Control Session Boundary.md` | `ADV-PR8`; supports `ADV-PR7` | `IMPLEMENTATION READY`; promoted after Child Index/handoff sync for a bounded control-boundary fixture/validator slice | `child-session-handoffs/adv-cas-s4-session-handoff.md` | Proposed: `openspec/changes/agent-delivery-visible-control-boundary/` | Can implement independently after S2 if desired; S3 consumes final control-boundary status before live runner success | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S4 Control Session Boundary.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `_specs/child-session-handoffs/adv-cas-s4-session-handoff.md`; `tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary/**`; `tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js`; `tests/docworkflow-agent-delivery/testcases/md-e2e-5-visible-codex-app-sessions.md`; `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`; `tests/docworkflow-agent-delivery/README.md`; `openspec/changes/agent-delivery-visible-control-boundary/**` | Rehearsed: draft JSON parse/whitespace and `ValidateChildReadiness.cs`; Delivery: control-boundary positive/negative fixture validation; do not run live MD-E2E-5 | Closeout must report control/editing session as observed-only; no live MD-E2E-5 run in S4 delivery | If S3 owns runner implementation entirely, keep S4 as accepted precondition and avoid double-editing runner files | Start fresh `spec-change-delivery` for ADV-CAS-S4 after/alongside S2 as integration owner allows |
| ADV-CAS-S5 | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S5 Closeout Archive Support.md` | `ADV-PR9`; supports `ADV-PR5`, `ADV-PR7`, `ADV-PR10` | `NEEDS HARDENING`; draft archive contract exists, but implementation waits for S2 validator schema and S1 delivery evidence shape | `child-session-handoffs/adv-cas-s5-session-handoff.md` | Proposed: `openspec/changes/agent-delivery-visible-session-closeout-archive/` | Depends on S1 visible evidence fields and S2 validator classes; may implement before S3 final live pass | `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S5 Closeout Archive Support.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `_specs/child-session-handoffs/adv-cas-s5-session-handoff.md`; `skills-repo/skills/spec-closeout/SKILL.md`; `docs/doc-workflow.md`; `skills-repo/tools/ArchiveVisibleCodexAppSession.cs`; `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`; `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**`; `tests/docworkflow-agent-delivery/e2e/validators/visible-session-closeout-summary.js`; `tests/docworkflow-agent-delivery/README.md` | Draft checked embedded JSON and whitespace. Next hardening: rehearse `thread/archive` schema, sync S1/S2 field names, create archive fixtures, then `ValidateChildReadiness.cs` | Reject final READY while visible sessions remain unarchived unless explicitly accepted; no live MD-E2E-5 run in S5 hardening | If archive API is unavailable, record blocked/manual retained-session decision before S3 pass | Continue `child-spec-hardening` after S2 schema |

## Coverage Matrix

| Parent Requirement | Owning Child | Coverage Status | Notes |
|---|---|---|---|
| `ADV-PR1` | `ADV-CAS-S2` primary; S1/S5 consume | pending | Terminology exists in parent; child validator must make it enforceable. |
| `ADV-PR2` | `ADV-CAS-S1` | implemented | Launcher app-server adapter delivered and smoke-proven via `thread/start`, `thread/name/set`, `turn/start` and `thread/list`. |
| `ADV-PR3` | `ADV-CAS-S1` | implemented | Evidence now records `initiating_project_cwd`, `target_workspace` and `project_cwd_source`; app-server smoke observed matching cwd. |
| `ADV-PR4` | `ADV-CAS-S1`, validated by S2 | implemented | Launcher derives `ADV-CAS-1: Implementation - ...` titles; S2 still owns downstream negative validation. |
| `ADV-PR5` | `ADV-CAS-S1`, `ADV-CAS-S2`, `ADV-CAS-S5` | partial | S1 freezes launcher evidence fields; S2/S5 still own broader validation/archive behavior. |
| `ADV-PR6` | `ADV-CAS-S2` | pending | Negative cases are identified but need fixtures/validator contract. |
| `ADV-PR7` | `ADV-CAS-S3` | pending | MD-E2E-5 must be added later; not run here. |
| `ADV-PR8` | `ADV-CAS-S4`, consumed by S3 | pending | Control boundary must be enforced by runner/evidence, not just prose. |
| `ADV-PR9` | `ADV-CAS-S5`, consumed by S3 | pending | Archive support must exist before MD-E2E-5 can pass. |
| `ADV-PR10` | S1/S2/S5 plus docs sync in S3/S5 | pending | Docs already contain some wording; child delivery must sync remaining stale semantics. |

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
| `ADV-PR8` | S4 owns control-session boundary contract. | preserves | S3 consumes the enforcement or merges only after S4 hardening. |
| `ADV-PR9` | S5 owns archive tool/closeout skill support. | preserves | S3 final success depends on S5 capability. |

## Hardening Queue

| Order | Child | Hardening Need | Blocking Questions For Hardening |
|---|---|---|---|
| complete | `ADV-CAS-S1` | Hardened implementation-ready child spec for app-server adapter, initiating cwd and title/evidence contract. | Frozen default: explicit visible adapter state such as `--adapter codex-app-server`; per-run `codex app-server --listen stdio://`; no `MD-E2E-5` in S1. |
| 2 | `ADV-CAS-S2` | Harden validator fixtures and negative/positive evidence schema. | Is validator a new file or extension of `ValidateAgentDeliveryLaunchEvidence.cs`? Which fixture paths are normative? |
| 3 | `ADV-CAS-S4` | Harden control-session boundary cases. | Which artifacts may the control runner write, and how is direct child artifact mutation detected? |
| 4 | `ADV-CAS-S5` | Harden archive support and closeout skill/tool contract. | Is archive a Launcher helper mode, closeout companion tool, or both? |
| 5 | `ADV-CAS-S3` | Harden MD-E2E-5 suite integration after S1/S2/S4/S5 contracts. | Exact runner summary schema and opt-in gate semantics; live execution remains later-only. |

## Parallel Work Control Surface

| Work Block | Lane Mode | Allowed Parallelism | Shared / Read-only Files | Integration Owner |
|---|---|---|---|---|
| S1 delivery | implementation | Serial leading slice; ready for one fresh `spec-change-delivery` session. | Parent spec, app-server spike evidence, S2/S3/S4/S5 child drafts and downstream validator/runner/archive files stay read-only. | S1 delivery session. |
| S2 hardening | spec hardening | Can start after S1 freezes evidence schema; can overlap with S4. | S1 child spec read-only after schema freeze. | S2 hardening session. |
| S4 hardening | spec hardening | Can run in parallel with S2. | Live runner files read-only until S3 or S4 implementation lane. | S4 hardening session. |
| S5 hardening | spec hardening | Can start after S1/S2 schema shape is known. | `spec-closeout` and docs read-only until S5 delivery. | S5 hardening session. |
| S3 hardening/delivery | spec hardening then implementation | Serialized after S1/S2/S4/S5 because it integrates final live workflow. | Mock runner baseline remains read-only and must not be replaced. | S3 integration owner. |

## Recommended Execution Order

1. Start a fresh `spec-change-delivery` session for only `ADV-CAS-S1`.
2. After S1 delivery, harden S2 and S4 against the implemented evidence shape; S2 and S4 may be parallel hardening lanes.
3. Harden S5 after S1/S2 schema shape is known.
4. Harden and deliver S5 before the final MD-E2E-5 live pass.
5. Harden S3 last, then deliver the MD-E2E-5 integration and run the live regression only in a later launcher/control session.

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
- Acceptance Signal: Positive app-server evidence passes; headless `codex exec`, `source='exec'`, wrong title, wrong cwd, missing thread, queued-only and unarchived closeout evidence fail.
- Next Skill: `child-spec-hardening` after S1 schema freeze.

## Delivery Pack: ADV-CAS-S3 Agent Delivery Workflow Test Suite Integration

- Goal: Add `MD-E2E-5` visible Codex-App session workflow testcase and runner contract.
- Non-Goals: Running MD-E2E-5 in this orchestration session; replacing mock-only standard gate.
- Implementation Write-Set To Harden: test case markdown, visible runner script, README docs, live evidence output tree and summary schema.
- Acceptance Signal: Later control/launcher run passes only when final output and visible-session evidence both pass.
- Next Skill: `child-spec-hardening` after S1/S2/S4/S5 contracts.

## Delivery Pack: ADV-CAS-S4 Control Session Boundary

- Goal: Make the control/editing session boundary machine-checkable for MD-E2E-5.
- Non-Goals: Full visible runner implementation unless hardening merges it into S3.
- Implementation Write-Set To Harden: control prompt contract, runner boundary checks, negative fixtures for direct artifact mutation and indistinguishable sessions.
- Acceptance Signal: Suite reports `control_session_status: observed_only` or fails when control session orchestrates, hardens, delivers, closes out, or writes child artifacts/output directly.
- Next Skill: `child-spec-hardening`.

## Delivery Pack: ADV-CAS-S5 Closeout Archive Support

- Goal: Add closeout archive support for visible Codex-App sessions via app-server `thread/archive` and explicit statuses for non-visible/no-thread evidence.
- Non-Goals: Final MD-E2E-5 runner implementation.
- Implementation Write-Set To Harden: `skills-repo/skills/spec-closeout/SKILL.md`; app-server archive helper/tool if needed; closeout fixtures; docs sync.
- Acceptance Signal: Closeout rejects `READY` if visible sessions remain unarchived unless explicitly accepted; headless and queued/manual evidence get explicit no-archive statuses.
- Next Skill: `child-spec-hardening` after S1/S2 schema.

## Session Launch / Queue Evidence

No Agent Delivery Session Launch/Queue Evidence was created in the orchestration or S1 hardening sessions.

Reason: the current Launcher is itself in scope for S1 and launching/queueing through the current `codex exec`-based adapter would create exactly the headless evidence class this parent spec is replacing. The next `ADV-CAS-S1` implementation session should start from `_specs/child-session-handoffs/adv-cas-s1-session-handoff.md` as a manual fresh session until the visible-app Launcher adapter exists.

## Mini-Retro

- Was wurde entschieden? The parent is too large for a single change; `ADV-CAS-S1` is now the implementation-ready leading child, while S2/S3/S4/S5 remain hardening or delivery follow-ups.
- Was wurde geaendert? Added this orchestration pack, hardened the S1 child spec, synchronized the S1 row and S1 handoff. No runtime implementation or live test was run.
- Was bleibt offen? S1 runtime delivery, then S2/S4 hardening, S5 archive support and S3 `MD-E2E-5` integration.
- Welche Evidenz/Verification fehlt? No runtime visible-app launch evidence exists yet; no launch/queue evidence was created because current Launcher evidence is headless; no MD-E2E-5 run by design.
- Welche Skill-/Workflow-Reibung ist aufgefallen? The current Launcher queue path is still `codex exec`-centric, so it should not be used as proof for visible-app transition during this orchestration.
- Session-/Kontextzustand: Continue with a fresh `spec-change-delivery` session for `ADV-CAS-S1`.
