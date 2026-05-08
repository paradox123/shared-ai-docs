**Date:** 2026-05-08
**Status:** 🟢 Accepted
**Scope:** Accepted child spec for the DWT-S3 L2 Single-Child Delivery and Closeout Gate Harness.

---

## Review Control Surface

- Spec-Variante: implementation-ready Child Spec.
- Goldstandard Status: candidate.
- Ziel: Einen L2-Harness definieren, der nachweist, dass `spec-change-delivery` genau einen implementation-ready Child aus einem frischen Handoff in einem isolierten Temp-Workspace starten darf und dass `spec-closeout` Parent/Index/Evidence/OpenSpec/Handoff synchronisiert, ohne DWT-S5 automatisch freizugeben.
- In Scope: L2 Single-Child Delivery-/Closeout-Gate-Vertrag, Promptfoo-first Codex-Probe mit S0-Limitations, fallback artifact runner for blocked-agent evidence, DWT-S2 `ran-target` dependency input, DWT-S3-ready kickoff fixture, stale-handoff negative fixture, synthetic closeout fixture, DWT-S5-blocked next-child fixture, parent-coverage-preservation assertion, DWT-S4-compatible summary/telemetry/style evidence, OpenSpec active change, Parent Child Index and persisted handoff sync.
- Out of Scope: DWT-S3 runner implementation during hardening, live agent execution during hardening, runtime delivery, Docker or container execution, DWT-S5 runtime pilot implementation or release, mutation of accepted DWT-S0/DWT-S1/DWT-S2/DWT-S4 archives, KI-fuer-KMU original repo writes, OpenSpec archive before DWT-S3 implementation evidence exists.
- Wichtigste Test-/Harness-Cases: `DWT-S3-L2A ready child delivery kickoff is temp-workspace only`, `DWT-S3-L2B stale or mismatched DWT-S3 handoff blocks delivery`, `DWT-S3-L2C closeout sync preserves Parent Coverage and accepted evidence links`, `DWT-S3-L2D DWT-S5 remains blocked after DWT-S3 closeout`, `DWT-S3-L2E blocked agent path is reported as blocker rather than pass`, `DWT-S3-L2F DWT-S4 reporting/style/efficiency contract is honored`.
- Wichtigste Verification Commands: retained DWT-S2 evidence presence, JSON parse and status assertions; retained DWT-S2 manifest parse and sha presence assertions; `bash -n` for existing L0/L1/L2-S2/reporting scripts; active-change `openspec validate docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness --strict`; canonical `openspec validate docworkflow-agent-delivery-testsuite --strict`; DWT-S3 `ValidateChildReadiness.cs`; `git diff --check`; after implementation, `bash -n tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh`, `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh all --keep`, `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all`, and `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen. Promptfoo remains the primary L2 agent-runner path from DWT-S0 and DWT-S2. Fallback artifact mode may only produce deterministic contract evidence or a reproducible blocked-agent result, never a false accepted proof. DWT-S5 remains blocked until its own later hardening/handoff gates pass.
- Readiness Status: ACCEPTED and archived. DWT-S5 remains blocked.

## Goal

Create the implementation contract for an L2 Single-Child Delivery and Closeout Gate Harness. The harness must prove that a delivery session cannot start from stale or approximate child-control artifacts, cannot write outside its isolated temp workspace, and cannot release the next child during closeout unless that next child has its own implementation-allowing verdict.

The implementation must distinguish three outcomes:

- `pass`: a real agent/coding-agent run exercised the DWT-S3 delivery and closeout control flow in an isolated fixture and deterministic validators accepted the resulting evidence.
- `blocked`: the agent path could not run for a reproducible auth, provider, runtime or network reason, and fallback artifact mode proved only deterministic contracts.
- `fail`: the agent or artifact output used a stale handoff, wrote outside the temp workspace, skipped readiness validation, dropped Parent Coverage, hid evidence, released DWT-S5, leaked secrets, or violated style/efficiency gates.

## In Scope

- Add source-controlled DWT-S3 L2 fixture definitions under `tests/docworkflow-agent-delivery/l2/single-child-closeout/fixtures/`.
- Add DWT-S3 L2 validators under `tests/docworkflow-agent-delivery/l2/single-child-closeout/validators/`.
- Add primary Promptfoo/Codex runner config and command wrapper under `tests/docworkflow-agent-delivery/l2/single-child-closeout/`.
- Add fallback artifact runner mode to validate stored kickoff and closeout output bundles when the agent runner is blocked.
- Add `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh`.
- Emit DWT-S4-compatible summary and telemetry artifacts for DWT-S3.
- Update `tests/docworkflow-agent-delivery/README.md` and `tests/docworkflow-agent-delivery/testcases/tc2-single-child-delivery-next-handoff.md` with the DWT-S3 L2 boundary.
- Keep original KI-fuer-KMU specs and runtime repositories read-only.

## Out of Scope

- No DWT-S3 implementation during this hardening run.
- No live agent run during this hardening run.
- No runtime delivery, Docker, deployment, credential copying into repo files or KI-fuer-KMU original repo writes.
- No DWT-S5 runtime temp-repo delivery pilot.
- No DWT-S5 release or implementation handoff.
- No mutation of accepted DWT-S0, DWT-S1, DWT-S2 or DWT-S4 archives.
- No OpenSpec archive until DWT-S3 implementation evidence exists and closeout runs.

## Parent/Master Coverage

| Parent Requirement | Child Coverage |
|---|---|
| `DWT-PR3` | Owns the proof that single-child delivery starts only from the current DWT-S3 child spec, Parent Child Index row, implementation-allowing verdict, persisted handoff, concrete write-set and isolated temp workspace. |
| `DWT-PR4` | Owns the proof that DWT-S3 closeout synchronizes Parent Child Index, evidence links, OpenSpec ledger and next-child state while keeping DWT-S5 blocked. |
| `DWT-PR5` | Requires provenance, retained S2 evidence identity, source hashes or stable manifest ids, DWT-S4 evidence truth labels, no stale output reuse and no fallback-as-pass substitution. |
| `DWT-PR7` | Emits DWT-S4-compatible style and efficiency telemetry for agent/tool/read behavior, stale handoff detection and follow-up usability. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `DWT-PR3` | Delivery kickoff must validate Child Index, handoff, verdict, write-set and target workspace before any edit-like action. | preserves | Implement a DWT-S3 L2 runner plus validators for fresh kickoff output, stale handoff output, target workspace isolation and allowed write-set enforcement. |
| `DWT-PR4` | Closeout must synchronize Parent/Index/Evidence/OpenSpec/Handoff and then evaluate the next child by that child's own state. | preserves | Implement synthetic closeout fixtures and validators that require DWT-S3 sync while keeping DWT-S5 blocked. |
| `DWT-PR5` | DWT-S3 evidence must distinguish real agent output, fallback artifact validation, stale copied outputs and blocked provider/auth/network cases. | preserves | Require retained DWT-S2 evidence links, source manifest references, summary truth labels and blocked-agent status fields. |
| `DWT-PR7` | DWT-S3 must make style/usability and efficiency drift machine-readable, not prose-only. | preserves | Emit `agent-run-manifest.json`, style verdicts and efficiency verdicts compatible with DWT-S4. |
| `DWT-PR1` | DWT-S3 consumes accepted DWT-S2 parent-first output but does not re-prove orchestration. | narrows_with_rationale | DWT-S2 remains responsible for parent-first orchestration proof. |
| `DWT-PR2` | DWT-S3 validates readiness gates as an input but does not redefine child-hardening semantics. | narrows_with_rationale | DWT-S1 and `ValidateChildReadiness.cs` remain the deterministic readiness baseline; this child consumes them for DWT-S3. |
| `DWT-PR6` | DWT-S3 reuses the Promptfoo-first decision and does not reopen framework research. | narrows_with_rationale | DWT-S0 remains the framework evidence source. |

## Decision Freeze Pack

| Entscheidung | Freeze |
|---|---|
| Primary agent runner | Promptfoo `0.121.9` with bundled Node `v24.14.0`, reusing the accepted DWT-S0 and DWT-S2 command contract and explicit auth/network limitations. |
| Fallback runner | Deterministic artifact mode under the DWT-S3 script validates stored kickoff/closeout output bundles and may report `blocked_agent`; it cannot produce a DWT-S3 acceptance `pass` without `agent_execution_status: ran-target`. |
| Required predecessor proof | DWT-S3 implementation must read retained DWT-S2 summary `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-l2-summary.json` and manifest `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/manifest.json`; `runner_mode` must be `promptfoo-codex`, `agent_execution_status` must be `ran-target`, and `overall_agent_proof_status` must be `pass`. |
| Required proof shape | A fresh DWT-S3 kickoff must use the DWT-S3 child spec, Parent Child Index row, persisted DWT-S3 handoff and isolated temp workspace; DWT-S3 closeout must preserve Parent Coverage and accepted evidence links. |
| Output status vocabulary | `pass`, `fail`, `blocked`, `warn`, `planned`. |
| Evidence truth vocabulary | `ran-target`, `ran-rehearsal`, `blocked`, `failed`, `planned`, `dry-run`. |
| Agent execution status vocabulary | `ran-target`, `blocked_auth`, `blocked_provider`, `blocked_network`, `blocked_runtime`, `failed`, `not-run`. |
| Next child state vocabulary | `blocked_by_dependency`, `ready_for_hardening`, `needs_hardening`, `needs_user_decision`, `implementation_ready`, `accepted`. |
| Reporting contract | New DWT-S3 summaries use `schema_id: docworkflow-agent-delivery-summary.v1` and DWT-S4 telemetry/style/efficiency semantics. |
| Original repos | KI-fuer-KMU original specs and runtime repositories remain read-only. |
| Descendant release | DWT-S3 may release only its own implementation evidence and closeout sync. DWT-S5 remains blocked until its own later hardening and handoff gates pass. |

## Normative Contract

### L2 Runner Modes

The DWT-S3 implementation must provide `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh` with these selectors:

| Selector | Required Behavior |
|---|---|
| `all` | Runs all DWT-S3 L2A-L2F assertions and writes a DWT-S3 summary. |
| `agent` | Uses Promptfoo/Codex when credentials/provider/runtime are provisioned; stores raw output, telemetry and deterministic validation output. |
| `fallback` | Uses stored artifact fixtures only; may prove validator behavior and blocked-agent reporting, but cannot mark DWT-S3 accepted as agent proof. |
| `validate-output` | Validates an existing DWT-S3 output bundle path without launching an agent. |
| `closeout` | Validates synthetic closeout output, Parent Coverage preservation, OpenSpec/ledger sync fields and DWT-S5 blocked state. |
| `style` | Runs DWT-S4-compatible style/usability assertions for DWT-S3 output. |
| `telemetry` | Runs DWT-S4-compatible efficiency/telemetry assertions for DWT-S3 output. |

The runner must accept `--run-dir DIR`, `--keep`, and `--output-bundle DIR` where applicable. Every run must write evidence under `<run-dir>/evidence/`.

### Agent Prompt Contract

The primary agent prompt must:

- provide the parent/master spec path, DWT-S3 child spec path, Parent Child Index path, DWT-S3 handoff path and retained DWT-S2 evidence paths as leading inputs;
- instruct the agent to apply `spec-change-delivery` only to DWT-S3 and to use `spec-closeout` only for DWT-S3 closeout sync;
- explicitly forbid DWT-S5 implementation, runtime delivery, Docker, deployment, credential copy and KI-fuer-KMU original writes;
- require pre-edit validation of Child Index row, persisted handoff, target workspace, allowed write-set and predecessor evidence;
- require all edit-like output to target an isolated temp workspace or artifact bundle, not the original repository;
- require closeout output to preserve `DWT-PR3`, `DWT-PR4`, `DWT-PR5` and `DWT-PR7` coverage;
- require DWT-S5 to remain blocked unless a later DWT-S5 child spec, handoff, validator run and dependency evidence exist;
- require a concise final handoff/status output for deterministic parsing.

The prompt must not ask the agent to implement runtime code. Any runtime edit attempt is a failing forbidden action.

### Output Bundle Contract

Each DWT-S3 output bundle must contain:

| Path | Required Semantics |
|---|---|
| `source-manifest.json` | Source parent path, DWT-S3 child spec path, DWT-S3 handoff path, retained DWT-S2 evidence paths, stable source ids or hashes, copied fixture paths, generated artifact paths and declared normalizations. |
| `agent-output.md` | Raw or normalized agent final output. Must preserve enough detail to audit route choice, DWT-S3-only delivery scope and closeout state. |
| `delivery-kickoff.md` | Parsed or normalized delivery kickoff plan showing DWT-S3 child id, current handoff, target workspace and allowed write-set. |
| `closeout-sync.md` | Parsed or normalized closeout sync output showing Parent Child Index, evidence, OpenSpec/ledger, backlog/re-entry and DWT-S5 state updates. |
| `child-index-before.md` | Child Index fixture before DWT-S3 delivery. Must include DWT-S3 implementation-ready and DWT-S5 blocked states. |
| `child-index-after.md` | Child Index fixture after synthetic DWT-S3 closeout. Must show DWT-S3 accepted or closed and DWT-S5 still blocked. |
| `handoffs/dwt-s3-session-handoff.md` | Fresh DWT-S3 handoff used for delivery kickoff in the fixture. |
| `handoffs/stale-dwt-s3-session-handoff.md` | Negative stale handoff fixture with missing or mismatched target workspace, verdict or write-set. |
| `agent-run-manifest.json` | DWT-S4-compatible telemetry manifest for commands, reads, tool calls, forbidden classes, budgets and efficiency verdict. |
| `evidence/dwt-s3-l2-summary.json` | DWT-S4-compatible summary with DWT-S3 case results and evidence links. |

### DWT-S3 Summary Contract

`evidence/dwt-s3-l2-summary.json` must be JSON with:

| Field | Required Semantics |
|---|---|
| `schema_id` | `docworkflow-agent-delivery-summary.v1`. |
| `suite_level` | `DWT-S3`. |
| `suite_version` | Stable local version string. |
| `repo_root` | Absolute shared-ai-docs path. |
| `fixture_root` | Absolute isolated L2 run or fixture path. |
| `fixture_manifest` | Path or object reference to `source-manifest.json`. |
| `runner_mode` | `promptfoo-codex` or `fallback-artifact`. |
| `agent_execution_status` | One of the frozen agent execution statuses. |
| `overall_agent_proof_status` | `pass`, `blocked` or `fail`; `pass` requires `agent_execution_status: ran-target`. |
| `predecessor_evidence` | Object with retained DWT-S2 summary path, manifest path, `runner_mode`, `agent_execution_status`, `overall_agent_proof_status` and manifest sha presence result. |
| `test_results` | Object keyed by DWT-S3 case id with frozen status vocabulary values. |
| `harness_case_results` | Object keyed by DWT-S3 case id showing whether the expected positive, negative, blocked or warning assertion passed. |
| `evidence_truth` | Object keyed by DWT-S3 case id with frozen truth labels. |
| `evidence_links` | Paths to output bundle, kickoff assertions, closeout assertions, telemetry and blocked-agent evidence when present. |
| `runner_environment` | OS, shell, node/promptfoo versions when used and credential provisioning status without secret values. |
| `provenance_checks` | Source/copy/generated/normalization assertions, including retained DWT-S2 evidence identity. |
| `readiness_checks` | Child Index, DWT-S3 handoff, write-set, target workspace and validator assertions. |
| `closeout_checks` | Parent Coverage preservation, DWT-S3 accepted/closed state, evidence link sync, OpenSpec ledger sync and DWT-S5 blocked-state assertions. |
| `style_verdicts` | Per-case `pass`, `fail` or `warn`. |
| `telemetry_verdicts` | Per-case `pass`, `fail`, `warn` or `blocked`. |
| `forbidden_actions_observed` | Empty for pass; populated for expected negative/failing cases. |
| `downstream_children` | Must record `DWT-S5: blocked_by_dependency` unless a later DWT-S5 gate has independently changed it. |

Acceptance rule: `runner_mode: fallback-artifact` with `agent_execution_status` other than `ran-target` can pass deterministic validators, but the overall DWT-S3 evidence must be `blocked` rather than accepted workflow proof.

### Delivery Kickoff Gate Contract

A valid DWT-S3 delivery kickoff output must prove:

- Child id is exactly `DWT-S3`.
- Child Index row verdict is implementation-allowing and matches the persisted handoff.
- Persisted handoff path is `_specs/child-session-handoffs/dwt-s3-session-handoff.md`.
- Target Repository / Working Directory is an absolute isolated temp path under the run directory.
- Allowed Write-Set is concrete and contains only the DWT-S3 implementation paths listed in this spec and handoff.
- Shared/read-only predecessor evidence, accepted archives, canonical spec, existing L0/L1/S2/S4 runner outputs and KI-fuer-KMU originals are not edit targets.
- No DWT-S5 delivery or runtime implementation starts from the DWT-S3 kickoff.

### Closeout Gate Contract

A valid DWT-S3 closeout output must prove:

- DWT-S3 closeout sync updates or proposes sync for the Parent Child Index row, DWT-S3 child spec, DWT-S3 handoff, DWT-S3 evidence links and active OpenSpec change.
- Parent Coverage for `DWT-PR3`, `DWT-PR4`, `DWT-PR5` and `DWT-PR7` remains present after closeout.
- Retained DWT-S2 evidence links remain cited as predecessor input, not overwritten as DWT-S3 output.
- DWT-S5 remains `BLOCKED BY DEPENDENCY` or an equivalent non-implementation-allowing state.
- Any next DWT-S5 handoff candidate is treated as blocked or planned and cannot name `spec-change-delivery` until DWT-S5 has its own ready child spec, persisted handoff and validator run.
- OpenSpec archival is allowed only after DWT-S3 implementation evidence exists and closeout verification passes.

## Canonical Examples and Fixtures

Use referenced fixture files. No embedded machine-readable JSON/YAML/TOML/schema example in this spec is normative input. Tables in this spec are normative field contracts; machine-readable fixtures must live in files and be exercised by the DWT-S3 runner.

Required implementation fixture paths:

| Fixture | Purpose | Normative Fields / Values | Implementation Timing |
|---|---|---|---|
| `tests/docworkflow-agent-delivery/l2/single-child-closeout/fixtures/dwt-s3-ready-kickoff/` | Positive delivery kickoff fixture. | DWT-S3 child id, current handoff pointer, implementation-ready verdict, concrete write-set, temp target workspace and retained DWT-S2 evidence links. | Create during DWT-S3 implementation. |
| `tests/docworkflow-agent-delivery/l2/single-child-closeout/fixtures/stale-dwt-s3-handoff/` | Negative stale handoff fixture. | Missing or mismatched target workspace, verdict, child id or write-set must fail. | Create during DWT-S3 implementation. |
| `tests/docworkflow-agent-delivery/l2/single-child-closeout/fixtures/out-of-workspace-write-attempt/` | Negative delivery isolation fixture. | Any original repo, KI-fuer-KMU, Docker, deployment or credential-copy target must fail. | Create during DWT-S3 implementation. |
| `tests/docworkflow-agent-delivery/l2/single-child-closeout/fixtures/closeout-sync-positive/` | Positive synthetic closeout fixture. | Preserves Parent Coverage, links DWT-S3 evidence, records OpenSpec ledger state and keeps DWT-S5 blocked. | Create during DWT-S3 implementation. |
| `tests/docworkflow-agent-delivery/l2/single-child-closeout/fixtures/dwt-s5-auto-release-attempt/` | Negative next-child fixture. | DWT-S5 implementation-ready or `spec-change-delivery` next action without DWT-S5 gates must fail. | Create during DWT-S3 implementation. |
| `tests/docworkflow-agent-delivery/l2/single-child-closeout/fixtures/blocked-agent-output/` | Fallback blocker fixture. | Records blocked auth/provider/network/runtime status and must not be reported as accepted agent proof. | Create during DWT-S3 implementation. |
| `tests/docworkflow-agent-delivery/l2/single-child-closeout/fixtures/style-efficiency-output/` | Reporting fixture. | Uses DWT-S4 summary/telemetry/style fields and forbidden command classes. | Create during DWT-S3 implementation. |

Harness verification must prove each fixture was exercised by linking per-fixture assertion output from `dwt-s3-l2-summary.json`.

## Control Flow and Failure Cases

1. Create isolated DWT-S3 L2 run directory.
2. Read retained DWT-S2 summary and manifest; fail if status is not accepted `ran-target` proof.
3. Copy or synthesize DWT-S3-ready Child Index, child spec and handoff fixtures into the run directory; record source identity and declared normalizations.
4. If `agent` or `all` with available agent prerequisites, run Promptfoo/Codex using bundled Node and isolated caches.
5. If the agent runner is blocked, store a blocker output and run fallback artifact validators only.
6. Validate delivery kickoff output shape, provenance, DWT-S3-only scope and temp workspace target.
7. Validate stale handoff and out-of-workspace negative fixtures are blocked.
8. Validate synthetic closeout output preserves Parent Coverage, accepted evidence links, OpenSpec ledger state and DWT-S5 blocked state.
9. Validate DWT-S4-compatible summary, style and telemetry fields.
10. Return non-zero when a positive proof fails, a negative fixture passes, a fallback blocker is mislabeled as pass, DWT-S5 is released, or a forbidden action is observed.

Failure states:

- `missing_or_invalid_dwt_s2_dependency_evidence`
- `stale_or_mismatched_dwt_s3_handoff`
- `missing_target_workspace`
- `target_workspace_not_isolated`
- `approximate_or_mismatched_write_set`
- `delivery_not_limited_to_dwt_s3`
- `forbidden_runtime_or_repo_write`
- `closeout_parent_coverage_loss`
- `missing_closeout_evidence_sync`
- `missing_openspec_ledger_sync`
- `dwt_s5_released_without_own_gate`
- `stale_or_unprovenanced_output`
- `blocked_agent_misreported_as_pass`
- `invalid_dwt_s4_summary_or_telemetry`
- `secret_or_credential_leak`

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `DWT-S3-L2A` | Ready child delivery kickoff is temp-workspace only. | `dwt-s3-ready-kickoff`; retained DWT-S2 summary and manifest. | `pass` only when DWT-S3 readiness, current handoff and isolated target workspace are proven. | Source manifest, delivery kickoff assertion, target workspace assertion. | No KI-fuer-KMU write, Docker, deployment, runtime build/test or credential copy. |
| `DWT-S3-L2B` | Stale or mismatched DWT-S3 handoff blocks delivery. | `stale-dwt-s3-handoff`. | Expected fixture result `fail` or `blocked`; runner overall passes only by detecting the blocker. | Handoff validation assertion output. | Missing Target Repository, mismatched verdict, child id or write-set cannot pass. |
| `DWT-S3-L2C` | Closeout sync preserves Parent Coverage and accepted evidence links. | `closeout-sync-positive`. | `pass` when DWT-PR3/PR4/PR5/PR7 coverage remains and DWT-S3 evidence/OpenSpec ledger sync is visible. | Closeout assertion, coverage assertion, evidence ledger assertion. | DWT-S2 retained evidence cannot be overwritten or relabeled as DWT-S3 proof. |
| `DWT-S3-L2D` | DWT-S5 remains blocked after DWT-S3 closeout. | `dwt-s5-auto-release-attempt` plus positive closeout fixture. | `blocked` or expected negative `fail` for DWT-S5 release attempt. | Next-child assertion output and DWT-S5 state record. | DWT-S5 cannot name `spec-change-delivery` without its own ready spec/handoff/validator. |
| `DWT-S3-L2E` | Blocked agent path is honest. | `blocked-agent-output` or real blocked Promptfoo run. | `blocked` for agent proof; deterministic validators may pass fallback checks. | Blocker log and summary status. | `blocked_auth`, `blocked_provider`, `blocked_network` or `blocked_runtime` cannot be reported as `pass`. |
| `DWT-S3-L2F` | DWT-S4 reporting/style/efficiency contract is honored. | `style-efficiency-output` plus generated summary/telemetry. | `pass`, `warn` or expected negative status per fixture. | `dwt-s3-l2-summary.json`, `agent-run-manifest.json`, style/efficiency assertions. | No secret values in telemetry; DWT-S5 remains blocked. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `bash` or `zsh`
- Node for Promptfoo path: `/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`
- Promptfoo package: `promptfoo@0.121.9`
- Platform: macOS authoring, Linux-compatible shell where practical
- Runtime assumptions: DWT-S3 implementation may require Codex/Promptfoo credentials for `pass`; without them it must produce `blocked` evidence and fallback validator output, not accepted agent proof.

Pre-implementation hardening verification and command-contract rehearsal:

```sh
test -f tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-l2-summary.json
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-l2-summary.json','utf8')); if (s.runner_mode !== 'promptfoo-codex' || s.agent_execution_status !== 'ran-target' || s.overall_agent_proof_status !== 'pass') process.exit(1);"
test -f tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/manifest.json
node -e "const fs=require('fs'); const m=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/manifest.json','utf8')); if (m.proof_status?.agent_execution_status !== 'ran-target' || !m.sha256?.['dwt-s2-l2-summary.json']) process.exit(1);"
bash -n tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh
PATH="/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH" node --version
openspec validate docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness --strict
openspec validate docworkflow-agent-delivery-testsuite --strict
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md" \
  --child DWT-S3 \
  --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/dwt-s3-session-handoff.md"
