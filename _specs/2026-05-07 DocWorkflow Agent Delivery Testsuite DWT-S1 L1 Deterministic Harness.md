**Date:** 2026-05-07  
**Status:** 🔵 Implemented  
**Scope:** Implementation-ready child spec for the DWT-S1 deterministic L1 contract harness.

---

## Review Control Surface

- Spec-Variante: implementation-ready Child Spec.
- Goldstandard Status: candidate.
- Ziel: Deterministische L1-Checks fuer Parent-only Orchestration-Fixtures, Child-Hardening-Gates und Evidence-Provenance schaffen, ohne Agent-Runner, Promptfoo-Erfolg oder Runtime-Delivery vorauszusetzen.
- In Scope: L1 Fixture-Builder, Manifest-/Provenance-Validator, Child-Index-/Handoff-/Readiness-Validator, negative Skeleton-Fixtures, TC1A/TC1B/TC1C statische Gate-Regressionen, Integration in den bestehenden L0-Harness.
- Out of Scope: Agentische L2-Ausfuehrung, Promptfoo-/Inspect-/Codex-Runner, Runtime-Delivery, KI-fuer-KMU-Originalaenderungen, S3/S4 echte Closeout-Ausfuehrung, Framework-Re-Evaluation.
- Wichtigste Test-/Harness-Cases: `DWT-S1-L1A parent-only fixture has no child artifacts at start`, `DWT-S1-L1B generated child index must be new/provenanced`, `DWT-S1-L1C thin skeleton cannot pass readiness`, `DWT-S1-L1D high-risk command without rehearsal blocks`, `DWT-S1-L1E hidden normalization fails`, `DWT-S1-L1F S0 limitations do not become L1 assumptions`.
- Wichtigste Verification Commands: `bash -n tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh`; `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all`; `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all`; `openspec validate docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness --strict`; `openspec validate docworkflow-agent-delivery-testsuite --strict`; `ValidateChildReadiness.cs`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen. L1 ist absichtlich deterministic-only; S0 `ADOPT_WITH_LIMITATIONS` bleibt fuer spaetere Promptfoo-/Codex-Agent-Slices relevant, erzeugt aber keine L1-Agent- oder Auth-Abhaengigkeit.
- Readiness Status: IMPLEMENTATION READY.

## Goal

Create a deterministic L1 harness layer that proves contract/gate logic against synthetic or temp fixtures. L1 must not claim that agent orchestration happened; it only proves machine-checkable gates that L2 will later reuse.

## In Scope

- Add L1 fixture definitions and validators under `tests/docworkflow-agent-delivery/l1/`.
- Add a narrow L1 runner script at `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh`.
- Add fixture manifest, provenance, child-readiness and forbidden-action assertions for the L1A-L1F cases.
- Extend existing test documentation only where needed to describe L1 boundaries.
- Keep original KI-fuer-KMU specs read-only.

## Out of Scope

- No Promptfoo, Inspect AI or Codex agent execution.
- No L2/L3 implementation.
- No runtime repository writes except isolated temp fixture stubs.
- No changes to accepted DWT-S0 artifacts except read-only use of its result as a dependency.
- No S2/S3/S5 unblocking; they remain dependency-blocked until their own prerequisites are satisfied.

## Parent/Master Coverage

| Parent Requirement | Child Coverage |
|---|---|
| `DWT-PR1` | Validates parent-only start-state and required child-control artifacts as deterministic contracts without claiming agent-generated orchestration. |
| `DWT-PR2` | Validates that thin skeletons, missing conformance, missing write-set, missing handoff and missing rehearsal evidence block readiness. |
| `DWT-PR5` | Validates fixture manifest, provenance, stale source artifact and hidden-normalization failure behavior. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `DWT-PR1` | L1 checks contract shape but does not claim agent-generated orchestration. | narrows_with_rationale | L2 proof remains in `DWT-S2`, which stays dependency-blocked. |
| `DWT-PR2` | L1 enforces negative readiness gates and reuses the shared readiness validator where possible. | preserves | Ready claims require index, handoff, write-set and validator consistency. |
| `DWT-PR5` | L1 rejects hidden fixture normalization, stale source artifacts and fake evidence. | preserves | Add manifest/provenance assertions and evidence truth labels. |
| `DWT-PR6` | S0 selected Promptfoo with limitations, but L1 does not invoke Promptfoo. | preserves | Record the S0 result as dependency context only; do not require Codex auth or npm registry connectivity for L1. |

## Decision Freeze Pack

