# MD-E2E-1 Mock Fixtures

## Why

The Agent Delivery E2E suite must stop using KI-fuer-KMU or other real product artifacts as standard fixtures. Later runner and standard-gate slices need small deterministic mock fixtures with machine-readable manifests and a hard failure when real fixture paths reappear.

## What

- Add the large parent mock fixture under `tests/docworkflow-agent-delivery/mock-data/large-parent/`.
- Add the small direct mock fixture under `tests/docworkflow-agent-delivery/mock-data/small-direct/`.
- Add `manifest.json` files matching the hardened MD-E2E-1 contract.
- Add Node validators for manifest schema and forbidden real fixture paths.
- Add positive and negative validator fixtures for manifest and forbidden-path behavior.

## Impact

- Gives `MD-E2E-2` stable local mock input data.
- Gives `MD-E2E-3` a deterministic forbidden-real-fixture validator to wire into standard gates.
- Keeps KI-fuer-KMU out of standard test data without preserving a compatibility fixture.

