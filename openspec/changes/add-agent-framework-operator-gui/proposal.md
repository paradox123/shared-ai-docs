Accepted Ticket 01 is extracted into [add-agent-framework-github-intake](../archive/2026-09-14-add-agent-framework-github-intake/proposal.md) and archived. This parent remains active for Tickets 02–16; unchecked tasks retain their original scope.

## Why

The Agent Framework pilot cannot yet be tested as an unattended end-to-end run without a foreground Codex task coordinating its execution. A graphical Operator Client should make admission, workflow progress and persisted session evidence accessible while independent background execution owns the work.

The reported failure is documented in Codex task `01a09bdd-b178-79c2-83a0-e06dce488c39` (Prüfe Pilot-Session-Fokus). Ticket 14 requires background readiness monitoring as well as correlated operator evidence. A visualization alone cannot provide that execution or monitoring.

Multi-machine access and complete shared session history are already required by the pilot PRD (User Stories 3, 27–35, 77–78 and its cross-client system tests). This change implements and verifies those obligations through the graphical and local-agent paths; it does not introduce or replace them.

## What Changes

- Start background processing from a GitHub issue URL or a local issue/PRD Markdown path.
- Treat a submitted PRD as an Arbeitsmandat: autonomously derive linked issues and process them according to dependencies, retaining human product decisions, blocker resolution and approval gates.
- Preserve the submission source: GitHub PRDs produce GitHub issues; file PRDs produce local issue files. Both use the same workflow and run view.
- Persist submissions, their admitted contents and provenance, derived issue records and run relationships in the database for the common overview.
- Show the workflow and its current execution state.
- List runs and expose their persisted observable session messages, tool calls/results, handoffs and other correlated evidence.
- Make execution independent of the initiating Operator Client or Codex foreground task.
- Prove a server-hosted control-plane case with separate human work machines already in the pilot. Notification and targeted session handoff must reach the responsible human's client, not the server's local desktop.
- Deliver the full human Operator surface in the first release: interventions, continuation and live commands, control ownership and transfer, targeted Open in Codex, and explicit human approval of the qualified head.
- Preserve local-agent access alongside the GUI: provide a correlated Handover with authorized access to persisted run data and supported control actions while sessions and execution remain centrally managed.
- Deliver actionable Handover requests through a Workstation Client that automatically opens the receiving human's local agent session with the correlated context. Include pending delivery, reconnect and duplicate-opening protection.
- Start local Handover sessions with automatic read-only diagnosis and a proposed resolution; perform mutating intervention only on human instruction under existing control rules.
- Persist all observable work from participating central and local sessions as workflow activities, including messages, findings, tool inputs/results, errors and artifacts, across the complete PRD/issue lifecycle.

## Capabilities

### New Capabilities
- `agent-framework-operator-gui`: Graphical admission, workflow observation and persisted run inspection with independent background execution.

### Modified Capabilities
The existing issue-bound run model is extended to GitHub and local Markdown issue sources while retaining one ImplementationRun per issue, mandate ancestry and repository authorization. These requirements are captured in the new capability; admission must no longer assume every issue has a GitHub issue number.

## Impact

The sibling `microsoft-agent-framework-work-package-pilot/` application, a receiving Workstation Client and their documentation. The design interview is complete; implementation and direct acceptance remain open. The existing `prove-three-identity-coexistence` change and its single-person rehearsal remain separate; the GUI cannot substitute for three distinct human identities or externally approved agent definitions. See `handoff.md` for requirement provenance, delivery slices, acceptance scenarios and remaining engineering risks.
