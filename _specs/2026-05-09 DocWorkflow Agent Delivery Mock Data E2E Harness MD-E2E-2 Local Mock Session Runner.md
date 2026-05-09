**Date:** 2026-05-09
**Status:** 🟢 Accepted
**Scope:** Hardened child spec for the local mock session runner and `run-mock-e2e-checks.sh large/small/all`.

---

## Review Control Surface

- Spec-Variante: Hardened Child Spec for Parent/Child delivery.
- Goldstandard Status: implementation-ready, consuming accepted `MD-E2E-1` fixture contracts.
- Ziel: Implement a deterministic local mock session runner that proves the large parent/child path and the small direct path without network, Docker, Codex auth, external agent providers or manual starts.
- In Scope: runner state machine, `run-mock-e2e-checks.sh` selectors, isolated run/evidence layout, generated parent/child/session artifacts, summary JSON schema/assertions, large/small output assertions, failure and blocked-state semantics, forbidden-real-fixture checks, OpenSpec proposal and closeout evidence contract.
- Out of Scope: changing accepted base fixture contracts except for an explicitly justified compatibility fix, migrating legacy standard gates (`MD-E2E-3`), README/final documentation sync (`MD-E2E-4`), live-agent/Codex execution (`MD-E2E-5`), Docker/network/auth dependencies.
- Wichtigste Test-/Harness-Cases: `MOCK-LARGE-E2E`, `MOCK-SMALL-E2E`, `MOCK-SESSION-CHAIN`, `MOCK-CHILD-WRITE-BOUNDARY`, `MOCK-FORBID-REAL-FIXTURE`, `MOCK-NEGATIVE-STATE-GUARDS`.
- Wichtigste Verification Commands: `node --version`; `node tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js tests/docworkflow-agent-delivery/mock-data`; `node tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js tests/docworkflow-agent-delivery/mock-data`; `bash -n tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh small --keep`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`; `openspec validate docworkflow-agent-mock-e2e-md-e2e-2-local-runner --strict`; `git diff --check`.
- Offene Entscheidungen: Keine blockierenden Produktentscheidungen. Implementation language is frozen to Node.js for runner logic plus a Bash wrapper, matching accepted validator style while keeping the public command shell-native.
- Readiness Status: ACCEPTED. The local mock runner, summary validator, negative guards and retained large/small/all evidence are implemented, verified and archived.

## Session Briefing

- Modus/Skill: `child-spec-hardening`.
- Source of Truth: this child spec; parent spec `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`; orchestration pack `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`; accepted MD-E2E-1 archive `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-1-mock-fixtures/`; current handoff `_specs/child-session-handoffs/md-e2e-2-session-handoff.md`.
- Target Child Goal: local runner proves workflow behavior through generated artifacts and retained evidence, not through live agents.
- Non-Goals: no legacy gate migration, no documentation final sync, no live-agent path, no real project fixture compatibility.
- Expected Deliverable: code-only implementation slice with a Bash command entrypoint, Node runner/validators under `tests/docworkflow-agent-delivery/e2e/**`, retained evidence for large/small/all runs, and OpenSpec closeout evidence.
- Verification/Review Path: OpenSpec proposal validation, MD-E2E-1 fixture validators, command gates, summary assertions, retained evidence inspection, readiness validator replay and `git diff --check`.

## Parent Coverage

| Parent Requirement | Coverage | Conformance | MD-E2E-2 Contract |
|---|---|---|---|
| `MD-PR1` mock fixtures only; real product fixtures forbidden | Consumes accepted policy and validator from MD-E2E-1. | preserves | Every runner mode invokes the forbidden-real-fixture validator against fixture roots, generated run roots, summaries, session evidence and write-set metadata. |
| `MD-PR2` large parent fixture with five children | Consumes accepted `large-parent/manifest.json`. | preserves | Large selector must read the accepted manifest and may not synthesize a different child list or output contract. |
| `MD-PR3` small direct fixture with no child artifacts | Consumes accepted `small-direct/manifest.json`. | preserves | Small selector must validate absence of child index/specs/handoffs/session queue. |
| `MD-PR4` local runner drives large path | Owns implementation. | preserves | Runner materializes sizing, parent control, five child sessions, closeout gates, count output and summary. |
| `MD-PR5` local runner drives small direct path | Owns implementation. | preserves | Runner materializes direct delivery, direct output and no child-control artifacts. |
| `MD-PR6` machine-readable evidence | Owns schema details. | extends | This spec freezes run layout, session evidence, state machine and summary v1 assertions. |
| `MD-PR7` standard gate migration | Not owned. | defers_to_child | `MD-E2E-3` later wires this runner into standard gates; MD-E2E-2 must not edit legacy defaults. |
| `MD-PR8` documentation sync | Not owned. | defers_to_child | `MD-E2E-4` documents accepted evidence after implementation. |
| `MD-PR9` optional live-agent path | Explicitly out of scope. | preserves | Runner mode is `local-mock-session-runner`; live-agent evidence cannot replace this baseline. |

No parent requirement is contradicted. Fixture contracts from `MD-E2E-1` are read-only inputs except for a documented compatibility fix that keeps the accepted manifest semantics intact.

## Accepted Input Contracts

MD-E2E-2 must consume these accepted files as normative inputs:

- `tests/docworkflow-agent-delivery/mock-data/large-parent/manifest.json`
- `tests/docworkflow-agent-delivery/mock-data/large-parent/mock-large-parent-spec.md`
- `tests/docworkflow-agent-delivery/mock-data/large-parent/mock-target/README.md`
- `tests/docworkflow-agent-delivery/mock-data/small-direct/manifest.json`
- `tests/docworkflow-agent-delivery/mock-data/small-direct/mock-small-direct-spec.md`
- `tests/docworkflow-agent-delivery/mock-data/small-direct/mock-target/README.md`
- `tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js`
- `tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js`

Normative large manifest values:

- `fixture_id`: `mock-large-parent-v1`
- `spec_type`: `large-parent`
- `expected_delivery_mode`: `parent_child`
- `runner_mode`: `local-mock-session-runner`
- `session_strategy`: `auto-start-and-resume`
- `mock_sizing_directive`: `force_parent_child`
- `expected_children`: exactly `ML-C1`, `ML-C2`, `ML-C3`, `ML-C4`, `ML-C5`
- `expected_outputs`: `mock-target/output/count.txt`
- `expected_output_content`: exactly `1\n2\n3\n4\n5\n`

Normative small manifest values:

- `fixture_id`: `mock-small-direct-v1`
- `spec_type`: `small-direct`
- `expected_delivery_mode`: `direct`
- `runner_mode`: `local-mock-session-runner`
- `session_strategy`: `direct-no-child-session`
- `expected_children`: empty list
- `expected_outputs`: `mock-target/output/small-direct-result.json`
- `expected_output_json`: `{ "mode": "direct", "result": "ok", "source": "mock-small-direct" }`

## Runner Architecture

Public entrypoint:

- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`

Implementation language:

- Bash wrapper for selector parsing, cwd checks and consistent exit codes.
- Node.js runner modules under `tests/docworkflow-agent-delivery/e2e/` for JSON parsing, filesystem checks, state transition validation and summary assertions.
- No npm install, network access, Docker daemon, Codex CLI invocation or external provider dependency is allowed.

Required selectors:

| Selector | Required Behavior | Passing Exit | Failure Exit |
|---|---|---|---|
| `large` | Run only `mock-large-parent-v1`, retain summary and session/output evidence when `--keep` is present. | `0` iff large summary is `pass` and all large assertions pass. | Non-zero for any invalid state, output mismatch, forbidden fixture, missing artifact or external dependency attempt. |
| `small` | Run only `mock-small-direct-v1`, retain summary/output evidence when `--keep` is present. | `0` iff small summary is `pass` and no child-control artifacts exist. | Non-zero for split artifacts, output mismatch, forbidden fixture or invalid sizing. |
| `all` | Run `large` then `small` in separate isolated run roots and write an aggregate summary. | `0` iff both child runs pass and aggregate summary is `pass`. | Non-zero if either sub-run fails or aggregate evidence cannot be written. |

Required flags:

| Flag | Behavior |
|---|---|
| `--keep` | Preserve the run root under `tests/docworkflow-agent-delivery/e2e/evidence/<run-id>/` and print the retained summary path. |
| no `--keep` | May use a temporary run root, but must still validate all assertions before exit. |
| `--run-id <id>` | Optional deterministic run id for tests; id must match `^[A-Za-z0-9._-]+$` and must not allow path traversal. |
| `--help` | Print selector/flag usage and exit `0`. |

Unknown selector, unknown flag, invalid `--run-id`, missing fixture, or unsupported cwd must exit non-zero before mutating fixture inputs.

## State Machine

The runner must model each workflow step as a state transition and record the transition history. State names are lowercase strings.

Allowed launch states:

| State | Meaning | Positive For Large E2E |
|---|---|---|
| `started` | Step began automatically from the runner. | Yes, as an intermediate state. |
| `queued` | Step was queued for automatic resume. | Intermediate only; must transition to `resumed` before pass. |
| `resumed` | Previously queued step was resumed automatically by the runner. | Yes, as an intermediate state. |
| `manual_start_required` | A human start would be needed. | Never. |
| `blocked` | Expected blocker occurred in a negative case. | Only in explicit negative cases. |
| `failed` | Unexpected failure occurred. | Never. |

Allowed completion states:

| State | Meaning | Positive For Large E2E |
|---|---|---|
| `ran-target` | Step wrote and validated its assigned target output. | Required for each `ML-C*` delivery. |
| `closed` | Step closeout synchronized index, handoff, output and summary pointers. | Required after `ran-target` before the next child can start. |
| `blocked` | Expected negative-case blocker completed. | Only in explicit negative cases. |
| `failed` | Unexpected failure completed. | Never. |

Large-path transition contract:

1. `parent-control`: `started -> ran-target -> closed`.
2. For each child `ML-C1` through `ML-C5`, in sequence:
   - either `started -> ran-target -> closed`, or `queued -> resumed -> ran-target -> closed`;
   - `ML-C(n+1)` may not enter `started`, `queued` or `resumed` until `ML-Cn` has `closed`;
   - `manual_start_required`, permanent `queued`, `blocked`, `failed` or `ran-rehearsal` cannot pass the leading large E2E.
3. `large-final-validation`: `started -> ran-target -> closed` after `ML-C5` is closed.

Small-path transition contract:

1. `direct-delivery`: `started -> ran-target -> closed`.
2. No `ML-C*` session evidence, child queue, child handoff or child spec may exist.

Negative state guard contract:

- Negative tests may inject invalid evidence under `tests/docworkflow-agent-delivery/e2e/fixtures/**` or generated run-root subdirectories.
- A negative case passes only when the runner returns non-zero or records `overall_workflow_status: blocked` with `expected_negative_case: true`.
- A negative case must never produce `overall_workflow_status: pass`.

## Evidence Directory Layout

With `--keep`, retained evidence must live under:

```text
tests/docworkflow-agent-delivery/e2e/evidence/<run-id>/
  mock-e2e-summary.json
  aggregate-summary.json              # only for selector all
  command-telemetry.json
  forbidden-real-fixture.json
  large/
    mock-e2e-summary.json
    parent-control/
      parent-control-summary.json
      child-index.md
      child-specs/ML-C1.md
      child-specs/ML-C2.md
      child-specs/ML-C3.md
      child-specs/ML-C4.md
      child-specs/ML-C5.md
      handoffs/ML-C1-handoff.md
      handoffs/ML-C2-handoff.md
      handoffs/ML-C3-handoff.md
      handoffs/ML-C4-handoff.md
      handoffs/ML-C5-handoff.md
    sessions/
      ML-C1-delivery.json
      ML-C2-delivery.json
      ML-C3-delivery.json
      ML-C4-delivery.json
      ML-C5-delivery.json
    mock-target/
      output/count.txt
    output-evidence/count.txt.sha256
  small/
    mock-e2e-summary.json
    direct-delivery.json
    mock-target/
      output/small-direct-result.json
    output-evidence/small-direct-result.json.sha256
```

Selector-specific runs may omit the sibling selector directory. `all --keep` must create both `large/` and `small/` and a root `aggregate-summary.json`.

Run ids:

- Default format: UTC timestamp plus selector, for example `20260509T071500Z-large`.
- The runner must reject run ids containing `/`, `\`, `..`, control characters or shell metacharacters.
- Evidence paths in summaries must be relative to the retained run root unless an absolute path is explicitly required by the schema; `mock_target_root` must be absolute.

## Session Evidence Schema

Each `sessions/<child-id>-delivery.json` file must be parseable JSON with these required fields:

| Field | Type / Allowed Values | Assertion |
|---|---|---|
| `schema_id` | `docworkflow-agent-delivery-mock-session.v1` | Exact match. |
| `fixture_id` | `mock-large-parent-v1` | Exact match for large. |
| `session_step_id` | `ML-C1-delivery` through `ML-C5-delivery` | Must match filename and child id. |
| `target_child_id` | `ML-C1` through `ML-C5` | Exact sequence. |
| `sequence_index` | integer `1` through `5` | Strictly increasing by one. |
| `source_handoff` | relative path under `large/parent-control/handoffs/` | File must exist. |
| `launch_status` | `started`, `queued`, `manual_start_required`, `blocked`, `failed` | `queued` requires a later `resumed` transition. |
| `launch_mechanism` | `local-mock-session-runner` or `local-mock-session-runner-queue` | No live-agent mechanism in this child. |
| `state_transitions` | array of `{ "state": "...", "at": "..." }` | Must satisfy the state machine. |
| `target_workspace` | absolute path under this run root | Must not point to repo root or real product repo. |
| `allowed_write_set` | array of relative paths | Must be scoped to this child output, this session evidence and closeout files. |
| `forbidden_paths_checked` | array | Must include accepted MD-E2E-1 forbidden paths. |
| `result_evidence` | object | Must link output, summary and closeout evidence. |
| `final_status` | `ran-target`, `closed`, `blocked`, `failed` | Positive large delivery must include `ran-target` and closeout must mark `closed`. |
| `closeout_status` | `closed`, `blocked`, `failed` | Must be `closed` before next child starts. |
| `child_output_action` | `append_or_set_line:1` through `append_or_set_line:5` | Must match accepted manifest contract. |
| `write_boundary_status` | `pass`, `fail` | Must be `pass` for positive cases. |
| `external_dependency_status` | `not_used`, `attempted` | Must be `not_used`. |

## Summary JSON Schema And Assertions

Every selector writes `mock-e2e-summary.json` using schema id `docworkflow-agent-delivery-mock-e2e-summary.v1`.

Required summary fields:

| Field | Type / Allowed Values | Required Assertion |
|---|---|---|
| `schema_id` | exact string | `docworkflow-agent-delivery-mock-e2e-summary.v1`. |
| `run_id` | string | Matches run directory name. |
| `selector` | `large`, `small`, `all` | Matches command selector. |
| `fixture_id` | fixture id or `mock-e2e-all-v1` | Large/small exact; all aggregate id. |
| `fixture_version` | string | Mirrors manifest for large/small. |
| `spec_type` | `large-parent`, `small-direct`, `aggregate` | Matches selector. |
| `sizing_decision` | `parent_child`, `direct`, `blocked`, `failed`, `aggregate` | Large must be `parent_child`; small must be `direct`. |
| `overall_workflow_status` | `pass`, `fail`, `blocked` | `pass` only if all selector assertions pass. |
| `session_chain_status` | `pass`, `fail`, `blocked`, `not_applicable` | Large `pass`; small `not_applicable`; all `pass` only if sub-runs pass. |
| `expected_outputs_status` | `pass`, `fail`, `blocked` | Positive selectors require `pass`. |
| `forbidden_fixture_status` | `pass`, `fail` | Positive selectors require `pass`. |
| `evidence_truth` | `ran-target`, `blocked`, `failed` | Positive selectors require `ran-target`; `ran-rehearsal` is not allowed. |
| `runner_mode` | `local-mock-session-runner` | Exact match for accepted baseline. |
| `session_strategy` | `auto-start-and-resume`, `direct-no-child-session`, `aggregate`, `negative-blocker` | Must match fixture or aggregate. |
| `mock_target_root` | absolute path or object for aggregate | Large/small path must exist under run root. |
| `session_evidence` | array | Large has five session files; small has empty array. |
| `output_evidence` | array | Contains validated output file paths and hashes. |
| `forbidden_paths_checked` | array | Includes accepted forbidden path patterns. |
| `generated_artifacts` | object | Records child index/spec/handoff counts. |
| `external_dependencies` | object | `network`, `docker`, `codex_auth`, `manual_start` all `not_used`. |
| `negative_cases` | array | Empty for positive large/small unless selector explicitly runs negative fixtures. |

Pass assertions:

- `overall_workflow_status: pass` is forbidden if any expected output is missing, mismatched or un-hashed.
- `overall_workflow_status: pass` is forbidden if forbidden-real-fixture validation fails for input fixtures, generated artifacts, summaries, session evidence, command telemetry or write-set metadata.
- `overall_workflow_status: pass` is forbidden if any large session ends in `queued`, `manual_start_required`, `blocked`, `failed` or lacks `closed`.
- `overall_workflow_status: pass` is forbidden if `evidence_truth` is `ran-rehearsal`.
- `overall_workflow_status: pass` is forbidden if command telemetry records network, Docker, Codex auth, external provider or manual launch usage.

Aggregate summary assertions:

- `aggregate-summary.json` must list `large_summary`, `small_summary`, `large_status`, `small_status`, `overall_workflow_status`, `forbidden_fixture_status`, `created_at`, `runner_mode` and `schema_id: docworkflow-agent-delivery-mock-e2e-aggregate.v1`.
- `all` exits `0` only if both sub-summaries pass and the aggregate summary passes its own schema assertions.

## Generated Artifact Contracts

Large parent-control artifacts:

- `child-index.md` must include exactly five rows for `ML-C1` through `ML-C5`.
- Each row must include child id, target output action, predecessor, readiness state, handoff path, allowed write-set and final state.
- Child specs are generated evidence artifacts, not real project child specs. Each generated child spec must state:
  - source fixture id,
  - child id,
  - required number,
  - allowed write-set,
  - expected session evidence file,
  - no external dependencies.
- Handoffs are generated evidence artifacts. Each generated handoff must point to its matching child spec, mock target root, session evidence path and write-set.

Small direct artifacts:

- The small run must not create `child-index.md`, `child-specs/**`, `handoffs/**`, `child-session-handoffs/**` or `sessions/ML-C*.json`.
- `direct-delivery.json` must record `schema_id: docworkflow-agent-delivery-mock-direct.v1`, `fixture_id: mock-small-direct-v1`, `sizing_decision: direct`, `final_status: ran-target`, `child_artifact_status: absent`, and output evidence.

## Output Assertions

Large:

- `large/mock-target/output/count.txt` must exist.
- File content must be exactly `1\n2\n3\n4\n5\n`.
- SHA-256 evidence must be written to `large/output-evidence/count.txt.sha256`.
- Each child session must prove exactly one line/action:
  - `ML-C1`: writes line `1`
  - `ML-C2`: writes line `2`
  - `ML-C3`: writes line `3`
  - `ML-C4`: writes line `4`
  - `ML-C5`: writes line `5`
- A child cannot rewrite, delete, reorder or prefill another child's line.

Small:

- `small/mock-target/output/small-direct-result.json` must exist.
- It must parse as JSON exactly equivalent to `{ "mode": "direct", "result": "ok", "source": "mock-small-direct" }`.
- SHA-256 evidence must be written to `small/output-evidence/small-direct-result.json.sha256`.
- Child artifact counts must all be zero.

## Failure And Blocked States

The runner must distinguish implementation/test failure from an expected negative blocker:

| Condition | Summary Status | Exit Code | Required Evidence |
|---|---|---|---|
| Positive large or small passes | `pass` | `0` | Summary, output evidence, forbidden validator pass; large also has five closed sessions. |
| Output mismatch | `fail` | non-zero | Summary with expected/actual digest or content class, without leaking unrelated file contents. |
| Forbidden real fixture path | `fail` | non-zero | Forbidden validator findings path and offending field. |
| Permanent `queued` | `fail` | non-zero | Session evidence names the stuck child. |
| `manual_start_required` in positive run | `fail` | non-zero | Session evidence names the child and mechanism. |
| `blocked` in positive run | `fail` | non-zero | Summary says unexpected blocked state. |
| Expected negative fixture blocker | `blocked` | `0` only for an explicit negative selector/case | `expected_negative_case: true`; no positive pass summary. |
| External dependency attempted | `fail` | non-zero | Command telemetry names the dependency class, not secrets. |
| Missing accepted fixture | `blocked` | non-zero | Preflight evidence names missing path. |

MD-E2E-2 does not need a public negative selector, but its implementation must include internal negative assertions or validator fixtures proving that positive `pass` cannot be produced for `manual_start_required`, permanent `queued`, `blocked`, `failed`, output mismatch and forbidden fixture states.

## Allowed Write-Set

Implementation may edit only:

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-2 Local Mock Session Runner.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`
- `_specs/child-session-handoffs/md-e2e-2-session-handoff.md`
- `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/**`
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/e2e/mock-runner/**`
- `tests/docworkflow-agent-delivery/e2e/validators/mock-e2e-summary.js`
- `tests/docworkflow-agent-delivery/e2e/fixtures/mock-runner-negative/**`
- `tests/docworkflow-agent-delivery/e2e/evidence/**` only for retained MD-E2E-2 implementation evidence
- `tests/docworkflow-agent-delivery/mock-data/**` only for an accepted MD-E2E-1 compatibility fix that is explicitly documented in this child's implementation evidence and does not change the fixture semantics listed above

Shared / read-only files:

- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`
- `tests/docworkflow-agent-delivery/README.md`
- `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` until MD-E2E-3 or MD-E2E-4 sync explicitly owns canonical updates
- accepted MD-E2E-1 archive files
- existing DWT L1/L2/L3/reporting harnesses and retained evidence
- KI-fuer-KMU and all other real product repositories

## Acceptance And Harness Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `MOCK-LARGE-E2E` | Prove parent/child flow through five local sessions. | `mock-large-parent-v1` manifest/spec/target. | Exit `0`; summary `pass`; `sizing_decision: parent_child`; `evidence_truth: ran-target`. | Large summary, parent-control artifacts, five session JSON files, `count.txt`, hash evidence, forbidden validator pass. | No real fixture path, no network/Docker/Codex/manual start, no `ran-rehearsal`. |
| `MOCK-SMALL-E2E` | Prove small direct delivery with no split. | `mock-small-direct-v1` manifest/spec/target. | Exit `0`; summary `pass`; `sizing_decision: direct`; `session_chain_status: not_applicable`. | Small summary, direct-delivery evidence, output JSON, hash evidence. | Child index/spec/handoff/session artifacts absent. |
| `MOCK-SESSION-CHAIN` | Prove sequence and closeout gates. | Large run session evidence. | `pass` only after each child closes before next starts. | `ML-C1` through `ML-C5` session files with ordered transitions. | Permanent queue, manual start, blocked or failed state cannot pass. |
| `MOCK-CHILD-WRITE-BOUNDARY` | Prove each child owns only its number. | Large run output action evidence. | `pass` only if each `child_output_action` matches manifest. | Count output plus per-child action evidence. | Rewriting another child's line fails. |
| `MOCK-FORBID-REAL-FIXTURE` | Preserve MD-E2E-1 real-fixture ban. | Accepted forbidden validator plus generated run root. | Positive run exits `0` only when validator status is `pass`; negative fixtures fail. | `forbidden-real-fixture.json` and summary field. | No secrets or real repo paths beyond named forbidden patterns in findings. |
| `MOCK-NEGATIVE-STATE-GUARDS` | Prove bad states cannot create pass summaries. | Generated negative evidence fixtures. | Non-zero or explicit `blocked` negative case; never positive pass. | Negative case evidence under runner fixtures or retained run root. | `manual_start_required`, permanent `queued`, `blocked`, `failed`, output mismatch and external dependency attempts are covered. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `zsh` or `bash`; scripts use `#!/usr/bin/env bash`.
- Runtime: Node.js only, matching accepted MD-E2E-1 validators. No package install is required.
- Platform: macOS primary, POSIX-compatible Bash/Node filesystem behavior preferred.

Pre-implementation/hardening checks:

```sh
node --version
node tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js tests/docworkflow-agent-delivery/mock-data
node tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js tests/docworkflow-agent-delivery/mock-data
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md" --child MD-E2E-2 --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/md-e2e-2-session-handoff.md"
openspec validate docworkflow-agent-mock-e2e-md-e2e-2-local-runner --strict
git diff --check
```

Delivery gate after implementation:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh small --keep
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep
git diff --check
```

Closeout evidence requirements:

- retain the `--keep` evidence paths for `large`, `small` and `all`;
- record the exact summary paths in `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/implementation-evidence.md`;
- include failure/blocked-state negative evidence;
- include forbidden-real-fixture validator evidence over generated run roots;
- rerun `ValidateChildReadiness.cs` and `openspec validate ... --strict` before archive.

## OpenSpec Change Proposal

Ledger id:

- `docworkflow-agent-mock-e2e-md-e2e-2-local-runner`

Required proposal files before implementation:

- `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/proposal.md`
- `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/design.md`
- `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/tasks.md`
- `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/scope-contract.md`
- `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/specs/docworkflow-agent-delivery-testsuite/spec.md`

The OpenSpec delta must add requirements for:

- local mock E2E runner selectors,
- large parent/child state chain,
- small direct no-child path,
- summary/evidence schema,
- forbidden real fixture enforcement in generated evidence,
- no external dependency baseline.

## Handoff / Child Index Sync

Before implementation starts:

- this child spec status must be `IMPLEMENTATION READY`;
- the Child Index row for `MD-E2E-2` must point to this spec, this handoff and the active OpenSpec change id;
- `_specs/child-session-handoffs/md-e2e-2-session-handoff.md` must mirror the verdict, write-set, verification commands and OpenSpec id;
- queue evidence `_specs/agent-delivery-session-launches/20260509T062536Z-md-e2e-2/evidence.json` remains retained hardening-start evidence, not implementation closeout evidence.

After implementation closeout:

- update the Child Index row to `ACCEPTED` only after OpenSpec archive and retained evidence exist;
- do not release `MD-E2E-3` until MD-E2E-2 large/small/all evidence is linked;
- documentation sync and README updates remain `MD-E2E-4` unless MD-E2E-3 explicitly owns a command reference update.

## Closeout Result

- Closeout Verdict: ACCEPTED.
- OpenSpec Archive: `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/`.
- Canonical OpenSpec Spec: `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`.
- Closeout Evidence:
  - Large: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-large/mock-e2e-summary.json`
  - Small: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-small/mock-e2e-summary.json`
  - All: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-all/aggregate-summary.json`
  - Implementation evidence: `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/implementation-evidence.md`
- Verification Replay: `node --version`; manifest schema validator; forbidden-real-fixture validator over mock data and generated closeout roots; `bash -n tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `run-mock-e2e-checks.sh large/small/all --keep --run-id closeout-md-e2e-2-*`; summary validator over retained summaries; `openspec validate docworkflow-agent-delivery-testsuite --strict`; `git diff --check`.
- Documentation Scope: README/final docs sync remains deferred to `MD-E2E-4`; standard gate migration remains `MD-E2E-3`.

## Content Quality Review

- Correctness/domain fit: Pass. The spec tests Agent Delivery workflow mechanics with accepted synthetic fixtures and does not widen into product implementation.
- Necessity/scope: Pass. Runner, state machine, evidence and summary contracts are required before standard-gate migration can safely consume `run-mock-e2e-checks.sh`.
- Completeness: Pass. Large/small selectors, state transitions, evidence tree, summary schema, outputs, failure states, forbidden fixtures, write-set, verification and OpenSpec proposal are concrete.
- Consistency: Pass. Fixture ownership remains with accepted MD-E2E-1; standard migration/docs/live-agent work remains in later children.
- Testability: Pass. Every positive and negative behavior has a command, summary assertion or retained evidence requirement.
- Implementation planning readiness: Pass with explicit command timing. The future runner script cannot be executed before implementation because it is the deliverable; the implementation gate must run syntax, large, small and all selectors before closeout.
- Blocking Marker: None.

## Mini-Retro

- Was wurde entschieden? MD-E2E-2 uses a Bash wrapper plus Node runner/validators, writes retained local evidence, and treats live agents as out of scope.
- Was wurde geaendert? The skeleton now contains a complete state machine, evidence layout, summary contract, output assertions, negative-state rules, write-set and OpenSpec proposal.
- Was bleibt offen? Runtime implementation and closeout evidence belong to the next `spec-change-delivery` session.
- Welche Evidenz/Verification fehlt? Functional `run-mock-e2e-checks.sh` evidence is not possible before implementation; this is now a delivery gate, not a hardening blocker.
- Welche Skill-/Workflow-Reibung ist aufgefallen? Future command rehearsal is awkward for file-creation slices; the spec freezes command contract now and requires immediate rehearsal after the script is created.
- Session-/Kontextzustand: Hardened and ready for implementation handoff.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-09 | Codex | Initial child skeleton created by orchestration. |
| 2026-05-09 | Codex | Hardened MD-E2E-2 to implementation-ready with runner state machine, selectors, evidence layout, summary schema, output assertions, failure semantics, write-set, verification and OpenSpec proposal. |
| 2026-05-09 | Codex | Implemented local mock session runner, summary validator, negative guards and retained large/small/all evidence. |
| 2026-05-09 | Codex | Accepted MD-E2E-2 after closeout verification replay, OpenSpec archival and Child Index evidence sync. |

SessionId: 2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner
