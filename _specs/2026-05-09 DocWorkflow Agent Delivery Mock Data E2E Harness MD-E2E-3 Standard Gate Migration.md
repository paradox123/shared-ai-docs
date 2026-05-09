**Date:** 2026-05-09
**Status:** 🔵 Implemented
**Scope:** Hardened child spec for replacing/deactivating old standard Agent Delivery gates that still default to KI-fuer-KMU fixture data.

---

## Review Control Surface

- Spec-Variante: implementation-ready Child Spec.
- Goldstandard Status: none.
- Ziel: Make the mock E2E runner the standard Agent Delivery regression gate and remove KI-fuer-KMU from all default script paths, fallback paths and compatibility fixture behavior.
- In Scope: `run-contract-checks.sh all` standard routing, `setup-fixture.sh` default behavior, command-reference updates in `tests/docworkflow-agent-delivery/README.md`, no-default-real-fixture guards, and a minimal OpenSpec change ledger for this migration.
- Out of Scope: authoring new mock fixtures, changing accepted MD-E2E-1 fixture contracts, changing accepted MD-E2E-2 mock runner internals except wiring required by standard routing, broad DWT historical rewrites, parent/final docs closeout beyond directly coupled command references, live-agent/Codex execution.
- Wichtigste Test-/Harness-Cases: `MOCK-STANDARD-ALL-MOCK`, `MOCK-CONTRACT-ALL-SHIM`, `MOCK-LEGACY-FIXTURE-NO-DEFAULT`, `MOCK-FORBID-REAL-FIXTURE`, `MOCK-README-STANDARD-COMMAND`.
- Wichtigste Verification Commands: `bash -n tests/docworkflow-agent-delivery/scripts/*.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-3-mock-all`; `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all --keep`; no-default-KI-fuer-KMU guards over scripts and README; `openspec validate docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration --strict`; `git diff --check`.
- Offene Entscheidungen: none.
- Readiness Status: IMPLEMENTATION READY; implementation evidence captured for standard gate migration.

## Goal

The standard Agent Delivery testsuite must not pass by reading KI-fuer-KMU or any other real product fixture. The leading standard gate is `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`. The legacy `run-contract-checks.sh all` command may remain as a compatibility command name only if it delegates to the mock-only standard gate and cannot create or copy a real fixture by default.

## In Scope

- Replace the `run-contract-checks.sh all` default path with a mock-only route.
- Remove the absolute KI-fuer-KMU `source_specs` default from `run-contract-checks.sh`.
- Remove the absolute KI-fuer-KMU `DEFAULT_SOURCE` behavior from `setup-fixture.sh`.
- Make `setup-fixture.sh` explicit-only for legacy fixture materialization; a no-argument call must fail with a clear non-standard/legacy message or be converted to a mock-data fixture command with no real repository source.
- Add or preserve a forbidden-real-fixture guard before any standard pass is reported.
- Update README command snippets directly coupled to standard gate behavior so the quickstart starts with `run-mock-e2e-checks.sh all --keep`.
- Create/use OpenSpec change id `docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration`.

## Out of Scope

- Creating or editing files under `tests/docworkflow-agent-delivery/mock-data/**`.
- Reworking `tests/docworkflow-agent-delivery/e2e/mock-runner/**` state-machine internals.
- Rewriting L1/L2/L3/Reporting historical fixtures or retained evidence.
- Marking parent/final docs complete; MD-E2E-4 owns final documentation synchronization.
- Reintroducing KI-fuer-KMU as an explicit accepted fixture, fallback fixture, compatibility fixture or positive assertion input.

## Parent/Master Coverage

