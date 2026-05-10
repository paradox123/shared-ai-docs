**Date:** 2026-05-10
**Status:** 🔵 Implemented
**Scope:** Child `ADV-CAS-S1` for the Launcher visible Codex-App/App-Server adapter.
**SessionId:** `adv-cas-s1-hardening-20260510`

---

## Goal

Make the Agent Delivery Session Launcher implementation-ready for a bounded `codex app-server` adapter that starts a visible Codex-App session, sets the deterministic Agent Delivery title, starts the persisted handoff prompt turn, and writes evidence proving the thread appears through the normal app-server interactive thread list.

## Review Control Surface

- Spec-Variante: Contract-heavy child spec for Launcher adapter implementation.
- Goldstandard Status: hardened child spec; implementation-ready after Child Index, handoff, command-contract rehearsal and validator sync.
- Ziel: Upgrade `AgentDeliverySessionLauncher.cs` so a later delivery can create visible Codex-App sessions through `codex app-server`, with deterministic initiating-project cwd, title and visibility evidence, while preserving the existing headless `codex exec` path as explicitly non-visible.
- In Scope: app-server adapter mode, `thread/start`, `thread/name/set`, `turn/start`, `thread/list` proof, initiating-project cwd fields, title derivation, visible-session evidence fields, headless-exec downgrade semantics, S1-local adapter evidence checks, targeted workflow-doc wording where directly coupled to Launcher evidence semantics.
- Out of Scope: `ADV-CAS-S2` validator fixture implementation, `ADV-CAS-S3` `MD-E2E-5` suite runner, `ADV-CAS-S4` control-session boundary enforcement, `ADV-CAS-S5` `thread/archive` support, running the live Parent+5 Child regression, direct SQLite mutation, screenshot/UI sidebar proof, fake backfill of historical `exec` evidence.
- Wichtigste Test-/Harness-Cases: `S1-APP-SERVER-POSITIVE`, `S1-HEADLESS-EXEC-DOWNGRADE`, `S1-MISSING-APP-SERVER`, `S1-WRONG-CWD`, `S1-WRONG-TITLE`, `S1-EMPTY-THREAD`, `S1-TURN-FAILED`, `S1-PROMPT-HASH-MISMATCH`, `S1-SECRET-REDACTION`.
- Wichtigste Verification Commands: `codex --help`; `codex app-server --help`; `codex app-server generate-ts --out /tmp/codex-app-schema-adv-cas-s1`; canonical JSON parse; targeted Launcher adapter/evidence checks defined below; `git diff --check`; readiness validator against the Child Index and S1 handoff.
- Offene Entscheidungen: None blocking. UI/sidebar screenshot proof and long-lived app-server sockets remain later enhancements.
- Readiness Status: IMPLEMENTED for `spec-change-delivery` of exactly `ADV-CAS-S1`.

## In Scope

1. Extend `skills-repo/tools/AgentDeliverySessionLauncher.cs` with an explicit visible app-server adapter state.
2. Add `skills-repo/tools/AgentDeliveryCodexAppServerClient.cs` if a separate helper keeps protocol handling maintainable.
3. Persist launch evidence under `_specs/agent-delivery-session-launches/**` with the evidence contract below.
4. Add S1-local fixtures or assertions only for the Launcher adapter/evidence contract.
5. Update `docs/doc-workflow.md` only where S1 must replace stale wording that treats `status: launched`, `verified_same_project`, or `codex exec` as visible-app proof.
6. Update this child spec, the orchestration pack and the handoff only for S1 delivery evidence and verdict sync.

## Out of Scope

1. No runtime code is implemented during this hardening session.
2. No `MD-E2E-5` live workflow is run by hardening or S1 implementation.
3. No full visible-session validator fixture matrix is implemented in S1; S2 owns it.
4. No closeout archive helper or `spec-closeout` behavior is implemented in S1; S5 owns it.
5. No direct writes to `~/.codex/state_5.sqlite` or Codex rollout JSONL files are allowed.
6. No historical `source='exec'` evidence may be upgraded to `visible_codex_app_session`.

## Parent/Master Coverage

