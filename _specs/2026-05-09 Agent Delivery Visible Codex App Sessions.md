**Date:** 2026-05-09
**Status:** 🟡 Spec
**Scope:** Agent Delivery Session Launcher upgrade from headless `codex exec` launches to visible or explicitly traceable Codex-App sessions.

---

## Review Control Surface

- Spec-Variante: Contract-heavy workflow/tooling follow-up Spec.
- Goldstandard Status: candidate. App-server feasibility is now proven by local spike; Launcher implementation still needs a scoped delivery plan and regression harness.
- Ziel: Agent Delivery Session Launcher must distinguish headless CLI execution, queued/manual starts, and genuinely visible Codex-App sessions, keep spawned sessions under the initiating Codex project, use deterministic Parent/Child-derived titles, and make closeout archive all sessions opened for a child-spec run.
- In Scope: local technical findings, terminology, required Launcher status model, initiating-project CWD contract, Codex-App visibility evidence contract, deterministic title contract, session lifecycle/archive contract, negative evidence for headless `exec`, app-server adapter design, integration into the existing Agent Delivery Workflow Test Suite as the Parent + 5 Child visible-session regression, workflow documentation implications.
- Out of Scope: starting a new runtime session in this spec-authoring run, mutating Codex internal SQLite rows directly, implementing the Launcher adapter before the app-server path is proven, fake backfilling historical RSW/DWT evidence as visible app sessions.
- Wichtigste Test-/Harness-Cases: `codex exec` launch with `source='exec'` fails the visible-session assertion even if exit code is 0; queued/manual start is traceable but not visible-session success; visible-app mode uses `codex app-server` `thread/start`, `thread/name/set`, `turn/start`, then proves the same thread appears in normal `thread/list` with `source: "vscode"` and matching initiator cwd/title/path; title is exactly `{ParentSpecAbbrevAndNumber}: {Hardening|Implementation} - {ChildSpecDesignation}`; the existing Agent Delivery Workflow Test Suite gets an `MD-E2E-5` visible-session testcase based on its simple Parent + five Child workflow, and the Parent plus each Child must have distinct visible-session evidence; the testcase must run from a dedicated control session/process that only prepares input, starts the Launcher, observes evidence, and reports status; the testcase fails if any workflow step is performed directly by the control/editing session or if any Child uses only headless `codex exec`; `spec-closeout` archives every visible session opened for the child-spec run and records explicit no-thread/not-app-visible statuses for non-visible evidence before marking closeout `READY`.
- Wichtigste Verification Commands: `codex --help`; `codex exec --help`; `codex app-server --help`; `codex app-server generate-ts --out /tmp/codex-app-schema`; visible-session validator for positive app-server evidence, headless `exec` negative evidence, wrong-title evidence, wrong-cwd evidence and unarchived-closeout evidence; `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep` after implementation; `rg -n "AgentDeliverySessionLauncher|thread/start|turn/start|thread/archive|visible_codex_app_session|Hardening|Implementation" docs/doc-workflow.md skills-repo/skills/spec-closeout/SKILL.md skills-repo/tools tests/docworkflow-agent-delivery`; `git diff --check`.
- Offene Entscheidungen: No blocking decisions. Non-blocking follow-up: whether UI/sidebar screenshot proof should be added on top of normal app-server `thread/list` machine evidence; whether the app-server process lifecycle should later support a shared long-lived socket instead of per-run stdio.
- Readiness Status: IMPLEMENTATION READY for one bounded Launcher/workflow-doc change, assuming the implementation keeps app-server process lifecycle local to the run and uses normal `thread/list` evidence as the machine visibility proof.

## Session Briefing

- Modus/Skill: `doc-coauthoring`.
- Source of Truth: `skills-repo/tools/AgentDeliverySessionLauncher.cs`, `docs/doc-workflow.md`, `skills-repo/skills/spec-orchestrator/SKILL.md`, `skills-repo/skills/child-spec-hardening/SKILL.md`, `skills-repo/skills/spec-change-delivery/SKILL.md`, `skills-repo/skills/spec-closeout/SKILL.md`, `tests/docworkflow-agent-delivery/README.md`, `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md`, `_specs/2026-05-08 Agent Delivery Session Launcher Automation.md`, local Codex CLI/app-server help and generated app-server protocol types.
- Ziel: Clarify whether the current Launcher can start visible Codex-App sessions and define the next safe change.
- Nicht-Ziele: no live child delivery, no runtime adapter implementation, no direct database write, no broad Agent Delivery refactor.
- In Scope: evidence-backed answer, spec update, blockers, decisions, regression-test contract.
- Erwarteter Output: this spec plus final session report.
- Verification/Review: content-quality review against the user's acceptance criteria and local command evidence.
- Offene Entscheidungen: whether UI/sidebar screenshot proof is additionally required beyond normal `thread/list`.

