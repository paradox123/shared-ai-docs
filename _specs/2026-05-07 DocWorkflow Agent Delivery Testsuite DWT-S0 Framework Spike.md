**Date:** 2026-05-07  
**Status:** 🟢 Accepted  
**Scope:** Implementation-ready child spec for the DWT-S0 Promptfoo-first framework spike.

---

## Review Control Surface

- Spec-Variante: implementation-ready Child Spec.
- Goldstandard Status: candidate.
- Ziel: Einen einmaligen Promptfoo-first Spike so ausfuehrbar machen, dass die Testsuite-Implementierung danach auf Promptfoo aufbauen, Promptfoo mit Limitierungen nutzen, zu Inspect AI wechseln oder die Framework-Evaluation wieder oeffnen kann.
- In Scope: Promptfoo CLI/runtime preflight, Codex/Coding-Agent adapter probe, isolierte Fixture, gespeicherte Agent-/Blocker-Outputs, deterministische Post-Run-Assertions, ADR-Re-Evaluation und Parent/Child-Index-Sync.
- Out of Scope: Wiederholbare L1/L2/L3 Testsuite-Implementierung, Runtime-Delivery, KI-fuer-KMU-Originalaenderungen, generisches Eigenbau-Agent-Testframework, vollstaendige Inspect-AI-Implementierung.
- Wichtigste Test-/Harness-Cases: `DWT-S0-PF1 promptfoo cli preflight`, `DWT-S0-PF2 isolated fixture setup`, `DWT-S0-PF3 codex provider probe or reproducible blocker`, `DWT-S0-PF4 deterministic assertion/report`, `DWT-S0-PF5 ADR re-evaluation gate`.
- Wichtigste Verification Commands: bundled Node `v24.14.0` plus isolated npm/HOME preflight; `npx --package promptfoo@0.121.9 promptfoo debug`; `promptfoo validate config`; `promptfoo eval ... --no-cache`; deterministic assertion script; pre-archive `openspec validate docworkflow-agent-testsuite-dwt-s0-framework-spike --strict`; post-archive `openspec validate docworkflow-agent-delivery-testsuite --strict`; `ValidateChildReadiness.cs`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen. Promptfoo adoption itself is the spike result, not a precondition.
- Readiness Status: Accepted; was IMPLEMENTATION READY before delivery.
- Implementation Result: `ADOPT_WITH_LIMITATIONS`; accepted and archived via OpenSpec. See `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json`.

## Goal

Run the smallest credible Promptfoo-first spike for the DocWorkflow Agent Delivery Testsuite. The spike must decide, with evidence, whether Promptfoo can be the primary agent/coding-agent eval runner for later slices.

## In Scope

- Create a spike-local Promptfoo config under `tests/docworkflow-agent-delivery/spikes/dwt-s0/`.
- Use isolated temp fixtures and never write KI-fuer-KMU original specs.
- Probe Promptfoo with Codex SDK or Codex app-server/Desktop provider path as supported by current docs.
- Persist runner output, blocker output, assertion output and summary evidence.
- Update the ADR with one of `ADOPT_PROMPTFOO`, `ADOPT_WITH_LIMITATIONS`, `FALLBACK_TO_INSPECT`, or `REOPEN_EVALUATION`.

## Out of Scope

- No implementation of recurring L1/L2/L3 testcases.
- No runtime repository implementation.
- No broad refactor of existing L0 harness scripts.
- No fallback implementation beyond documenting `FALLBACK_TO_INSPECT` when Promptfoo blocks.

## Parent/Master Coverage

| Parent Requirement | Child Coverage |
|---|---|
| `DWT-PR5` Evidence Integrity | Requires isolated fixture manifest, stored outputs and deterministic assertion evidence; static fake outputs cannot pass the spike. |
| `DWT-PR6` Framework Reuse | Directly owns the Promptfoo-first adoption gate and Inspect AI fallback decision. |
| `DWT-PR7` Style and Efficiency | Captures runner metadata, command behavior and reporting shape needed by later telemetry gates. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `DWT-PR5` | Spike evidence must distinguish `ran-target`, `blocked`, `failed` and static fake outputs. | preserves | Implement evidence status taxonomy in the spike summary. |
| `DWT-PR6` | Promptfoo is recommended but not adopted until spike evidence supports it. | preserves | Update ADR only after evidence. |
| `DWT-PR7` | Spike records command/runtime/trace visibility sufficient for later efficiency gates. | extends | Include visibility assessment in evidence. |