| Parent Requirement | Coverage |
|---|---|
| `MD-PR1` | Enforces the mock-only fixture policy in default/standard commands and guards against real fixture fallback. |
| `MD-PR7` | Migrates or deactivates old standard gates that used KI-fuer-KMU by default. |
| `MD-PR8` | Narrows to README command references directly coupled to standard gate behavior; full docs sync remains MD-E2E-4. |

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `MD-PR1` | No default, fallback or compatibility path may use KI-fuer-KMU. | preserves | Block standard success when real fixture references remain in scripts or standard evidence. |
| `MD-PR7` | `run-mock-e2e-checks.sh all --keep` becomes the leading standard gate; `run-contract-checks.sh all` is a mock-only shim or is removed from the standard path. | preserves | Implement exact script/README migration and verify both standard commands. |
| `MD-PR8` | README command snippets are updated only where they define standard gate behavior. | narrows_with_rationale | Final parent/canonical docs closeout remains MD-E2E-4. |
| `MD-PR9` | Live-agent path is irrelevant for this migration. | defers_to_child | Keep local mock runner as the accepted baseline. |

No parent requirement is missing or contradicted.

## Decision Freeze Pack

| Decision | Frozen Value | Rationale |
|---|---|---|
| Leading standard E2E gate | `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep` | Accepted MD-E2E-2 runner already proves large and small mock flows without external dependencies. |
| `run-contract-checks.sh all` fate | Keep only as a mock-only standard-compatible shim, or remove it from README standard quickstart. It must not call `setup-fixture.sh` with real defaults. | Preserves a familiar command name without preserving the bad fixture source. |
| `tc1` / `tc2` legacy selectors | Non-standard legacy selectors. They may require an explicit `--fixture` and must run a forbidden-real-fixture guard before pass, or be marked unavailable. | Prevents old L0 real-fixture checks from counting as standard regression evidence. |
| `reporting` selector | May delegate to existing reporting runner if it does not use real fixture data. | Reporting is already separate from the KI-fuer-KMU setup path. |
| `setup-fixture.sh` no-arg behavior | Must not copy KI-fuer-KMU. No-arg invocation either fails with exit `2` and a clear message or creates only source-controlled mock fixture data. | No silent real fixture creation remains. |
| KI-fuer-KMU references in scripts | None allowed. | Scripts are executable gates, not historical docs. |
| KI-fuer-KMU references in README | The literal name may appear only as historical/non-gating context. Absolute source paths and quickstart/default fixture instructions are forbidden. | Lets docs explain the migration without giving users a usable real-fixture path. |
| Compatibility fixture | Forbidden. | Parent explicitly disallows keeping KI-fuer-KMU alive as fallback. |

## Normative Contract

### Standard Gate Contract

`run-mock-e2e-checks.sh all --keep` is the primary standard command. It must:

- run from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`;
- use only `tests/docworkflow-agent-delivery/mock-data/**` and generated isolated evidence roots;
- report `RESULT: PASS` only when both large and small mock paths pass;
- write retained summary evidence for the run;
- include forbidden-real-fixture validation in the generated evidence;
- require no network, Docker, Codex auth, external provider or manual session start.

### Legacy Contract Runner Migration

`run-contract-checks.sh all` must become one of these two implementation forms:

1. Preferred: a shim that invokes `run-mock-e2e-checks.sh all`, propagates `--keep`, and returns the mock runner exit code.
2. Acceptable: a non-leading legacy command that exits non-zero unless an explicit mock-safe fixture is supplied; README must not present it as quickstart or standard E2E evidence.

If `run-contract-checks.sh all --keep` remains executable, its success evidence must be mock-only. It must not invoke `setup-fixture.sh` with an implicit source, must not set `source_specs` to KI-fuer-KMU, and must not create positive evidence from real product specs.

`tc1` and `tc2` selectors are not standard gates after this child. If retained, they must be explicit fixture-only selectors. A missing `--fixture` must fail, or the selector must route to a source-controlled mock fixture. A real product source path is never accepted as positive fixture input.

### Fixture Setup Contract

`setup-fixture.sh` must not contain an absolute default source path. A no-argument call must not copy real specs. Allowed forms:

- `setup-fixture.sh --fixture-dir <dir> --source-specs <mock-safe-source>` with a source that is not forbidden by the accepted MD-E2E-1 policy; or
- a rewritten mock fixture setup that copies only source-controlled mock data.

The script must reject the absolute KI-fuer-KMU path and any source path matching the forbidden-real-fixture policy. Rejection is a successful negative guard when tested.

### README Command Contract

README quickstart must lead with:

```sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep
```

Any mention of `run-contract-checks.sh all` must state that it is a mock-only shim or legacy/non-leading command. Any mention of `setup-fixture.sh` must be explicit-only and must not show a no-arg command that creates real fixtures.

## Canonical Examples and Fixtures

Pattern: referenced fixture files.

The implementation consumes accepted fixture and runner artifacts from prior children:

| Fixture / Artifact | Owner | Normative Fields / Behavior |
|---|---|---|
| `tests/docworkflow-agent-delivery/mock-data/**` | Accepted MD-E2E-1 | Mock fixture source; must remain read-only in this child. |
| `tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js` | Accepted MD-E2E-1 | Forbidden source policy and validation behavior. |
| `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh` | Accepted MD-E2E-2, wiring allowed in this child | `large`, `small`, `all`, `--keep`, `--run-id`; local mock baseline. |
| `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-all/aggregate-summary.json` | Accepted MD-E2E-2 | Proof that the mock `all` selector exists and passes before migration. |

No new fixture authoring is required or allowed in this child. Harness verification proves fixture exercise through the retained `run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-3-mock-all` summary and forbidden-real-fixture evidence.

## Control Flow and Failure Cases

1. User or CI invokes the standard command.
2. README and handoff point first to `run-mock-e2e-checks.sh all --keep`.
3. Optional legacy `run-contract-checks.sh all --keep` either delegates to the mock runner or exits with a clear non-standard/legacy failure.
4. Standard success requires mock runner success plus forbidden-real-fixture guard success.
5. Any executable script reference to KI-fuer-KMU, any absolute real source default, or any compatibility fixture path blocks closeout.

Failure classes:

| Failure | Required Behavior |
|---|---|
| Script contains KI-fuer-KMU default | Verification fails before acceptance. |
| `setup-fixture.sh` no-arg copies real specs | Verification fails. |
| `run-contract-checks.sh all` succeeds through real fixture setup | Verification fails. |
| README quickstart still uses legacy real fixture path | Verification fails. |
| Mock runner fails | Standard gate fails. |
| Forbidden-real-fixture validator finds a real path in generated evidence | Standard gate fails. |

## Harness and Verification Cases

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|
| `MOCK-STANDARD-ALL-MOCK` | Prove the leading standard command uses accepted mock data. | `run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-3-mock-all`. | Exit `0`; aggregate summary `pass`; forbidden fixture status `pass`. | Retained closeout evidence under `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-3-mock-all/`. | No network, Docker, Codex auth, manual start or real repo path. |
| `MOCK-CONTRACT-ALL-SHIM` | Prove the old standard command name no longer uses real defaults. | `run-contract-checks.sh all --keep`. | Exit `0` only if it delegates to mock-only gate; otherwise documented non-standard exit is allowed only if README no longer presents it as standard. | Mock evidence or clear non-standard message. | Must not call `setup-fixture.sh` with real default; must not set `source_specs` to KI-fuer-KMU. |
| `MOCK-LEGACY-FIXTURE-NO-DEFAULT` | Prove fixture setup cannot silently copy real specs. | `setup-fixture.sh` with no args and with explicit forbidden source path. | No-arg exits `2` or creates mock-only fixture; forbidden source exits non-zero. | Error text naming explicit/mock-only usage or mock fixture evidence. | Absolute KI-fuer-KMU path is rejected, not normalized. |
| `MOCK-FORBID-REAL-FIXTURE` | Prove scripts and generated evidence have no real fixture fallback. | Scripts plus retained closeout run root. | Guard commands exit `0`. | Forbidden-real-fixture evidence JSON. | No script match for `ki-fuer-kmu`; no absolute KI path in README. |
| `MOCK-README-STANDARD-COMMAND` | Prove command docs steer users to mock E2E. | `tests/docworkflow-agent-delivery/README.md`. | Inspection/grep passes. | README quickstart shows mock `all --keep`; legacy commands are absent from quickstart or labelled non-leading. | No no-arg `setup-fixture.sh` fixture recipe; no absolute real fixture path. |

## Verification Commands

Execution context:

- CWD: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Shell: `zsh` or `bash`; scripts use `#!/usr/bin/env bash`.
- Runtime: Node.js and Bash for script gates; .NET 10 for child readiness validation.
- Network/Docker/Codex auth: not required.

Rehearsal evidence already collected during hardening:

- `bash -n tests/docworkflow-agent-delivery/scripts/*.sh` passed.
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id hardening-md-e2e-3-rehearsal` passed and wrote `tests/docworkflow-agent-delivery/e2e/evidence/hardening-md-e2e-3-rehearsal/mock-e2e-summary.json`.
- `run-contract-checks.sh --help` and `setup-fixture.sh --help` confirmed current CLI shapes.
- `rg` preflight found current forbidden defaults in `run-contract-checks.sh`, `setup-fixture.sh` and README; these are the delivery targets.
- `node --version` returned `v22.12.0`; `dotnet --list-sdks` includes .NET 10.

Delivery gate after implementation:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/*.sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-3-mock-all
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all --keep
```

No-default-real-fixture guards:

```sh
if rg -n "/Users/dh/Documents/DanielsVault/ki-fuer-kmu|ki-fuer-kmu" tests/docworkflow-agent-delivery/scripts; then
  echo "Forbidden real fixture reference remains in executable scripts" >&2
  exit 1
fi

if rg -n "/Users/dh/Documents/DanielsVault/ki-fuer-kmu" tests/docworkflow-agent-delivery/README.md; then
  echo "Forbidden absolute real fixture path remains in README" >&2
  exit 1
fi

if rg -n 'setup-fixture\.sh( \| |$)' tests/docworkflow-agent-delivery/README.md; then
  echo "README still documents no-arg setup-fixture usage; inspect and either remove it or label explicit mock-only usage" >&2
  exit 1
fi
```

OpenSpec/readiness/hygiene:

```sh
openspec validate docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration --strict
cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md" --child MD-E2E-3 --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/md-e2e-3-session-handoff.md"
git diff --check
```

Anti-loop rule: do not add a command whose only effect is to verify that another verification command was listed. Every command above must inspect executable syntax, run the accepted mock path, run the migrated standard path, validate absence of real defaults, validate OpenSpec/readiness state, or check patch hygiene.

## Definition of Ready for Implementation

- Parent, child spec, Child Index and handoff all identify `MD-E2E-3`.
- Readiness verdict is `IMPLEMENTATION READY`.
- Migration strategy is frozen: mock `all --keep` is leading standard; no KI-fuer-KMU default/fallback/compatibility fixture remains.
- Allowed write-set is concrete and bounded.
- Required positive, negative and documentation cases are listed above.
- High-risk commands have rehearsal evidence or are explicitly delivery-only because their current behavior is the defect being changed.
- Persisted handoff exists at `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`.
- Agent Delivery queue evidence exists before the implementation session starts.

## Definition of Done / Closeout Evidence

Closeout must retain or cite:

- passing `bash -n tests/docworkflow-agent-delivery/scripts/*.sh`;
- retained mock all evidence from `closeout-md-e2e-3-mock-all`;
- `run-contract-checks.sh all --keep` result or explicit evidence that it is no longer a standard command and README no longer presents it as one;
- no-default-real-fixture guard output over scripts and README;
- `openspec validate docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration --strict`;
- `git diff --check`;
- Child Index row updated from `IMPLEMENTATION READY` to implementation/closeout result only after evidence exists;
- handoff and OpenSpec evidence synced for MD-E2E-4 documentation closeout.

## Dependencies and Write-Set

Dependencies:

- `MD-E2E-1` accepted mock fixtures and forbidden-real-fixture validator.
- `MD-E2E-2` accepted local mock runner and retained `all` evidence.
- Current `run-contract-checks.sh`, `setup-fixture.sh`, `run-mock-e2e-checks.sh` and README command references.

Implementation write-set:

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`
- `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`
- `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration/**`
- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/README.md`

Shared/read-only files:

- `tests/docworkflow-agent-delivery/mock-data/**`
- `tests/docworkflow-agent-delivery/e2e/mock-runner/**`
- `tests/docworkflow-agent-delivery/e2e/validators/**` except no edits are expected for this child
- accepted MD-E2E-1 and MD-E2E-2 archived OpenSpec evidence
- KI-fuer-KMU and all other real product repositories
- retained DWT historical evidence unless MD-E2E-4 later marks documentation state

Parallelism:

- Runtime implementation should run serially after MD-E2E-2 acceptance because it touches standard scripts and README command references.
- MD-E2E-4 may draft docs after this child but cannot finalize until this child has closeout evidence.

## Closeout Sync Targets

- Child Index row for `MD-E2E-3`.
- `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`.
- OpenSpec change `docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration`.
- README command references directly coupled to standard gate behavior.
- MD-E2E-4 handoff/backlog note that final docs sync must cite MD-E2E-3 evidence.

## Child Session Handoff

Persisted handoff:

- `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`

Next mode/skill:

- `spec-change-delivery` for `MD-E2E-3`.

Implementation sessions must read the handoff, Child Index row and this child spec before editing. If any of those disagree, stop with `NOT READY` and persist evidence instead of changing runtime files.

## Content Quality Review

- Correctness/domain fit: Pass. The child removes a known real-fixture default and promotes the accepted mock E2E runner as the standard path.
- Necessity/scope: Pass. Changes are limited to standard gate routing, fixture setup defaults, directly coupled README commands and OpenSpec ledger.
- Completeness: Pass. The spec freezes command behavior, failure modes, residual reference policy, cases, verification, write-set, dependencies and closeout evidence.
- Consistency: Pass. It preserves parent MD-PR1 and MD-PR7, narrows README work for MD-PR8, and leaves final docs sync to MD-E2E-4.
- Unambiguity: Pass. The implementation has exact allowed outcomes for `run-contract-checks.sh all`, `setup-fixture.sh`, README and forbidden references.
- Feasibility: Pass. Accepted MD-E2E-2 mock runner already passes; the remaining work is bounded script/docs migration.
- Verifiability/testability: Pass. Positive, negative and guard commands are concrete.
- Traceability: Pass. Parent requirements, child cases and closeout evidence are mapped.
- Operational/lifecycle fit: Pass. OpenSpec ledger, readiness validator and implementation handoff are defined.
- Blocking Marker: None.

## Implementation Closeout Evidence

- `bash -n tests/docworkflow-agent-delivery/scripts/*.sh`: passed.
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-3-mock-all`: passed; retained evidence at `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-3-mock-all/mock-e2e-summary.json`.
- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all --keep`: passed as a mock-only shim; retained evidence at `tests/docworkflow-agent-delivery/e2e/evidence/20260509T081555Z-all/mock-e2e-summary.json`.
- No-default-real-fixture guards over executable scripts and README: passed.
- Negative setup checks: no-arg fixture setup exits `2`; explicit forbidden real fixture source exits non-zero; legacy `tc1` without explicit fixture exits `2`.
- `openspec validate docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration --strict`: passed.
- `ValidateChildReadiness.cs` for `MD-E2E-3`: passed.
- `git diff --check`: passed.

## Mini-Retro

- Was wurde entschieden? The standard gate is `run-mock-e2e-checks.sh all --keep`; `run-contract-checks.sh all` can only survive as a mock-only shim or non-leading legacy command.
- Was wurde geaendert? The standard command path now routes to mock-only evidence; legacy fixture setup is explicit-only and rejects forbidden real sources; README quickstart points to the mock E2E gate.
- Was bleibt offen? Final parent/canonical documentation synchronization remains MD-E2E-4; OpenSpec archive is a post-acceptance closeout step.
- Welche Evidenz/Verification fehlt? No required MD-E2E-3 delivery evidence is missing after this implementation run.
- Welche Skill-/Workflow-Reibung ist aufgefallen? The child-readiness validator still expects an implementation-allowing verdict even after delivery evidence exists, so the index/handoff keep `IMPLEMENTATION READY` while appending implemented evidence.
- Session-/Kontextzustand: Implemented with retained evidence; ready for acceptance/closeout and MD-E2E-4 documentation sync.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-09 | Codex | Hardened MD-E2E-3 from skeleton to implementation-ready migration contract. |
| 2026-05-09 | Codex | Implemented MD-E2E-3 standard gate migration and captured closeout evidence. |