| Parent Requirement | S1 Coverage |
|---|---|
| `ADV-PR2` | Primary owner. Implements the app-server launch path using `thread/start`, `thread/name/set`, `turn/start`, then `thread/list` interactive-source proof. |
| `ADV-PR3` | Primary owner. Adds and records `initiating_project_cwd`, `target_workspace`, and `project_cwd_source`. |
| `ADV-PR4` | Primary owner for title derivation and evidence. S2 later validates title negatives. |
| `ADV-PR1` | Supports by keeping headless, queued/manual and visible classes distinct in Launcher evidence. |
| `ADV-PR5` | Supports by writing S1 evidence fields and retaining app-server transcript paths for downstream validation. |
| `ADV-PR10` | Supports by downgrading old `codex exec` visibility wording where S1 touches Launcher/workflow docs. |

## Parent Scope Conformance

| Parent Intent | Conformance | S1 Contract |
|---|---|---|
| Visible app sessions use app-server, not `codex exec`. | preserves | Visible mode must start or connect to `codex app-server`, never call `codex exec` and relabel the result. |
| Initiating Codex project owns visible cwd. | preserves | `thread/start.params.cwd` must equal `initiating_project_cwd`; `target_workspace` remains separate evidence and prompt context. |
| Title format is parent-owned. | preserves | Session title is exactly `{ParentSpecAbbrevAndNumber}: {Hardening|Implementation} - {ChildSpecDesignation}`. For this parent, the prefix is `ADV-CAS-1`. |
| Validator and suite negatives are downstream slices. | narrows_with_rationale | S1 must produce enough evidence for S2/S3, but it does not implement their fixture matrices or live workflow runner. |
| Closeout archives visible sessions. | defers_to_child | S1 records `thread_id`, title and evidence paths needed by S5; S5 owns archive behavior. |

No parent requirement is missing or contradicted.

## Decision Freeze Pack

| Decision | Frozen Value | Rationale |
|---|---|---|
| Parent title prefix | `ADV-CAS-1` | Assigned by the orchestration pack and required by the parent title contract. |
| Visible adapter selector | Explicit visible adapter state such as `--adapter codex-app-server` | Freezes a clear app-server mode without removing the existing headless path. |
| Headless selector | Existing `codex exec` behavior remains `headless_cli` | Backward compatibility and negative evidence clarity. |
| App-server lifecycle | Per-run `codex app-server --listen stdio://` by default | Parent marks shared long-lived sockets as non-blocking future optimization. |
| Visibility proof | Normal `thread/list` and/or `sourceKinds: ["vscode"]`, after a materialized `turn/start` | Local spike showed empty threads do not appear, and completed turns list as `source: "vscode"`. |
| Runtime cwd | `thread/start.params.cwd == initiating_project_cwd` | Preserves visible project context. |
| Live suite execution | Do not run `MD-E2E-5` in S1 | S3 owns the final Parent + five Child regression. |

## Normative Contract

### Adapter Modes

| Channel | Mechanism | Visibility Class |
|---|---|---|
| `headless_cli` | Existing `codex exec --json -C <target_workspace> --output-last-message <file> -` path. | `headless_cli_session` or `traceable_but_not_visible`; never `visible_codex_app_session`. |
| `app_server` | `codex app-server --listen stdio://` JSON-RPC flow. | `visible_codex_app_session` only after thread/list proof passes. |
| `manual_queue` | Existing queue/start-prompt behavior. | `queued_manual_start` until paired with separate manual visible evidence. |

The exact CLI flag names may be chosen in delivery, but the user-facing command contract must expose an operator-selectable visible path. Evidence must state the selected `execution_channel`.

### App-Server Flow

For `execution_channel: "app_server"`, the Launcher must:

1. Start or connect to `codex app-server --listen stdio://`.
2. Send `initialize` and record sanitized protocol metadata.
3. Send `thread/start` with `cwd == initiating_project_cwd` and persisted/non-ephemeral behavior.
4. Send `thread/name/set` before `turn/start`.
5. Send `turn/start` with the persisted `start-prompt.md` content.
6. Wait until the turn reaches `completed`, or record an explicit failed/blocked/timeout status.
7. Query normal `thread/list` and/or `sourceKinds: ["vscode"]`.
8. Mark visibility success only if the same thread id appears with matching cwd, title/name, app-visible source kind and rollout/path evidence.

