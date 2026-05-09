**Date:** 2026-05-09
**Status:** IMPLEMENTATION READY
**Scope:** Child spec for mock data, manifests, mock target fixtures and forbidden-real-fixture validators.

---

## Review Control Surface

- Spec-Variante: implementation-ready Child Spec.
- Goldstandard Status: candidate.
- Ziel: Create the source-controlled mock fixture family that later Mock E2E runner slices consume, and add deterministic validators that prevent KI-fuer-KMU or other real product paths from returning as standard test fixtures.
- In Scope: `mock-large-parent-spec.md`, `mock-small-direct-spec.md`, `manifest.json` for both fixture families, minimal mock target fixture roots, manifest schema validator, forbidden-real-fixture validator, positive and negative validator fixtures.
- Out of Scope: Local Mock Session Runner implementation, `run-mock-e2e-checks.sh`, standard gate migration, README/parent closeout documentation, live-agent/Codex path, OpenSpec archive.
- Wichtigste Test-/Harness-Cases: `MD-E2E-1A manifest schema positive`, `MD-E2E-1B large fixture contract`, `MD-E2E-1C small fixture contract`, `MD-E2E-1D forbidden source path`, `MD-E2E-1E forbidden target/write/evidence path`, `MD-E2E-1F no compatibility fixture`.
- Wichtigste Verification Commands: `node tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js tests/docworkflow-agent-delivery/mock-data`; `node tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js tests/docworkflow-agent-delivery/mock-data tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture`; `git diff --check`; `ValidateChildReadiness.cs` for `MD-E2E-1`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen. Node is the validator runtime for this child.
- Readiness Status: IMPLEMENTATION READY after Child Index, handoff and readiness validation pass.

## Goal

Make the mock fixture family real enough for later runner work without touching runner scripts. This child owns the data contracts and validators that future slices consume. It must prove that the only positive fixture source is `tests/docworkflow-agent-delivery/mock-data/**` and that KI-fuer-KMU is not retained as a default, fallback or compatibility fixture.

## In Scope

- Add the large parent fixture:
  - `tests/docworkflow-agent-delivery/mock-data/large-parent/mock-large-parent-spec.md`
  - `tests/docworkflow-agent-delivery/mock-data/large-parent/manifest.json`
  - `tests/docworkflow-agent-delivery/mock-data/large-parent/mock-target/README.md`
- Add the small direct fixture:
  - `tests/docworkflow-agent-delivery/mock-data/small-direct/mock-small-direct-spec.md`
  - `tests/docworkflow-agent-delivery/mock-data/small-direct/manifest.json`
  - `tests/docworkflow-agent-delivery/mock-data/small-direct/mock-target/README.md`
- Add deterministic Node validators:
  - `tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js`
  - `tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js`
- Add validator exercise fixtures:
  - `tests/docworkflow-agent-delivery/e2e/fixtures/manifest-schema-valid-large/manifest.json`
  - `tests/docworkflow-agent-delivery/e2e/fixtures/manifest-schema-valid-small/manifest.json`
  - `tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture/source-path.json`
  - `tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture/target-workspace.json`
  - `tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture/write-set.json`
  - `tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture/evidence-path.json`

## Out of Scope

- No implementation of the local mock session runner.
- No creation or modification of `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`.
- No migration of `run-contract-checks.sh` or `setup-fixture.sh`; that is `MD-E2E-3`.
- No README, parent spec or OpenSpec canonical closeout sync except this child spec, handoff and Child Index.
- No live-agent/Codex session path.
- No copied KI-fuer-KMU spec, no real product fixture and no compatibility fixture.

## Parent/Master Coverage

| Parent Requirement | Child Coverage |
|---|---|
| `MD-PR1` | Establishes mock-only standard fixture roots and validator-enforced forbidden real fixture policy. |
| `MD-PR2` | Provides the large mock parent fixture contract, manifest contract, child list `ML-C1` through `ML-C5`, and final count output expectation. |
| `MD-PR3` | Provides the small direct fixture contract, manifest contract, direct mode and forbidden child artifact expectations. |
| `MD-PR7` | Supplies the no-real-fixture validator that `MD-E2E-3` must later wire into standard gates. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `MD-PR1` | This child creates only mock fixture inputs and explicitly forbids real product fixture compatibility. | preserves | Validator negative cases must fail on KI-fuer-KMU path variants. |
| `MD-PR2` | This child defines and creates large fixture data but does not run the large workflow. | narrows_with_rationale | `MD-E2E-2` consumes the fixture to execute the large E2E. |
| `MD-PR3` | This child defines and creates small direct fixture data but does not run direct delivery. | narrows_with_rationale | `MD-E2E-2` consumes the fixture to execute the small E2E. |
| `MD-PR7` | This child provides the validator but does not migrate standard gates. | defers_to_child | `MD-E2E-3` wires validators into standard commands and removes legacy defaults. |

