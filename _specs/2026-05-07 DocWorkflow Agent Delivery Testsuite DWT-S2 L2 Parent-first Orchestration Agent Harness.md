**Date:** 2026-05-08
**Status:** 🟢 Accepted
**Scope:** Implementation-ready child spec for the DWT-S2 L2 Parent-first Orchestration Agent Harness.

---

## Review Control Surface

- Spec-Variante: implementation-ready Child Spec.
- Goldstandard Status: accepted.
- Ziel: Einen L2-Harness definieren, der nachweist, dass ein grosser Parent/Master-Spec-Start nicht direkt implementiert wird, sondern ueber `spec-orchestrator` und `child-spec-hardening` zu Child Specs, exaktem Child Index, Coverage Matrix, Dependencies, Hardening Queue und mindestens einem validen naechsten Child-State fuehrt.
- In Scope: L2 Parent-first Agent-/Fallback-Runner-Vertrag, Promptfoo-first Codex-Probe mit S0-Limitations, fallback artifact runner for blocked-agent evidence, parent-only oversized fixture, generated child-control outputs, thin-child negative output, ready-child positive output, DWT-S4-compatible summary/telemetry/style evidence, TC1D/TC1A/TC1E coverage, OpenSpec active change, Parent Child Index and persisted handoff sync.
- Out of Scope: DWT-S2 runner implementation during hardening, live agent execution during hardening, runtime delivery, DWT-S3/DWT-S5 implementation or release, S0/S1/S4 archive mutation, KI-fuer-KMU original repo writes, OpenSpec archive before DWT-S2 implementation evidence exists.
- Wichtigste Test-/Harness-Cases: `DWT-S2-L2A oversized parent refuses direct implementation`, `DWT-S2-L2B parent-only orchestration produces child control surface`, `DWT-S2-L2C thin generated child cannot become ready`, `DWT-S2-L2D hardenable child reaches exactly one valid next child state`, `DWT-S2-L2E blocked agent path is reported as blocker rather than pass`, `DWT-S2-L2F DWT-S4 reporting/style/efficiency contract is honored`.
- Wichtigste Verification Commands: retained DWT-S0/S1/S4 evidence presence and JSON parse checks; `bash -n` for existing L0/L1/reporting scripts; active-change `openspec validate docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness --strict`; canonical `openspec validate docworkflow-agent-delivery-testsuite --strict`; DWT-S2 `ValidateChildReadiness.cs`; `git diff --check`; after implementation, `bash -n tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh`, `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh all --keep`, `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all`, and `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen. Promptfoo remains the primary L2 agent-runner path from DWT-S0; DWT-S2 closeout accepted real `ran-target` agent evidence. Fallback artifact mode may only produce deterministic contract evidence or a reproducible blocked-agent result, never a false pass.
- Readiness Status: IMPLEMENTATION READY.

## Goal

Create the implementation contract for an L2 Parent-first Orchestration Agent Harness. The harness must prove that a large parent/master spec is routed through parent-first orchestration and child hardening instead of direct implementation.

The implementation must distinguish three outcomes:

- `pass`: a real agent/coding-agent run produced the parent-first control surface and deterministic validators accepted it.
- `blocked`: the agent path could not run for a reproducible auth, provider, runtime or network reason, and fallback artifact mode proved only the deterministic contracts.
- `fail`: the agent or artifact output attempted direct implementation, skipped child controls, released a skeleton child, hid evidence, or violated style/efficiency gates.

## In Scope

- Add source-controlled L2 fixture definitions under `tests/docworkflow-agent-delivery/l2/parent-first/fixtures/`.
- Add L2 validators under `tests/docworkflow-agent-delivery/l2/parent-first/validators/`.
- Add primary Promptfoo/Codex runner config and command wrapper under `tests/docworkflow-agent-delivery/l2/parent-first/`.
- Add fallback artifact runner mode to validate stored outputs when the agent runner is blocked.
- Add `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh`.
- Emit DWT-S4-compatible summary and telemetry artifacts.
- Update `tests/docworkflow-agent-delivery/README.md` and `tests/docworkflow-agent-delivery/testcases/tc1-parent-first-orchestration-child-hardening.md` with the L2 boundary.
- Keep original KI-fuer-KMU specs and runtime repositories read-only.

## Out of Scope

- No DWT-S2 implementation during this hardening run.
- No live agent run during this hardening run.
- No DWT-S3 single-child delivery/closeout gate harness.
- No DWT-S5 runtime temp-repo delivery pilot.
- No runtime delivery, Docker, deployment, credential copying into repo files, or KI-fuer-KMU original repo writes.
- No OpenSpec archive until DWT-S2 implementation evidence exists and closeout runs.
- No mutation of accepted DWT-S0, DWT-S1 or DWT-S4 archives.

## Parent/Master Coverage

| Parent Requirement | Child Coverage |
|---|---|
| `DWT-PR1` | Owns the L2 proof that an oversized parent is not directly implemented and instead yields Child Specs, exact Child Index, Coverage Matrix, Dependencies, Hardening Queue and at least one valid next child state. |
| `DWT-PR2` | Reuses S1 readiness gate rules to prove thin child skeletons cannot become implementation-ready and that ready output requires conformance, write-set, handoff and validator consistency. |
| `DWT-PR5` | Requires provenance, source hashes/stable IDs, DWT-S4 evidence truth labels, no fixture-normalization hiding and no stale output reuse. |
| `DWT-PR7` | Emits DWT-S4-compatible style and efficiency telemetry for agent/tool/read behavior and follow-up usability. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `DWT-PR1` | L2 must run or reproducibly block a parent-first agent path and must validate generated child-control artifacts. | preserves | Implement Promptfoo-first runner plus deterministic validators for child specs, index, coverage matrix, dependencies, hardening queue and next state. |
| `DWT-PR2` | L2 output cannot mark a skeleton ready unless hardening gates and `ValidateChildReadiness.cs` pass for the generated ready child fixture/output. | preserves | Reuse S1 readiness semantics and require positive/negative readiness cases. |
| `DWT-PR5` | L2 evidence must distinguish real agent output, fallback artifact validation, stale copied outputs and blocked provider/auth/network cases. | preserves | Emit DWT-S4 truth labels, source provenance and blocked-agent status fields. |
| `DWT-PR7` | L2 must make style/usability and efficiency drift machine-readable, not prose-only. | preserves | Emit `agent-run-manifest.json`, style verdicts and efficiency verdicts compatible with DWT-S4. |
| `DWT-PR3` | DWT-S2 may identify a valid next child state, but must not kick off delivery. | narrows_with_rationale | DWT-S3 owns single-child delivery and closeout gate proof. |
| `DWT-PR4` | DWT-S2 may leave next-child handoff candidates as output artifacts, but must not claim post-closeout gating. | narrows_with_rationale | DWT-S3 owns closeout sync and stale next-handoff blocking. |

## Decision Freeze Pack

| Entscheidung | Freeze |
|---|---|
| Primary agent runner | Promptfoo `0.121.9` with bundled Node `v24.14.0`, reusing the accepted DWT-S0 command contract and explicit auth/network limitations. |
| Fallback runner | Deterministic artifact mode under the DWT-S2 script validates stored output bundles and may report `blocked_agent`; it cannot produce a DWT-S2 acceptance `pass` without `agent_execution_status: ran-target`. |
| Required proof shape | Parent-only oversized input must produce child-control artifacts and no runtime implementation edits. |
| Output status vocabulary | `pass`, `fail`, `blocked`, `warn`, `planned`. |
| Evidence truth vocabulary | `ran-target`, `ran-rehearsal`, `blocked`, `failed`, `planned`, `dry-run`. |
| Agent execution status vocabulary | `ran-target`, `blocked_auth`, `blocked_provider`, `blocked_network`, `blocked_runtime`, `failed`, `not-run`. |
| Valid next child state vocabulary | `ready_for_hardening`, `implementation_ready`, `blocked_by_dependency`, `needs_user_decision`, `needs_hardening`. |
| Reporting contract | New DWT-S2 summaries use `schema_id: docworkflow-agent-delivery-summary.v1` and DWT-S4 telemetry/style/efficiency semantics. |
| Original repos | KI-fuer-KMU original specs and runtime repositories remain read-only. |
| Descendant release | DWT-S2 may release only its own implementation. DWT-S3 and DWT-S5 remain unreleased until their own hardening/handoff gates pass. |

## Normative Contract

### L2 Runner Modes

The DWT-S2 implementation must provide `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh` with these selectors:

| Selector | Required Behavior |
|---|---|
| `all` | Runs all DWT-S2 L2A-L2F assertions and writes a DWT-S2 summary. |
| `agent` | Uses Promptfoo/Codex when credentials/provider/runtime are provisioned; stores raw output, telemetry and deterministic validation output. |
| `fallback` | Uses stored artifact fixtures only; may prove validator behavior and blocked-agent reporting, but cannot mark DWT-S2 accepted as agent proof. |
| `validate-output` | Validates an existing output bundle path without launching an agent. |
| `style` | Runs DWT-S4-compatible style/usability assertions for DWT-S2 output. |
| `telemetry` | Runs DWT-S4-compatible efficiency/telemetry assertions for DWT-S2 output. |

The runner must accept `--run-dir DIR`, `--keep`, and `--output-bundle DIR` where applicable. Every run must write evidence under `<run-dir>/evidence/`.

### Agent Prompt Contract

The primary agent prompt must:

- provide the parent/master spec path as the leading input;
- instruct the agent to apply Spec Sizing Gate and choose `spec-orchestrator` before implementation;
- explicitly forbid runtime implementation, direct parent-as-child delivery, Docker, deployment, credential copy and KI-fuer-KMU original writes;
- require child specs/skeletons, exact Child Index, Coverage Matrix, Dependencies, Hardening Queue and next child state output;
- require provenance for generated child-control artifacts;
- require a concise final handoff/status output for deterministic parsing.

The prompt must not ask the agent to implement runtime code. Any runtime edit attempt is a failing forbidden action.

### Output Bundle Contract

Each L2 output bundle must contain:

| Path | Required Semantics |
|---|---|
| `source-manifest.json` | Source parent path, stable source id or hash, copied fixture paths, generated artifact paths and declared normalizations. |
| `agent-output.md` | Raw or normalized agent final output. Must preserve enough detail to audit route choice and generated artifacts. |
| `child-index.md` | Exact operational Child Index header and generated rows. |
| `coverage-matrix.md` | Mapping from parent requirements to child ids and evidence intent. |
| `dependencies.md` | Dependency graph or ordered dependency table for generated children. |
| `hardening-queue.md` | Queue entries with child id, required hardening, dependencies and next action. |
| `child-specs/` | Generated child specs or skeletons. |
| `child-session-handoffs/` | Generated handoff candidates when a child reaches `implementation_ready`; skeleton children may omit handoffs only when their next state is not implementation-allowing. |
| `agent-run-manifest.json` | DWT-S4-compatible telemetry manifest for commands, reads, tool calls, forbidden classes, budgets and efficiency verdict. |
| `evidence/dwt-s2-l2-summary.json` | DWT-S4-compatible summary with DWT-S2 case results and evidence links. |

### DWT-S2 Summary Contract

`evidence/dwt-s2-l2-summary.json` must be JSON with:

| Field | Required Semantics |
|---|---|
| `schema_id` | `docworkflow-agent-delivery-summary.v1`. |
| `suite_level` | `DWT-S2`. |
| `suite_version` | Stable local version string. |
| `repo_root` | Absolute shared-ai-docs path. |
| `fixture_root` | Absolute isolated L2 run or fixture path. |
| `fixture_manifest` | Path or object reference to `source-manifest.json`. |
| `runner_mode` | `promptfoo-codex` or `fallback-artifact`. |
| `agent_execution_status` | One of the frozen agent execution statuses. |
| `test_results` | Object keyed by DWT-S2 case id with frozen status vocabulary values. |
| `evidence_truth` | Object keyed by DWT-S2 case id with frozen truth labels. |
| `evidence_links` | Paths to output bundle, assertions, telemetry and blocked-agent evidence when present. |
| `runner_environment` | OS, shell, node/promptfoo versions when used and credential provisioning status without secret values. |
| `provenance_checks` | Source/copy/generated/normalization assertions. |
| `readiness_checks` | Child Index, handoff, write-set, next-state and validator assertions. |
| `style_verdicts` | Per-case `pass`, `fail` or `warn`. |
| `telemetry_verdicts` | Per-case `pass`, `fail`, `warn` or `blocked`. |
| `forbidden_actions_observed` | Empty for pass; populated for expected negative/failing cases. |

Acceptance rule: `runner_mode: fallback-artifact` with `agent_execution_status` other than `ran-target` can pass deterministic validators, but the overall DWT-S2 evidence must be `blocked` rather than accepted workflow proof.

### Valid Next Child State Contract

The generated orchestration output must identify exactly one leading next child recommendation and may list additional queued children. A valid leading state is:

| State | Required Meaning |
|---|---|
| `ready_for_hardening` | Child skeleton is coherent enough for `child-spec-hardening`, but not implementation-ready. |
| `implementation_ready` | Child has parent conformance, concrete write-set, persisted handoff, command rehearsal evidence and passes `ValidateChildReadiness.cs`. |
| `blocked_by_dependency` | Child is blocked by named predecessor evidence. |
| `needs_user_decision` | Child requires a named decision before hardening or delivery. |
| `needs_hardening` | Child needs contract/case/write-set/verification depth before delivery. |

The L2 validator must fail if an output identifies no next child, multiple leading next children, a skeleton with `implementation_ready`, or an implementation-ready child without matching handoff and validator evidence.

## Canonical Examples and Fixtures

Use referenced fixture files. No embedded machine-readable JSON/YAML/TOML/schema example in this spec is normative input.

Required implementation fixture paths:

| Fixture | Purpose | Normative Fields / Values | Implementation Timing |
|---|---|---|---|
| `tests/docworkflow-agent-delivery/l2/parent-first/fixtures/oversized-parent-only/` | Parent-only oversized input for agent prompt. | Start state contains parent/master spec only; no generated child-control artifacts before the run. | Create during DWT-S2 implementation. |
| `tests/docworkflow-agent-delivery/l2/parent-first/fixtures/valid-orchestration-output/` | Positive output bundle with child control surface. | Contains child specs, exact Child Index, Coverage Matrix, Dependencies, Hardening Queue and one leading next child. | Create during DWT-S2 implementation as fallback/validator fixture; real agent output must be stored separately when available. |
| `tests/docworkflow-agent-delivery/l2/parent-first/fixtures/direct-implementation-attempt/` | Negative output bundle. | Contains runtime/direct implementation attempt and must fail. | Create during DWT-S2 implementation. |
| `tests/docworkflow-agent-delivery/l2/parent-first/fixtures/thin-child-ready-claim/` | Negative child readiness output. | Skeleton claims implementation readiness without conformance/write-set/handoff/validator evidence and must fail or block. | Create during DWT-S2 implementation. |
| `tests/docworkflow-agent-delivery/l2/parent-first/fixtures/ready-child-output/` | Positive ready-child next-state fixture. | Exactly one generated child may be `implementation_ready` only with concrete write-set, handoff and validator output. | Create during DWT-S2 implementation. |
| `tests/docworkflow-agent-delivery/l2/parent-first/fixtures/blocked-agent-output/` | Fallback blocker fixture. | Records blocked auth/provider/network/runtime status and must not be reported as accepted agent proof. | Create during DWT-S2 implementation. |
| `tests/docworkflow-agent-delivery/l2/parent-first/fixtures/style-efficiency-output/` | Reporting fixture. | Uses DWT-S4 summary/telemetry/style fields and forbidden command classes. | Create during DWT-S2 implementation. |

Harness verification must prove each fixture was exercised by linking per-fixture assertion output from `dwt-s2-l2-summary.json`.

## Control Flow and Failure Cases

1. Create isolated L2 run directory.
2. Copy or synthesize a parent-only oversized fixture; record source identity and declared normalizations.
3. If `agent` or `all` with available agent prerequisites, run Promptfoo/Codex using bundled Node and isolated caches.
4. If the agent runner is blocked, store a blocker output and run fallback artifact validators only.
5. Validate output bundle shape and provenance.
6. Validate no direct implementation or forbidden command class occurred.
7. Validate exact Child Index header, generated child ids, Coverage Matrix, Dependencies and Hardening Queue.
8. Validate next child state and readiness gate behavior.
9. Validate DWT-S4-compatible summary, style and telemetry fields.
10. Return non-zero when a positive proof fails, a negative fixture passes, a fallback blocker is mislabeled as pass, or a forbidden action is observed.

Failure states:

- `direct_parent_implementation`
- `missing_child_control_surface`
- `invalid_child_index_header`
- `missing_coverage_matrix`
- `missing_dependencies`
- `missing_hardening_queue`
- `missing_or_ambiguous_next_child_state`
- `skeleton_released_as_ready`
- `missing_ready_child_handoff`
- `readiness_validator_missing_or_failed`
- `stale_or_unprovenanced_output`
- `blocked_agent_misreported_as_pass`
- `forbidden_runtime_or_repo_write`
- `invalid_dwt_s4_summary_or_telemetry`
- `secret_or_credential_leak`

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `DWT-S2-L2A` | Oversized parent refuses direct implementation. | `oversized-parent-only`; agent or fallback output. | `pass` only when no runtime/direct implementation edits are present. | Source manifest, raw output, forbidden-action assertion. | No KI-fuer-KMU write, Docker, deployment, runtime build/test or credential copy. |
| `DWT-S2-L2B` | Parent-only orchestration produces child control surface. | `valid-orchestration-output`. | `pass` when child specs, exact Child Index, Coverage Matrix, Dependencies and Hardening Queue exist. | Generated child-control artifacts and provenance assertions. | Copied old child index without provenance fails. |
| `DWT-S2-L2C` | Thin generated child cannot become ready. | `thin-child-ready-claim`. | Expected fixture result `fail` or `blocked`; runner overall passes only by detecting the blocker. | Readiness assertion output. | Skeleton cannot name `spec-change-delivery` as next action. |
| `DWT-S2-L2D` | Hardenable child reaches exactly one valid next child state. | `ready-child-output`. | `pass` only with one leading next child and validator/handoff/write-set consistency when state is `implementation_ready`. | Next-state assertion, handoff pointer and validator output. | Multiple leading children or missing handoff fails. |
| `DWT-S2-L2E` | Blocked agent path is honest. | `blocked-agent-output` or real blocked Promptfoo run. | `blocked` for agent proof; deterministic validators may pass fallback checks. | Blocker log and summary status. | `blocked_auth`, `blocked_provider`, `blocked_network` or `blocked_runtime` cannot be reported as `pass`. |
| `DWT-S2-L2F` | DWT-S4 reporting/style/efficiency contract is honored. | `style-efficiency-output` plus generated summary/telemetry. | `pass`, `warn` or expected negative status per fixture. | `dwt-s2-l2-summary.json`, `agent-run-manifest.json`, style/efficiency assertions. | No secret values in telemetry; DWT-S3/DWT-S5 remain unreleased. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `bash` or `zsh`
- Node for Promptfoo path: `/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`
- Promptfoo package: `promptfoo@0.121.9`
- Platform: macOS authoring, Linux-compatible shell where practical
- Runtime assumptions: DWT-S2 implementation may require Codex/Promptfoo credentials for `pass`; without them it must produce `blocked` evidence and fallback validator output, not accepted agent proof.

Pre-implementation hardening verification and command-contract rehearsal:

```sh
test -f tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json
node -e "JSON.parse(require('fs').readFileSync('tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json','utf8'))"
test -f /var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.bMyVlu/evidence/l1-summary.json
node -e "JSON.parse(require('fs').readFileSync('/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.bMyVlu/evidence/l1-summary.json','utf8'))"
test -f /var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-reporting.CA7ryD/evidence/dwt-s4-reporting-summary.json
node -e "JSON.parse(require('fs').readFileSync('/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-reporting.CA7ryD/evidence/dwt-s4-reporting-summary.json','utf8'))"
bash -n tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh
bash -n tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh
PATH="/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH" node --version
openspec validate docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness --strict
openspec validate docworkflow-agent-delivery-testsuite --strict
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md" \
  --child DWT-S2 \
  --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/dwt-s2-session-handoff.md"