An empty `thread/start` without a materialized turn must not count as visible success.

### Initiating Project CWD

Required fields:

- `initiating_project_cwd`: absolute path used for `thread/start.cwd`.
- `target_workspace`: absolute path from the handoff/work target.
- `project_cwd_source`: `current_thread_cwd`, `explicit_cli_arg`, or `handoff_target_workspace_fallback`.

Rules:

1. `thread/start.cwd` uses `initiating_project_cwd`.
2. `target_workspace` remains the handoff/work target.
3. If no current-thread cwd is available, delivery must add an explicit CLI argument or documented fallback and record the source.
4. `cwd_observed` must equal `initiating_project_cwd` for visible success.

### Title Contract

S1 uses:

```text
ADV-CAS-1: {Hardening|Implementation} - {ChildSpecDesignation}
```

Rules:

1. Stage is `Hardening` when the handoff next skill is `child-spec-hardening`.
2. Stage is `Implementation` when the handoff next skill is `spec-change-delivery`.
3. `ChildSpecDesignation` comes from the Child Index `Child Spec` cell or handoff child spec title after removing file/date noise.
4. `thread/name/set` must be attempted before `turn/start`.
5. Evidence must record both `session_title` and `title_observed`.

## Canonical Examples and Fixtures

Pattern: **Hybrid**.

This compact embedded JSON object is the canonical S1 evidence field contract. S2 owns full validator fixtures; S1 delivery may add narrow adapter fixtures under `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-launcher-s1/**` only when needed to verify Launcher output shape.

```json
{
  "schema_version": "agent-delivery.session-launch.v2",
  "status": "launched",
  "execution_channel": "app_server",
  "adapter_id": "codex-app-server",
  "target_id": "ADV-CAS-S1",
  "target_role": "child",
  "initiating_project_cwd": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
  "target_workspace": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
  "project_cwd_source": "handoff_target_workspace_fallback",
  "parent_spec_abbrev_and_number": "ADV-CAS-1",
  "session_stage": "Implementation",
  "child_spec_designation": "ADV-CAS-S1 Launcher Visible-App Adapter",
  "session_title": "ADV-CAS-1: Implementation - ADV-CAS-S1 Launcher Visible-App Adapter",
  "prompt_sha256": "SHA256_HEX_OF_START_PROMPT",
  "session_visibility": {
    "class": "visible_codex_app_session",
    "visible_in_codex_app": true,
    "proof_status": "verified",
    "proof_method": "app_server_thread_list",
    "thread_id": "THREAD_ID",
    "thread_source_observed": "vscode",
    "source_kind_observed": "vscode",
    "cwd_observed": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
    "title_observed": "ADV-CAS-1: Implementation - ADV-CAS-S1 Launcher Visible-App Adapter",
    "rollout_path": "/Users/dh/.codex/sessions/YYYY/MM/DD/rollout-THREAD_ID.jsonl",
    "sidebar_or_default_list_observed": true
  },
  "app_server": {
    "listen": "stdio://",
    "thread_start_observed": true,
    "thread_name_set_observed": true,
    "turn_start_observed": true,
    "turn_completed_status": "completed",
    "thread_list_observed": true,
    "transcript_path": "_specs/agent-delivery-session-launches/RUN_ID/app-server-transcript.jsonl"
  }
}
```

The `prompt_sha256` placeholder above means the actual implementation must write a 64-character lowercase SHA-256 hex digest of `start-prompt.md`; the literal placeholder value is not valid runtime evidence. Any app-server transcript persisted by S1 must redact secrets and include JSON-RPC method order, request ids and relevant responses.

## Control Flow and Failure Cases

