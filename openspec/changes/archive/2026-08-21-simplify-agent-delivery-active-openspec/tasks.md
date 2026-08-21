> Archive reconciliation: these checkboxes record the original implementation. A later cleanup commit intentionally removed the dedicated Agent Delivery docs, skills, testsuite, cleanup validator, and prose-budget validator. The final maintained surface is `ValidateActiveOpenSpecScope.cs`; the reconciled delta specs describe that end state.

## 1. Canonical Workflow Simplification

- [x] 1.1 Update `docs/doc-workflow.md` so Agent Delivery defaults to one narrow active OpenSpec change as the implementation context.
- [x] 1.2 Mark parent/master specs as reference-only implementation inputs and describe how they are used for conformance and coverage.
- [x] 1.3 Remove or clearly mark as legacy/debug-only the default child-session launch, visible-session controller, launcher evidence, run-profile, and archive-proof rules.
- [x] 1.4 Add a short derived active-context view, explicitly sourced from the active OpenSpec change and not treated as a separate source of truth.

## 2. Skill MD Slimming

- [x] 2.1 Slim `spec-orchestrator` so it routes large work toward narrow OpenSpec changes and does not release implementation through child-session handoffs.
- [x] 2.2 Slim `child-spec-hardening` so it no longer requires child handoff/index machinery for default Agent Delivery work.
- [x] 2.3 Slim `spec-change-delivery` so implementation starts from the active OpenSpec change and blocks parent-as-implementation behavior.
- [x] 2.4 Slim `spec-closeout` so closeout records OpenSpec verification and cleanup evidence without requiring visible-session archive proof.
- [x] 2.5 Slim `agent-delivery-retro-review` so retro reviews evaluate active-scope adherence, skill bloat, and cleanup quality instead of launcher/controller evidence completeness.
- [x] 2.6 Replace long Agent Delivery rule prose in affected Skill MDs with short routing text and validator command references.
- [x] 2.7 Run a prose-budget scan proving Skill MDs no longer duplicate large Agent Delivery session, controller, run-profile, archive, active-scope, or cleanup rule matrices as default rules.

## 3. Simplified Validation

- [x] 3.1 Add deterministic active-scope fixtures for parent-as-implementation rejection and narrow OpenSpec slice acceptance.
- [x] 3.2 Add `skills-repo/tools/ValidateActiveOpenSpecScope.cs` or an equivalent small CLI validator for active OpenSpec scope, out-of-scope boundaries, write-set expectations, tasks, and verification presence.
- [x] 3.3 Add `skills-repo/tools/ValidateAgentDeliveryCleanup.cs` or an equivalent small CLI validator for cleanup-manifest deleted, retained, and archive-reference path classes.
- [x] 3.4 Add a prose-budget validator or script that fails long Agent Delivery rule blocks in affected Skill MDs and requires validator command references.
- [x] 3.5 Replace old default session-orchestration test entrypoints with simplified active-scope, cleanup, and prose-budget validation commands.
- [x] 3.6 Ensure validation fails if canonical docs, active Skill MDs, or active tests reference deleted Agent Delivery artifacts as default workflow inputs.
- [x] 3.7 Add a deterministic Active OpenSpec E2E that derives five narrow changes from a large parent fixture and writes final output `1` through `5`.

## 4. Artifact Inventory and Cleanup

- [x] 4.1 Create `cleanup-manifest.json` covering Agent Delivery OpenSpec changes, docs, Skill MDs, tools, tests, fixtures, generated evidence, session-workflow data, and handoff/index artifacts.
- [x] 4.2 Classify each cleanup candidate as `delete`, `retain`, or `archive-reference` with a short reason.
- [x] 4.3 Delete obsolete generated session evidence and live-session run directories that are not retained baselines.
- [x] 4.4 Delete obsolete visible-session, controller/launcher, and orchestration tests/fixtures after simplified validation is in place.
- [x] 4.5 Delete or archive obsolete tools such as launcher/controller/evidence/archive/orchestration helpers unless `cleanup-manifest.json` records an explicit retained legacy/debug reason.
- [x] 4.6 Delete or archive obsolete Agent Delivery OpenSpec experiment changes after retaining any necessary summary or accepted baseline reference.
- [x] 4.7 Write `cleanup-evidence.md` listing deleted paths, retained paths, archive-reference paths, and unresolved cleanup decisions.

## 5. OpenSpec and Regression Sync

- [x] 5.1 Update canonical OpenSpec specs to remove retired Agent Delivery testsuite requirements and add simplified active-scope requirements.
- [x] 5.2 Resolve or retire the active `agent-delivery-run-profiles-compact-debug` change if it conflicts with the simplified default workflow.
- [x] 5.3 Run OpenSpec validation for `simplify-agent-delivery-active-openspec`.
- [x] 5.4 Run simplified active-scope validation, cleanup-manifest validation, prose-budget validation, doc/skill text scans, and `git diff --check`.
- [x] 5.5 Review the final diff for accidental deletion of retained historical evidence or canonical docs.
