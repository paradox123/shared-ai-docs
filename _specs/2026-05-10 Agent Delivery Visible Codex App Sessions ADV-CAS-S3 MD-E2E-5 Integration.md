**Date:** 2026-05-11
**Status:** 🟢 Accepted
**Scope:** Accepted child delivery for `ADV-CAS-S3` Agent Delivery Workflow Test Suite integration of `MD-E2E-5`. The live visible Codex-App regression runner now passes against retained controller-backed parent plus five child session evidence.
**SessionId:** adv-cas-s3-hardening-20260511

---

## Goal

`ADV-CAS-S3` integrates the parent-visible session requirements into the Agent Delivery Workflow Test Suite as `MD-E2E-5`.

The accepted runner starts from the real-session workflow parent fixture, launches the parent workflow and five child workflow sessions through the S1 app-server Launcher path, validates every parent/child visible-session evidence record through the accepted S2 validator, consumes the accepted S4 control-boundary summary, consumes the accepted S5 archive/no-thread closeout summary, and fails unless the final output is exactly:

```text
1
2
3
4
5
```

## Review Control Surface

- Spec-Variant: Contract-heavy integration child spec.
- Goldstandard Status: accepted S3 delivery; S1 is implemented, S2/S4/S5 are accepted prerequisites, and retained controller-backed live `MD-E2E-5` evidence passes.
- Goal: Add `MD-E2E-5` as the live visible Codex-App session regression that gates both final workflow output and visible-session evidence.
- In Scope: runner CLI contract; visible-session summary schema; run directory/evidence tree; parent plus five child visible-session evidence requirements; S2 validator coupling; S4 control-boundary coupling; S5 closeout/archive coupling; final-output gate; README/testcase synchronization; implementation handoff.
- Out of Scope: Launcher app-server adapter implementation; visible evidence validator implementation; archive tool implementation; replacing `run-mock-e2e-checks.sh all --keep`; accepting mock/headless/queued evidence as visible-session proof.
- Key Test / Harness Cases: positive Parent+5 Child visible workflow; final output correct but visible evidence missing fails; visible evidence present but final output wrong fails; headless/queued/source-exec/wrong-title/wrong-cwd child evidence fails; control-session takeover fails; unarchived visible session fails; mock-runner substitute fails; setup/usage errors exit distinctly.
- Key Verification Commands: hardening rehearsal: `bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`; `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh control-boundary`; `node tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary`; `dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence`; `dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout --mode validate`; `cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- --index /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-10\ Agent\ Delivery\ Visible\ Codex\ App\ Sessions\ Orchestration\ Pack.md --child ADV-CAS-S3 --handoff /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/adv-cas-s3-session-handoff.md`; accepted delivery replay: `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id 20260511T123609Z-md-e2e-5-controller-live --keep --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`; controller fixture replays; live control-boundary validation; live archive-summary validation; canonical OpenSpec spec validation; `git diff --check`.
- Open Decisions / Blockers: none.
- Readiness Status: ACCEPTED for exactly `ADV-CAS-S3`.

## Session Briefing

- Mode / Skill: `child-spec-hardening`.
- Source of Truth: parent spec `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`; orchestration pack `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; S1 launcher adapter evidence contract; accepted S2 validator spec/tool/fixtures; accepted S4 control-boundary validator/fixtures; accepted S5 archive tool/fixtures; existing live real-session workflow fixture under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/`.
- Target Child Goal: harden S3 so a fresh `spec-change-delivery` session can implement the live `MD-E2E-5` runner without guessing schema, status, failure, evidence, or closeout semantics.
- Non-Goals: no live `MD-E2E-5` execution; no runtime Launcher changes; no validator changes; no archive implementation; no mock-only standard gate replacement.
- Expected Deliverable: this hardened child spec, synchronized S3 Child Index row, persisted S3 handoff, and testcase/README wording that point at the future live runner contract.
- Verification / Review Path: run S2/S4/S5 fixture gates and command-contract rehearsals now; run the live `--run-id <id> --keep` gate only in the later implementation/control workflow.
- Open Decisions: none.

## In Scope

