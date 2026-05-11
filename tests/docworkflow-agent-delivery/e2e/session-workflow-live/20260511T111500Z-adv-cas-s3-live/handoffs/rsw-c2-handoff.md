# Agent Delivery Session Handoff: RSW-C2

- Parent: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/input/test-parent.md`
- Target ID: RSW-C2
- Target Role: child
- Child Spec: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/child-specs/rsw-c2.md`
- Child Index / Queue: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/orchestration-pack.md`
- Handoff File: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/handoffs/rsw-c2-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Next Mode / Skill: spec-change-delivery
- Current Verdict: IMPLEMENTATION READY
- Scope Summary: Deliver RSW-C2 in a launcher-created child Codex session by appending exactly `2\n` after the RSW-C1 output, then persist RSW-C2 delivery and closeout evidence.
- Non-Goals: Do not write values 1, 3, 4, or 5; do not repair RSW-C1; do not edit parent input; do not edit orchestration-pack.md; do not edit handoffs; do not use run-mock-e2e-checks.sh; do not edit unrelated specs or project docs.
- Allowed Write-Set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/delivery-evidence/rsw-c2/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c2.json`
- Shared / Read-only Files: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/input/test-parent.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/orchestration-pack.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/child-specs/rsw-c2.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/handoffs/rsw-c2-handoff.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c1.json`; `skills-repo/skills/spec-change-delivery/SKILL.md`; `skills-repo/tools/ValidateChildReadiness.cs`
- Verification Commands: `dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/orchestration-pack.md --child RSW-C2 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/handoffs/rsw-c2-handoff.md`; `node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/target/output/count.txt','utf8') !== '1\n2\n') process.exit(1);"`; `node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c2.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"`
- Evidence / OpenSpec: direct smoke ledger only; write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/delivery-evidence/rsw-c2/delivery.json`; write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/closeout/children/rsw-c2.json`; no OpenSpec archive expected.
- Open Notes: Fresh child session is required. If the handoff, Child Index row, target workspace, verdict, allowed write-set, RSW-C1 closeout, or count prefix is inconsistent, stop with NOT READY and write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/delivery-evidence/rsw-c2/not-ready.md`.

## Required Child Behavior

1. Read this handoff, the Child Index row, and the child spec before writing.
2. Validate `closeout/children/rsw-c1.json` has `final_status: ran-target` and `closeout_status: closed`.
3. Validate `count.txt` is exactly `1\n` before delivery. If not, stop with NOT READY evidence.
4. Append exactly `2\n` to `count.txt`.
5. Write `delivery-evidence/rsw-c2/delivery.json` with `target_id`, `final_status: ran-target`, `written_value: "2"`, and `observed_output: "1\n2\n"`.
6. Write `closeout/children/rsw-c2.json` with `target_id`, `final_status: ran-target`, `closeout_status: closed`, and `output_status: pass`.
7. Run the verification commands and report the result.
