**Date:** 2026-05-09
**Status:** NEEDS HARDENING
**Scope:** Child spec skeleton for README, Parent Spec, OpenSpec/canonical and evidence documentation sync.

---

## Review Control Surface

- Spec-Variante: Child Spec skeleton.
- Goldstandard Status: not hardened.
- Ziel: Synchronize docs after MD-E2E-1 through MD-E2E-3 so the accepted workflow points to mock data, mock E2E evidence and no-real-fixture policy.
- In Scope: README standard commands, Parent Spec status/history, orchestration pack closeout rows, DWT parent/canonical spec references if selected, evidence links, mini-retro.
- Out of Scope: changing runtime behavior, fixing runner failures, creating missing evidence, live-agent path.
- Wichtigste Test-/Harness-Cases: documentation coverage for `MOCK-LARGE-E2E`, `MOCK-SMALL-E2E`, `MOCK-MIGRATE-EXISTING-TESTS`, `MOCK-FORBID-REAL-FIXTURE`.
- Wichtigste Verification Commands: `git diff --check`; `openspec validate docworkflow-agent-delivery-testsuite --strict` only if OpenSpec canonical spec changes.
- Offene Entscheidungen: final evidence paths and whether OpenSpec canonical spec sync is in scope depend on prior closeouts.
- Readiness Status: NEEDS HARDENING.

## Goal

Make the documentation tell the truth after implementation: the leading E2E regression is mock-based, KI-fuer-KMU is not a fixture, and accepted evidence is linked without claiming optional live-agent support.

## Parent Coverage

| Parent Requirement | Coverage |
|---|---|
| `MD-PR8` | Docs and evidence sync for the mock-first E2E strategy. |
| `MD-PR1`, `MD-PR7` | Documentation states KI-fuer-KMU is historical/read-only/non-gating only. |

## Dependencies

- MD-E2E-1 through MD-E2E-3 implemented or at least their accepted evidence paths are known.
- Parent spec and orchestration pack.

## Allowed Write-Set

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-4 Documentation Sync.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`
- `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md`
- `_specs/child-session-handoffs/md-e2e-4-session-handoff.md`
- `tests/docworkflow-agent-delivery/README.md`
- `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` only if hardening selects OpenSpec canonical sync

## Shared / Read-only Files

- Runner scripts and fixture files are read-only evidence sources for this child.
- Accepted MD-E2E-1 through MD-E2E-3 evidence is read-only.
- KI-fuer-KMU and other real product repositories remain forbidden fixture sources.

## Acceptance Criteria

1. README identifies mock data as the standard Agent Delivery E2E fixture family.
2. README standard command points to `run-mock-e2e-checks.sh all --keep` or the accepted equivalent.
3. Parent spec and orchestration pack link accepted child evidence and final statuses.
4. DWT parent/canonical spec no longer implies KI-fuer-KMU-backed standard success for Agent Delivery E2E.
5. Documentation distinguishes historical retained evidence from current mock E2E evidence.
6. Optional live-agent path is documented only as follow-up and cannot replace local baseline.
7. Mini-retro records that direct Parent implementation was avoided.

## Verification Commands

Candidate commands:

```sh
openspec validate docworkflow-agent-delivery-testsuite --strict
git diff --check
```

If no OpenSpec file changes in implementation, the OpenSpec command can be documented as not applicable for this child closeout.

## Evidence / Closeout Erwartung

- Links to accepted MD-E2E-1, MD-E2E-2 and MD-E2E-3 evidence.
- Updated Child Index rows in orchestration pack.
- Parent history entry documenting docs sync.
- README snippet showing the standard command and no-real-fixture policy.

## Hardening Bedarf

- Determine final evidence links from prior children.
- Decide whether `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md` and OpenSpec canonical sync are mandatory or conditional.
- Define exact documentation assertions to avoid stale success claims.

## Empfohlene Naechste Session

Harden after MD-E2E-3 implementation evidence exists. Draft-only parallel work is safe, final sync is not.

