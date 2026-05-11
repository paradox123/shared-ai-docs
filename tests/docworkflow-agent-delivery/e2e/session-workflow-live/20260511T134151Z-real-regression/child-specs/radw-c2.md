# RADW-C2 Child Spec

## Goal

Append the second workflow value, `2`, to `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt` from a launcher-created child Codex session.

## Review Control Surface

- Spec variant: child delivery regression spec.
- Goldstandard status: implementation-ready direct regression ledger.
- Goal: prove `RADW-PR5`.
- In scope: verify the previous output is exactly `1\n`; update the count file to exactly `1\n2\n`; write child delivery evidence; write child closeout JSON.
- Out of scope: writing values `3` through `5`; editing parent input, orchestration pack, handoffs, launcher code, skills, unrelated docs, or unrelated specs.
- Key harness cases: count file is exactly `1\n` before delivery; count file is exactly `1\n2\n` after delivery.
- Verification commands: `node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt','utf8') !== '1\n2\n') process.exit(1);"`; JSON assertions for child evidence and closeout.
- Open decisions: no open decisions for this child.
- Readiness status: IMPLEMENTATION READY.

## Parent Coverage

- Covers `RADW-PR5`: Child 2 writes `2` as the second line of `target/output/count.txt`.

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| RADW-PR5 | Append only `2` as the second line. | preserves | Deliver in RADW-C2 only. |
| RADW-PR4 | Prior child owns first line. | preserves | Require existing `1\n` prefix. |
| RADW-PR6 through RADW-PR8 | Later children write later values. | defers_to_child | Do not write later child values. |
| RADW-PR11 | Parent closeout consumes this child evidence. | preserves | Write child closeout JSON. |

## In Scope

- Confirm `target/output/count.txt` exists and equals exactly `1\n`.
- If the prefix differs, stop as `NOT READY` and write `delivery-evidence/radw-c2/not-ready.md`.
- Write exactly `1\n2\n` to `count.txt`.
- Write `delivery-evidence/radw-c2/delivery.json`.
- Write `closeout/children/radw-c2.json`.

## Out of Scope

- Launching other children.
- Parent closeout summary.
- Editing shared control files.

## Decision Freeze Pack

- Assigned value: `2`.
- Required previous output before write: `1\n`.
- Required child-local output after write: `1\n2\n`.
- Ledger mode: direct regression ledger, no OpenSpec archive.
- Allowed write-set is exactly the child handoff write-set.

## Acceptance Criteria

- `count.txt` contains exactly `1\n2\n`.
- `delivery-evidence/radw-c2/delivery.json` contains `final_status: ran-target`.
- `closeout/children/radw-c2.json` contains `final_status: ran-target` and `closeout_status: closed`.

## Verification Commands

```sh
node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt','utf8') !== '1\n2\n') process.exit(1);"
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c2.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"
```

## Dependencies and Write-Set

- Dependencies: RADW-C1 closeout exists and count file equals exactly `1\n`.
- Allowed write-set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c2/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c2.json`.

## Closeout Sync Targets

- `delivery-evidence/radw-c2/delivery.json`
- `closeout/children/radw-c2.json`
- Parent `closeout/summary.json` after all children complete.
