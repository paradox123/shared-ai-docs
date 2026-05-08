**Date:** 2026-05-08
**Status:** 🟢 Accepted
**Scope:** Accepted child spec for the DWT-S5 L3 Runtime Temp-Repo Delivery Pilot.

---

## Review Control Surface

- Spec-Variante: accepted Child Spec.
- Goldstandard Status: accepted.
- Ziel: Einen L3-Piloten definieren, der eine einzelne synthetische Child-Delivery in einem isolierten Temp-Repo ausfuehrt, lokale Runtime-Gates und Container-/Harness-Gates als Evidence trennt und beweist, dass keine Original-Repositories oder Folge-Children beschrieben, veraendert oder freigegeben werden.
- In Scope: DWT-S5 L3 Temp-Repo runner contract, synthetic runtime fixture, temp-repo materialization, local runtime gate, container/harness gate contract, Promptfoo/Codex delivery kickoff through the current DWT-S5 handoff, retained DWT-S3 evidence dependency checks, DWT-S4-compatible summary/telemetry/style evidence, OpenSpec active change, Parent Child Index and persisted handoff sync.
- Out of Scope: DWT-S5 implementation during hardening, runtime or Docker execution as hardening acceptance proof, any KI-fuer-KMU original repo description or write, broad runtime migration, deployment, credential copying, mutation of accepted DWT-S0 through DWT-S4 archives, auto-release of any child after DWT-S5.
- Wichtigste Test-/Harness-Cases: `DWT-S5-L3A temp repo is materialized from synthetic fixture only`, `DWT-S5-L3B delivery kickoff validates current DWT-S5 handoff and write-set`, `DWT-S5-L3C local runtime gate runs inside temp repo only`, `DWT-S5-L3D container/harness gate is isolated and honestly blocked when unavailable`, `DWT-S5-L3E forbidden original-repo or credential writes fail`, `DWT-S5-L3F closeout preserves DWT-PR3/DWT-PR4/DWT-PR5 and DWT-S3 retained evidence`.
- Wichtigste Verification Commands: retained DWT-S3 summary/manifest presence and status assertions; `bash -n` for existing L0/L1/S2/S3/S4 scripts; active-change `openspec validate docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot --strict`; canonical `openspec validate docworkflow-agent-delivery-testsuite --strict`; DWT-S5 `ValidateChildReadiness.cs`; `git diff --check`; after implementation, `bash -n tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh`, `tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh preflight --keep`, `tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh all --keep`, `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all`, and `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen. The L3 pilot uses a synthetic fixture repository, not a KI-fuer-KMU original repository. Container execution is an implementation-time gate; if Docker or the container runtime is unavailable, the result must be `blocked_runtime`, not `pass`.
- Readiness Status: ACCEPTED; was IMPLEMENTATION READY.

## Goal

Create the implementation contract for an L3 Runtime Temp-Repo Delivery Pilot. The pilot must prove that a single child delivery can run against a disposable synthetic repository while preserving the parent-control gates established by DWT-S2 and DWT-S3.

The implementation must distinguish three outcomes:

- `pass`: a real DWT-S5 delivery run exercised the synthetic temp repo, local runtime gate and container/harness gate, and deterministic validators accepted the evidence.
- `blocked`: auth, provider, runtime, container or network prerequisites prevented the target run, and fallback/preflight evidence proves the blocker without accepting the pilot as runtime proof.
- `fail`: the run touched or described forbidden original repositories, used stale handoffs, skipped readiness validation, wrote outside the temp repo or source-controlled DWT-S5 harness write-set, hid evidence, released another child, leaked secrets, or mislabeled blocked runtime evidence as pass.

## In Scope

- Add source-controlled DWT-S5 L3 fixture definitions under `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/`.
- Add DWT-S5 L3 validators under `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/validators/`.
- Add primary Promptfoo/Codex runner config and command wrapper under `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/`.
- Add temp-repo materialization that creates disposable runtime workspaces under a generated run directory.
- Add local runtime gate checks for the synthetic fixture only.
- Add container/harness gate checks that either run in the generated temp workspace or report `blocked_runtime`.
- Add `tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh`.
- Emit DWT-S4-compatible summary and telemetry artifacts for DWT-S5.
- Update `tests/docworkflow-agent-delivery/README.md` and `tests/docworkflow-agent-delivery/testcases/tc2-single-child-delivery-next-handoff.md` with the DWT-S5 L3 boundary.

## Out of Scope

- No DWT-S5 implementation during this hardening run.
- No runtime execution or Docker/container execution as hardening acceptance proof.
- No KI-fuer-KMU original repo description, copy, mutation, build, test or deployment.
- No broad runtime migration or non-synthetic project fixture.
- No credential copying into repo files or generated evidence.
- No auto-release of any later child after DWT-S5.
- No mutation of accepted DWT-S0, DWT-S1, DWT-S2, DWT-S3 or DWT-S4 archives.
- No OpenSpec archive until DWT-S5 implementation evidence exists and closeout runs.

## Parent/Master Coverage

| Parent Requirement | Child Coverage |
|---|---|
| `DWT-PR3` | Owns the L3 proof that single-child delivery still starts only from the current DWT-S5 child spec, Parent Child Index row, implementation-ready verdict, persisted handoff, concrete write-set and isolated temp repo. |
| `DWT-PR4` | Owns the L3 closeout proof that Parent/Index/Evidence/OpenSpec/Handoff remain synchronized after runtime pilot evidence without releasing another child. |
| `DWT-PR5` | Requires provenance for fixture source, temp-repo materialization, retained DWT-S3 evidence, local/container gate truth labels, no stale output reuse and no blocked-runtime-as-pass substitution. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `DWT-PR3` | Runtime delivery must validate Child Index, handoff, verdict, write-set and isolated temp repo before any edit-like or runtime action. | preserves | Implement DWT-S5 L3 runner plus validators for current handoff, allowed write-set, temp repo materialization and DWT-S5-only delivery scope. |
| `DWT-PR4` | Closeout must synchronize Parent/Index/Evidence/OpenSpec/Handoff and must not release another child by implication. | preserves | Implement closeout assertions that preserve DWT-PR3/DWT-PR4/DWT-PR5, link DWT-S5 evidence and keep descendant release state non-implementation-allowing. |
| `DWT-PR5` | L3 evidence must distinguish real runtime/container execution, blocked runtime prerequisites, stale copied outputs and forbidden write attempts. | preserves | Require retained DWT-S3 evidence links, source manifests, summary truth labels, local/container gate statuses and forbidden-action assertions. |
| `DWT-PR1` | DWT-S5 consumes accepted parent-first orchestration output but does not re-prove child slicing. | narrows_with_rationale | DWT-S2 remains responsible for parent-first orchestration proof. |
| `DWT-PR2` | DWT-S5 consumes readiness gates as inputs but does not redefine child-hardening semantics. | narrows_with_rationale | DWT-S1 and `ValidateChildReadiness.cs` remain the deterministic readiness baseline. |
| `DWT-PR6` | DWT-S5 reuses the Promptfoo-first decision and does not reopen framework research. | narrows_with_rationale | DWT-S0 remains the framework evidence source. |
| `DWT-PR7` | DWT-S5 reuses the DWT-S4 reporting contract for summaries, telemetry, style and efficiency. | narrows_with_rationale | DWT-S4 remains the reporting-contract source; DWT-S5 emits compatible evidence. |

## Decision Freeze Pack

| Entscheidung | Freeze |
|---|---|
| Primary agent runner | Promptfoo `0.121.9` with bundled Node `v24.14.0`, reusing accepted DWT-S0, DWT-S2 and DWT-S3 command-contract patterns and explicit auth/network limitations. |
| Runtime target | A synthetic fixture repository generated under the DWT-S5 run directory. No KI-fuer-KMU original repository may be named, copied, described as the target, built, tested or changed. |
| Required predecessor proof | DWT-S5 implementation must read retained DWT-S3 summary `tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/dwt-s3-l2-summary.json` and manifest `tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/manifest.json`; `runner_mode` must be `promptfoo-codex`, `agent_execution_status` must be `ran-target`, and `overall_agent_proof_status` must be `pass`. |
| Required proof shape | A DWT-S5 run must materialize a disposable temp repo from source-controlled synthetic fixtures, run or honestly block local and container/harness gates inside that temp repo, and write evidence under the DWT-S5 run directory. |
| Fallback runner | Deterministic preflight/artifact mode may validate stored output bundles and blocker evidence; it cannot produce accepted L3 runtime proof without target local and container/harness gate evidence. |
| Output status vocabulary | `pass`, `fail`, `blocked`, `warn`, `planned`. |
| Evidence truth vocabulary | `ran-target`, `ran-rehearsal`, `blocked`, `failed`, `planned`, `dry-run`. |
| Runtime execution status vocabulary | `ran-target`, `blocked_auth`, `blocked_provider`, `blocked_network`, `blocked_runtime`, `failed`, `not-run`. |
| Reporting contract | DWT-S5 summaries use `schema_id: docworkflow-agent-delivery-summary.v1` and DWT-S4 telemetry/style/efficiency semantics. |
| Original repos | KI-fuer-KMU original specs and runtime repositories remain read-only and unnamed as runtime targets. |
| Descendant release | DWT-S5 may release only its own implementation evidence and closeout sync. No later child receives implementation authorization from DWT-S5 closeout. |

## Normative Contract

### L3 Runner Modes

The DWT-S5 implementation must provide `tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh` with these selectors:

| Selector | Required Behavior |
|---|---|
| `all` | Runs DWT-S5 L3A-L3F assertions, including prerequisite validation, temp-repo materialization, local runtime gate, container/harness gate, forbidden-action assertions, reporting checks and summary writing. |
| `preflight` | Validates retained DWT-S3 evidence, tool availability, fixture integrity and temp directory creation without running runtime or Docker/container commands. |
| `agent` | Uses Promptfoo/Codex when credentials/provider/runtime are provisioned; stores raw output, telemetry and deterministic validation output. |
| `fallback` | Uses stored artifact fixtures and blocker outputs only; may prove validator behavior and blocked-runtime reporting, but cannot mark DWT-S5 accepted as L3 runtime proof. |
| `validate-output` | Validates an existing DWT-S5 output bundle path without launching an agent or runtime command. |
| `local-runtime` | Runs the local runtime gate only inside the materialized synthetic temp repo. |
| `container-harness` | Runs the container/harness gate only inside the materialized synthetic temp repo, or reports `blocked_runtime` with reproducible preflight evidence. |
| `closeout` | Validates closeout output, Parent Coverage preservation, evidence/OpenSpec ledger fields and descendant non-release state. |
| `style` | Runs DWT-S4-compatible style/usability assertions for DWT-S5 output. |
| `telemetry` | Runs DWT-S4-compatible efficiency/telemetry assertions for DWT-S5 output. |

The runner must accept `--run-dir DIR`, `--keep`, `--output-bundle DIR`, `--fixture DIR` and `--skip-container` where applicable. Every run must write evidence under `<run-dir>/evidence/` and generated repositories under `<run-dir>/target-repos/`.

### Synthetic Runtime Fixture Contract

The runtime fixture must be a small source-controlled repository template created for this testsuite only. It must:

- live under `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/synthetic-runtime-repo/`;
- include a deterministic local command that can pass without network access;
- include a deterministic container/harness command or a fixture-level blocker contract that reports `blocked_runtime`;
- include no secrets, real credentials, deployment targets, original project names, or KI-fuer-KMU domain content;
- be copied into `<run-dir>/target-repos/dwt-s5-synthetic-runtime-repo/` before edit-like or runtime actions;
- expose a manifest with fixture id, version, file list, local gate command, container gate command and forbidden path classes;
- be treated as immutable source input during each run.

### Agent Prompt Contract

The primary agent prompt must:

- provide the parent/master spec path, DWT-S5 child spec path, Parent Child Index path, DWT-S5 handoff path and retained DWT-S3 evidence paths as leading inputs;
- instruct the agent to apply `spec-change-delivery` only to DWT-S5 and only against the generated synthetic temp repo;
- explicitly forbid DWT-S5 from describing, copying, building, testing, deploying or editing any KI-fuer-KMU original repository;
- require pre-action validation of Child Index row, persisted handoff, target repository, allowed write-set, retained DWT-S3 evidence and synthetic fixture manifest;
- require local runtime and container/harness output truth labels before any pass verdict;
- require closeout output to preserve `DWT-PR3`, `DWT-PR4` and `DWT-PR5` coverage;
- require a concise final handoff/status output for deterministic parsing.

### Output Bundle Contract

Each DWT-S5 output bundle must contain:

| Path | Required Semantics |
|---|---|
| `source-manifest.json` | Source parent path, DWT-S5 child spec path, DWT-S5 handoff path, retained DWT-S3 evidence paths, synthetic fixture path, stable ids or hashes, generated temp-repo path and declared normalizations. |
| `agent-output.md` | Raw or normalized agent final output preserving route choice, DWT-S5-only scope, runtime gate statuses and closeout state. |
| `delivery-kickoff.md` | Parsed or normalized delivery kickoff plan showing DWT-S5 child id, current handoff, target workspace, temp repo path and allowed write-set. |
| `runtime-gates.md` | Local runtime and container/harness gate commands, statuses, exit codes and blocked-runtime reasons without secret values. |
| `closeout-sync.md` | Parsed or normalized closeout output showing Parent Child Index, evidence, OpenSpec/ledger and descendant non-release state. |
| `child-index-before.md` | Child Index fixture before DWT-S5 delivery. Must include DWT-S5 implementation-ready state and retained DWT-S3 evidence references. |
| `child-index-after.md` | Child Index fixture after synthetic DWT-S5 closeout. Must show DWT-S5 accepted or closed and no descendant implementation authorization. |
| `handoffs/dwt-s5-session-handoff.md` | Fresh DWT-S5 handoff used for delivery kickoff in the fixture. |
| `agent-run-manifest.json` | DWT-S4-compatible telemetry manifest for commands, reads, tool calls, forbidden classes, budgets and efficiency verdict. |
| `evidence/dwt-s5-l3-summary.json` | DWT-S4-compatible summary with DWT-S5 case results and evidence links. |

### DWT-S5 Summary Contract

`evidence/dwt-s5-l3-summary.json` must be JSON with:

| Field | Required Semantics |
|---|---|
| `schema_id` | `docworkflow-agent-delivery-summary.v1`. |
| `suite_level` | `DWT-S5`. |
| `suite_version` | Stable local version string. |
| `repo_root` | Absolute shared-ai-docs path. |
| `fixture_root` | Absolute isolated L3 run or fixture path. |
| `fixture_manifest` | Path or object reference to `source-manifest.json`. |
| `runner_mode` | `promptfoo-codex`, `fallback-artifact` or `preflight`. |
| `agent_execution_status` | One of the frozen runtime execution statuses. |
| `overall_runtime_proof_status` | `pass`, `blocked` or `fail`; `pass` requires target local and container/harness evidence from the synthetic temp repo. |
| `predecessor_evidence` | Object with retained DWT-S3 summary path, manifest path, `runner_mode`, `agent_execution_status`, `overall_agent_proof_status` and manifest sha presence result. |
| `temp_repo` | Object with generated path, fixture id, fixture version, source hash or manifest id, and isolation checks. |
| `test_results` | Object keyed by DWT-S5 case id with frozen status vocabulary values. |
| `harness_case_results` | Object keyed by DWT-S5 case id showing whether the positive, negative, blocked or warning assertion passed. |
| `evidence_truth` | Object keyed by DWT-S5 case id with frozen truth labels. |
| `evidence_links` | Paths to output bundle, kickoff assertions, runtime gate assertions, closeout assertions, telemetry and blocker evidence when present. |
| `runner_environment` | OS, shell, Node/Promptfoo versions when used, local runtime details and container runtime availability without secret values. |
| `provenance_checks` | Source/copy/generated/normalization assertions, including retained DWT-S3 evidence identity. |
| `readiness_checks` | Child Index, DWT-S5 handoff, write-set, target workspace and validator assertions. |
| `runtime_checks` | Local runtime gate and container/harness gate status, command category, exit status and blocked-runtime reason. |
| `closeout_checks` | Parent Coverage preservation, DWT-S5 accepted/closed state, evidence link sync, OpenSpec ledger sync and descendant non-release assertions. |
| `style_verdicts` | Per-case `pass`, `fail` or `warn`. |
| `telemetry_verdicts` | Per-case `pass`, `fail`, `warn` or `blocked`. |
| `forbidden_actions_observed` | Empty for pass; populated for expected negative/failing cases. |
| `downstream_children` | Empty object or explicit non-implementation-allowing descendant state. |

Acceptance rule: `runner_mode: fallback-artifact` or `agent_execution_status` other than `ran-target` can pass deterministic validators, but the overall DWT-S5 runtime proof must be `blocked` rather than accepted workflow proof. A container/harness preflight blocker may be accepted only as a blocked implementation result, not as the L3 pass condition.

## Canonical Examples and Fixtures

Use referenced fixture files. No embedded machine-readable JSON/YAML/TOML/schema example in this spec is normative input. Tables in this spec are normative field contracts; machine-readable fixtures must live in files and be exercised by the DWT-S5 runner.

Required implementation fixture paths:

| Fixture | Purpose | Normative Fields / Values | Implementation Timing |
|---|---|---|---|
| `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/synthetic-runtime-repo/` | Positive synthetic runtime repository template. | Fixture id/version, local gate command, container/harness gate command or blocker contract, no original repo names, no secrets. | Create during DWT-S5 implementation. |
| `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/dwt-s5-ready-kickoff/` | Positive delivery kickoff fixture. | DWT-S5 child id, current handoff pointer, implementation-ready verdict, concrete write-set, temp repo path and retained DWT-S3 evidence links. | Create during DWT-S5 implementation. |
| `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/stale-dwt-s5-handoff/` | Negative stale handoff fixture. | Missing or mismatched target repository, verdict, child id, write-set or retained evidence must fail. | Create during DWT-S5 implementation. |
| `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/original-repo-write-attempt/` | Negative forbidden target fixture. | Any KI-fuer-KMU original reference, original repo write, deployment target, credential copy or out-of-run-dir path must fail. | Create during DWT-S5 implementation. |
| `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/container-runtime-blocked/` | Blocked runtime fixture. | Records unavailable Docker/container runtime as `blocked_runtime` and prevents pass labeling. | Create during DWT-S5 implementation. |
| `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/closeout-sync-positive/` | Positive synthetic closeout fixture. | Preserves DWT-PR3/DWT-PR4/DWT-PR5, links DWT-S5 evidence, records OpenSpec ledger state and no descendant release. | Create during DWT-S5 implementation. |
| `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/style-efficiency-output/` | Reporting fixture. | Uses DWT-S4 summary/telemetry/style fields and forbidden command classes. | Create during DWT-S5 implementation. |

Harness verification must prove each fixture was exercised by linking per-fixture assertion output from `dwt-s5-l3-summary.json`.

## Control Flow and Failure Cases

1. Create isolated DWT-S5 L3 run directory.
2. Read retained DWT-S3 summary and manifest; fail if status is not accepted `ran-target` proof.
3. Validate DWT-S5 child spec, Parent Child Index row and persisted handoff with `ValidateChildReadiness.cs`.
4. Copy the synthetic runtime fixture into `<run-dir>/target-repos/dwt-s5-synthetic-runtime-repo/`; record source identity and declared normalizations.
5. Validate the fixture manifest and forbidden path classes before any edit-like or runtime action.
6. If `agent` or `all` with available agent prerequisites, run Promptfoo/Codex using bundled Node and isolated caches.
7. Run local runtime gate inside the generated temp repo, or record a failing local runtime status.
8. Run container/harness gate inside the generated temp repo, or record `blocked_runtime` when the container runtime is unavailable.
9. Validate stale handoff and forbidden original-repo negative fixtures are blocked.
10. Validate closeout output preserves Parent Coverage, retained DWT-S3 evidence links, OpenSpec ledger state and descendant non-release state.
11. Validate DWT-S4-compatible summary, style and telemetry fields.
12. Return non-zero when a positive proof fails, a negative fixture passes, fallback or blocked-runtime evidence is mislabeled as pass, a forbidden original repo is referenced as runtime target, a secret is exposed, or another child is released.

Failure states:

- `missing_or_invalid_dwt_s3_dependency_evidence`
- `stale_or_mismatched_dwt_s5_handoff`
- `missing_synthetic_fixture_manifest`
- `target_repo_not_under_run_dir`
- `runtime_gate_outside_temp_repo`
- `container_gate_outside_temp_repo`
- `container_runtime_blocked_misreported_as_pass`
- `approximate_or_mismatched_write_set`
- `delivery_not_limited_to_dwt_s5`
- `forbidden_original_repo_reference`
- `forbidden_original_repo_write`
- `credential_or_secret_leak`
- `closeout_parent_coverage_loss`
- `missing_closeout_evidence_sync`
- `missing_openspec_ledger_sync`
- `descendant_released_without_own_gate`
- `stale_or_unprovenanced_output`
- `invalid_dwt_s4_summary_or_telemetry`

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `DWT-S5-L3A` | Temp repo is materialized from synthetic fixture only. | `synthetic-runtime-repo`; retained DWT-S3 summary and manifest. | `pass` only when generated target repo is under `<run-dir>/target-repos/` and fixture provenance is recorded. | Source manifest, fixture manifest assertion, temp-repo isolation assertion. | No original repo names, deployment targets, secrets or out-of-run-dir paths. |
| `DWT-S5-L3B` | Delivery kickoff validates current DWT-S5 handoff and write-set. | `dwt-s5-ready-kickoff`; DWT-S5 handoff; Parent Child Index. | `pass` only when DWT-S5 readiness, current handoff, concrete write-set and temp repo target agree. | Delivery kickoff assertion and readiness validator output. | Stale handoff, mismatched verdict or approximate write-set cannot pass. |
| `DWT-S5-L3C` | Local runtime gate runs inside temp repo only. | Generated synthetic temp repo. | `pass` when local gate exits `0` inside the temp repo and evidence records command, cwd and exit status. | Local runtime gate log and assertion output. | Local gate outside `<run-dir>/target-repos/` fails. |
| `DWT-S5-L3D` | Container/harness gate is isolated and honestly blocked when unavailable. | Generated synthetic temp repo; `container-runtime-blocked` fixture when runtime is absent. | `pass` when container/harness gate exits `0`; `blocked` when container runtime is unavailable and honestly reported. | Container/harness log, blocked-runtime record or assertion output. | `blocked_runtime` cannot be reported as accepted L3 pass. |
| `DWT-S5-L3E` | Forbidden original-repo or credential writes fail. | `original-repo-write-attempt`. | Expected fixture result `fail` or `blocked`; runner overall passes only by detecting the blocker. | Forbidden-action assertion output. | Any KI-fuer-KMU original target, credential copy, deployment or secret value fails. |
| `DWT-S5-L3F` | Closeout preserves DWT-PR3/DWT-PR4/DWT-PR5 and DWT-S3 retained evidence. | `closeout-sync-positive` plus generated summary/telemetry. | `pass` when coverage remains, DWT-S3 evidence is retained as predecessor input and OpenSpec ledger state is visible. | Closeout assertion, coverage assertion, evidence ledger assertion. | DWT-S3 retained evidence cannot be overwritten or relabeled as DWT-S5 proof; no descendant child is released. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `bash` or `zsh`
- Node for Promptfoo path: `/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`
- Promptfoo package: `promptfoo@0.121.9`
- Platform: macOS authoring, Linux-compatible shell where practical
- Runtime assumptions: DWT-S5 implementation may require Codex/Promptfoo credentials and a container runtime for `pass`; without them it must produce `blocked` evidence, not accepted L3 runtime proof.

Pre-implementation hardening verification and command-contract rehearsal:

```sh
test -f tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/dwt-s3-l2-summary.json
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/dwt-s3-l2-summary.json','utf8')); if (s.runner_mode !== 'promptfoo-codex' || s.agent_execution_status !== 'ran-target' || s.overall_agent_proof_status !== 'pass') process.exit(1);"
test -f tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/manifest.json
node -e "const fs=require('fs'); const m=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/manifest.json','utf8')); if (m.proof_status?.agent_execution_status !== 'ran-target' || !m.sha256?.['dwt-s3-l2-summary.json']) process.exit(1);"
bash -n tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh
PATH="/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH" node --version
openspec validate docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot --strict
openspec validate docworkflow-agent-delivery-testsuite --strict
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md" \
  --child DWT-S5 \
  --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/dwt-s5-session-handoff.md"
