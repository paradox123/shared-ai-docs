**Date:** 2026-05-10
**Status:** 🟡 Spec
**Scope:** Child spec hardening for `ADV-CAS-S2 Visible Evidence Validator` under parent `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`.

---

## Review Control Surface

- Spec Variant: Contract-heavy Parent/Child validation child spec.
- Goldstandard Status: post-S1 hardened child spec; implementation-ready for the validator slice.
- Goal: Define the validator contract, fixture strategy, negative matrix, acceptance cases and verification lifecycle for proving that Agent Delivery evidence represents a real visible Codex-App session rather than a headless or queued false positive.
- In Scope: evidence class validation; visible-app positive validation; false-positive rejection for `codex exec`, `source='exec'`, missing visibility class, wrong title, wrong cwd, missing thread, queued-only evidence and unarchived visible sessions; fixture manifest requirements; future tool command contract; parent coverage and conformance.
- Out of Scope: creating visible sessions; implementing the app-server Launcher adapter; editing `AgentDeliverySessionLauncher.cs`; editing validator/runtime/test files in this hardening run; creating handoffs or launch evidence; running `MD-E2E-5`; changing closeout archive implementation.
- Key Test / Harness Cases: positive app-server evidence passes; headless `codex exec` evidence fails visible-session validation; `status: "launched"` without `session_visibility.class: "visible_codex_app_session"` fails; `thread_source_observed: "exec"` fails; wrong parent-prefixed title fails; wrong initiating cwd fails; missing thread/list proof fails; queued/manual-only evidence cannot count as visible; visible evidence with missing prompt or turn linkage fails; visible evidence with required closeout archive still unarchived fails.
- Key Verification Commands: hardening/readiness: `dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --help`; `node tests/docworkflow-agent-delivery/e2e/validators/visible-app-launcher-s1.js tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-launcher-s1`; `cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- --index /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-10\ Agent\ Delivery\ Visible\ Codex\ App\ Sessions\ Orchestration\ Pack.md --child ADV-CAS-S2 --handoff /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/adv-cas-s2-session-handoff.md`; future S2 delivery: `dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence`; existing launch-evidence regression remains green through `dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/agent-delivery-session-launcher/fixtures/launch-evidence`; `git diff --check`.
- Open Blockers: None for S2 implementation readiness. Fixture files and `ValidateVisibleCodexAppSessionEvidence.cs` are in the S2 implementation write-set.
- Readiness Status: IMPLEMENTATION READY for exactly `ADV-CAS-S2`.

## Session Briefing

- Modus/Skill: `child-spec-hardening`.
- Source of Truth: parent spec `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`; orchestration pack `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`; `docs/doc-workflow.md`; current Launcher evidence behavior in `skills-repo/tools/AgentDeliverySessionLauncher.cs`.
- Ziel: Harden only the S2 validator child contract so a later implementation session knows exactly what evidence to accept and reject.
- Nicht-Ziele: no runtime implementation, no test runner edits, no MD-E2E-5 execution, no app-server launch, no orchestration pack or handoff edits.
- In Scope: this child spec, Child Index sync and persisted S2 handoff.
- Erwarteter Output: this hardened child spec with explicit blockers.
- Verification/Review: content-quality review, command-contract notes, and local hardening checks that do not run live visible-session workflows.
- Offene Entscheidungen: no product decision is needed from the user.

## Goal

`ADV-CAS-S2` turns the parent visible-session evidence requirements into a deterministic validator and fixture matrix.

The validator must prevent the historical false positive where a successful `codex exec` launch, same-cwd local SQLite row, or `status: "launched"` was treated as a visible Codex-App session. It validates evidence artifacts only. It does not create sessions, name sessions, archive sessions, or run the Parent + five Child workflow.

## In Scope

1. Define semantic validation rules for `visible_codex_app_session` evidence.
2. Define failure rules for headless CLI, queued/manual, wrong title, wrong cwd, missing thread/list proof, missing prompt/turn linkage and unarchived visible sessions.
3. Define source-controlled fixture paths and fixture manifest shape.
4. Define future validator command behavior and exit-code expectations.
5. Preserve existing `ValidateAgentDeliveryLaunchEvidence.cs` launch/queue evidence behavior while adding visible-session-specific validation.
6. Provide a handoff-ready contract once S2 is synchronized to the S1 schema.

