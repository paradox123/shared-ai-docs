## Context

The repository was initially dirty only through the untracked `openspec/changes/prove-three-identity-coexistence/` directory. That existing work is preserved.

Sources: the linked Codex task; the pilot README; Ticket 14 under `.scratch/distributed-codex-work-package-control-plane/issues/agent-framework-pilot/`; the control-plane PRD and its proposed OpenSpec specification; `CONTEXT.md`; ADR 0002 and ADR 0008. The pilot README already documents authenticated run/event/artifact/export APIs and a reconnectable event stream. Their presence does not establish an integrated unattended workflow or a graphical client.

The existing PRD already requires work across human machines, full observable messages/tool results (US 27–35), a common history across sessions (US 77–78) and cross-client readback/reconnect tests. These are inherited requirements to deliver, not new GUI features or grounds to narrow existing acceptance.

## Agreed starting scope

- Provide graphical start from a GitHub issue URL or a local issue/PRD Markdown path.
- Visualize background execution as a workflow and expose historical run details, including observable chats, tool calls/results and handoffs.
- Treat this surface as the existing glossary's Operator Client. Run History remains canonical across sessions. No new glossary term or architectural decision is needed for that reuse.
- Close the execution/monitoring gap alongside the display. Closing the initiating UI or Codex task must not stop an admitted run.
- Preserve existing repository authorization, Control Lease, redaction and human approval boundaries.
- Persist each submission, its admitted content/version and provenance, and its relationships to derived issues and runs in the database. The overview is built from these records, not from source URLs or paths alone.
- The user explicitly rejected a local-only shortcut: the pilot must represent the server-hosted application and separate human work machines, including recipient-side notifications and targeted session handoff.
- The user selected the complete human Operator surface for the first release. Routine intervention, continuation, control ownership/transfer and qualified-head approval must be possible through the GUI; targeted Open in Codex remains an explicit path for detailed session work.
- The GUI is additive. The user explicitly retains access through their local agent and the existing pilot Handover route; central session management does not make the GUI mandatory for diagnosis or supported intervention.

## First-release operator scope

Expose the existing product actions: answer an intervention; Resume, Fork, Fresh Retry or Cancel an explicit attempt/run as appropriate; send targeted queue/interrupt commands; claim/release control, request/approve a transfer or perform an audited Forced Takeover; open the selected attempt in Codex; and explicitly approve the currently qualified head as an authenticated human. Show the current controller, target attempt/session, head and actionable rejection reasons. All actions retain their existing authorization, fencing, identity and history semantics.

An existing API is not assumed to implement every required action. Delivery includes missing backend behavior needed to make these paths work through public surfaces. Ordinary Operator actions are available in the GUI without requiring manual CLI commands; this does not remove CLI, native Codex or local-agent access. The existing Codex TUI may still be used by targeted Open in Codex. Human approval does not imply mark-ready, merge, deployment or release.

This is a product-scope decision within ADRs 0001, 0002 and 0007, not a new architectural trade-off requiring another ADR.

## PRD work mandate

The user accepted autonomous PRD decomposition into linked issues and processing according to their dependencies. The PRD is the existing glossary's Arbeitsmandat; derived issues inherit authorization only within its scope. Each issue retains its own ImplementationRun. The GUI must make the PRD, derived issues, dependencies and run links navigable rather than flattening the entire PRD into one issue run.

Unresolved product decisions, actionable blockers and human approvals surface to the user. Routine decomposition and implementation within the mandate do not require another start approval. The existing per-repository serial queue still applies: a dependent successor may start only after the predecessor PR is human-merged and the blocking issue is closed. Qualification or approval alone does not satisfy that dependency.

The user subsequently chose source-preserving issue creation: a PRD submitted as a GitHub issue produces linked GitHub issues; a PRD file produces linked local Markdown issues. A directly submitted issue also retains its source. Both use the same workflow and run view. This is not an optional automatic publication or synchronization path. Issue closure and dependency checks must reflect the originating source, including local issue completion after the corresponding human merge.

