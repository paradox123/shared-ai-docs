Accepted Ticket 01 is extracted into [add-agent-framework-github-intake](../archive/2026-09-14-add-agent-framework-github-intake/proposal.md) and archived. Accepted Ticket 02 is extracted into [add-agent-framework-background-start](../archive/2026-09-14-add-agent-framework-background-start/proposal.md). This parent remains active for Tickets 03–16; unchecked tasks retain their original scope.

## 1. Design interview

- [x] 1.1 Recover the reported testing gap and inspect existing domain, pilot and Ticket 14 contracts.
- [x] 1.2 Record explicit starting requirements and distinguish GUI delivery from Ticket 14 acceptance.
- [x] 1.3 Settle first-release human intervention/control scope: complete human Operator surface selected.
- [x] 1.4a Settle PRD semantics: autonomous linked-issue decomposition within the mandate, with dependency and human-merge gates.
- [x] 1.4b Preserve the submitted issue source; document explicit repository binding and immutable admission input as implementation assumptions.
- [x] 1.5 Select automatic local-agent opening via Workstation Client as the Handover delivery path; document durable pending delivery and visible opening failures.
- [x] 1.5a Require persisted submissions/relationships and the server-to-human-client case in the pilot; reject server-local notification shortcuts.
- [x] 1.5b Keep sessions/execution centrally managed and preserve the local-agent Handover/access path alongside the GUI.
- [x] 1.5c Start automatic read-only local diagnosis; require human instruction for mutating intervention.
- [x] 1.5d Confirm existing distributed-history requirements and explicitly include complete local-session output across the PRD/issue lifecycle.
- [x] 1.6 Perform the interview exit audit, update requirements and record glossary/ADR changes.

## 2. Vertical delivery slices

- [x] 2.0a Prepare 16 self-contained vertical tickets with acceptance criteria, dependency graph and requirement coverage in ticket-plan.md; the approved files are published in the local tracker.
- [x] 2.0b User approved ticket granularity and blocking edges; publish 16 individual ready-for-agent tickets plus feature/spec entry points to the configured local tracker.
- [x] 2.1 Document vertical slices, assumptions, existing-requirement traceability and direct acceptance scenarios in handoff.md.
- [x] 2.2a Ticket 01 implementation and local acceptance: GitHub intake, immutable redacted submission, current authorization and GUI readback without starting a run; user accepted the local/live-provider evidence in [issue-01-evidence.md](../archive/2026-09-14-add-agent-framework-github-intake/issue-01-evidence.md) on 2026-09-14. Separate-machine acceptance moved from 2.2b to Ticket 16 / 3.2a.
- [ ] 2.2 Submission-to-run slice: persist GitHub/file input, admitted version and repository binding; read it through API and GUI after restart.
- [ ] 2.3 PRD-to-issues slice: derive linked issues in the originating source, capture decomposition observations, reconcile interrupted creation and enforce dependency/merge gates.
- [ ] 2.4 Unattended-run slice: connect admission to background execution and monitoring; prove progress to intervention/readiness with all initiating clients closed.
- [x] 2.4a Ticket 02: atomically link GitHub submissions to runs and durable first-step disposition; preserve authorization, immutable mandate and duplicate-start safety.
- [x] 2.4b Ticket 02: independent worker performs real requirements analysis through the central agent/history integration; retain session, messages, tools, artifacts and concrete errors.
- [x] 2.4c Ticket 02: GUI start and simple status/result view; browser/launcher closure, restart/replay, late-response reconciliation and controlled failure verified; final regression 218 tests (194 passed, 24 optional skipped), both review axes clear. See [issue-02-evidence.md](../archive/2026-09-14-add-agent-framework-background-start/issue-02-evidence.md).
- [ ] 2.5 Lifecycle-observation slice: ingest central and local activity/session events, artifacts and actor/host provenance; show workflow, timeline, session detail and pending synchronization; verify replay/readback/export.
- [x] 2.5a Ticket 03: GUI-started run list, observed activity/attempt/session graph and complete retained detail through public history/artifact reads.
- [x] 2.5b Ticket 03: confirmed pagination/live cursors, replay/restart, explicit unavailable/redacted evidence and access revocation across filters/artifacts verified through the browser.
- [x] 2.5c Ticket 03: real controlled issue GUI start, two-client semantic comparison, visual acceptance, full regression (223 tests: 198 passed, 25 optional skipped; added race case separately green) and two-axis review (0/0 remaining findings). See [issue-03-evidence.md](issue-03-evidence.md).
- [ ] 2.6 Workstation-Handover slice: authenticate receiving client, deliver/open the actual local agent, start recorded read-only diagnosis and prove offline/reconnect/duplicate-opening behavior.
- [ ] 2.5d Ticket 03 usability correction: readable workflow/session presentation, named tool and artifact details, complete technical evidence on demand; verify semantic content and desktop/mobile reading paths against controlled and real runs.
- [ ] 2.7 Human-operation slice: expose GUI and local-agent interventions under common authorization/lease/fencing, retain native session opening and prove explicit current-head human approval.

## 3. Acceptance and completion

- [x] 3.0a Deploy the accepted Ticket 01 GUI/API and durable database to an isolated Azure pilot under the user's credit subscription, retaining the spending limit, HTTPS and current repository authorization. See [azure-deployment-evidence.md](../archive/2026-09-14-add-agent-framework-github-intake/azure-deployment-evidence.md).
- [x] 3.0b Verify the deployed GUI, authenticated intake/readback and persistence after service replacement; document URL, resource ownership, cost controls and operating commands. Deployment evidence does not close the remaining Ticket 16 scenarios. See [azure-deployment-evidence.md](../archive/2026-09-14-add-agent-framework-github-intake/azure-deployment-evidence.md).

- [ ] 3.1 Use TDD through public interfaces for each behavior-bearing slice and rendered browser checks for the GUI.
- [ ] 3.2 Prove server-to-separate-workstation Handover with GUI closed, complete local diagnostic chat/tool capture and a human-directed continuation; inspect the same lifecycle through another authorized client.
- [ ] 3.2a Ticket 16 distributed intake acceptance (moved from 2.2b): repeat real GitHub GUI intake into an empty database, authorized readback, redaction/error checks, duplicate delivery and server/browser restart on separate machines; retain the same submission identity/version with no run until explicitly started. Azure server and Mac browser intake/replacement evidence now exist; finish the remaining distributed permission/error and overall acceptance cases before closing this gate.
- [ ] 3.3 Execute the acceptance matrix in handoff.md; record expected behavior, observations and retained evidence, including capability gaps.
- [ ] 3.4 Keep Ticket 14 identity, approval, external-definition governance and coexistence gates separate; document remaining unverified gates honestly.
- [ ] 3.5 Refactor touched code/skills/specs for DRY/SOLID/KISS before archive, rerun relevant verification and strict OpenSpec validation.