## Out of Scope

1. No app-server adapter implementation.
2. No visible Codex-App session creation.
3. No direct SQLite mutation or UI/sidebar screenshot tooling.
4. No `MD-E2E-5` live regression execution.
5. No changes to `docs/doc-workflow.md`, `skills-repo/skills/spec-closeout/SKILL.md`, orchestration pack, handoffs, tools, tests or runtime code in this hardening run.
6. No acceptance of historical `exec` evidence as visible-session proof.

## Parent/Master Coverage

| Parent Requirement | S2 Coverage | Status |
|---|---|---|
| `ADV-PR1` | Enforces the distinct evidence classes `headless_cli_session`, `queued_manual_start`, `manual_visible_start`, `visible_codex_app_session` and `traceable_but_not_visible`. | covered by contract; blocked for implementation by S1 schema sync and missing fixtures |
| `ADV-PR5` | Validates required visibility evidence fields for execution channel, title, cwd, thread, source, proof method, prompt and turn linkage. | covered by contract; field names pending S1 |
| `ADV-PR6` | Rejects `codex exec`, `source='exec'`, wrong title, wrong cwd, missing thread and queued-only false positives. | covered by harness matrix |
| `ADV-PR10` | Supplies the deterministic gate that lets docs/skills stop treating `status: "launched"` from `codex exec` as visible-app success. | supported; docs sync belongs to later child or integration owner |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `ADV-PR1` | S2 validates evidence classes; S1/S5 may produce or consume them. | preserves | Keep class values exact after S1 freeze. |
| `ADV-PR5` | S2 validates the visible-session schema but does not define app-server adapter internals beyond consumed evidence. | narrows_with_rationale | S1 owns evidence production; S2 consumes frozen fields. |
| `ADV-PR6` | S2 owns false-positive rejection. | preserves | Fixture matrix must include every parent negative case. |
| `ADV-PR10` | S2 provides a machine gate for stale launch wording. | extends | Later docs/skill sync must call this validator or cite its result. |
| `ADV-PR2`, `ADV-PR3`, `ADV-PR4` | S2 does not create app-server sessions, initiating cwd, or titles, but validates the resulting evidence. | preserves | S1 remains producer and schema owner. |
| `ADV-PR7`, `ADV-PR8`, `ADV-PR9` | S2 does not run MD-E2E-5, enforce control-session boundaries, or archive sessions. | preserves | S3/S4/S5 consume S2 results. |

No parent requirement is contradicted. No S2 behavior may mark a queued, headless or unverified record as visible success.

## Decision Freeze Pack

Frozen for S2:

1. `codex exec` and `source='exec'` are never accepted as visible Codex-App proof in the current contract.
2. A visible success requires `session_visibility.class == "visible_codex_app_session"` and `session_visibility.visible_in_codex_app == true`.
3. `status: "launched"` remains process status only; it is not visibility proof.
4. The title must follow `{ParentSpecAbbrevAndNumber}: {Hardening|Implementation} - {ChildSpecDesignation}`.
5. `cwd_observed` must equal `initiating_project_cwd` for app-visible evidence.
6. The preferred machine proof method is `app_server_thread_list`, based on `thread/start`, `thread/name/set`, `turn/start` and later `thread/list`.
7. S2 must not run `MD-E2E-5`; it only validates fixture evidence and later supports S3.

S1 evidence schema now consumed by S2:

1. `schema_version` is `agent-delivery.session-launch.v2`.
2. Visible launches use `execution_channel: "app_server"` and `adapter_id: "codex-app-server"`.
3. Required top-level context fields are `initiating_project_cwd`, `project_cwd_source`, `target_workspace`, `session_stage`, `parent_spec_abbrev_and_number`, `child_spec_designation`, `session_title`, `prompt_sha256` and `evidence_paths.prompt`.
4. App-server transcript evidence is referenced by `evidence_paths.app_server_transcript` and `app_server.transcript_path`.
5. Current app-server visible evidence observes both `thread_source_observed: "vscode"` and `source_kind_observed: "vscode"`.
6. Required app-server proof flags are `thread_start_observed`, `thread_name_set_observed`, `turn_start_observed`, `turn_completed_status: "completed"` and `thread_list_observed`.

