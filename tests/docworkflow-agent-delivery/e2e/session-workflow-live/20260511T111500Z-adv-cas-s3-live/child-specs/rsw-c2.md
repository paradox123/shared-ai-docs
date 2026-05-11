# RSW-C2 Child Spec

## Goal

Append the second workflow value, `2`, to `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt` from a launcher-created child Codex session.

## Review Control Surface

- Spec variant: child delivery smoke spec.
- Goldstandard status: implementation-ready direct smoke ledger.
- Goal: prove `RSW-PR3`.
- In scope: validate the RSW-C1 prefix, append exactly `2\n`, write child delivery evidence, and write child closeout JSON.
- Out of scope: writing values `1`, `3`, `4`, or `5`; repairing predecessor children; editing the parent input, orchestration pack, handoff, launcher code, skills, unrelated docs or specs.
- Key harness cases: count file is exactly `1\n` before delivery; count file is exactly `1\n2\n` after delivery.
- Verification commands: `node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt','utf8') !== '1\n2\n') process.exit(1);"`; JSON assertions for child evidence and closeout.
- Open decisions: none.
- Readiness status: IMPLEMENTATION READY.

## Parent Coverage

- Covers `RSW-PR3`: Child 2 writes `2` to `target/output/count.txt`.

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| RSW-PR3 | Append only `2` after RSW-C1. | preserves | Deliver in RSW-C2 only. |
| RSW-PR2 | RSW-C1 owns the prefix. | defers_to_child | Validate but do not repair RSW-C1. |
| RSW-PR4 through RSW-PR6 | Later children write later values. | defers_to_child | Do not write other child values. |
| RSW-PR7 | Parent closeout consumes this child evidence. | preserves | Write child closeout JSON. |

## In Scope

- Validate `closeout/children/rsw-c1.json` has `final_status: ran-target` and `closeout_status: closed`.
- Validate `count.txt` is exactly `1\n` before delivery.
- Append exactly `2\n` to `count.txt`.
- Write `delivery-evidence/rsw-c2/delivery.json`.
- Write `closeout/children/rsw-c2.json`.

## Out of Scope

- Launching other children.
- Parent closeout summary.
- Editing shared control files.

## Decision Freeze Pack

- Assigned value: `2`.
- Expected final child-local output after this child: `1\n2\n`.
- Ledger mode: direct smoke ledger, no OpenSpec archive.
- Allowed write-set is exactly the child handoff write-set.

## Acceptance Criteria

- `count.txt` contains exactly `1\n2\n`.
- `delivery-evidence/rsw-c2/delivery.json` contains `final_status: ran-target`.
- `closeout/children/rsw-c2.json` contains `final_status: ran-target` and `closeout_status: closed`.

## Verification Commands

```sh
node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt','utf8') !== '1\n2\n') process.exit(1);"
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c2.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"
```

## Dependencies and Write-Set

- Dependencies: RSW-C1 closeout exists and count prefix is exact.
- Allowed write-set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/delivery-evidence/rsw-c2/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c2.json`.

## Closeout Sync Targets

- `delivery-evidence/rsw-c2/delivery.json`
- `closeout/children/rsw-c2.json`
- Parent `closeout/summary.json` after all children complete.