## 1. Current Technical Answer

Current state: **moeglich via `codex app-server`; not possible with the current Launcher implementation; not possible via `codex exec` alone.**

The existing Launcher can start a **headless CLI session** with `codex exec --json -C <target_workspace> --output-last-message <file> -`. It can also find the resulting local Codex thread metadata in `~/.codex/state_5.sqlite` and observe `source='exec'`, `cwd`, `title`, and `rollout_path`.

That is not enough to prove a visible Codex-App chat. The latest regression showed that these `exec` sessions did not appear in the Codex-App left chat list. Therefore:

1. `status: "launched"` from `codex exec` means only "headless CLI process launched and completed".
2. `codex_app.visibility_status: "verified_same_project"` currently proves only that local thread metadata has the same `cwd`.
3. `verified_same_project` does **not** prove "visible in the Codex-App sidebar".
4. Future workflow evidence must not treat `codex exec` success as visible-session success.

The local spike on 2026-05-09 proved the candidate technical path:

1. `codex app-server --listen stdio://` accepted JSON-RPC requests.
2. `thread/start` created a non-ephemeral thread in the target workspace.
3. `thread/name/set` persisted a deterministic title.
4. `turn/start` executed a minimal no-tools prompt and completed.
5. A later normal `thread/list` returned the same thread with `source: "vscode"`, matching `cwd`, matching title, and the rollout path.

This is sufficient to treat app-server as the technical mechanism for visible/interactive-source Codex sessions, with one remaining wording caveat: no screenshot of the left desktop sidebar was captured in this spike. The machine evidence proves the thread is in the normal app-server list used for interactive sources, not merely in the `exec` metadata path.

All future Launcher-created visible sessions must use the **initiating Codex project** as their visible project context. The initiating project is the `cwd` of the parent/current Codex thread that calls the Launcher, not the directory where the handoff file happens to live and not an arbitrary shell cwd. The target workspace can still be recorded separately when the child delivery work must reason about another repository, but the app-visible thread must open under the project from which it was initiated unless the operator explicitly chooses a different project.

## 2. Local Findings

### 2.1 Current Launcher

`skills-repo/tools/AgentDeliverySessionLauncher.cs` currently builds Codex launch commands as:

```text
codex exec --json -C <workspace> --output-last-message <last-message.md> -
```

Relevant behavior:

1. `BuildCodexCommand` hardcodes `codex exec`.
2. `LaunchCodexAsync` starts a local process, writes the prompt to stdin, captures JSONL stdout, and marks zero exit code as `status: "launched"`.
3. `CodexAppInspector.TryInspectAsync` queries `~/.codex/state_5.sqlite` for recent rows where `source='exec'`.
4. The inspector can currently report `verified_same_project` when the observed `cwd` matches the target workspace.

Finding: this is useful traceability, but not visible-app proof.

### 2.2 Codex CLI

Local `codex --help` shows:

1. `codex exec`: non-interactive run.
2. `codex resume` / `codex fork`: interactive commands around existing sessions.
3. `codex app-server`: experimental app-server tooling.
4. `codex app`: launches the desktop app, but does not expose "create new app chat with prompt" in CLI help.

Local `codex exec --help` shows no title parameter and describes the command as non-interactive.

### 2.3 Codex App Metadata

Local `~/.codex/state_5.sqlite` has a `threads` table with fields including:

```text
id, rollout_path, source, cwd, title, first_user_message, thread_source
```

Recent rows in this workspace show both:

1. `source='vscode'`: ordinary visible/current app sessions.
2. `source='exec'`: Launcher-created headless `codex exec` runs.

Observed counts in the shared-ai-docs cwd at investigation time:

```text
vscode: 66
exec: 7
```

The app-server generated type `ThreadListParams` documents that when `sourceKinds` is omitted or empty, listing defaults to interactive sources. This is consistent with `exec` sessions being persisted but not visible in the app list by default.

### 2.4 App Server Spike Result

`codex app-server generate-ts --out /tmp/codex-app-schema` generated protocol types that include:

1. `thread/start` with `ThreadStartParams`.
2. `turn/start` with `TurnStartParams`.
3. `thread/name/set`.
4. `thread/list` with `sourceKinds?: Array<ThreadSourceKind>`.
5. `ThreadSourceKind = "cli" | "vscode" | "exec" | "appServer" | ...`.