Provisional implementation decision:

1. S2 should add a dedicated visible-session validator file named `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs` and keep `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs` backward compatible for launch/queue evidence.
2. If S1 freezes visible-session schema directly inside `ValidateAgentDeliveryLaunchEvidence.cs`, S2 may extend that tool instead, but the existing launch-evidence fixture command must remain green.
3. This decision is now implementation-ready for S2.

## Normative Contract

### Validator Purpose

The S2 validator answers one question:

```text
Does this evidence prove a visible Codex-App Agent Delivery session under the parent contract?
```

It must not infer success from process exit alone. It must not query the live Codex state database as a substitute for persisted evidence. It may validate paths, hashes and transcript files that are named by the evidence.

### Inputs

The future validator must support fixture mode:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- \
  --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence
```

It should also support single-case mode after S1 freezes field names:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- \
  --evidence /absolute/path/to/evidence.json \
  --prompt /absolute/path/to/start-prompt.md \
  --expect-title "ADV-CAS-1: Implementation - S2 Visible Evidence Validator" \
  --expect-initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
```

Single-case mode is not implementation-ready until S1 freezes the option names and required evidence fields.

### Evidence Semantics

The validator must evaluate these semantic fields after S1 freezes exact names:

| Semantic Field | Required For Visible Success | Rule |
|---|---:|---|
| schema id/version | yes | Must match an accepted S1 visible-session evidence schema. |
| status | yes | `launched` may coexist with visible success but cannot prove it alone. |
| execution channel | yes | Must be `app_server` or reviewed manual-visible equivalent; `headless_cli` fails. |
| initiating project cwd | yes | Absolute path used for app-visible `thread/start.cwd`. |
| target workspace | yes | Recorded separately; may differ only when S1 explicitly supports cross-project delivery. |
| session title | yes | Exact parent-prefixed title. |
| session stage | yes | `Hardening` or `Implementation`; no uncontracted stage labels. |
| parent spec abbreviation and number | yes | For this parent, orchestration assigned `ADV-CAS-1`. |
| child spec designation | yes | Human-readable child designation, for S2 `S2 Visible Evidence Validator` or equivalent frozen designation. |
| prompt hash | yes | Must match persisted `start-prompt.md`. |
| turn proof | yes for app-server launches | Must show a materialized `turn/start` or equivalent first user message. |
| session visibility class | yes | Must be `visible_codex_app_session`. |
| visible in Codex app | yes | Must be boolean true or equivalent accepted value. |
| proof status | yes | Must be `verified`. |
| proof method | yes | `app_server_thread_list`, `codex_app_ui_observation`, or `manual_human_confirmation` only under manual-visible mode. |
| thread id | yes | Non-empty real thread id. |
| observed source | yes | Must be app-visible for current contract, currently `vscode` from app-server list; `exec` fails. |
| observed cwd | yes | Must equal initiating project cwd. |
| observed title | yes | Must equal expected session title. |
| sidebar/default list observed | yes | Must prove default app-visible list or sidebar-equivalent observation. |
| rollout/app-server path | yes when available | Required for app-server machine proof unless S1 freezes a replacement transcript rule. |

### Positive Visible-App Rules

A positive app-server evidence record passes only when all of these are true:

1. Evidence is syntactically valid JSON.
2. Evidence schema matches the S1-frozen visible-session schema.
3. `execution_channel` is `app_server`.
4. The app-server proof contains `thread/start`, `thread/name/set`, `turn/start` and `thread/list` evidence or S1-frozen equivalents.
5. The same `thread_id` appears in the creation, turn and list proof.
6. The listed thread has an app-visible source for the current Codex app contract, currently `source: "vscode"`.
7. The observed title equals the expected title.
8. The observed cwd equals `initiating_project_cwd`.
9. The prompt hash matches `start-prompt.md`.
10. The validator can distinguish the visible session from the control/editing session when such identifiers are present.

### Negative Rules

The validator must fail visible-session validation when any of these are true:

1. `mechanism.actual_command` contains `codex exec`.
2. `execution_channel` is `headless_cli`.
3. `session_visibility.class` is absent or not `visible_codex_app_session`.
4. `session_visibility.visible_in_codex_app` is false, missing or non-boolean.
5. `thread_source_observed`, `source_kind_observed` or legacy `codex_app.thread_source` is `exec`.
6. `codex_app.visibility_status` is only `verified_same_project`.
7. `status` is `queued`, `manual_start_required`, `blocked` or `failed`.
8. Evidence has no real `thread_id`.
9. Evidence has no proof that the thread appeared in normal app-server `thread/list`, UI/sidebar observation, or accepted manual visible confirmation.
10. The observed title uses the child id as the prefix, for example `ADV-CAS-S2: Implementation`, instead of the parent prefix `ADV-CAS-1: Implementation - ...`.
11. The observed cwd equals only `target_workspace` but not `initiating_project_cwd`, unless S1 freezes an explicit cross-project exception.
12. The prompt hash is absent, malformed or does not match the persisted prompt.
13. App-server evidence created only an empty thread without a materialized turn.
14. Closeout-required evidence says a visible thread remains unarchived when the case requires archive validation.

### Exit Code Contract

Fixture mode should follow the existing launch-evidence validator pattern:

| Condition | Exit Code | Output Contract |
|---|---:|---|
| all fixture cases match expected outcomes | `0` | Print one line per case and final `RESULT: PASS (<n> cases)`. |
| one or more fixture cases mismatch | `1` | Print mismatched cases, errors and final `RESULT: FAIL`. |
| manifest missing, invalid JSON, invalid fixture shape, unsupported schema | `2` | Print a setup error to stderr. |

Single-case mode should exit `0` only for a visible-session pass, `1` for validation failure and `2` for invalid CLI usage or unreadable inputs.

## Canonical Examples and Fixtures

Pattern: **Hybrid**, blocked by S1 schema sync and missing fixture files.

This child spec uses a compact pseudo-sketch for reader orientation and requires full source-controlled fixtures for implementation. The embedded sketch below is not a canonical machine-readable input and must not be copied into tests as-is.

```json
{
  "schema_version": "S1_FROZEN_VISIBLE_SESSION_SCHEMA",
  "status": "launched",
  "execution_channel": "app_server",
  "initiating_project_cwd": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
  "target_workspace": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
  "session_title": "ADV-CAS-1: Implementation - S2 Visible Evidence Validator",
  "session_visibility": {
    "class": "visible_codex_app_session",
    "visible_in_codex_app": true,
    "proof_status": "verified",
    "proof_method": "app_server_thread_list",
    "thread_id": "019e0000-0000-7000-8000-000000000000",
    "thread_source_observed": "vscode",
    "cwd_observed": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
    "title_observed": "ADV-CAS-1: Implementation - S2 Visible Evidence Validator",
    "sidebar_or_default_list_observed": true
  }
}
```

Required fixture root after S1 freeze:

```text
tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/
  fixture-manifest.json
  positive-app-server/
    evidence.json
    start-prompt.md
    app-server-transcript.json
  headless-exec/
    evidence.json
    start-prompt.md
  source-exec/
    evidence.json
  launched-without-visible-class/
    evidence.json
  wrong-title/
    evidence.json
  wrong-cwd/
    evidence.json
  missing-thread/
    evidence.json
  queued-only/
    evidence.json
  prompt-hash-mismatch/
    evidence.json
    start-prompt.md
  empty-thread-no-turn/
    evidence.json
    app-server-transcript.json
  unarchived-visible-closeout/
    evidence.json
    closeout-summary.json
```

Fixture manifest requirements:

1. `fixture-manifest.json` lists every case id, evidence path, optional prompt path, optional transcript path, expected outcome and expected failure class.
2. Positive fixture fields are normative after S1 freeze.
3. Negative fixtures are normative for failure reasons, not for exact incidental timestamps or generated ids.
4. Fixtures are in scope for S2 implementation, not for this hardening run.
5. Harness verification must prove every manifest case was executed; missing fixture files fail setup with exit code `2`, not skipped success.

## Control Flow and Failure Cases