## Decision Freeze Pack

| Entscheidung | Freeze |
|---|---|
| Primary candidate | Promptfoo `0.121.9`, the current npm package observed during command rehearsal on 2026-05-07. |
| Runtime | Use bundled Node `/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node` (`v24.14.0`) because default local Node `v22.12.0` does not satisfy current Promptfoo runtime requirements. |
| Cache isolation | Use temp `HOME` and temp `npm_config_cache` for Promptfoo runs to avoid stale native module cache issues. |
| Provider path | Start with Promptfoo Codex SDK or app-server provider; choose the one that can be run reproducibly in this local environment. |
| Adoption result | Exactly one of `ADOPT_PROMPTFOO`, `ADOPT_WITH_LIMITATIONS`, `FALLBACK_TO_INSPECT`, `REOPEN_EVALUATION`. |
| Original specs | Read-only source fixtures only; no KI-fuer-KMU original writes. |

## Normative Contract

### Spike Summary

The spike must write `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json` with:

| Field | Allowed / Required |
|---|---|
| `child` | Must be `DWT-S0`. |
| `promptfoo_version` | Promptfoo version or `null` with blocker. |
| `node_executable` | Absolute executable path used. |
| `node_version` | Runtime version used. |
| `fixture_root` | Temp or spike-local fixture path. |
| `runner_status` | `ran-target`, `blocked`, or `failed`. |
| `assertion_status` | `pass`, `blocked`, or `fail`. |
| `reevaluation_result` | `ADOPT_PROMPTFOO`, `ADOPT_WITH_LIMITATIONS`, `FALLBACK_TO_INSPECT`, or `REOPEN_EVALUATION`. |
| `manual_steps_used` | Boolean; `true` blocks `ADOPT_PROMPTFOO`. |
| `static_fake_outputs_used` | Boolean; `true` blocks `ADOPT_PROMPTFOO`. |
| `hidden_normalizations_used` | Boolean; `true` blocks `ADOPT_PROMPTFOO`. |
| `evidence_links` | Paths to runner, blocker, assertion and ADR evidence. |

### Result Rules

- `ADOPT_PROMPTFOO` requires a real Promptfoo run or accepted Codex adapter run, isolated fixture, stored output, deterministic assertion pass and no manual-only/static-fake/hidden-normalization workaround.
- `ADOPT_WITH_LIMITATIONS` is allowed when Promptfoo runs but leaves named gaps, for example limited trace visibility.
- `FALLBACK_TO_INSPECT` is required when Promptfoo cannot drive the Codex/Coding-Agent path reproducibly enough for the testsuite.
- `REOPEN_EVALUATION` is required when neither Promptfoo nor the immediate Inspect fallback path can be selected from the evidence.

## Canonical Examples and Fixtures

Examples are referenced fixture files, not embedded normative JSON/YAML. Implementation must create:

| Fixture | Purpose |
|---|---|
| `tests/docworkflow-agent-delivery/spikes/dwt-s0/fixtures/minimal-parent-spec.md` | Tiny parent-like input that can prove file access or blocked file access. |
| `tests/docworkflow-agent-delivery/spikes/dwt-s0/promptfooconfig.yaml` | Promptfoo probe config. |
| `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json` | Canonical result artifact. |

The deterministic assertion must read `spike-summary.json`; it must not accept final prose alone.

## Control Flow and Failure Cases

1. Preflight bundled Node and isolated npm/HOME.
2. Run Promptfoo debug/config validation.
3. Create isolated fixture.
4. Run Codex provider probe or capture reproducible blocker.
5. Run deterministic post-run assertion against output/evidence.
6. Update ADR with exactly one result.
7. Sync Parent Child Index, Handoff and OpenSpec evidence link.

Failure states:

- `blocked_runtime`: Node or Promptfoo cannot be selected reproducibly.
- `blocked_provider`: Promptfoo works but Codex provider/auth/app-server path cannot run reproducibly.
- `failed_assertion`: Runner output exists but deterministic assertion fails.
- `invalid_adoption`: Result claims `ADOPT_PROMPTFOO` while manual/static/hidden-normalization workaround was used.

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `DWT-S0-PF1` | Prove Promptfoo CLI/runtime selection. | Bundled Node plus isolated npm/HOME. | Exit `0` from `promptfoo debug`. | Debug output with version and Node path evidence. | Default stale npm cache must not be reused as success. |
| `DWT-S0-PF2` | Prove fixture isolation. | Minimal parent fixture under spike/temp path. | `pass`. | Fixture manifest with copied/generated files. | No KI-fuer-KMU original write path. |
| `DWT-S0-PF3` | Probe Codex provider. | Promptfoo config. | `ran-target` or `blocked_provider`. | Agent output or blocker log. | Manual-only and static fake output block adoption. |
| `DWT-S0-PF4` | Prove deterministic assertions. | `spike-summary.json`. | `pass`, `blocked`, or `fail`. | Assertion output. | Final prose alone cannot pass. |
| `DWT-S0-PF5` | Sync ADR result. | Evidence from PF1-PF4. | One allowed result. | ADR history row and result section. | `ADOPT_PROMPTFOO` forbidden when workaround flags are true. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `zsh` or `bash`
- Node: `/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`
- Promptfoo package: `promptfoo@0.121.9`

Preflight and command-contract rehearsal:

```sh
PATH="/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH" node --version
tmp_home="$(mktemp -d /tmp/docworkflow-agent-delivery-dwt-s0-home.XXXXXX)"
tmp_cache="$(mktemp -d /tmp/docworkflow-agent-delivery-dwt-s0-npm-cache.XXXXXX)"
PATH="/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH" \
  HOME="$tmp_home" \
  npm_config_cache="$tmp_cache" \
  FORCE_COLOR=0 \
  npx --yes --package promptfoo@0.121.9 promptfoo debug
```

Gate verification after implementation creates the config and fixtures:

```sh
openspec validate docworkflow-agent-testsuite-dwt-s0-framework-spike --strict
PATH="/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH" \
  HOME="$tmp_home" \
  npm_config_cache="$tmp_cache" \
  FORCE_COLOR=0 \
  npx --yes --package promptfoo@0.121.9 promptfoo validate config -c tests/docworkflow-agent-delivery/spikes/dwt-s0/promptfooconfig.yaml
PATH="/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH" \
  HOME="$tmp_home" \
  npm_config_cache="$tmp_cache" \
  FORCE_COLOR=0 \
  npx --yes --package promptfoo@0.121.9 promptfoo eval -c tests/docworkflow-agent-delivery/spikes/dwt-s0/promptfooconfig.yaml --no-cache
```

After OpenSpec archive, validate the canonical spec instead:

```sh
openspec validate docworkflow-agent-delivery-testsuite --strict
```

Success criteria:

- `node --version` reports a version accepted by Promptfoo; rehearsed value was `v24.14.0`.
- `promptfoo debug` exits `0`; rehearsed Promptfoo value was `0.121.9`.
- `promptfoo validate config` exits `0` after implementation creates the config.
- `promptfoo eval` exits `0` for a successful probe or writes a reproducible blocker log for `FALLBACK_TO_INSPECT` / `REOPEN_EVALUATION`.

Anti-loop rule: Do not add commands that only verify this verification contract. The post-run assertion must evaluate spike evidence, not re-run the same preflight recursively.

## Command-Contract Rehearsal Evidence

Performed during hardening on 2026-05-07:

| Rehearsal | Result | Meaning |
|---|---|---|
| Default `node v22.12.0` plus `npx promptfoo@latest --version` | Failed because current Promptfoo requires `^20.20.0 || >=22.22.0`. | Default shell Node is not acceptable for this slice. |
| Bundled `node v24.14.0` plus existing npx cache | Failed with stale `better-sqlite3` native module compiled for a different Node module version. | Reusing user/global npx cache is unsafe. |
| Bundled `node v24.14.0` plus isolated `HOME` and `npm_config_cache`, `npx --package promptfoo@0.121.9 promptfoo debug` | Passed and reported Promptfoo `0.121.9`. | Command contract is viable when cache and runtime are pinned. |

