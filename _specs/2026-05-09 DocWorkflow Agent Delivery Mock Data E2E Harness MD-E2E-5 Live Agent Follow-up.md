**Date:** 2026-05-09
**Status:** DEFERRED FOLLOW-UP
**Scope:** Optional future child for live Agent/Codex session path.

---

## Review Control Surface

- Spec-Variante: Deferred Child Spec skeleton.
- Goldstandard Status: not in first baseline.
- Ziel: Add a live-agent/Codex session path only after the local mock E2E baseline is accepted.
- In Scope: future live launch/queue evidence, provider/auth blockers, compatibility with `docworkflow-agent-delivery-mock-e2e-summary.v1`.
- Out of Scope: first accepted baseline, replacing local mock session runner, requiring network/Docker/Codex auth for standard gate.
- Wichtigste Test-/Harness-Cases: future live `MOCK-SESSION-CHAIN` supplement.
- Wichtigste Verification Commands: not defined until this follow-up is activated.
- Offene Entscheidungen: provider adapter, auth model, launch evidence mechanism.
- Readiness Status: DEFERRED; do not harden before MD-E2E-1 through MD-E2E-4 are accepted.

## Goal

Provide a future extension point for real agent-session proof while protecting the local deterministic baseline.

## Parent Coverage

| Parent Requirement | Coverage |
|---|---|
| `MD-PR9` | Optional live-agent/Codex path is separated and cannot block or replace local baseline. |

## Dependencies

- MD-E2E-1 through MD-E2E-4 accepted.
- Local `run-mock-e2e-checks.sh all --keep` remains the standard pass path.

## Allowed Write-Set

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-5 Live Agent Follow-up.md`
- `_specs/child-session-handoffs/md-e2e-5-session-handoff.md`
- Future live-agent harness files selected by a later hardening session

## Shared / Read-only Files

- Local mock runner and accepted baseline evidence are read-only compatibility contracts.
- Standard gate migration docs remain read-only unless a later parent/orchestrator reopens them.

## Acceptance Criteria

1. Live path writes evidence compatible with local summary/session schema.
2. Auth/provider/network/manual-start blockers are represented as `blocked`, not pass.
3. Local mock baseline remains required and green independently.
4. Live path cannot introduce KI-fuer-KMU or real product fixtures.

## Verification Commands

Not frozen. Future hardening must define commands and blocker behavior.

## Evidence / Closeout Erwartung

Future only. Must include launch/queue evidence and local baseline replay.

## Hardening Bedarf

- Full hardening required after local baseline acceptance.
- Define adapter and auth strategy.
- Rehearse or block high-risk launch commands before implementation.

## Empfohlene Naechste Session

Do not start now. Re-enter after MD-E2E-4 closeout.

