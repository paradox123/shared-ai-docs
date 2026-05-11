# Real Agent Delivery Workflow Regression Parent

Mock Sizing Directive: force_parent_child

## Goal

Run a real Agent Delivery Workflow regression across launcher-started Codex sessions. This control session may only prepare this parent and the initial parent handoff. The launched parent session owns orchestration, child specs, child handoffs, child launcher execution, evidence, closeout, and final output validation.

## Requirements

| Requirement | Description | Expected Owner |
|---|---|---|
| RADW-PR1 | The launched parent session creates an orchestration pack from this parent input. | RADW-PARENT |
| RADW-PR2 | The launched parent session creates exactly five child specs. | RADW-PARENT |
| RADW-PR3 | The launched parent session creates exactly five child handoffs. | RADW-PARENT |
| RADW-PR4 | Child 1 writes exactly `1` as the first line of `target/output/count.txt`. | RADW-C1 |
| RADW-PR5 | Child 2 writes exactly `2` as the second line of `target/output/count.txt`. | RADW-C2 |
| RADW-PR6 | Child 3 writes exactly `3` as the third line of `target/output/count.txt`. | RADW-C3 |
| RADW-PR7 | Child 4 writes exactly `4` as the fourth line of `target/output/count.txt`. | RADW-C4 |
| RADW-PR8 | Child 5 writes exactly `5` as the fifth line of `target/output/count.txt`. | RADW-C5 |
| RADW-PR9 | Each child runs in its own `AgentDeliverySessionLauncher.cs --mode launch --agent codex` session. | RADW-PARENT |
| RADW-PR10 | Each child passes its readiness/handoff gate before delivery. | RADW-PARENT |
| RADW-PR11 | Parent closeout verifies launcher evidence, child statuses, closeout statuses, and final output. | RADW-PARENT |

## Expected Final Output

```text
1
2
3
4
5
```

## Mandatory Evidence

- Parent launcher evidence exists under `launches/parent/`.
- Child launcher evidence exists for `RADW-C1` through `RADW-C5` under `launches/children/`.
- Every child closeout JSON reports `final_status: ran-target`.
- Every child closeout JSON reports `closeout_status: closed`.
- `closeout/summary.json` reports `overall_status: pass`.
- `target/output/count.txt` exactly equals the expected final output, including trailing newline.

## Hard Rules

- Do not use `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`.
- Do not simulate all work in one session.
- Do not let the control session write orchestration, child specs, child handoffs, child evidence, closeout, or `target/output/count.txt`.
- Do not reuse an old accepted run directory or old child specs as delivery output.
- If any launcher or readiness gate fails, stop the workflow and write a NOT READY closeout summary with the failure step, existing evidence, missing evidence, and current `count.txt` contents.
