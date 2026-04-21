# Improve Skills Report

## Run Summary
- Processed window: 2026-04-07T12:14:36.000Z -> 2026-04-17T06:13:55.930Z
- Sessions reviewed:
  - /Users/dh/.codex/sessions/2026/04/16/rollout-2026-04-16T08-21-54-019d94f4-0b73-71f2-8640-05bac38b653a.jsonl
  - /Users/dh/.claude/projects/-Users-dh-Documents-DanielsVault/9427cfd7-4ce4-47dc-ba12-443d2136cb0d.jsonl
  - /Users/dh/.claude/projects/-Users-dh-Documents-DanielsVault/b03a0ff1-12f5-42bb-bba9-cb18bb078c02.jsonl
- Existing skills updated: 3 (`spec-change-delivery`, `check-build-watcher`, `improve-skills`)
- New candidate counters changed:
  - `runtime-proof-gate`: 1 -> 2
  - `gate-environment-truth-labeling`: +1 (new)
  - `watcher-vs-functional-proof-separation`: +1 (new)

## Skill Updates
- [spec-change-delivery] scope=general reason=Verification claims were ahead of gate-valid evidence and environment labeling was ambiguous (`READY` on 2026-04-16 followed by explicit correction on 2026-04-17 that Hetzner evidence was rehearsal-only). change=Added Verification Truth Contract (`planned`/`ran-target`/`ran-rehearsal`/`failed`/`blocked`), explicit environment truth rules, old-vs-candidate endpoint assertion rule, and stronger verify/report requirements. evidence=/Users/dh/.codex/sessions/2026/04/16/rollout-2026-04-16T08-21-54-019d94f4-0b73-71f2-8640-05bac38b653a.jsonl
- [check-build-watcher] scope=general reason=Pipeline watcher success created ambiguity about whether required Store token flow had actually been executed. change=Added hard boundaries and guardrails that watcher output is pipeline-health evidence only and cannot be reported as functional endpoint verification. evidence=/Users/dh/.codex/sessions/2026/04/16/rollout-2026-04-16T08-21-54-019d94f4-0b73-71f2-8640-05bac38b653a.jsonl
- [improve-skills] scope=general reason=Current run evidence lived primarily in Codex session logs, while skill input guidance prioritized `.claude/projects`, risking partial analysis. change=Extended input contract to include `.codex/sessions/**/*.jsonl` and `.codex/archived_sessions/*.jsonl` as co-primary for Codex Desktop runs. evidence=/Users/dh/.codex/sessions/2026/04/16/rollout-2026-04-16T08-21-54-019d94f4-0b73-71f2-8640-05bac38b653a.jsonl

## New Or Escalated Candidates
- [runtime-proof-gate] scope=general counter=2 signal=Status confidence was reported before final target-runtime verification was truly complete. recommendation=Keep reinforcing hard gate semantics in delivery skills and require explicit `ran-target` evidence for `READY`.
- [gate-environment-truth-labeling] scope=general counter=1 signal=Local rehearsal and gate-valid Hetzner runtime evidence were conflated during status communication. recommendation=Potential general playbook: environment-truth checklist before every gate verdict.
- [watcher-vs-functional-proof-separation] scope=general counter=1 signal=Watcher/build success was interpreted as broader test completion until challenged. recommendation=Keep as candidate; if repeated, create dedicated verification-evidence skill/playbook.

## Notable Discovery Patterns
- session=019d94f4-0b73-71f2-8640-05bac38b653a pattern=Gate verdict drift between reported status and actual runtime scope (rehearsal vs target environment) classification=improve-existing-skill/general note=Directly addressed in `spec-change-delivery` with strict status taxonomy and verdict gating.
- session=019d94f4-0b73-71f2-8640-05bac38b653a pattern=Pipeline monitoring used as proxy for functional endpoint proof classification=improve-existing-skill/general note=Directly addressed in `check-build-watcher` boundaries and workflow guardrails.
- session=b03a0ff1-12f5-42bb-bba9-cb18bb078c02 pattern=Sparse/failed `.claude` session data can hide active-run evidence classification=improve-existing-skill/general note=Addressed by adding Codex logs to improve-skills inputs.

## Deferred Items
- item=Automated lint/check that blocks `READY` wording when required checks are not `ran-target` reason=Useful but requires toolchain-level enforcement beyond SKILL.md edits in this run.
- item=Project-scoped STS gate runner playbook with one canonical script for local rehearsal and target-runtime gate reason=High leverage, but needs one more recurrence to decide between extending `spec-change-delivery` vs creating a dedicated playbook.

## Cursor Update
- newest_session_timestamp: 2026-04-17T06:13:55.930Z
- last-run file updated: /Users/dh/.agents/skills/improve-skills/last-run.json
