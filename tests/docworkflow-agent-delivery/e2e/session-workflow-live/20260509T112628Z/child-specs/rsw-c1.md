# RSW-C1 Child Spec

## Goal

Write the first workflow value, `1`, to `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt` from a launcher-created child Codex session.

## Review Control Surface

- Spec variant: child delivery smoke spec.
- Goldstandard status: implementation-ready direct smoke ledger.
- Goal: prove `RSW-PR2`.
- In scope: create or initialize the count file with exactly `1\n`; write child delivery evidence; write child closeout JSON.
- Out of scope: writing values `2` through `5`; editing the parent input, orchestration pack, handoff, launcher code, skills, unrelated docs or specs.
- Key harness cases: count file is absent or empty before delivery; count file is exactly `1\n` after delivery.
- Verification commands: `test "$(cat tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt)" = "1"`; JSON assertions for child evidence and closeout.
- Open decisions: none.
- Readiness status: IMPLEMENTATION READY.

## Parent Coverage

- Covers `RSW-PR2`: Child 1 writes `1` to `target/output/count.txt`.

## Parent Scope Conformance

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| RSW-PR2 | Write only `1` as the first line. | preserves | Deliver in RSW-C1 only. |
| RSW-PR3 through RSW-PR6 | Later children write later values. | defers_to_child | Do not write other child values. |
| RSW-PR7 | Parent closeout consumes this child evidence. | preserves | Write child closeout JSON. |

## In Scope

- Ensure `target/output/` exists.
- If `count.txt` exists with non-empty content, stop as `NOT READY` and write `delivery-evidence/rsw-c1/not-ready.md`.
- Write exactly `1\n` to `count.txt`.
- Write `delivery-evidence/rsw-c1/delivery.json`.
- Write `closeout/children/rsw-c1.json`.

## Out of Scope

- Launching other children.
- Parent closeout summary.
- Editing shared control files.

## Decision Freeze Pack

- Assigned value: `1`.
- Expected final child-local output after this child: `1\n`.
- Ledger mode: direct smoke ledger, no OpenSpec archive.
- Allowed write-set is exactly the child handoff write-set.

## Acceptance Criteria

- `count.txt` contains exactly `1\n`.
- `delivery-evidence/rsw-c1/delivery.json` contains `final_status: ran-target`.
- `closeout/children/rsw-c1.json` contains `final_status: ran-target` and `closeout_status: closed`.

## Verification Commands

```sh
node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt','utf8') !== '1\n') process.exit(1);"
node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c1.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"
```

## Dependencies and Write-Set

- Dependencies: parent orchestration pack exists and readiness validation passed.
- Allowed write-set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/delivery-evidence/rsw-c1/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c1.json`.

## Closeout Sync Targets

- `delivery-evidence/rsw-c1/delivery.json`
- `closeout/children/rsw-c1.json`
- Parent `closeout/summary.json` after all children complete.