git -C /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs diff --check
```

Gate verification after DWT-S5 implementation creates the runner, config, validators and fixtures:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh
tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh preflight --keep
tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh all --keep
tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all
openspec validate docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot --strict
openspec validate docworkflow-agent-delivery-testsuite --strict
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md" \
  --child DWT-S5 \
  --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/dwt-s5-session-handoff.md"
```

Success criteria:

- Retained DWT-S3 summary and manifest exist, parse and prove `promptfoo-codex` `ran-target` accepted predecessor evidence.
- Active DWT-S5 OpenSpec change validates strictly.
- Canonical accepted OpenSpec spec remains valid while DWT-S5 is active.
- `ValidateChildReadiness.cs` passes for DWT-S5 before delivery starts.
- Existing L0, L1, DWT-S2, DWT-S3 and DWT-S4 gates remain syntactically runnable and do not become hidden dependencies for false DWT-S5 proof.
- After implementation, `run-l3-runtime-temp-repo-checks.sh all --keep` exits `0` only when positive, negative, blocked, runtime, container/harness, closeout, style and telemetry cases match required statuses.
- DWT-S5 pass evidence includes target local runtime and container/harness truth from the generated synthetic temp repo. If the agent path or container runtime is blocked, the implementation result remains blocked and is not accepted as L3 pass proof.
- No original runtime repository is described, copied, built, tested or modified.