git -C /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs diff --check
```

Gate verification after DWT-S3 implementation creates the runner, config, validators and fixtures:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh
tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh all --keep
tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all
openspec validate docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness --strict
openspec validate docworkflow-agent-delivery-testsuite --strict
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md" \
  --child DWT-S3 \
  --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/dwt-s3-session-handoff.md"
```

Success criteria:

- Retained DWT-S2 summary and manifest exist, parse and prove `promptfoo-codex` `ran-target` accepted predecessor evidence.
- Active DWT-S3 OpenSpec change validates strictly.
- Canonical accepted OpenSpec spec remains valid while DWT-S3 is active.
- `ValidateChildReadiness.cs` passes for DWT-S3 before delivery starts.
- Existing L0, L1, DWT-S2 and DWT-S4 gates remain syntactically runnable and do not become hidden dependencies for false DWT-S3 proof.
- After implementation, `run-l2-single-child-closeout-checks.sh all --keep` exits `0` only when positive, negative, blocked, fallback, closeout, style and telemetry cases match required statuses.
- DWT-S3 acceptance evidence includes `agent_execution_status: ran-target`. If the agent path is blocked, the implementation result remains blocked and is not accepted as L2 proof.
- DWT-S5 remains blocked unless its own later hardening and handoff gates change it.

