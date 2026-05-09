# RSW-C5 Child Spec

## Goal

Append the fifth workflow value, `5`, to `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt` from a launcher-created child Codex session.

## Review Control Surface

- Spec variant: child delivery smoke spec.
- Goldstandard status: implementation-ready direct smoke ledger.
- Goal: prove `RSW-PR6`.
- In scope: verify `RSW-C4` evidence; append exactly `5\n`; write child delivery evidence; write child closeout JSON.
- Out of scope: writing values `1`, `2`, `3`, or `4`; parent closeout summary; editing shared control files.
- Key harness cases: count file is exactly `1\n2\n3\n4\n` before delivery; count file is exactly `1\n2\n3\n4\n5\n` after delivery.
- Verification commands: exact count assertion and JSON assertions for child evidence and closeout.
- Open decisions: none.
- Readiness status: IMPLEMENTATION READY.

## Parent Coverage

- Covers `RSW-PR6`: Child 5 writes `5` to `target/output/count.txt`.

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| RSW-PR6 | Append only `5` as the fifth line. | preserves | Deliver in RSW-C5 only. |
| RSW-PR5 | Requires prior `4` output. | preserves | Validate RSW-C4 closeout before writing. |
| RSW-PR7 | Parent closeout checks final output. | preserves | Write child closeout JSON. |

## In Scope

- Validate `closeout/children/rsw-c4.json` has `final_status: ran-target` and `closeout_status: closed`.
- Validate `count.txt` is exactly `1\n2\n3\n4\n` before writing.
- Append exactly `5\n`.
- Write `delivery-evidence/rsw-c5/delivery.json`.
- Write `closeout/children/rsw-c5.json`.

## Out of Scope

- Repairing missing predecessor evidence.
- Parent closeout summary.
- Editing shared control files.

## Decision Freeze Pack

- Assigned value: `5`.
- Expected final child-local output after this child: `1\n2\n3\n4\n5\n`.
- Ledger mode: direct smoke ledger, no OpenSpec archive.
- Allowed write-set is exactly the child handoff write-set.

## Acceptance Criteria

- `count.txt` contains exactly `1\n2\n3\n4\n5\n`.
- `delivery-evidence/rsw-c5/delivery.json` contains `final_status: ran-target`.
- `closeout/children/rsw-c5.json` contains `final_status: ran-target` and `closeout_status: closed`.

## Verification Commands

```sh
node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt','utf8') !== '1\n2\n3\n4\n5\n') process.exit(1);"
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c5.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"
```

## Dependencies and Write-Set

- Dependencies: `RSW-C4` closed and `count.txt` equals `1\n2\n3\n4\n`.
- Allowed write-set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/delivery-evidence/rsw-c5/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c5.json`.

## Closeout Sync Targets

- `delivery-evidence/rsw-c5/delivery.json`
- `closeout/children/rsw-c5.json`
- Parent `closeout/summary.json` after all children complete.