| Entscheidung | Freeze |
|---|---|
| Harness type | Shell plus deterministic validators; no agent runner. |
| Fixture root | Temp directories under `/tmp/docworkflow-agent-delivery-l1.*` plus source-controlled tiny fixtures under `tests/docworkflow-agent-delivery/l1/fixtures/`. |
| Positive status vocabulary | `pass`, `fail`, `blocked`, `warn`. |
| Evidence truth vocabulary | `ran-target`, `ran-rehearsal`, `blocked`, `failed`, `planned`, `dry-run`. |
| Original specs | Read-only; copied or synthetic fixture files only. |
| S0 dependency interpretation | `ADOPT_WITH_LIMITATIONS` confirms Promptfoo remains primary for later agent slices, but L1 must be runnable without Codex credentials, Promptfoo, isolated npm cache or network registry access. |
| Blocked descendants | `DWT-S2`, `DWT-S3` and `DWT-S5` stay `BLOCKED BY DEPENDENCY`; DWT-S1 may only supply deterministic validators for their later use. |

## Normative Contract

### L1 Runner Contract

The L1 runner must accept at least `all` and case-specific selectors for `l1a`, `l1b`, `l1c`, `l1d`, `l1e` and `l1f`. It must write evidence to an isolated run directory and must print or persist that directory path so a later reviewer can inspect the retained evidence when `--keep` or an equivalent debug mode is used.

The runner must not invoke these command classes:

- Promptfoo, Inspect AI or Codex/agent providers.
- Docker, container runtime or runtime repository build/test commands.
- Any command that writes into KI-fuer-KMU original specs or runtime repositories.

### L1 Summary

The L1 runner must write `evidence/l1-summary.json` in the retained or temp fixture with:

| Field | Required |
|---|---|
| `suite_level` | Must be `L1`. |
| `suite_version` | Spec or harness version, commit, or stable local version string. |
| `repo_root` | Absolute shared-ai-docs path used by the run. |
| `fixture_root` | Absolute temp or retained fixture path. |
| `fixture_manifest` | Path to manifest used by assertions. |
| `test_results` | Per-case `pass`, `fail`, `blocked`, or `warn`. |
| `provenance_checks` | Source, copied, removed and normalized file assertions. |
| `readiness_checks` | Child Index, handoff, write-set and readiness verdict assertions. |
| `forbidden_actions_observed` | Must be an empty array for pass. |
| `evidence_truth` | Per-case truth label from the frozen vocabulary. |
| `s0_dependency_context` | Must record `ADOPT_WITH_LIMITATIONS` and state that no Promptfoo/Codex auth was required for L1. |

### Fixture Manifest Contract

Each L1 fixture manifest must record:

| Field | Required |
|---|---|
| `fixture_id` | Stable fixture id, e.g. `parent-only` or `thin-child-skeleton`. |
| `source_files` | Original or synthetic sources with path and hash or stable version marker. |
| `copied_files` | Files copied into the fixture. |
| `generated_files` | Files generated by fixture setup. |
| `removed_from_start_state` | Child Index, Child Specs or Handoffs intentionally absent from parent-only starts. |
| `normalizations` | Every transformation applied to fixture copies. Empty when none were applied. |
| `forbidden_source_write_paths` | Original paths that must not be written. |

### Blocking Rules

- A parent-only start fixture containing Child Index, Child Specs or Handoffs fails `DWT-S1-L1A`.
- A generated child-control surface without provenance, source hash/version marker or output path fails `DWT-S1-L1B`.
- A ready verdict with missing Parent Conformance, concrete write-set, persisted handoff or command rehearsal evidence fails `DWT-S1-L1C`/`DWT-S1-L1D`.
- Any normalization not listed in `fixture-manifest.json` fails `DWT-S1-L1E`.
- Any L1 implementation that requires Promptfoo, Codex credentials, isolated npm registry access or S0 runner evidence fails `DWT-S1-L1F`.

## Canonical Examples and Fixtures

Use referenced fixture files. The fixtures are in implementation scope and must be exercised by the L1 runner:

| Fixture | Purpose | Normative Fields / Values |
|---|---|---|
| `tests/docworkflow-agent-delivery/l1/fixtures/parent-only/` | Parent-only fixture with no child artifacts. | Manifest must list removed child artifacts; start state must not contain child index/spec/handoff files. |
| `tests/docworkflow-agent-delivery/l1/fixtures/generated-control-surface/` | Positive provenance fixture for generated child-control artifacts. | Generated artifacts must be linked to source hashes or stable source ids. |
| `tests/docworkflow-agent-delivery/l1/fixtures/thin-child-skeleton/` | Negative child skeleton. | Missing conformance/write-set/handoff must block readiness. |
| `tests/docworkflow-agent-delivery/l1/fixtures/missing-rehearsal-ready-claim/` | Negative ready-claim fixture. | Ready claim with high-risk command and no rehearsal must fail or block. |
| `tests/docworkflow-agent-delivery/l1/fixtures/hidden-normalization/` | Negative manifest/provenance fixture. | Output depending on undeclared normalization must fail. |
| `tests/docworkflow-agent-delivery/l1/fixtures/s0-limitations-no-agent/` | Guard that S0 limitations stay out of deterministic L1 execution. | Runner must record S0 context without invoking Promptfoo/Codex/auth/network setup. |