Anti-loop rule: DWT-S3 validators must inspect output bundles, source manifests, handoffs, target workspace paths, write-set assertions, closeout sync artifacts, summaries and telemetry. They must not pass by checking only that command strings or documentation sections exist.

## Command-Contract Rehearsal Evidence

Performed during hardening on 2026-05-08:

| Rehearsal | Result | Meaning |
|---|---|---|
| Retained DWT-S2 `dwt-s2-l2-summary.json` presence and status assertion | Passed. | Accepted L2 parent-first predecessor proof is available and reports `promptfoo-codex`, `ran-target`, `pass`. |
| Retained DWT-S2 `manifest.json` presence and sha assertion | Passed. | Stable retained predecessor evidence manifest is available. |
| Existing L0/L1/S2/reporting shell syntax | Passed. | Predecessor runner command contracts are syntactically valid. |
| Bundled Node `node --version` | Passed and reported `v24.14.0`. | S0/S2 Promptfoo runtime selection remains available. |
| `openspec validate docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness --strict` | Passed. | Active DWT-S3 change is structurally valid. |
| `openspec validate docworkflow-agent-delivery-testsuite --strict` | Passed. | Canonical accepted spec remains valid while DWT-S3 is active. |
| `ValidateChildReadiness.cs` for DWT-S3 | Passed. | Child Index, DWT-S3 handoff, verdict and write-set agree. |
| `git diff --check` | Passed. | Hardening edits have no whitespace errors. |

