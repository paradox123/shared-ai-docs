# RSW Parent Delivery Orchestration Pack

**Spec Orchestration Result**

Parent: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/input/test-parent.md`
Child set: `RSW-C1`, `RSW-C2`, `RSW-C3`, `RSW-C4`, `RSW-C5`
Mode: Generate Child Delivery Packs for direct smoke ledger execution through launcher-created Codex sessions.

## Review Control Surface

- Spec variant: Real Session Workflow Test Parent.
- Goldstandard status: direct smoke ledger, no OpenSpec archive expected.
- Goal: prove parent/child Agent Delivery Workflow across launcher-started Codex sessions.
- In scope: orchestration pack, five child specs, five child handoffs, child launcher evidence, child delivery evidence, final `target/output/count.txt`, parent closeout summary.
- Out of scope: mock runner shortcuts, accepted MD-E2E child spec reuse, unrelated specs or project docs, single-session simulation.
- Key harness cases: five fresh child launches; each child writes only its assigned value; final count file is exactly `1\n2\n3\n4\n5\n`.
- Verification commands: `dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/orchestration-pack.md --child RSW-C1 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/handoffs/rsw-c1-handoff.md` and repeat for `RSW-C2` through `RSW-C5`; final JSON/count assertions; `git diff --check`.
- Open decisions: none.
- Readiness status: orchestration complete when all five child launches produce evidence and closeout summary reports pass.

## Coverage

- done: `RSW-PR1` is covered by this pack and Child Index.
- partial: `RSW-PR2` through `RSW-PR6` are delegated to launcher-created child sessions until child evidence exists.
- pending: `RSW-PR7` parent closeout remains pending until all child launches and child closeout files exist.
- missing: none.
- blocked: none at orchestration time.

## Parent Requirements

| Requirement | Summary | Owning Child | Required Evidence | Coverage Status |
|---|---|---|---|---|
| RSW-PR1 | Choose Parent/Child delivery from parent input. | RSW-PARENT | This orchestration pack and exact Child Index. | done |
| RSW-PR2 | Child 1 writes `1` to `target/output/count.txt`. | RSW-C1 | RSW-C1 launch evidence, delivery evidence, child closeout JSON. | pending |
| RSW-PR3 | Child 2 writes `2` to `target/output/count.txt`. | RSW-C2 | RSW-C2 launch evidence, delivery evidence, child closeout JSON. | pending |
| RSW-PR4 | Child 3 writes `3` to `target/output/count.txt`. | RSW-C3 | RSW-C3 launch evidence, delivery evidence, child closeout JSON. | pending |
| RSW-PR5 | Child 4 writes `4` to `target/output/count.txt`. | RSW-C4 | RSW-C4 launch evidence, delivery evidence, child closeout JSON. | pending |
| RSW-PR6 | Child 5 writes `5` to `target/output/count.txt`. | RSW-C5 | RSW-C5 launch evidence, delivery evidence, child closeout JSON. | pending |
| RSW-PR7 | Closeout synchronizes control layer, index, handoffs, child evidence and final output status. | RSW-PARENT | `closeout/summary.json` with pass status and exact count output. | pending |

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RSW-C1 | child-specs/rsw-c1.md | RSW-PR2 | IMPLEMENTATION READY | handoffs/rsw-c1-handoff.md | direct smoke ledger in delivery-evidence/rsw-c1/ and closeout/children/rsw-c1.json | RSW-PARENT orchestration pack exists | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/delivery-evidence/rsw-c1/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c1.json | assert count.txt becomes exactly 1 newline; assert delivery-evidence/rsw-c1/delivery.json exists; assert closeout/children/rsw-c1.json has final_status ran-target and closeout_status closed | delivery-evidence/rsw-c1/delivery.json and closeout/children/rsw-c1.json | No backlog; parent closeout consumes evidence | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex |
| RSW-C2 | child-specs/rsw-c2.md | RSW-PR3 | IMPLEMENTATION READY | handoffs/rsw-c2-handoff.md | direct smoke ledger in delivery-evidence/rsw-c2/ and closeout/children/rsw-c2.json | RSW-C1 closed and count.txt equals 1 newline | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/delivery-evidence/rsw-c2/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c2.json | assert count.txt becomes exactly 1 newline 2 newline; assert delivery-evidence/rsw-c2/delivery.json exists; assert closeout/children/rsw-c2.json has final_status ran-target and closeout_status closed | delivery-evidence/rsw-c2/delivery.json and closeout/children/rsw-c2.json | No backlog; parent closeout consumes evidence | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex after RSW-C1 evidence |
| RSW-C3 | child-specs/rsw-c3.md | RSW-PR4 | IMPLEMENTATION READY | handoffs/rsw-c3-handoff.md | direct smoke ledger in delivery-evidence/rsw-c3/ and closeout/children/rsw-c3.json | RSW-C2 closed and count.txt equals 1 newline 2 newline | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/delivery-evidence/rsw-c3/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c3.json | assert count.txt becomes exactly 1 newline 2 newline 3 newline; assert delivery-evidence/rsw-c3/delivery.json exists; assert closeout/children/rsw-c3.json has final_status ran-target and closeout_status closed | delivery-evidence/rsw-c3/delivery.json and closeout/children/rsw-c3.json | No backlog; parent closeout consumes evidence | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex after RSW-C2 evidence |
| RSW-C4 | child-specs/rsw-c4.md | RSW-PR5 | IMPLEMENTATION READY | handoffs/rsw-c4-handoff.md | direct smoke ledger in delivery-evidence/rsw-c4/ and closeout/children/rsw-c4.json | RSW-C3 closed and count.txt equals 1 newline 2 newline 3 newline | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/delivery-evidence/rsw-c4/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c4.json | assert count.txt becomes exactly 1 newline 2 newline 3 newline 4 newline; assert delivery-evidence/rsw-c4/delivery.json exists; assert closeout/children/rsw-c4.json has final_status ran-target and closeout_status closed | delivery-evidence/rsw-c4/delivery.json and closeout/children/rsw-c4.json | No backlog; parent closeout consumes evidence | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex after RSW-C3 evidence |
| RSW-C5 | child-specs/rsw-c5.md | RSW-PR6 | IMPLEMENTATION READY | handoffs/rsw-c5-handoff.md | direct smoke ledger in delivery-evidence/rsw-c5/ and closeout/children/rsw-c5.json | RSW-C4 closed and count.txt equals 1 newline 2 newline 3 newline 4 newline | tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/delivery-evidence/rsw-c5/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c5.json | assert count.txt becomes exactly 1 newline 2 newline 3 newline 4 newline 5 newline; assert delivery-evidence/rsw-c5/delivery.json exists; assert closeout/children/rsw-c5.json has final_status ran-target and closeout_status closed | delivery-evidence/rsw-c5/delivery.json and closeout/children/rsw-c5.json | No backlog; parent closeout consumes evidence | spec-change-delivery via AgentDeliverySessionLauncher.cs --mode launch --agent codex after RSW-C4 evidence |

## Parent Scope Conformance

| Child | Parent Requirement | Conformance | Action |
|---|---|---|---|
| RSW-C1 | RSW-PR2 | preserves | Launch after readiness validation; require child evidence before parent closeout. |
| RSW-C2 | RSW-PR3 | preserves | Launch only after RSW-C1 evidence and count prefix exist. |
| RSW-C3 | RSW-PR4 | preserves | Launch only after RSW-C2 evidence and count prefix exist. |
| RSW-C4 | RSW-PR5 | preserves | Launch only after RSW-C3 evidence and count prefix exist. |
| RSW-C5 | RSW-PR6 | preserves | Launch only after RSW-C4 evidence and count prefix exist. |
| RSW-PARENT | RSW-PR7 | preserves | Parent writes final `closeout/summary.json` after all child evidence exists. |

## Child Readiness

| Child | Status | Main Gap | Required Hardening |
|---|---|---|---|
| RSW-C1 | ready | none | Child spec includes implementation-ready smoke contract. |
| RSW-C2 | ready | none | Child spec includes implementation-ready smoke contract. |
| RSW-C3 | ready | none | Child spec includes implementation-ready smoke contract. |
| RSW-C4 | ready | none | Child spec includes implementation-ready smoke contract. |
| RSW-C5 | ready | none | Child spec includes implementation-ready smoke contract. |

## Hardening Queue

| Child | Current Status | Required Hardening | Sources To Read | Blockers | Next Handoff Target |
|---|---|---|---|---|---|
| RSW-C1 | IMPLEMENTATION READY | none | parent input; this pack; child spec; child handoff | none | handoffs/rsw-c1-handoff.md |
| RSW-C2 | IMPLEMENTATION READY | none | parent input; this pack; child spec; child handoff | waits for RSW-C1 closeout | handoffs/rsw-c2-handoff.md |
| RSW-C3 | IMPLEMENTATION READY | none | parent input; this pack; child spec; child handoff | waits for RSW-C2 closeout | handoffs/rsw-c3-handoff.md |
| RSW-C4 | IMPLEMENTATION READY | none | parent input; this pack; child spec; child handoff | waits for RSW-C3 closeout | handoffs/rsw-c4-handoff.md |
| RSW-C5 | IMPLEMENTATION READY | none | parent input; this pack; child spec; child handoff | waits for RSW-C4 closeout | handoffs/rsw-c5-handoff.md |

## Parallelization

| Lane | Child/Work Block | Mode | Safe? | Owner/Agent | Allowed Write-Sets | Shared Files / Read-only Files | Dependencies | Verification Commands | Integration Owner | Merge/Sync Order |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | RSW-C1 | implementation | yes | launcher-created Codex child session | count.txt; delivery-evidence/rsw-c1/**; closeout/children/rsw-c1.json | parent input; orchestration pack; child spec; handoff | orchestration complete | child handoff verification | RSW-PARENT | first |
| 2 | RSW-C2 | implementation | serial only | launcher-created Codex child session | count.txt; delivery-evidence/rsw-c2/**; closeout/children/rsw-c2.json | parent input; orchestration pack; child spec; handoff | RSW-C1 closed | child handoff verification | RSW-PARENT | second |
| 3 | RSW-C3 | implementation | serial only | launcher-created Codex child session | count.txt; delivery-evidence/rsw-c3/**; closeout/children/rsw-c3.json | parent input; orchestration pack; child spec; handoff | RSW-C2 closed | child handoff verification | RSW-PARENT | third |
| 4 | RSW-C4 | implementation | serial only | launcher-created Codex child session | count.txt; delivery-evidence/rsw-c4/**; closeout/children/rsw-c4.json | parent input; orchestration pack; child spec; handoff | RSW-C3 closed | child handoff verification | RSW-PARENT | fourth |
| 5 | RSW-C5 | implementation | serial only | launcher-created Codex child session | count.txt; delivery-evidence/rsw-c5/**; closeout/children/rsw-c5.json | parent input; orchestration pack; child spec; handoff | RSW-C4 closed | child handoff verification | RSW-PARENT | fifth |

## Recommended Next Moves

1. Validate each child row with `ValidateChildReadiness.cs`.
2. Launch `RSW-C1` through `RSW-C5` serially with `AgentDeliverySessionLauncher.cs --mode launch --agent codex --adapter codex-app-server`.
3. After all child launcher evidence and child closeout JSON files exist, write `closeout/summary.json` and assert final output.

## Closeout Sync Checklist

- All five child launch directories exist under `launches/`.
- Every child launch evidence has status `launched`.
- Every child has `delivery-evidence/rsw-cN/delivery.json`.
- Every child has `closeout/children/rsw-cN.json` with `final_status: ran-target` and `closeout_status: closed`.
- `target/output/count.txt` equals the parent expected final output exactly.
- `closeout/summary.json` records `overall_status: pass`.
- `git diff --check` passes.

## Mini-Retro

- What was decided? Use serial child launches because all children share `target/output/count.txt`.
- What changed? The parent input is split into five implementation-ready child smoke specs and handoffs.
- What remains open? Child launches and parent closeout evidence remain pending until launcher execution completes.
- Which evidence is missing? Child launcher evidence, child delivery evidence, final closeout summary.
- Workflow friction: the parent handoff has no pre-existing Control Index path, so this pack becomes the operational control surface.
- Session/context state: continue in this parent session for launcher execution and closeout.
