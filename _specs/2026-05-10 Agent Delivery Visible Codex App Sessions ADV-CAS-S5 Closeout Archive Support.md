**Date:** 2026-05-10
**Status:** 🟢 Accepted
**Scope:** Delivered and accepted `ADV-CAS-S5 Closeout Archive Support`. Adds closeout archive tooling, S5 fixtures, S2 validator bridge and workflow/docs sync; no live `thread/archive` call and no live `MD-E2E-5` execution.

---

## Session Briefing

- Modus/Skill: `child-spec-hardening`.
- Source of Truth: `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; accepted S2 validator spec `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S2 Visible Evidence Validator.md`; `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`; `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/**`; `skills-repo/skills/spec-closeout/SKILL.md`; `docs/doc-workflow.md`; `skills-repo/tools/AgentDeliverySessionLauncher.cs`; generated local app-server protocol references under `/tmp/codex-app-schema-adv-cas-s5/`.
- Ziel: Harden child `ADV-CAS-S5` into an implementation-ready closeout/archive support spec that consumes the accepted S2 visible evidence validator contract.
- Nicht-Ziele: No runtime code edits; no Launcher implementation; no MD-E2E-5 runner implementation; no live `MD-E2E-5` run; no live app-server archive call; no direct SQLite mutation; no S3 runner edits.
- In Scope: Review Control Surface, archive contract for `thread/archive`, closeout archive summary fields, `ArchiveVisibleCodexAppSession.cs` tool contract, source-controlled S5 fixture family, S2 validator coupling, no-thread/headless statuses, negative unarchived `READY` case, verification lifecycle, parent conformance, Child Index sync, S5 handoff sync, and final readiness verdict.
- Erwarteter Output: this child spec, the S5 Child Index row, and `_specs/child-session-handoffs/adv-cas-s5-session-handoff.md`.
- Verification/Review: parse embedded JSON examples; rehearse app-server archive/list protocol schema; `git diff --check`; `ValidateChildReadiness.cs` for `ADV-CAS-S5`.
- Offene Entscheidungen: none blocking for implementation. The S5 implementation must not call live `thread/archive` unless the delivery session explicitly opts into live archive mode.

## Review Control Surface

- Spec-Variante: Contract-heavy Parent/Child closeout child spec.
- Goldstandard Status: accepted child spec after S5 delivery and closeout.
- Ziel: Define how `spec-closeout` archives visible Codex-App sessions opened for a child run, records explicit archive statuses for headless/no-thread evidence, and blocks final `READY` when any visible thread remains unarchived.
- In Scope: `spec-closeout` closeout gate behavior; app-server `thread/archive` request/response contract; post-archive proof using `thread/list`; closeout archive summary fields; status enums for visible, headless, queued, manual, no-thread and failure cases; negative false-positive case where a child closeout claims `READY` while visible sessions remain unarchived.
- Out of Scope: Launcher app-server adapter implementation; S2 visible evidence validator implementation; MD-E2E-5 runner implementation; live Codex-App session creation; direct SQLite mutation; broad project docs sync beyond closeout wording; archiving historical evidence created before this parent unless explicitly linked to the target child run.
- Key Test/Harness Cases: visible archive positive; already archived positive; headless/not-app-visible evidence gets `not_app_visible_not_archived`; queued/manual without a thread gets `no_thread_created`; visible thread archive failure returns `NOT_READY`; post-archive proof failure returns `NOT_READY`; mixed child run with archived visible plus explicit non-visible records returns `READY`; negative unarchived `READY` case fails with S2-compatible `unarchived_visible_session`; manual-visible without thread proof fails.
- Key Verification Commands: `codex app-server --help`; `codex app-server generate-ts --out /tmp/codex-app-schema-adv-cas-s5`; inspect generated `ThreadArchiveParams`, `ThreadArchiveResponse`, `ThreadListParams`; parse embedded JSON examples; future S5 fixture suite through `ArchiveVisibleCodexAppSession.cs`; S2 validator closeout coupling through `ValidateVisibleCodexAppSessionEvidence.cs`; `git diff --check`; `ValidateChildReadiness.cs` for `ADV-CAS-S5`. Do not run `MD-E2E-5` for S5 hardening.
- Open Decisions / Blockers: none for implementation readiness.
- Readiness Status: ACCEPTED for exactly `ADV-CAS-S5`.

## Goal

`ADV-CAS-S5` makes child closeout honest for visible Codex-App sessions. A child closeout may only report final `READY` when every session evidence record for the same parent and child/spec id has an explicit archive outcome:

1. visible app-server/manual-visible threads are archived or proven already archived,
2. headless `codex exec` records are explicitly marked not app-visible and not archived,
3. queued/manual starts without a thread are explicitly marked no-thread,
4. every archive/proof failure keeps closeout `NOT_READY` unless the user explicitly accepts a retained visible-session note.

## In Scope

- Extend `spec-closeout` behavior so child closeout finds launch/session evidence for the target child and evaluates archive state before final `READY`.
- Define a closeout companion tool contract for app-server `thread/archive`.
- Define S5 closeout archive summary fields and status values.
- Define negative and fallback cases, including unarchived visible thread evidence that must fail even when implementation verification passed.
- Define a verification lifecycle that separates delivery gates, pre-archive closeout, and post-archive/current replay.
- Sync workflow wording so `launched` or headless `exec` evidence is never treated as app-visible archive success.

## Out of Scope

- Implementing S1 visible app-server launch support.
- Implementing S2 visible evidence validation.
- Editing `AgentDeliverySessionLauncher.cs`; S5 consumes its launch evidence and may not change Launcher behavior.
- Running `thread/archive` against real user sessions in this hardening run.
- Running `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh` or any `MD-E2E-5` live workflow.
- Updating the orchestration pack, handoffs, tools, tests, docs, runtime code or OpenSpec artifacts in this hardening lane.

## Parent/Master Coverage

| Parent Requirement | S5 Coverage | Status |
|---|---|---|
| `ADV-PR9` | Primary owner. Child closeout archives visible app-server sessions through `thread/archive` or records explicit no-thread/not-app-visible states. | covered_by_implementation_ready_contract |
| `ADV-PR5` | Consumes S1/S2 `agent-delivery.session-launch.v2` fields for `execution_channel`, `session_visibility`, thread identity, title, cwd, prompt/hash, transcripts, closeout summary linkage and evidence paths. | covered_by_accepted_S2_contract |
| `ADV-PR7` | Supplies archive/no-thread evidence required for final `MD-E2E-5` pass. | supports_later_S3 |
| `ADV-PR10` | Prevents workflow docs/skills from treating `status: launched` from `codex exec` as visible-app success and preserves S2 false-positive failure classes. | covered_by_implementation_ready_contract |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `ADV-PR9` | `spec-closeout` must archive every visible thread for the child run before final `READY`. | preserves | Implement S5 via `spec-closeout` plus `ArchiveVisibleCodexAppSession.cs`; no direct SQLite mutation. |
| `ADV-PR5` | S5 consumes S1/S2 `agent-delivery.session-launch.v2` field names and extends closeout summary validation without weakening the S2 validator. | preserves | Preserve `ValidateVisibleCodexAppSessionEvidence.cs` CLI behavior and failure classes. |
| `ADV-PR7` | S5 does not run or implement `MD-E2E-5`; it provides the archive condition that S3 must consume. | narrows_with_rationale | S3 remains the live workflow integration owner. |
| `ADV-PR10` | S5 treats headless `exec` as `not_app_visible_not_archived`, never as archived visible evidence. | preserves | Add closeout docs/skill wording during S5 delivery. |

Conformance verdict: no parent contradiction found. S5 delivery and closeout are accepted after validator sync, fixture replay and Child Index/handoff promotion.

## Decision Freeze Pack

Frozen for S5:

1. Closeout owner is `spec-closeout`.
2. Runtime archive mechanism is app-server `thread/archive`, not direct SQLite mutation.
3. S5 uses a closeout companion tool contract, `skills-repo/tools/ArchiveVisibleCodexAppSession.cs`, rather than changing `AgentDeliverySessionLauncher.cs`.
4. `thread/archive` accepts `{ "threadId": "<id>" }` and returns an empty object according to generated app-server protocol types.
5. Post-archive proof must use app-server `thread/list` with `archived: false` absence and/or `archived: true` presence for the same thread id.
6. Final child closeout `READY` is blocked by any visible thread with `archive_status` other than `archived`, `already_archived`, or `retained_session_accepted`.
7. Headless `codex exec` evidence is not archived by S5 and must receive `archive_status: "not_app_visible_not_archived"`.
8. Queued/manual evidence without a real thread id must receive `archive_status: "no_thread_created"`.
9. `retained_session_accepted` is allowed only with explicit user acceptance captured in the closeout archive summary.
10. S5 preserves the accepted S2 visible validator entry point `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`, fixture root `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/`, and failure class `unarchived_visible_session` for closeout-required visible evidence.
11. S5 source-controlled archive fixtures live under `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/` and must not be mixed into the S2 visible-evidence fixture root.

## Normative Contract

### Evidence Discovery

For child closeout, S5 must discover all launch/session evidence records that match the same:

1. parent spec path or stable parent id,
2. target child/spec id,
3. child spec path when present,
4. handoff path when present.

Default discovery roots:

1. `_specs/agent-delivery-session-launches/**/evidence.json`
2. `_specs/agent-delivery-session-launches/**/launch-request.json`
3. any child-local launch/evidence directory named by the Child Index or Child Session Handoff
4. MD-E2E-5 run evidence roots when S3 later owns a live suite run

S5 must not archive sessions for sibling children, parent orchestration runs, unrelated manual sessions, or historical spikes unless their evidence explicitly matches the target parent and child/spec id.

### Consumed Launch Evidence Fields

The S5 archive evaluator consumes the accepted S1/S2 `agent-delivery.session-launch.v2` fields below. These names are no longer provisional for S5 implementation:

| Field | Required For | Meaning |
|---|---|---|
| `schema_version` | all records | Must be `agent-delivery.session-launch.v2`. |
| `parent` or `parent_spec` | all records | Parent spec identity used for child-run grouping; retain compatibility with existing launch evidence when both are not present. |
| `target_id` | all records | Stable child id, for example `ADV-CAS-S5` or `RSW-C1`. |
| `target_spec` | all child records | Child spec path or stable child spec reference. |
| `handoff_path` | all handoff-backed records | Handoff that created or queued the session. |
| `execution_channel` | all records | `headless_cli`, `app_server`, `manual_queue`, or `manual_visible`. |
| `status` | all records | Launch/queue process status, not visibility proof by itself. |
| `session_visibility.class` | all records | `visible_codex_app_session`, `manual_visible_start`, `headless_cli_session`, `queued_manual_start`, or `traceable_but_not_visible`. |
| `session_visibility.thread_id` | visible/manual-visible records | App-server or manually observed Codex thread id. |
| `session_visibility.visible_in_codex_app` | visible/manual-visible records | True only when app visibility is proven. |
| `session_visibility.proof_status` | visible/manual-visible records | Must be `verified` for app-visible archive actions. |
| `session_visibility.proof_method` | visible/manual-visible records | For S1/S2 app-server evidence, expected `app_server_thread_list`; manual visible remains stricter because a real thread id is still required. |
| `session_visibility.thread_source_observed` | visible/headless records | Observed source such as `vscode` or `exec`. |
| `session_visibility.source_kind_observed` | visible/headless records | S2 also rejects `exec` here. |
| `session_visibility.cwd_observed` | visible records | Observed cwd, used to distinguish target workspace from initiating project. |
| `session_title` or `session_visibility.title_observed` | visible records | Deterministic Agent Delivery title. |
| `prompt_sha256` | launched records | Prompt linkage for forensic grouping. |
| `evidence_paths.prompt` | queued/launched records | Prompt path retained with the launch record. |
| `evidence_paths.app_server_transcript` or `app_server.transcript_path` | app-server records | Transcript path used for S2 proof and S5 archive transcript redaction checks. |
| `app_server.thread_start_observed` | app-server records | S2 positive app-server proof flag. |
| `app_server.thread_name_set_observed` | app-server records | S2 positive app-server proof flag. |
| `app_server.turn_start_observed` | app-server records | S2 positive app-server proof flag. |
| `app_server.turn_completed_status` | app-server records | Expected `completed` for S2 positive app-server evidence. |
| `app_server.thread_list_observed` | app-server records | Required S2 app-visible list proof. |

### S2 Validator Coupling

S5 implementation must keep the accepted S2 validator command compatible:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- \
  --fixture /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence
```

