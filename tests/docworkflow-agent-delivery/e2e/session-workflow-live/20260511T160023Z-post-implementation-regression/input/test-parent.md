# Agent Delivery Real Regression Parent

Run directory: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T160023Z-post-implementation-regression`

This is a real post-implementation regression test for the Agent Delivery Workflow.

Requirements:

1. Create `orchestration-pack.md`.
2. Create exactly five child specs: `RADW3-C1` through `RADW3-C5`.
3. Create exactly five child handoffs: `handoffs/radw3-c1-handoff.md` through `handoffs/radw3-c5-handoff.md`.
4. Each child must pass its readiness/handoff gate before launch.
5. Launch each child in its own launcher-created Codex session using:
   `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --handoff <child-handoff> --target-id <RADW3-CN> --mode launch --agent codex --out tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T160023Z-post-implementation-regression/launches/children`
6. Children run serially and write only their own value to `target/output/count.txt`:
   - `RADW3-C1` writes exactly `1\n`
   - `RADW3-C2` changes it to exactly `1\n2\n`
   - `RADW3-C3` changes it to exactly `1\n2\n3\n`
   - `RADW3-C4` changes it to exactly `1\n2\n3\n4\n`
   - `RADW3-C5` changes it to exactly `1\n2\n3\n4\n5\n`
7. The parent must not write child output values itself.
8. Do not use `run-mock-e2e-checks.sh`.
9. Final closeout passes only when parent launcher evidence exists, five child launcher evidence records exist, each child has `final_status: ran-target` and `closeout_status: closed`, and `closeout/summary.json` has `overall_status: pass`.

On failure or hang:

- Stop the test.
- Stop only processes started by this test.
- Persist NOT READY evidence with failed child/step, existing evidence, missing evidence, and current `count.txt` content.
