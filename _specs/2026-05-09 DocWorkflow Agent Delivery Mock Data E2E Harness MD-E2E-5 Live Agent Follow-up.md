**Date:** 2026-05-09
**Status:** NEEDS PARENT/ORCHESTRATOR SYNC
**Scope:** Optional live Agent/Codex follow-up path that supplements, but never replaces, the accepted local mock-first E2E baseline.

---

## Review Control Surface

- Spec-Variante: Hardened Child Spec for optional live-agent follow-up.
- Goldstandard Status: hardened ready-candidate blocked by Child Index synchronization.
- Ziel: Define an optional live Agent/Codex evidence path that can write compatible launch/session/evidence artifacts while preserving `run-mock-e2e-checks.sh all --keep` as the required local baseline.
- In Scope: live-agent harness contract; launch/queue/manual/blocker evidence semantics; compatibility with `docworkflow-agent-delivery-mock-e2e-summary.v1` meaning; local baseline replay requirement; forbidden real-fixture guards; OpenSpec ledger expectations; implementation write-set for a later `spec-change-delivery` run.
- Out of Scope: changing the accepted local mock runner; changing the standard gate; making network, Docker, Codex auth, external providers or manual starts required for `run-mock-e2e-checks.sh all --keep`; KI-fuer-KMU or other real product fixtures; claiming live-agent success without launch/session evidence.
- Wichtigste Test-/Harness-Cases: `LIVE-BASELINE-REPLAY`, `LIVE-AUTO-QUEUE-EVIDENCE`, `LIVE-MANUAL-START-BLOCKED`, `LIVE-AUTH-PROVIDER-BLOCKED`, `LIVE-FORBID-REAL-FIXTURE`, `LIVE-SUMMARY-COMPAT`, `LIVE-NO-STANDARD-GATE-REPLACEMENT`.
- Wichtigste Verification Commands: `git diff --check`; `bash -n tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-5-local-baseline`; `tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh blocked --keep --run-id closeout-md-e2e-5-blocked`; `dotnet run skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/live-agent/fixtures/launch-evidence`; `openspec validate docworkflow-agent-mock-e2e-md-e2e-5-live-agent-follow-up --strict`.
- Offene Entscheidungen: None blocking for the hardened contract. Provider availability is runtime state and must be represented as `blocked` or `manual_start_required`, not pass.
- Readiness Status: NEEDS PARENT/ORCHESTRATOR SYNC. The child contract is hardened, but the Child Index row still says `DEFERRED FOLLOW-UP`; implementation cannot start until the integration owner updates the Child Index row and reruns readiness validation.

## Session Briefing

- Modus/Skill: `child-spec-hardening`.
- Source of Truth: this child spec; parent spec `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`; Child Index in `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`; accepted MD-E2E-1 through MD-E2E-4 specs, handoffs and retained evidence.
- Ziel: Make MD-E2E-5 precise enough for a later implementation handoff without weakening the accepted local baseline.
- Nicht-Ziele: no runtime implementation in this hardening session, no live-provider call, no standard-gate change, no real product fixture.
- Erwarteter Output: hardened child spec, synchronized MD-E2E-5 handoff, exact Child Index integration-owner patch, and hardening verification evidence.
- Verification/Review: content-quality review, `git diff --check`, non-ready readiness validation showing the Child Index sync blocker, and safe command-contract checks for commands that already exist.
- Offene Entscheidungen: none blocking.

## Goal

Add an optional live Agent/Codex path that proves whether a real agent launch can be queued, launched, manually deferred, blocked or failed with machine-readable evidence. The path must always replay the accepted local mock baseline and must never become the standard success path unless the parent/orchestrator opens a separate standard-gate change.

## In Scope

