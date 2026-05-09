# Mock Large Parent Spec

Mock Sizing Directive: force_parent_child

## Goal

Exercise the Agent Delivery parent/child workflow with a tiny synthetic domain. The workflow must split this parent into exactly five child deliveries and keep the parent as the control layer.

## Requirements

| Requirement | Description | Expected Child |
|---|---|---|
| `ML-PR1` | The mock sizing directive forces `parent_child` delivery and blocks direct delivery. | Orchestrator/Parent |
| `ML-PR2` | Child 1 writes the value `1` to `mock-target/output/count.txt`. | `ML-C1` |
| `ML-PR3` | Child 2 writes the value `2` to `mock-target/output/count.txt`. | `ML-C2` |
| `ML-PR4` | Child 3 writes the value `3` to `mock-target/output/count.txt`. | `ML-C3` |
| `ML-PR5` | Child 4 writes the value `4` to `mock-target/output/count.txt`. | `ML-C4` |
| `ML-PR6` | Child 5 writes the value `5` to `mock-target/output/count.txt`. | `ML-C5` |
| `ML-PR7` | Closeout synchronizes parent control output, child index, session evidence and final output status. | Closeout |

## Expected Final Output

```text
1
2
3
4
5
```

## Boundaries

- No external APIs.
- No secrets.
- No Docker or infrastructure dependency.
- No real product repository or real product fixture input.

