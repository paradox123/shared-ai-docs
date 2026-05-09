# Scope Contract

## In Scope

- `run-contract-checks.sh all` standard routing.
- `setup-fixture.sh` no-default behavior and forbidden-source rejection.
- README quickstart and command references directly coupled to standard gate behavior.
- OpenSpec ledger and closeout evidence for `MD-E2E-3`.

## Out of Scope

- New mock fixture authoring.
- Accepted `MD-E2E-1` mock-data contract edits.
- `MD-E2E-2` mock-runner internals beyond standard routing integration.
- Final parent/canonical documentation closeout beyond directly coupled README command references.
- Live-agent or Codex execution.

## Acceptance Targets

- `run-mock-e2e-checks.sh all --keep` is the leading standard gate.
- `run-contract-checks.sh all --keep` succeeds only through the mock-only runner.
- No executable script contains the forbidden real fixture literal or absolute path.
- `setup-fixture.sh` with no args exits non-zero and cannot copy a real fixture by default.
- README quickstart starts with the mock E2E command and does not document no-arg fixture setup.
