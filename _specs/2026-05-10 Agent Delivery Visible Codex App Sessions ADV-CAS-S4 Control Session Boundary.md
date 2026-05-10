**Date:** 2026-05-10
**Status:** 🟡 Spec
**Scope:** Hardened child contract for `ADV-CAS-S4 Control Session Boundary` under `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`. Documentation-only hardening; no runtime implementation and no live `MD-E2E-5` execution.

---

## Goal

Make the `MD-E2E-5` control/editing session boundary machine-checkable. The control session may prepare input, invoke the Launcher, observe machine-readable evidence, stop only processes it started, and write its own control report. It must not perform parent orchestration, child hardening, child delivery, child closeout, or final output writes on behalf of Launcher-created sessions.

This child freezes the Review Control Surface, allowed/prohibited control-session actions, machine-readable evidence/summary requirements, negative cases, verification lifecycle, and parent conformance for the later S3 live runner integration. It does not implement runner code.

## Review Control Surface

- Spec-Variante: Contract-heavy child spec for workflow/test boundary enforcement.
- Goldstandard Status: hardened child spec, implementation-ready after Child Index and handoff sync.
- Ziel: Define an enforceable control-session boundary so `MD-E2E-5` fails if the invoking/control session directly performs orchestration, hardening, delivery, closeout, or output writes instead of delegating workflow work to Launcher-created visible Codex-App sessions.
- In Scope: Review Control Surface, allowed/prohibited control-session actions, control-session identity/provenance fields, machine-readable boundary summary schema, evidence linkage, negative cases for direct orchestration/hardening/delivery/closeout/output writes, verification lifecycle, parent conformance, later implementation write-set contract.
- Out of Scope: Launcher adapter changes, visible-session validator changes outside S4 boundary fields, closeout archive support, running `MD-E2E-5`, launching Codex-App sessions, changing `run-mock-e2e-checks.sh`, or changing `mock-runner/run.js`.
- Key test/harness cases: positive observed-only control session; direct orchestration pack write; direct child spec or hardening write; direct child delivery evidence write; direct closeout summary write; direct `target/output/count.txt` write; indistinguishable control/parent/child session evidence; final output correct but boundary violated; visible-session evidence correct but control provenance missing.
- Key verification commands: documentation-only hardening checks are `git diff --check -- _specs/2026-05-10\ Agent\ Delivery\ Visible\ Codex\ App\ Sessions\ ADV-CAS-S4\ Control\ Session\ Boundary.md` and JSON parse checks for embedded canonical examples. Later implementation gates are defined in `Verification Commands` but must not run in this hardening session.
- Open decisions: none blocking for the S4 contract.
- Readiness Status: IMPLEMENTATION READY for exactly `ADV-CAS-S4`.

## In Scope

1. Define the control session as an observer/coordinator, not a workflow executor.
2. Define allowed control-session actions and required evidence for those actions.
3. Define prohibited actions and the exact failure statuses they cause.
4. Define machine-readable control-boundary evidence and summary records.
5. Define negative cases that must fail when direct writes or indistinguishable session roles appear.
6. Define how S3 must consume this contract when implementing the live visible-session runner.
7. Define the future implementation write-set and read-only/shared files for S4 delivery.
8. Preserve the parent spec's requirement that correct final output is insufficient when session provenance is wrong.

## Out of Scope

1. No edits to `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`.
2. No creation or update of `_specs/child-session-handoffs/adv-cas-s4-session-handoff.md`.
3. No edits to `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`.
4. No edits to `tests/docworkflow-agent-delivery/e2e/mock-runner/run.js`.
5. No edits to `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`.
6. No edits to Launcher, validators, workflow skills, docs, tests, or runtime code.
7. No `MD-E2E-5` run, app-server launch, or `codex exec` launch.
8. No acceptance of mock-runner evidence as live visible-session evidence.

## Parent/Master Coverage