Required S2 contract points S5 must not break:

1. `ValidateVisibleCodexAppSessionEvidence.cs` remains the visible evidence validator.
2. The S2 fixture manifest remains under `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence/fixture-manifest.json`.
3. The S2 closeout-required negative case id is `S2-VIS-011-unarchived-visible-closeout`.
4. The S2 closeout failure class is `unarchived_visible_session`.
5. The S2 validator option `--require-closeout-archived` keeps exiting `1` for a visible record whose closeout proof says `archived: false` or `visible_session_archived: false`.

S5 may extend the S2 validator in its implementation write-set so `--closeout <summary>` also understands the S5 summary schema below. That extension must preserve all accepted S2 fixture results and must map S5 unarchived visible records to the same `unarchived_visible_session` failure class.

### Archive Status Values

S5 emits exactly one `archive_status` per discovered session evidence record:

| Status | Applies To | Final READY Impact |
|---|---|---|
| `archived` | A visible/manual-visible thread was archived by this closeout run and post-archive proof passed. | allows READY |
| `already_archived` | The thread was already archived before this closeout run and proof passed. | allows READY |
| `not_app_visible_not_archived` | Headless `codex exec` or traceable non-visible evidence. | allows READY when explicit |
| `no_thread_created` | Queued/manual start with no real thread id. | allows READY when explicit |
| `manual_visible_missing_thread` | Manual-visible claim lacks a thread id or proof source. | blocks READY |
| `archive_failed` | `thread/archive` failed or timed out. | blocks READY |
| `proof_failed` | Archive call returned but post-archive proof failed. | blocks READY |
| `retained_session_accepted` | Visible session intentionally retained by explicit user acceptance. | allows READY only with `retention_accepted_by` and `retention_reason` |