The local spike then executed the adapter flow successfully.

Evidence path:

```text
_specs/codex-app-server-spikes/20260509T171506Z/
  summary.json
  app-server-jsonrpc.json
  list-summary.json
  app-server-list-jsonrpc.json
  turn-summary.json
  app-server-turn-jsonrpc.json
```

Observed thread:

```text
thread_id: 019e0dbc-5439-7df3-8849-847f29a93ce0
title: APP-SERVER-SPIKE 20260509T171506Z
cwd: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
source: vscode
rollout_path: /Users/dh/.codex/sessions/2026/05/09/rollout-2026-05-09T19-15-06-019e0dbc-5439-7df3-8849-847f29a93ce0.jsonl
turn result: APP_SERVER_SPIKE_OK
```

Important behavioral finding:

1. `thread/start` alone created SQLite and rollout evidence, but immediate `thread/list` did not return the empty thread.
2. After `turn/start` created a user event and completed, normal `thread/list` returned the thread.
3. Therefore Launcher visible-app mode should create the thread, set the title, start the prompt turn, wait for completion or accepted in-progress state, and only then validate app-list visibility.

The implementation adapter should:

1. Connect to a running app-server control socket or start an app-server process in a supported mode.
2. Send `thread/start` with `cwd=<initiating_project_cwd>`, model/config, source metadata, and non-ephemeral setting.
3. Send `thread/name/set` to assign the deterministic Agent Delivery title from section 4.
4. Send `turn/start` with the persisted handoff prompt.
5. Query normal `thread/list` and, when using source filters, `sourceKinds: ["vscode"]`.
6. Record app-visible evidence.

Spike result: `sourceKinds: ["appServer"]` did not return the thread. The created session appeared as `source: "vscode"`, matching current Codex Desktop/app-server semantics. The adapter must therefore validate against default interactive listing and/or `sourceKinds: ["vscode"]`, not `sourceKinds: ["appServer"]`.

## 3. Required Terminology

The workflow must use these terms exactly enough that status cannot drift.

| Term | Meaning | May count as visible Codex-App session? |
|---|---|---|
| `headless_cli_session` | A non-interactive process started through `codex exec`, with stdout/event files and local rollout metadata. | No. |
| `queued_manual_start` | A persisted `launch-request.json` and `start-prompt.md` that a human or future adapter can use to start a session. | No, unless later paired with manual visible-session evidence. |
| `manual_visible_start` | A human opens a new Codex-App session and pastes/starts the prompt, then records real thread id/log/title evidence. | Yes, if evidence proves app visibility. |
| `visible_codex_app_session` | A session created or observed through Codex App Server with `thread/start` plus a materialized `turn/start`, then proven in normal app-server `thread/list` as an interactive-source thread with matching cwd/title/path. | Yes. |
| `traceable_but_not_visible` | Local DB/log evidence exists, but app sidebar/list visibility is absent or unproven. | No. |

## 4. Initiating Project And Title Contract

### 4.1 Initiating Project

Visible App-Server sessions must open under the same Codex project from which they were initiated.

Required Launcher inputs/fields:

```json
{
  "initiating_project_cwd": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
  "target_workspace": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
  "project_cwd_source": "current_thread_cwd | explicit_cli_arg | handoff_target_workspace_fallback"
}
```

Rules:

1. `initiating_project_cwd` is the `cwd` used for `thread/start`.
2. `target_workspace` remains the workspace named by the handoff and prompt.
3. When the Launcher is invoked from an app-server/visible parent thread, it must pass the current thread `cwd` as `initiating_project_cwd`.
4. When invoked from shell without a current thread, it must accept `--initiating-project-cwd <path>`; if missing, it may fall back to the handoff `Target Repository / Working Directory` and must record `project_cwd_source: "handoff_target_workspace_fallback"`.
5. Evidence must prove `thread/list` returned the created thread with `cwd == initiating_project_cwd`.
6. If `target_workspace` differs from `initiating_project_cwd`, the prompt must show both values and the implementation turn must not silently switch the visible project. The future adapter may pass a turn-level `cwd` only if the spec explicitly decides cross-project delivery semantics.

### 4.2 Session Title

Visible Agent Delivery child sessions must have deterministic titles:

```text
{ParentSpecAbbrevAndNumber}: {Hardening|Implementation} - {ChildSpecDesignation}
```

Examples:

```text
DWT-1: Implementation - S3 Content Bundle
MD-E2E-4: Hardening - Documentation Sync
RSW-1: Implementation - C5 Append Final Count
```

Derivation rules:

1. `ParentSpecAbbrevAndNumber` is derived from the parent/master spec identifier, not from the child id. Use the parent spec's established short code and parent number, for example `DWT-1`, `MD-E2E-4`, `RSW-1`, `KI-V2`, or `NCG-STS-4`.
2. `Hardening` is used when the next skill/session is `child-spec-hardening`.
3. `Implementation` is used when the next skill/session is `spec-change-delivery`.
4. If the parent spec has no established number, the orchestrator/hardening owner must assign or record a stable parent number/identifier before visible launch. Do not substitute a child number as the parent number.
5. `ChildSpecDesignation` is the human-readable child designation from the Child Index `Child Spec` cell, child spec title, or handoff `Child Spec` field after removing path/date noise and any duplicated parent prefix. Keep the stable child id when it is part of the child designation itself, for example `S3 Content Bundle`, `Documentation Sync`, or `C5 Append Final Count`.
6. The child id alone, for example `DWT-S3` or `RSW-C5`, is not sufficient as the title prefix because it hides which parent spec owns the session. It may appear in `ChildSpecDesignation` when useful.
7. If no child designation exists for a parent/workflow-step session, use an explicit workflow designation such as `Parent Orchestration`, `Parent Closeout`, or `Integration Sync`.
8. Other modes must not invent new stage labels in this adapter change. They must either be out of scope, use queued/manual mode, or receive an explicit future title contract.
9. The title must be written via `thread/name/set` before `turn/start` when possible, and evidence must show `thread/name/updated` or equivalent observed title in `thread/list`.

## 5. Launcher Evidence Contract

The Launcher must stop using a single `status: "launched"` as if it described both process launch and app visibility.

Required fields:

```json
{
  "execution_channel": "headless_cli | app_server | manual_queue | manual_visible",
  "initiating_project_cwd": "...",
  "target_workspace": "...",
  "session_title": "DWT-1: Implementation - S3 Content Bundle",
  "session_stage": "Hardening | Implementation",
  "parent_spec_abbrev_and_number": "DWT-1",
  "child_spec_designation": "S3 Content Bundle",
  "session_visibility": {
    "class": "headless_cli_session | queued_manual_start | manual_visible_start | visible_codex_app_session | traceable_but_not_visible",
    "visible_in_codex_app": true,
    "proof_status": "verified | unverified | failed | not_applicable",
    "proof_method": "app_server_thread_list | codex_app_ui_observation | manual_human_confirmation | local_exec_metadata_only",
    "thread_id": "...",
    "thread_source_observed": "vscode | appServer | exec | cli | unknown",
    "source_kind_observed": "vscode | appServer | exec | unknown",
    "cwd_observed": "...",
    "title_observed": "...",
    "sidebar_or_default_list_observed": true
  }
}
```

Rules:

1. `codex exec` may produce `execution_channel: "headless_cli"` only.
2. `codex exec` may never set `session_visibility.class` to `visible_codex_app_session`.
3. A local SQLite row with `source='exec'` is `traceable_but_not_visible` unless a separate app-visible proof exists.
4. `status: "launched"` may remain as process status, but visible-session claims must use `session_visibility`.
5. Any report that says "new visible Codex-App session started" must require `session_visibility.visible_in_codex_app == true`.
6. `queued` and `manual_start_required` remain valid workflow states, but they must not be counted as app-session starts.
7. `session_title` must match the title contract from section 4.2.
8. `cwd_observed` must equal `initiating_project_cwd` for visible app sessions.

## 6. Visible App Evidence Contract

A `visible_codex_app_session` needs all of these:

1. A real `thread_id`.
2. A real `rollout_path` or app-server thread path, when available.
3. Observed `cwd` matching `initiating_project_cwd`.
4. A deterministic title or name exactly matching `{ParentSpecAbbrevAndNumber}: {Hardening|Implementation} - {ChildSpecDesignation}`.
5. An observed source/source kind that is app-visible for the current app list, not `exec` unless the app explicitly lists `exec` sessions in the sidebar.
6. Proof that the thread appears in an app-visible list or sidebar-equivalent source.
7. The prompt hash or first user message hash matching `start-prompt.md`.
8. Separate evidence for turn execution if the Launcher is expected to start work, not just create an empty visible chat.

Allowed proof methods:

| Proof method | Required evidence | Status |
|---|---|---|
| `app_server_thread_list` | app-server request/response showing `thread/start`, `thread/name/set`, `turn/start`, and normal `thread/list` returning the same thread as `source: "vscode"` with matching cwd/title/path. | Preferred machine proof, proven by local spike. |
| `codex_app_ui_observation` | screenshot or structured browser/app observation showing the new thread title/id in the left list. | Strong proof, may need manual/app tooling. |
| `manual_human_confirmation` | operator records visible thread id/title/log path after manual app start. | Acceptable for manual mode only. |
| `local_exec_metadata_only` | SQLite row with `source='exec'`, rollout path, cwd. | Not visible proof. |

## 7. Session Lifecycle And Closeout Archive Contract

All sessions opened for a child-spec run must be closed out explicitly. This prevents Agent Delivery from filling the Codex-App sidebar with stale Hardening/Implementation threads after the child is accepted.

Definitions:

1. A child-spec run includes every visible, manual-visible, queued, or headless session whose launcher evidence has the same parent spec and target child/spec id.
2. The closeout owner is `spec-closeout`.
3. Archival means calling the app-server `thread/archive` method for visible/app-server threads, or recording why a non-visible/headless/manual session cannot or need not be archived.

Requirements for `spec-closeout`:

1. Before final `READY`, find all session evidence for the child target under `_specs/agent-delivery-session-launches/**` and any child-local launch evidence directory named by the Child Index/Handoff.
2. For every evidence record with `session_visibility.class == "visible_codex_app_session"` and a real `thread_id`, call `thread/archive` through app-server or prove it is already archived.
3. For every archived thread, record `archived_at`, `archive_method`, `thread_id`, `session_title`, and post-archive `thread/list` or SQLite evidence showing `archived=true` or absent from the non-archived list.
4. For headless `codex exec` sessions, record `archive_status: "not_app_visible_not_archived"` unless a future Codex API supports archiving exec rollouts.
5. For queued/manual starts that did not produce a real thread, record `archive_status: "no_thread_created"`.
6. If any visible thread opened for the child cannot be archived, closeout is `NOT READY` unless the user explicitly accepts a non-blocking retained-session note.
7. Parent closeout must confirm that all child rows either have session archive evidence, an explicit no-thread status, or an accepted retained-session note.

## 8. Candidate Implementation Plan

1. Add `--session-kind <headless-cli|visible-app|manual-queue>` or equivalent.
2. Keep current `codex exec` behavior under `headless-cli`.
3. Add `--agent codex-app` or `--adapter codex-app-server`.
4. Implement a small app-server client/probe that can:
   - start `codex app-server --listen stdio://` for isolated Launcher-created sessions or connect to a configured endpoint when provided,
   - send JSON-RPC `initialize`,
   - send `thread/start`,
   - set a thread name,
   - send `turn/start` with the persisted prompt,
   - wait until the turn is completed or reaches a documented acceptable in-progress state,
   - query `thread/list` after the first user event exists,
   - write request/response evidence without secrets.
5. Capture `initiating_project_cwd`, `target_workspace`, `project_cwd_source`, exact `session_title`, and exact `session_stage`.
6. Update `CodexAppInspector` so `verified_same_project` is renamed or downgraded for `exec` rows.
7. Add a validator, for example `ValidateVisibleCodexAppSessionEvidence.cs`, that rejects `exec` source for visible-session claims and rejects wrong title/cwd/stage.
8. Add or extend the existing Agent Delivery Workflow Test Suite runner so the visible-session path is a first-class testcase, not an external ad hoc script. The testcase id is `MD-E2E-5` and it reuses the existing simple Parent + five Child workflow shape.
9. Add app-server archive support, either in the Launcher as a helper mode or in a small closeout companion tool.
10. Update `docs/doc-workflow.md` and Agent Delivery skills so "fresh visible app session" means `session_visibility.class: visible_codex_app_session`, not `status: launched`.
11. Update `spec-closeout` so accepted child closeout archives all visible sessions opened for that child before final `READY`.

## 9. Regression Test Contract: Parent + 5 Child Sessions