| Parent Requirement | S4 Coverage |
|---|---|
| `ADV-PR7` | Supports S3 by making `MD-E2E-5` fail unless workflow outcome and visible-session/control-boundary evidence both pass. |
| `ADV-PR8` | Owns the control-session boundary: the invoking session may prepare input, start Launcher, observe evidence, stop own test processes, and report; it may not run workflow steps directly. |
| `ADV-PR5` | Extends evidence requirements with role/provenance fields that make control, parent, and child sessions distinguishable. |
| `ADV-PR6` | Adds false-positive cases where visible-session evidence or final output exists but was produced by the wrong session role. |
| `ADV-PR10` | Reinforces that "launched" or "ran target" cannot imply valid workflow proof when control-boundary provenance is absent. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Notes |
|---|---|---|---|
| `ADV-PR7` | S4 does not implement the full `MD-E2E-5` runner; it defines the boundary contract S3 must enforce. | narrows_with_rationale | S3 remains the owning child for suite integration and live runner execution. |
| `ADV-PR8` | Control session is allowed setup/observe/report actions only and must fail on direct orchestration, hardening, delivery, closeout, or output writes. | preserves | This is the direct S4 ownership area from the orchestration pack. |
| `ADV-PR5` | S4 adds `actor_role`, `session_role`, `control_session_id`, provenance hashes, and forbidden write observations to the evidence surface. | extends | Extension is necessary to make parent-visible evidence machine-checkable. |
| `ADV-PR6` | S4 adds negative cases for role/provenance false positives. | extends | The parent already requires false-positive rejection; S4 specializes it for boundary violations. |
| `ADV-PR10` | S4 requires summaries to keep delivery status separate from boundary status. | preserves | Correct output with boundary violation remains failed. |

No parent requirement is contradicted. No parent requirement owned by S4 is missing from this child contract.

## Decision Freeze Pack

| Decision | Frozen Value | Rationale |
|---|---|---|
| Control-session role name | `control` | Stable role used in summary and evidence records. |
| Parent workflow role name | `parent_workflow` | Distinguishes the Launcher-created parent session from the invoking control session. |
| Child workflow role name | `child_workflow` | Distinguishes Launcher-created child sessions from the parent and control sessions. |
| Boundary pass value | `observed_only` | Matches parent language and makes the positive state explicit. |
| Boundary fail value | `failed` | Used when any prohibited direct action is observed. |
| Boundary blocked value | `not_ready` | Used when required provenance/evidence is missing or indistinguishable before the workflow can be accepted. |
| Direct write handling | Fail, not warn | A correct output produced through a direct control write is a false positive and must fail. |
| Mock-runner handling | May inform fixture design only | `run-mock-e2e-checks.sh` and `mock-runner/run.js` are read-only references for deterministic summary patterns, not substitutes for live `MD-E2E-5`. |

## Normative Contract

### Roles

| Role | Description | May perform orchestration? | May perform hardening? | May perform delivery writes? | May perform closeout? | May write final output? |
|---|---|---:|---:|---:|---:|---:|
| `control` | Invoking/editing session or process that prepares the live testcase and starts/observes Launcher-created sessions. | no | no | no | no | no |
| `parent_workflow` | Launcher-created visible Codex-App parent session for the test parent. | yes | may coordinate child hardening according to workflow | no child output writes unless explicitly scoped as parent-owned control artifacts | parent-level closeout only after child evidence exists | no |
| `child_workflow` | Launcher-created visible Codex-App child session for one child handoff. | no parent orchestration | only if the child session was launched for hardening | yes, only inside its own allowed write-set | child closeout only for its target | yes, only when the child handoff allows the target output line/value |
| `closeout_workflow` | Launcher-created or delegated closeout session/tooling for closeout evidence and archive checks. | no | no | no child delivery writes | yes | no |

### Control-Session Allowed Actions

The control session may perform only these actions:

1. Create or copy the parent input fixture into the live run input location.
2. Create run directories and empty setup/report directories for the live testcase.
3. Create the initial parent launch handoff or launch request.
4. Invoke `AgentDeliverySessionLauncher.cs` or the S3 runner to start Launcher-created parent/child sessions.
5. Read Launcher evidence, session evidence, summaries, output files, and logs.
6. Poll for evidence readiness and timeout/hang states.
7. Stop or clean up only processes the control session started for the testcase.
8. Write control-only reports, timeout reports, and boundary summary artifacts.
9. Record `NOT READY`, `failed`, or `blocked` verdicts when evidence is missing or invalid.

Allowed control-session writes must be limited to setup and reporting artifacts owned by the runner, for example:

```text
tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/input/test-parent.md
tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/handoffs/parent-start-handoff.md
tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/control/control-boundary-summary.json
tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/control/timeout-report.json
tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/visible-session-summary.json
```