### App-Server Archive API

S5 delivery must use the app-server protocol, not SQLite writes:

```json
{
  "method": "thread/archive",
  "params": {
    "threadId": "019e0dbc-5439-7df3-8849-847f29a93ce0"
  }
}
```

Expected response:

```json
{}
```

Expected notification when observed:

```json
{
  "method": "thread/archived",
  "params": {
    "threadId": "019e0dbc-5439-7df3-8849-847f29a93ce0"
  }
}
```

Post-archive proof must perform at least one of:

1. `thread/list` with `archived: false` and the initiating cwd/title filters no longer returns the thread id,
2. `thread/list` with `archived: true` returns the same thread id with `archived: true`.

The generated `ThreadListParams` supports `archived?: boolean | null`; omitted or false returns non-archived threads.

### Closeout Archive Summary

S5 delivery must write or require a closeout archive summary under a stable workspace evidence path. The summary is the source of truth for `spec-closeout` final `READY` on the archive dimension.

Parseable summary shape:

```json
{
  "schema_id": "agent-delivery.visible-session-closeout-archive.v1",
  "parent": "_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md",
  "target_id": "ADV-CAS-S5",
  "target_spec": "_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S5 Closeout Archive Support.md",
  "overall_archive_status": "READY",
  "created_at": "2026-05-10T00:00:00Z",
  "session_records": [
    {
      "evidence_path": "_specs/agent-delivery-session-launches/20260510T000000Z-adv-cas-s5/evidence.json",
      "execution_channel": "app_server",
      "visibility_class": "visible_codex_app_session",
      "thread_id": "019e0dbc-5439-7df3-8849-847f29a93ce0",
      "session_title": "ADV-CAS-1: Implementation - S5 Closeout Archive Support",
      "archive_status": "archived",
      "archive_method": "app_server_thread_archive",
      "archived_at": "2026-05-10T00:01:00Z",
      "post_archive_proof": {
        "method": "thread/list",
        "archived_false_absent": true,
        "archived_true_present": true
      }
    }
  ]
}
```

