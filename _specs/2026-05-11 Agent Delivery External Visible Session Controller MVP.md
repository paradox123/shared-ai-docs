**Date:** 2026-05-11
**Status:** 🟢 Accepted
**Scope:** MVP controller for externally orchestrated visible Codex App parent/child sessions. This replaces nested child `codex app-server --listen stdio://` launches from inside a parent app-server session with controller-owned launches from outside the parent turn.
**SessionId:** external-visible-session-controller-mvp-20260511

---

## Goal

Build a minimal external controller that can run the smallest visible parent/child workflow without nesting an app-server launch inside a parent Codex turn.

The controller starts the visible parent session from outside the parent, waits for the parent to publish one child launch request artifact, starts that child visible session from the controller process, then writes a controller summary that proves whether the workflow reached a real child session or blocked with retained evidence.

This MVP exists to unblock the later `MD-E2E-5` redesign. It does not implement the full parent plus five child workflow.

## Review Control Surface

- Spec-Variante: Implementation-ready MVP tool spec with explicit artifact contracts and state machine.
- Goldstandard Status: Hardened for one bounded `spec-change-delivery` implementation slice.
- Ziel: Add an external visible-session controller that launches parent and child sessions from outside app-server-backed Codex turns.
- In Scope: controller CLI; request/response artifact contract; controller state machine; timeout/failure semantics; minimal parent-child live fixture; controller summary; process cleanup boundary; verification commands.
- Out of Scope: full `MD-E2E-5` runner migration; five-child orchestration; archive closeout; changing `AgentDeliverySessionLauncher.cs` app-server protocol; reusing a parent stdio transport; treating blocked/nested evidence as success.
- Wichtigste Test-/Harness-Cases: parent launch succeeds and publishes one child request; controller launches one child from outside the parent; child writes `target/output/controller-spike.txt`; child launch blocks/fails and controller writes deterministic summary; parent fails to publish request before timeout; malformed request is rejected without launching.
- Wichtigste Verification Commands: post-implementation `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --help`; deterministic `--fixture` suite; live minimal controller run with `--run-dir tests/docworkflow-agent-delivery/e2e/session-workflow-live/<timestamp>-external-controller-mvp`; summary assertion; `git diff --check`.
- Offene Entscheidungen: none blocking. Future optimization of a long-lived app-server transport is deferred.
- Readiness Status: IMPLEMENTATION READY for exactly the controller MVP.

## Context

The nested app-server spike under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T092105Z-nested-app-server-spike/` proved:

1. A visible parent launch initiated from outside the Codex turn can succeed.
2. A child launch initiated from inside that parent turn creates a launcher run directory but blocks at JSON-RPC `initialize`.
3. The launcher now writes deterministic blocked evidence with `app_server_initialize_timeout`.

Therefore the controller must own every visible-session launch process. Parent sessions may request child work, but must not spawn `codex app-server --listen stdio://` themselves.

## In Scope