git -C /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs diff --check
```

Gate verification after DWT-S2 implementation creates the runner, config, validators and fixtures:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh
tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh all --keep
tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all
openspec validate docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness --strict
openspec validate docworkflow-agent-delivery-testsuite --strict
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md" \
  --child DWT-S2 \
  --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/dwt-s2-session-handoff.md"
```

Success criteria:

- Active DWT-S2 OpenSpec change validates strictly.
- Canonical accepted OpenSpec spec remains valid while DWT-S2 is active.
- `ValidateChildReadiness.cs` passes for DWT-S2 before delivery starts.
- Existing L0, L1 and DWT-S4 reporting gates remain runnable and do not become hidden dependencies for false L2 proof.
- After implementation, `run-l2-parent-orchestration-checks.sh all --keep` exits `0` only when positive, negative, blocked, fallback and reporting cases match expected statuses.
- DWT-S2 acceptance evidence includes `agent_execution_status: ran-target`. If the agent path is blocked, the implementation result remains blocked and is not accepted as L2 proof.
- DWT-S3 and DWT-S5 remain unreleased unless their own later hardening and handoff gates change them.

Anti-loop rule: DWT-S2 validators must inspect output bundles, source manifests, child-control artifacts, readiness evidence, summaries and telemetry. They must not pass by checking only that command strings or documentation sections exist.