These decisions reuse Arbeitsmandat, Implementierungsfreigabe and Implementierungswarteschlange from CONTEXT.md. The source distinction is recorded there as Issue-Quelle and in ADR 0012, because preserving two issue sources affects durable identity and external effects rather than only presentation.

## Working assumptions, not additional user decisions

The architectural direction discussed on 2026-09-14 is recorded in [ADR 0014](../../../docs/adr/0014-evolve-control-plane-backend-with-versioned-workflows.md): evolve the existing pilot backend, separate shared control-plane rules from workflow execution, and prepare a definition/version boundary for different workflows. It distinguishes the accepted target from implemented evidence. Additional workflows, definition-selection/governance behavior and a visual editor require separately specified scope; they do not automatically expand the current 16 tickets.

- Reuse the pilot's public run/history/control surfaces and extend them where necessary.
- Bind every submission to a visible implementation repository. For local files, infer a candidate from explicit metadata or the containing repository when unambiguous; otherwise require repository selection in the start form. Source location alone does not grant repository authorization. Record a stable source identity and an admitted content revision/snapshot so later file edits cannot silently change an active mandate.
- Resolve a file input against an explicit accessible workspace/host, never silently against the server's filesystem when the user meant their own machine. Use an appropriate file-ingestion/workspace boundary for remote clients and persist the submitted content in the database. Follow the source repository's local issue conventions (this repo uses `.scratch/<feature>/issues/`); do not ask the user to design filenames or identifier formats. The exact ingestion mechanism is a delivery decision; preserving the file source and its readable/writable location is required behavior.
- Use a browser-based Operator Client that connects to the central API with each human's authenticated identity. Same-machine development is useful but is not acceptance evidence for the distributed case.
- Persist only observable session content and expose unavailable content explicitly; do not claim access to private model reasoning.
- Retain progress for on-demand inspection. Surface actionable blockers and readiness rather than requiring the user to watch routine execution.
- Continue to distinguish a native Codex TUI opening from a Codex desktop task: the current documented adapter reports `appTaskVisible:false`.

## Server-hosted observation and handoff

The service owns submission records, background orchestration, Run History and outstanding human-action state independently of client connections. Human clients connect from separate work machines. The user selected a Workstation Client as the delivery channel: a server-originated trigger automatically opens the receiving human's local agent with the targeted Handover. Server-local macOS notifications, email/chat delivery or a web link alone do not establish this behavior. Delivery failures remain visible without losing the underlying human-action request.

The user confirmed centrally managed sessions: handoff does not move workflow execution or its workspace to the human machine. The user also explicitly retained the ability to use their existing local agent to investigate and assist with the run. The local agent is an additional authorized access path, not a replacement central worker or a mandatory GUI interaction. ADR 0002 now makes this distinction explicit.

For that route, the service provides a correlated Handover identifying the submission, run, activity/attempt, central session, head, error or pending request, current control state and supported next actions. The receiving local agent can retrieve the authorized persisted submission, observable messages, tool calls/results, artifacts and relevant history, including further pages after the initial context package. A static summary without access to retained evidence is insufficient. Context may be selected/bounded without losing discoverability of the remaining authorized records.

Implementation assumption: database-backed content is exposed through scoped public read/control interfaces, not raw database credentials or direct state edits. The exact local-agent connector/CLI/API packaging is a delivery decision. The entire observable work of the associated local session joins the central Run History, not just commands or returned answers; this includes user/agent messages, tool inputs/results, findings and artifacts. Private internal reasoning remains outside the observable-history contract as already stated in the PRD. Merely reading an Handover neither claims control nor creates a session fork. Mutating run control requires the current human authorization/control context; local agent assistance cannot perform the interactive human head-approval gate.

## Automatic local agent opening