Validator flow:

1. Parse CLI options.
2. Load fixture manifest or single evidence input.
3. Parse evidence JSON and optional prompt/transcript/closeout files.
4. Resolve expected title and initiating cwd from fixture metadata or CLI options.
5. Apply schema-version compatibility gate.
6. Apply visible-session positive rules.
7. Apply negative false-positive rules.
8. Apply prompt/turn linkage rules.
9. Apply archive-required rule when fixture metadata marks closeout validation as required.
10. Print per-case result and aggregate result.

Failure classification values should include:

| Failure Class | Meaning |
|---|---|
| `invalid_schema` | Missing or unsupported S1 visible-session schema. |
| `headless_cli_not_visible` | Evidence came from `codex exec` or `headless_cli`. |
| `missing_visible_class` | No visible-session class or visible boolean. |
| `source_exec_not_visible` | Observed thread source is `exec`. |
| `wrong_title` | Observed title does not match parent-prefixed title contract. |
| `wrong_cwd` | Observed cwd does not match initiating project cwd. |
| `missing_thread` | Missing thread id or list proof. |
| `queued_not_visible` | Queued/manual-only evidence is traceable but not visible proof. |
| `prompt_hash_mismatch` | Prompt hash does not match `start-prompt.md`. |
| `missing_turn` | App-server thread exists without a materialized turn. |
| `unarchived_visible_session` | Closeout-required visible thread remains unarchived. |

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| S2-VIS-001 positive app-server | Prove valid visible evidence passes. | `positive-app-server/` | Fixture run exit `0`; case `pass`. | Evidence, prompt, transcript all read. | Transcript contains no secrets; prompt hash matches. |
| S2-VIS-002 headless command | Reject `codex exec` even when status is `launched`. | `headless-exec/` | Fixture run exit `0`; case expected `fail` with `headless_cli_not_visible`. | Evidence read. | `mechanism.actual_command` containing `codex exec` fails. |
| S2-VIS-003 exec source | Reject local metadata with `source='exec'`. | `source-exec/` | Case expected `fail` with `source_exec_not_visible`. | Evidence read. | `verified_same_project` cannot pass visible proof. |
| S2-VIS-004 missing visible class | Reject launched evidence without `session_visibility`. | `launched-without-visible-class/` | Case expected `fail` with `missing_visible_class`. | Evidence read. | Status alone cannot pass. |
| S2-VIS-005 wrong title | Enforce parent-prefixed title. | `wrong-title/` | Case expected `fail` with `wrong_title`. | Evidence read. | Child-id-only prefix fails. |
| S2-VIS-006 wrong cwd | Enforce initiating project cwd. | `wrong-cwd/` | Case expected `fail` with `wrong_cwd`. | Evidence read. | Target workspace match alone is insufficient. |
| S2-VIS-007 missing thread | Reject missing thread or list proof. | `missing-thread/` | Case expected `fail` with `missing_thread`. | Evidence read. | Empty thread id fails. |
| S2-VIS-008 queued only | Keep queue traceability separate from visible success. | `queued-only/` | Case expected `fail` with `queued_not_visible`. | Evidence read. | `queued` and `manual_start_required` do not pass visible claims. |
| S2-VIS-009 prompt hash mismatch | Prove prompt provenance is checked. | `prompt-hash-mismatch/` | Case expected `fail` with `prompt_hash_mismatch`. | Evidence and prompt read. | No prompt body is printed in error output. |
| S2-VIS-010 empty thread | Require materialized turn proof. | `empty-thread-no-turn/` | Case expected `fail` with `missing_turn`. | Evidence and transcript read. | `thread/start` alone fails. |
| S2-VIS-011 unarchived visible closeout | Support S5/S3 closeout gate. | `unarchived-visible-closeout/` | Case expected `fail` with `unarchived_visible_session`. | Evidence and closeout summary read. | Visible retained thread blocks closeout-required pass. |
| S2-VIS-012 malformed setup | Prove setup errors are distinct. | Manifest path to missing evidence. | Fixture run exit `2`. | Error names missing file. | Missing fixture cannot be reported as expected negative pass. |

## Verification Commands