Anti-loop rule: DWT-S5 validators must inspect output bundles, source manifests, handoffs, target repo paths, write-set assertions, runtime gate logs, container/harness gate logs, closeout sync artifacts, summaries and telemetry. They must not pass by checking only that command strings or documentation sections exist.

## Command-Contract Rehearsal Evidence

Performed during hardening on 2026-05-08:

| Rehearsal | Result | Meaning |
|---|---|---|
| Retained DWT-S3 `dwt-s3-l2-summary.json` presence and status assertion | Passed. | Accepted L2 single-child predecessor proof is available and reports `promptfoo-codex`, `ran-target`, `pass`. |
| Retained DWT-S3 `manifest.json` presence and sha assertion | Passed. | Stable retained predecessor evidence manifest is available. |
| Existing L0/L1/S2/S3/reporting shell syntax | Passed. | Predecessor runner command contracts are syntactically valid. |
| Bundled Node `node --version` | Passed and reported `v24.14.0`. | S0/S2/S3 Promptfoo runtime selection remains available. |
| `openspec validate docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot --strict` | Passed. | Active DWT-S5 change is structurally valid. |
| `openspec validate docworkflow-agent-delivery-testsuite --strict` | Passed. | Canonical accepted spec remains valid while DWT-S5 is active. |
| `ValidateChildReadiness.cs` for DWT-S5 | Passed. | Child Index, DWT-S5 handoff, verdict and write-set agree. |
| `git diff --check` | Passed. | Hardening edits have no whitespace errors. |

