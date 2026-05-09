**Date:** 2026-05-09
**Status:** NEEDS HARDENING
**Scope:** Child spec skeleton for migration/deactivation of old standard gates that default to KI-fuer-KMU fixtures.

---

## Review Control Surface

- Spec-Variante: Child Spec skeleton.
- Goldstandard Status: not hardened.
- Ziel: Remove KI-fuer-KMU from standard Agent Delivery test gates and make the mock E2E runner the standard regression path.
- In Scope: `run-contract-checks.sh`, `setup-fixture.sh`, standard `all` routing, non-gating/historical treatment of old L0 real-fixture checks, no-compatibility-fixture enforcement.
- Out of Scope: creating fixtures, implementing runner internals, broad DWT historical rewrite, final parent docs sync beyond command references needed for gate behavior.
- Wichtigste Test-/Harness-Cases: `MOCK-MIGRATE-EXISTING-TESTS`, `MOCK-FORBID-REAL-FIXTURE`.
- Wichtigste Verification Commands: future standard `all` gate selected during hardening, `run-mock-e2e-checks.sh all --keep`, no-default-KI-fuer-KMU guard.
- Offene Entscheidungen: whether legacy L0 remains as explicit non-gating selector or is fully removed from standard commands.
- Readiness Status: NEEDS HARDENING.

## Goal

Ensure the standard Agent Delivery testsuite cannot pass by reading KI-fuer-KMU or any real product fixture. Historical references may remain only as documentation or explicit non-gating retro paths; they must not be default, compatibility mode or positive fixture input.

## Parent Coverage

| Parent Requirement | Coverage |
|---|---|
| `MD-PR1` | Makes mock-only fixture policy enforceable in default commands. |
| `MD-PR7` | Migrates or disables old standard gates using real product fixtures. |

## Dependencies

- `MD-E2E-1` accepted or ready, so replacement mock fixtures exist.
- `MD-E2E-2` accepted or ready, so `run-mock-e2e-checks.sh all --keep` exists.
- Current scripts: `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`, `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`.

## Allowed Write-Set

- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md`
- `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`
- `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`
- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/README.md` only for command references directly coupled to standard gate behavior

## Shared / Read-only Files

- `tests/docworkflow-agent-delivery/mock-data/**` should be treated as accepted inputs from MD-E2E-1.
- `tests/docworkflow-agent-delivery/e2e/**` should be treated as accepted runner behavior from MD-E2E-2.
- Existing retained evidence under DWT paths is historical/read-only unless hardening explicitly permits metadata marking.
- KI-fuer-KMU and other real product repositories are forbidden as fixture sources.

## Acceptance Criteria

1. Standard Agent Delivery test command no longer defaults `source_specs` to `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs`.
2. `setup-fixture.sh` does not silently copy KI-fuer-KMU as default fixture data.
3. `run-contract-checks.sh all` is either migrated to mock data or explicitly no longer the leading standard gate.
4. Leading standard gate uses `run-mock-e2e-checks.sh all --keep` or an equivalent mock-only command.
5. Any legacy KI-fuer-KMU path is explicit, non-gating, historical/retro-only and cannot produce a standard pass.
6. No compatibility fixture keeps KI-fuer-KMU alive as fallback.
7. Forbidden-real-fixture validator runs in or before the standard gate.

## Verification Commands

Hardening must freeze exact commands. Candidate commands:

```sh
bash -n tests/docworkflow-agent-delivery/scripts/*.sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all
rg -n "/Users/dh/Documents/DanielsVault/ki-fuer-kmu|ki-fuer-kmu" tests/docworkflow-agent-delivery/scripts tests/docworkflow-agent-delivery/README.md
git diff --check
```

The `rg` command is not by itself pass/fail until hardening defines allowed historical references. It must at minimum prove no default positive fixture path remains.

## Evidence / Closeout Erwartung

- Command output showing the mock-only standard gate passes.
- Evidence that any KI-fuer-KMU references are historical/read-only/non-gating.
- Clear README command snippet or handoff note for the next user.
- Child Index updated before MD-E2E-4 final documentation sync.

## Hardening Bedarf

- Decide fate of old L0 command names.
- Define exact allowed residual KI-fuer-KMU references.
- Define whether README command updates are in this child or deferred to MD-E2E-4.
- Rehearse no-default-real-fixture guard.

## Empfohlene Naechste Session

Harden after MD-E2E-2 has a stable command contract. Keep KI-fuer-KMU fully out of standard test data.