- A new optional command `tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh` with selectors `preflight`, `blocked`, `auto`, `launch` and `all`.
- Live-agent harness code under `tests/docworkflow-agent-delivery/e2e/live-agent/**`.
- Launch evidence that uses the existing Agent Delivery Session Launch/Queue Evidence semantics from `docs/doc-workflow.md`.
- Validation of `queued`, `launched`, `manual_start_required`, `blocked` and `failed` states.
- Compatibility checks that keep local mock summaries and live launch evidence distinguishable.
- OpenSpec change ledger `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-5-live-agent-follow-up/**`.
- Retained evidence roots matching `tests/docworkflow-agent-delivery/e2e/evidence/live-agent-md-e2e-5-*`.

## Out of Scope

- Editing `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`.
- Editing `tests/docworkflow-agent-delivery/e2e/mock-runner/**`.
- Requiring live-agent auth, network, Docker, external providers or manual starts for the local mock baseline.
- Promoting `run-live-agent-e2e-checks.sh` to the standard command.
- Reading, copying, building, testing, deploying or modifying KI-fuer-KMU or any other real product repository.
- Treating fallback artifacts, blocked auth, blocked network, blocked provider adapters or manual starts as pass evidence.

## Parent/Master Coverage

| Parent Requirement | Coverage |
|---|---|
| `MD-PR9` | Primary owner. Separates optional live Agent/Codex evidence from the accepted local mock runner baseline. |
| `MD-PR1` | Reinforces the no-real-fixture policy for any live evidence path. |
| `MD-PR6` | Extends the evidence truth model by making live launch/session states explicit and machine-readable. |
| `MD-PR7` | Preserves the mock-only standard gate and prevents live provider availability from becoming a hidden prerequisite. |

## Parent Scope Conformance

| Parent Requirement / Intent | Conformance | MD-E2E-5 Contract |
|---|---|---|
| `MD-PR9` optional live-agent path | preserves | Live-agent behavior is isolated in an optional command and cannot replace local baseline acceptance. |
| `MD-PR1` no real product fixtures | preserves | Live evidence may target only synthetic/mock harness inputs and generated evidence roots; KI-fuer-KMU paths remain forbidden. |
| `MD-PR6` evidence states distinguish pass, blocked and manual | extends | The live path records `queued`, `launched`, `manual_start_required`, `blocked` and `failed` without collapsing blockers into pass. |
| `MD-PR7` mock-only standard gate | preserves | The accepted standard remains `run-mock-e2e-checks.sh all --keep`; live commands are supplemental only. |
| MD-E2E-1 through MD-E2E-4 accepted baseline | preserves | Implementation must replay the local baseline and cite retained predecessor evidence before any live success claim. |

No parent requirement is contradicted. The only extension is the optional live evidence surface under `MD-PR9`.

## Decision Freeze Pack

- The live command is optional and supplemental.
- The accepted local baseline command remains:

```sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep
```

- A live run may report `pass` only when matching launch evidence is `queued` or `launched` and the required local baseline replay also passes.
- `manual_start_required`, `blocked` and `failed` are valid reported outcomes, but they are not pass evidence and cannot release implementation closeout by themselves.
- Provider selection defaults to the existing `codex` launcher contract. Unsupported providers must produce `manual_start_required` or `blocked` evidence rather than synthetic success.
- No secret values may be written to prompts, summaries, launch requests, evidence files, telemetry or retained logs.
- No KI-fuer-KMU or other real product path may appear as a target workspace, fixture source, compatibility source, write-set or positive evidence path.
- Child Index synchronization is blocking before implementation starts.

## Normative Contract

### Command Contract

The later implementation must add:

```sh
tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh [preflight|blocked|auto|launch|all] [--keep] [--run-id ID]
```

Selector meanings:

| Selector | Required Behavior | Pass Meaning |
|---|---|---|
| `preflight` | Validate local paths, fixture contracts, no-real-fixture policy and presence of required local tooling without launching a provider. | Passes only local contract checks. |
| `blocked` | Exercise deterministic blocked/manual cases without network, auth or provider calls. | Passes only if blockers are reported as blocked/manual and not pass. |
| `auto` | Use `AgentDeliverySessionLauncher.cs --mode queue` or equivalent dry-run-safe queue behavior for Codex. | Passes only with valid `queued` launch evidence and local baseline replay. |
| `launch` | Attempt a real Codex launch only when explicitly selected. | Passes only with valid `launched` evidence and local baseline replay; blocked provider/auth/network remains blocked. |
| `all` | Run `preflight`, `blocked`, `auto`, and local baseline replay. | Passes only when local baseline passes and `auto` produces queued/launched evidence; otherwise records blocked/manual status and exits non-zero for implementation closeout. |

The command must run from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`. Any unsupported cwd exits `2` with a clear usage or cwd error.

### Evidence Contract

The live path must write evidence under a retained run root:

```text
tests/docworkflow-agent-delivery/e2e/evidence/live-agent-md-e2e-5-<run-id>/
```

Required files for a retained run:

| File | Meaning |
|---|---|
| `live-agent-summary.json` | Top-level live follow-up summary. |
| `local-baseline/mock-e2e-summary.json` | Copied or referenced local baseline replay summary from `run-mock-e2e-checks.sh all --keep`. |
| `launch/launch-request.json` | Agent Delivery launch request when a queue/launch/manual path is attempted. |
| `launch/evidence.json` | Agent Delivery launch evidence with status and provider fields. |
| `launch/start-prompt.md` | Prompt evidence only when generated by the launcher and scrubbed of secrets. |
| `negative-guard-evidence.json` | Deterministic blocked/manual/forbidden-path assertions. |
| `command-telemetry.json` | Command classes, cwd, selector, status and forbidden action telemetry. |

`live-agent-summary.json` must include at least:

| Field | Allowed / Required Values |
|---|---|
| `schema_id` | `docworkflow-agent-delivery-live-agent-follow-up.v1` |
| `run_id` | non-empty string matching the retained evidence directory suffix |
| `selector` | `preflight`, `blocked`, `auto`, `launch` or `all` |
| `overall_live_status` | `pass`, `blocked`, `manual_start_required` or `failed` |
| `local_baseline_status` | `pass` or `failed` |
| `local_baseline_command` | `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep` |
| `launch_status` | `queued`, `launched`, `manual_start_required`, `blocked`, `failed` or `not_attempted` |
| `evidence_truth` | `ran-target`, `queued`, `blocked`, `manual`, `failed` or `not_attempted` |
| `runner_mode` | `live-agent-follow-up` |
| `standard_gate_replaced` | `false` |
| `forbidden_fixture_status` | `pass` or `fail` |
| `external_dependencies` | object with `network`, `docker`, `codex_auth`, `external_provider`, `manual_start`; values must be `used`, `not_used`, `blocked` or `manual_required` |
| `launch_evidence` | relative paths to launch evidence files when present |
| `local_mock_summary` | relative path to local baseline summary |
| `negative_cases` | array of deterministic negative case results |

The existing local mock summary schema remains unchanged. Live-agent evidence must not mutate `docworkflow-agent-delivery-mock-e2e-summary.v1`; it must reference the local mock summary as baseline evidence.

### Launch Evidence Compatibility

The later implementation must use or remain compatible with:

```sh
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff _specs/child-session-handoffs/md-e2e-5-session-handoff.md \
  --target-id MD-E2E-5 \
  --agent codex \
  --mode queue \
  --out _specs/agent-delivery-session-launches
```

and validate launch artifacts with:

```sh
dotnet run skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- \
  --handoff _specs/child-session-handoffs/md-e2e-5-session-handoff.md \
  --launch-request <run-root>/launch/launch-request.json \
  --evidence <run-root>/launch/evidence.json