Compatibility rule for the accepted S2 validator:

1. For a single visible evidence record checked with `ValidateVisibleCodexAppSessionEvidence.cs --require-closeout-archived`, S5 summary validation must expose or derive `archived: true` or `visible_session_archived: true` only when the matching visible session record has `archive_status: "archived"` or `archive_status: "already_archived"`.
2. A visible session record with `archive_status: "unarchived"`, missing `archive_status`, `archive_failed`, `proof_failed`, or `manual_visible_missing_thread` must fail as `unarchived_visible_session` when S2 closeout coupling is required.
3. `retained_session_accepted` may satisfy final `spec-closeout` only when explicit user retention fields are present, but it must not be reported to S2's visible-evidence validator as ordinary `archived: true`.

### `ArchiveVisibleCodexAppSession.cs` Tool Expectations

S5 implementation should add `skills-repo/tools/ArchiveVisibleCodexAppSession.cs` as a closeout companion tool with these modes:

| Mode / Option | Required Behavior |
|---|---|
| `--fixture <dir>` | Validate every S5 archive fixture case from `fixture-manifest.json` and return `0` only when each expected pass/fail outcome and failure class matches. |
| `--validate-summary <summary.json>` | Validate one closeout archive summary without live app-server calls. |
| `--evidence <evidence.json> --summary-out <path>` | Build or update an archive summary from one or more persisted evidence records. |
| `--mode validate` | Never call live `thread/archive`; only replay fixtures, summaries and mock transcripts. |
| `--mode live --app-server <stdio-or-socket>` | Opt-in only; may call `thread/archive` and then `thread/list` proof for real visible threads. |
| `--retained-session-accepted-by <id> --retention-reason <text>` | Allow `retained_session_accepted` only when the user explicitly accepted retention. |

Exit code contract:

| Condition | Exit Code | Output Contract |
|---|---:|---|
| all fixture or summary cases match expected outcomes | `0` | Print one line per case and final `RESULT: PASS (<n> cases)`. |
| one or more semantic mismatches | `1` | Print mismatched case id, failure class, thread id when available and final `RESULT: FAIL`. |
| invalid CLI usage, missing manifest, invalid JSON, unreadable files, or unsupported schema | `2` | Print setup errors to stderr. |

Required failure classes for S5 fixtures:

| Failure Class | Required Trigger |
|---|---|
| `unarchived_visible_session` | Visible record remains unarchived or summary claims `READY` while visible archive proof is absent. |
| `manual_visible_missing_thread` | Manual-visible evidence lacks a real thread id or accepted proof source. |
| `archive_failed` | App-server archive response is an error, timeout, or missing success response. |
| `proof_failed` | Archive response exists but post-archive `thread/list` proof is absent or contradictory. |
| `secret_leak` | Transcript or summary includes secrets, bearer tokens, raw environment dumps, or prompt body content beyond hashes/paths. |

### Redaction And Safety

Archive summaries and protocol transcripts must not include secrets, bearer tokens, raw environment dumps, full prompts with secrets, or unrelated user thread contents. Required retained content is limited to session identity, target grouping fields, app-server method names, non-secret params, response status, thread id, cwd/title, timestamps, hashes, and evidence paths.

## Canonical Examples and Fixtures

Pattern: hybrid.

- Embedded examples in this spec are compact, parseable examples for the intended summary shape.
- Full fixtures must be created during S5 implementation under `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**`.
- Fixture manifests must name each case id, input launch evidence files, optional S2 visible evidence fixture reference, mock app-server transcript, expected `archive_status` records, expected final closeout verdict, expected failure class for failing cases, and whether app-server calls are replayed through a mock transcript or a real opted-in app-server process.
- Fixtures are in scope for S5 implementation, not this hardening run. They are source-controlled because they must live under the implementation write-set and must be executed by the S5 delivery gate.

Required source-controlled fixture family:

| Fixture Path | Case Coverage |
|---|---|
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/fixture-manifest.json` | manifest listing every S5 case, expected outcome, expected status values and expected failure classes |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/visible-archive-positive/` | visible thread archived, post-archive proof passes, final `READY` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/already-archived/` | already archived proof passes without requiring a second archive call, final `READY` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/headless-not-app-visible/` | headless/traceable evidence gets `not_app_visible_not_archived`, final archive dimension `READY` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/queued-no-thread/` | queued/manual no-thread gets `no_thread_created`, final archive dimension `READY` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/archive-failure/` | archive API failure blocks `READY` with `archive_failed` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/post-archive-proof-failure/` | archive call without post-archive proof blocks `READY` with `proof_failed` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/mixed-child-run/` | visible archived, headless not-visible and queued no-thread records combine to final `READY` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/unarchived-visible-negative/` | closeout summary claiming `READY` with unarchived visible thread fails as `unarchived_visible_session` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/manual-visible-missing-thread/` | manual-visible claim without thread blocks `READY` with `manual_visible_missing_thread` |

Minimum fixture files per case:

```text
evidence.json
expected-summary.json
mock-app-server-transcript.jsonl
```

Cases that do not call app-server, such as `headless-not-app-visible` and `queued-no-thread`, may omit `mock-app-server-transcript.jsonl` only when the manifest explicitly sets `"expectsArchiveCall": false`.

## Control Flow and Failure Cases

S5 closeout flow:

1. Load target child closeout context from spec path, Child Index row and/or handoff.
2. Discover all matching launch/session evidence records for the same parent and target child/spec id.
3. Classify each evidence record by `execution_channel` and `session_visibility.class`.
4. For visible/manual-visible records with a real `thread_id`, check whether already archived.
5. If not archived, call app-server `thread/archive`.
6. Run post-archive proof.
7. Emit one `archive_status` per evidence record.
8. Compute `overall_archive_status`.
9. Allow `spec-closeout` final `READY` only when `overall_archive_status == "READY"` and all other closeout gates are green.

Required failure behavior:

1. No matching evidence records: closeout may continue only if the child had no launch/session evidence requirement and records `overall_archive_status: "READY_NO_SESSION_EVIDENCE"` with a rationale. MD-E2E-5 children must not use this status.
2. Visible record missing `thread_id`: `manual_visible_missing_thread`, final `NOT_READY`.
3. Visible record with archive call failure: `archive_failed`, final `NOT_READY`.
4. Visible record with archive call success but no post-archive proof: `proof_failed`, final `NOT_READY`.
5. Headless `exec` record: `not_app_visible_not_archived`, final can be `READY`.
6. Queued/manual no-thread record: `no_thread_created`, final can be `READY`.
7. Summary says `READY` while any visible record is unarchived: validator must fail the summary.

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `S5-ARCH-001-visible-archive-positive` | Prove visible app thread is archived. | `visible-archive-positive/` with visible evidence, prompt/transcript linkage and mock app-server archive transcript. | pass / `READY` | closeout archive summary with `archive_status: archived`. | Transcript contains no prompt body or secrets. |
| `S5-ARCH-002-already-archived` | Avoid failing idempotent closeout. | `already-archived/` with visible evidence plus archived-list proof. | pass / `READY` | `archive_status: already_archived`. | No second archive call required. |
| `S5-ARCH-003-headless-not-app-visible` | Preserve honest headless status. | `headless-not-app-visible/` using S2-style headless evidence with `execution_channel: headless_cli` or `source: exec`. | pass / `READY` for archive dimension | `archive_status: not_app_visible_not_archived`. | Must not set `visible_codex_app_session`; compatible with S2 `headless_cli_not_visible`. |
| `S5-ARCH-004-queued-no-thread` | Handle queued/manual starts without real sessions. | `queued-no-thread/` with queued/manual evidence without `thread_id`. | pass / `READY` for archive dimension | `archive_status: no_thread_created`. | Must not invent thread ids; compatible with S2 `queued_not_visible`. |
| `S5-ARCH-005-archive-failure` | Ensure failed archive blocks closeout. | `archive-failure/` with app-server error response or timeout. | fail / `NOT_READY` | `archive_status: archive_failed`. | Error text redacted. |
| `S5-ARCH-006-post-archive-proof-failure` | Ensure archive proof is mandatory. | `post-archive-proof-failure/` with archive response without archived-list proof. | fail / `NOT_READY` | `archive_status: proof_failed`. | Empty `{}` response alone is insufficient. |
| `S5-ARCH-007-mixed-child-run` | Prove combined status computation. | `mixed-child-run/` with one archived visible record, one headless record, one queued no-thread record. | pass / `READY` | three explicit session records. | No hidden skipped case counts as passed. |
| `S5-ARCH-008-unarchived-visible-negative` | Block false closeout success. | `unarchived-visible-negative/` closeout summary says `READY` while visible thread is unarchived. | fail / `NOT_READY` | validator finding names the unarchived thread with `unarchived_visible_session`. | Required negative unarchived READY case; aligns with S2 `S2-VIS-011`. |
| `S5-ARCH-009-manual-visible-missing-thread` | Reject unverifiable manual visible claim. | `manual-visible-missing-thread/` manual-visible evidence without `thread_id`. | fail / `NOT_READY` | `archive_status: manual_visible_missing_thread`. | Human text alone is not enough. |
| `S5-ARCH-010-retained-session-accepted` | Allow explicit user-approved retained visible thread. | Optional `retained-session-accepted/` visible record plus explicit retention acceptance. | pass / `READY` only with retained note | `archive_status: retained_session_accepted`. | Missing `retention_accepted_by` or reason fails. |