## Command-Contract Rehearsal Evidence

Performed during hardening on 2026-05-08:

| Rehearsal | Result | Meaning |
|---|---|---|
| DWT-S0 `spike-summary.json` presence and JSON parse | Passed. | Promptfoo-first accepted context is available and reports `ADOPT_WITH_LIMITATIONS`. |
| Retained DWT-S1 `l1-summary.json` presence and JSON parse | Passed. | Deterministic readiness/provenance baseline is available. |
| Retained DWT-S4 reporting summary presence and JSON parse | Passed. | Summary/telemetry/style contract evidence is available. |
| Existing L0/L1/reporting shell syntax | Passed. | Predecessor runner command contracts are syntactically valid. |
| Bundled Node `node --version` | Passed and reported `v24.14.0`. | S0's Promptfoo runtime selection remains available. |
| `openspec validate docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness --strict` | Passed. | Active DWT-S2 change is structurally valid. |
| `openspec validate docworkflow-agent-delivery-testsuite --strict` | Passed. | Canonical accepted spec remains valid while DWT-S2 is active. |
| `ValidateChildReadiness.cs` for DWT-S2 | Passed. | Child Index, DWT-S2 handoff, verdict and write-set agree. |
| `git diff --check` | Passed. | Hardening edits have no whitespace errors. |

