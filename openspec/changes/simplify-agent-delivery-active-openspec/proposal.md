## Why

Agent Delivery was introduced to keep large spec work from blurring the active implementation scope, but the current solution has grown into a heavy Parent/Child/session-orchestration framework with large Skill MDs, many control artifacts, launcher/controller evidence, and retained test data. The workflow now risks creating the same context pressure it was meant to prevent.

This change simplifies Agent Delivery around a smaller rule: the active implementation context is one narrow OpenSpec change, while large specs remain read-only reference material. Cleanup is part of the change because the repository now contains many obsolete workflow, evidence, fixture, and session artifacts from the previous approach.

## What Changes

- Introduce an OpenSpec-first active-scope model for Agent Delivery: each implementation run works from one small OpenSpec change, not from an entire parent/master spec or a generated session chain.
- Replace "fresh session as default scope control" with a compact derived active-context view from the active OpenSpec change.
- Keep parent/master specs only as strategic reference and coverage sources; they must not become the direct implementation contract.
- Deprecate broad Parent/Child session orchestration, visible-session controller requirements, and launcher/archive evidence as normal workflow requirements.
- Update `docs/doc-workflow.md` to make the simplified OpenSpec-first model canonical.
- Slim the affected Skill MDs so they point to the canonical workflow and avoid duplicating large matrices or handoff schemas.
- Move enforceable workflow rules out of long Skill-MD prose and into small deterministic tools or command-line checks.
- Add cleanup requirements for obsolete Agent Delivery artifacts, including archived experimental OpenSpec changes, tests, fixtures, generated session evidence, launcher/controller tooling, and old handoff/index structures that are no longer part of the simplified workflow.
- Preserve only artifacts that remain useful as historical reference, accepted baseline evidence, or regression tests for the simplified workflow.
- **BREAKING**: Workflows that require visible Codex-App child sessions, controller-backed multi-session proof, or launcher/archive evidence as a normal pass condition are no longer part of the default Agent Delivery workflow. They must be explicitly retained as legacy/debug tooling or deleted.

## Capabilities

### New Capabilities

- `docworkflow-active-openspec-scope`: Defines the simplified Agent Delivery operating model where a narrow OpenSpec change is the active implementation context, with parent specs as reference-only inputs and cleanup of obsolete workflow artifacts as a first-class requirement.

### Modified Capabilities

- `docworkflow-agent-delivery-testsuite`: Replaces heavy session-orchestration validation requirements with checks that prove active OpenSpec scope, skill slimming, cleanup safety, and absence of stale default-session requirements.

## Impact

- `docs/doc-workflow.md`
- `skills-repo/skills/spec-orchestrator/SKILL.md`
- `skills-repo/skills/child-spec-hardening/SKILL.md`
- `skills-repo/skills/spec-change-delivery/SKILL.md`
- `skills-repo/skills/spec-closeout/SKILL.md`
- `skills-repo/skills/agent-delivery-retro-review/SKILL.md`
- Legacy or experimental Agent Delivery tools under `skills-repo/tools/`
- New or updated lightweight validation tools under `skills-repo/tools/`
- Legacy Agent Delivery tests, fixtures, generated evidence, and session-workflow data under `tests/docworkflow-agent-delivery/`
- Active and archived OpenSpec changes that exist only to validate the discarded session-orchestration workflow
- Any child-session handoff, launch evidence, run-profile, visible-session, or archive artifacts that are no longer referenced by the simplified workflow