The Workstation Client receives a durable Handover addressed to its associated human and creates or reopens the correlated local assistance session with the Handover already available. This local session is distinct from the central execution session; both identities and their relationship are explicit. The opening does not relocate central execution or implicitly acquire control. ADR 0013 explicitly extends ADR 0002's previous no-automatic-human-task rule for this path, rather than silently changing the meaning of central sessions.

Working delivery assumptions: use an authenticated client-initiated connection to the control plane, durable delivery/opening acknowledgements and reconciliation by Handover identity. Bind a delivery to the addressed workstation and reconcile before re-dispatch so multiple connections/restarts do not create duplicate sessions. Keep offline delivery pending; revalidate recipient access and whether the request is still actionable before opening after reconnect. Report unsupported local-agent capabilities or opening failures in the GUI with a supported retry path. These transport, registration and retry details are implementation choices, not questions for the design interview.

The user accepted automatic read-only diagnosis: the opened local agent loads relevant history and evidence, investigates the problem and prepares a proposed resolution. Mutating intervention waits for a human instruction and the existing control gates. Automatic recording of the diagnosis is part of observation, not authority to change workflow decisions or business state.

## Complete lifecycle observation

Persist every participating session's observable user/agent messages, prompts/assignments, findings, tool calls with parameters/results/duration/errors, artifact references, handovers, commands and decisions centrally. A local diagnosis is an explicit workflow activity/attempt with its own session identity, linked to its target and Handover. Record execution host, responsible human, agent identity and applicable definition/runtime provenance. Human or host changes never start an unrelated history.

The Einreichung anchors the complete lifecycle: intake and PRD decomposition observations exist before derived issue runs, and each child issue retains one ImplementationRun. The overview traverses mandate activities and child-run histories without flattening them or creating duplicate issue runs. Filters by actor, host, activity and session expose detail without removing the shared lifecycle view.

Extend the existing observation/ingestion boundary to Workstation Clients. Stable source event identities, replay acknowledgements and redacted buffering permit reconnect without duplicate/lost observations. Preserve source-session order and causal links; central committed order is not proof of physical event order across disconnected hosts. Expose pending synchronization or unavailable content explicitly. Never label a workflow step's history complete while its recorded observations remain unsynchronized. Lack of an observable local-agent integration is a capability blocker, not permission to substitute summary-only capture.

## Interview exit audit

No material product decision remains unresolved. Accepted: full additive GUI, both issue sources, database-backed submissions, autonomous PRD decomposition with human gates, distributed server/client operation, automatic agent opening, read-only local diagnosis and complete lifecycle observation. Remaining questions concern adapter support, transport, schemas, UI implementation and deployment prerequisites; resolve these during delivery rather than extending the interview. See `handoff.md` for the implementation assumptions and evidence still required.

## Acceptance direction

Start one controlled input in the GUI, close the UI and initiating Codex task, and observe independent progress to a concrete intervention or a qualified result. Reopen the same run and trace activities, observable messages, tool calls/results, handoffs and outcome through persisted public evidence. This proof supplements, but does not replace, Ticket 14's identity and governance gates.

Run the acceptance flow with a server environment and a separate human work machine, without shared localhost, an assumed shared filesystem or direct database access. Show that the addressed human receives actionable notice and opens the corresponding run/session from their own client. Read the admitted input and PRD/issue/run relationships after client/server restart. A same-machine demonstration cannot satisfy this distributed acceptance criterion.

Also exercise the retained local-agent route with the GUI closed: obtain the targeted Handover, retrieve persisted context/evidence, submit an authorized supported intervention and observe its result in the same central run. Reopen the GUI to verify the action and outcome. Prove a stale or unauthorized local agent cannot mutate the run, and that neither access path silently replaces the central session or performs human approval.

Prove automatic agent opening on the receiving machine from a server-triggered Handover with the GUI closed, then repeat the delivery and reconnect the Workstation Client. The same logical Handover must identify one correlated local assistance session. Test offline/pending delivery and an actionable opening failure without treating either as completed intervention. Preserve the central session identity throughout.
