**Date:** 2026-05-11
**Status:** 🟡 Spec
**Scope:** Add Agent Delivery run profiles so normal workflow runs are compact and headless by default, while explicit debug runs are visible and retain full diagnostic evidence.
**SessionId:** agent-delivery-run-profiles-compact-debug-20260511

---

## Goal

Agent Delivery needs two operating modes:

1. A normal mode that runs child/parent sessions in the background without flooding the repository with prompt, transcript, request, response, and status artifacts.
2. A debug mode that makes sessions visible in the Codex App and retains the detailed evidence needed to explain or diagnose failures.

The default must be the quiet normal mode. Debug mode must be explicit, or recommended after a failure with a reproducible command, not silently enabled by the workflow.

## Review Control Surface

- Spec-Variante: Contract-heavy workflow/tooling spec for Launcher, Controller, resolver, and central workflow documentation.
- Goldstandard Status: Hardened implementation-ready tooling spec.
- Ziel: Introduce compact/default and debug/visible Agent Delivery run profiles without expanding every skill with more procedural text.
- In Scope: run profile contract; default compact behavior; explicit debug behavior; failure escalation recommendation; minimal-vs-full evidence retention; CLI options for Launcher and Controller; resolver/readiness implications; compact summary schema; targeted docs update; deterministic fixture tests.
- Out of Scope: changing product/runtime repos; making visible sessions the default; removing all evidence; deleting historical evidence; broad skill rewrites; live automatic rerun in debug after failure; redesigning the Agent Delivery Workflow itself.
- Wichtigste Test-/Harness-Cases: default Launcher run is compact/headless and writes only minimal evidence; debug Launcher run is visible via `codex-app-server` and writes full evidence; default Controller run launches children headlessly and writes compact aggregate evidence; debug Controller run launches visible child sessions and retains full request/response/transcript artifacts; failure in compact mode writes a concise failure summary and debug rerun command; no skill MD grows with duplicated profile rules.
- Wichtigste Verification Commands: `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help`; `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --help`; fixture tests for compact/debug launcher evidence; fixture tests for compact/debug controller summary; resolver fixture tests for compact pass, debug pass, compact failure with rerun recommendation; `rg -n "Agent Delivery Run Profiles|compact|debug" docs/doc-workflow.md skills-repo/skills`; `git diff --check`.
- Offene Entscheidungen: none blocking. The default profile is compact; debug is explicit.
- Readiness Status: IMPLEMENTATION READY for one bounded tooling/docs change.

## Session Briefing

