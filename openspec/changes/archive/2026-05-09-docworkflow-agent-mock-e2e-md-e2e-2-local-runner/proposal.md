# MD-E2E-2 Local Mock Session Runner

## Why

The accepted `MD-E2E-1` fixtures give the Agent Delivery testsuite deterministic mock inputs, but there is still no local runner that proves the workflow from fixture input to retained E2E evidence. The next slice must materialize the large parent/child path and small direct path without network, Docker, Codex auth, live agents or manual starts.

## What

- Add `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh` with `large`, `small` and `all` selectors plus `--keep`.
- Add Node-based local mock runner logic under `tests/docworkflow-agent-delivery/e2e/mock-runner/**`.
- Add summary validation for `docworkflow-agent-delivery-mock-e2e-summary.v1`.
- Generate retained evidence for large, small and aggregate runs.
- Enforce the accepted MD-E2E-1 manifest and forbidden-real-fixture validator contracts.
- Prove large-path session sequencing, closeout, output ownership and final `count.txt`.
- Prove small direct delivery creates no child-control artifacts.
- Add negative guards proving bad states cannot produce a positive pass summary.

## Impact

- Enables `MD-E2E-3` to migrate standard gates onto a concrete mock E2E command.
- Keeps live-agent/Codex execution as a later optional follow-up.
- Preserves accepted mock fixture contracts and avoids real product fixture compatibility paths.
