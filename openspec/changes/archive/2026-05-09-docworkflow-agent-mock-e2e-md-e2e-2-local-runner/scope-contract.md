# Scope Contract

## In Scope

- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/e2e/mock-runner/**`
- `tests/docworkflow-agent-delivery/e2e/validators/mock-e2e-summary.js`
- `tests/docworkflow-agent-delivery/e2e/fixtures/mock-runner-negative/**`
- `tests/docworkflow-agent-delivery/e2e/evidence/**` for retained MD-E2E-2 evidence
- MD-E2E-2 child spec, handoff and Child Index row synchronization
- Active OpenSpec change files for `docworkflow-agent-mock-e2e-md-e2e-2-local-runner`

## Conditional Scope

- `tests/docworkflow-agent-delivery/mock-data/**` may be edited only for an accepted MD-E2E-1 compatibility fix. Any such fix must be documented in the implementation evidence and must not change the accepted fixture semantics.

## Out Of Scope

- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`
- `tests/docworkflow-agent-delivery/README.md`
- `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` canonical sync
- legacy standard gate migration
- live-agent/Codex execution
- Docker, network, external provider or manual-start integration
- KI-fuer-KMU or other real product fixture compatibility

## Exit Criteria

The change can close only after large, small and all selectors pass with retained evidence, bad states are proven unable to pass, forbidden-real-fixture checks pass over generated evidence, and OpenSpec plus whitespace checks pass.