No touched parent requirement contradicts the parent spec. Runtime execution and standard-gate migration are explicitly delegated to later children.

## Decision Freeze Pack

| Entscheidung | Wert |
|---|---|
| Fixture root | `tests/docworkflow-agent-delivery/mock-data/` |
| Large fixture root | `tests/docworkflow-agent-delivery/mock-data/large-parent/` |
| Small fixture root | `tests/docworkflow-agent-delivery/mock-data/small-direct/` |
| Manifest filename | `manifest.json` in each fixture root |
| Large source spec filename | `mock-large-parent-spec.md` |
| Small source spec filename | `mock-small-direct-spec.md` |
| Target repo name inside manifests | `mock-target` |
| Large expected delivery mode | `parent_child` |
| Small expected delivery mode | `direct` |
| Large children | exactly `ML-C1`, `ML-C2`, `ML-C3`, `ML-C4`, `ML-C5` |
| Large output | `mock-target/output/count.txt` with exact content `1\n2\n3\n4\n5\n` |
| Small output | `mock-target/output/small-direct-result.json` |
| Validator runtime | Node.js, matching existing Agent Delivery validator style |
| Forbidden real fixture policy | KI-fuer-KMU and other real product paths are fail conditions, not compatibility fixtures |

## Normative Contract

### Fixture Layout

Implementation must create exactly these positive fixture roots:

```text
tests/docworkflow-agent-delivery/mock-data/
  large-parent/
    manifest.json
    mock-large-parent-spec.md
    mock-target/
      README.md
  small-direct/
    manifest.json
    mock-small-direct-spec.md
    mock-target/
      README.md
```

The `mock-target/output/**` files are runtime outputs for `MD-E2E-2`; they must not be committed as positive source fixture outputs in this child.

### Manifest Required Fields

Every positive manifest must contain:

| Field | Type | Rule |
|---|---|---|
| `fixture_id` | string | Stable id; `mock-large-parent-v1` or `mock-small-direct-v1`. |
| `fixture_version` | string | Semantic version; initial value `1.0.0`. |
| `spec_type` | string | `large-parent` or `small-direct`. |
| `expected_delivery_mode` | string | `parent_child` or `direct`. |
| `runner_mode` | string | `local-mock-session-runner`. |
| `session_strategy` | string | `auto-start-and-resume` or `direct-no-child-session`. |
| `source_spec` | string | Source spec filename in same fixture root. |
| `target_repo` | string | `mock-target`. |
| `expected_children` | array | Large: five child ids; small: empty array. |
| `expected_outputs` | array | Output paths relative to fixture target. |
| `forbidden_outputs` | array | Paths/globs that must not be created for this fixture. |
| `expected_sessions` | array | Large: one entry per child; small: empty array. |
| `expected_closeout_state` | object | Machine-checkable post-run closeout expectations. |
| `forbidden_source_paths` | array | Must include both `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**` and `ki-fuer-kmu/**`. |

Large manifests must also contain:

- `mock_sizing_directive: "force_parent_child"`
- `expected_output_content: "1\n2\n3\n4\n5\n"`
- `child_output_contract` with one entry per `ML-Cn` mapping to `append_or_set_line:n`

Small manifests must contain:

- `expected_output_json` with `mode: "direct"`, `result: "ok"`, `source: "mock-small-direct"`

### Forbidden Real Fixture Validator Contract

`forbidden-real-fixture.js` must scan JSON, Markdown and text fixture/evidence files passed on the command line. It must return:

- exit `0` only when no forbidden real fixture path or real-fixture compatibility marker is found;
- non-zero when any forbidden path is found;
- machine-readable JSON on stdout or an evidence file containing `status`, `checked_paths`, `findings`, and `forbidden_patterns`.

Forbidden matches include:

- `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`
- `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**`
- `ki-fuer-kmu/`
- `ki-fuer-kmu/**`
- string markers `compatibility_fixture`, `real_product_fixture`, `kmu_fixture_fallback` when used as a positive fixture mode.

Allowed historical references are out of scope for this child because this child scans only positive mock fixture roots and explicit negative validator fixtures.

### Manifest Schema Validator Contract

`mock-manifest-schema.js` must:

- discover positive manifests under `tests/docworkflow-agent-delivery/mock-data/**/manifest.json`;
- validate both required manifests exist;
- validate required fields and allowed values;
- validate `source_spec` files exist;
- validate `target_repo` directories exist;
- validate large child ids and output content exactly;
- validate small fixture has no child ids and declares forbidden child artifacts;
- invoke or reuse the forbidden-real-fixture check for every positive manifest.

## Canonical Examples and Fixtures

This child uses a hybrid pattern: compact embedded canonical manifest examples plus full fixture files created during implementation.

Large canonical manifest:

```json
{
  "fixture_id": "mock-large-parent-v1",
  "fixture_version": "1.0.0",
  "spec_type": "large-parent",
  "expected_delivery_mode": "parent_child",
  "runner_mode": "local-mock-session-runner",
  "session_strategy": "auto-start-and-resume",
  "source_spec": "mock-large-parent-spec.md",
  "target_repo": "mock-target",
  "mock_sizing_directive": "force_parent_child",
  "expected_children": ["ML-C1", "ML-C2", "ML-C3", "ML-C4", "ML-C5"],
  "expected_outputs": ["mock-target/output/count.txt"],
  "forbidden_outputs": ["mock-target/output/small-direct-result.json"],
  "expected_output_content": "1\n2\n3\n4\n5\n",
  "child_output_contract": {
    "ML-C1": "append_or_set_line:1",
    "ML-C2": "append_or_set_line:2",
    "ML-C3": "append_or_set_line:3",
    "ML-C4": "append_or_set_line:4",
    "ML-C5": "append_or_set_line:5"
  },
  "expected_sessions": [
    { "child_id": "ML-C1", "sequence_index": 1, "expected_final_status": "ran-target", "handoff_required": true },
    { "child_id": "ML-C2", "sequence_index": 2, "expected_final_status": "ran-target", "handoff_required": true },
    { "child_id": "ML-C3", "sequence_index": 3, "expected_final_status": "ran-target", "handoff_required": true },
    { "child_id": "ML-C4", "sequence_index": 4, "expected_final_status": "ran-target", "handoff_required": true },
    { "child_id": "ML-C5", "sequence_index": 5, "expected_final_status": "ran-target", "handoff_required": true }
  ],
  "expected_closeout_state": {
    "child_index_synced": true,
    "session_chain_closed": true,
    "final_output_validated": true
  },
  "forbidden_source_paths": [
    "/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**",
    "ki-fuer-kmu/**"
  ]
}
```

Small canonical manifest:

```json
{
  "fixture_id": "mock-small-direct-v1",
  "fixture_version": "1.0.0",
  "spec_type": "small-direct",
  "expected_delivery_mode": "direct",
  "runner_mode": "local-mock-session-runner",
  "session_strategy": "direct-no-child-session",
  "source_spec": "mock-small-direct-spec.md",
  "target_repo": "mock-target",
  "expected_children": [],
  "expected_outputs": ["mock-target/output/small-direct-result.json"],
  "forbidden_outputs": ["child-index.md", "child-session-handoffs/**", "child-specs/**"],
  "expected_sessions": [],
  "expected_closeout_state": {
    "child_index_created": false,
    "child_specs_created": false,
    "child_handoffs_created": false
  },
  "expected_output_json": {
    "mode": "direct",
    "result": "ok",
    "source": "mock-small-direct"
  },
  "forbidden_source_paths": [
    "/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**",
    "ki-fuer-kmu/**"
  ]
}
```

The embedded JSON examples are normative and must remain parseable. Full fixture files created during implementation must match these examples unless the child spec is updated before delivery.

## Control Flow and Failure Cases

1. Create positive fixture files and mock target roots.
2. Create validator files.
3. Run the manifest schema validator against `tests/docworkflow-agent-delivery/mock-data`.
4. Run the forbidden-real-fixture validator against positive fixture roots.
5. Run the forbidden-real-fixture validator against negative fixtures and assert non-zero failure for each forbidden case.
6. Confirm no positive fixture file contains `ki-fuer-kmu`, `compatibility_fixture`, `real_product_fixture`, or `kmu_fixture_fallback`.