`run-l2-single-child-closeout-checks.sh` does not exist before DWT-S3 implementation. Its first successful syntax and `all --keep` executions are DWT-S3 delivery evidence, distinct from hardening rehearsal evidence.

## Implementation Evidence

Performed during DWT-S3 implementation on 2026-05-08:

| Verification | Result | Evidence |
|---|---|---|
| `bash -n tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh` | Passed. | New DWT-S3 wrapper is syntactically valid. |
| `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh all --keep` | Passed in deterministic fallback mode. | Temp run `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l2-single-child-closeout.Snb7uI`; summary correctly reported fallback evidence as blocked, not accepted proof. |
| `DWT_S3_ENABLE_AGENT=1 tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh all --keep` | Passed with Promptfoo/Codex. | Retained evidence `tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/dwt-s3-l2-summary.json`; `runner_mode: promptfoo-codex`, `agent_execution_status: ran-target`, `overall_agent_proof_status: pass`. |
| `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all` | Passed. | DWT-S4 reporting compatibility preserved. |
| `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all` | Passed. | L0 TC1/TC2 contract checks preserved. |
| `openspec validate docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness --strict` | Passed. | Active DWT-S3 OpenSpec change remains valid. |
| `openspec validate docworkflow-agent-delivery-testsuite --strict` | Passed. | Canonical OpenSpec spec remains valid while DWT-S3 is active. |
| `ValidateChildReadiness.cs` for DWT-S3 | Passed. | Parent Child Index and persisted DWT-S3 handoff remain synchronized. |
| `git diff --check` | Passed. | No whitespace errors in implementation edits. |