1. Define the future `MD-E2E-5` runner CLI, exit codes, run directory, and summary schema.
2. Define how the runner consumes S1 launch evidence, S2 visible evidence validation, S4 control-boundary validation, and S5 archive/no-thread evidence.
3. Define positive, negative, setup-error, blocked, and redaction/security cases.
4. Define delivery preflight and closeout evidence requirements for a later implementation run.
5. Preserve the existing mock-only standard gate and make `MD-E2E-5` an additional live, opt-in gate.
6. Keep S3 serialized because it owns the cross-slice live integration.

## Out of Scope

1. No live visible Codex-App sessions in this hardening run.
2. No `AgentDeliverySessionLauncher.cs` or `AgentDeliveryCodexAppServerClient.cs` edits.
3. No `ValidateVisibleCodexAppSessionEvidence.cs`, `ArchiveVisibleCodexAppSession.cs`, S4 validator, or S5 fixture implementation.
4. No OpenSpec archive execution for S3 during hardening.
5. No direct SQLite mutation, UI/sidebar screenshot automation, or manual backfill of historical evidence.
6. No replacement, weakening, or aliasing of `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`.

## Parent/Master Coverage

| Parent Requirement | S3 Coverage | Status |
|---|---|---|
| `ADV-PR7` | Primary owner. Adds `MD-E2E-5` live suite integration and summary gate. | covered_by_implementation_ready_contract |
| `ADV-PR2` | Consumes S1 app-server Launcher evidence for parent and child visible sessions. | covered_by_dependency |
| `ADV-PR5` | Requires parent plus five child visible-session evidence records with S2-visible fields. | covered_by_accepted_S2_contract |
| `ADV-PR6` | Fails headless, queued, source-exec, wrong title, wrong cwd, missing-thread and output-only false positives. | covered_by_cases |
| `ADV-PR8` | Consumes S4 `control_session_status: "observed_only"` and fails control takeover. | covered_by_accepted_S4_contract |
| `ADV-PR9` | Consumes S5 closeout archive summary and fails unarchived visible sessions. | covered_by_accepted_S5_contract |
| `ADV-PR10` | Keeps "launched" separate from visible success and preserves mock/live gate distinction. | covered_by_contract |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `ADV-PR7` | S3 owns the live visible-session suite integration and final runner summary. | preserves | Implement in S3 delivery only after this hardening handoff. |
| `ADV-PR2` | S3 does not change Launcher internals; it requires S1 app-server evidence for every workflow role. | preserves | Consume S1 evidence fields and reject headless/queued substitutes. |
| `ADV-PR5`, `ADV-PR6` | S3 calls the accepted S2 validator before a visible evidence record can count. | preserves | Do not duplicate or weaken S2 validation logic. |
| `ADV-PR8` | S3 requires S4's accepted control-boundary status and negative cases. | preserves | Embed or link a S4 summary in every live run. |
| `ADV-PR9` | S3 requires S5 archive/no-thread closeout summary before final pass. | preserves | Do not call live archive unless the implementation session explicitly opts in through S5 tooling. |
| `ADV-PR10` | S3 keeps the mock-only standard gate intact and adds a separate live opt-in gate. | preserves | README and testcase must describe both gates without aliasing them. |

No parent contradiction remains. S3 is serialized because it integrates all predecessor contracts.

## Decision Freeze Pack

Frozen for S3 delivery:

1. The live runner command to implement is `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep`.
2. The runner is an additional live gate; `run-mock-e2e-checks.sh all --keep` remains the mock-only standard gate.
3. The live parent fixture is the real-session workflow parent under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md`, or a byte-for-byte equivalent fixture copied into the new run directory.
4. The workflow child ids are `RSW-C1`, `RSW-C2`, `RSW-C3`, `RSW-C4`, and `RSW-C5`.
5. The parent visible workflow session and each child workflow session must have distinct visible Codex-App evidence. The control session cannot be counted as any workflow session.
6. A visible evidence record counts only after `ValidateVisibleCodexAppSessionEvidence.cs` accepts it under the S2 contract.
7. `control_session_status` must be exactly `observed_only` for final pass.
8. S5 archive summary `overall_archive_status` must be `READY` for final pass; `READY_NO_SESSION_EVIDENCE` is not sufficient for a live visible run.
9. Final output must equal `1\n2\n3\n4\n5\n` and its SHA-256 must be `f6b49467f595b1a44e442c198b3df4d221e88efcaabc26254f8e0ad4f79b6242`.
10. Setup/usage problems exit `2`; semantic workflow failures exit `1`; a fully valid live run exits `0`.
11. Machine-readable summaries must not include prompt bodies, API tokens, app-server raw environment, or unredacted transcript text beyond paths/hashes and allowed protocol method/status summaries.

## Normative Contract

### Runner CLI

The S3 implementation must extend `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh` without removing the existing S4 `control-boundary` fixture selector.

Required selectors and modes:

| Command | Required Behavior |
|---|---|
| `run-visible-app-session-workflow-checks.sh --help` | Print usage, selectors, live-run warning, and exit `0`. |
| `run-visible-app-session-workflow-checks.sh control-boundary` | Replay S4 control-boundary fixtures and exit according to the S4 validator. |
| `run-visible-app-session-workflow-checks.sh --run-id <id> --keep` | Run the live `MD-E2E-5` visible-session workflow for the supplied run id, retain evidence, and exit `0` only when every S3 pass condition is satisfied. |

Required implementation options:

| Option | Required Behavior |
|---|---|
| `--run-id <id>` | Required for live mode. `<id>` must be path-safe: letters, numbers, dot, underscore, hyphen. |
| `--keep` | Retain live run evidence. S3 delivery should keep evidence for accepted runs. |
| `--initiating-project-cwd <path>` | Optional explicit app-visible project context; default is the repository root only when no current visible parent context is available, and the summary must record that fallback. |
| `--timeout-seconds <n>` | Optional bounded wait for visible-session, delivery, closeout, and archive evidence. Timeout produces `overall_workflow_status: "not_ready"` and exit `1`. |

The implementation may add narrower helper options, but the accepted delivery gate remains the `--run-id <id> --keep` form.

### Run Directory

For `--run-id <id>`, the runner must use:

```text
tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/
  input/test-parent.md
  control/control-boundary-summary.json
  control/timeout-report.json
  handoffs/parent-start-handoff.md
  launches/parent/evidence.json
  launches/rsw-c1/evidence.json
  launches/rsw-c2/evidence.json
  launches/rsw-c3/evidence.json
  launches/rsw-c4/evidence.json
  launches/rsw-c5/evidence.json
  visible-session-summary.json
  closeout/archive-summary.json
  target/output/count.txt
