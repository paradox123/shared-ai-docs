# Improve Skills Report

## Run Summary
- Processed window: 2026-04-03 (Thread STS/Hetzner/OpenSpec)
- Sessions reviewed: 1 thread-level pattern analysis
- Existing skills updated: 0
- New candidate counters changed: 3

## Skill Updates
- [improve-skills] scope=general reason=Recurring rework patterns were concrete enough for workflow hardening change=Applied the method to extend documentation workflow with Decision Freeze, DoR/DoD, OpenSpec gates, and anti-rework guardrails evidence=Repeated late decisions on migration, cert source, pipeline parity, and runtime validation caused multiple correction loops

## New Or Escalated Candidates
- [decision-freeze-pack] scope=general counter=1 signal=Late architecture/ops decisions caused repeated rework recommendation=Add mandatory pre-apply decision freeze in workflow
- [openspec-ssot-discipline] scope=general counter=1 signal=Hybrid execution (partly OpenSpec, partly ad-hoc) reduced predictability recommendation=Use explicit mode: OpenSpec SSOT for medium/large changes
- [runtime-proof-gate] scope=general counter=1 signal=Implementation felt partial until compose/runtime proof was shown recommendation=Require runtime validation evidence before "done"

## Notable Discovery Patterns
- session=sts-hetzner-onboarding-thread pattern=Key choices were finalized during implementation, not before planning classification=project-scoped-playbook note=Introduce Decision Freeze Pack before apply
- session=sts-hetzner-onboarding-thread pattern=Reference repo parity expectations surfaced late classification=project-scoped-playbook note=Define baseline contract and parity checklist at start
- session=sts-hetzner-onboarding-thread pattern=OpenSpec artifacts existed but blocked items remained while implementation continued classification=improve-existing-skill note=Treat blocked tasks as release blockers, not soft notes

## Deferred Items
- item=Automated cursor-based improve-skills run on full `.claude/projects/**/*.jsonl` reason=This update focused on concrete thread outcomes and immediate workflow hardening

## Cursor Update
- newest_session_timestamp: 2026-04-03
- last-run file updated: no
