# Tasks

- [ ] Create L2 parent-first fixture directories under `tests/docworkflow-agent-delivery/l2/parent-first/fixtures/`.
- [ ] Implement output bundle validators under `tests/docworkflow-agent-delivery/l2/parent-first/validators/`.
- [ ] Add Promptfoo/Codex runner config and wrapper for parent-first orchestration.
- [ ] Add fallback artifact mode for stored output bundles and blocked-agent evidence.
- [ ] Add `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh` with `all`, `agent`, `fallback`, `validate-output`, `style` and `telemetry` selectors.
- [ ] Emit `evidence/dwt-s2-l2-summary.json` using the DWT-S4 summary contract.
- [ ] Emit `agent-run-manifest.json` using the DWT-S4 telemetry contract.
- [ ] Add positive, negative, blocked, fallback, style and efficiency assertions for DWT-S2-L2A through DWT-S2-L2F.
- [ ] Update README and TC1 testcase documentation with the L2 boundary.
- [ ] Run DWT-S2 L2, DWT-S4 reporting, L0, OpenSpec and child-readiness verification before closeout.