`run-l2-parent-orchestration-checks.sh` does not exist before DWT-S2 implementation. Its first successful syntax and `all --keep` executions are DWT-S2 delivery evidence, distinct from hardening rehearsal evidence.

## Implementation Evidence

| Evidence | Result | Meaning |
|---|---|---|
| `bash -n tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh` | Passed. | DWT-S2 runner syntax is valid. |
| `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh all --keep` | Passed with retained evidence `tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-l2-summary.json`. | Promptfoo/Codex and deterministic positive, negative, blocked, style and telemetry bundle assertions pass. |
| L2 agent proof status | Passed: `runner_mode: promptfoo-codex`; `agent_execution_status: ran-target`; `overall_agent_proof_status: pass`. | Accepted L2 agent proof exists; DWT-S3 and DWT-S5 remain unreleased. |

## Closeout Evidence

| Evidence | Result | Meaning |
|---|---|---|
| Retained S0/S1/S4/S2 evidence presence and JSON parse | Passed. | Accepted baselines and fresh DWT-S2 retained summary are readable. |
| `bash -n` for L0/L1/S4/L2 scripts | Passed. | Script command contracts are syntactically valid. |
| Bundled Node version | Passed: `v24.14.0`. | Promptfoo/Codex runner uses the expected bundled runtime. |
| Active DWT-S2 OpenSpec strict validate | Passed before archive. | Active change was valid before closure. |
| Canonical OpenSpec strict validate | Passed before and after archive. | Canonical testsuite spec is valid. |
| DWT-S2 child readiness validator | Passed. | Parent Child Index, DWT-S2 handoff and write-set agree. |
| `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all` | Passed. | DWT-S4 reporting contract remains green. |
| `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all` | Passed. | L0/TC1/TC2 harness and reporting integration remain green. |
| `git diff --check` | Passed. | Closeout edits have no whitespace errors. |
| OpenSpec archive | Passed: `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness/`. | DWT-S2 delta is archived into the canonical spec. |

