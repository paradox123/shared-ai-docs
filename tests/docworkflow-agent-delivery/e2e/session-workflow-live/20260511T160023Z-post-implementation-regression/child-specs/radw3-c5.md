# RADW3-C5 Child Spec

## Goal

Append the fifth workflow value, `5`, to `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T160023Z-post-implementation-regression/target/output/count.txt` from a launcher-created child Codex session.

## Review Control Surface

- Spec variant: child delivery regression spec.
- Goldstandard status: implementation-ready direct regression ledger.
- Goal: prove `RADW3-PR8`.
- In scope: verify previous output is exactly `1\n2\n3\n4\n`; update count file to exactly `1\n2\n3\n4\n5\n`; write child delivery evidence; write child closeout JSON.
- Out of scope: editing parent input, orchestration pack, handoffs, launcher code, skills, unrelated docs, or unrelated specs.
- Key harness cases: count file is exactly `1\n2\n3\n4\n` before delivery; count file is exactly `1\n2\n3\n4\n5\n` after delivery.
- Verification commands: assert `count.txt` equals `1\n2\n3\n4\n5\n`; assert child evidence and closeout JSON statuses.
- Open decisions: no open decisions for this child.
- Readiness status: IMPLEMENTATION READY.

## Parent Coverage

- Covers `RADW3-PR8`: Child 5 writes `5` as the fifth line of `target/output/count.txt`.

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| RADW3-PR8 | Append only `5` as the fifth line. | preserves | Deliver in RADW3-C5 only. |
| RADW3-PR4 through RADW3-PR7 | Prior children own earlier lines. | preserves | Require existing `1\n2\n3\n4\n` prefix. |
| RADW3-PR11 | Parent closeout consumes this child evidence. | preserves | Write child closeout JSON. |

## In Scope

- Confirm `target/output/count.txt` exists and equals exactly `1\n2\n3\n4\n`.
- If the prefix differs, stop as `NOT READY` and write `delivery-evidence/radw3-c5/not-ready.md`.
- Write exactly `1\n2\n3\n4\n5\n` to `count.txt`.
- Write `delivery-evidence/radw3-c5/delivery.json`.
- Write `closeout/children/radw3-c5.json`.

## Out of Scope

- Launching other children.
- Parent closeout summary.
- Editing shared control files.

## Decision Freeze Pack

- Assigned value: `5`.
- Required previous output before write: `1\n2\n3\n4\n`.
- Required child-local output after write: `1\n2\n3\n4\n5\n`.
- Ledger mode: direct regression ledger, no OpenSpec archive.
- Allowed write-set is exactly the child handoff write-set.

## Acceptance Criteria

- `count.txt` contains exactly `1\n2\n3\n4\n5\n`.
- `delivery-evidence/radw3-c5/delivery.json` contains `final_status: ran-target`.
- `closeout/children/radw3-c5.json` contains `final_status: ran-target` and `closeout_status: closed`.

## Verification Commands

```sh
node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T160023Z-post-implementation-regression/target/output/count.txt','utf8') !== '1\n2\n3\n4\n5\n') process.exit(1);"
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T160023Z-post-implementation-regression/closeout/children/radw3-c5.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"
```

## Dependencies and Write-Set

- Dependencies: RADW3-C4 closeout exists and count file equals exactly `1\n2\n3\n4\n`.
- Allowed write-set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T160023Z-post-implementation-regression/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T160023Z-post-implementation-regression/delivery-evidence/radw3-c5/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T160023Z-post-implementation-regression/closeout/children/radw3-c5.json`.

## Closeout Sync Targets

- `delivery-evidence/radw3-c5/delivery.json`
- `closeout/children/radw3-c5.json`
- Parent `closeout/summary.json` after all children complete.
