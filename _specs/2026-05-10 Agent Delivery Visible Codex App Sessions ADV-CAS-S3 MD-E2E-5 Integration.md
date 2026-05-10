**Date:** 2026-05-10
**Status:** 🟡 Spec
**Scope:** Child `ADV-CAS-S3` for Agent Delivery Workflow Test Suite integration of `MD-E2E-5`. This is a blocked integration child; it does not authorize running the live regression.

---

## Review Control Surface

- Spec-Variante: Contract-heavy integration child spec.
- Goldstandard Status: blocked hardened draft.
- Ziel: Define the future `MD-E2E-5` visible Codex-App session regression contract so the Agent Delivery Workflow Test Suite gates both final workflow output and visible-session evidence.
- In Scope: testcase contract, visible runner command contract, summary schema, evidence tree, final-output gate, parent plus five child visible-session evidence requirements, dependency intake from S1/S2/S4/S5.
- Out of Scope: running `MD-E2E-5`; implementing Launcher app-server adapter; implementing validator or archive support; bypassing control-session boundary; replacing `run-mock-e2e-checks.sh all --keep`.
- Key Test / Harness Cases: positive Parent+5 Child visible workflow; correct output but missing visible evidence fails; visible evidence passes but output wrong fails; headless/queued/wrong-title/wrong-cwd/unarchived/control-takeover negatives fail.
- Key Verification Commands: future only: `bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`; `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep` from a launcher/control session; `git diff --check`.
- Open Blockers: S1 app-server adapter not delivered; S2 validator not delivered; S4 control-boundary enforcement not promoted; S5 archive support not delivered.
- Readiness Status: NEEDS HARDENING - blocked by S1/S2/S4/S5.

## Parent Coverage

| Parent Requirement | Coverage |
|---|---|
| `ADV-PR7` | Owns `MD-E2E-5` test suite integration. |
| `ADV-PR2`, `ADV-PR5`, `ADV-PR6` | Consumes S1 visible launch evidence and S2 validator results. |
| `ADV-PR8` | Consumes S4 control-session boundary proof. |
| `ADV-PR9` | Consumes S5 archive/no-thread proof. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `ADV-PR7` | S3 adds the live visible-session testcase and runner contract. | preserves | Wait for prerequisite slices before implementation. |
| `ADV-PR8` | S3 reports control-session status but does not define all boundary negatives. | defers_to_child | S4 owns boundary fixtures. |
| `ADV-PR9` | S3 requires archive/no-thread evidence but does not implement archive calls. | defers_to_child | S5 owns closeout archive support. |
| `ADV-PR2`, `ADV-PR5`, `ADV-PR6` | S3 consumes adapter/validator outputs. | preserves | S1/S2 must be accepted or explicitly available before S3 delivery. |

## Normative Contract

The future runner command is:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep
```

The runner summary MUST include:

```json
{
  "schema_id": "docworkflow-agent-delivery-visible-app-e2e-summary.v1",
  "overall_workflow_status": "pass",
  "visible_session_status": "pass",
  "control_session_status": "observed_only",
  "final_output_status": "pass",
  "parent_visible_session_evidence": "path/to/evidence.json",
  "child_visible_session_evidence": [
    "path/to/c1/evidence.json",
    "path/to/c2/evidence.json",
    "path/to/c3/evidence.json",
    "path/to/c4/evidence.json",
    "path/to/c5/evidence.json"
  ]
}
```

Pass requires all of these:

1. Parent plus five child sessions have distinct `visible_codex_app_session` evidence.
2. No session evidence is `headless_cli`, `source='exec'`, queued-only, wrong-title or wrong-cwd.
3. Control session status is observed-only.
4. Closeout archive/no-thread evidence is complete.
5. Final output file is exactly `1\n2\n3\n4\n5\n`.

## Acceptance And Harness Cases

| Case | Purpose | Expected Result |
|---|---|---|
| `S3-POSITIVE-VISIBLE-WORKFLOW` | Parent + five child visible sessions, final output and archive evidence all pass. | pass |
| `S3-OUTPUT-ONLY-FALSE-POSITIVE` | Final output is correct but visible evidence is missing/headless/queued. | fail |
| `S3-VISIBLE-ONLY-FALSE-POSITIVE` | Visible evidence exists but output is wrong or incomplete. | fail |
| `S3-CONTROL-TAKEOVER` | Control session writes child artifacts or output directly. | fail |
| `S3-UNARCHIVED-VISIBLE` | Visible sessions remain unarchived without accepted retained-session note. | fail |

## Dependencies And Write-Set

Future implementation write-set after prerequisites:

- `tests/docworkflow-agent-delivery/testcases/md-e2e-5-visible-codex-app-sessions.md`
- `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`
- `tests/docworkflow-agent-delivery/README.md`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/**`
- `tests/docworkflow-agent-delivery/e2e/evidence/*visible-app*`
- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S3 MD-E2E-5 Integration.md`
- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`
- `_specs/child-session-handoffs/adv-cas-s3-session-handoff.md`

Read-only until prerequisites are delivered:

- `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`
- `skills-repo/skills/spec-closeout/SKILL.md`
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/e2e/mock-runner/run.js`

## Verification Lifecycle

- Hardening validation: `ValidateChildReadiness.cs --allow-non-ready` until prerequisites are accepted.
- Delivery preflight: shell syntax and fixture schema checks.
- Delivery gate: live `run-visible-app-session-workflow-checks.sh --run-id <id> --keep`, but only in a later launcher/control workflow.
- Closeout: retain visible-session summary, final output, control-boundary and archive evidence.

## Hardening Verdict

`NEEDS HARDENING - blocked by S1/S2/S4/S5`.

S3 must remain serialized. It is the integration child, not a parallel implementation lane.