## Definition of Ready for Implementation

- Parent coverage and conformance are explicit for `DWT-PR1`, `DWT-PR2`, `DWT-PR5` and `DWT-PR7`.
- Runner modes, output bundle, summary, telemetry, next-state and fallback/blocker contracts are normative.
- Fixture strategy is concrete and names implementation paths.
- Harness cases include positive, negative, blocked, fallback, style, telemetry and secret/redaction assertions.
- Allowed Write-Set and Shared/Read-only Files are enforceable.
- Verification commands, success criteria and anti-loop rule are defined.
- Active OpenSpec change exists and validates.
- Persisted handoff exists and matches this spec and the Parent Child Index.
- `ValidateChildReadiness.cs` passes for `DWT-S2` before delivery starts.

## Definition of Done / Closeout Evidence

- L2 parent-first fixtures, validators, Promptfoo config and fallback artifact runner exist.
- `run-l2-parent-orchestration-checks.sh all --keep` writes retained evidence under an isolated run directory.
- A real agent run produces accepted `ran-target` evidence, or the DWT-S2 implementation remains blocked with reproducible blocker evidence.
- The accepted DWT-S2 summary uses DWT-S4 summary/telemetry/style fields and links assertion outputs.
- The harness proves no direct implementation, exact child-control surface generation, thin-child readiness block and exactly one valid next child state.
- Parent Child Index links DWT-S2 implementation evidence and next action after closeout.
- OpenSpec change tasks and canonical spec are synchronized after acceptance/archive.
- DWT-S3 and DWT-S5 remain unreleased unless their own later hardening gates pass.
- No original source specs, KI-fuer-KMU repos or runtime repositories were modified.