1. Queue/manual mode continues to write a start prompt and evidence without claiming app visibility.
2. Headless `codex exec` launch continues to work but reports only headless/traceable status.
3. Visible mode blocks before prompt persistence if the handoff contains secret-like content.
4. Visible mode blocks before launch if `initiating_project_cwd` is not absolute or cannot be resolved.
5. Visible mode records a process-level failure if `codex app-server` cannot start or exits before protocol initialization.
6. Visible mode records a protocol-level failure if any required JSON-RPC request fails.
7. Visible mode records a visibility-level failure if the completed thread cannot be found in the normal/default interactive list or `sourceKinds: ["vscode"]`.
8. Visible mode must terminate only the app-server process it started for the run.

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `S1-APP-SERVER-POSITIVE` | Prove visible app-server launch evidence shape. | Valid child handoff; explicit initiating cwd; app-server available. | Launcher exits `0` or records launched/verified status. | `launch-request.json`, `evidence.json`, `start-prompt.md`, app-server transcript, thread id/path. | No secret-like prompt/request content; source is not `exec`; cwd/title match. |
| `S1-HEADLESS-EXEC-DOWNGRADE` | Preserve old `codex exec` path without visible claim. | Existing codex adapter mode. | Process status may be `launched`, visibility class is non-visible. | Evidence records `execution_channel: headless_cli`. | `visible_codex_app_session` is forbidden. |
| `S1-MISSING-APP-SERVER` | Honest blocked state when app-server is unavailable. | PATH without usable `codex app-server` or failing help probe. | `blocked` or `failed`, not queued-as-visible. | Evidence records blocker. | No visible success claim. |
| `S1-WRONG-CWD` | Reject visibility when observed cwd differs from initiating cwd. | Synthetic app-server list response or controlled mock response. | Visibility proof fails. | Evidence includes mismatch. | Must not fall back to target workspace silently. |
| `S1-WRONG-TITLE` | Reject visibility when observed title differs. | Synthetic list/name response. | Visibility proof fails. | Evidence includes expected and observed titles. | Child id alone cannot substitute parent prefix. |
| `S1-EMPTY-THREAD` | Ensure empty `thread/start` is not enough. | App-server thread started but no turn materialized. | Visibility proof unverified/failed. | Evidence records missing turn/list materialization. | No visible success claim. |
| `S1-TURN-FAILED` | Prevent failed turns from passing visibility. | App-server transcript with failed/interrupted turn. | Launcher exits non-zero or evidence status failed. | Failure records turn status and transcript path. | A listed thread with failed turn is not a successful launch. |
| `S1-PROMPT-HASH-MISMATCH` | Tie evidence to the persisted handoff prompt. | Evidence fixture where hash differs from `start-prompt.md`. | Validation gate fails. | Failure records expected/actual hash. | Prompt text is not copied into logs if secret scan blocks it. |
| `S1-SECRET-REDACTION` | Preserve current secret screening. | Handoff or prompt fixture with secret-like content. | Launcher blocks before live start. | Redacted evidence only. | No secret-like literal appears in prompt, transcript or evidence. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `zsh` or `bash`
- Runtime: local Codex CLI plus file-based .NET tooling; implementation may use Node for JSON fixture assertions.
- Prohibited in S1: `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep` and any live `MD-E2E-5` execution.

Hardening command-contract rehearsal completed on 2026-05-10:

```sh
codex --help
codex app-server --help
rm -rf /tmp/codex-app-schema-adv-cas-s1 && codex app-server generate-ts --out /tmp/codex-app-schema-adv-cas-s1
rg -n "thread/start|thread/name/set|turn/start|thread/list|ThreadStartParams|TurnStartParams|ThreadListParams|ThreadSourceKind" /tmp/codex-app-schema-adv-cas-s1
```

Required delivery checks for S1 implementation:

```sh
git diff --check
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help
codex app-server --help
codex app-server generate-ts --out /tmp/codex-app-schema-adv-cas-s1
```

S1 delivery must add or identify targeted checks for:

1. app-server command/protocol method order,
2. evidence schema fields,
3. headless exec downgrade,
4. wrong cwd/title/source negative handling,
5. secret redaction before prompt/evidence persistence.

Readiness gate:

```sh
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-10\ Agent\ Delivery\ Visible\ Codex\ App\ Sessions\ Orchestration\ Pack.md \
  --child ADV-CAS-S1 \
  --handoff /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/adv-cas-s1-session-handoff.md
```

## Definition of Ready for Implementation

S1 is ready when:

1. This child spec, the Child Index row and the handoff agree on `IMPLEMENTATION READY`.
2. The implementation write-set is concrete and excludes downstream validator, live runner and closeout archive implementation files.
3. Parent conformance has no `missing_from_child` or `contradicts_parent` rows.
4. The app-server command contract has been rehearsed.
5. The canonical JSON example parses.
6. `ValidateChildReadiness.cs` passes for `ADV-CAS-S1`.
7. `git diff --check` passes.

