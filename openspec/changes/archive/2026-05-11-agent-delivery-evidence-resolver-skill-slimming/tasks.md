## 1. Resolver Contract

- [x] 1.1 Add the evidence-resolution CLI entrypoint, preferably `WorkflowDoctor.cs --phase evidence-resolution`, with JSON output fields defined in `design.md`.
- [x] 1.2 Implement launcher-only evidence resolution for matching handoff, `launch-request.json`, `start-prompt.md`, and `evidence.json`.
- [x] 1.3 Implement controller-backed visible multi-session resolution for controller summary, requests, responses, retained visible-session summary, and matched per-session launcher evidence.
- [x] 1.4 Implement closeout archive resolution for archive summaries, explicit no-thread statuses, accepted retained-session notes, and matched session evidence paths.
- [x] 1.5 Return deterministic `pass`, `not_ready`, and `fail` verdicts with blockers, warnings, evidence paths, and recommended next action.
- [x] 1.6 Document canonical resolver inputs and claim levels for launcher-only, controller-backed visible multi-session, and closeout archive modes.

## 2. Fixtures And Validators

- [x] 2.1 Add resolver fixture manifests for launcher-only positive and negative evidence.
- [x] 2.2 Add resolver fixture manifests for controller-backed visible multi-session positive and negative evidence, reusing existing fixture families where possible.
- [x] 2.3 Add resolver fixture manifests for closeout archive positive and negative evidence, reusing existing visible-session closeout fixtures where possible.
- [x] 2.4 Add negative cases for parent-started child launch, missing controller response, mismatched target id, mismatched handoff path, `manual_start_required`, `blocked`, `failed`, unarchived visible session, and manual-visible missing thread.
- [x] 2.5 Run resolver fixture replay and retain summary evidence under the Agent Delivery testsuite evidence tree.

## 3. Skill Slimming

- [x] 3.1 Update `docs/doc-workflow.md` with the canonical resolver command and output contract.
- [x] 3.2 Slim `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout`, and `agent-delivery-retro-review` only after resolver fixture replay passes, so they call or require the resolver instead of duplicating detailed evidence checks.
- [x] 3.3 Preserve skill stop conditions: resolver `not_ready` or `fail` blocks implementation, closeout, and next-child release.
- [x] 3.4 Verify the skills still state Launcher, Controller, and archive roles consistently with `docs/doc-workflow.md`.

## 4. Verification

- [x] 4.1 Run `openspec validate agent-delivery-evidence-resolver-skill-slimming --strict`.
- [x] 4.2 Run the resolver fixture replay command.
- [x] 4.3 Run focused grep checks for stale Launcher-only or parent-started child launch wording in `docs/doc-workflow.md` and affected skills.
- [x] 4.4 Run `git diff --check`.