The regression must be integrated into the existing Agent Delivery Workflow Test Suite. It must not live only as a one-off spike or standalone proof. The existing suite already has a simple real-session workflow shape under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/`: one parent spec fans out to five children (`RSW-C1` through `RSW-C5`) and produces final output `1\n2\n3\n4\n5\n`. The visible Codex-App session change must add this as the live `MD-E2E-5` testcase and make it impossible to satisfy with only `codex exec`.

### Suite Integration

Required suite changes:

1. Add a source-controlled visible-session testcase contract under `tests/docworkflow-agent-delivery/testcases/`, for example `md-e2e-5-visible-codex-app-sessions.md`.
2. Add or extend a runner under `tests/docworkflow-agent-delivery/scripts/`, for example `run-visible-app-session-workflow-checks.sh`, that executes the live visible-session workflow using `AgentDeliverySessionLauncher.cs`.
3. The runner may require an explicit selector or opt-in environment flag because it starts real Codex-App/app-server sessions. It must not silently replace the mock-only standard gate `run-mock-e2e-checks.sh all --keep`.
4. The runner must enforce a control-session boundary: the invoking session/process may prepare the test parent, call the Launcher, monitor evidence, stop only processes it started if the test hangs, and produce the final report; it must not run `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout`, or write child delivery artifacts directly.
5. The actual Parent workflow must run in a separate visible Codex-App session created by `AgentDeliverySessionLauncher.cs`. That Parent session must create the orchestration pack, five child specs, five child handoffs, and launch each Child through `AgentDeliverySessionLauncher.cs`; the control session cannot do those steps on its behalf.
6. The runner must materialize run evidence under the existing suite evidence tree, for example `tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/` or `tests/docworkflow-agent-delivery/e2e/evidence/<run-id>-visible-app/`.
7. The runner must preserve the existing parent-child workflow semantics: Parent session orchestrates, five Child sessions deliver serially, each Child appends exactly one line to `target/output/count.txt`, and closeout verifies the final file.
8. The testcase summary must be machine-readable and include both workflow outcome and visible-session outcome. A passing delivery with failed visible-session evidence is a failed `MD-E2E-5` testcase.
9. `tests/docworkflow-agent-delivery/README.md` must document the new live visible-session gate separately from the mock-only standard gate and state that `MD-E2E-5` is the accepted verification for the Launcher visible-session change.

Suggested command contract after implementation:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep
```

Success criteria for the command:

1. Exit code `0`.
2. Summary JSON reports `schema_id: "docworkflow-agent-delivery-visible-app-e2e-summary.v1"`.
3. Summary JSON reports `overall_workflow_status: "pass"`.
4. Summary JSON reports `visible_session_status: "pass"`.
5. Summary JSON reports `control_session_status: "observed_only"` or equivalent and records that orchestration, child hardening, child delivery, and closeout were performed by Launcher-created sessions, not by the invoking control/editing session.
6. Summary JSON points to parent and five child visible-session evidence files.
7. Final output file is exactly `1\n2\n3\n4\n5\n`.

Control prompt contract:

```text
Diese Session ist nur Kontrollsession.
Der eigentliche Workflow muss in einer separaten, vom Agent Delivery Session Launcher gestarteten Session laufen.
Keine Single-Session-Simulation.
Kein run-mock-e2e-checks.sh als Ersatz.
Keine Abkuerzungen.
Der Test gilt nur als gruen, wenn echte Launcher-/Session-Evidence fuer Parent und Child-Sessions existiert.
```

If the workflow fails or hangs, the control session must stop the test, terminate only test processes it started, and report `NOT READY` with:

1. failed Child or workflow step,
2. evidence that exists,
3. evidence that is missing,
4. current `target/output/count.txt` contents,
5. started Launcher sessions,
6. final verdict `NOT READY`.

### Positive visible-app path

Fixture shape:

```text
tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/
  input/test-parent.md
  handoffs/parent-start-handoff.md
  child-specs/rsw-c1.md ... rsw-c5.md
  handoffs/rsw-c1-handoff.md ... rsw-c5-handoff.md
  launches/<parent>/evidence.json
  launches/<child>/evidence.json
  closeout/summary.json
  visible-session-summary.json
```

Required assertions:

1. Parent evidence has `session_visibility.class == "visible_codex_app_session"`.
2. Each of the five Child evidence files has `session_visibility.class == "visible_codex_app_session"`.
3. Parent and each Child have distinct `thread_id`.
4. No visible-session evidence has `execution_channel == "headless_cli"`.
5. No visible-session evidence has `thread_source_observed == "exec"` unless a later explicit app contract proves `exec` is sidebar-visible. Current expected behavior: reject `exec`.
6. Each title/name exactly follows the contract, for example `RSW-1: Hardening - Parent Orchestration`, `RSW-1: Implementation - C1 Initial Count`, ..., `RSW-1: Implementation - C5 Append Final Count`.
7. Each `cwd_observed` equals the initiating project cwd `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`.
8. Each prompt hash matches its `start-prompt.md`.
9. Child delivery evidence still proves the workflow result: final output exactly `1\n2\n3\n4\n5\n`.
10. Closeout archives all six visible sessions or records a blocking `NOT READY` result.
11. The Agent Delivery Workflow Test Suite summary marks the run failed unless both the workflow delivery and visible-session validation pass.
12. The test suite records the exact Launcher command or app-server transcript used for each parent/child launch so a later reviewer can distinguish `codex app-server` from `codex exec`.
13. The test suite records which session/process acted as control and proves it did not directly write orchestration packs, child specs, child handoffs, child delivery evidence, closeout summaries, or `target/output/count.txt` except for allowed setup/report artifacts.

