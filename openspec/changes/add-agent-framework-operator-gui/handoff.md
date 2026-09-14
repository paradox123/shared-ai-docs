# Operator GUI and complete distributed lifecycle: delivery handoff

The design interview is complete. Ticket 01 intake is implemented and locally accepted by the user on 2026-09-14, including real GitHub verification. Its separate-machine proof remains open under Ticket 16. See [issue-01-evidence.md](issue-01-evidence.md). Other implementation and end-to-end acceptance remain pending. The deliverable combines a full graphical Operator Client with unattended execution and a Workstation Client that opens local-agent Handovers. Existing CLI/native/local-agent access and the pilot's distributed history contract remain in force.

The user approved the [ticket plan](ticket-plan.md): 16 vertical slices with explicit blocking edges and requirement coverage are [published in the local tracker](../../../.scratch/agent-framework-operator-gui/README.md), with their current state recorded in each ticket. Ticket 01 is resolved; Ticket 02 is unblocked. Later tickets remain ready-for-agent subject to blockers. Ticket 16 owns the transferred distributed intake proof (task 3.2a).

## Existing requirements and selected extensions

| Requirement | Authority | Treatment |
| --- | --- | --- |
| Independent central execution and access from different human machines | [Pilot PRD](../../../.scratch/distributed-codex-work-package-control-plane/spec.md), US 3, 7–10; ADR 0002 | Existing obligation; verify through separate server/workstation environments. |
| Complete observable messages, tool calls/results, findings and artifacts | Pilot PRD US 27–35, 77–78 and cross-client system tests | Existing obligation; capture local assistance sessions as well as central worker sessions. |
| Exact session/attempt opening, correlated handoff, lease and fencing | Pilot PRD US 133 and execution contracts; ADRs 0001–0003 | Preserve; opening does not itself acquire control or replace the central session. |
| Graphical start, workflow, run detail and all human actions | Current user decisions; [spec](specs/agent-framework-operator-gui/spec.md) | First-release GUI scope. |
| Source-preserving PRD decomposition and database-backed submissions | Current user decisions; [ADR 0012](../../../docs/adr/0012-preserve-submission-source-for-derived-issues.md) | GitHub produces GitHub issues; file produces issue files; both link to central records. |
| Automatic local-agent opening and read-only diagnosis | Current user decisions; [ADR 0013](../../../docs/adr/0013-deliver-handover-through-a-workstation-client.md) | Concrete Handover delivery mechanism; mutating intervention requires human instruction. |

## Agreed behavior

Submit an issue or PRD through the GUI. Persist its admitted contents, origin and target repository. A PRD becomes an Arbeitsmandat with linked derived issues; each issue retains its own run. Background processing continues independently of clients. Dependencies retain the existing human merge and issue-closure gates.

On an actionable problem, the service addresses a Handover to the responsible human's Workstation Client. It automatically opens a correlated local assistance session, supplies scoped context/access and starts read-only diagnosis. The human may then instruct intervention through the local agent or GUI. Approval remains interactive and bound to the exact qualified head.

Capture the complete observable work of all participating sessions centrally: assignments/context, chats, findings, tool inputs/results/timing/errors, artifacts, handovers and decisions. Include intake/decomposition before child runs exist and retain links across issues, hosts and people. A local assistance session is a workflow step, not a disconnected conversation whose final summary alone is imported. Observation recording does not confer workflow-control authority.

## Implementation assumptions