Fixture examples are referenced, not embedded canonical JSON/YAML. No embedded machine-readable canonical example is normative in this child spec.

## Control Flow and Failure Cases

1. Create or select an isolated L1 run directory.
2. Load the fixture manifest and verify source/copy/generated/removed/normalization declarations.
3. Run case-specific deterministic assertions.
4. Run readiness checks against fixture child specs, child index rows and handoffs where applicable.
5. Record forbidden command classes and source-write attempts.
6. Write `evidence/l1-summary.json`.
7. Return non-zero when any required positive or negative assertion does not match its expected status.

Failure states:

- `invalid_parent_only_start`: parent-only fixture contains child artifacts at start.
- `stale_or_unprovenanced_control_surface`: generated child-control output lacks provenance or is copied from a source index without evidence.
- `invalid_ready_claim`: child claims implementation readiness without required conformance/write-set/handoff/validator gates.
- `missing_rehearsal`: high-risk command is used as readiness evidence without rehearsal or explicit blocker.
- `hidden_normalization`: output depends on undeclared fixture transformation.
- `forbidden_agent_dependency`: L1 run invokes or requires Promptfoo, Codex, Inspect, credentials or npm registry access.
- `source_write_violation`: L1 writes to read-only original source paths.

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `DWT-S1-L1A` | Parent-only start is clean. | `parent-only`. | `pass` only when child artifacts are absent. | Manifest and assertion result. | No inherited Child Index, Child Spec or Handoff. |
| `DWT-S1-L1B` | New child control surface has provenance. | `generated-control-surface`. | `pass` when output is new or generated and linked to source hashes/ids. | Assertions JSON and provenance entries. | Old source index copied as "generated" cannot pass. |
| `DWT-S1-L1C` | Thin skeleton blocks readiness. | `thin-child-skeleton`. | `blocked` or `fail` for implementation-ready claim. | Validator/readiness output. | No delivery next action. |
| `DWT-S1-L1D` | Missing high-risk rehearsal blocks. | `missing-rehearsal-ready-claim`. | `fail` or `blocked` for ready claim. | Validator/readiness output. | No skipped rehearsal as pass. |
| `DWT-S1-L1E` | Hidden normalization fails. | `hidden-normalization`. | `fail`. | Manifest diff or normalization assertion output. | Normalization must be declared. |
| `DWT-S1-L1F` | S0 limitations remain context only. | `s0-limitations-no-agent`. | `pass` only when L1 records S0 result without agent/auth/network dependency. | Summary field `s0_dependency_context`. | No Promptfoo, Codex, Inspect, credential copy or npm registry command. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `bash` or `zsh`
- Platform: macOS authoring, Linux-compatible shell where practical
- Runtime assumptions: No Promptfoo/Codex credentials, npm registry connectivity, Docker daemon or KI-fuer-KMU runtime repository required for L1.

Pre-implementation hardening verification and command-contract rehearsal:

```sh
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all
openspec validate docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness --strict
openspec validate docworkflow-agent-delivery-testsuite --strict
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md" \
  --child DWT-S1 \
  --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/dwt-s1-session-handoff.md"
```

Gate verification after implementation creates the L1 script and fixtures:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh
tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all
openspec validate docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness --strict
openspec validate docworkflow-agent-delivery-testsuite --strict
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md" \
  --child DWT-S1 \
  --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/dwt-s1-session-handoff.md"