Failure states:

| Failure | Meaning |
|---|---|
| `missing_manifest` | Required fixture manifest is absent. |
| `invalid_manifest_schema` | Required field, type or allowed value is invalid. |
| `missing_source_spec` | Manifest source spec does not exist. |
| `invalid_large_children` | Large fixture does not declare exactly `ML-C1` through `ML-C5`. |
| `invalid_small_direct_contract` | Small fixture declares child artifacts or wrong direct output. |
| `forbidden_real_fixture_path` | KI-fuer-KMU or other real fixture path appears in scanned inputs. |
| `compatibility_fixture_detected` | A real-fixture fallback/compatibility mode appears as positive test data. |

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `MD-E2E-1A` | Validate positive manifest schema discovery. | `tests/docworkflow-agent-delivery/mock-data/**/manifest.json` | exit `0`, status `pass` | validator summary or stdout with both fixture ids | No missing manifest, no undeclared source spec. |
| `MD-E2E-1B` | Validate large fixture contract. | `large-parent/manifest.json`; `mock-large-parent-spec.md`; `mock-target/` | exit `0`, status `pass` | child ids, output path and output content assertions | No direct-mode output, no real fixture path. |
| `MD-E2E-1C` | Validate small fixture contract. | `small-direct/manifest.json`; `mock-small-direct-spec.md`; `mock-target/` | exit `0`, status `pass` | no-child-artifact assertions | No child index/spec/handoff in positive small fixture. |
| `MD-E2E-1D` | Reject forbidden source path. | `e2e/fixtures/forbidden-real-fixture/source-path.json` | non-zero, status `fail_expected` | finding with `forbidden_real_fixture_path` | Must detect absolute and relative KI-fuer-KMU forms. |
| `MD-E2E-1E` | Reject forbidden target, write-set or evidence path. | `target-workspace.json`, `write-set.json`, `evidence-path.json` | non-zero, status `fail_expected` | finding with offending field path | No positive result when a forbidden path hides outside manifest source fields. |
| `MD-E2E-1F` | Reject compatibility fixture mode. | negative fixture containing `compatibility_fixture` or `kmu_fixture_fallback` | non-zero, status `fail_expected` | finding with `compatibility_fixture_detected` | Compatibility mode cannot preserve KI-fuer-KMU as a fixture. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `zsh` or `bash`
- Runtime: Node.js available on PATH; no network, Docker, Codex auth or external agent provider required.

Pre-implementation hardening verification:

```sh
node --version
git diff --check
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md" \
  --child MD-E2E-1 \
  --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/md-e2e-1-session-handoff.md"
```

Delivery gate after implementation creates the fixture and validator files:

```sh
node tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js tests/docworkflow-agent-delivery/mock-data
node tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js tests/docworkflow-agent-delivery/mock-data
node tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture && exit 1 || test "$?" -ne 0
git diff --check
```

