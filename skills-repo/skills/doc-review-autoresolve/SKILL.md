---
name: doc-review-autoresolve
description: Automatically resolve review findings in specs/docs, including strict content-quality review, and rerun review until no autonomous inconsistencies remain. USE WHEN the user asks to review docs/specs and wants findings fixed immediately (e.g. "reviewe", "fix findings", "reviewe nochmals", "passe Findings an"). Prefer autonomous fix + re-review loops and only ask the user when a real decision or missing requirement blocks safe resolution.
---

# doc-review-autoresolve

## Purpose

Resolve documentation/spec review findings with minimal back-and-forth:
1. review,
2. fix autonomous findings immediately,
3. re-review in the same run,
4. assign an implementation-readiness verdict after spec edits,
5. repeat until only true decision blockers remain.

## Shared Workflow Contract

Use `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` as the canonical reference for:
- marker meaning (`[MISSING ...]`, `[DECISION ...]`, `[REVIEW ...]`, `[BLOCKED ...]`),
- Session Briefing,
- Review Control Surface,
- Mini-Retro,
- DoR/DoD expectations,
- history/session requirements.

This skill must not introduce conflicting gate definitions.

## Trigger Conditions

Use this skill when the user asks to:
- review specs/docs,
- apply review findings,
- resolve inconsistencies automatically,
- re-review after edits in the same thread.

Typical prompts:
- "reviewe die spec"
- "passe es an"
- "reviewe nochmals"
- "fix die findings"
- "mach das automatisch"

For larger, resumed, or context-compressed review work, begin by clarifying or inferring the Session Briefing: active mode/skill, source-of-truth files, review goal, non-goals, in-scope fixes, expected output, verification/review path, and open decisions. Ask only when a blocker cannot be inferred safely.

## Default Mode (Auto-Resolve)

Default behavior is **autonomous resolution**:
- Do not stop after listing findings when a safe textual/spec correction is possible.
- Apply fixes directly.
- Re-run review immediately.
- Continue until no autonomous findings remain.
- Ensure the spec's Review Control Surface exists and matches the detailed goal/scope/cases/commands/open decisions/readiness.
- Do not invent product behavior, data fields, acceptance criteria, or architecture decisions that are not already implied by the spec and its normative sources.

## Stop-and-Ask Boundary

Ask the user only if one of these applies:
1. Multiple valid fixes with materially different product behavior.
2. Security/legal/compliance/policy implications.
3. Missing requirement or unresolved decision that cannot be inferred safely.
4. Any marker that requires owner input to close (`[MISSING ...]`, `[DECISION ...]`, blocking `[REVIEW ...]`).
5. A content or semantic problem has multiple plausible domain fixes and the spec does not already choose one.

If none apply, resolve findings without waiting for confirmation.

## Review-to-Resolution Loop

1. **Collect findings**
   - Review target docs/specs with file+line references.
   - Prioritize by severity/risk.
   - Include formal checklist findings, content-quality findings, and domain/semantic findings.
   - Write findings for a reader who may only have checked goal, in-scope, out-of-scope, verification commands, and test cases.
   - Treat a missing or stale Review Control Surface as a finding for specs.

2. **Classify each finding**
   - `autonomous`: can be fixed safely now.
   - `needs-decision`: blocked by requirement/decision gap.

3. **Patch autonomous findings**
   - Apply minimal, targeted edits.
   - Preserve scope and existing accepted decisions.

4. **Re-review immediately**
   - Re-run focused review on touched sections and cross-references.
   - Catch regressions/secondary inconsistencies.

5. **Assign readiness verdict**
   - After every spec edit or review loop, report `IMPLEMENTATION READY`, `READY WITH NON-BLOCKING NOTES`, or `NOT IMPLEMENTATION READY`.
   - Do this automatically; do not wait for the user to ask "is it implementation-ready?"
   - Base the verdict on the shared DoR, parent/child conformance, open blockers, content-quality findings, acceptance criteria, and verification commands.

6. **Repeat until stable**
   - Stop when either:
     - no findings remain, or
     - only `needs-decision` findings remain.

7. **Report clearly**
   - What was fixed.
   - What remains and why user input is required.
   - Final implementation-readiness verdict.
   - Final state: clean vs pending decisions.
   - Mini-Retro after larger review loops or before context/handoff loss: decisions, changes, open items, missing evidence, skill/workflow friction, and whether to continue in this session or start a new one.

## Reader-Calibrated Finding Format

Findings must be understandable without assuming the user has read the full middle of the spec. The user often reviews goal, in scope, out of scope, verification commands, and test cases first; write findings so they make sense from that reading path.

For every non-trivial finding, include:

1. **Short finding**: one sentence in plain language.
2. **Why it matters**: what could go wrong in implementation or review if this stays as-is.
3. **Where to check**: point to the relevant goal/scope/verification/test-case section, not only the deep contract section.
4. **Concrete example**: a small example of the missing/ambiguous artifact, command, status, case, or behavior.
5. **Needed action**: what can be fixed autonomously, or what decision the user must make.

Avoid findings that only say things like "contract depth missing", "fixture strategy unclear", or "status provenance incomplete". Expand them:

```md
Finding: The S3 bundle contract says a manifest must be signed, but the verification cases do not say what a valid or invalid signed manifest looks like.
Why it matters: An implementation could pass by checking only that a `signature` field exists, while never proving that wrong signatures block installation.
Where to check: S3 goal/scope says "signed Free-Entry bundle"; Verification Commands and Harness Cases should prove valid and invalid signature behavior.
Example: Add one small embedded manifest example or require fixtures such as `valid-free-entry-bundle.yaml` and `invalid-signature-bundle.yaml`.
Needed action: Autonomous if fixture names and fields follow existing S1/S2 harness conventions; ask the user only if the signing model itself is undecided.
```