```

Success criteria:

- Existing L0 harness exits `0` and remains green.
- OpenSpec active change and canonical spec validate in strict mode.
- `ValidateChildReadiness.cs` passes for `DWT-S1`.
- After implementation, shell syntax exits `0`.
- After implementation, L1 runner exits `0` only when all required positive/negative cases match expected status.
- `l1-summary.json` exists and contains all required summary fields.

Anti-loop rule: Do not add commands that only verify this verification contract. The L1 runner must evaluate fixture, provenance, readiness and forbidden-action evidence, not recursively re-run itself as proof.

## Command-Contract Rehearsal Evidence

Performed during hardening on 2026-05-07:

| Rehearsal | Result | Meaning |
|---|---|---|
| `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all` | Passed. | Existing L0 contract harness remains green before S1 implementation. |
| `openspec validate docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness --strict` | Passed. | Active OpenSpec change is structurally valid. |
| `openspec validate docworkflow-agent-delivery-testsuite --strict` | Passed. | Canonical accepted OpenSpec spec remains valid while S1 is active. |
| `ValidateChildReadiness.cs` before sync | Failed due Child Index/Handoff verdict and pointer mismatch. | Existing draft was not ready and required sync. |
| `ValidateChildReadiness.cs` after sync | Passed. | Child Index, DWT-S1 handoff, verdict and enforceable write-set agree for implementation kickoff. |

`run-l1-contract-checks.sh` now exists. Its first successful syntax and `all` executions are DWT-S1 delivery evidence, distinct from the earlier hardening rehearsal evidence.

## Definition of Ready for Implementation

- Parent coverage and conformance are explicit.
- Fixture, summary, readiness and evidence contracts are concrete.
- Harness cases include positive, negative, blocked and forbidden-action assertions.
- Allowed write-set is enforceable.
- Verification commands and success criteria are defined.
- OpenSpec change exists and validates.
- Persisted handoff exists and matches this spec and the Parent Child Index.
- `ValidateChildReadiness.cs` passes for `DWT-S1` before delivery starts.

## Definition of Done / Closeout Evidence

- L1 fixtures and runner exist.
- L1 runner evidence proves all cases L1A-L1F.
- `l1-summary.json` exists and satisfies the summary contract.
- Parent Child Index links DWT-S1 evidence and next action.
- OpenSpec change tasks and canonical spec are synchronized after acceptance/archive.
- S2/S3/S5 remain blocked unless their own dependency gates are later satisfied.
- No original source specs were modified.
- Retained L1 summary evidence: `/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/docworkflow-agent-delivery-l1.sPlnN6/evidence/l1-summary.json`.

## Dependencies and Write-Set

Allowed implementation write-set:

- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S1 L1 Deterministic Harness.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`
- `_specs/child-session-handoffs/dwt-s1-session-handoff.md`
- `openspec/changes/docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness/**`
- `tests/docworkflow-agent-delivery/l1/**`
- `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh`
- `tests/docworkflow-agent-delivery/README.md`
- `tests/docworkflow-agent-delivery/testcases/tc1-parent-first-orchestration-child-hardening.md`

Shared/read-only files:

- `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`
- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `docs/doc-workflow.md`
- `skills-repo/skills/**`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S0 Framework Spike.md`
- `_specs/2026-05-07 DocWorkflow Agent Test Framework Evaluation ADR.md`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/**`
- KI-fuer-KMU original specs and runtime repositories

Parallel hardening / implementation:

- Runtime implementation parallelization is not authorized from this child.
- `DWT-S2`, `DWT-S3` and `DWT-S5` remain dependency-blocked.
- `DWT-S4` may be hardened separately only if a future orchestrator/integration owner keeps shared summary/output contracts synchronized.

## Closeout Sync Targets

- Parent Child Index row `DWT-S1`.
- OpenSpec change `docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness`.
- Canonical OpenSpec spec `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` after S1 acceptance/archive.
- L1 evidence links in README/testcase docs.
- DWT-S2/S3/S5 dependency rows remain blocked until later closeout or orchestrator sync explicitly changes them.

## Child Session Handoff

Persisted handoff: `_specs/child-session-handoffs/dwt-s1-session-handoff.md`.

## Content Quality Review

- Correctness/domain fit: Pass. L1 is deterministic contract proof, not agent proof.
- Scope discipline: Pass. Agentic, Promptfoo and runtime tests remain out of scope.
- Completeness: Pass. Cases, fixture contract, negative assertions, S0 limitation handling and commands are explicit.
- Consistency: Pass after Child Index/Handoff sync and readiness validator pass.
- Testability: Pass. Commands are concrete; implementation must create the runner/fixtures and replay the gates.
- Blocking Marker: None after validator sync passes.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-07 | Codex | Initial implementation-ready DWT-S1 child spec created from hardening queue. |
| 2026-05-07 | Codex | Hardened DWT-S1 contract, S0 limitation handling, verification evidence, handoff/index sync requirements and dependency-blocked descendants. |
| 2026-05-07 | Codex | Locked DWT-S1 delivery scope for deterministic L1 harness implementation. |
| 2026-05-07 | Codex | Implemented L1 fixtures, runner, summary evidence and documentation sync for DWT-S1. |

SessionId: 2026-05-07-docworkflow-agent-delivery-testsuite-dwt-s1