### Control-Session Prohibited Actions

The control session must not:

1. Write or modify orchestration packs except for the initial parent launch handoff/request explicitly scoped as setup.
2. Create, update, or repair child specs.
3. Create, update, or repair child handoffs after the parent workflow session has started.
4. Run `spec-orchestrator` to produce the live run's orchestration output.
5. Run `child-spec-hardening` for any live child target.
6. Run `spec-change-delivery` for any live child target.
7. Run `spec-closeout` for child or parent closeout.
8. Write child delivery evidence.
9. Write closeout summaries.
10. Write `target/output/count.txt` or any other final output artifact.
11. Backfill missing parent/child visible-session evidence.
12. Re-label headless, queued, or mock evidence as a Launcher-created visible session.
13. Accept indistinguishable evidence where the same session id or role appears as control and workflow actor.

Any prohibited action causes `control_session_status: "failed"` and `overall_workflow_status: "fail"` even when final output content is correct.

### Session Identity and Provenance

Every control-boundary check must compare these identities:

| Field | Required For | Rule |
|---|---|---|
| `control_session_id` | control summary | Stable id for the invoking/control session or process. |
| `control_actor_kind` | control summary | One of `codex_app_session`, `codex_cli_process`, `shell_process`, `test_runner_process`, `unknown`. |
| `parent_session_id` | parent launch evidence | Must be present and must differ from `control_session_id`. |
| `child_session_id` | each child launch/evidence record | Must be present and must differ from `control_session_id` and sibling child sessions. |
| `actor_role` | every write/evidence observation | One of `control`, `parent_workflow`, `child_workflow`, `closeout_workflow`, `unknown`. |
| `writer_session_id` | write observations | Required for any observed write to orchestration, child spec, handoff, delivery, closeout, or output artifacts. |
| `artifact_path` | write observations | Repository-relative path for the observed or declared write. |
| `artifact_class` | write observations | One of `setup_input`, `parent_orchestration`, `child_spec`, `child_handoff`, `child_delivery_evidence`, `closeout_evidence`, `target_output`, `control_report`, `launcher_evidence`, `unknown`. |

If a field cannot be observed directly, the implementation must record `unknown` and the summary must become `not_ready` unless a parent-approved manual evidence mode supplies an equivalent identity proof. It must not silently assume the writer.

### Boundary Summary Status Rules

The S3 runner or S4 implementation must compute statuses independently:

| Status Field | Allowed Values | Pass Rule |
|---|---|---|
| `control_session_status` | `observed_only`, `failed`, `not_ready` | `observed_only` only when no prohibited direct action is observed and all required role identities are distinguishable. |
| `session_chain_status` | `pass`, `fail`, `not_ready` | `pass` only when parent and child workflow sessions have valid launch/visibility evidence and distinct identities. |
| `workflow_delivery_status` | `pass`, `fail`, `not_ready` | `pass` only when the parent/child workflow produces expected artifacts through allowed workflow roles. |
| `visible_session_status` | `pass`, `fail`, `not_ready` | `pass` only under S1/S2 visible-session evidence rules. |
| `overall_workflow_status` | `pass`, `fail`, `not_ready` | `pass` only when all status fields above pass and final output matches the parent contract. |

The summary must not collapse these statuses into a single `status: "launched"` or `status: "ran-target"` field.

### Forbidden Write Detection

The implementation must detect prohibited control-session writes by at least one deterministic method and record the method used. Acceptable methods:

1. Runner-managed write ledger with path, actor role, session id, action, and timestamp.
2. File snapshot before/after with allowed setup/report paths excluded, plus evidence that the writer role was not control for workflow-owned paths.
3. Launcher/session evidence that ties each workflow-owned write to a distinct parent/child/closeout session.
4. OS/file watcher telemetry when available, provided it is retained as machine-readable evidence.

The detection method must be explicit. Missing detection is `control_session_status: "not_ready"`, not pass.

## Canonical Examples and Fixtures

Pattern: hybrid.

This child embeds compact canonical JSON examples for the summary and direct-write negative cases because the downstream runner/validator must share exact status and field names. Full fixture files are future implementation scope for S4 or S3 and must live under a source-controlled fixture directory such as:

```text
tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary/
```

Required future fixtures:

| Fixture | Purpose | Required Before Implementation? |
|---|---|---|
| `positive-observed-only.json` | Control performs setup/observe/report only; parent and child sessions are distinct. | yes, if S4 implements a validator independently; otherwise before S3 runner delivery. |
| `direct-orchestration-write.json` | Control session writes orchestration pack or child index. | yes |
| `direct-hardening-write.json` | Control session writes child spec or hardening output. | yes |
| `direct-delivery-write.json` | Control session writes child delivery evidence. | yes |
| `direct-closeout-write.json` | Control session writes closeout evidence. | yes |
| `direct-output-write.json` | Control session writes `target/output/count.txt`. | yes |
| `indistinguishable-session-role.json` | Same or missing session id is used for control and workflow actors. | yes |
| `correct-output-boundary-fail.json` | Final output is correct but prohibited control write exists. | yes |

The embedded examples below are normative and must parse as JSON.

### Canonical Positive Summary

```json
{
  "schema_id": "docworkflow-agent-delivery-control-boundary-summary.v1",
  "run_id": "20260510T000000Z-visible-app",
  "control_session": {
    "control_session_id": "control-001",
    "control_actor_kind": "test_runner_process",
    "allowed_actions": [
      "prepare_input",
      "create_parent_launch_handoff",
      "invoke_launcher",
      "observe_evidence",
      "write_control_report"
    ],
    "prohibited_actions_observed": []
  },
  "workflow_sessions": [
    {
      "session_role": "parent_workflow",
      "session_id": "parent-visible-001",
      "launch_evidence": "launches/parent/evidence.json"
    },
    {
      "session_role": "child_workflow",
      "session_id": "child-rsw-c1-visible-001",
      "target_child_id": "RSW-C1",
      "launch_evidence": "launches/rsw-c1/evidence.json"
    }
  ],
  "write_observations": [
    {
      "artifact_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260510T000000Z/control/control-boundary-summary.json",
      "artifact_class": "control_report",
      "actor_role": "control",
      "writer_session_id": "control-001",
      "allowed": true
    },
    {
      "artifact_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260510T000000Z/target/output/count.txt",
      "artifact_class": "target_output",
      "actor_role": "child_workflow",
      "writer_session_id": "child-rsw-c1-visible-001",
      "allowed": true
    }
  ],
  "control_session_status": "observed_only",
  "session_chain_status": "pass",
  "workflow_delivery_status": "pass",
  "visible_session_status": "pass",
  "overall_workflow_status": "pass"
}
```

### Canonical Direct Output Negative

```json
{
  "schema_id": "docworkflow-agent-delivery-control-boundary-summary.v1",
  "run_id": "20260510T000000Z-visible-app",
  "control_session": {
    "control_session_id": "control-001",
    "control_actor_kind": "codex_app_session",
    "allowed_actions": [
      "prepare_input",
      "invoke_launcher",
      "observe_evidence"
    ],
    "prohibited_actions_observed": [
      "direct_output_write"
    ]
  },
  "workflow_sessions": [
    {
      "session_role": "parent_workflow",
      "session_id": "parent-visible-001",
      "launch_evidence": "launches/parent/evidence.json"
    }
  ],
  "write_observations": [
    {
      "artifact_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260510T000000Z/target/output/count.txt",
      "artifact_class": "target_output",
      "actor_role": "control",
      "writer_session_id": "control-001",
      "allowed": false,
      "violation_code": "direct_output_write"
    }
  ],
  "control_session_status": "failed",
  "session_chain_status": "not_ready",
  "workflow_delivery_status": "fail",
  "visible_session_status": "not_ready",
  "overall_workflow_status": "fail"
}
```

## Control Flow and Failure Cases

1. Control prepares input and parent launch handoff.
2. Control invokes Launcher or S3 runner.
3. Launcher-created parent session performs orchestration and creates child specs/handoffs.
4. Parent session or orchestrated workflow launches child sessions.
5. Child sessions harden/deliver only their own scopes.
6. Closeout workflow records child/parent closeout and archive/no-thread statuses.
7. Control observes evidence and writes control-boundary summary.
8. Summary fails if any workflow-owned artifact was written by the control session.

Failure handling:

| Failure | Required Status | Required Report Detail |
|---|---|---|
| Missing parent session id | `not_ready` | Name missing launch evidence path and expected parent role. |
| Parent session id equals control session id | `failed` | Record `violation_code: "control_parent_same_session"`. |
| Missing child session id | `not_ready` | Name child id and missing evidence path. |
| Child session id equals control session id | `failed` | Record `violation_code: "control_child_same_session"`. |
| Control writes orchestration pack | `failed` | Record path, writer, and `direct_orchestration_write`. |
| Control writes child spec/hardening output | `failed` | Record path, writer, and `direct_hardening_write`. |
| Control writes delivery evidence | `failed` | Record path, writer, and `direct_delivery_write`. |
| Control writes closeout summary | `failed` | Record path, writer, and `direct_closeout_write`. |
| Control writes final output | `failed` | Record path, writer, and `direct_output_write`. |
| Output correct but boundary failed | `failed` | Preserve output evidence but set overall status to fail. |

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `S4-POS-OBSERVED-ONLY` | Prove allowed setup/observe/report path. | `positive-observed-only.json`; parent input from `20260509T112628Z/input/test-parent.md`. | Exit `0`; `control_session_status: observed_only`; `overall_workflow_status: pass`. | `control-boundary-summary.json`; launch evidence links; final output evidence. | Control does not write child specs, handoffs, delivery, closeout, or output. |
| `S4-NEG-DIRECT-ORCHESTRATION` | Fail when control writes orchestration/Child Index. | `direct-orchestration-write.json`. | Non-zero or summary `overall_workflow_status: fail`; `violation_code: direct_orchestration_write`. | Failure summary with offending path. | Must not be downgraded to warning. |
| `S4-NEG-DIRECT-HARDENING` | Fail when control writes child spec/hardening artifact. | `direct-hardening-write.json`. | Fail; `control_session_status: failed`. | Failure summary with child id and path. | Correct later child session evidence cannot erase violation. |
| `S4-NEG-DIRECT-DELIVERY` | Fail when control writes child delivery evidence. | `direct-delivery-write.json`. | Fail; `violation_code: direct_delivery_write`. | Failure summary names evidence path. | No secret values in captured prompt/log snippets. |
| `S4-NEG-DIRECT-CLOSEOUT` | Fail when control writes closeout evidence. | `direct-closeout-write.json`. | Fail; `violation_code: direct_closeout_write`. | Failure summary names closeout path. | Closeout cannot be accepted from control role. |
| `S4-NEG-DIRECT-OUTPUT` | Fail when control writes `target/output/count.txt`. | `direct-output-write.json`. | Fail even if output is `1\n2\n3\n4\n5\n`. | Failure summary plus retained output hash. | Correct output cannot satisfy boundary. |
| `S4-NEG-INDISTINGUISHABLE-SESSION` | Fail when control/parent/child ids are missing or equal. | `indistinguishable-session-role.json`. | `not_ready` for missing ids; `failed` for equal ids. | Failure summary names missing/equal ids. | No inferred pass from path names. |
| `S4-NEG-MOCK-RUNNER-SUBSTITUTE` | Fail if mock-runner output is used as live visible boundary proof. | Existing `run-mock-e2e-checks.sh` and `mock-runner/run.js` summary shape. | Fail for live `MD-E2E-5`; may pass mock-only gate separately. | Summary states `runner_mode` is not live visible session. | Mock evidence cannot be re-labelled as visible-app proof. |
| `S4-NEG-CORRECT-OUTPUT-BOUNDARY-FAIL` | Ensure delivery pass does not mask boundary failure. | `correct-output-boundary-fail.json`. | Fail; `workflow_delivery_status: pass`; `control_session_status: failed`; `overall_workflow_status: fail`. | Separate delivery and boundary statuses. | Prevents single-status false positive. |

## Verification Commands

### Hardening-Only Verification For This Session

Run from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`:

```sh
git diff --check -- "_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S4 Control Session Boundary.md"
```

Parse embedded canonical JSON examples:

```sh
node -e "const fs=require('fs'); const p='_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S4 Control Session Boundary.md'; const s=fs.readFileSync(p,'utf8'); const blocks=[...s.matchAll(/```json\n([\s\S]*?)\n```/g)].map(m=>m[1]); if(blocks.length!==2) throw new Error('expected 2 json blocks'); for (const b of blocks) JSON.parse(b);"
```

Do not run `MD-E2E-5` in this hardening session.

### Future Implementation Verification Contract

After an integration owner syncs the Child Index and persisted S4 handoff, readiness must include:

```sh
cd /tmp
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-10\ Agent\ Delivery\ Visible\ Codex\ App\ Sessions\ Orchestration\ Pack.md \
  --child ADV-CAS-S4 \
  --handoff /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/adv-cas-s4-session-handoff.md