## Verification Commands

Do not run `MD-E2E-5` during S5 hardening or S5 implementation. `MD-E2E-5` belongs to S3 after S1/S2/S4/S5 contracts exist.

Command contract for S5 hardening completion:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
codex app-server --help
codex app-server generate-ts --out /tmp/codex-app-schema-adv-cas-s5
test -f /tmp/codex-app-schema-adv-cas-s5/v2/ThreadArchiveParams.ts
test -f /tmp/codex-app-schema-adv-cas-s5/v2/ThreadArchiveResponse.ts
test -f /tmp/codex-app-schema-adv-cas-s5/v2/ThreadListParams.ts
git diff --check
```

Future S5 delivery gates after implementation:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout --mode validate
dotnet run skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout
dotnet run skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence
rg -n "thread/archive|archive_status|not_app_visible_not_archived|no_thread_created|visible_codex_app_session" docs/doc-workflow.md skills-repo/skills/spec-closeout/SKILL.md skills-repo/tools tests/docworkflow-agent-delivery
git diff --check
```

Success criteria:

1. All S5 fixture cases match expected pass/fail outcomes.
2. `s5-unarchived-ready-negative` fails with a finding naming the unarchived thread.
3. Headless and queued/no-thread records are explicit and do not require app-server archive calls.
4. App-server archive transcript records method, params, response status and post-archive proof.
5. No command relies on direct SQLite mutation.
6. `git diff --check` passes.

Current hardening verification result:

- `MD-E2E-5`: not run by design.
- `thread/archive`: no live archive call run by design.
- Embedded JSON examples: passed, 4 JSON blocks parsed.
- App-server schema rehearsal: passed; `ThreadArchiveParams`, `ThreadArchiveResponse`, and `ThreadListParams` generated under `/tmp/codex-app-schema-adv-cas-s5/v2/`.
- S2 visible evidence regression: passed, `ValidateVisibleCodexAppSessionEvidence.cs --fixture` reported `RESULT: PASS (11 cases)`.
- `ValidateChildReadiness.cs`: passed for `ADV-CAS-S5`.

Current delivery verification result:

- S5 archive fixture suite: passed, `ArchiveVisibleCodexAppSession.cs --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout --mode validate` reported `RESULT: PASS (10 cases)`.
- S5/S2 closeout bridge: passed, `ValidateVisibleCodexAppSessionEvidence.cs --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout` reported `RESULT: PASS (10 cases)`.
- S2 visible evidence regression: passed, `ValidateVisibleCodexAppSessionEvidence.cs --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence` reported `RESULT: PASS (11 cases)`.
- Source wording check: passed for `thread/archive`, `archive_status`, `not_app_visible_not_archived`, `no_thread_created`, and `visible_codex_app_session`.
- `ValidateChildReadiness.cs`: passed for `ADV-CAS-S5` after delivery sync.
- `git diff --check`: passed.
- `MD-E2E-5`: not run by design; belongs to S3.
- Live `thread/archive`: not run by design; live archive mode remains opt-in.

Current closeout verification result:

- `codex app-server --help`: passed.
- `codex app-server generate-ts --out /tmp/codex-app-schema-adv-cas-s5`: passed.
- Generated protocol file presence checks for `ThreadArchiveParams.ts`, `ThreadArchiveResponse.ts`, and `ThreadListParams.ts`: passed.
- S5 archive fixture suite: passed, `RESULT: PASS (10 cases)`.
- S5/S2 closeout bridge: passed, `RESULT: PASS (10 cases)`.
- S2 visible evidence regression: passed, `RESULT: PASS (11 cases)`.
- Source wording check: passed for `thread/archive`, `archive_status`, `not_app_visible_not_archived`, `no_thread_created`, and `visible_codex_app_session`.
- `ValidateChildReadiness.cs`: passed before accepted-status sync.
- OpenSpec archive: passed; archived as `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-closeout-archive/`.
- `git diff --check`: passed before accepted-status sync.
- `MD-E2E-5`: not run by design; belongs to S3.
- Live `thread/archive`: not run by design; live archive mode remains opt-in.

## Definition of Ready for Implementation

S5 is ready for implementation only when all are true:

1. S1 freezes the launch evidence fields consumed by S5.
2. S2 freezes validator behavior, visible evidence class names, fixture root and failure classes.
3. This child spec is resynced to the frozen field names and accepted S2 validator contract.
4. The Child Index row points to this child spec and a persisted S5 handoff.
5. The S5 handoff has an enforceable implementation write-set.
6. `ValidateChildReadiness.cs` passes for `ADV-CAS-S5`.
7. App-server protocol rehearsal confirms `thread/archive` and `ThreadListParams.archived`.
8. S5 fixture manifests are defined as source-controlled implementation artifacts with exact expected outcomes.

Current DoR verdict: satisfied; implementation has been delivered for exactly `ADV-CAS-S5`.

## Definition of Done / Closeout Evidence

S5 delivery is done only when:

1. `spec-closeout` requires closeout archive evaluation before child final `READY`.
2. The closeout companion tool can validate archive summaries and, in an opted-in live mode, call app-server `thread/archive`.
3. Fixture cases cover visible archived, already archived, headless, queued/no-thread, manual-visible missing thread, archive failure, proof failure and unarchived `READY` negative.
4. Workflow docs describe explicit statuses for headless/no-thread evidence.
5. S5 implementation evidence retains fixture summaries and command outputs under stable workspace paths.
6. Parent/orchestration closeout references S5 evidence before S3 live MD-E2E-5 can claim final success.

## Dependencies and Write-Set

Hardening lane write ownership for this run:

- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S5 Closeout Archive Support.md`
- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`
- `_specs/child-session-handoffs/adv-cas-s5-session-handoff.md`

Read-only for this run:

- `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`
- `skills-repo/skills/spec-closeout/SKILL.md`
- `docs/doc-workflow.md`
- `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`
- `skills-repo/tools/ValidateChildReadiness.cs`
- `tests/docworkflow-agent-delivery/**`

S5 implementation write-set:

- `skills-repo/skills/spec-closeout/SKILL.md`
- `docs/doc-workflow.md`
- `skills-repo/tools/ArchiveVisibleCodexAppSession.cs`
- `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`
- `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**`
- `tests/docworkflow-agent-delivery/e2e/validators/visible-session-closeout-summary.js`
- `tests/docworkflow-agent-delivery/README.md`
- `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-closeout-archive/**`

Future implementation read-only files:

- `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- S1 child spec and S1 retained evidence
- S2 child spec and S2 retained validator evidence
- S3/S4 child specs until their own child gates are ready
- `_specs/codex-app-server-spikes/20260509T171506Z/**`

Dependencies:

| Dependency | Status | Why It Matters |
|---|---|---|
| S1 evidence schema | implemented | S5 consumes the `agent-delivery.session-launch.v2` visible/headless/queued evidence fields. |
| S2 validator delivery | accepted | S5 consumes `ValidateVisibleCodexAppSessionEvidence.cs`, S2 fixture root, and `unarchived_visible_session`. |
| App-server protocol archive support | rehearsed schema, no live archive | `thread/archive`, archive notification and `ThreadListParams.archived` are confirmed by generated schema; live archive remains delivery opt-in only. |
| Orchestration pack S5 row | accepted by closeout run | Row records `ACCEPTED`, archived OpenSpec path and retained S5 fixture evidence. |

Parallelism:

- S5 hardening is complete after accepted S2 validator sync.
- S5 implementation is accepted and closed.
- S3 final live `MD-E2E-5` may consume S5 archive behavior after S4/S3 gates are ready.

## Closeout Sync Targets

S5 closeout sync updated:

1. S5 child spec status and implementation evidence.
2. Orchestration pack Child Index row for `ADV-CAS-S5`.
3. Parent coverage for `ADV-PR9`.
4. Next child/handoff state for S3 if S3 becomes the leading live-test child.
5. `spec-closeout` skill wording and docs workflow wording.
6. S5 OpenSpec archive path.
7. Retained evidence paths for archive fixture summaries.

This closeout run updates the S5 child spec, Child Index row, S5 handoff, closeout skill, workflow docs, tools, fixtures, README and archived OpenSpec ledger.

## Child Session Handoff

Persisted S5 implementation handoff:

- `_specs/child-session-handoffs/adv-cas-s5-session-handoff.md`

The handoff must remain synchronized with the Child Index row and must carry:

1. `Aktueller Verdict: ACCEPTED / CLOSED`.
2. Accepted implementation write-set for `skills-repo/skills/spec-closeout/SKILL.md`, `docs/doc-workflow.md`, `skills-repo/tools/ArchiveVisibleCodexAppSession.cs`, `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`, `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**`, `tests/docworkflow-agent-delivery/e2e/validators/visible-session-closeout-summary.js`, `tests/docworkflow-agent-delivery/README.md`, and `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-closeout-archive/**`.
3. Explicit non-goals: no live `MD-E2E-5` in S5 delivery, no Launcher adapter work, no S3 runner edits except a handoff note if this spec explicitly requires it, no direct SQLite mutation, no live archive call unless opt-in.
4. Verification gates for S5 fixture validation, S2 visible evidence regression, source search for archive/status wording, `git diff --check`, and no MD-E2E-5.

Next mode:

- no further S5 action; continue with S4/S3 according to the orchestration pack.

## Content Quality Review

- Correctness/domain fit: pass for a closeout/archive child. The spec uses app-server `thread/archive` and treats headless `exec` as non-visible evidence.
- Scope discipline: pass. Runtime implementation, MD-E2E-5 and shared control edits remain out of scope.
- Completeness: pass. Archive statuses, fields, cases, S2 validator coupling, tool expectations, fixture family and verification lifecycle are defined.
- Consistency: pass. Review Control Surface, DoR, delivery and closeout verdicts all state that S5 is accepted after S2 validator delivery and S5 archive fixture replay.
- Feasibility: pass as a future companion-tool implementation. Local generated schema includes `ThreadArchiveParams`, `ThreadArchiveResponse`, `ThreadArchivedNotification` and `ThreadListParams.archived`.
- Verifiability: pass for implementation readiness. Negative unarchived `READY`, headless/no-thread, archive failure, proof failure and mixed child run cases are concrete; fixture files and validators are explicitly in the S5 implementation write-set.

## Final Hardening Verdict

IMPLEMENTATION READY for exactly `ADV-CAS-S5` before delivery; superseded by accepted closeout.

Implementation completed and closeout accepted using this child spec, the synchronized Child Index row, and `_specs/child-session-handoffs/adv-cas-s5-session-handoff.md`.

Non-blocking notes:

1. Live `thread/archive` remains opt-in for delivery; fixture/mock transcript validation is the default gate.
2. `retained_session_accepted` requires explicit user acceptance and must not be treated as ordinary archive success by the S2 validator.

## Final Delivery Verdict

ACCEPTED for `ADV-CAS-S5`. S5 now has the closeout archive companion tool, S5 fixture family, S2 validator bridge, docs/skill wording, README entry and archived OpenSpec evidence required for downstream S3 consumption.

## Mini-Retro

- Was wurde entschieden? S5 should be a `spec-closeout` plus closeout companion-tool contract, not a Launcher change. Visible threads require app-server `thread/archive`; headless and queued/no-thread records require explicit archive statuses.
- Was wurde geaendert? Re-hardened S5 after accepted S2, synchronized validator names/failure classes, finalized archive summary/tool expectations, defined the source-controlled closeout fixture family, and promoted the Child Index/handoff path for implementation.
- Was bleibt offen? Later S3 live MD-E2E-5 consumption and any explicitly opted-in live archive call.
- Welche Evidenz/Verification fehlt? No live archive call and no MD-E2E-5 run by design; S5 fixture and validator evidence is retained in source-controlled fixtures and archived OpenSpec evidence.
- Welche Skill-/Workflow-Reibung ist aufgefallen? S2's accepted closeout check is intentionally narrow (`archived` / `visible_session_archived` booleans), so S5 implementation must preserve that bridge while adding the richer closeout summary schema.
- Session-/Kontextzustand: No further S5 session needed; continue with S4/S3 according to the orchestration pack.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-10 | Codex | Created S5 closeout archive support child spec as a contract-heavy hardening draft; final verdict remains blocked on S1/S2 evidence schema. |
| 2026-05-10 | Codex | Re-hardened S5 after S1 implementation and S2 promotion; S5 now waits specifically for S2 validator delivery. |
| 2026-05-10 | Codex | Re-hardened S5 after accepted S2 validator delivery; synchronized S2 contract names, fixture/failure classes, archive tool expectations, Child Index and handoff; promoted to implementation-ready. |
| 2026-05-11 | Codex | Implemented S5 closeout archive support, fixture suite, S2 validator bridge, docs/skill sync and OpenSpec evidence; delivery gates passed. |
| 2026-05-11 | Codex | Accepted S5 closeout, replayed verification, archived OpenSpec change and synchronized Child Index/handoff evidence. |

SessionId: 2026-05-10-adv-cas-s5-closeout-archive-support-hardening
