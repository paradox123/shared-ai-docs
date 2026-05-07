# Tasks

- [x] Create the DWT-S0 scope contract and exact command contract.
- [x] Rehearse high-risk runner/config commands enough to prove path, runtime, and config selection.
- [x] Build or document the smallest isolated fixture for a Codex-skill-like run.
- [x] Run the Promptfoo-first probe or capture a reproducible blocker.
- [x] Run deterministic post-run assertions or capture why they are blocked.
- [x] Write the spike evidence artifact.
- [x] Update the ADR with one re-evaluation result.
- [x] Sync the parent Child Index, DWT-S0 handoff, evidence links, and next slice recommendation.

## Evidence

- Result: `ADOPT_WITH_LIMITATIONS`
- Summary: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json`
- Runner output: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/promptfoo-eval.txt`
- Runner JSON: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/promptfoo-eval.json`
- Deterministic assertion: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/assertion-output.txt`
- Blocker notes: `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/blocker-output.txt`

Promptfoo `0.121.9` with bundled Node `v24.14.0` ran the Codex SDK provider against the isolated DWT-S0 fixture and passed Promptfoo plus post-run assertions. Adoption remains limited by explicit Codex auth provisioning, cold-cache npm network sensitivity, and the fact that this spike validated Codex SDK rather than Codex Desktop/app-server.