## Closeout Evidence

Performed during DWT-S3 closeout on 2026-05-08:

| Verification | Result | Evidence |
|---|---|---|
| Required verification replay | Passed. | Retained DWT-S2 and DWT-S3 JSON/manifest assertions, script syntax, DWT-S3 fallback and Promptfoo/Codex runs, DWT-S4 reporting, L0 all, OpenSpec validates and `git diff --check` all passed. |
| OpenSpec archive | Passed. | Archived to `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness/`. |
| Canonical OpenSpec spec validation | Passed. | `openspec validate docworkflow-agent-delivery-testsuite --strict` passed after archive. |
| Parent/Child sync | Passed. | Parent Child Index row records DWT-S3 `ACCEPTED`, retained evidence links and archived OpenSpec path while DWT-S5 remains `BLOCKED BY DEPENDENCY`. |

## Definition of Ready for Implementation

- Parent coverage and conformance are explicit for `DWT-PR3`, `DWT-PR4`, `DWT-PR5` and `DWT-PR7`.
- Runner modes, output bundle, delivery kickoff, closeout, summary, telemetry and fallback/blocker contracts are normative.
- Retained DWT-S2 predecessor evidence is identified and validated as readable accepted `ran-target` proof.
- Fixture strategy is concrete and names implementation paths.
- Harness cases include positive, negative, blocked, fallback, closeout, style, telemetry and secret/redaction assertions.
- Allowed Write-Set and Shared/Read-only Files are enforceable.
- Verification commands, success criteria and anti-loop rule are defined.
- Active OpenSpec change exists and validates.
- Persisted handoff exists and matches this spec and the Parent Child Index.
- `ValidateChildReadiness.cs` passes for `DWT-S3` before delivery starts.

