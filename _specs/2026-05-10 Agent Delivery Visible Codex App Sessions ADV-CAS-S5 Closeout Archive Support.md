**Date:** 2026-05-10
**Status:** Spec
**Scope:** Child hardening draft for `ADV-CAS-S5 Closeout Archive Support`. Documentation/spec hardening only; no runtime implementation and no live `MD-E2E-5` execution.

---

## Session Briefing

- Modus/Skill: `child-spec-hardening`.
- Source of Truth: `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`; `skills-repo/skills/spec-closeout/SKILL.md`; `docs/doc-workflow.md`; `skills-repo/tools/AgentDeliverySessionLauncher.cs`; `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`; generated local app-server protocol references under `/tmp/codex-app-schema/`.
- Ziel: Harden only child `ADV-CAS-S5` into a contract-heavy closeout/archive support spec that can later be made implementation-ready after S1/S2 freeze the visible evidence schema.
- Nicht-Ziele: No runtime code edits; no orchestration pack edit; no child handoff edit; no Launcher implementation; no validator implementation; no test fixture creation; no `MD-E2E-5` run; no app-server archive call in this hardening run.
- In Scope: Review Control Surface, archive contract for `thread/archive`, closeout evidence fields, no-thread/headless statuses, negative unarchived `READY` case, verification lifecycle, parent conformance, and final readiness verdict.
- Erwarteter Output: this child spec file only.
- Verification/Review: content-quality review and `git diff --check` after the spec edit. `ValidateChildReadiness.cs` is intentionally not an implementation-ready gate here because the lane may not update the Child Index or create a persisted S5 handoff.
- Offene Entscheidungen: No product decision is requested in this hardening pass. Blocking dependency remains S2 validator schema and S1 delivery evidence shape.

## Review Control Surface

- Spec-Variante: Contract-heavy Parent/Child closeout child spec.
- Goldstandard Status: candidate child spec, not implementation-ready because predecessor schema contracts are missing.
- Ziel: Define how `spec-closeout` archives visible Codex-App sessions opened for a child run, records explicit archive statuses for headless/no-thread evidence, and blocks final `READY` when any visible thread remains unarchived.
- In Scope: `spec-closeout` closeout gate behavior; app-server `thread/archive` request/response contract; post-archive proof using `thread/list`; closeout archive summary fields; status enums for visible, headless, queued, manual, no-thread and failure cases; negative false-positive case where a child closeout claims `READY` while visible sessions remain unarchived.
- Out of Scope: Launcher app-server adapter implementation; S1/S2 visible evidence schema implementation; MD-E2E-5 runner implementation; live Codex-App session creation; direct SQLite mutation; broad project docs sync beyond closeout wording; archiving historical evidence created before this parent unless explicitly linked to the target child run.
- Key Test/Harness Cases: visible archive positive; already archived positive; headless `codex exec` gets `not_app_visible_not_archived`; queued/manual without a thread gets `no_thread_created`; manual-visible without thread proof fails; visible thread archive failure returns `NOT_READY`; post-archive proof failure returns `NOT_READY`; mixed child run with all visible sessions archived and all non-visible records explicit can return `READY`; negative unarchived `READY` case fails.
- Key Verification Commands: `codex app-server --help`; `codex app-server generate-ts --out /tmp/codex-app-schema`; inspect generated `ThreadArchiveParams`, `ThreadArchiveResponse`, `ThreadListParams`; future delivery command for S5 archive fixture suite; future validator command after S2 validator schema; `git diff --check`. Do not run `MD-E2E-5` for this child hardening.
- Open Decisions / Blockers: `[MISSING S1/S2 evidence schema]` S5 cannot finalize exact consumed field names, validator class names, or fixture manifests until S1 and S2 freeze the visible launch evidence schema and validator behavior.
- Readiness Status: `NEEDS HARDENING - waiting for S2 validator schema and S1 delivery evidence shape`.

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
| `ADV-PR9` | Primary owner. Child closeout archives visible app-server sessions through `thread/archive` or records explicit no-thread/not-app-visible states. | covered_by_contract |
| `ADV-PR5` | Consumes launch evidence fields for `execution_channel`, `session_visibility`, thread identity, title, cwd, prompt/hash and evidence paths. | blocked_on_S1_S2_schema |
| `ADV-PR7` | Supplies archive/no-thread evidence required for final `MD-E2E-5` pass. | supports_later_S3 |
| `ADV-PR10` | Prevents workflow docs/skills from treating `status: launched` from `codex exec` as visible-app success. | covered_by_contract |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `ADV-PR9` | `spec-closeout` must archive every visible thread for the child run before final `READY`. | preserves | Implement S5 only after S1/S2 schema fields are frozen. |
| `ADV-PR5` | S5 defines consumed and emitted fields, but exact upstream evidence names remain provisional. | defers_to_child | S1 owns launch evidence production; S2 owns validator schema. S5 must resync after both exist. |
| `ADV-PR7` | S5 does not run or implement `MD-E2E-5`; it provides the archive condition that S3 must consume. | narrows_with_rationale | S3 remains the live workflow integration owner. |
| `ADV-PR10` | S5 treats headless `exec` as `not_app_visible_not_archived`, never as archived visible evidence. | preserves | Add closeout docs/skill wording during S5 delivery. |