No runtime command or Docker/container command was executed as hardening acceptance proof. `run-l3-runtime-temp-repo-checks.sh` does not exist before DWT-S5 implementation. Its first successful syntax, preflight and `all --keep` executions are DWT-S5 delivery evidence, distinct from hardening rehearsal evidence.

## Definition of Ready for Implementation

- Parent coverage and conformance are explicit for `DWT-PR3`, `DWT-PR4` and `DWT-PR5`.
- Runner modes, synthetic fixture, output bundle, summary, telemetry, runtime gate and fallback/blocker contracts are normative.
- Retained DWT-S3 predecessor evidence is identified and validated as readable accepted `ran-target` proof.
- Fixture strategy is concrete and names implementation paths.
- Harness cases include positive, negative, blocked, fallback, local runtime, container/harness, closeout, style, telemetry and secret/redaction assertions.
- Allowed Write-Set and Shared/read-only Files are enforceable.
- Verification commands, success criteria and anti-loop rule are defined.
- OpenSpec change existed, validated before archive and is now archived.
- Persisted handoff exists and matches this spec and the Parent Child Index.
- `ValidateChildReadiness.cs` passes for DWT-S5 before delivery starts.

## Definition of Done / Closeout Evidence

- L3 runtime-temp-repo fixtures, validators, Promptfoo config and fallback/preflight runner exist.
- `run-l3-runtime-temp-repo-checks.sh preflight --keep` validates retained DWT-S3 evidence, fixture integrity and temp-repo setup without runtime execution.
- `run-l3-runtime-temp-repo-checks.sh all --keep` writes retained evidence under an isolated run directory.
- A real target run produces local runtime and container/harness evidence from the synthetic temp repo, or the DWT-S5 implementation remains blocked with reproducible blocker evidence.
- The accepted DWT-S5 summary uses DWT-S4 summary/telemetry/style fields and links assertion outputs.
- The harness proves DWT-S5-only kickoff, stale handoff block, temp repo isolation, local runtime gate, container/harness gate, closeout sync and Parent Coverage preservation.
- Parent Child Index links DWT-S5 implementation evidence and next action after closeout.
- OpenSpec change tasks and canonical spec are synchronized after acceptance/archive.
- No later child is released unless a later parent/orchestrator change creates one explicitly.
- No original source specs, KI-fuer-KMU repos or runtime repositories were described as runtime targets or modified.