1. Add `skills-repo/tools/AgentDeliveryVisibleSessionController.cs`.
2. Define and implement a controller CLI that launches one parent and one child for the MVP.
3. Define request artifacts written by the parent session and consumed by the controller.
4. Define response artifacts written by the controller and consumed by later parent closeout work.
5. Define a controller state machine with deterministic terminal statuses.
6. Create a minimal live fixture under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/<timestamp>-external-controller-mvp/`.
7. Run one minimal parent-child live test after implementation and retain evidence.

## Out of Scope

1. No full `MD-E2E-5` parent plus five child workflow.
2. No archive or closeout integration.
3. No direct changes to the existing `run-visible-app-session-workflow-checks.sh` live runner.
4. No nested child launch from inside the parent session.
5. No reuse of the parent's private stdio app-server transport.
6. No cleanup of unrelated existing live-run artifacts.
7. No claim of `READY` for `ADV-CAS-S3` or `MD-E2E-5`.

## Design Decision

The controller is a technical orchestration process, not a new workflow owner.

- Parent session owns workflow reasoning and child request production.
- Child session owns child delivery.
- Controller owns process launch, polling, timeout, cleanup of its own child processes, and summary evidence.

The controller must run from a normal shell/control process, outside the app-server-backed parent turn. That is the mechanism that avoids the observed nested `initialize` hang.

## Parent Request Publication Contract

The parent handoff used by this MVP must make the parent session publish exactly one controller request and then stop. The parent session is not responsible for child process orchestration.

Required parent behavior:

1. Create `<run-dir>/controller/requests/` if missing.
2. Write one complete JSON request to `<run-dir>/controller/requests/CTRL-C1.request.json` using an atomic write pattern: write a temporary file below the same directory, then rename it to the final `.request.json` name.
3. Reference only the pre-created child handoff and output paths below `<run-dir>`.
4. Do not run `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs`, `codex app-server`, or any other child launcher command.
5. Do not edit the request after publication.

The controller does not trust the parent blindly. It validates the request before launching the child and rejects malformed or unsafe requests without invoking a launcher.

## CLI Contract

The MVP tool is:

```sh
dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- [options]
```

Required live-mode options:

| Option | Meaning |
|---|---|
| `--run-dir <dir>` | Existing or creatable run directory for the controller fixture and evidence. |
| `--parent-handoff <path>` | Handoff that starts the visible parent session. |
| `--parent-target-id <id>` | Target id for the parent launch, for example `CTRL-PARENT`. |
| `--initiating-project-cwd <path>` | Visible Codex App project cwd passed to the launcher. |

Optional options:

| Option | Default | Meaning |
|---|---:|---|
| `--fixture <dir>` | n/a | Replay deterministic controller request/response fixtures without launching live Codex sessions. Mutually exclusive with live `--run-dir` mode. |
| `--request-timeout-seconds <n>` | `300` | Max time to wait for a child request after parent launch. |
| `--parent-timeout-minutes <n>` | `30` | App-server turn timeout passed to the parent launcher. |
| `--child-timeout-minutes <n>` | `30` | App-server turn timeout passed to the child launcher. |
| `--app-server-request-timeout-seconds <n>` | `60` | JSON-RPC request timeout passed to launcher app-server adapter. |
| `--poll-interval-ms <n>` | `1000` | Poll interval for request/response artifacts. |
| `--summary-out <path>` | `<run-dir>/controller/controller-summary.json` | Controller summary path. |
| `--help` | n/a | Print usage and exit `0`. |

Mode rules:

1. `--fixture <dir>` runs fixture validation only and must not start `codex`, `dotnet run AgentDeliverySessionLauncher.cs`, or `codex app-server`.
2. Live mode requires `--run-dir`, `--parent-handoff`, `--parent-target-id`, and `--initiating-project-cwd`.
3. `--fixture` and live mode options are mutually exclusive except `--summary-out` when a fixture wants an explicit report path.

Exit codes:

| Exit | Meaning |
|---:|---|
| `0` | Live mode: parent launched, request accepted, child launched, child evidence status is `launched`, and configured output assertion passes. Fixture mode: all fixture cases match expected outcomes. |
| `1` | Semantic workflow failure or blocked child launch with retained evidence. |
| `2` | Usage/setup error, malformed request, missing required files, or unsafe path. |

## Directory Contract

The MVP run directory uses:

```text
<run-dir>/
  input/parent.md
  handoffs/parent-handoff.md
  handoffs/ctrl-c1-handoff.md
  child-specs/ctrl-c1.md
  controller/requests/
  controller/responses/
  controller/controller-summary.json
  launches/parent/
  launches/children/
  target/output/controller-spike.txt
  delivery-evidence/ctrl-c1/
