---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.
---

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-matt-pocock-skills` if not.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments.

Before drafting, confirm only the repo guidance needed for issue creation:

- issue tracker location
- triage labels and milestone conventions
- domain docs / glossary locations
- project-specific planning guards only when the source material or repo guidance makes them relevant

If the repository has an `AGENTS.md` / `CLAUDE.md` Agent skills block, read only the issue-tracker, label, domain-doc, and planning-guard references needed for issue creation. Do not continue with generic labels when the repo has a local label vocabulary.

When creating issues from a PRD or parent issue, inspect nearby open issues or the relevant milestone only enough to avoid duplicate slices and preserve dependency chains.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Apply repo-specific planning guards only when they are present in local guidance and relevant to the slice.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
- Contract/decision and documentation/operator-readiness slices are valid only when they produce a directly usable decision/artifact with clear verification criteria.
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)
- **Labels / milestone**: proposed tracker labels and milestone, if the repo uses them
- **Spec decision**: required spec/change reference or no-spec rationale when relevant

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

If the current conversation already contains an explicit grill/design approval, treat that as approval only for the decisions that were actually resolved. Still show the final slice map before publishing unless the user explicitly asked you to create issues immediately.

### 5. Publish the issues to the issue tracker

For each approved slice, publish a new issue to the issue tracker. Use the issue body template below.

Only publish an issue with a ready-for-agent / AFK-ready label when the slice has enough context, acceptance criteria, dependency information, and verification guidance for an agent to start without more human decisions. Use a HITL or needs-decision label instead when the slice is still a decision/design task.

Publish issues in dependency order (blockers first) so you can reference real issue identifiers in the "Blocked by" field.

For GitHub-specific publishing details and batch checks, use [publishing.md](references/publishing.md).

<issue-template>
## Parent

A reference to the parent issue on the issue tracker (if the source was an existing issue, otherwise omit this section).

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

Avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it here and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Verification

- [ ] Relevant test, documentation, spec, or operational check

## Blocked by

- A reference to the blocking ticket (if any)

Or "None - can start immediately" if no blockers.

</issue-template>

Do NOT close or modify any parent issue.
