# RADW-C1 Child Spec

## Goal

Write the first workflow value, `1`, to `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt` from a launcher-created child Codex session.

## Review Control Surface

- Spec variant: child delivery regression spec.
- Goldstandard status: implementation-ready direct regression ledger.
- Goal: prove `RADW-PR4`.
- In scope: create or initialize the count file with exactly `1\n`; write child delivery evidence; write child closeout JSON.
- Out of scope: writing values `2` through `5`; editing parent input, orchestration pack, handoffs, launcher code, skills, unrelated docs, or unrelated specs.
- Key harness cases: count file is absent or empty before delivery; count file is exactly `1\n` after delivery.
- Verification commands: `node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt','utf8') !== '1\n') process.exit(1);"`; JSON assertions for child evidence and closeout.
- Open decisions: no open decisions for this child.
- Readiness status: IMPLEMENTATION READY.

## Parent Coverage

- Covers `RADW-PR4`: Child 1 writes `1` as the first line of `target/output/count.txt`.

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| RADW-PR4 | Write only `1` as the first line. | preserves | Deliver in RADW-C1 only. |
| RADW-PR5 through RADW-PR8 | Later children write later values. | defers_to_child | Do not write other child values. |
| RADW-PR11 | Parent closeout consumes this child evidence. | preserves | Write child closeout JSON. |

## In Scope

- Ensure `target/output/` exists.
- If `count.txt` exists with non-empty content, stop as `NOT READY` and write `delivery-evidence/radw-c1/not-ready.md`.
- Write exactly `1\n` to `count.txt`.
- Write `delivery-evidence/radw-c1/delivery.json`.
- Write `closeout/children/radw-c1.json`.

## Out of Scope

- Launching other children.
- Parent closeout summary.
- Editing shared control files.

## Decision Freeze Pack

- Assigned value: `1`.
- Required previous output before write: absent file or empty file.
- Required child-local output after write: `1\n`.
- Ledger mode: direct regression ledger, no OpenSpec archive.
- Allowed write-set is exactly the child handoff write-set.

## Acceptance Criteria

- `count.txt` contains exactly `1\n`.
- `delivery-evidence/radw-c1/delivery.json` contains `final_status: ran-target`.
- `closeout/children/radw-c1.json` contains `final_status: ran-target` and `closeout_status: closed`.

## Verification Commands

```sh
node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt','utf8') !== '1\n') process.exit(1);"
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c1.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"
```

## Dependencies and Write-Set

- Dependencies: parent orchestration pack exists and readiness validation passed.
- Allowed write-set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c1/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c1.json`.

## Closeout Sync Targets

- `delivery-evidence/radw-c1/delivery.json`
- `closeout/children/radw-c1.json`
- Parent `closeout/summary.json` after all children complete.
