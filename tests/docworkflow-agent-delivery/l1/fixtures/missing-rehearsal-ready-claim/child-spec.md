# RISK-S1 Child Spec

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| `RISK-PR1` | Runtime gate. | preserves | Run Docker verification. |

## Verification Commands

```sh
docker build .
docker run risk-s1
```

This fixture intentionally omits command-contract rehearsal evidence for the
high-risk Docker commands above.
