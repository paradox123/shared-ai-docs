# Improve Skills Report

## Run Summary
- Processed window: 2026-04-17T06:13:55.930Z -> 2026-04-22T06:31:22.442Z
- Sessions reviewed:
  - /Users/dh/.codex/sessions/2026/04/21/rollout-2026-04-21T07-49-37-019dae96-456d-76e2-b1e5-562f1534a6cd.jsonl
  - /Users/dh/.codex/sessions/2026/04/21/rollout-2026-04-21T09-22-45-019daeeb-8c2d-74d0-b046-52b4161ab01d.jsonl
- Existing skills updated: 2 (`spec-change-delivery`, `improve-skills`)
- New candidate counters changed:
  - `runtime-proof-gate`: 2 -> 3
  - `blocker-first-runtime-prereq-gate`: +1 (new)

## Skill Updates
- [spec-change-delivery] scope=general reason=In the RAG delivery run, foundational runtime prerequisites (`rag` CLI/runtime) were discovered as blockers only after deep verification/documentation execution, and the user explicitly reported mismatch with expected OpenSpec implementation. change=Added non-negotiable + workflow gate for early foundational runtime reality checks, explicit stop-and-choose path (`bootstrap prerequisites` vs `docs-only NOT READY`), and explicit stop-and-ask rule when OpenSpec/Direct mode is simultaneously present without selection. evidence=/Users/dh/.codex/sessions/2026/04/21/rollout-2026-04-21T07-49-37-019dae96-456d-76e2-b1e5-562f1534a6cd.jsonl (assistant blocker callout around line 927, user escalation around line 1123, assistant acknowledgement around line 1128)
- [improve-skills] scope=general reason=Current run initially surfaced unrelated workspace logs (`private/me`) in the same date window, increasing noise risk for findings. change=Added explicit session selection rule to filter by active workspace/cwd, cross-workspace inclusion only on explicit request, and cursor guard for non-persisted active-thread evidence. evidence=/Users/dh/.codex/sessions/2026/04/22/rollout-2026-04-22T08-26-14-019db3de-290c-7e61-9ac1-4896394be5e3.jsonl (session_meta cwd mismatch), plus filtering behavior observed during this run.

## New Or Escalated Candidates
- [runtime-proof-gate] scope=general counter=3 signal=Even with a correct `NOT READY` verdict, late blocker escalation can still create a perceived delivery mismatch when prerequisite runtime is absent. recommendation=Keep strengthening blocker-first gating and require explicit user decision at first prerequisite failure.
- [blocker-first-runtime-prereq-gate] scope=general counter=1 signal=Spec-execution workflows can drift into evidence-heavy progress before confirming that mandatory runtime prerequisites exist. recommendation=If this repeats, create a dedicated preflight playbook skill or a reusable preflight checklist artifact for spec-change-delivery.

## Notable Discovery Patterns
- session=019dae96-456d-76e2-b1e5-562f1534a6cd pattern=User requested OpenSpec implementation with strict DoD while runtime prerequisites were missing; blocker handling happened, but too late for expectation alignment. classification=improve-existing-skill/general note=Addressed by early runtime reality gate + forced decision checkpoint in `spec-change-delivery`.
- session=019dae96-456d-76e2-b1e5-562f1534a6cd pattern=Prompt included both OpenSpec and Direct mode blocks; this increases mode ambiguity risk if not normalized immediately. classification=improve-existing-skill/general note=Addressed by explicit stop-and-ask rule for multi-mode ambiguity.
- session=019db3de-290c-7e61-9ac1-4896394be5e3 pattern=Recent session list included unrelated workspace activity by date proximity. classification=improve-existing-skill/general note=Addressed by cwd/workspace-first filtering in `improve-skills`.

## Deferred Items
- item=Automated preflight command in `spec-change-delivery` to validate required CLI/runtime before any implementation step reason=High leverage, but requires script/tooling integration beyond SKILL.md guidance.
- item=Template linter for prompts that include both OpenSpec and Direct instructions without explicit mode selection reason=Valuable but currently outside skill-document scope.

## Cursor Update
- newest_session_timestamp: 2026-04-22T06:31:22.442Z
- last-run file updated: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/improve-skills/last-run.json
