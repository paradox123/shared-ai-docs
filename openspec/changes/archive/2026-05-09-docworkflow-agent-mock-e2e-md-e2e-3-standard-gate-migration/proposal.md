# MD-E2E-3 Standard Gate Migration

## Why

The Agent Delivery testsuite still exposes legacy standard commands that can create or consume real product fixtures by default. The accepted mock E2E runner from `MD-E2E-2` is now available, so the standard gate can be moved to source-controlled mock data only.

## What

- Make `run-mock-e2e-checks.sh all --keep` the leading standard command.
- Convert `run-contract-checks.sh all --keep` into a mock-only compatibility shim.
- Make legacy fixture setup explicit-only and reject forbidden real fixture sources.
- Update README standard command references to lead with the mock E2E gate.
- Record verification evidence that no default, fallback or compatibility fixture path remains.

## Impact

- Removes real product fixture defaults from executable standard paths.
- Preserves the familiar `run-contract-checks.sh all --keep` command name as a mock-only route.
- Leaves legacy TC1/TC2 fixture checks explicit-only and outside the standard gate.
