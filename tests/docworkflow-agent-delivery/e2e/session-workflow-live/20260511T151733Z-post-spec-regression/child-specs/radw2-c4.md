# RADW2-C4 Child Spec

## Goal

Append the fourth workflow value, `4`, to `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/target/output/count.txt` from a launcher-created child Codex session.

## Review Control Surface

- Spec variant: child delivery regression spec.
- Goldstandard status: implementation-ready direct regression ledger.
- Goal: prove `RADW2-PR7`.
- In scope: verify previous output is exactly `1\n2\n3\n`; update count file to exactly `1\n2\n3\n4\n`; write child delivery evidence; write child closeout JSON.
- Out of scope: writing value `5`; editing parent input, orchestration pack, handoffs, launcher code, skills, unrelated docs, or unrelated specs.
- Key harness cases: count file is exactly `1\n2\n3\n` before delivery; count file is exactly `1\n2\n3\n4\n` after delivery.
- Verification commands: assert `count.txt` equals `1\n2\n3\n4\n`; assert child evidence and closeout JSON statuses.
- Open decisions: no open decisions for this child.
- Readiness status: IMPLEMENTATION READY.

## Parent Coverage

- Covers `RADW2-PR7`: Child 4 writes `4` as the fourth line of `target/output/count.txt`.

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| RADW2-PR7 | Append only `4` as the fourth line. | preserves | Deliver in RADW2-C4 only. |
| RADW2-PR4 through RADW2-PR6 | Prior children own first three lines. | preserves | Require existing `1\n2\n3\n` prefix. |
| RADW2-PR8 | Later child writes final value. | defers_to_child | Do not write value `5`. |
| RADW2-PR11 | Parent closeout consumes this child evidence. | preserves | Write child closeout JSON. |

## In Scope

- Confirm `target/output/count.txt` exists and equals exactly `1\n2\n3\n`.
- If the prefix differs, stop as `NOT READY` and write `delivery-evidence/radw2-c4/not-ready.md`.
- Write exactly `1\n2\n3\n4\n` to `count.txt`.
- Write `delivery-evidence/radw2-c4/delivery.json`.
- Write `closeout/children/radw2-c4.json`.

## Out of Scope

- Launching other children.
- Parent closeout summary.
- Editing shared control files.

## Decision Freeze Pack

- Assigned value: `4`.
- Required previous output before write: `1\n2\n3\n`.
- Required child-local output after write: `1\n2\n3\n4\n`.
- Ledger mode: direct regression ledger, no OpenSpec archive.
- Allowed write-set is exactly the child handoff write-set.

## Acceptance Criteria

- `count.txt` contains exactly `1\n2\n3\n4\n`.
- `delivery-evidence/radw2-c4/delivery.json` contains `final_status: ran-target`.
- `closeout/children/radw2-c4.json` contains `final_status: ran-target` and `closeout_status: closed`.

## Verification Commands

```sh
node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/target/output/count.txt','utf8') !== '1\n2\n3\n4\n') process.exit(1);"
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/closeout/children/radw2-c4.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"
```

## Dependencies and Write-Set

- Dependencies: RADW2-C3 closeout exists and count file equals exactly `1\n2\n3\n`.
- Allowed write-set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/delivery-evidence/radw2-c4/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/closeout/children/radw2-c4.json`.

## Closeout Sync Targets

- `delivery-evidence/radw2-c4/delivery.json`
- `closeout/children/radw2-c4.json`
- Parent `closeout/summary.json` after all children complete.