## Definition of Ready for Implementation

- Parent coverage and conformance are explicit.
- Promptfoo docs were checked during hardening.
- Command contract is pinned to bundled Node and isolated cache.
- Allowed write-set is enforceable.
- OpenSpec change exists, validates, and is archived after acceptance.
- Persisted child handoff exists and matches this spec.
- `ValidateChildReadiness.cs` must pass before delivery starts.

## Definition of Done / Closeout Evidence

- `spike-summary.json` exists and matches the normative contract.
- ADR contains the re-evaluation result and rationale.
- Parent Child Index row for `DWT-S0` links evidence and sets next slice based on the result.
- OpenSpec tasks and evidence are synchronized.
- No KI-fuer-KMU original files were modified.

## Implementation Evidence

- Result: `ADOPT_WITH_LIMITATIONS`
- Summary: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json`
- Runner output: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/promptfoo-eval.txt`
- Runner JSON: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/promptfoo-eval.json`
- Deterministic assertion: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/assertion-output.txt`
- Blocker notes: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/blocker-output.txt`
- Closeout verification replay: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/closeout-verification.txt`
- OpenSpec archive: `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/`
- Canonical OpenSpec spec: `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`

Promptfoo/Codex SDK can drive the smallest DWT-S0 isolated fixture reproducibly when `CODEX_HOME` is explicitly provisioned from a temp auth copy. Empty isolated `CODEX_HOME` blocks with `401 Unauthorized`, and cold isolated npm cache resolution can hit network `ETIMEDOUT`, so later slices must make credential provisioning and cache strategy explicit.

## Dependencies and Write-Set

Hardening/delivery write-set:

- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S0 Framework Spike.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`
- `_specs/2026-05-07 DocWorkflow Agent Test Framework Evaluation ADR.md`
- `_specs/child-session-handoffs/dwt-s0-session-handoff.md`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/**`
- `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`
- `tests/docworkflow-agent-delivery/spikes/dwt-s0/**`

Shared/read-only files:

- `docs/doc-workflow.md`
- `docs/spec-goldstandard.md`
- `skills-repo/skills/**`
- `tests/docworkflow-agent-delivery/scripts/**`
- KI-fuer-KMU original specs and runtime repositories

Parallel hardening:

- `DWT-S1` and `DWT-S4` can be hardened in separate sessions after `DWT-S0` result is known.
- Runtime implementation parallelization is not allowed from this child.

## Closeout Sync Targets

- Parent Child Index row `DWT-S0`.
- ADR re-evaluation section/history.
- OpenSpec archive `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/`.
- Handoff evidence pointer and next recommended slice.

## Child Session Handoff

Persisted handoff: `_specs/child-session-handoffs/dwt-s0-session-handoff.md`.

## Content Quality Review

- Correctness/domain fit: Pass. The child answers only the framework adoption gate.
- Scope discipline: Pass. Recurring harness implementation and runtime delivery are excluded.
- Completeness: Pass. Contract, cases, command preflight, evidence, fallback and closeout sync are specified.
- Consistency: Pass. Parent, ADR, OpenSpec and handoff agree after sync.
- Testability: Pass. The high-risk runtime/cache portion was rehearsed; target eval runs after the implementation creates the config.
- Blocking Marker: None.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-07 | Codex | Initial implementation-ready DWT-S0 child spec created from spec-orchestrator queue and command-contract rehearsal. |
| 2026-05-07 | Codex | DWT-S0 Promptfoo-first spike implemented and verified with `ADOPT_WITH_LIMITATIONS` evidence. |
| 2026-05-07 | Codex | DWT-S0 accepted, closeout verification replayed, and OpenSpec change archived. |

SessionId: 2026-05-07-docworkflow-agent-delivery-testsuite-dwt-s0
