# Visible Agent Delivery Workflow Regression Parent

Mock Sizing Directive: force_parent_child

## Goal

Run a real visible Agent Delivery Workflow regression across Codex-App sessions created through the Agent Delivery visible session controller and `AgentDeliverySessionLauncher.cs --adapter codex-app-server`.

## Requirements

| Requirement | Description | Expected Owner |
|---|---|---|
| VADW-PR1 | The visible parent session creates an orchestration pack from this parent input. | VADW-PARENT |
| VADW-PR2 | The visible parent session creates exactly five child specs. | VADW-PARENT |
| VADW-PR3 | The visible parent session creates exactly five child handoffs. | VADW-PARENT |
| VADW-PR4 | The visible parent session publishes exactly five controller child launch requests. | VADW-PARENT |
| VADW-PR5 | Child 1 writes exactly `1` as the first line of `target/output/count.txt`. | VADW-C1 |
| VADW-PR6 | Child 2 writes exactly `2` as the second line of `target/output/count.txt`. | VADW-C2 |
| VADW-PR7 | Child 3 writes exactly `3` as the third line of `target/output/count.txt`. | VADW-C3 |
| VADW-PR8 | Child 4 writes exactly `4` as the fourth line of `target/output/count.txt`. | VADW-C4 |
| VADW-PR9 | Child 5 writes exactly `5` as the fifth line of `target/output/count.txt`. | VADW-C5 |
| VADW-PR10 | Each child runs in its own visible launcher-created Codex-App session. | Controller |
| VADW-PR11 | Each child passes its readiness/handoff gate before delivery. | Controller and Child |
| VADW-PR12 | Final closeout verifies visible launcher evidence, child statuses, closeout statuses, and final output. | VADW-PARENT |

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
- Parent evidence reports `session_visibility.class: visible_codex_app_session`.
- Child launcher evidence exists for `VADW-C1` through `VADW-C5` under `launches/children/`.
- Every child evidence reports `session_visibility.class: visible_codex_app_session`.
- Every child closeout JSON reports `final_status: ran-target`.
- Every child closeout JSON reports `closeout_status: closed`.
- `closeout/summary.json` reports `overall_status: pass`.
- `controller/controller-summary.json` reports `status: pass`.
- `target/output/count.txt` exactly equals the expected final output, including trailing newline.

## Hard Rules

- Do not use `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`.
- Do not simulate all work in one session.
- Do not use the default headless `codex-cli` adapter as success evidence.
- Do not let the control session write orchestration, child specs, child handoffs, child evidence, closeout, controller requests, or `target/output/count.txt`.
- Do not reuse an old accepted run directory or old child specs as delivery output.
- If any visible launcher or readiness gate fails, stop the workflow and write a NOT READY closeout summary with the failure step, existing evidence, missing evidence, and current `count.txt` contents.