If implementation introduces or edits shell scripts despite this child not requiring script edits:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/*.sh
```

Success criteria:

- Positive manifest validator exits `0`.
- Positive forbidden-real-fixture scan exits `0`.
- Each negative forbidden-real-fixture case exits non-zero and identifies the offending field or file.
- `git diff --check` exits `0`.
- Child readiness validation passes before implementation kickoff.

Anti-loop rule: do not add a validator that only checks that another validator exists. The validators must parse fixture content and assert field-level behavior.

## Definition of Ready for Implementation

- Parent Scope Conformance has no `contradicts_parent` or unexplained `missing_from_child`.
- Decision Freeze Pack has no blocking decision.
- Canonical JSON examples parse.
- Child Index row, child spec and handoff all say `IMPLEMENTATION READY`.
- Allowed write-set is concrete in Child Index, child spec and handoff.
- `ValidateChildReadiness.cs` passes for `MD-E2E-1`.
- `git diff --check` passes.
- Agent Delivery Session Launch/Queue Evidence is created or the final answer reports a blocker. The implementation handoff may be queued, but no implementation starts in this hardening run.

## Definition of Done / Closeout Evidence

Implementation closeout must provide:

- Paths to the two positive manifests and two mock source specs.
- Validator command output for positive manifests.
- Negative validator evidence for source path, target workspace, write-set, evidence path and compatibility fixture mode.
- Confirmation that no positive mock fixture contains KI-fuer-KMU or real product path strings.
- Updated Child Index row marking `MD-E2E-1` accepted or implemented only after delivery evidence exists.
- Handoff update that releases `MD-E2E-2` hardening only after fixture contracts are accepted.

## Dependencies and Write-Set

Dependencies:

- Parent: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`
- Child Index: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`
- Handoff: `_specs/child-session-handoffs/md-e2e-1-session-handoff.md`
- Active OpenSpec ledger: `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-1-mock-fixtures/`

Implementation Allowed Write-Set:

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-1 Mock Fixtures.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`
- `_specs/child-session-handoffs/md-e2e-1-session-handoff.md`
- `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-1-mock-fixtures/**`
- `tests/docworkflow-agent-delivery/mock-data/large-parent/**`
- `tests/docworkflow-agent-delivery/mock-data/small-direct/**`
- `tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js`
- `tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js`
- `tests/docworkflow-agent-delivery/e2e/fixtures/manifest-schema-valid-large/**`
- `tests/docworkflow-agent-delivery/e2e/fixtures/manifest-schema-valid-small/**`
- `tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture/**`

Shared / Read-only Files:

- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/README.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`
- `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`
- KI-fuer-KMU and other real product repositories

Parallelization:

- `MD-E2E-1` implementation is serial-first because later runner and gate-migration slices consume its fixture contracts.
- `MD-E2E-4` may draft documentation in parallel, but it cannot finalize evidence links until `MD-E2E-1` through `MD-E2E-3` closeout evidence exists.

## Closeout Sync Targets

- Update this child spec history and status after implementation.
- Update the `MD-E2E-1` Child Index row in the orchestration pack.
- Update `_specs/child-session-handoffs/md-e2e-1-session-handoff.md` with retained evidence.
- Do not change README or standard runner docs in this child except if closeout must fix a stale handoff pointer.
- Do not archive OpenSpec until implementation evidence exists.

## Child Session Handoff

Implementation handoff:

- `_specs/child-session-handoffs/md-e2e-1-session-handoff.md`

The handoff must remain synchronized with this spec and the Child Index before `spec-change-delivery` starts.

## Content Quality Review

- Correctness/domain fit: Pass. The child covers only fixture and validator contracts.
- Necessity/scope discipline: Pass. Runner and legacy gate changes are delegated to later children.
- Completeness: Pass. Manifest fields, canonical examples, positive and negative cases, write-set and closeout evidence are specified.
- Consistency: Pass. KI-fuer-KMU is forbidden as standard, fallback and compatibility fixture.
- Verifiability/testability: Pass. Delivery gates are deterministic Node commands plus `git diff --check`; hardening gates include readiness validation.
- Blocking markers: None.

## Hardening Verdict

`IMPLEMENTATION READY`

Rationale:

- Parent conformance is explicit and non-contradictory.
- Contract-heavy manifest examples are embedded and parseable.
- Fixture files and validator files have concrete paths.
- Positive and negative cases are defined.
- Implementation write-set is enforceable.
- Child Index and handoff are synchronized by this hardening run.
- No runtime implementation starts in this hardening run.

## Mini-Retro

- Was wurde entschieden? Node validators and `manifest.json` per fixture root are frozen for `MD-E2E-1`.
- Was wurde geaendert? The child skeleton was hardened into an implementation-ready fixture/validator contract.
- Was bleibt offen? Actual fixture and validator files still need `spec-change-delivery`.
- Welche Evidenz/Verification fehlt? Functional validator output comes during implementation closeout.
- Welche Skill-/Workflow-Reibung ist aufgefallen? New commands that create files cannot be fully rehearsed before implementation; the readiness gate therefore rehearses runtime/path contracts and requires delivery evidence after implementation.
- Session-/Kontextzustand: Stop at implementation handoff unless the user explicitly starts `spec-change-delivery`.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-09 | Codex | Initial child skeleton created by spec-orchestrator. |
| 2026-05-09 | Codex | Hardened MD-E2E-1 with fixture layout, manifest contract, canonical examples, validator contracts, verification lifecycle and implementation-ready handoff. |

SessionId: 2026-05-09-md-e2e-1-child-spec-hardening
