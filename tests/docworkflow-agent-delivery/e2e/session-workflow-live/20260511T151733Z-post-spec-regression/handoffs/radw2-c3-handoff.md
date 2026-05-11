# Agent Delivery Session Handoff: RADW2-C3

- Parent: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/input/test-parent.md`
- Target ID: RADW2-C3
- Target Role: child
- Child Spec: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/child-specs/radw2-c3.md`
- Child Index / Queue: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/orchestration-pack.md`
- Handoff File: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/handoffs/radw2-c3-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Next Mode / Skill: spec-change-delivery
- Current Verdict: IMPLEMENTATION READY
- Scope Summary: Deliver RADW2-C3 in a launcher-created child Codex session by changing `target/output/count.txt` from exactly `1\n2\n` to exactly `1\n2\n3\n`, then persist RADW2-C3 delivery and closeout evidence.
- Non-Goals: Do not write values 4 or 5; do not rewrite prior lines except to preserve them; do not edit parent input; do not edit orchestration-pack.md; do not edit handoffs; do not use run-mock-e2e-checks.sh; do not edit unrelated specs or project docs.
- Allowed Write-Set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/delivery-evidence/radw2-c3/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/closeout/children/radw2-c3.json`
- Shared / Read-only Files: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/input/test-parent.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/orchestration-pack.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/child-specs/radw2-c3.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/handoffs/radw2-c3-handoff.md`; `skills-repo/skills/spec-change-delivery/SKILL.md`; `skills-repo/tools/ValidateChildReadiness.cs`
- Verification Commands: `dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/orchestration-pack.md --child RADW2-C3 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/handoffs/radw2-c3-handoff.md`; `node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/target/output/count.txt','utf8') !== '1\n2\n3\n') process.exit(1);"`; `node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/closeout/children/radw2-c3.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"`
- Evidence / OpenSpec: direct regression ledger only; write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/delivery-evidence/radw2-c3/delivery.json`; write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/closeout/children/radw2-c3.json`; no OpenSpec archive expected.
- Open Notes: Fresh child session is required. If the handoff, Child Index row, target workspace, verdict, allowed write-set, prior child closeout, or current count prefix is inconsistent, stop with NOT READY and write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/delivery-evidence/radw2-c3/not-ready.md`.

## Required Child Behavior

1. Read this handoff, the Child Index row, and the child spec before writing.
2. Validate that `count.txt` exists and equals exactly `1\n2\n`. If not, stop with NOT READY evidence.
3. Write exactly `1\n2\n3\n` to `count.txt`.
4. Write `delivery-evidence/radw2-c3/delivery.json` with `target_id`, `final_status: ran-target`, `written_value: "3"`, and `observed_output: "1\n2\n3\n"`.
5. Write `closeout/children/radw2-c3.json` with `target_id`, `final_status: ran-target`, `closeout_status: closed`, and `output_status: pass`.
6. Run the verification commands and report the result.