## Dependencies and Write-Set

Allowed implementation write-set:

- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S2 L2 Parent-first Orchestration Agent Harness.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`
- `_specs/child-session-handoffs/dwt-s2-session-handoff.md`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness/**`
- `tests/docworkflow-agent-delivery/l2/parent-first/**`
- `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh`
- `tests/docworkflow-agent-delivery/README.md`
- `tests/docworkflow-agent-delivery/testcases/tc1-parent-first-orchestration-child-hardening.md`

Shared/read-only files:

- `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json`
- `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.bMyVlu/evidence/l1-summary.json`
- `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-reporting.CA7ryD/evidence/dwt-s4-reporting-summary.json`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S0 Framework Spike.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S1 L1 Deterministic Harness.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S4 Summary Telemetry Style Reporting Contract.md`
- `_specs/child-session-handoffs/dwt-s0-session-handoff.md`
- `_specs/child-session-handoffs/dwt-s1-session-handoff.md`
- `_specs/child-session-handoffs/dwt-s4-session-handoff.md`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/**`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness/**`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s4-reporting-telemetry-contract/**`
- `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`
- `tests/docworkflow-agent-delivery/l1/**`
- `tests/docworkflow-agent-delivery/reporting/**`
- `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `docs/doc-workflow.md`
- `skills-repo/skills/**`
- KI-fuer-KMU original specs and runtime repositories

Parallel hardening / implementation:

- DWT-S2 implementation is not safe to run in parallel with another lane editing `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh` or shared reporting validators.
- DWT-S3 may be hardened separately as a spec-only lane after DWT-S2 output contract is stable, but DWT-S3 implementation remains blocked until DWT-S2 evidence exists.
- DWT-S5 remains blocked until DWT-S2 and DWT-S3 are accepted.

## Closeout Sync Targets

- Parent Child Index row `DWT-S2`.
- Archived OpenSpec change `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness/`.
- Canonical OpenSpec spec `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` after DWT-S2 acceptance/archive.
- DWT-S2 retained evidence path and README/testcase documentation.
- DWT-S3 dependency row may be unblocked only by later closeout or orchestrator sync after accepted DWT-S2 evidence exists.
- DWT-S5 remains blocked.

## Child Session Handoff

Persisted handoff: `_specs/child-session-handoffs/dwt-s2-session-handoff.md`.

## Content Quality Review

- Correctness/domain fit: Pass. DWT-S2 owns L2 parent-first orchestration proof and does not claim delivery/closeout/runtime proof.
- Scope discipline: Pass. Runner implementation, live agents, DWT-S3, DWT-S5 and runtime delivery remain out of hardening scope.
- Completeness: Pass. Runner modes, outputs, fixture paths, cases, verification, write-set, OpenSpec and handoff are concrete.
- Consistency: Pass after Parent Child Index, handoff and active OpenSpec sync.
- Testability: Pass. Implementation has deterministic fixture/validator paths plus explicit handling for real agent pass versus blocked fallback.
- Blocking Marker: None after hardening verification passes.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-08 | Codex | Hardened DWT-S2 into an implementation-ready L2 Parent-first Orchestration Agent Harness child spec with runner/fallback contract, fixtures, verification, OpenSpec change and handoff/index sync. |
| 2026-05-08 | Codex | Implemented DWT-S2 L2 fixtures, validator, Promptfoo config, fallback runner and retained deterministic evidence; live agent proof remained blocked until auth was provisioned. |
| 2026-05-08 | Codex | Accepted DWT-S2 after real Promptfoo/Codex `ran-target` evidence passed, closeout verification replay was green, and OpenSpec archived into the canonical testsuite spec. |

SessionId: 2026-05-08-docworkflow-agent-delivery-testsuite-dwt-s2
