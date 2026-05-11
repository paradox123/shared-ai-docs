# RADW Parent Delivery Orchestration Pack

**Spec Orchestration Result**

Parent: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/input/test-parent.md`
Child set: `RADW-C1`, `RADW-C2`, `RADW-C3`, `RADW-C4`, `RADW-C5`
Mode: Generate Child Delivery Packs for direct regression ledger execution through launcher-created Codex sessions.

## Review Control Surface

- Spec variant: Real Agent Delivery Workflow Regression Parent.
- Goldstandard status: direct regression ledger, no OpenSpec archive expected.
- Goal: prove parent/child Agent Delivery Workflow across five launcher-started Codex child sessions.
- In scope: orchestration pack, five child specs, five child handoffs, child launcher evidence, child delivery evidence, final `target/output/count.txt`, parent closeout summary.
- Out of scope: mock runner shortcuts, prior accepted MD-E2E output reuse, parent-session child delivery, queue-only or manual success claims, unrelated repository edits.
- Key harness cases: five fresh child launches; each child writes only its assigned line; final count file is exactly `1\n2\n3\n4\n5\n`.
- Verification commands: `dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/orchestration-pack.md --child RADW-C1 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/handoffs/radw-c1-handoff.md` and repeat for `RADW-C2` through `RADW-C5`; final JSON/count assertions; `git diff --check`.
- Open decisions: no open decisions for this regression slice.
- Readiness status: orchestration complete when all five child specs, handoffs, launches, child closeouts, and parent closeout evidence exist.

## Coverage

- done: `RADW-PR1`, `RADW-PR2`, and `RADW-PR3` are covered by this pack, the exact Child Index, five child specs, and five child handoffs.
- pending: `RADW-PR4` through `RADW-PR11` are delegated to serial launcher-created child sessions plus parent closeout.
- missing: no parent requirement is missing from the child set.
- blocked: no orchestration blocker remains before child launch validation.

## Parent Requirements

| Requirement | Summary | Owning Child | Required Evidence | Coverage Status |
|---|---|---|---|---|
| RADW-PR1 | Launched parent creates this orchestration pack from parent input. | RADW-PARENT | `orchestration-pack.md`. | done |
| RADW-PR2 | Launched parent creates exactly five child specs. | RADW-PARENT | `child-specs/radw-c1.md` through `child-specs/radw-c5.md`. | done |
| RADW-PR3 | Launched parent creates exactly five child handoffs. | RADW-PARENT | `handoffs/radw-c1-handoff.md` through `handoffs/radw-c5-handoff.md`. | done |
| RADW-PR4 | Child 1 writes `1` as the first line. | RADW-C1 | RADW-C1 launcher evidence, delivery evidence, child closeout JSON. | pending |
| RADW-PR5 | Child 2 writes `2` as the second line. | RADW-C2 | RADW-C2 launcher evidence, delivery evidence, child closeout JSON. | pending |
| RADW-PR6 | Child 3 writes `3` as the third line. | RADW-C3 | RADW-C3 launcher evidence, delivery evidence, child closeout JSON. | pending |
| RADW-PR7 | Child 4 writes `4` as the fourth line. | RADW-C4 | RADW-C4 launcher evidence, delivery evidence, child closeout JSON. | pending |
| RADW-PR8 | Child 5 writes `5` as the fifth line. | RADW-C5 | RADW-C5 launcher evidence, delivery evidence, child closeout JSON. | pending |
| RADW-PR9 | Each child runs in its own launcher-created Codex session. | RADW-PARENT | Child launcher evidence under `launches/children/`. | pending |
| RADW-PR10 | Each child passes readiness before delivery. | RADW-PARENT | Validator output before each launch. | pending |
| RADW-PR11 | Parent closeout verifies evidence, statuses, and final output. | RADW-PARENT | `closeout/summary.json` with `overall_status: pass`. | pending |

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RADW-C1 | child-specs/radw-c1.md | RADW-PR4 | IMPLEMENTATION READY | handoffs/radw-c1-handoff.md | direct regression ledger in delivery-evidence/radw-c1/ and closeout/children/radw-c1.json | RADW-PARENT orchestration pack exists and readiness validator passes | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c1/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c1.json | assert count.txt becomes exactly 1 newline; assert delivery-evidence/radw-c1/delivery.json exists; assert closeout/children/radw-c1.json has final_status ran-target and closeout_status closed | delivery-evidence/radw-c1/delivery.json and closeout/children/radw-c1.json | Parent closeout consumes evidence; re-entry file is delivery-evidence/radw-c1/not-ready.md | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex |
| RADW-C2 | child-specs/radw-c2.md | RADW-PR5 | IMPLEMENTATION READY | handoffs/radw-c2-handoff.md | direct regression ledger in delivery-evidence/radw-c2/ and closeout/children/radw-c2.json | RADW-C1 closed and count.txt equals 1 newline | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c2/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c2.json | assert count.txt becomes exactly 1 newline 2 newline; assert delivery-evidence/radw-c2/delivery.json exists; assert closeout/children/radw-c2.json has final_status ran-target and closeout_status closed | delivery-evidence/radw-c2/delivery.json and closeout/children/radw-c2.json | Parent closeout consumes evidence; re-entry file is delivery-evidence/radw-c2/not-ready.md | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex after RADW-C1 evidence |
| RADW-C3 | child-specs/radw-c3.md | RADW-PR6 | IMPLEMENTATION READY | handoffs/radw-c3-handoff.md | direct regression ledger in delivery-evidence/radw-c3/ and closeout/children/radw-c3.json | RADW-C2 closed and count.txt equals 1 newline 2 newline | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c3/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c3.json | assert count.txt becomes exactly 1 newline 2 newline 3 newline; assert delivery-evidence/radw-c3/delivery.json exists; assert closeout/children/radw-c3.json has final_status ran-target and closeout_status closed | delivery-evidence/radw-c3/delivery.json and closeout/children/radw-c3.json | Parent closeout consumes evidence; re-entry file is delivery-evidence/radw-c3/not-ready.md | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex after RADW-C2 evidence |
| RADW-C4 | child-specs/radw-c4.md | RADW-PR7 | IMPLEMENTATION READY | handoffs/radw-c4-handoff.md | direct regression ledger in delivery-evidence/radw-c4/ and closeout/children/radw-c4.json | RADW-C3 closed and count.txt equals 1 newline 2 newline 3 newline | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c4/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c4.json | assert count.txt becomes exactly 1 newline 2 newline 3 newline 4 newline; assert delivery-evidence/radw-c4/delivery.json exists; assert closeout/children/radw-c4.json has final_status ran-target and closeout_status closed | delivery-evidence/radw-c4/delivery.json and closeout/children/radw-c4.json | Parent closeout consumes evidence; re-entry file is delivery-evidence/radw-c4/not-ready.md | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex after RADW-C3 evidence |
| RADW-C5 | child-specs/radw-c5.md | RADW-PR8 | IMPLEMENTATION READY | handoffs/radw-c5-handoff.md | direct regression ledger in delivery-evidence/radw-c5/ and closeout/children/radw-c5.json | RADW-C4 closed and count.txt equals 1 newline 2 newline 3 newline 4 newline | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c5/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c5.json | assert count.txt becomes exactly 1 newline 2 newline 3 newline 4 newline 5 newline; assert delivery-evidence/radw-c5/delivery.json exists; assert closeout/children/radw-c5.json has final_status ran-target and closeout_status closed | delivery-evidence/radw-c5/delivery.json and closeout/children/radw-c5.json | Parent closeout consumes evidence; re-entry file is delivery-evidence/radw-c5/not-ready.md | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex after RADW-C4 evidence |

## Parent Scope Conformance

| Child | Parent Requirement | Conformance | Action |
|---|---|---|---|
| RADW-C1 | RADW-PR4 | preserves | Launch after readiness validation; require child evidence before launching RADW-C2. |
| RADW-C2 | RADW-PR5 | preserves | Launch only after RADW-C1 evidence and count prefix exist. |
| RADW-C3 | RADW-PR6 | preserves | Launch only after RADW-C2 evidence and count prefix exist. |
| RADW-C4 | RADW-PR7 | preserves | Launch only after RADW-C3 evidence and count prefix exist. |
| RADW-C5 | RADW-PR8 | preserves | Launch only after RADW-C4 evidence and count prefix exist. |
| RADW-PARENT | RADW-PR9 through RADW-PR11 | preserves | Parent validates child launch evidence, child closeouts, final output, and writes summary only after all checks pass. |

## Child Readiness

| Child | Status | Main Gap | Required Hardening |
|---|---|---|---|
| RADW-C1 | ready | no gap | Child spec and handoff define exact write contract. |
| RADW-C2 | ready | no gap | Child spec and handoff define exact append contract. |
| RADW-C3 | ready | no gap | Child spec and handoff define exact append contract. |
| RADW-C4 | ready | no gap | Child spec and handoff define exact append contract. |
| RADW-C5 | ready | no gap | Child spec and handoff define exact append contract. |

## Hardening Queue

| Child | Current Status | Required Hardening | Sources To Read | Blockers | Next Handoff Target |
|---|---|---|---|---|---|
| RADW-C1 | IMPLEMENTATION READY | completed for this regression | parent input; this pack; child spec; child handoff | launch waits for readiness command pass | handoffs/radw-c1-handoff.md |
| RADW-C2 | IMPLEMENTATION READY | completed for this regression | parent input; this pack; child spec; child handoff | waits for RADW-C1 closeout | handoffs/radw-c2-handoff.md |
| RADW-C3 | IMPLEMENTATION READY | completed for this regression | parent input; this pack; child spec; child handoff | waits for RADW-C2 closeout | handoffs/radw-c3-handoff.md |
| RADW-C4 | IMPLEMENTATION READY | completed for this regression | parent input; this pack; child spec; child handoff | waits for RADW-C3 closeout | handoffs/radw-c4-handoff.md |
| RADW-C5 | IMPLEMENTATION READY | completed for this regression | parent input; this pack; child spec; child handoff | waits for RADW-C4 closeout | handoffs/radw-c5-handoff.md |

## Parallel Work Control Surface

| Lane | Child/Work Block | Mode | Safe? | Owner/Agent | Allowed Write-Sets | Shared Files / Read-only Files | Dependencies | Verification Commands | Integration Owner | Merge/Sync Order |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | RADW-C1 | implementation | yes for first serial step | launcher-created Codex child session | count.txt; delivery-evidence/radw-c1/**; closeout/children/radw-c1.json | parent input; orchestration pack; child spec; handoff | orchestration complete | child handoff validation and child output assertions | RADW-PARENT | first |
| 2 | RADW-C2 | implementation | serial only | launcher-created Codex child session | count.txt; delivery-evidence/radw-c2/**; closeout/children/radw-c2.json | parent input; orchestration pack; child spec; handoff | RADW-C1 closed | child handoff validation and child output assertions | RADW-PARENT | second |
| 3 | RADW-C3 | implementation | serial only | launcher-created Codex child session | count.txt; delivery-evidence/radw-c3/**; closeout/children/radw-c3.json | parent input; orchestration pack; child spec; handoff | RADW-C2 closed | child handoff validation and child output assertions | RADW-PARENT | third |
| 4 | RADW-C4 | implementation | serial only | launcher-created Codex child session | count.txt; delivery-evidence/radw-c4/**; closeout/children/radw-c4.json | parent input; orchestration pack; child spec; handoff | RADW-C3 closed | child handoff validation and child output assertions | RADW-PARENT | fourth |
| 5 | RADW-C5 | implementation | serial only | launcher-created Codex child session | count.txt; delivery-evidence/radw-c5/**; closeout/children/radw-c5.json | parent input; orchestration pack; child spec; handoff | RADW-C4 closed | child handoff validation and child output assertions | RADW-PARENT | fifth |

## Recommended Execution Order

1. Validate `RADW-C1` with `ValidateChildReadiness.cs`.
2. Launch `RADW-C1` through `AgentDeliverySessionLauncher.cs --mode launch --agent codex`.
3. Verify RADW-C1 launcher status, child closeout JSON, and count prefix.
4. Repeat the same validate-launch-verify cycle for `RADW-C2`, `RADW-C3`, `RADW-C4`, and `RADW-C5`.
5. Write `closeout/summary.json` only after every launcher evidence status is `launched`, every child closeout is closed, and count output is exact.

## Closeout Sync Checklist

- Parent launcher evidence exists under `launches/parent/`.
- Exactly five child specs exist under `child-specs/`.
- Exactly five child handoffs exist under `handoffs/`.
- Every child launch directory exists under `launches/children/`.
- Every child launch evidence has status `launched`.
- Every child has `delivery-evidence/radw-cN/delivery.json`.
- Every child has `closeout/children/radw-cN.json` with `final_status: ran-target` and `closeout_status: closed`.
- `target/output/count.txt` equals `1\n2\n3\n4\n5\n` exactly.
- `closeout/summary.json` records `overall_status: pass`.
- `git diff --check` passes.

## Direct Ledger Recommendation

This regression uses the direct ledger named by the parent handoff. No OpenSpec archive is expected. The operational Child Index in this pack is the Control Index / Queue for all five child launches.

## Mini-Retro

- Decision: split parent requirements into five serial child specs because all children share `target/output/count.txt`.
- Orchestration output: exact Child Index, five implementation-ready child specs, five persisted child handoffs.
- Remaining work: run readiness validation, launch all five child sessions, verify child evidence, and write parent closeout.
- Evidence gap before launches: child launcher evidence, child delivery evidence, final count output, and parent closeout summary.