```

The runner may create additional child specs, delivery evidence, app-server transcripts, and closeout files below the same run directory. It must not write outside the run directory except through source-controlled runner/test documentation changes made during implementation.

### Summary Schema

Every live run must write `visible-session-summary.json` with:

```json
{
  "schema_id": "docworkflow-agent-delivery-visible-app-e2e-summary.v1",
  "run_id": "20260511T000000Z-adv-cas-s3",
  "testcase_id": "MD-E2E-5",
  "parent": "_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md",
  "parent_identifier": "ADV-CAS-1",
  "input_parent_fixture": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/input/test-parent.md",
  "overall_workflow_status": "pass",
  "visible_session_status": "pass",
  "control_session_status": "observed_only",
  "archive_status": "READY",
  "final_output_status": "pass",
  "mock_gate_status": "not_applicable_live_md_e2e_5",
  "final_output": {
    "path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/target/output/count.txt",
    "expected_text": "1\n2\n3\n4\n5\n",
    "expected_sha256": "f6b49467f595b1a44e442c198b3df4d221e88efcaabc26254f8e0ad4f79b6242",
    "actual_sha256": "f6b49467f595b1a44e442c198b3df4d221e88efcaabc26254f8e0ad4f79b6242"
  },
  "parent_visible_session_evidence": {
    "target_id": "RSW-PARENT",
    "evidence_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/launches/parent/evidence.json",
    "visible_validator_status": "pass"
  },
  "child_visible_session_evidence": [
    {
      "target_id": "RSW-C1",
      "evidence_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/launches/rsw-c1/evidence.json",
      "visible_validator_status": "pass"
    },
    {
      "target_id": "RSW-C2",
      "evidence_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/launches/rsw-c2/evidence.json",
      "visible_validator_status": "pass"
    },
    {
      "target_id": "RSW-C3",
      "evidence_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/launches/rsw-c3/evidence.json",
      "visible_validator_status": "pass"
    },
    {
      "target_id": "RSW-C4",
      "evidence_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/launches/rsw-c4/evidence.json",
      "visible_validator_status": "pass"
    },
    {
      "target_id": "RSW-C5",
      "evidence_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/launches/rsw-c5/evidence.json",
      "visible_validator_status": "pass"
    }
  ],
  "control_boundary_summary": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/control/control-boundary-summary.json",
  "closeout_archive_summary": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T000000Z-adv-cas-s3/closeout/archive-summary.json",
  "secret_redaction_status": "pass"
}
```

Allowed status values:

| Field | Allowed Values | Pass Requirement |
|---|---|---|
| `overall_workflow_status` | `pass`, `fail`, `not_ready` | `pass` only when all other status dimensions pass. |
| `visible_session_status` | `pass`, `fail`, `not_ready` | `pass` only when parent plus five child visible evidence records pass S2 validation and have distinct app-visible thread ids. |
| `control_session_status` | `observed_only`, `failed`, `not_ready` | Must be `observed_only`. |
| `archive_status` | `READY`, `NOT_READY`, `READY_NO_SESSION_EVIDENCE` | Must be `READY`; `READY_NO_SESSION_EVIDENCE` is invalid for live S3. |
| `final_output_status` | `pass`, `fail`, `not_ready` | Must be `pass` and exact byte content must match the expected text. |
| `mock_gate_status` | `not_applicable_live_md_e2e_5` | Must not be reported as `pass` for the live gate. |

### Pass Conditions

A live `MD-E2E-5` run passes only when all conditions below are true:

1. Parent workflow and `RSW-C1` through `RSW-C5` are started through Launcher-created visible Codex-App sessions.
2. Every visible evidence record uses S1 `agent-delivery.session-launch.v2` app-server/manual-visible fields and passes the S2 visible validator.
3. Parent and child thread ids are non-empty and distinct from each other and from the control session.
4. No evidence record is `headless_cli_session`, `queued_manual_start`, `traceable_but_not_visible`, `source: "exec"`, wrong-title, wrong-cwd, missing-thread, empty-turn, prompt-hash mismatch, or manually backfilled.
5. The S4 control-boundary summary reports `control_session_status: "observed_only"` and no prohibited direct control writes.
6. The S5 archive summary reports `overall_archive_status: "READY"` and has explicit per-record archive statuses for every parent/child evidence record.
7. `target/output/count.txt` exists and its byte content is exactly `1\n2\n3\n4\n5\n`.
8. The summary and retained evidence redact prompt bodies, secrets, auth tokens, app-server raw environment, and transcript payloads that are not needed for proof.

## Canonical Examples and Fixtures

Pattern: **Hybrid**.

The canonical positive summary is embedded above and must remain parseable JSON. Full executable live fixtures are produced during S3 implementation under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/`. Source-controlled predecessor fixtures remain:

| Fixture / Tool | Purpose | Required Before S3 Implementation? |
|---|---|---|
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/**` | S2 positive and false-positive visible evidence cases. | yes, already accepted |
| `tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary/**` | S4 control-boundary positive and direct-write/session-role negatives. | yes, already accepted |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**` | S5 archive/no-thread/retained/failure closeout cases. | yes, already accepted |
| `tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/**` | S3 live run evidence, summaries, child launches, final output and closeout evidence. | in scope for S3 delivery |

## Control Flow and Failure Cases

The runner must execute or observe this order:

1. Prepare the live run directory and parent fixture.
2. Create a parent launch handoff/request for a visible parent workflow session.
3. Launch or require Launcher-created parent workflow evidence through S1.
4. Parent workflow creates child specs/handoffs for `RSW-C1` through `RSW-C5`.
5. Child sessions are launched serially because they share `target/output/count.txt`.
6. After each child, collect visible evidence, child delivery evidence, and closeout evidence.
7. After `RSW-C5`, verify final output and parent closeout.
8. Validate visible evidence through S2, control boundary through S4, archive/no-thread state through S5.
9. Write `visible-session-summary.json` and exit according to the summary verdict.

Failure handling:

1. Setup/usage errors such as missing `--run-id`, invalid run id, unreadable fixture roots, invalid JSON summary, or missing validators exit `2`.
2. Workflow semantic failures such as missing visible evidence, wrong final output, control takeover, unarchived visible session, timeout, or secret leak exit `1`.
3. The runner must not convert unavailable live app-server capability into pass. It must report `not_ready` with retained evidence.

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `S3-POSITIVE-VISIBLE-WORKFLOW` | Prove parent plus five child visible workflow sessions and exact output. | Live run directory with S1 app-server evidence, S2 passes, S4 observed-only, S5 READY. | exit `0`; `overall_workflow_status: "pass"`. | `visible-session-summary.json`, six launch evidence records, control summary, archive summary, `target/output/count.txt`. | No secrets or prompt bodies in summary; all thread ids distinct. |
| `S3-OUTPUT-ONLY-FALSE-POSITIVE` | Fail when output is correct but visible evidence is missing/headless/queued. | Correct `count.txt` plus missing or S2-failing launch evidence. | exit `1`; `visible_session_status: "fail"` or `not_ready`. | Failure summary retaining output proof and failed validator classes. | Correct bytes cannot override missing visible proof. |
| `S3-VISIBLE-ONLY-FALSE-POSITIVE` | Fail when visible evidence exists but output is wrong or incomplete. | Six visible records plus wrong `count.txt`. | exit `1`; `final_output_status: "fail"`. | Failure summary with expected/actual hash. | Visible sessions cannot override wrong delivery result. |
| `S3-HEADLESS-OR-QUEUED-CHILD` | Fail non-visible child evidence. | S2 fixture classes `headless_cli_session`, `queued_manual_start`, `source='exec'`. | exit `1`; `visible_session_status: "fail"`. | Failed S2 validator evidence. | `status: launched` alone never counts. |
| `S3-WRONG-TITLE-OR-CWD` | Fail app-visible evidence for the wrong title or initiating cwd. | S2 wrong-title/wrong-cwd fixtures or live equivalent. | exit `1`; visible validator failure class retained. | Validator output and offending evidence path. | No manual relabeling or cwd fallback pass. |
| `S3-CONTROL-TAKEOVER` | Fail when control session writes workflow artifacts or final output. | S4 direct-write fixtures or live boundary summary with prohibited action. | exit `1`; `control_session_status: "failed"`. | Control-boundary summary. | Correct output still fails. |
| `S3-UNARCHIVED-VISIBLE` | Fail visible sessions left unarchived without retained-session acceptance. | S5 unarchived/failed/proof_failed fixtures or live equivalent. | exit `1`; `archive_status: "NOT_READY"`. | Archive summary and S5 failure class. | Retention accepted only with explicit user acceptance fields. |
| `S3-MOCK-RUNNER-SUBSTITUTE` | Fail mock-only evidence relabelled as live visible proof. | Existing mock runner outputs or S4 `mock-runner-substitute` fixture. | exit `1`; `overall_workflow_status: "not_ready"` or `fail`. | Failure summary naming mock substitute. | `run-mock-e2e-checks.sh` evidence cannot satisfy live S3. |
| `S3-SETUP-ERROR` | Fail invalid usage/setup distinctly. | Missing `--run-id`, invalid run id, missing fixture/validator. | exit `2`. | Setup error on stderr; no pass summary. | Setup errors cannot be downgraded to skipped success. |
| `S3-SECRET-REDACTION` | Prevent sensitive leakage in retained summary. | Live transcript paths and launch evidence with redaction scan. | exit `1` if secret pattern appears; otherwise pass dimension. | Redaction status in summary. | No auth tokens, raw env, prompt bodies, or unneeded transcript payloads. |

## Verification Commands

Run these from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs` unless the command explicitly changes directory.

Hardening and command-contract rehearsal:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh control-boundary
node tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout --mode validate
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- --index /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-10\ Agent\ Delivery\ Visible\ Codex\ App\ Sessions\ Orchestration\ Pack.md --child ADV-CAS-S3 --handoff /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/adv-cas-s3-session-handoff.md
git diff --check
```

Future S3 delivery gate, not run during hardening:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep
```

Delivery success criteria:

1. The future live command exits `0`.
2. `visible-session-summary.json` validates the S3 schema and reports all pass statuses.
3. Parent plus five child visible evidence records pass S2 validation.
4. S4 control-boundary validator accepts the run summary.
5. S5 archive validator accepts the closeout archive summary.
6. Final output equals `1\n2\n3\n4\n5\n` and the SHA-256 matches the frozen value.
7. `git diff --check` passes.

Anti-loop rule: do not add commands that only verify that verification commands were listed. Each command must either parse/lint the runner, replay accepted fixture gates, validate child readiness, or execute the live S3 runner.

## Historical Definition of Ready for Implementation

Before delivery, S3 was ready for a fresh `spec-change-delivery` session when:

1. This child spec reported `IMPLEMENTATION READY`.
2. The Child Index row for `ADV-CAS-S3` reported `IMPLEMENTATION READY` and pointed to `_specs/child-session-handoffs/adv-cas-s3-session-handoff.md`.
3. The S3 handoff verdict was `IMPLEMENTATION READY`.
4. S1 is implemented and S2/S4/S5 are accepted in the Child Index.
5. The hardening verification commands above pass, except the future live delivery gate remains explicitly not run.
6. The implementation session accepts that live app-server execution is in scope and retains evidence.

## Definition of Done / Closeout Evidence

S3 delivery is accepted because the implementation/closeout sessions retained:

1. The exact command used: `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep`.
2. `tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/visible-session-summary.json`.
3. Parent plus five child launch evidence records under the live run directory.
4. S2 validator output for all six visible records.
5. S4 control-boundary summary with `control_session_status: "observed_only"`.
6. S5 archive summary with `overall_archive_status: "READY"` or explicit accepted retention evidence for every visible thread.
7. Final `target/output/count.txt` and SHA-256 proof.
8. Negative evidence for at least output-only, visible-only, control-takeover, unarchived-visible and mock-substitute false positives.
9. README/testcase sync that clearly distinguishes mock-only standard gate from live `MD-E2E-5`.
10. `git diff --check` and any S3 runner/test validator commands used during implementation.

## Dependencies and Write-Set

Serial dependencies:

1. S1 app-server Launcher adapter is implemented.
2. S2 visible evidence validator is accepted.
3. S4 control-boundary fixture/validator slice is accepted.
4. S5 closeout archive support is accepted.
5. S3 implementation must run serially after these dependencies because it owns the live integration runner.

Implementation allowed write-set:

- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S3 MD-E2E-5 Integration.md`
- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`
- `_specs/child-session-handoffs/adv-cas-s3-session-handoff.md`
- `tests/docworkflow-agent-delivery/testcases/md-e2e-5-visible-codex-app-sessions.md`
- `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`
- `tests/docworkflow-agent-delivery/README.md`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/**`
- `tests/docworkflow-agent-delivery/e2e/evidence/*visible-app*`

Shared / read-only for S3 implementation unless a follow-up is explicitly approved:

- `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- `skills-repo/tools/AgentDeliveryCodexAppServerClient.cs`
- `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`
- `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`
- `skills-repo/tools/ArchiveVisibleCodexAppSession.cs`
- `skills-repo/skills/spec-closeout/SKILL.md`
- `docs/doc-workflow.md`
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/e2e/mock-runner/run.js`
- `tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js`
- `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/**`
- `tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary/**`
- `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**`

Integration owner: `ADV-CAS-S3` owns runner/testcase/README live integration changes. S3 must route back to S1/S2/S4/S5 only if the accepted contracts cannot support the live runner without changing their owned tools or fixtures.

## Closeout Sync Targets

After S3 delivery:

1. Update the S3 Child Index row to `ACCEPTED` only after live evidence exists.
2. Update `_specs/child-session-handoffs/adv-cas-s3-session-handoff.md` with delivery evidence, retained run id, and closeout status.
3. Update this child spec's status to implemented/accepted according to the actual closeout evidence.
4. Keep the mock-only standard gate documentation intact and add live `MD-E2E-5` evidence paths.
5. Archive or close any S3 OpenSpec ledger only if one is created during delivery.

Closeout sync completed on 2026-05-11:

- S3 Child Index row updated to `ACCEPTED`.
- S3 handoff updated with retained live evidence and closeout status.
- OpenSpec archived to `openspec/changes/archive/2026-05-11-agent-delivery-md-e2e-5-external-controller-integration/`.
- README and `MD-E2E-5` testcase point at accepted controller-backed live evidence.

## Child Session Handoff

Persisted handoff: `_specs/child-session-handoffs/adv-cas-s3-session-handoff.md`.

The accepted implementation evidence is retained under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/`.

## Hardening Verification Record

Hardening verification run on 2026-05-11:

| Check | Result |
|---|---|
| Embedded JSON parse | Passed; canonical positive summary parsed as JSON. |
| `bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh` | Passed; exit `0`. |
| S4 control-boundary replay through runner selector | Passed; `RESULT: PASS (9 cases)`. |
| S4 control-boundary direct validator replay | Passed; `RESULT: PASS (9 cases)`. |
| S2 visible evidence replay | Passed; `RESULT: PASS (11 cases)`. |
| S5 archive fixture replay | Passed; `RESULT: PASS (10 cases)`. |
| `ValidateChildReadiness.cs` for `ADV-CAS-S3` from `/tmp` | Passed; child readiness validation passed. |
| `git diff --check` | Passed; exit `0`. |
| Live `MD-E2E-5` command | Not run by design; belongs to the next S3 `spec-change-delivery` control workflow. |

## Delivery Implementation Record

S3 delivery implementation on 2026-05-11 added the executable live runner command:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep
```

Retained rehearsal evidence:

| Check | Result |
|---|---|
| `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id 20260511T103700Z-adv-cas-s3-rehearsal --keep` | Retained `visible-session-summary.json` with `overall_workflow_status: "not_ready"` and exit `1` because no live parent/child visible-session evidence, S4 summary, S5 archive summary, or final output existed for that run id. |

This is implementation evidence for the runner behavior, not an accepted live `MD-E2E-5` pass. The accepted live pass is recorded below.

## Accepted Closeout Record

S3 accepted closeout on 2026-05-11 retained a controller-backed live `MD-E2E-5` run:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id 20260511T123609Z-md-e2e-5-controller-live --keep --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
```

Result: `MD-E2E-5 pass`.

Retained evidence:

- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/controller/controller-summary.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/visible-session-summary.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/control/control-boundary-summary.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/closeout/archive-summary.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/target/output/count.txt`

Closeout verification replay:

| Check | Result |
|---|---|
| Live `MD-E2E-5` runner replay | Passed; `MD-E2E-5 pass`. |
| Controller MVP fixture replay | Passed; `RESULT: PASS (6 controller fixture cases)`. |
| Controller MD-E2E-5 fixture replay | Passed; `RESULT: PASS (2 controller fixture cases)`. |
| Live control-boundary summary validation | Passed; `RESULT: PASS (1 cases)`. |
| Live archive summary validation | Passed; `PASS: archive-summary.json expected=pass actual=pass`. |
| `openspec validate agent-delivery-md-e2e-5-external-controller-integration --strict` | Passed before archive. Post-archive replay by change id is stale because the change is archived; canonical spec replay is listed below. |
| `openspec validate docworkflow-agent-delivery-testsuite --strict` | Passed after archive; canonical testsuite spec is valid. |
| `git diff --check` | Passed before archive and will be replayed after closeout sync. |

OpenSpec closeout:

- Archived change: `openspec/changes/archive/2026-05-11-agent-delivery-md-e2e-5-external-controller-integration/`
- Canonical spec updated: `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`

## Hardening Verdict

`ACCEPTED` for exactly `ADV-CAS-S3`.

S3 is closed with retained live controller-backed `MD-E2E-5` evidence. No further S3 delivery action is required unless a future regression changes the accepted S1/S2/S4/S5 contracts.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-11 | Codex | Hardened S3 into an implementation-ready live `MD-E2E-5` integration contract consuming accepted S1/S2/S4/S5 prerequisites. |
| 2026-05-11 | Codex | Implemented the S3 live runner command and retained a not-ready rehearsal summary proving missing live evidence does not pass. |
| 2026-05-11 | Codex | Accepted S3 after retained controller-backed live `MD-E2E-5` pass and archived OpenSpec change `agent-delivery-md-e2e-5-external-controller-integration`. |
