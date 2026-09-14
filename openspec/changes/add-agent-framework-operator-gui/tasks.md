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
- [x] 2.2a Ticket 01 implementation and local acceptance: GitHub intake, immutable redacted submission, current authorization and GUI readback without starting a run; user accepted the local/live-provider evidence in issue-01-evidence.md on 2026-09-14. Separate-machine acceptance moved from 2.2b to Ticket 16 / 3.2a.
- [ ] 2.2 Submission-to-run slice: persist GitHub/file input, admitted version and repository binding; read it through API and GUI after restart.
- [ ] 2.3 PRD-to-issues slice: derive linked issues in the originating source, capture decomposition observations, reconcile interrupted creation and enforce dependency/merge gates.
- [ ] 2.4 Unattended-run slice: connect admission to background execution and monitoring; prove progress to intervention/readiness with all initiating clients closed.
- [ ] 2.5 Lifecycle-observation slice: ingest central and local activity/session events, artifacts and actor/host provenance; show workflow, timeline, session detail and pending synchronization; verify replay/readback/export.
- [ ] 2.6 Workstation-Handover slice: authenticate receiving client, deliver/open the actual local agent, start recorded read-only diagnosis and prove offline/reconnect/duplicate-opening behavior.
- [ ] 2.7 Human-operation slice: expose GUI and local-agent interventions under common authorization/lease/fencing, retain native session opening and prove explicit current-head human approval.

## 3. Acceptance and completion

- [x] 3.0a Deploy the accepted Ticket 01 GUI/API and durable database to an isolated Azure pilot under the user's credit subscription, retaining the spending limit, HTTPS and current repository authorization. See azure-deployment-evidence.md.
- [x] 3.0b Verify the deployed GUI, authenticated intake/readback and persistence after service replacement; document URL, resource ownership, cost controls and operating commands. Deployment evidence does not close the remaining Ticket 16 scenarios. See azure-deployment-evidence.md.

- [ ] 3.1 Use TDD through public interfaces for each behavior-bearing slice and rendered browser checks for the GUI.
- [ ] 3.2 Prove server-to-separate-workstation Handover with GUI closed, complete local diagnostic chat/tool capture and a human-directed continuation; inspect the same lifecycle through another authorized client.
- [ ] 3.2a Ticket 16 distributed intake acceptance (moved from 2.2b): repeat real GitHub GUI intake into an empty database, authorized readback, redaction/error checks, duplicate delivery and server/browser restart on separate machines; retain the same submission identity/version with no run until explicitly started. Requires a reachable test server and separate browser machine; local Ticket 01 acceptance does not satisfy this gate.
- [ ] 3.3 Execute the acceptance matrix in handoff.md; record expected behavior, observations and retained evidence, including capability gaps.
- [ ] 3.4 Keep Ticket 14 identity, approval, external-definition governance and coexistence gates separate; document remaining unverified gates honestly.
- [ ] 3.5 Refactor touched code/skills/specs for DRY/SOLID/KISS before archive, rerun relevant verification and strict OpenSpec validation.