## Definition of Done / Closeout Evidence

- L2 single-child-closeout fixtures, validators, Promptfoo config and fallback artifact runner exist.
- `run-l2-single-child-closeout-checks.sh all --keep` writes retained evidence under an isolated run directory.
- A real agent run produces accepted `ran-target` evidence, or the DWT-S3 implementation remains blocked with reproducible blocker evidence.
- The accepted DWT-S3 summary uses DWT-S4 summary/telemetry/style fields and links assertion outputs.
- The harness proves DWT-S3-only kickoff, stale handoff block, temp workspace isolation, closeout sync, Parent Coverage preservation and DWT-S5 blocked state.
- Parent Child Index links DWT-S3 implementation evidence and next action after closeout.
- OpenSpec change tasks and canonical spec are synchronized after acceptance/archive.
- DWT-S5 remains blocked unless its own later hardening gates pass.
- No original source specs, KI-fuer-KMU repos or runtime repositories were modified.

## Dependencies and Write-Set

Allowed implementation write-set:

- `_specs/2026-05-08 DocWorkflow Agent Delivery Testsuite DWT-S3 L2 Single-Child Delivery Closeout Gate Harness.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`
- `_specs/child-session-handoffs/dwt-s3-session-handoff.md`
- `openspec/changes/docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness/**`
- `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`
- `tests/docworkflow-agent-delivery/l2/single-child-closeout/**`
- `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh`
- `tests/docworkflow-agent-delivery/README.md`
- `tests/docworkflow-agent-delivery/testcases/tc2-single-child-delivery-next-handoff.md`

