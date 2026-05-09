**Date:** 2026-05-09
**Status:** NEEDS HARDENING
**Scope:** Child spec skeleton for the local mock session runner and `run-mock-e2e-checks.sh large/small/all`.

---

## Review Control Surface

- Spec-Variante: Child Spec skeleton.
- Goldstandard Status: not hardened.
- Ziel: Implement a local mock session runner that proves large parent/child and small direct E2E flows without network, Docker, Codex auth or manual starts.
- In Scope: runner state machine, `run-mock-e2e-checks.sh`, large/small/all selectors, session evidence, summary artifact, mock target output validation, write-boundary checks.
- Out of Scope: creating base fixture contracts owned by MD-E2E-1, legacy standard gate migration owned by MD-E2E-3, docs sync owned by MD-E2E-4, live-agent/Codex execution owned by MD-E2E-5.
- Wichtigste Test-/Harness-Cases: `MOCK-LARGE-E2E`, `MOCK-SMALL-E2E`, `MOCK-SESSION-CHAIN`, `mock-large-artifact-e2e`, `mock-small-direct-artifact`, `mock-child-write-boundary`.
- Wichtigste Verification Commands: future `run-mock-e2e-checks.sh large --keep`, `small --keep`, `all --keep`.
- Offene Entscheidungen: runner implementation language and exact evidence tree are not frozen yet.
- Readiness Status: NEEDS HARDENING.

## Goal

Materialize the Agent Delivery Workflow locally and deterministically. The runner must not fake pass evidence: it must create parent control output, child specs, handoffs, per-step session evidence, target outputs and summary artifacts in isolated run directories.

## Parent Coverage

| Parent Requirement | Coverage |
|---|---|
| `MD-PR4` | Large path from mock parent to final `count.txt`. |
| `MD-PR5` | Small path direct delivery with no child artifacts. |
| `MD-PR6` | Machine-readable session and summary evidence. |

## Dependencies

- `MD-E2E-1` fixture and forbidden validator contract hardened and preferably accepted.
- Parent spec and orchestration pack.

## Allowed Write-Set

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-2 Local Mock Session Runner.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`
- `_specs/child-session-handoffs/md-e2e-2-session-handoff.md`
- `tests/docworkflow-agent-delivery/e2e/**`
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/mock-data/**` only for compatibility fixes required by the accepted MD-E2E-1 contract

## Shared / Read-only Files

- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`
- `tests/docworkflow-agent-delivery/README.md`
- Existing DWT L1/L2/L3/reporting harnesses and accepted evidence
- KI-fuer-KMU and other real product repositories

## Acceptance Criteria

1. `run-mock-e2e-checks.sh` supports `large`, `small`, `all` and `--keep`.
2. Large run creates isolated run root and mock target.
3. Large run records `sizing_decision: parent_child`.
4. Large run creates parent control output, child index, exactly five child specs and five handoffs for `ML-C1` through `ML-C5`.
5. Large run records session evidence for each child with `started` or automatic resume and final `ran-target`, followed by closeout before the next child.
6. Large run writes `mock-target/output/count.txt` exactly as `1\n2\n3\n4\n5\n`.
7. Each child writes only its own number and only inside the mock target.
8. Small run records `sizing_decision: direct`, creates no child index/spec/handoff/session queue and writes the expected direct output.
9. Summary artifact uses `docworkflow-agent-delivery-mock-e2e-summary.v1`.
10. `manual_start_required`, permanent `queued`, `blocked`, `failed` or dry-run-only evidence cannot pass the leading large E2E.
11. Runner requires no network, Docker, Codex auth, external agent provider or manual session start.

## Verification Commands

Hardening must freeze exact command paths. Candidate delivery commands:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh small --keep
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep
git diff --check
```

## Evidence / Closeout Erwartung

- Retained large and small run directories or stable retained summaries.
- `mock-e2e-summary.json` for both large and small cases.
- Session evidence list for `ML-C1` through `ML-C5`.
- Output evidence for `count.txt` and `small-direct-result.json`.
- Explicit no-forbidden-fixture result from the accepted MD-E2E-1 validator.

## Hardening Bedarf

- Freeze runner language and file layout.
- Define exact output directory and summary schema assertions.
- Define generated parent control/child index/handoff minimal contents.
- Define negative cases for queued/manual/blocked/failed states.
- Clarify how runner records command telemetry without invoking live agents.

## Empfohlene Naechste Session

Harden after MD-E2E-1 is ready or accepted. Do not start implementation from this skeleton.