If a finding is technical, translate the technical term once. For example, define "canonical serialization" as "the exact byte representation that is hashed or signed, so two systems calculate the same hash for the same logical data."

## Content Quality Review Gate

Do not limit reviews to "does the spec have the expected sections?" A spec can be formally complete and still wrong.

Always perform a strict content-level review of the whole intended change, using established requirements-quality criteria as a checklist. Data contracts are only one part of this review.

Review the spec for:

1. **Correctness and domain fit**: The described behavior matches the stated user/problem context and does not solve the wrong problem.
2. **Necessity and scope discipline**: Requirements are needed for the goal; extras, hidden scope creep, and accidental non-goals are visible.
3. **Completeness**: Normal paths, edge cases, failure paths, dependencies, constraints, and open assumptions are covered or explicitly marked.
4. **Consistency**: Requirements, examples, terminology, statuses, parent/child scope, acceptance criteria, and verification commands do not contradict each other.
5. **Unambiguity**: A competent implementer would not have to choose between multiple materially different meanings.
6. **Feasibility and implementability**: The requested behavior is technically plausible in the declared environment and does not depend on impossible timing, missing systems, or undefined capabilities.
7. **Verifiability/testability**: Each important requirement can be proven by inspection, test, demonstration, analysis, or explicit acceptance evidence.
8. **Traceability**: Important requirements connect to source intent, parent scope, acceptance criteria, verification commands, and downstream artifacts.
9. **Atomicity and abstraction level**: Requirements are not bundled so broadly that partial implementation can masquerade as completion, and they do not over-prescribe implementation unless that is the actual constraint.
10. **Operational and lifecycle fit**: Migration, fallback, observability, rollback, compatibility, ownership, and closeout evidence are present when the change needs them.

Then perform domain-specific semantic checks for the actual system flow:

1. Identify the core user journey, system flow, or operational lifecycle in the spec.
2. For every data contract, check whether produced data remains interpretable downstream.
3. For every artifact, check whether it includes enough provenance, identity, version, status, and relationship fields to be useful later.
4. For every state transition, check that the source event, allowed statuses, failure statuses, and blocking behavior are defined.
5. For every security/privacy rule, check that leaks, unsafe defaults, and forbidden flows are testable.
6. For every acceptance criterion, ask whether an implementation could pass the written test while still violating the intended behavior.

Treat these as high-priority findings when present:

- produced data that lacks the identity/context/provenance required by the spec's own downstream flow,
- hashes/signatures without canonical serialization rules,
- manifests without version/source/provenance/status fields,
- status fields without allowed values or failure states,
- "success" paths that can skip required runtime/harness assertions,
- local/online fallback paths that produce incompatible artifacts,
- requirements that are ambiguous, infeasible, untestable, internally inconsistent, or not traceable to the stated goal,
- missing failure/edge-case behavior that makes the intended feature impossible to implement safely,
- child spec scope that contradicts or silently drops parent-scope intent.

Use domain examples only as examples. For instance, in a survey contract, answers may need stable question identity if later steps must interpret answers by question. Do not turn that specific field into a universal requirement for unrelated specs.

## Relationship To Doc Co-Authoring

`doc-coauthoring` creates and expands the spec: requirements, test cases, verification commands, examples, and user-facing decisions.

`doc-review-autoresolve` is the cleanup and consistency loop after that authoring work:

1. Reorder or clarify existing content.
2. Align repeated terminology, statuses, acceptance criteria, and verification commands.
3. Resolve contradictions where the correct fix is already implied by the spec or normative sources.
4. Add missing cross-references, parent/child conformance rows, and readiness verdicts when they follow from existing content.
5. Stop when a real product, scope, architecture, security, legal, or data-contract decision is required.

This skill may run directly after `doc-coauthoring`. Its goal is to make the authored spec coherent and implementation-ready where possible, not to hallucinate missing product decisions.

When invoked after `child-spec-hardening`, treat the hardened child spec, parent conformance table, normative contract, harness cases, verification commands, DoR/DoD, and closeout sync targets as the review surface. Fix autonomous drift and inconsistencies, but do not invent missing contract decisions or mark a child ready when hardening gates are absent.

## Spec Hygiene Rules

When touching spec files:
- keep header contract intact,
- keep the Review Control Surface synchronized with detailed sections and final readiness verdict,
- preserve `SessionId`,
- append one concise history row for meaningful changes,
- do not silently weaken acceptance/verification gates,
- keep parent/child specs consistent where one references the other as normative source.
- after changes, add or report a readiness verdict so the user does not need a separate follow-up question.

## Output Contract

After each run, report:
1. **Applied fixes** (file + line references).
2. **Residual findings requiring user decision** (if any).
3. **Content quality review result** (`no content blockers` or list of content blockers, including domain/data-contract blockers when present).
4. **Review Control Surface result** (`present and consistent`, `updated`, or remaining blocker).
5. **Readiness verdict** (`IMPLEMENTATION READY`, `READY WITH NON-BLOCKING NOTES`, or `NOT IMPLEMENTATION READY`).
6. **Re-review result** (`no findings` or list of remaining blockers).
7. **Mini-Retro** when the review loop was substantial, ended a session, or hands off to another skill.
8. **Smallest next step** only when user input is needed.

Never claim "done" while unresolved blocking decision findings remain.