- Modus/Skill: `doc-coauthoring` followed by `doc-review-autoresolve`.
- Source of Truth: user requirement from 2026-05-11 regression review; `docs/doc-workflow.md`; `skills-repo/tools/AgentDeliverySessionLauncher.cs`; `skills-repo/tools/AgentDeliveryVisibleSessionController.cs`; `skills-repo/tools/WorkflowDoctor.cs`; current visible-run evidence under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/`.
- Ziel: Define a smaller operational contract that keeps daily Agent Delivery runs quiet while preserving a strong debug path for visible diagnosis.
- Nicht-Ziele: no broad skill expansion, no default visible sessions, no silent debug reruns, no evidence-free success claims.
- In Scope: spec and implementation-ready contracts for run profiles, evidence levels, CLI behavior, resolver gates, and tests.
- Erwarteter Output: hardened implementation-ready spec in `_specs`.
- Verification/Review: content-quality review against the regression failure, evidence-noise concern, and no-skill-bloat constraint.
- Offene Entscheidungen: none.

## Problem

The current Agent Delivery tooling conflates two different needs:

1. **Operational proof**: enough machine-readable evidence to prove a workflow step ran, passed, failed, or is blocked.
2. **Debug diagnosis**: enough detail for a human to inspect session behavior, prompts, transcripts, controller requests, responses, stdout, stderr, and Codex-App visibility.

During the live regression, the first run used real launcher sessions but defaulted to headless `codex-cli`, so the sessions were not visible in the Codex App. The follow-up visible run used the controller/app-server path and produced rich evidence, but it created many files and made the run directory difficult to scan.

The workflow needs a profile boundary so daily execution is quiet and debug execution is intentionally noisy.

## Design Decision

Add a shared **Agent Delivery Run Profile** concept with two profiles:

| Profile | Default? | Session class | Evidence level | Primary use |
|---|---:|---|---|---|
| `compact` | yes | headless/background where possible | minimal aggregate evidence plus failure summary | normal Agent Delivery execution |
| `debug` | no | visible Codex-App sessions through app-server/controller | full per-session diagnostic evidence | troubleshooting, explanation, demos, regression for visibility behavior |

This profile concept belongs in tools and central workflow docs. Skills should not duplicate the full profile contract.

## Normative Contract

### Profile Selection

1. `compact` is the default profile for Launcher and Controller commands.
2. `debug` must be explicitly selected by CLI option, for example `--profile debug` or `--debug`.
3. `--debug` is an alias for `--profile debug`.
4. `--profile compact` is an explicit form of the default.
5. Invalid profile values exit `2` with usage/setup error.
6. A handoff may request debug in prose, but the tool profile is authoritative for actual behavior.
7. Debug must never be silently enabled just because a compact run failed.

### Compact Profile

Compact mode optimizes for low filesystem noise.

Required behavior:

1. Use the existing headless/background adapter for Codex launches unless a specific workflow requires visible sessions as the target behavior under test.
2. Do not create visible Codex-App sessions.
3. Do not retain raw app-server transcripts.
4. Do not retain full prompts by default.
5. Do not retain per-step controller state files unless needed for failure diagnosis.
6. Persist one compact machine-readable summary per launched session or per controller run.
7. The compact summary must contain enough identity and status information for downstream gates.
8. If a compact run fails, retain a concise failure packet and a reproducible debug rerun command.

Compact Launcher minimum evidence:

```json
{
  "schema_version": "agent-delivery.session-launch.compact.v1",
  "profile": "compact",
  "status": "launched",
  "target_id": "CHILD-ID",
  "target_role": "child",
  "handoff_path": "path/to/handoff.md",
  "handoff_sha256": "sha256",
  "target_workspace": "/abs/path",
  "adapter_id": "codex-cli",
  "execution_channel": "headless_cli",
  "started_at": "2026-05-11T00:00:00Z",
  "completed_at": "2026-05-11T00:00:00Z",
  "exit_code": 0,
  "final_status": "ran-target",
  "closeout_status": "closed",
  "debug_rerun_command": "dotnet run ... --profile debug ..."
}
```

Compact Controller minimum evidence:

```json
{
  "schema_id": "agent-delivery.controller.compact-summary.v1",
  "profile": "compact",
  "status": "pass",
  "run_dir": "tests/.../<run-id>",
  "parent": {
    "target_id": "PARENT",
    "status": "launched",
    "session_class": "headless_cli_session"
  },
  "children": [
    {
      "target_id": "C1",
      "status": "launched",
      "final_status": "ran-target",
      "closeout_status": "closed",
      "output_status": "pass"
    }
  ],
  "final_output_status": "pass",
  "debug_rerun_command": "dotnet run ... --profile debug ..."
}
```

Compact mode may retain a small `stderr_excerpt`, status tokens, hashes, and paths. It must not retain raw prompt bodies, raw transcripts, large event streams, or full controller request/response bodies unless the run fails and the retained material is part of the failure packet.

The Launcher may create prompt material transiently in memory or in a temporary file while starting a compact session. On compact success, raw prompt material must be deleted or never persisted. On compact failure, prompt material may be retained only when it is needed to reproduce the failure and has passed the existing secret guard.

### Debug Profile

Debug mode optimizes for visibility and diagnosis.

Required behavior:

1. Use `codex-app-server` for Codex Launcher sessions.
2. Use the external visible-session Controller for Parent/Child chains.
3. Create visible Codex-App sessions in the initiating project cwd.
4. Retain full diagnostic evidence equivalent to the current rich evidence model:
   - `start-prompt.md`
   - `launch-request.json`
   - `evidence.json`
   - `app-server-transcript.jsonl`
   - stdout/stderr logs
   - controller requests/responses
   - controller summary
5. Debug evidence must include `profile: "debug"`.
6. Debug success must require `session_visibility.class: "visible_codex_app_session"` for every session that is claimed visible.
7. Debug summaries may be noisy, but must keep a high-level index, for example `debug-index.json`, so the run directory is navigable.

Debug mode is not only for failure. A user may explicitly request it when they want to watch sessions, explain behavior, or validate visible-session contracts.

### Failure Escalation

Compact failure must not silently rerun in debug.

Required compact failure behavior:

1. Stop at the failed gate.
2. Write a compact failure summary with:
   - failed step or child,
   - existing evidence,
   - missing evidence,
   - current output content or output hash when relevant,
   - terminal verdict,
   - `debug_rerun_command`.
3. Report `NOT READY` unless the requested workflow explicitly allows a blocked/manual state.
4. Recommend the debug command as the next action.

Optional future behavior:

1. A human or calling workflow may invoke the debug rerun command.
2. A later automation may support `--on-failure suggest-debug` as a default and `--on-failure rerun-debug` only behind an explicit opt-in flag.

### Evidence Retention Levels

| Artifact | Compact success | Compact failure | Debug success/failure |
|---|---|---|---|
| Aggregate summary | yes | yes | yes |
| Per-session compact evidence | yes | yes | yes |
| Full prompt body | no | optional failure packet | yes |
| Raw event stream / transcript | no | optional failure packet | yes |
| Controller requests/responses | summarized | failed request/response only if useful | yes |
| stdout/stderr | excerpt/hash | excerpt plus path if retained | yes |
| Visible Codex-App proof | no, unless target behavior under test | no, unless target behavior under test | yes |

If a workflow specifically tests visibility, it must run in debug or an explicit visibility-test profile. Compact mode must not be accepted as proof of visible sessions.

### File Layout

Compact runs should prefer a small layout:

```text
<run-dir>/
  run-summary.json
  sessions/
    <target-id>.summary.json
  failure/
    failure-summary.json      # only on failure
```

Debug runs may keep the current detailed layout:

```text
<run-dir>/
  controller/
    requests/
    responses/
    controller-summary.json
    *.stdout.log
    *.stderr.log
  launches/
    parent/
    children/
      <timestamp-target-id>/
        start-prompt.md
        launch-request.json
        evidence.json
        app-server-transcript.jsonl
        app-server-stderr.log
  target/output/
  closeout/
```

The exact directory names may stay compatible with existing tests, but compact mode must not create the full debug tree on successful runs.

### CLI Contract

`AgentDeliverySessionLauncher.cs` must support:

```sh
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --profile compact \
  --handoff <path> \
  --target-id <id> \
  --mode launch \
  --agent codex
```

and:

```sh
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --profile debug \
  --handoff <path> \
  --target-id <id> \
  --mode launch \
  --agent codex \
  --initiating-project-cwd <path>
```

Rules:

1. Missing `--profile` means `compact`.
2. `--profile debug` implies `--adapter codex-app-server` for `--agent codex` unless an explicit incompatible adapter is supplied, in which case the command exits `2`.
3. `--profile compact` implies `--adapter codex-exec` for `--agent codex` unless another supported non-visible adapter is explicitly supplied.
4. `--adapter codex-app-server` with `--profile compact` is a setup error unless the command also declares a visibility-test override. This prevents accidental noisy visible runs.
5. The help output must state which profile is default and what each profile retains.

`AgentDeliveryVisibleSessionController.cs` must support:

```sh
dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- \
  --profile debug \
  --run-dir <dir> \
  --parent-handoff <path> \
  --parent-target-id <id> \
  --initiating-project-cwd <path>
```

Rules:

1. Existing visible controller behavior becomes debug profile behavior.
2. Compact profile must delegate Parent and Child launches to the Launcher with compact/headless profile and must write compact aggregate evidence instead of the full debug request/response/transcript tree on success.
3. A command named `AgentDeliveryVisibleSessionController.cs` must not pretend compact mode is visible. Its summary must state `profile` and `session_class`.
4. Future naming may introduce a neutral `AgentDeliverySessionController.cs`, but this spec does not require a rename.

### Resolver Contract

`WorkflowDoctor.cs --phase evidence-resolution` must understand profile-aware claims.

Required behavior:

1. A compact claim can pass with compact summaries and headless session class.
2. A debug-visible claim must require visible session evidence.
3. A visibility test must fail on compact/headless evidence even if outputs are correct.
4. A compact failure packet with a debug rerun command yields `verdict: not_ready`, not `pass`.
5. Resolver output must include `profile_observed` and, when failing, `recommended_next_action`.

### Workflow Documentation and Skill Contract

`docs/doc-workflow.md` is the canonical place for the profile definition.

Skill edits should be minimal:

1. Do not add long profile explanations to every skill.
2. Replace repeated evidence-detail prose with a short pointer to the canonical profile/resolver contract where touched.
3. Skills may say: "Use the Agent Delivery Run Profile contract; compact is default, debug is explicit for visible diagnosis."
4. Existing skill rules that specifically require visible sessions remain valid, but should route through `profile=debug` instead of restating app-server details.

This spec intentionally avoids another long checklist inside each skill.

## Acceptance Criteria

### Functional

1. Default Launcher runs use compact profile.
2. Default Controller behavior does not create visible sessions unless debug is selected or a visibility-test workflow explicitly requires it.
3. Debug Launcher runs create visible Codex-App sessions and retain full diagnostic evidence.
4. Debug Controller runs create visible Parent/Child Codex-App sessions and retain full controller/launcher evidence.
5. Compact success creates only compact summaries and required final output/closeout artifacts.
6. Compact failure creates a concise failure packet and debug rerun command.
7. Resolver distinguishes compact proof from debug-visible proof.
8. Existing visible regression tests can be updated to call debug mode explicitly.
9. Existing headless launcher tests remain valid under compact mode.
10. No broad skill MD expansion is required.

### Negative Cases

1. `--profile debug --adapter codex-exec` exits `2`.
2. `--profile compact --adapter codex-app-server` exits `2` unless an explicit visibility-test override exists.
3. A visibility-required workflow fails if only compact/headless evidence is present.
4. A compact run with correct final output but missing child closeout remains `NOT READY`.
5. Debug run with visible Parent but headless Child remains `NOT READY`.
6. Debug run with full child evidence but missing final closeout summary remains `NOT READY`.

### Noise Budget

Compact success should create at most:

1. one run summary,
2. one compact session summary per launched session,
3. required target output or closeout artifacts owned by the workflow.

Any additional retained diagnostic file in compact success must be justified by a specific downstream gate and listed in the run summary.

## Verification Commands

These commands are the expected post-implementation gates. They are not all runnable before implementation because the new profile options do not exist yet.

```sh
# from /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help
dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --help
```

Success criteria:

- both help outputs mention `--profile compact|debug`;
- both state that compact is default;
- Launcher help states debug uses visible app-server evidence;
- Controller help states existing visible behavior belongs to debug profile.

```sh
# from /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
node tests/docworkflow-agent-delivery/e2e/validators/run-profile-fixtures.js \
  tests/docworkflow-agent-delivery/e2e/fixtures/run-profiles
