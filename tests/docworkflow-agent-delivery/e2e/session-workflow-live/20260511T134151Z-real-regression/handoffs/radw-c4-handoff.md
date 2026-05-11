# Agent Delivery Session Handoff: RADW-C4

- Parent: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/input/test-parent.md`
- Target ID: RADW-C4
- Target Role: child
- Child Spec: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/child-specs/radw-c4.md`
- Child Index / Queue: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/orchestration-pack.md`
- Handoff File: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/handoffs/radw-c4-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Next Mode / Skill: spec-change-delivery
- Current Verdict: IMPLEMENTATION READY
- Scope Summary: Deliver RADW-C4 in a launcher-created child Codex session by changing `target/output/count.txt` from exactly `1\n2\n3\n` to exactly `1\n2\n3\n4\n`, then persist RADW-C4 delivery and closeout evidence.
- Non-Goals: Do not write value 5; do not edit parent input; do not edit orchestration-pack.md; do not edit handoffs; do not use run-mock-e2e-checks.sh; do not edit unrelated specs or project docs.
- Allowed Write-Set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c4/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c4.json`
- Shared / Read-only Files: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/input/test-parent.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/orchestration-pack.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/child-specs/radw-c4.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/handoffs/radw-c4-handoff.md`; `skills-repo/skills/spec-change-delivery/SKILL.md`; `skills-repo/tools/ValidateChildReadiness.cs`
- Verification Commands: `dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/orchestration-pack.md --child RADW-C4 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/handoffs/radw-c4-handoff.md`; `node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt','utf8') !== '1\n2\n3\n4\n') process.exit(1);"`; `node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c4.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"`
- Evidence / OpenSpec: direct regression ledger only; write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c4/delivery.json`; write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c4.json`; no OpenSpec archive expected.
- Open Notes: Fresh child session is required after RADW-C3 evidence exists. If the handoff, Child Index row, target workspace, verdict, allowed write-set, or current count prefix is inconsistent, stop with NOT READY and write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c4/not-ready.md`.

## Required Child Behavior

1. Read this handoff, the Child Index row, and the child spec before writing.
2. Validate that `count.txt` exists and is exactly `1\n2\n3\n` before delivery. If it differs, stop with NOT READY evidence.
3. Write exactly `1\n2\n3\n4\n` to `count.txt`.
4. Write `delivery-evidence/radw-c4/delivery.json` with `target_id`, `final_status: ran-target`, `written_value: "4"`, and `observed_output: "1\n2\n3\n4\n"`.
5. Write `closeout/children/radw-c4.json` with `target_id`, `final_status: ran-target`, `closeout_status: closed`, and `output_status: pass`.
6. Run the verification commands and report the result.
