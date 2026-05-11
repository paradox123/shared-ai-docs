# Implementation Evidence

Date: 2026-05-11

## Scope Contract

In scope:

- Add a surgical evidence-resolution phase to `WorkflowDoctor.cs`.
- Resolve launcher-only, controller-backed visible multi-session, and closeout archive claims into stable JSON.
- Add deterministic resolver fixtures and retained fixture replay evidence.
- Update `docs/doc-workflow.md` and the five affected Agent Delivery skills so they defer concrete evidence checks to the resolver.

Out of scope:

- Changing launcher/controller runtime behavior.
- Fixing the previously observed RADW2-C5 live regression hang.
- Replacing existing live E2E scripts or redesigning Agent Delivery orchestration.
- NCG backend build monitoring; this repository is `shared-ai-docs`, not the NCG backend.

## Verification

| Command | Status | Evidence |
| --- | --- | --- |
| `openspec validate agent-delivery-evidence-resolver-skill-slimming --strict` | ran/pass | Change is valid. |
| `dotnet run skills-repo/tools/WorkflowDoctor.cs -- --help` | ran/pass | Help includes `--phase evidence-resolution`. |
| `dotnet run skills-repo/tools/WorkflowDoctor.cs -- --phase evidence-resolution --fixture tests/docworkflow-agent-delivery/e2e/fixtures/evidence-resolver --summary-out tests/docworkflow-agent-delivery/e2e/evidence/evidence-resolver/latest-summary.json` | ran/pass | Fixture replay verdict `pass`; retained summary written. |
| `dotnet run skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence` | ran/pass | Existing visible-session fixture family still passes, 11 cases. |
| `dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout` | ran/pass | Existing archive fixture family still passes, 10 cases. |
| Focused `rg` consistency checks for canonical resolver/role wording | ran/pass | Affected skills reference the resolver and no stale duplicated evidence-matrix wording remained. |
| `git diff --check` | ran/pass | No whitespace errors. |
| Real Agent Delivery regression via `AgentDeliverySessionLauncher.cs --mode launch --agent codex` | ran/pass | Run `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T160023Z-post-implementation-regression`; parent evidence plus five child launcher evidence files exist; closeout `overall_status: pass`; `count.txt` is exactly `1\n2\n3\n4\n5\n`. |
| NCG `check-build-watcher` build monitoring | blocked/not-applicable | Current repo is `shared-ai-docs`; no NCG backend build was in scope or available for this change. |

## Acceptance Evidence

- Launcher-only resolver covers positive launch evidence and negative mismatched target, mismatched handoff, `manual_start_required`, `blocked`, and `failed` cases.
- Controller-backed resolver covers positive visible multi-session evidence, missing response, and parent-started child launch rejection.
- Closeout archive resolver covers positive retained/archive evidence, unarchived visible session, and manual-visible missing thread rejection.
- Skills now keep role/stop-condition guidance and delegate low-level artifact consistency to `WorkflowDoctor.cs --phase evidence-resolution`.
- The real post-implementation regression passed with one launcher-created parent session and five launcher-created child sessions.
