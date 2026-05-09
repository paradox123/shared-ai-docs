# Agent Delivery Session Handoff: RSW-C4

- Parent: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md`
- Target ID: RSW-C4
- Target Role: child
- Child Spec: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/child-specs/rsw-c4.md`
- Child Index / Queue: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/orchestration-pack.md`
- Handoff File: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/handoffs/rsw-c4-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Next Mode / Skill: spec-change-delivery
- Current Verdict: IMPLEMENTATION READY
- Scope Summary: Deliver RSW-C4 in a launcher-created child Codex session by appending exactly `4\n` after the RSW-C3 output, then persist RSW-C4 delivery and closeout evidence.
- Non-Goals: Do not write values 1, 2, 3, or 5; do not repair predecessor children; do not edit parent input; do not edit orchestration-pack.md; do not edit handoffs; do not use run-mock-e2e-checks.sh; do not edit unrelated specs or project docs.
- Allowed Write-Set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/delivery-evidence/rsw-c4/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c4.json`
- Shared / Read-only Files: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/orchestration-pack.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/child-specs/rsw-c4.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/handoffs/rsw-c4-handoff.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c3.json`; `skills-repo/skills/spec-change-delivery/SKILL.md`; `skills-repo/tools/ValidateChildReadiness.cs`
- Verification Commands: `dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/orchestration-pack.md --child RSW-C4 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/handoffs/rsw-c4-handoff.md`; `node -e "const fs=require('fs'); if (fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt','utf8') !== '1\n2\n3\n4\n') process.exit(1);"`; `node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c4.json','utf8')); if (s.final_status !== 'ran-target' || s.closeout_status !== 'closed') process.exit(1);"`
- Evidence / OpenSpec: direct smoke ledger only; write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/delivery-evidence/rsw-c4/delivery.json`; write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c4.json`; no OpenSpec archive expected.
- Open Notes: Fresh child session is required. If the handoff, Child Index row, target workspace, verdict, allowed write-set, RSW-C3 closeout, or count prefix is inconsistent, stop with NOT READY and write `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/delivery-evidence/rsw-c4/not-ready.md`.

## Required Child Behavior

1. Read this handoff, the Child Index row, and the child spec before writing.
2. Validate `closeout/children/rsw-c3.json` has `final_status: ran-target` and `closeout_status: closed`.
3. Validate `count.txt` is exactly `1\n2\n3\n` before delivery. If not, stop with NOT READY evidence.
4. Append exactly `4\n` to `count.txt`.
5. Write `delivery-evidence/rsw-c4/delivery.json` with `target_id`, `final_status: ran-target`, `written_value: "4"`, and `observed_output: "1\n2\n3\n4\n"`.
6. Write `closeout/children/rsw-c4.json` with `target_id`, `final_status: ran-target`, `closeout_status: closed`, and `output_status: pass`.
7. Run the verification commands and report the result.
