---
name: agent-delivery-retro-review
description: Review a completed or in-progress Parent/Child Agent Delivery Workflow as a meta-test, reconstruct sessions and handoffs, find workflow/skill/template failures, and feed concrete improvements back into shared-ai-docs. USE WHEN the user asks to review how a parent spec or child delivery process went, analyze handoffs/session history/evidence, make the Agent Delivery Workflow learn from past mistakes, self-optimize the workflow, or run a process retro after parent/child spec work.
---

# agent-delivery-retro-review

Run an evidence-first meta-review of Parent/Child Agent Delivery work and turn the findings into concrete workflow improvements.

This skill is for reviewing the process, not the product feature. It asks: did the Agent Delivery Workflow itself work correctly while the parent spec was split, hardened, delivered, closed out, and handed off?

## When To Use

Use this skill when:

- a Parent/Master Spec or child-slice sequence has just been delivered or partially delivered,
- multiple sessions/handoffs were involved and the user wants to learn from the process,
- a Mini-Retro mentions stale handoffs, command-contract repair, context drift, missing evidence, late blockers, or next-child ambiguity,
- the user asks for workflow self-optimization, a process review, a juror-like assessment, or "what should the workflow learn from this?"

Do not use this as a normal code review or runtime implementation skill.

## Inputs To Gather

Start from the artifacts, not from memory.

Required where available:

- Parent/Master Spec.
- Child Index or Delivery Orchestration Pack.
- Child Specs and Child Session Handoffs.
- OpenSpec active/archive changes and canonical specs.
- Evidence, closeout reports, retained summaries, command logs.
- Agent Delivery Session Launch/Queue Evidence under `_specs/agent-delivery-session-launches/` or run-local evidence roots.
- Resolver output from `WorkflowDoctor.cs --phase evidence-resolution`, when available, for launcher-only, controller-backed visible multi-session, or closeout archive claims.
- For controller-backed visible multi-session workflows, `AgentDeliveryVisibleSessionController.cs` summaries, request/response artifacts, retained visible-session summaries, and the matching per-session launcher evidence produced underneath the controller.
- History rows and SessionId lines.
- Codex session logs under `.codex/sessions/**/*.jsonl` and `.codex/archived_sessions/*.jsonl` when they are relevant and available.

If session ids are semantic labels rather than real Codex ids, document the gap and reconstruct through handoffs/history/evidence as far as possible. For future work, semantic-only `SessionId` is a finding unless the handoff also has resolver-backed launch/controller/archive evidence or explicit `legacy_reconstructed` source/date for historical pre-launcher transitions.

## Review Questions

Compare the actual flow against the desired Agent Delivery Workflow:

1. Did the Parent remain the control layer?
2. Did `spec-orchestrator` only claim orchestration/control readiness unless children were actually hardened?
3. Did each implementation-ready child have a full Child Index row, child spec, persisted handoff, enforceable write-set, verification lifecycle and evidence?
4. Did hardening stop at the handoff boundary instead of drifting into delivery or the next child?
5. Did `spec-change-delivery` implement exactly one ready child and verify the handoff/index before edits?
6. Did `spec-closeout` replay verification, archive OpenSpec, sync parent/index/evidence/handoff, and avoid releasing the next child prematurely?
7. Were command-contract rehearsals run before high-risk commands became gates?
8. Did post-archive/current replay commands replace active-change commands?
9. Was accepted evidence stable enough for future fresh sessions, or only stored in temp paths?
10. Were decisions, blockers and next actions visible early enough for the next session?
11. Did each claimed fresh-session, controller-backed, or archive transition have a matching resolver verdict? Missing resolver inputs are a workflow finding; resolver `not_ready`/`fail` should have stopped follow-up delivery.

## Output Format

Use findings first.

```markdown
## Findings
- P0/P1/P2/P3: finding title. Evidence: file/session/evidence references. Impact: why it matters. Recommendation: concrete fix.

## Reconstructed Flow
- Parent/Scope:
- Orchestrator:
- Child Hardening:
- Delivery:
- Closeout:
- Handoff / Next Child:
- Sessions:

## What Worked
- ...

## Improvements
- Sofort patchbar:
- Braucht Entscheidung:
- Spaeterer Testsuite-Ausbau:
- Automatisierung / Validator:

## Applied Changes
- Only list changes actually made.

## Next Best Patch
- One recommended next patch or hardening.
```

## Patch Policy

If the user asks only for analysis, do not edit files.

If the user asks the workflow to learn, self-optimize, or incorporate improvements:

- Apply small, evidence-backed patches to workflow docs, skills, templates or validators when the fix is obvious and local.
- Prefer improving existing skills/templates over creating broad new systems.
- Do not modify original product specs, runtime repositories, or unrelated child slices.
- Do not perform broad refactors.
- If a fix needs a policy decision, classify it as `Braucht Entscheidung` instead of guessing.

## Persistent Learning

When a pattern is likely to recur:

- Add or update a workflow/skill rule so future sessions do not rediscover it.
- Add a testsuite case or validator idea when a deterministic check would catch it.
- Record missing automation ideas, especially `.NET` file-based tools under `skills-repo/tools` when multiple skills would benefit.
- If the finding is broader than Agent Delivery, hand it to `improve-skills` or `retro-plan` as a follow-up.

## Common Findings To Watch For

- Handoff exists but the conversation did not stop at the handoff boundary.
- Child Index says one verdict while the handoff/spec says another.
- Active OpenSpec validation remains listed after the change has been archived.
- Accepted evidence points only to `/tmp` or OS temp paths.
- A command failed because it was launched from the wrong CWD.
- `spec-orchestrator` is treated as if it made children implementation-ready.
- A static fixture is used as proof of agentic orchestration.
- Optional validators leave a green result with weaker evidence.
- Session IDs in specs are semantic labels, but real Codex session logs are not linked.
- Agent Delivery resolver input is missing, stale, points at a different handoff/run, or emits `not_ready`/`fail` while the workflow narrative claims a successful transition.
