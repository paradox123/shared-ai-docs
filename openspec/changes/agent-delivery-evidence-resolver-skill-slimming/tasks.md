## 1. Resolver Contract

- [ ] 1.1 Add the evidence-resolution CLI entrypoint, preferably `WorkflowDoctor.cs --phase evidence-resolution`, with JSON output fields defined in `design.md`.
- [ ] 1.2 Implement launcher-only evidence resolution for matching handoff, `launch-request.json`, `start-prompt.md`, and `evidence.json`.
- [ ] 1.3 Implement controller-backed visible multi-session resolution for controller summary, requests, responses, retained visible-session summary, and matched per-session launcher evidence.
- [ ] 1.4 Implement closeout archive resolution for archive summaries, explicit no-thread statuses, accepted retained-session notes, and matched session evidence paths.
- [ ] 1.5 Return deterministic `pass`, `not_ready`, and `fail` verdicts with blockers, warnings, evidence paths, and recommended next action.

## 2. Fixtures And Validators

- [ ] 2.1 Add resolver fixture manifests for launcher-only positive and negative evidence.
- [ ] 2.2 Add resolver fixture manifests for controller-backed visible multi-session positive and negative evidence, reusing existing fixture families where possible.
- [ ] 2.3 Add resolver fixture manifests for closeout archive positive and negative evidence, reusing existing visible-session closeout fixtures where possible.
- [ ] 2.4 Add negative cases for parent-started child launch, missing controller response, mismatched target id, mismatched handoff path, `manual_start_required`, `blocked`, `failed`, unarchived visible session, and manual-visible missing thread.
- [ ] 2.5 Run resolver fixture replay and retain summary evidence under the Agent Delivery testsuite evidence tree.

## 3. Skill Slimming

- [ ] 3.1 Update `docs/doc-workflow.md` with the canonical resolver command and output contract.
- [ ] 3.2 Slim `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout`, and `agent-delivery-retro-review` so they call or require the resolver instead of duplicating detailed evidence checks.
- [ ] 3.3 Preserve skill stop conditions: resolver `not_ready` or `fail` blocks implementation, closeout, and next-child release.
- [ ] 3.4 Verify the skills still state Launcher, Controller, and archive roles consistently with `docs/doc-workflow.md`.

## 4. Verification

- [ ] 4.1 Run `openspec validate agent-delivery-evidence-resolver-skill-slimming --strict`.
- [ ] 4.2 Run the resolver fixture replay command.
- [ ] 4.3 Run focused grep checks for stale Launcher-only or parent-started child launch wording in `docs/doc-workflow.md` and affected skills.
- [ ] 4.4 Run `git diff --check`.