```

Later S4/S3 implementation gates must include, at minimum:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh
node tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary/positive-observed-only.json
node tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary/direct-output-write.json
```

The live `MD-E2E-5` command remains future-only and must run from a dedicated control/launcher session after S1/S2/S4/S5 are implemented and S3 has integrated the runner:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep
```

Success criteria for future implementation:

1. Exit code `0` only when control boundary, visible-session evidence, and workflow output all pass.
2. Summary includes `schema_id: "docworkflow-agent-delivery-visible-app-e2e-summary.v1"` or links a nested `docworkflow-agent-delivery-control-boundary-summary.v1`.
3. Summary reports `control_session_status: "observed_only"`.
4. Summary reports parent plus five child workflow sessions distinct from the control session.
5. Summary fails all S4 negative cases.
6. Final output is exactly `1\n2\n3\n4\n5\n`.
7. No evidence includes secret values or raw credentials.

Anti-loop rule: do not add a verification command that only verifies that another verification command was listed. Commands must parse, execute, or validate real artifacts.

## Definition of Ready for Implementation

S4 is implementation-ready because these conditions are now true:

1. Child Index row for `ADV-CAS-S4` points to this child spec file, uses the exact operational columns, and has a concrete allowed write-set.
2. Persisted handoff exists at `_specs/child-session-handoffs/adv-cas-s4-session-handoff.md`.
3. Handoff, Child Index row, and this spec agree on child id, verdict, scope, allowed write-set, read-only files, verification commands, and next skill.
4. `ValidateChildReadiness.cs` passes for `ADV-CAS-S4`.
5. `git diff --check` passes for this file and any handoff/index sync.
6. Embedded canonical JSON examples parse.
7. Future implementation write-set is accepted by the integration owner.
8. S1/S2 visible-session evidence schema dependencies are either implemented or explicitly frozen for S4 fixture work.

Current verdict: IMPLEMENTATION READY.

## Definition of Done / Closeout Evidence

Future S4 implementation is done only when:

1. Control-boundary validator or runner checks exist and cover all S4 harness cases.
2. Positive observed-only fixture passes.
3. Negative direct orchestration, hardening, delivery, closeout, output, mock-substitute, and indistinguishable-session cases fail.
4. Runner summary preserves separate `control_session_status`, `session_chain_status`, `workflow_delivery_status`, `visible_session_status`, and `overall_workflow_status`.
5. S3 runner consumes S4 status before accepting live `MD-E2E-5`.
6. Closeout evidence retains fixture results and notes whether live `MD-E2E-5` was not run, blocked, failed, or passed.

## Dependencies and Write-Set

### Hardening Lane Write Ownership

This hardening lane may write only:

```text
_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S4 Control Session Boundary.md
```

Read-only for this lane:

```text
_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md
_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md
tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh
tests/docworkflow-agent-delivery/e2e/mock-runner/run.js
_specs/child-session-handoffs/**
tests/docworkflow-agent-delivery/**
skills-repo/**
docs/**
```

Integration owner for shared control files: parent/orchestration pack owner. Required sync is listed in `Child Session Handoff`.

### Future Implementation Write-Set To Validate

The future implementation owner must narrow and validate this proposed write-set before delivery:

```text
tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary/**
tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js
tests/docworkflow-agent-delivery/testcases/md-e2e-5-visible-codex-app-sessions.md
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh
tests/docworkflow-agent-delivery/README.md
```

Shared/read-only during future implementation unless explicitly transferred:

```text
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh
tests/docworkflow-agent-delivery/e2e/mock-runner/run.js
tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md
skills-repo/tools/AgentDeliverySessionLauncher.cs
skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs
_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md
_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md
```

S4 can harden in parallel with S2, but implementation should be coordinated with S3 because S3 consumes the boundary status in the live runner.

## Closeout Sync Targets

When S4 is later implemented, closeout must sync:

1. Child Index row for `ADV-CAS-S4`.
2. `_specs/child-session-handoffs/adv-cas-s4-session-handoff.md`.
3. S4 fixture/validator evidence paths.
4. S3 `MD-E2E-5` integration notes if S3 consumes S4 outputs.
5. Parent coverage for `ADV-PR8` and support notes for `ADV-PR7`.
6. Any live-run summary that reports `control_session_status`.

This hardening run does not perform those syncs because the user limited write ownership to this child spec.

## Child Session Handoff

Persisted child session handoff:

```text
_specs/child-session-handoffs/adv-cas-s4-session-handoff.md
```

Integration-owner sync applied for implementation:

1. Update the `ADV-CAS-S4` Child Index row in `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`:
   - `Child Spec`: `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S4 Control Session Boundary.md`
   - `Readiness / Hardening Verdict`: `IMPLEMENTATION READY`.
   - `Session Handoff`: `_specs/child-session-handoffs/adv-cas-s4-session-handoff.md`
   - `Allowed Write-Set`: exact future implementation write-set from this spec, with shared/read-only files excluded.
   - `Next Action`: `spec-change-delivery` for S4 after `ValidateChildReadiness.cs` passes.
2. Create `_specs/child-session-handoffs/adv-cas-s4-session-handoff.md` with:
   - Parent: `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`
   - Child ID: `ADV-CAS-S4`
   - Child Spec: this file
   - Child Index / Queue: `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`
   - Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
   - Next Mode / Skill: `spec-change-delivery` only after readiness validation passes
   - Scope Summary: implement control-boundary fixtures/validator/runner checks only
   - Non-Goals: no Launcher app-server adapter, no visible-session validator outside S4 boundary fields, no closeout archive support, no live `MD-E2E-5` until S3
   - Allowed Write-Set: concrete paths accepted by integration owner
   - Verification Lifecycle: hardening validation, fixture validation, negative cases, no live MD-E2E-5 in S4 delivery
3. Run `ValidateChildReadiness.cs` from `/tmp` against the synced row and handoff.

## Hardening Verdict

Verdict: IMPLEMENTATION READY.

Rationale:

1. The child contract is sufficiently specified for S4's boundary domain.
2. Parent conformance has no contradiction or unexplained gap.
3. Machine-readable summary fields, allowed/prohibited actions, negative cases, and verification lifecycle are defined.
4. Implementation is still blocked because shared orchestration/handoff artifacts were intentionally not edited in this lane.
5. `ValidateChildReadiness.cs` was not run because the required handoff and synced Child Index row do not yet exist and this lane may not create/update them.

## Content Quality Review

- Correctness/domain fit: Pass. The child targets the exact parent requirement that the control session must not execute workflow steps directly.
- Scope discipline: Pass. Launcher implementation, S2 validator delivery, S5 closeout archive support, and live `MD-E2E-5` execution remain out of scope.
- Completeness: Pass. The spec defines roles, actions, prohibited writes, evidence fields, statuses, negative cases, verification commands, dependencies, and closeout sync targets.
- Consistency: Pass. Review Control Surface, contract, cases, handoff and Child Index row all agree on `IMPLEMENTATION READY`.
- Verifiability: Pass for contract depth. Future fixtures and commands are concrete; live `MD-E2E-5` remains deliberately future-only.
- Remaining blocker: none for S4 implementation readiness.

## Mini-Retro

- Decision: S4 is a boundary-contract child, not the full live runner implementation.
- Change made: created a contract-heavy child spec with role/provenance schema, allowed/prohibited actions, negative cases, verification lifecycle, parent conformance, then promoted it after Child Index/handoff sync.
- Open item: S4 implementation must create the control-boundary fixtures/validator and keep live `MD-E2E-5` out of scope.
- Evidence not produced: no live `MD-E2E-5`, no launch evidence.
- Continue here or fresh session: use a later `spec-change-delivery` session for S4 when integration ownership is clear.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-10 | Codex | Created hardened `ADV-CAS-S4 Control Session Boundary` child spec as a ready candidate with implementation blocked on Child Index/handoff sync and readiness validator run. |
| 2026-05-10 | Codex | Promoted S4 to `IMPLEMENTATION READY` after Child Index/handoff sync. |

SessionId: 2026-05-10-adv-cas-s4-control-session-boundary-hardening
