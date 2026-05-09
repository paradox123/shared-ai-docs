**Date:** 2026-05-09
**Status:** 🟡 Orchestrated
**Scope:** Parent/Child control pack for the DocWorkflow Agent Delivery Mock Data E2E Harness. No runtime or harness implementation is released by this artifact.

---

## Review Control Surface

- Spec-Variante: Delivery Orchestration Pack for a Parent/Control Spec.
- Goldstandard Status: orchestration draft, ready for child hardening.
- Ziel: Split `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md` into hardening-ready Child Specs, make coverage and dependencies explicit, and prevent direct one-session implementation.
- In Scope: Child Index, Coverage Matrix, Parent Scope Conformance, Hardening Queue, allowed write-sets, shared/read-only files, verification expectations, closeout expectations and next-session handoffs.
- Out of Scope: creating mock fixture files, editing runner scripts, changing README behavior, modifying OpenSpec canonical specs, launching live agents, or touching KI-fuer-KMU.
- Wichtigste Test-/Harness-Cases: `MOCK-FORBID-REAL-FIXTURE`, `MOCK-LARGE-E2E`, `MOCK-SMALL-E2E`, `MOCK-MIGRATE-EXISTING-TESTS`, `MOCK-SESSION-CHAIN`.
- Wichtigste Verification Commands: `git diff --check`; after later hardening, per-child `ValidateChildReadiness.cs`; after later implementation, the child-specific commands listed below.
- Offene Entscheidungen: No product decision is blocking. OpenSpec ledger ids are proposed but not created in this orchestration-only pass.
- Readiness Status: ORCHESTRATION COMPLETE; `MD-E2E-1` is `IMPLEMENTATION READY` after child-spec-hardening; `MD-E2E-2` through `MD-E2E-4` still need hardening; `MD-E2E-5` is deferred.

## Session Briefing

- Modus/Skill: `spec-orchestrator`.
- Source of Truth: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`; `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`; `docs/doc-workflow.md`.
- Ziel: Turn the large mock-data E2E harness spec into bounded child slices with coverage, dependencies and hardening queue.
- Nicht-Ziele: No code implementation, no script edits, no fixture creation, no OpenSpec active change creation, no live session launch.
- In Scope: Child Specs and handoffs under `_specs/**`, operational Child Index, coverage and handoff-ready next actions.
- Erwarteter Output: this orchestration pack, child spec files, child handoffs and a clear first hardening recommendation.
- Verification/Review: Docs-only sanity checks and `git diff --check`.
- Offene Entscheidungen: Whether the later implementation ledger creates one OpenSpec change per child or one parent OpenSpec change with child tasks is left to child hardening. Preferred default: one OpenSpec change per child.

## Parent Requirements

| Requirement | Summary | Source |
|---|---|---|
| `MD-PR1` | Mock data is the only standard Agent Delivery E2E fixture source; KI-fuer-KMU and other real product fixtures are forbidden. | Sections 1, 2, 5, 10 |
| `MD-PR2` | Large-path mock parent fixture exists with manifest, forced parent/child sizing, exactly `ML-C1` through `ML-C5`, and expected `count.txt`. | Sections 3.1, 3.3, 4.1 |
| `MD-PR3` | Small direct mock fixture exists with manifest, direct sizing, no child artifacts and expected JSON output. | Sections 3.2, 3.3, 4.2 |
| `MD-PR4` | Local Mock Session Runner drives the large path through sizing, parent control, five child sessions, closeout and final count output. | Sections 2.2, 4.1, 4.3, 6, 7 |
| `MD-PR5` | Local Mock Session Runner drives the small path as direct delivery with no child control artifacts. | Sections 2.2, 4.2, 6, 7 |
| `MD-PR6` | Session and summary evidence are machine-readable and distinguish positive, queued, blocked, manual and failed states. | Sections 4.3, 7 |
| `MD-PR7` | Existing standard gates stop using KI-fuer-KMU by default; old gates are migrated, replaced, or non-gating/historical. | Sections 2.1, 4.4, 4.5, 10 |
| `MD-PR8` | README, parent testsuite spec and evidence docs explain mock-first strategy, standard command and real-fixture exclusion. | Sections 4.5, 8, 10 |
| `MD-PR9` | Optional live-agent/Codex path is a separated follow-up and cannot block or replace the local mock runner baseline. | Sections 2.2, 8, 10 |

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MD-E2E-1 | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-1 Mock Fixtures.md` | `MD-PR1`, `MD-PR2`, `MD-PR3`; supports `MD-PR7` | `IMPLEMENTATION READY`; hardening completed for fixture, manifest and forbidden-path validator contract | `child-session-handoffs/md-e2e-1-session-handoff.md` | `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-1-mock-fixtures/` | Parent spec; existing dirs `tests/docworkflow-agent-delivery/mock-data/large-parent`, `tests/docworkflow-agent-delivery/mock-data/small-direct`, `tests/docworkflow-agent-delivery/e2e` are adopted as implementation roots | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-1 Mock Fixtures.md`; `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`; `_specs/child-session-handoffs/md-e2e-1-session-handoff.md`; `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-1-mock-fixtures/**`; `tests/docworkflow-agent-delivery/mock-data/large-parent/**`; `tests/docworkflow-agent-delivery/mock-data/small-direct/**`; `tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js`; `tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js`; `tests/docworkflow-agent-delivery/e2e/fixtures/manifest-schema-valid-large/**`; `tests/docworkflow-agent-delivery/e2e/fixtures/manifest-schema-valid-small/**`; `tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture/**` | Preflight: `node --version`; `git diff --check`; `ValidateChildReadiness.cs` for `MD-E2E-1`. Delivery: manifest schema validator, forbidden-real-fixture validator positive scan, forbidden-real-fixture negative scan, `git diff --check` | Hardening evidence: child spec, handoff, Child Index and queued launch evidence `_specs/agent-delivery-session-launches/20260509T050712Z-md-e2e-1/evidence.json`; implementation closeout must link manifest files, source specs, validator outputs and no-KI-fuer-KMU evidence | If implementation discovers runner-coupled fixture ambiguity, stop and re-enter child-spec-hardening; do not widen into `MD-E2E-2` | `spec-change-delivery` may start for `MD-E2E-1` only |
| MD-E2E-2 | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-2 Local Mock Session Runner.md` | `MD-PR4`, `MD-PR5`, `MD-PR6`; consumes `MD-PR1` through `MD-PR3` | `NEEDS HARDENING`; runner contracts, command selectors and evidence schema need implementation-ready detail | `_specs/child-session-handoffs/md-e2e-2-session-handoff.md` | Proposed: `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-2-local-runner/` | `MD-E2E-1` fixture/manifests/validator contract accepted or at least frozen by hardening | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-2 Local Mock Session Runner.md`; `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`; `_specs/child-session-handoffs/md-e2e-2-session-handoff.md`; `tests/docworkflow-agent-delivery/e2e/**`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `tests/docworkflow-agent-delivery/mock-data/**` read/write only for test fixture compatibility fixes owned by MD-E2E-1 contract | After implementation: `bash -n tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep`; `small --keep`; `all --keep`; summary JSON assertions; `git diff --check` | Closeout must link retained large and small mock-e2e summaries, session evidence, target output evidence and failure evidence for forbidden states | Live-agent behavior is deferred to `MD-E2E-5`; any network/Docker/Codex-auth dependency is a runner bug for MD-E2E-2 baseline | Harden after `MD-E2E-1` |
| MD-E2E-3 | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md` | `MD-PR1`, `MD-PR7`; depends on runner command from `MD-E2E-2` | `NEEDS HARDENING`; exact migration/deactivation strategy must be frozen before delivery | `_specs/child-session-handoffs/md-e2e-3-session-handoff.md` | Proposed: `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration/` | `MD-E2E-1`; `MD-E2E-2`; current `run-contract-checks.sh` and `setup-fixture.sh` KI-fuer-KMU defaults | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md`; `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`; `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`; `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`; `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `tests/docworkflow-agent-delivery/README.md` only for command references directly coupled to standard gate behavior | After implementation: `bash -n tests/docworkflow-agent-delivery/scripts/*.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`; standard `all` command chosen during hardening; negative grep/validator proving no default KI-fuer-KMU fixture; `git diff --check` | Closeout must show old KI-fuer-KMU default removed, replaced or non-gating/historical, and no compatibility fixture remains | If legacy L0 behavior must be preserved for historical docs, move it behind explicit non-gating selector; do not keep KI-fuer-KMU as default or compatibility fixture | Harden after `MD-E2E-2` runner contract stabilizes |
| MD-E2E-4 | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-4 Documentation Sync.md` | `MD-PR8`; references all prior coverage | `NEEDS HARDENING`; documentation sync targets and accepted evidence links must be concrete | `_specs/child-session-handoffs/md-e2e-4-session-handoff.md` | Proposed: `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-4-doc-sync/` | `MD-E2E-1` through `MD-E2E-3` accepted or at least implemented with retained evidence | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-4 Documentation Sync.md`; `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`; `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`; `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`; `_specs/child-session-handoffs/md-e2e-4-session-handoff.md`; `tests/docworkflow-agent-delivery/README.md`; `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` if OpenSpec canonical sync is selected during hardening | After implementation: docs link checks by inspection or local validator; `openspec validate docworkflow-agent-delivery-testsuite --strict` if canonical spec changes; `git diff --check` | Closeout must synchronize parent status, child index rows, evidence pointers, standard command docs and mini-retro | If implementation evidence is incomplete, mark documentation as blocked instead of writing accepted claims | Harden after `MD-E2E-3`; can partially draft in parallel as docs-only, but final sync waits |
| MD-E2E-5 | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-5 Live Agent Follow-up.md` | `MD-PR9`; optional extension only | `DEFERRED FOLLOW-UP`; do not harden before local baseline is accepted | `_specs/child-session-handoffs/md-e2e-5-session-handoff.md` | Proposed later: `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-5-live-agent-follow-up/` | `MD-E2E-1` through `MD-E2E-4` accepted; local mock runner remains primary | `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-5 Live Agent Follow-up.md`; future live-agent harness files selected by separate hardening | Future only: launch/queue evidence with real adapter, auth/provider blockers represented as `blocked`, local baseline replay remains green | Closeout must prove live path writes compatible evidence and never replaces `local-mock-session-runner` acceptance | If auth/provider/network is unavailable, keep this follow-up blocked without impacting standard gate | Do not start until local baseline has closeout evidence |

## Coverage Matrix

| Parent Requirement | Owning Child | Coverage Status | Notes |
|---|---|---|---|
| `MD-PR1` | `MD-E2E-1`, `MD-E2E-3` | ready_for_md_e2e_1_implementation | Fixture policy is hardened in MD-E2E-1 and becomes standard-gate enforceable in MD-E2E-3. |
| `MD-PR2` | `MD-E2E-1` | ready_for_implementation | Large parent fixture, manifest, child list and count output contract are hardened. |
| `MD-PR3` | `MD-E2E-1` | ready_for_implementation | Small direct fixture, manifest and forbidden child artifact contract are hardened. |
| `MD-PR4` | `MD-E2E-2` | pending | Requires MD-E2E-1 fixtures and forbidden validator. |
| `MD-PR5` | `MD-E2E-2` | pending | Requires small-direct fixture from MD-E2E-1. |
| `MD-PR6` | `MD-E2E-2` | pending | Summary and session evidence schemas are runner-owned. |
| `MD-PR7` | `MD-E2E-3` | pending | Must remove KI-fuer-KMU from `run-contract-checks.sh`/`setup-fixture.sh` standard defaults. |
| `MD-PR8` | `MD-E2E-4` | pending | Final docs sync waits for accepted evidence from MD-E2E-1 through MD-E2E-3. |
| `MD-PR9` | `MD-E2E-5` | deferred | Optional follow-up; out of first baseline. |

No parent requirement is intentionally left missing. `MD-PR9` is explicitly deferred and must not be used to block the local baseline.

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `MD-PR1` | The standard fixture source moves completely to mock data; no KI-fuer-KMU compatibility fixture remains. | preserves | Carry this as a blocking gate in MD-E2E-1 and MD-E2E-3. |
| `MD-PR2` | Large-path fixture belongs to MD-E2E-1, not runner implementation. | narrows_with_rationale | Runner consumes the fixture in MD-E2E-2. |
| `MD-PR3` | Small-direct fixture belongs to MD-E2E-1, not runner implementation. | narrows_with_rationale | Runner consumes the fixture in MD-E2E-2. |
| `MD-PR4` | Large E2E local runner is isolated in MD-E2E-2. | preserves | Requires MD-E2E-1 contract first. |
| `MD-PR5` | Small E2E local runner is isolated in MD-E2E-2. | preserves | Requires MD-E2E-1 contract first. |
| `MD-PR6` | Evidence schemas are runner-owned but documentation sync later references accepted evidence. | defers_to_child | MD-E2E-4 may not invent success evidence. |
| `MD-PR7` | Legacy default migration is separated into MD-E2E-3. | preserves | Prevents fixture creation and runner code from also rewriting legacy gates. |
| `MD-PR8` | Documentation sync is separated into MD-E2E-4. | preserves | Prevents docs from claiming success before implementation evidence exists. |
| `MD-PR9` | Live-agent path is optional MD-E2E-5. | preserves | Keep deferred until local baseline is accepted. |

## Hardening Queue

| Order | Child | Hardening Need | Blocking Questions For Hardening |
|---|---|---|---|
| complete | `MD-E2E-1` | Hardening complete; ready for one-child implementation. | No blocking hardening questions remain. Implementation must follow the hardened spec and handoff. |
| 2 | `MD-E2E-2` | Define runner state machine, generated artifact tree, command selectors and summary/session evidence assertions. | Runner implementation language, exact evidence directory layout, child delivery simulation mechanics and failure fixtures. |
| 3 | `MD-E2E-3` | Freeze migration strategy for `run-contract-checks.sh` and `setup-fixture.sh`. | Does historical KI-fuer-KMU L0 move to explicit non-gating selector or get removed? What exact command becomes standard `all`? |
| 4 | `MD-E2E-4` | Define final docs/OpenSpec sync based on accepted evidence. | Which evidence paths are retained and which parent/canonical docs are updated after implementation? |
| deferred | `MD-E2E-5` | Live-agent follow-up is not part of first baseline. | Auth/provider/adapter decision and launch evidence strategy after local baseline. |

## Parallel Work Control Surface

| Work Block | Lane Mode | Allowed Parallelism | Shared / Read-only Files | Integration Owner |
|---|---|---|---|---|
| `MD-E2E-1` hardening | serial-first | Can harden alone immediately. | Parent spec, DWT accepted specs, current scripts read-only. | MD-E2E-1 hardening session. |
| `MD-E2E-2` hardening | serial after MD-E2E-1 | May begin drafting after MD-E2E-1 contracts are frozen, but cannot become ready first. | Fixture manifests from MD-E2E-1 read-only once accepted. | MD-E2E-2 hardening session. |
| `MD-E2E-3` hardening | serial after runner contract | Not parallel with MD-E2E-2 implementation because both may touch `run-mock-e2e-checks.sh` and standard scripts. | `run-contract-checks.sh`, `setup-fixture.sh`, README. | MD-E2E-3 hardening/session owner. |
| `MD-E2E-4` docs drafting | partially parallel | Can draft docs sync plan, but final accepted docs wait for MD-E2E-1..3 evidence. | Parent specs, README and OpenSpec canonical spec. | Final closeout owner. |
| `MD-E2E-5` live follow-up | deferred | No parallel start before local baseline accepted. | Local runner evidence remains canonical. | Future follow-up owner. |

## Recommended Execution Order

1. Implement `MD-E2E-1` with `spec-change-delivery` only, using the synchronized child spec and handoff.
2. Harden then implement `MD-E2E-2`, consuming the accepted fixture contracts.
3. Harden then implement `MD-E2E-3`, replacing/deactivating legacy standard gates after `run-mock-e2e-checks.sh all --keep` exists.
4. Harden then implement `MD-E2E-4` for final README, parent, OpenSpec and evidence sync.
5. Consider `MD-E2E-5` only after the local mock E2E baseline is accepted.

## Closeout Sync Checklist

- Child Index row status updated after each child hardening, delivery and closeout.
- Handoff freshness checked before any implementation session.
- Parent spec section 13 remains aligned with this orchestration pack.
- README standard commands identify mock data as the default E2E path.
- Any remaining KI-fuer-KMU references are historical/read-only/non-gating, never standard fixtures.
- Accepted evidence for large and small E2E is linked before MD-E2E-4 claims completion.
- OpenSpec canonical spec is validated if touched.

## Session Launch / Queue Evidence

Agent Delivery Session Launch/Queue Evidence exists for `MD-E2E-1` after child-spec-hardening:

- `_specs/agent-delivery-session-launches/20260509T050712Z-md-e2e-1/evidence.json`

`MD-E2E-2` through `MD-E2E-4` still require child-spec-hardening before launch evidence can be considered valid. `MD-E2E-5` remains deferred.

## Mini-Retro

- Was wurde entschieden? The Parent Spec is a control layer and must not be implemented as one bounded slice; `MD-E2E-1` is now the first implementation-ready child.
- Was wurde geaendert? Child boundaries, Child Index, Coverage Matrix, Hardening Queue and handoffs were established; `MD-E2E-1` was hardened.
- Was bleibt offen? `MD-E2E-2`, `MD-E2E-3` and `MD-E2E-4` still need child-spec-hardening; `MD-E2E-5` remains deferred.
- Welche Evidenz/Verification fehlt? Functional fixture and validator evidence is intentionally absent until `MD-E2E-1` implementation.
- Welche Skill-/Workflow-Reibung ist aufgefallen? The Parent Spec had an older "bounded follow-change" suggestion; this pack supersedes it because scope pressure requires orchestration and per-child hardening first.
- Session-/Kontextzustand: Start `spec-change-delivery` for `MD-E2E-1` in a fresh implementation session, or harden `MD-E2E-2` after `MD-E2E-1` delivery is accepted.