Conformance verdict: no parent contradiction found. Implementation readiness is blocked only by missing S1/S2 evidence schema and by the current lane's read-only control surfaces.

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

Blocking marker:

- `[MISSING S1/S2 evidence schema]` Exact source fields and validator fixture layout cannot be final until S1/S2 produce stable `session_visibility` and validator contracts.

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

The S5 archive evaluator consumes these fields. Names are provisional until S1/S2 freeze the schema, but the semantics are required:

| Field | Required For | Meaning |
|---|---|---|
| `schema_version` | all records | Launch/evidence schema version. |
| `parent` or `parent_spec` | all records | Parent spec identity used for child-run grouping. |
| `target_id` | all records | Stable child id, for example `ADV-CAS-S5` or `RSW-C1`. |
| `target_spec` | all child records | Child spec path or stable child spec reference. |
| `handoff_path` | all handoff-backed records | Handoff that created or queued the session. |
| `execution_channel` | all records | `headless_cli`, `app_server`, `manual_queue`, or `manual_visible`. |
| `status` | all records | Launch/queue process status, not visibility proof by itself. |
| `session_visibility.class` | all records | `visible_codex_app_session`, `manual_visible_start`, `headless_cli_session`, `queued_manual_start`, or `traceable_but_not_visible`. |
| `session_visibility.thread_id` | visible/manual-visible records | App-server or manually observed Codex thread id. |
| `session_visibility.visible_in_codex_app` | visible/manual-visible records | True only when app visibility is proven. |
| `session_visibility.thread_source_observed` | visible/headless records | Observed source such as `vscode` or `exec`. |
| `session_visibility.cwd_observed` | visible records | Observed cwd, used to distinguish target workspace from initiating project. |
| `session_title` or `session_visibility.title_observed` | visible records | Deterministic Agent Delivery title. |
| `prompt_sha256` | launched records | Prompt linkage for forensic grouping. |
| `evidence_paths.prompt` | queued/launched records | Prompt path retained with the launch record. |

If S1/S2 choose different field names, S5 must update this table before implementation.

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

Provisional parseable shape:

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

### Redaction And Safety

Archive summaries and protocol transcripts must not include secrets, bearer tokens, raw environment dumps, full prompts with secrets, or unrelated user thread contents. Required retained content is limited to session identity, target grouping fields, app-server method names, non-secret params, response status, thread id, cwd/title, timestamps, hashes, and evidence paths.

## Canonical Examples and Fixtures

Pattern: hybrid.

- Embedded examples in this spec are compact, parseable examples for the intended summary shape.
- Full fixtures must be created during S5 implementation under `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**`.
- Fixture manifests must name each case, its input launch evidence files, the expected `archive_status` records, expected final closeout verdict, and whether app-server calls are replayed through a mock transcript or a real opted-in app-server process.
- Fixtures are not required before this hardening pass ends because final verdict is blocked on S1/S2 schema.

Required future fixture paths:

| Fixture Path | Case Coverage |
|---|---|
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/archive-positive/` | visible thread archived, proof passes |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/already-archived/` | already archived proof passes |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/headless-exec/` | headless evidence gets `not_app_visible_not_archived` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/queued-no-thread/` | queued/manual no-thread gets `no_thread_created` |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/manual-visible-missing-thread/` | manual-visible claim without thread blocks READY |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/unarchived-ready-negative/` | closeout summary claiming READY with unarchived visible thread fails |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/archive-failed/` | archive API failure blocks READY |
| `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/proof-failed/` | archive call without post-archive proof blocks READY |

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
| `s5-archive-positive` | Prove visible app thread is archived. | Visible evidence with `thread_id`, mock app-server archive transcript. | pass / `READY` | closeout archive summary with `archive_status: archived`. | Transcript contains no prompt body or secrets. |
| `s5-already-archived` | Avoid failing idempotent closeout. | Visible evidence plus archived-list proof. | pass / `READY` | `archive_status: already_archived`. | No second archive call required. |
| `s5-headless-explicit` | Preserve honest headless status. | `codex exec` evidence with `source: exec`. | pass / `READY` for archive dimension | `archive_status: not_app_visible_not_archived`. | Must not set `visible_codex_app_session`. |
| `s5-queued-no-thread` | Handle queued/manual starts without real sessions. | Queued/manual evidence without `thread_id`. | pass / `READY` for archive dimension | `archive_status: no_thread_created`. | Must not invent thread ids. |
| `s5-manual-visible-missing-thread` | Reject unverifiable manual visible claim. | Manual-visible evidence without `thread_id`. | fail / `NOT_READY` | `archive_status: manual_visible_missing_thread`. | Human text alone is not enough. |
| `s5-unarchived-ready-negative` | Block false closeout success. | Closeout summary says `READY` while visible thread is unarchived. | fail / `NOT_READY` | validator finding names the unarchived thread. | This is the required negative unarchived READY case. |
| `s5-archive-failed` | Ensure failed archive blocks closeout. | App-server error response or timeout. | fail / `NOT_READY` | `archive_status: archive_failed`. | Error text redacted. |
| `s5-proof-failed` | Ensure archive proof is mandatory. | Archive response without archived-list proof. | fail / `NOT_READY` | `archive_status: proof_failed`. | Empty `{}` response alone is insufficient. |
| `s5-mixed-child-run` | Prove combined status computation. | One archived visible record, one headless record, one queued no-thread record. | pass / `READY` | three explicit session records. | No hidden skipped case counts as passed. |
| `s5-retained-session-accepted` | Allow explicit user-approved retained visible thread. | Visible record plus explicit retention acceptance. | pass / `READY` only with retained note | `archive_status: retained_session_accepted`. | Missing `retention_accepted_by` or reason fails. |

## Verification Commands

Do not run `MD-E2E-5` during S5 hardening or S5 implementation. `MD-E2E-5` belongs to S3 after S1/S2/S4/S5 contracts exist.

Command contract for future S5 hardening completion after S1/S2:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
codex app-server --help
codex app-server generate-ts --out /tmp/codex-app-schema
test -f /tmp/codex-app-schema/v2/ThreadArchiveParams.ts
test -f /tmp/codex-app-schema/v2/ThreadArchiveResponse.ts
test -f /tmp/codex-app-schema/v2/ThreadListParams.ts
git diff --check
```

Future S5 delivery gates after implementation:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout --mode validate
dotnet run skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout
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
- `ValidateChildReadiness.cs`: not run because this lane may not update the Child Index or create a persisted S5 handoff, and the final verdict is not implementation-ready.

## Definition of Ready for Implementation

S5 is ready for implementation only when all are true:

1. S1 freezes the launch evidence fields consumed by S5.
2. S2 freezes validator behavior and visible evidence class names.
3. This child spec is resynced to the frozen field names.
4. The Child Index row points to this child spec and a persisted S5 handoff.
5. The S5 handoff has an enforceable implementation write-set.
6. `ValidateChildReadiness.cs` passes for `ADV-CAS-S5`.
7. App-server protocol rehearsal confirms `thread/archive` and `ThreadListParams.archived`.
8. Fixture manifests exist or are in the implementation write-set with exact expected outcomes.

Current DoR verdict: `NEEDS HARDENING - waiting for S2 validator schema and S1 delivery evidence shape`.

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

Read-only for this run:

- `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`
- `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions Orchestration Pack.md`
- `_specs/child-session-handoffs/**`
- `skills-repo/skills/spec-closeout/SKILL.md`
- `docs/doc-workflow.md`
- `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`
- `skills-repo/tools/ValidateChildReadiness.cs`
- `tests/docworkflow-agent-delivery/**`

Future S5 implementation write-set after S2 validator schema and S1 delivery evidence shape stabilize:

- `skills-repo/skills/spec-closeout/SKILL.md`
- `docs/doc-workflow.md`
- `skills-repo/tools/ArchiveVisibleCodexAppSession.cs`
- `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`
- `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout/**`
- `tests/docworkflow-agent-delivery/e2e/validators/visible-session-closeout-summary.js`
- `tests/docworkflow-agent-delivery/README.md`
- `openspec/changes/agent-delivery-visible-session-closeout-archive/**`

Future implementation read-only files:

- `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- S1 child spec and S1 retained evidence
- S2 child spec and S2 retained validator evidence
- S3/S4 child specs until S5 closeout evidence is accepted
- `_specs/codex-app-server-spikes/20260509T171506Z/**`

Dependencies:

| Dependency | Status | Why It Matters |
|---|---|---|
| S1 evidence schema | missing | S5 needs exact launch/session fields and visibility class shape. |
| S2 validator schema | missing | S5 needs the canonical validator names and fixture manifest contract. |
| App-server protocol archive support | observed in generated schema | `thread/archive`, archive notification and `ThreadListParams.archived` exist locally, but S5 has not rehearsed a live archive. |
| Orchestration pack S5 row | read-only | Current row says S5 needs hardening and no handoff exists. |

Parallelism:

- S5 hardening can proceed as a contract draft in parallel only as long as S1/S2 files remain read-only.
- S5 implementation must wait until S1/S2 schema is stable.
- S3 final live `MD-E2E-5` must wait until S5 archive behavior is implemented and accepted.

## Closeout Sync Targets

When S5 is eventually delivered and accepted, closeout sync must update:

1. S5 child spec status and implementation evidence.
2. Orchestration pack Child Index row for `ADV-CAS-S5`.
3. Parent coverage for `ADV-PR9`.
4. Next child/handoff state for S3 if S3 becomes the leading live-test child.
5. `spec-closeout` skill wording and docs workflow wording.
6. S5 OpenSpec archive or ledger path.
7. Retained evidence paths for archive fixture summaries.

This hardening lane may not update those targets. Integration owner must apply that sync after S5 becomes implementation-ready or accepted.

## Child Session Handoff

No S5 implementation handoff is created in this run.

Reason:

1. Final verdict is not implementation-ready.
2. The current write ownership is limited to this child spec file.
3. The orchestration pack has no S5 handoff pointer yet.
4. `ValidateChildReadiness.cs` cannot pass until the Child Index and persisted handoff are synchronized.

Future handoff target:

- `_specs/child-session-handoffs/adv-cas-s5-session-handoff.md`

Future next mode:

- `spec-change-delivery` only after S2 validator schema and S1 delivery evidence shape stabilize, S5 resync, Child Index sync, S5 handoff creation and readiness validation.

## Content Quality Review

- Correctness/domain fit: pass for a closeout/archive child. The spec uses app-server `thread/archive` and treats headless `exec` as non-visible evidence.
- Scope discipline: pass. Runtime implementation, MD-E2E-5 and shared control edits remain out of scope.
- Completeness: partial by design. Archive statuses, fields, cases and verification lifecycle are defined, but exact S1/S2 field names are still blocked.
- Consistency: pass. Review Control Surface, DoR and verdict all state that S5 waits for S2 validator schema and S1 delivery evidence shape.
- Feasibility: pass as a future companion-tool implementation. Local generated schema includes `ThreadArchiveParams`, `ThreadArchiveResponse`, `ThreadArchivedNotification` and `ThreadListParams.archived`.
- Verifiability: partial by design. Negative unarchived `READY`, headless/no-thread, archive failure and proof failure cases are concrete, but fixture files and validators are future implementation artifacts.

## Final Hardening Verdict

`NEEDS HARDENING - waiting for S2 validator schema and S1 delivery evidence shape`.

Implementation must not start from this S5 spec yet.

Blocking items:

1. S1 visible app-server launch evidence schema is not frozen.
2. S2 visible evidence validator schema and fixture manifest are not frozen.
3. S5 Child Index row and S5 persisted handoff are not synchronized because this hardening lane may not edit shared control artifacts.
4. S5 command-contract rehearsal and `ValidateChildReadiness.cs` are intentionally not complete.

## Mini-Retro

- Was wurde entschieden? S5 should be a `spec-closeout` plus closeout companion-tool contract, not a Launcher change. Visible threads require app-server `thread/archive`; headless and queued/no-thread records require explicit archive statuses.
- Was wurde geaendert? Created the S5 child spec with Review Control Surface, archive contract, evidence fields, no-thread/headless statuses, negative unarchived `READY` case, verification lifecycle and parent conformance.
- Was bleibt offen? S1/S2 evidence schema, S5 handoff, Child Index sync, fixture manifests and readiness validation.
- Welche Evidenz/Verification fehlt? No live archive call, no MD-E2E-5 run, no S5 fixture execution, no `ValidateChildReadiness.cs` pass.
- Welche Skill-/Workflow-Reibung ist aufgefallen? S5 can be contract-hardened before S1/S2, but cannot become implementation-ready without exact predecessor schema and shared control-surface sync.
- Session-/Kontextzustand: Stop after this hardening draft; continue after S2 validator schema and S1 delivery evidence shape stabilize.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-10 | Codex | Created S5 closeout archive support child spec as a contract-heavy hardening draft; final verdict remains blocked on S1/S2 evidence schema. |

SessionId: 2026-05-10-adv-cas-s5-closeout-archive-support-hardening