## Definition of Done / Closeout Evidence

S1 implementation can be accepted only when closeout records:

1. Changed files within the allowed write-set.
2. Exact CLI/API visible adapter surface delivered.
3. Evidence from positive visible-app launch or an explicit implementation-time blocker if app-server is unavailable.
4. Evidence that old `codex exec` behavior remains headless/traceable, not visible.
5. S1 cases covered by targeted verification commands.
6. `MD-E2E-5` not run in S1.
7. OpenSpec change archived or explicitly not used.
8. Child Index row and handoff moved from implementation-ready to accepted only after evidence exists.

## Dependencies and Write-Set

Hardening lane write-set used by this session:

- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S1 Launcher Visible App Adapter.md`
- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`
- `_specs/child-session-handoffs/adv-cas-s1-session-handoff.md`

Future S1 implementation allowed write-set:

- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S1 Launcher Visible App Adapter.md`
- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`
- `_specs/child-session-handoffs/adv-cas-s1-session-handoff.md`
- `_specs/agent-delivery-session-launches/**`
- `openspec/changes/agent-delivery-visible-app-launcher-adapter/**`
- `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- `skills-repo/tools/AgentDeliveryCodexAppServerClient.cs`
- `docs/doc-workflow.md`
- `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-launcher-s1/**`
- `tests/docworkflow-agent-delivery/e2e/validators/visible-app-launcher-s1.js`

Shared / read-only for S1 implementation:

- `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`
- `_specs/codex-app-server-spikes/20260509T171506Z/**`
- `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`
- `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`
- `skills-repo/skills/spec-closeout/SKILL.md`
- `tests/docworkflow-agent-delivery/README.md`
- `tests/docworkflow-agent-delivery/testcases/md-e2e-5-visible-codex-app-sessions.md`
- `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/**`

Dependencies:

1. Parent identifier `ADV-CAS-1` is already assigned in the orchestration pack.
2. App-server spike evidence exists and remains read-only.
3. S2/S3/S5 depend on S1 evidence field names; after S1 implementation changes them, those children must re-sync before delivery.

## Closeout Sync Targets

After S1 delivery, synchronize:

1. This child spec readiness/history and closeout evidence.
2. `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md` Child Index row for `ADV-CAS-S1`.
3. `_specs/child-session-handoffs/adv-cas-s1-session-handoff.md`.
4. `docs/doc-workflow.md` if S1 changed workflow wording.
5. OpenSpec archive/evidence path if the implementation uses `openspec/changes/agent-delivery-visible-app-launcher-adapter/**`.

## Child Session Handoff

Persisted handoff for the next implementation run:

- `_specs/child-session-handoffs/adv-cas-s1-session-handoff.md`

Launch/queue evidence status for this hardening pass:

- `manual_start_required`: no automated Launcher queue was created during hardening because the current Launcher is the runtime target of S1 and still has headless `codex exec` semantics. Starting implementation should use a fresh manual or future visible-app session from the persisted handoff.

## Implementation Closeout Evidence

S1 delivery implemented the visible app-server adapter in `skills-repo/tools/AgentDeliverySessionLauncher.cs` and retained S1-local runtime smoke evidence at:

- `_specs/agent-delivery-session-launches/20260510T081130Z-adv-cas-s1/evidence.json`
- `_specs/agent-delivery-session-launches/20260510T081130Z-adv-cas-s1/app-server-transcript.jsonl`
- `_specs/agent-delivery-session-launches/adv-cas-s1-visible-smoke-handoff.md`

The retained smoke is intentionally a launcher-adapter smoke, not the actual child implementation session. It proves the delivered adapter can start an app-server-backed interactive-source thread through `initialize`, `thread/start`, `thread/name/set`, `turn/start` and `thread/list` without using the real S1 handoff to spawn duplicate implementation work.

Delivered S1 artifacts:

1. `--adapter codex-app-server` visible adapter mode.
2. `--adapter codex-exec` headless downgrade evidence.
3. `initiating_project_cwd`, `target_workspace`, `project_cwd_source`, title components and prompt SHA-256 evidence fields.
4. App-server transcript retention with prompt text truncation in transcript entries.
5. S1-local fixture validator covering app-server positive, headless downgrade, empty thread, wrong title, wrong cwd, failed turn, prompt hash mismatch, app-server unavailable and secret redaction cases.

Verification status:

| Command / Check | Status | Evidence |
|---|---|---|
| `cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- --index /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-10\ Agent\ Delivery\ Visible\ Codex\ App\ Sessions\ Orchestration\ Pack.md --child ADV-CAS-S1 --handoff /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/adv-cas-s1-session-handoff.md` | ran-target | Child readiness validation passed. |
| `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help` | ran-target | Help lists `--adapter codex-app-server`, initiating cwd and app-server timeout flags. |
| `codex app-server --help` | ran-target | App-server CLI and `--listen stdio://` are available. |
| `codex app-server generate-ts --out /tmp/codex-app-schema-adv-cas-s1` | ran-target | Protocol TypeScript schema generated. |
| canonical S1 JSON example parse | ran-target | Embedded canonical JSON block parsed successfully. |
| `openspec validate agent-delivery-visible-app-launcher-adapter --strict` | ran-target | Change validates with S1 delta. |
| `node tests/docworkflow-agent-delivery/e2e/validators/visible-app-launcher-s1.js tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-launcher-s1` | ran-target | All 9 S1 launcher fixture cases passed. |
| S1-local visible app-server smoke launch | ran-target | `_specs/agent-delivery-session-launches/20260510T081130Z-adv-cas-s1/evidence.json` reports `visible_codex_app_session`; `MD-E2E-5` was not run. |
| `git diff --check` | ran-target | Patch whitespace clean. |

OpenSpec status: `openspec/changes/agent-delivery-visible-app-launcher-adapter/` is retained as an active implementation ledger. It is not archived in S1 because canonical OpenSpec spec mutation is outside the S1 allowed write-set; archive is a post-acceptance closeout step.

## Content Quality Review

| Review Dimension | Result |
|---|---|
| Correctness/domain fit | Pass. The spec follows the proven app-server spike and parent terminology. |
| Scope discipline | Pass. Validator, live runner, control boundary and archive behavior remain in downstream children. |
| Completeness | Pass. CLI/API surface, evidence schema, cases, commands, write-set, DoR/DoD and handoff are explicit. |
| Consistency | Pass. Review Control Surface, detailed contract, Child Index and handoff use the same verdict and write-set. |
| Verifiability | Pass. Includes rehearsed app-server command contract, parseable JSON example and child-readiness validation. |
| Operational fit | Pass. Keeps per-run app-server lifecycle and records manual-start status instead of using headless launch evidence as visible proof. |

No blocking `[MISSING ...]`, `[DECISION ...]` or `[REVIEW ...]` markers remain.

## Mini-Retro

- Was wurde entschieden? S1 is the schema-freezing Launcher adapter child. The implementation-ready default is per-run `codex app-server --listen stdio://` with normal/default or `vscode` thread-list proof after a completed/materialized turn.
- Was wurde geaendert? Created this hardened child spec and synchronized the Child Index and handoff for a future S1 `spec-change-delivery` session.
- Was bleibt offen? UI/sidebar screenshot proof and shared app-server sockets remain non-blocking follow-ups; S2/S3/S5 still need separate hardening/delivery.
- Welche Evidenz/Verification fehlt? Runtime visible-app launch evidence is intentionally absent until S1 implementation. `MD-E2E-5` was not run.
- Welche Skill-/Workflow-Reibung ist aufgefallen? Current Launcher queue evidence is still `codex exec`-centric, so hardening records `manual_start_required` instead of creating misleading headless launch evidence.
- Session-/Kontextzustand: Handoff boundary reached. Continue with a fresh `spec-change-delivery` session for S1.

## History

| Date | Actor | Change |
|---|---|---|
| 2026-05-10 | Codex | Hardened `ADV-CAS-S1` into an implementation-ready child spec, rehearsed app-server help/schema commands, synchronized Child Index/handoff, and preserved the no-runtime/no-`MD-E2E-5` boundary. |
| 2026-05-10 | Codex | Implemented the S1 launcher app-server adapter, added S1-local validator fixtures, retained visible app-server smoke evidence, and kept `MD-E2E-5` out of scope. |