```

Success criteria:

- positive compact launcher fixture passes;
- positive debug launcher fixture passes;
- compact output-only false positive fails visibility claim;
- debug visible-missing-child fails;
- compact failure packet with debug rerun command yields `not_ready`;
- invalid adapter/profile combinations fail setup.

```sh
# from /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
rg -n "Agent Delivery Run Profiles|profile compact|profile debug|compact is default" \
  docs/doc-workflow.md \
  skills-repo/skills/spec-orchestrator/SKILL.md \
  skills-repo/skills/spec-change-delivery/SKILL.md \
  skills-repo/skills/spec-closeout/SKILL.md
```

Success criteria:

- central docs contain the full profile contract;
- skills contain only short pointer language or no change when already routed through the resolver;
- no skill duplicates the long compact/debug matrix.

```sh
# from /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
git diff --check
```

Success criteria:

- no whitespace errors.

## Implementation Notes

Suggested implementation order:

1. Add profile parsing and help text to `AgentDeliverySessionLauncher.cs`.
2. Add compact evidence writing while preserving debug/full evidence path.
3. Add profile parsing and help text to `AgentDeliveryVisibleSessionController.cs`.
4. Keep current visible controller behavior behind `--profile debug`.
5. Add compact controller behavior that starts Parent and Child sessions headlessly through the Launcher compact profile.
6. Extend `WorkflowDoctor.cs` evidence resolver for profile-aware verdicts.
7. Add fixtures and validators.
8. Update `docs/doc-workflow.md` with one concise canonical section.
9. Touch skill MDs only if needed to replace duplicated visible-session rules with a short pointer.

Compatibility rule:

Existing commands without `--profile` must keep working, but their retained artifacts may become compact after this change. Tests that require current full evidence must opt into `--profile debug`.

## Closeout Requirements

Implementation closeout must prove:

1. compact is the default;
2. debug creates visible sessions;
3. compact does not create the current noisy debug tree on success;
4. compact failure recommends debug instead of silently rerunning;
5. visibility-required tests cannot pass with compact evidence;
6. skill docs did not grow into another procedural checklist.

## Review Findings Resolved During Hardening

| Finding | Resolution |
|---|---|
| The initial requirement could be misread as removing evidence entirely. | The spec distinguishes minimal operational evidence from full diagnostic evidence; compact still writes enough machine-readable proof for gates. |
| Debug could be accidentally enabled by failure handling. | The spec forbids silent rerun and requires a debug rerun command instead. |
| Existing visible controller naming could conflict with compact mode. | The spec allows a future neutral controller name but requires the current controller summary to state `profile` and `session_class`. |
| Skills could grow with repeated profile details. | The spec makes `docs/doc-workflow.md` canonical and limits skills to short pointer language. |
| Visibility tests might accidentally pass with compact evidence. | The resolver and negative cases require visibility claims to fail on compact/headless evidence. |

## Mini-Retro

- What was decided? Agent Delivery gets two run profiles: compact default and explicit debug.
- What changed? Visibility and diagnostic verbosity become profile behavior instead of implicit Launcher/Controller behavior.
- What remains open? A future neutral controller name may reduce confusion, but the current implementation can remain in place if summaries state `profile` and `session_class`.
- Which evidence/verification is missing? Post-implementation fixture and resolver tests are still future gates.
- Which skill/workflow friction showed up? Large skill MDs are already too easy to skip; this spec keeps the detailed contract centralized.
- Session/context state: ready for implementation planning or a bounded tooling delivery spec.