Do not run `MD-E2E-5` for S2 hardening or S2 implementation. `MD-E2E-5` belongs to S3 after S1/S2/S4/S5 contracts are ready.

Hardening-only checks for this spec:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --help
git diff --check -- "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S2 Visible Evidence Validator.md"
```

Existing launch-evidence regression that must keep passing after S2 implementation:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- \
  --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/agent-delivery-session-launcher/fixtures/launch-evidence
```

Future S2 delivery gate after S1 freezes schema:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- \
  --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence
```

Future source checks after S2 implementation:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
rg -n "visible_codex_app_session|headless_cli_session|traceable_but_not_visible|source_exec_not_visible|wrong_title|wrong_cwd" \
  /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools \
  /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence
```

Success criteria:

1. Existing launch-evidence validator fixtures still pass.
2. New visible-session fixture command exits `0` only when all positive and negative cases match expected outcomes.
3. Negative cases are executed and reported as expected failures, not skipped.
4. No command starts Codex app-server, launches a session, archives a session or runs `MD-E2E-5` during S2 implementation verification.

## Definition of Ready for Implementation

S2 is ready for implementation only after all of these are true:

1. S1 freezes the visible-session evidence schema and records the exact field names and required/optional status.
2. S1 freezes title, initiating cwd, transcript, prompt hash and turn linkage evidence fields.
3. This S2 spec is updated to replace S1-dependent placeholders with the frozen schema references.
4. The orchestration pack S2 row is synchronized to this child spec path.
5. `_specs/child-session-handoffs/adv-cas-s2-session-handoff.md` exists and points to this child spec.
6. `ValidateChildReadiness.cs` passes or is intentionally run with a non-ready allowance only for another hardening iteration.
7. Future implementation write-set is confirmed as concrete and does not include unrelated runner, workflow doc or app-server adapter files.
8. Hardening command-contract rehearsal evidence is captured.

Current status: not ready. The primary blockers are `[MISSING S1 schema sync]` and missing source-controlled visible evidence fixtures.

## Definition of Done / Closeout Evidence

S2 implementation is done only when:

1. The visible-session validator exists or the existing validator is extended according to the S1-frozen schema.
2. Source-controlled fixtures under `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/` cover every S2 harness case.
3. The future visible-session fixture command passes.
4. The existing launch-evidence fixture command still passes.
5. Negative cases fail for the intended failure class.
6. Validation output avoids leaking prompt bodies, environment values or secret-like tokens.
7. Closeout retains fixture summaries and command output references.
8. No MD-E2E-5 live run is claimed as S2 evidence.

## Dependencies and Write-Set

Hardening lane write ownership for this run:

```text
_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S2 Visible Evidence Validator.md
```

Read-only sources for this run:

```text
_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md
_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md
docs/doc-workflow.md
skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs
skills-repo/tools/AgentDeliverySessionLauncher.cs
tests/agent-delivery-session-launcher/fixtures/launch-evidence/**
tests/docworkflow-agent-delivery/README.md
```

Future S2 implementation write-set after S1 freeze:

```text
skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs
skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs
tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/**
tests/agent-delivery-session-launcher/fixtures/launch-evidence/**
```

Shared/read-only files for future S2 implementation unless the integration owner explicitly expands scope:

```text
skills-repo/tools/AgentDeliverySessionLauncher.cs
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh
tests/docworkflow-agent-delivery/testcases/md-e2e-5-visible-codex-app-sessions.md
docs/doc-workflow.md
skills-repo/skills/spec-closeout/SKILL.md
```

Serial dependencies:

1. S2 must synchronize to the S1 visible evidence schema before implementation.
2. S2 must complete before S3 can rely on visible-session validation.
3. S5 closeout archive fields may add additional archive validation cases, but S2 can first implement visible false-positive validation against an S1-frozen schema.

Parallelization:

1. S2 hardening can overlap with S4 only while S1 schema is stable or once S2 keeps S1-dependent fields explicitly blocked.
2. S2 implementation must not run in parallel with S1 implementation while the evidence schema is still changing.

## Closeout Sync Targets

These are not writable in this hardening lane, but must be synchronized by the integration owner before implementation readiness:

1. `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md` Child Index row for `ADV-CAS-S2`:
   - `Session Handoff` should point to `_specs/child-session-handoffs/adv-cas-s2-session-handoff.md`.
   - `Readiness / Hardening Verdict` should mirror this spec while blocked: `NEEDS HARDENING - requires S1 schema sync and fixture implementation`.
   - `Child Spec` should point to this file.
2. `_specs/child-session-handoffs/adv-cas-s2-session-handoff.md` should be kept synchronized during later integration sync.
3. OpenSpec ledger `openspec/changes/agent-delivery-visible-session-validator/` should be created only when implementation starts.
4. Later closeout must retain S2 fixture command output and visible-validator fixture summaries.

## Child Session Handoff

No persisted S2 handoff was created in this hardening run because the user's write ownership is limited to this child spec file and the child is not implementation-ready.

Required future handoff path:

```text
_specs/child-session-handoffs/adv-cas-s2-session-handoff.md
```

Minimum future handoff contract:

1. Parent: `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`.
2. Child: `ADV-CAS-S2`.
3. Child Spec: this file.
4. Child Index / Queue: `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`.
5. Current Verdict: `IMPLEMENTATION READY`.
6. Next Mode/Skill: `spec-change-delivery`.
7. Allowed Write-Set: concrete validator/tool/fixture/spec paths only; no Launcher adapter, runner integration, closeout skill, docs or MD-E2E-5 live runner files.

## Content Quality Review

| Dimension | Result | Notes |
|---|---|---|
| Correctness / domain fit | pass | The spec targets the exact false positive in the parent: headless `exec` evidence cannot prove app visibility. |
| Scope discipline | pass | Runtime implementation, MD-E2E-5, app-server launch and shared control edits are excluded. |
| Completeness | pass | Contract, cases, fixture strategy and S1 evidence schema are present. |
| Consistency | pass | Review Control Surface, DoR and verdict all report S2 as implementation-ready. |
| Unambiguity | pass | S1-dependent fields are now concrete. |
| Feasibility | pass | Existing launch validator and S1-local visible validator patterns give a feasible command/fixture model. |
| Verifiability | pass | S2 has concrete fixture cases and future commands; command contracts were rehearsed where possible. |
| Traceability | pass | Parent requirements `ADV-PR1`, `ADV-PR5`, `ADV-PR6` and `ADV-PR10` are mapped. |

## Hardening Verdict

Final readiness verdict:

```text
IMPLEMENTATION READY
```

Blocking findings: none.

Implementation notes:

1. S2 must add the reusable visible-session validator and fixture family in the allowed write-set.
2. S2 must keep the existing `ValidateAgentDeliveryLaunchEvidence.cs` fixture regression green.
3. S2 must not run `MD-E2E-5`.

Non-blocking notes:

1. UI/sidebar screenshot proof remains optional; app-server `thread/list` machine proof is the default parent-approved proof.
2. Long-lived app-server socket lifecycle remains outside S2.

## Mini-Retro

- Was wurde entschieden? S2 is a validator/fixture child only. It validates visible-session evidence and false positives, but it does not launch, archive or run live workflows.
- Was wurde geaendert? Created this child spec with Review Control Surface, parent conformance, contract, fixture strategy, harness cases, verification lifecycle, then re-hardened it against the implemented S1 schema.
- Was bleibt offen? S2 implementation must create the reusable validator and visible evidence fixtures.
- Welche Evidenz/Verification fehlt? No future visible-session validator exists yet; no S2 visible evidence fixtures exist yet.
- Welche Skill-/Workflow-Reibung ist aufgefallen? S1's local validator provides a useful pattern, but S2 must generalize it without taking over Launcher or MD-E2E-5 scope.
- Session-/Kontextzustand: Ready for a fresh `spec-change-delivery` session for S2.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-10 | Codex | Created and hardened the `ADV-CAS-S2 Visible Evidence Validator` child spec as a blocked draft. |
| 2026-05-10 | Codex | Re-hardened S2 after S1 implementation, synchronized the concrete S1 evidence schema, and promoted S2 to `IMPLEMENTATION READY`. |

SessionId: 2026-05-10-adv-cas-s2-visible-evidence-validator-hardening