### Negative And False-Positive Paths

Use the existing `codex exec` style evidence as a negative fixture.

Required assertions:

1. If `mechanism.actual_command` contains `codex exec`, then visible-session validation fails.
2. If `codex_app.thread_source == "exec"`, then visible-session validation fails.
3. If `status == "launched"` but `session_visibility.class != "visible_codex_app_session"`, the Parent + 5 Child visible regression fails.
4. `verified_same_project` from old evidence is accepted only as `traceable_but_not_visible`.
5. A visible-app evidence record with title `RSW-C1: Implementation` or `RSW-C1 spec-change-delivery - ...` fails because it uses the child id as the prefix instead of the parent spec abbreviation/number plus child designation.
6. A visible-app evidence record whose `cwd_observed` is the target repo but not the initiating project fails unless the initiating project was explicitly set to that target repo.
7. A closeout summary that accepts a child while its visible Hardening or Implementation thread remains unarchived fails.
8. A suite run whose final `count.txt` is correct but whose visible-session evidence is missing, headless-only, queued-only, wrong-title, wrong-cwd, or unarchived fails `MD-E2E-5`.
9. A suite run whose visible-session evidence passes but whose parent/child workflow did not produce `1\n2\n3\n4\n5\n` fails `MD-E2E-5`.
10. A standalone spike evidence directory outside `tests/docworkflow-agent-delivery/**` cannot satisfy `MD-E2E-5`; spike evidence can only support implementation debugging.
11. A run fails if the current implementation/editing session or control runner performs parent orchestration, child hardening, child delivery, child closeout, or final output writes directly instead of delegating those steps to Launcher-created visible sessions.
12. A run fails if evidence cannot distinguish the control session from the Launcher-created Parent and Child sessions.

## 10. Open Decisions And Blockers

Non-blocking follow-up: app-server socket/control lifecycle. The implementation-ready default is to start `codex app-server --listen stdio://` per Launcher visible-session run and capture the protocol transcript. A later optimization may connect to a long-lived app/server socket.

Non-blocking follow-up: UI/sidebar proof source. The implementation-ready machine proof is normal `thread/list` with `source: "vscode"`, matching title, cwd, thread id and rollout path. A later hardening pass may add screenshot/UI observation as additional evidence.

Blockers:

1. The current Launcher still has no app-server adapter.
2. Runtime closeout tooling for app-server `thread/archive` is not implemented yet.
3. `codex exec` creates `source='exec'` rows that are traceable but not app-visible in the observed workflow.
4. `codex app-server` is experimental, so the adapter must record CLI version and protocol evidence.
5. Direct SQLite mutation would be fragile and must not be used as a visibility shortcut.

## 11. Acceptance Criteria

1. The workflow distinguishes headless CLI, queued/manual start, and visible Codex-App session.
2. Current `codex exec` success cannot satisfy visible-session acceptance.
3. Launcher evidence records both process launch status and visibility class.
4. A visible-session claim requires app-visible proof, not only same-cwd metadata.
5. Visible-session evidence proves `cwd_observed == initiating_project_cwd`.
6. Visible-session titles exactly follow `{ParentSpecAbbrevAndNumber}: {Hardening|Implementation} - {ChildSpecDesignation}`.
7. Parent + 5 Child regression fails when any session uses only headless `codex exec`.
8. Parent + 5 Child regression is part of the Agent Delivery Workflow Test Suite as `MD-E2E-5`; standalone spike evidence outside `tests/docworkflow-agent-delivery/**` cannot satisfy the regression.
9. Parent + 5 Child regression passes only when six distinct visible app sessions are proven or when a reviewed manual-visible mode supplies equivalent human/app evidence.
10. `MD-E2E-5` fails if the final workflow output is correct but visible-session evidence is missing, headless-only, queued-only, wrong-title, wrong-cwd, or unarchived.
11. `MD-E2E-5` fails if the control/editing session performs parent orchestration, child hardening, child delivery, child closeout, or final output writes directly instead of only starting and observing Launcher-created sessions.
12. `MD-E2E-5` reports `NOT READY` on failure/hang with failed step, existing evidence, missing evidence, current `count.txt` contents, started Launcher sessions and final verdict.
13. `spec-closeout` archives every visible session opened for the child-spec run before final `READY`.
14. Workflow docs and skills stop saying "launched session" when they mean only `codex exec` headless success.