```

The controller may create missing `controller/`, `launches/`, `target/`, and `delivery-evidence/` directories. It must not write outside `<run-dir>` except by invoking `AgentDeliverySessionLauncher.cs` with explicit `--out` paths below `<run-dir>`.

`<run-dir>` must resolve to a path below `tests/docworkflow-agent-delivery/e2e/session-workflow-live/` for the live MVP verification. The controller should reject live runs whose configured output, request, response, launcher, or expected-output paths escape `<run-dir>` after full path normalization.

Process cleanup boundary:

1. The controller may terminate only subprocesses it started directly.
2. It must not kill the Codex desktop app, unrelated `codex app-server` processes, or pre-existing launcher/test processes.
3. On timeout, the controller records the timeout state and then performs best-effort cleanup of its own active subprocess tree.

## Request Artifact Contract

The parent session publishes exactly one child request in the MVP:

```text
<run-dir>/controller/requests/CTRL-C1.request.json
```

Request schema:

```json
{
  "schema_id": "agent-delivery.visible-session-controller.request.v1",
  "request_id": "CTRL-C1",
  "created_at": "2026-05-11T00:00:00Z",
  "requested_by": {
    "target_id": "CTRL-PARENT",
    "role": "parent"
  },
  "child": {
    "target_id": "CTRL-C1",
    "handoff_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/handoffs/ctrl-c1-handoff.md",
    "expected_output_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/target/output/controller-spike.txt",
    "expected_output_text": "controller child reached\n"
  },
  "launch": {
    "agent": "codex",
    "adapter": "codex-app-server",
    "mode": "launch",
    "initiating_project_cwd": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
    "out": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/launches/children"
  }
}
```

Normative request rules:

1. `schema_id` must be exactly `agent-delivery.visible-session-controller.request.v1`.
2. `request_id` must equal `child.target_id`.
3. `requested_by.target_id` must equal the CLI `--parent-target-id`.
4. `child.handoff_path`, `child.expected_output_path`, and `launch.out` must resolve below the configured `<run-dir>`.
5. `launch.initiating_project_cwd` must equal the normalized CLI `--initiating-project-cwd`.
6. `launch.agent` must be `codex`, `launch.adapter` must be `codex-app-server`, and `launch.mode` must be `launch`.
7. Request files are immutable after acceptance. The controller records the SHA-256 of the accepted request bytes.
8. Malformed or unsafe requests produce a response with `status: "rejected"` and controller exit `2`; they must not invoke the launcher.

## Launcher Invocation Contract

The controller invokes the existing launcher rather than reimplementing visible app-server session mechanics.

Parent launch command shape:

```sh
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff <parent-handoff> \
  --target-id <parent-target-id> \
  --mode launch \
  --agent codex \
  --adapter codex-app-server \
  --initiating-project-cwd <initiating-project-cwd> \
  --out <run-dir>/launches/parent \
  --app-server-timeout-minutes <parent-timeout-minutes> \
  --app-server-request-timeout-seconds <app-server-request-timeout-seconds>
```

Child launch command shape:

```sh
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff <request.child.handoff_path> \
  --target-id <request.child.target_id> \
  --mode launch \
  --agent codex \
  --adapter codex-app-server \
  --initiating-project-cwd <request.launch.initiating_project_cwd> \
  --out <request.launch.out> \
  --app-server-timeout-minutes <child-timeout-minutes> \
  --app-server-request-timeout-seconds <app-server-request-timeout-seconds>
```

Launcher result rules:

1. The controller records the exact argument vector, exit code, stdout path if captured, stderr path if captured, resolved launcher run directory, and evidence paths in the summary/response.
2. The controller determines launcher status from `evidence.json` when present. Exit code alone is not enough.
3. If `evidence.json` is missing, the launch result is `failed` unless the controller itself timed out the subprocess.
4. If evidence status is `blocked`, the controller result is `blocked` and evidence paths must be retained.
5. If the launcher writes `app_server_initialize_timeout`, the controller must surface that blocker without converting it to success.

## Response Artifact Contract

The controller writes:

```text
<run-dir>/controller/responses/CTRL-C1.response.json
```

Response schema:

```json
{
  "schema_id": "agent-delivery.visible-session-controller.response.v1",
  "request_id": "CTRL-C1",
  "request_sha256": "sha256",
  "status": "launched",
  "created_at": "2026-05-11T00:00:00Z",
  "completed_at": "2026-05-11T00:00:00Z",
  "launcher": {
    "command": "dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- ...",
    "exit_code": 0,
    "run_dir": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/launches/children/20260511T000000Z-ctrl-c1",
    "evidence_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/launches/children/20260511T000000Z-ctrl-c1/evidence.json",
    "transcript_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/launches/children/20260511T000000Z-ctrl-c1/app-server-transcript.jsonl",
    "stderr_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/launches/children/20260511T000000Z-ctrl-c1/app-server-stderr.log"
  },
  "output_assertion": {
    "path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/target/output/controller-spike.txt",
    "expected_text": "controller child reached\n",
    "actual_text_sha256": "sha256",
    "status": "pass"
  },
  "blockers": [],
  "warnings": []
}
```

For rejected requests, the same response schema is used with `status: "rejected"`, `launcher: null`, and `output_assertion.status: "not_checked"`.

Allowed `status` values:

| Status | Meaning |
|---|---|
| `launched` | Child launcher exited `0`, child evidence status is `launched`, and output assertion passes. |
| `blocked` | Child launcher exited non-zero with retained evidence status `blocked`. |
| `failed` | Child launcher exited non-zero, evidence status is `failed`, missing, or incompatible. |
| `rejected` | Request failed schema/path/safety validation before launching. |
| `timeout` | Controller timed out waiting for a request or launcher completion. |

Allowed `output_assertion.status` values: `pass`, `fail`, `not_checked`, `missing`.

Response rules:

1. A response must be written for every discovered request, including rejected requests. If JSON parsing fails, derive `request_id` from the filename pattern `<request-id>.request.json`; if that pattern is absent, use `request_id: "unknown"` and write `<run-dir>/controller/responses/unknown.response.json`.
2. If no request appears before timeout, the controller writes only the summary because no request id exists.
3. A rejected request must include blockers and `launcher: null`.
4. A blocked or failed launch must preserve launcher evidence paths if any were produced.
5. A response must not include prompt bodies, raw transcript text, tokens, environment variables, or secret-like values.

## Controller Summary Contract

The controller writes `<run-dir>/controller/controller-summary.json`:

```json
{
  "schema_id": "agent-delivery.visible-session-controller.summary.v1",
  "run_dir": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>",
  "status": "pass",
  "started_at": "2026-05-11T00:00:00Z",
  "completed_at": "2026-05-11T00:00:00Z",
  "states": [
    {
      "state": "initialized",
      "entered_at": "2026-05-11T00:00:00Z",
      "exited_at": "2026-05-11T00:00:00Z",
      "status": "completed"
    },
    {
      "state": "parent_launching",
      "entered_at": "2026-05-11T00:00:00Z",
      "exited_at": "2026-05-11T00:00:00Z",
      "status": "completed"
    }
  ],
  "parent": {
    "target_id": "CTRL-PARENT",
    "launcher_exit_code": 0,
    "evidence_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/launches/parent/.../evidence.json",
    "status": "launched"
  },
  "requests": [
    {
      "request_id": "CTRL-C1",
      "request_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/controller/requests/CTRL-C1.request.json",
      "response_path": "tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/controller/responses/CTRL-C1.response.json",
      "status": "launched"
    }
  ],
  "blockers": [],
  "warnings": []
}
```

Allowed summary `status` values: `pass`, `blocked`, `failed`, `timeout`, `setup_error`.

## Controller State Machine

The controller state machine is linear for the MVP and must be recorded in `summary.states`.

| State | Entry Action | Success Transition | Failure Transition |
|---|---|---|---|
| `initialized` | Parse CLI, resolve paths, create controller directories. | `parent_launching` | `setup_error` |
| `parent_launching` | Invoke `AgentDeliverySessionLauncher.cs` for parent with `--adapter codex-app-server`. | `waiting_for_request` when parent evidence status is `launched`. | `failed` or `blocked` based on parent evidence/exit. |
| `waiting_for_request` | Poll `<run-dir>/controller/requests/*.request.json`. | `validating_request` when one request appears. | `timeout` when no request appears before `--request-timeout-seconds`. |
| `validating_request` | Validate schema, ids, paths, adapter, request hash. | `child_launching` | `writing_summary` with response status `rejected` and summary status `setup_error`. |
| `child_launching` | Invoke `AgentDeliverySessionLauncher.cs` for child from controller process. | `validating_child_result` after launcher exits. | `timeout` if launcher exceeds configured timeout. |
| `validating_child_result` | Read child evidence and expected output. | `writing_summary` with response status `launched`, `blocked`, or `failed`. | `writing_summary` with response status `failed`. |
| `writing_summary` | Write response and summary JSON. | terminal `pass`, `blocked`, `failed`, `timeout`, or `setup_error`. | terminal `failed` if summary cannot be written. |

Terminal state rules:

1. `pass` only if parent evidence is `launched`, child response is `launched`, and output assertion is `pass`.
2. `blocked` if child evidence is retained with `status: "blocked"`.
3. `failed` if launcher evidence is missing, incompatible, or semantically failed.
4. `timeout` if request or launcher wait exceeds configured timeout.
5. `setup_error` if CLI/path/schema setup fails before parent launch or if a discovered request is rejected before child launch.

## Minimal Parent-Child Test Fixture

Implementation must create or generate one fixture run directory under:

```text
tests/docworkflow-agent-delivery/e2e/session-workflow-live/<timestamp>-external-controller-mvp/
```

Fixture behavior:

1. Parent handoff starts a visible parent session.
2. Parent session writes `controller/requests/CTRL-C1.request.json`.
3. Parent session does not run `AgentDeliverySessionLauncher.cs` for the child.
4. Controller detects the request and launches `CTRL-C1` from outside the parent session.
5. Child handoff writes exactly `controller child reached\n` to `target/output/controller-spike.txt`.
6. Controller writes `controller/responses/CTRL-C1.response.json`.
7. Controller writes `controller/controller-summary.json`.

The fixture passes only when the controller summary status is `pass`, the parent and child evidence are visible app-server evidence, and the child output matches exactly.

## Deterministic Fixture Suite Contract

The `--fixture <dir>` mode exists so the controller state machine and contracts can be tested without starting live Codex sessions.

Required fixture directory shape:

```text
<fixture>/
  fixture-manifest.json
  positive/
  malformed-request/
  unsafe-path/
  missing-request/
  blocked-child/
  missing-output/
```

`fixture-manifest.json` schema:

```json
{
  "schema_id": "agent-delivery.visible-session-controller.fixture-manifest.v1",
  "cases": [
    {
      "id": "positive",
      "expected_exit_code": 0,
      "expected_summary_status": "pass",
      "expected_response_status": "launched"
    }
  ]
}
```

Fixture mode rules:

1. The controller may create a temporary run directory for each fixture case, copy case inputs into it, and evaluate the same request validation, result interpretation, output assertion, response writing, and summary writing code paths used by live mode.
2. Fixture mode must simulate launcher outputs from fixture files. It must not spawn `codex`, `codex app-server`, or `AgentDeliverySessionLauncher.cs`.
3. Fixture mode must cover at least the positive, malformed-request, unsafe-path, missing-request, blocked-child, and missing-output cases.
4. Fixture mode exits `0` only when every case matches the expected exit code, summary status, and response status declared in the manifest.

## Negative Harness Cases

The implementation must include fixture or direct test coverage for:

| Case | Expected Result |
|---|---|
| Missing request before timeout | Summary `status: "timeout"`, exit `1`. |
| Malformed JSON request | Response `status: "rejected"`, summary `status: "setup_error"`, exit `2`, no launcher command. |
| Request path outside run directory | Response `status: "rejected"`, summary `status: "setup_error"`, exit `2`, no launcher command. |
| Child launcher blocked at app-server initialize | Response `status: "blocked"`, summary `status: "blocked"`, retained launcher evidence paths. |
| Child output missing after launched evidence | Response `status: "failed"`, summary `status: "failed"`. |

## Verification Commands

Run from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs` on macOS/zsh:

```sh
dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --help
```

Expected: exit `0`, usage includes `--run-dir`, `--parent-handoff`, `--parent-target-id`, parent timeout, child timeout, request timeout, app-server request timeout, and summary output options.

```sh
dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-session-controller-mvp
```

Expected: exit `0`; positive and negative fixture cases pass without launching live Codex sessions.

```sh
dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --run-dir tests/docworkflow-agent-delivery/e2e/session-workflow-live/<timestamp>-external-controller-mvp --parent-handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/<timestamp>-external-controller-mvp/handoffs/parent-handoff.md --parent-target-id CTRL-PARENT --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
```

Expected: exit `0` for the minimal live fixture; retained `controller-summary.json` has `status: "pass"`; parent and child evidence paths exist; child output equals `controller child reached\n`.

```sh
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/<timestamp>-external-controller-mvp/controller/controller-summary.json','utf8')); if (s.status !== 'pass') process.exit(1);"
```

Expected: exit `0`.

```sh
git diff --check
```

Expected: exit `0`.

## Implementation Write-Set

Allowed implementation write-set for the next delivery slice:

- `skills-repo/tools/AgentDeliveryVisibleSessionController.cs`
- `_specs/2026-05-11 Agent Delivery External Visible Session Controller MVP.md`
- `tests/docworkflow-agent-delivery/e2e/fixtures/visible-session-controller-mvp/**`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/*-external-controller-mvp/**`

Shared/read-only unless a later spec explicitly changes them:

- `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`
- `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`
- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S3 MD-E2E-5 Integration.md`

## Acceptance Criteria

1. The controller help command exits `0`.
2. The controller fixture suite exits `0` and covers positive, malformed, unsafe-path, timeout, blocked, and output-missing cases.
3. The live minimal parent-child controller run exits `0`.
4. The live parent is visible app-server evidence.
5. The live child is visible app-server evidence launched by the controller, not by the parent session.
6. The child output is exactly `controller child reached\n`.
7. Controller response and summary artifacts preserve enough evidence paths to debug blocked/failed launches.
8. No nested child `codex app-server --listen stdio://` launch from inside the parent session appears in the parent transcript.
9. `git diff --check` passes.
10. Rejected request cases write deterministic response and summary artifacts while launching no child process.

## Security And Redaction

The controller must not copy prompt bodies, raw transcript text, tokens, environment variables, or secret-like values into response or summary artifacts.

Allowed evidence references are paths, statuses, hashes, target ids, timestamps, launcher exit codes, and bounded blocker strings already redacted by `AgentDeliverySessionLauncher.cs`.

## Review And Hardening Result

Review pass applied during authoring:

| Review Area | Result |
|---|---|
| Scope discipline | Pass. The spec is limited to one parent and one child controller MVP. |
| Request/response data contract | Pass. Identity, provenance, status, evidence paths, output assertion, and failure states are explicit. |
| State machine | Pass. Every state has entry, success, failure, and terminal semantics. |
| Failure handling | Pass. Timeout, rejected request, blocked child launch, failed output, and setup errors are covered. |
| Path safety | Pass after hardening. Child handoff, output, and launch output paths must stay below `<run-dir>`. |
| Fixture semantics | Pass after hardening. Fixture mode now has an explicit manifest, case set, and no-live-launch rule. |
| Rejection semantics | Pass after hardening. Rejected requests map to response `rejected`, summary `setup_error`, exit `2`, and no launcher command. |
| Verification | Pass with one implementation-time command contract note: controller commands are post-implementation gates because the new tool does not exist before this slice. |
| MD-E2E-5 boundary | Pass. Full runner migration remains out of scope. |

No blocking markers remain. The spec was implemented and accepted for the controller MVP slice.

## Closeout Evidence

- OpenSpec archived: `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-controller-mvp/`
- Canonical OpenSpec spec updated: `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`
- Retained live controller run: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/controller/controller-summary.json`
- Verification replay: help command, fixture suite, retained summary assertion, canonical OpenSpec validation, and `git diff --check` passed during closeout.
- Documentation sync: repository docs search found no pre-existing stale project-doc references to the controller MVP beyond this spec and the canonical OpenSpec testsuite spec, so no additional docs file required an update.

## Mini-Retro

- Decision: External controller owns visible-session process launch; parent owns only request production.
- Change: This spec defines and now accepts the MVP controller contract, state machine, fixture, implementation, and verification gates.
- Open follow-up: After this MVP passes, create a separate spec/slice for integrating the controller into `MD-E2E-5`.
- Missing evidence: none for the MVP closeout. `MD-E2E-5` integration evidence remains a separate future slice.
- Workflow note: This spec intentionally avoids altering the already accepted visible evidence validator and app-server launcher protocol.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-11 | Codex | Created and hardened the external visible-session controller MVP spec. |
| 2026-05-11 | Codex | Review-hardened path boundaries, parent timeout, launcher invocation, fixture mode, and rejected-request summary semantics. |
| 2026-05-11 | Codex | Locked implementation scope contract and opened OpenSpec change `agent-delivery-visible-session-controller-mvp`. |
| 2026-05-11 | Codex | Implemented controller MVP with fixture and live minimal parent-child evidence under `20260511T120609Z-external-controller-mvp`. |
| 2026-05-11 | Codex | Accepted and closed the controller MVP; archived OpenSpec change to `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-controller-mvp/`. |