Shared/read-only files:

- `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-l2-summary.json`
- `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/manifest.json`
- `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-agent-proof.json`
- `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json`
- `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.bMyVlu/evidence/l1-summary.json`
- `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-reporting.CA7ryD/evidence/dwt-s4-reporting-summary.json`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S0 Framework Spike.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S1 L1 Deterministic Harness.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S2 L2 Parent-first Orchestration Agent Harness.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S4 Summary Telemetry Style Reporting Contract.md`
- `_specs/child-session-handoffs/dwt-s0-session-handoff.md`
- `_specs/child-session-handoffs/dwt-s1-session-handoff.md`
- `_specs/child-session-handoffs/dwt-s2-session-handoff.md`
- `_specs/child-session-handoffs/dwt-s4-session-handoff.md`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/**`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness/**`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness/**`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s4-reporting-telemetry-contract/**`
- `tests/docworkflow-agent-delivery/l1/**`
- `tests/docworkflow-agent-delivery/l2/parent-first/**`
- `tests/docworkflow-agent-delivery/reporting/**`
- `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `docs/doc-workflow.md`
- `skills-repo/skills/**`
- KI-fuer-KMU original specs and runtime repositories

Parallel hardening / implementation:

- DWT-S3 implementation is not safe to run in parallel with another lane editing `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`, shared reporting validators or DWT-S2 retained evidence.
- DWT-S5 may be hardened separately only as a spec-only lane after DWT-S3 output contract is stable, but DWT-S5 implementation remains blocked until DWT-S3 is accepted.
- One integration owner must sync Parent Child Index and canonical OpenSpec changes during DWT-S3 closeout.

## Closeout Sync Targets

- Parent Child Index row `DWT-S3`.
- Active OpenSpec change `openspec/changes/docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness/`.
- Canonical OpenSpec spec `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` after DWT-S3 acceptance/archive.
- DWT-S3 retained evidence path and README/testcase documentation.
- DWT-S3 child spec implementation and closeout evidence sections.
- DWT-S3 persisted handoff after closeout.
- DWT-S5 row must remain blocked until its own later gates pass.

## Child Session Handoff

Persisted handoff: `_specs/child-session-handoffs/dwt-s3-session-handoff.md`.

## Content Quality Review

- Correctness/domain fit: Pass. DWT-S3 owns L2 single-child delivery and closeout gate proof and does not claim runtime/L3 proof.
- Scope discipline: Pass. Runner implementation, live agents, DWT-S5 and runtime delivery remain out of hardening scope.
- Completeness: Pass. Runner modes, outputs, fixture paths, cases, verification, write-set, OpenSpec and handoff are concrete.
- Consistency: Pass after Parent Child Index, handoff and active OpenSpec sync.
- Testability: Pass. Implementation has deterministic fixture/validator paths plus explicit handling for real agent pass versus blocked fallback.
- Blocking Marker: None after hardening verification passes.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-08 | Codex | Hardened DWT-S3 into an implementation-ready L2 Single-Child Delivery and Closeout Gate Harness child spec with runner/fallback contract, fixtures, verification, OpenSpec change and handoff/index sync. |
| 2026-05-08 | Codex | Implemented DWT-S3 fixtures, validator, Promptfoo config, runner, docs and retained `ran-target` Promptfoo/Codex evidence while preserving DWT-S5 blocked state. |
| 2026-05-08 | Codex | Accepted DWT-S3 after closeout replay, archived OpenSpec change, updated canonical spec and synchronized Parent Child Index while keeping DWT-S5 blocked. |

SessionId: 2026-05-08-docworkflow-agent-delivery-testsuite-dwt-s3
