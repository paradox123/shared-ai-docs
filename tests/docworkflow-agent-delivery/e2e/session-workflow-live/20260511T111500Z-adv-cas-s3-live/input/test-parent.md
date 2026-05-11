# Real Session Workflow Test Parent

Mock Sizing Directive: force_parent_child

## Goal

Prove the Agent Delivery Workflow across real launcher-started Codex sessions. The control session may only prepare this parent and the initial launch handoff. The launched session must create the orchestration pack, child specs, child handoffs, harden children, deliver each child through the declared workflow gates, close out the parent, and produce the final output.

## Requirements

| Requirement | Description | Expected Child |
|---|---|---|
| `RSW-PR1` | The workflow must choose Parent/Child delivery from this parent input. | Orchestrator |
| `RSW-PR2` | Child 1 writes `1` to `target/output/count.txt`. | `RSW-C1` |
| `RSW-PR3` | Child 2 writes `2` to `target/output/count.txt`. | `RSW-C2` |
| `RSW-PR4` | Child 3 writes `3` to `target/output/count.txt`. | `RSW-C3` |
| `RSW-PR5` | Child 4 writes `4` to `target/output/count.txt`. | `RSW-C4` |
| `RSW-PR6` | Child 5 writes `5` to `target/output/count.txt`. | `RSW-C5` |
| `RSW-PR7` | Closeout synchronizes the parent control layer, child index, handoffs, child evidence and final output status. | Closeout |

## Expected Final Output

```text
1
2
3
4
5
```

## Test Rules

- The control session must not create orchestration, child specs, child handoffs, delivery evidence, closeout evidence or `target/output/count.txt`.
- The launched parent session must use `spec-orchestrator` first, then create child handoffs and use `AgentDeliverySessionLauncher.cs --mode launch` for child work instead of doing all child work directly in the parent session.
- Child work must cross launcher-created session boundaries. At minimum, each child `RSW-C1` through `RSW-C5` must have launch evidence for a dedicated child session.
- No mock-runner shortcut may be used.
- No existing accepted MD-E2E child specs may be reused as the delivery output.
- If the launcher cannot create a fresh session, the test is `NOT READY`.
- If any child is delivered before its handoff and readiness gate pass, the test is `NOT READY`.
- If all child hardening and delivery happen inside the parent launched session without child launch evidence, the test is `NOT READY`.
- If any child writes another child's value, the test is `NOT READY`.