```

If this command returns manual, blocked or failed, the live path must preserve that state in `live-agent-summary.json` and must not convert it into pass.

### Forbidden Fixture and Secret Contract

The live path must scan handoff, launch request, prompt, summaries, telemetry, target workspace declarations, write-sets and retained evidence for forbidden real-fixture markers:

- `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**`
- `ki-fuer-kmu/**`
- real-fixture compatibility markers
- target workspaces outside generated mock/synthetic evidence roots

Secret-like values must be redacted before persistence. If redaction cannot be proven, the run status is `blocked`.

## Canonical Examples and Fixtures

Pattern: referenced fixture files.

The implementation must create deterministic live-agent fixture cases under:

```text
tests/docworkflow-agent-delivery/e2e/live-agent/fixtures/launch-evidence/
```

Required fixture cases:

| Fixture Case | Required Meaning |
|---|---|
| `queued-valid` | Matching handoff, launch request and evidence produce queued pass for launch-evidence validation. |
| `manual-start-required` | Manual provider/manual start evidence is visible and reported as manual, not automatic pass. |
| `blocked-auth-provider` | Missing auth/provider/network produces blocked evidence and blocks live closeout. |
| `failed-launch` | Failed launch evidence stays failed and blocks live closeout. |
| `forbidden-real-fixture` | Forbidden real fixture marker fails the no-real-fixture gate. |
| `summary-local-baseline-missing` | Live summary without local baseline replay fails closeout. |

Fixture files are in implementation scope and must be exercised by the live harness. This spec intentionally avoids embedded normative JSON examples; the fixture files become the canonical machine-readable examples once implemented.

## Control Flow and Failure Cases

1. `preflight` checks repo root, script syntax, no-real-fixture policy and fixture availability.
2. `blocked` writes deterministic blocker evidence and verifies that blocker states do not pass.
3. `auto` creates queue evidence through the launcher when possible.
4. `launch` attempts a real Codex launch only when explicitly selected.
5. `all` runs local baseline replay and then the live path.
6. The live path exits `0` only when both local baseline replay and live launch evidence satisfy the selected pass contract.
7. Any auth, provider, network, unsupported adapter, missing CLI, secret, forbidden fixture, stale handoff or Child Index mismatch is reported as `blocked`, `manual_start_required` or `failed` and exits non-zero for implementation closeout.

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `LIVE-BASELINE-REPLAY` | Prove the optional live path did not replace the accepted local baseline. | `run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-5-local-baseline`. | Exit `0`; `local_baseline_status: pass`. | `local-baseline/mock-e2e-summary.json`; `aggregate-summary.json`. | No network/auth/provider/manual-start dependency for the baseline. |
| `LIVE-AUTO-QUEUE-EVIDENCE` | Prove an automatic queue path writes launch evidence. | MD-E2E-5 handoff; Child Index after sync; `AgentDeliverySessionLauncher.cs --mode queue`. | Exit `0` only when status is `queued` or `launched`. | `launch-request.json`; `evidence.json`; `start-prompt.md`; summary launch references. | Prompt and request are secret-scrubbed; handoff path and target id match. |
| `LIVE-MANUAL-START-BLOCKED` | Ensure manual-start residue is visible but not accepted as automatic proof. | `manual-start-required` fixture. | Fixture validation passes; live closeout status is `manual_start_required`; implementation closeout remains blocked unless parent accepts manual evidence separately. | `negative-guard-evidence.json`; summary case result. | Manual status is not converted into pass. |
| `LIVE-AUTH-PROVIDER-BLOCKED` | Ensure missing auth/provider/network is represented honestly. | `blocked-auth-provider` fixture or real blocked launcher evidence. | Status `blocked`; live closeout exits non-zero. | `launch/evidence.json`; blocker list. | No placeholder success evidence; no secret values persisted. |
| `LIVE-FORBID-REAL-FIXTURE` | Prevent real product fixture regression. | `forbidden-real-fixture` fixture plus generated live evidence. | Forbidden fixture case fails as expected; harness negative guard passes. | `negative-guard-evidence.json`. | KI-fuer-KMU and real product paths cannot be source, target, write-set or positive evidence. |
| `LIVE-SUMMARY-COMPAT` | Keep local mock summary and live summary compatible but distinct. | `live-agent-summary.json`; local `mock-e2e-summary.json`. | Validator passes only when schemas and truth labels are distinct and linked. | `live-agent-summary.json`; local baseline summary. | Live summary cannot overwrite or relabel local mock summary. |
| `LIVE-NO-STANDARD-GATE-REPLACEMENT` | Ensure docs/scripts still name the mock command as standard. | README, parent specs, scripts. | Inspection/assertion passes. | Telemetry records live path as supplemental. | No standard command depends on live provider availability. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `zsh` or `bash`
- Runtime: Node.js for harness code; .NET 10 file-based app execution for launcher/evidence validators; no Docker required.

Hardening-time checks for this spec:

```sh
git diff --check
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-09\ DocWorkflow\ Agent\ Delivery\ Mock\ Data\ E2E\ Harness\ Orchestration\ Pack.md \
  --child MD-E2E-5 \
  --handoff /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/md-e2e-5-session-handoff.md \
  --allow-non-ready
```

Expected hardening-time result before parent/orchestrator sync: `ValidateChildReadiness.cs` reports a Child Index/handoff verdict mismatch because the Child Index still says `DEFERRED FOLLOW-UP`. That failure is the current sync blocker, not a runtime implementation failure.

Implementation-start command-contract rehearsal, after Child Index sync:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh
dotnet run skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/live-agent/fixtures/launch-evidence
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-5-local-baseline
```

Delivery gate:

```sh
git diff --check
bash -n tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh
tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh blocked --keep --run-id closeout-md-e2e-5-blocked
tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh all --keep --run-id closeout-md-e2e-5-all
dotnet run skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/live-agent/fixtures/launch-evidence
openspec validate docworkflow-agent-mock-e2e-md-e2e-5-live-agent-follow-up --strict
```

Closeout gate:

```sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-5-local-baseline
node tests/docworkflow-agent-delivery/e2e/live-agent/validators/live-agent-summary.js \
  tests/docworkflow-agent-delivery/e2e/evidence/live-agent-md-e2e-5-all/live-agent-summary.json
git diff --check
openspec validate docworkflow-agent-delivery-testsuite --strict
```

Success criteria:

- `git diff --check` exits `0`.
- The local mock baseline replay exits `0`.
- Blocked/manual negative cases are reported as blocked/manual and not pass.
- Queue/launch evidence validates only when handoff path, target id, provider fields and prompt evidence agree.
- The live summary validator rejects missing local baseline replay, forbidden fixture markers, secret-like content and standard-gate replacement.
- OpenSpec validates before closeout.

## Definition of Ready for Implementation

Implementation may start only after all of these are true:

1. Child Index row is updated from `DEFERRED FOLLOW-UP` to `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES`.
2. Child Index row points to `child-session-handoffs/md-e2e-5-session-handoff.md` relative to the `_specs` directory.
3. Child Index, child spec and handoff agree on the allowed write-set below.
4. `ValidateChildReadiness.cs` passes without `--allow-non-ready`.
5. A fresh Agent Delivery Session Launch/Queue Evidence run exists with status `queued`, or the handoff records `manual_start_required` or `blocked` explicitly and implementation does not start.
6. `run-mock-e2e-checks.sh all --keep` remains green and remains the standard baseline.

## Definition of Done / Closeout Evidence

Closeout requires:

- OpenSpec change created, validated and archived or explicitly left active with blocker evidence.
- New optional live command and harness implemented in the allowed write-set.
- Local mock baseline replay retained and linked.
- Live summary, launch evidence, blocked/manual negative cases, no-real-fixture scan and command telemetry retained.
- README or parent docs changed only if the parent/orchestrator explicitly adds them to a later write-set; otherwise no docs may claim live-agent success.
- Child Index and handoff synchronized after delivery; if live provider is unavailable, the closeout state remains blocked without affecting the local baseline.

## Dependencies and Write-Set

Dependencies:

- MD-E2E-1 accepted fixture and forbidden-real-fixture contract.
- MD-E2E-2 accepted local mock runner and summary schema.
- MD-E2E-3 accepted mock-only standard gate.
- MD-E2E-4 accepted docs/control-surface sync.
- Existing launcher/evidence semantics in `docs/doc-workflow.md`, `skills-repo/tools/AgentDeliverySessionLauncher.cs` and `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`.

Current hardening write-set:

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-5 Live Agent Follow-up.md`
- `_specs/child-session-handoffs/md-e2e-5-session-handoff.md`

Later implementation write-set:

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-5 Live Agent Follow-up.md`
- `_specs/child-session-handoffs/md-e2e-5-session-handoff.md`
- `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-5-live-agent-follow-up/**`
- `tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/e2e/live-agent/**`
- `tests/docworkflow-agent-delivery/e2e/evidence/live-agent-md-e2e-5-*`
- `_specs/agent-delivery-session-launches/*-md-e2e-5/**`

Shared / read-only files:

- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/e2e/mock-runner/**`
- `tests/docworkflow-agent-delivery/mock-data/**`
- `tests/docworkflow-agent-delivery/README.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md` until an integration-owner sync explicitly edits the Child Index row
- Accepted predecessor specs, handoffs, OpenSpec archives and retained evidence for MD-E2E-1 through MD-E2E-4
- KI-fuer-KMU and all other real product repositories

Parallelization:

- Hardening is not safe to treat as implementation-ready until the Child Index row is synchronized.
- Later implementation can be isolated from the local mock runner because it owns only the live-agent command, live-agent harness directory, live evidence roots and OpenSpec ledger.
- Any docs change that advertises the optional live path must be opened as a separate parent/orchestrator sync or explicitly added to a later implementation write-set.

## Closeout Sync Targets

- Child Index row for MD-E2E-5 in `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`.
- `_specs/child-session-handoffs/md-e2e-5-session-handoff.md`.
- This child spec.
- OpenSpec ledger for `docworkflow-agent-mock-e2e-md-e2e-5-live-agent-follow-up`.
- Optional README/parent docs only when explicitly authorized by the integration owner.

## Integration Owner Patch Required

Because this hardening lane is not allowed to edit the orchestration pack, the integration owner must update the MD-E2E-5 Child Index row before implementation can start. Required replacement meaning:

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MD-E2E-5 | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-5 Live Agent Follow-up.md` | `MD-PR9`; reinforces `MD-PR1`, `MD-PR6`, `MD-PR7` | `IMPLEMENTATION READY`; optional live-agent follow-up hardened; start only after fresh launch/queue evidence is created or record blocked/manual without delivery | `child-session-handoffs/md-e2e-5-session-handoff.md` | Proposed: `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-5-live-agent-follow-up/`; queue evidence required under `_specs/agent-delivery-session-launches/*-md-e2e-5/` before delivery | MD-E2E-1 through MD-E2E-4 accepted; local mock baseline replay remains required; provider/auth/network blockers do not pass | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-5 Live Agent Follow-up.md`; `_specs/child-session-handoffs/md-e2e-5-session-handoff.md`; `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-5-live-agent-follow-up/**`; `tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh`; `tests/docworkflow-agent-delivery/e2e/live-agent/**`; `tests/docworkflow-agent-delivery/e2e/evidence/live-agent-md-e2e-5-*`; `_specs/agent-delivery-session-launches/*-md-e2e-5/**` | `git diff --check`; `bash -n tests/docworkflow-agent-delivery/scripts/run-live-agent-e2e-checks.sh`; `run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-5-local-baseline`; `run-live-agent-e2e-checks.sh blocked --keep --run-id closeout-md-e2e-5-blocked`; `ValidateAgentDeliveryLaunchEvidence.cs --fixture tests/docworkflow-agent-delivery/e2e/live-agent/fixtures/launch-evidence`; `openspec validate docworkflow-agent-mock-e2e-md-e2e-5-live-agent-follow-up --strict` | Closeout must retain local baseline replay, live summary, launch evidence, blocked/manual negative cases, no-real-fixture scan and telemetry; no live path can replace `local-mock-session-runner` acceptance | If auth/provider/network is unavailable, keep MD-E2E-5 blocked/manual without impacting standard gate; docs advertising live success require separate sync | `spec-change-delivery` after Child Index sync, readiness validation and launch/queue evidence; otherwise keep blocked |

After applying the row patch, run:

```sh
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-09\ DocWorkflow\ Agent\ Delivery\ Mock\ Data\ E2E\ Harness\ Orchestration\ Pack.md \
  --child MD-E2E-5 \
  --handoff /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/md-e2e-5-session-handoff.md
```

Then create queue evidence:

```sh
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff _specs/child-session-handoffs/md-e2e-5-session-handoff.md \
  --target-id MD-E2E-5 \
  --agent codex \
  --mode queue \
  --out _specs/agent-delivery-session-launches
```

## Child Session Handoff

Persisted handoff:

- `_specs/child-session-handoffs/md-e2e-5-session-handoff.md`

The handoff currently mirrors this hardening verdict as `NEEDS PARENT/ORCHESTRATOR SYNC`. It must not be used as a `spec-change-delivery` kickoff until the Child Index row and queue evidence are synchronized.

## Content Quality Review

- Correctness/domain fit: Pass. The child stays focused on optional live evidence and keeps the accepted mock baseline primary.
- Necessity/scope: Pass. The live path exists only because `MD-PR9` explicitly allows an optional follow-up.
- Completeness: Pass for child contract depth. Command selectors, evidence fields, failure states, fixtures, write-set and closeout gates are defined.
- Consistency: Blocking sync issue. Child spec and handoff now represent a hardened sync-blocked state, while the Child Index still says deferred.
- Unambiguity: Pass. Provider/auth/network blockers are runtime states, not product decisions.
- Feasibility: Pass with blocker handling. Live launch may be blocked in a given environment, but the harness must report that honestly.
- Testability: Pass after implementation. Deterministic blocked fixtures and existing launch-evidence validator provide non-network coverage; real launch remains explicit.
- Traceability: Pass. Parent requirement coverage maps to `MD-PR9`, with guard links to `MD-PR1`, `MD-PR6` and `MD-PR7`.
- Atomicity: Pass. Runtime implementation is isolated to live-agent harness files and does not touch local mock runner files.
- Operational/lifecycle fit: Needs parent/orchestrator sync before delivery.

Blocking marker:

- `[REVIEW Child Index sync required]` The MD-E2E-5 Child Index row remains `DEFERRED FOLLOW-UP`; implementation cannot start until the integration owner applies the row patch above and readiness validation passes.

## Mini-Retro

- Was wurde entschieden? MD-E2E-5 can be hardened as an optional live-agent evidence supplement, not a standard gate replacement.
- Was wurde geaendert? The child contract now defines command selectors, evidence files, status semantics, fixtures, verification commands, write-set and sync blocker.
- Was bleibt offen? Child Index integration-owner sync and queue/launch evidence creation.
- Welche Evidenz/Verification fehlt? Readiness validator cannot pass until the Child Index row is updated; live harness commands do not exist until implementation.
- Welche Skill-/Workflow-Reibung ist aufgefallen? The original handoff was intentionally deferred, but predecessor docs now show the local baseline accepted; the safe handoff is a sync-blocked hardened candidate.
- Session-/Kontextzustand: Stop after hardening; start a fresh `spec-change-delivery` session only after Child Index sync and launch/queue evidence.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-09 | Codex | Created deferred follow-up skeleton for optional live Agent/Codex path. |
| 2026-05-09 | Codex | Hardened MD-E2E-5 as an optional live-agent follow-up contract and marked it sync-blocked pending Child Index update. |