## 12. Content Quality Review

- Correctness/domain fit: Pass. The spec addresses the exact regression: `codex exec` created persisted, same-cwd threads but not visible app chats.
- Scope discipline: Pass. It defines one bounded adapter/workflow-doc change plus closeout archive behavior, without requiring broad runtime delivery.
- Completeness: Pass. It covers current behavior, app-server path, initiating project, title contract, evidence classes, positive and negative tests, closeout archiving, control-session separation, failure/hang reporting, and the Agent Delivery Workflow Test Suite `MD-E2E-5` Parent + 5 Child regression.
- Consistency: Pass. `headless_cli_session`, `queued_manual_start`, and `visible_codex_app_session` are distinct and cannot satisfy each other's acceptance criteria. The title and cwd rules are reflected in review surface, contract, regression tests and acceptance criteria.
- Feasibility: Pass for a bounded adapter implementation. Local spike proved `codex app-server --listen stdio://`, `thread/start`, `thread/name/set`, `turn/start`, and normal `thread/list` evidence.
- Verifiability: Pass. The regression is concrete, is tied to the existing Agent Delivery Workflow Test Suite, and includes negative controls for old `codex exec` evidence, wrong title, wrong initiating project, missing closeout archive, standalone spike-only evidence, correct-output-but-invisible-session false positives, and single-session/control-session takeover false positives.

## Mini-Retro

- Was wurde entschieden? Current Launcher `codex exec` is not visible-app proof; same-cwd local metadata is only traceability. App-server with `thread/start` + `turn/start` is technically viable for Launcher-created visible/interactive-source sessions. Visible sessions inherit the initiating project, titles use `{ParentSpecAbbrevAndNumber}: {Hardening|Implementation} - {ChildSpecDesignation}`, `spec-closeout` owns archiving child-run sessions, final verification belongs in the existing Agent Delivery Workflow Test Suite as `MD-E2E-5`, and the invoking session is only a control session, not a workflow executor.
- Was wurde geaendert? This spec was added as the follow-up control artifact, updated with local spike evidence, hardened with project/title/archive contracts, extended with the `MD-E2E-5` suite testcase contract, and hardened with a control-session boundary plus failure/hang reporting contract.
- Was bleibt offen? Socket lifecycle and whether machine `thread/list` proof is enough or UI/sidebar observation is also required.
- Welche Evidenz/Verification fehlt? No app-sidebar screenshot/human visual check was captured; machine proof exists through app-server normal `thread/list`.
- Welche Skill-/Workflow-Reibung ist aufgefallen? Earlier wording overloaded `launched` and `verified_same_project`; that made a headless success look stronger than it was.
- Session-/Kontextzustand: Continue with a focused proof spike or doc/skill wording patch before runtime implementation.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-09 | Codex | Created visible Codex-App session follow-up spec after regression showed `codex exec` sessions were headless/traceable but not sidebar-visible. |
| 2026-05-09 | Codex | Ran local `codex app-server` spike; proved thread creation, title persistence, minimal turn execution, SQLite/rollout persistence, and normal app-server list visibility as `source: "vscode"`. |
| 2026-05-09 | Codex | Hardened the spec with initiating-project inheritance, deterministic Hardening/Implementation title format, closeout session archiving, expanded regression negatives and implementation-ready acceptance criteria. |
| 2026-05-10 | Codex | Corrected the title contract to use parent-spec abbreviation/number as prefix and child-spec designation after the Hardening/Implementation stage. |
| 2026-05-10 | Codex | Added the existing Agent Delivery Workflow Test Suite integration as `MD-E2E-5`, using the simple Parent + five Child workflow as the required visible-session regression testcase. |
| 2026-05-10 | Codex | Hardened `MD-E2E-5` with a dedicated control-session boundary so the invoking/editing session cannot drive the workflow directly or masquerade as Launcher-created Parent/Child sessions. |

SessionId: 2026-05-09-agent-delivery-visible-codex-app-sessions