- Extend existing public APIs, event/artifact boundaries and projections; expose database-backed evidence without distributing raw database credentials.
- Use a versioned workstation/agent adapter and a client-initiated authenticated connection. Retain pending Handovers and reconcile opening receipts before retrying; protocol, ports and polling/streaming choice are delivery details.
- Local file submission identifies the source host/workspace and ingests actual content. Infer an unambiguous target repository or ask for it in the start form. Follow the source repository's issue-file conventions and do not silently treat a client path as a server path.
- Preserve stable source-event IDs, per-session order and causal links. Buffer observations under the existing redaction policy and expose unsynchronized or unavailable history explicitly. Central commit order does not imply physical chronology across disconnected machines.
- Use existing bounded recovery/reconciliation contracts. Unresolved effects, exhausted retries, unavailable agent capabilities and transport/opening failures become concrete visible states; no hidden foreground coordinator or fabricated success.
- Capture every observable event of participating task sessions, not unrelated activity elsewhere on a user's machine. Existing redaction and private-reasoning boundaries continue to apply.

## Direct acceptance matrix

The matrix below covers the full change and remains open. The narrower Ticket 01 intake evidence is recorded separately above and does not complete the combined scenarios.

| Scenario | Expected behavior | Required evidence |
| --- | --- | --- |
| GitHub intake on separate machines (Ticket 16, transferred from 01) | Starting with an empty database, actual GitHub content is admitted without a run; its identity/version/provenance survive server and browser restart, and redelivery creates no duplicate. Current authorization, actionable errors and redaction apply across the connection. | GUI input and public readback from a different machine, retained topology and restart evidence; no server filesystem or database access from the client. Local Ticket 01 evidence is a baseline only. |
| GitHub and file intake; service restart | Admitted content/version and issue/run associations survive restart; file input is the intended remote file. | Public readback plus rendered overview for both input types. |
| PRD decomposition; interruption during child creation | Correct source-specific issues, parent/dependency links and no duplicate child on recovery. | Source readback, decomposition session history and GUI links. |
| Predecessor qualified but not merged | Dependent work stays waiting until human merge and source issue closure. | Run/queue state before and after the actual gates. |
| All initiating clients closed | Server progresses to actionable intervention or readiness independently. | Background events and later public run readback. |
| Server-triggered Handover to another machine | Actual local agent opens with correlated context and performs recorded read-only diagnosis. | Recipient-side visible session, central opening receipt, full chat/tool history and diagnosis activity in GUI. |
| Repeated delivery, offline recipient and reconnect | One local session per logical Handover; pending delivery/observations recover without duplicates or silent loss. | Stable IDs and source/central event comparison across disconnect/restart. |
| Human directs a local-agent intervention | Accepted action and outcome remain under the original run; stale control is rejected. | Local session transcript, central command/effect records and another client's GUI readback. |
| Person/host changes across a PRD lifecycle | Intake, decomposition, child runs and every central/local activity remain navigable with actor/host attribution. | Workflow overview, filtered session views and persisted history/artifact/export comparison. |
| GUI human approval | Only explicit authorized approval of the current qualified head succeeds; a changed head is rejected. | Interactive action evidence and head-bound decision history. |
| Unsupported adapter capture/opening | Concrete capability failure; no claim of complete handoff/history. | Public failure state and visible incomplete/unavailable evidence. |

## Risks and limits to resolve during delivery

The current pilot documents native TUI session opening, not automatic remote desktop task creation. Actual local-agent launch and complete event capture must be proven through supported integration surfaces. Do not substitute a prompt file, summary export or a same-host launch for the selected behavior. Workstation credentials, reachable server deployment and real human identities are integration prerequisites to establish, not evidence already present.

The GUI and Handover proof do not close Ticket 14 by themselves. Three distinct humans, exact-head approval, external Agent Definition governance and unchanged LangGraph coexistence retain their own acceptance gates. Preserve the existing `prove-three-identity-coexistence` work.

## Documentation outcome

Updated the new change's proposal, design, specification and resumable tasks. Added/clarified Einreichung, Issue-Quelle, Handover, Workstation Client and Run History in [CONTEXT.md](../../../CONTEXT.md). Clarified [ADR 0002](../../../docs/adr/0002-operator-clients-instead-of-human-agent-sessions.md); recorded source preservation in ADR 0012 and automatic Handover delivery in ADR 0013. No remaining material product question requires another interview round.