## Dependencies and Write-Set

Allowed implementation write-set:

- `_specs/2026-05-08 DocWorkflow Agent Delivery Testsuite DWT-S5 L3 Runtime Temp-Repo Delivery Pilot.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`
- `_specs/child-session-handoffs/dwt-s5-session-handoff.md`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot/**`
- `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`
- `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/**`
- `tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh`
- `tests/docworkflow-agent-delivery/README.md`
- `tests/docworkflow-agent-delivery/testcases/tc2-single-child-delivery-next-handoff.md`

Shared/read-only files:

- `tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/dwt-s3-l2-summary.json`
- `tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/manifest.json`
- `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-l2-summary.json`
- `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/manifest.json`
- `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json`
- `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.bMyVlu/evidence/l1-summary.json`
- `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-reporting.CA7ryD/evidence/dwt-s4-reporting-summary.json`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S0 Framework Spike.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S1 L1 Deterministic Harness.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S2 L2 Parent-first Orchestration Agent Harness.md`
- `_specs/2026-05-08 DocWorkflow Agent Delivery Testsuite DWT-S3 L2 Single-Child Delivery Closeout Gate Harness.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S4 Summary Telemetry Style Reporting Contract.md`
- `_specs/child-session-handoffs/dwt-s0-session-handoff.md`
- `_specs/child-session-handoffs/dwt-s1-session-handoff.md`
- `_specs/child-session-handoffs/dwt-s2-session-handoff.md`
- `_specs/child-session-handoffs/dwt-s3-session-handoff.md`
- `_specs/child-session-handoffs/dwt-s4-session-handoff.md`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/**`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness/**`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness/**`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness/**`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s4-reporting-telemetry-contract/**`
- `tests/docworkflow-agent-delivery/l1/**`
- `tests/docworkflow-agent-delivery/l2/parent-first/**`
- `tests/docworkflow-agent-delivery/l2/single-child-closeout/**`
- `tests/docworkflow-agent-delivery/reporting/**`
- `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `docs/doc-workflow.md`
- `skills-repo/skills/**`
- KI-fuer-KMU original specs and runtime repositories

Parallel hardening / implementation:

- DWT-S5 implementation is not safe to run in parallel with another lane editing `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`, shared reporting validators, DWT-S3 retained evidence or the Parent Child Index.
- One integration owner must sync Parent Child Index and canonical OpenSpec changes during DWT-S5 closeout.
- Generated runtime target repos are per-run disposable artifacts under the DWT-S5 run directory and must not be committed as implementation outputs.

## Closeout Sync Targets

- Parent Child Index row `DWT-S5`.
- Archived OpenSpec change `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot/`.
- Canonical OpenSpec spec `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` after DWT-S5 acceptance/archive.
- DWT-S5 retained evidence path and README/testcase documentation.
- DWT-S5 child spec implementation and closeout evidence sections.
- DWT-S5 persisted handoff after closeout.
- Parent backlog/re-entry rule for any future child remains non-implementation-allowing until a new parent/orchestrator change creates that child explicitly.

## Child Session Handoff

Persisted handoff: `_specs/child-session-handoffs/dwt-s5-session-handoff.md`.

## Content Quality Review

- Correctness/domain fit: Pass. DWT-S5 owns L3 runtime temp-repo proof and does not re-prove L2 orchestration or closeout gates.
- Scope discipline: Pass. Runtime and Docker/container execution are implementation-time gates only; hardening did not execute them as acceptance proof.
- Completeness: Pass. Runner modes, outputs, fixture paths, cases, verification, write-set, OpenSpec and handoff are concrete.
- Consistency: Pass after Parent Child Index, handoff and archived OpenSpec sync.
- Testability: Pass. Implementation has deterministic fixture/validator paths plus explicit handling for real runtime pass versus blocked runtime.
- Blocking Marker: None after hardening verification passes.

## Implementation Evidence

- Implemented source-controlled synthetic runtime fixture, L3 validator, Promptfoo/Codex config, prompt and `run-l3-runtime-temp-repo-checks.sh`.
- Retained target evidence path: `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/evidence/2026-05-08-ran-target/dwt-s5-l3-summary.json`.
- Latest target run: `DWT_S5_ENABLE_AGENT=1 run-l3-runtime-temp-repo-checks.sh all --keep` passed DWT-S5-L3A through DWT-S5-L3F with `runner_mode: promptfoo-codex`, `agent_execution_status: ran-target`, `overall_runtime_proof_status: pass`, local runtime evidence and container/harness fixture evidence from the generated temp repo.
- Blocked-runtime rehearsal remains available at `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/evidence/2026-05-08-blocked-runtime/dwt-s5-l3-summary.json` as fallback-path evidence only.

## Closeout Evidence

- OpenSpec archived at `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot/`.
- Canonical OpenSpec spec updated at `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`.
- Parent Child Index, DWT-S5 handoff, README/testcase docs and retained DWT-S5 evidence links are synchronized.
- No descendant child is implementation-authorized by this closeout.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-08 | Codex | Hardened DWT-S5 into an implementation-ready L3 Runtime Temp-Repo Delivery Pilot child spec with synthetic fixture contract, runtime/container evidence contract, OpenSpec change and handoff/index sync. |
| 2026-05-08 | Codex | Implemented the DWT-S5 L3 synthetic temp-repo runner, fixtures, validators, Promptfoo/Codex config and retained blocked-runtime rehearsal evidence before target agent proof was enabled. |
| 2026-05-08 | Codex | Repaired the Promptfoo/Codex command contract, ran DWT-S5 target proof with `DWT_S5_ENABLE_AGENT=1`, and retained `ran-target` pass evidence for closeout. |
| 2026-05-08 | Codex | Accepted DWT-S5 and archived the OpenSpec change after verification replay and parent/handoff/evidence sync. |

SessionId: 2026-05-08-docworkflow-agent-delivery-testsuite-dwt-s5
