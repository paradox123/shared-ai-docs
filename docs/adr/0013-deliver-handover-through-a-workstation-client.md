# Deliver Handover through a Workstation Client

The server-hosted control plane delivers actionable Handover requests to a Workstation Client associated with the addressed human. The client automatically opens a correlated session in that human's local agent with the Handover and authorized access to the centrally retained evidence. The user selected this direct agent entry point instead of email, chat or a server-local desktop notification as the primary delivery path. Multiple clients and complete shared history are existing pilot requirements; this ADR selects their concrete automatic Handover delivery mechanism, not a new distributed product model.

This extends ADR 0002's earlier rule that an intervention does not create a human agent task: an explicitly addressed Handover can now automatically create/open a local assistance session. Ordinary observation still creates no supervisor session, central execution remains central, and the local session is not presented as the original worker session or an implicit fork of it.

## Consequences

- The pilot must prove server-to-workstation delivery and actual local agent opening. A web link, generated prompt file or same-host server notification alone does not prove this behavior.
- Handover identity, recipient, delivery/opening state and resulting local-session correlation belong to the central history. Repeated delivery must reconcile an existing opening rather than spawn duplicate local sessions.
- Offline workstations retain pending delivery. Missing agent support or opening failures remain actionable and visible; session opening is not itself an intervention answer or human approval.
- Use a versioned local agent adapter and authenticated workstation connection. Transport and endpoint choices remain implementation decisions; the preferred design is a client-initiated connection so the server need not reach a public port on each human machine.
- After opening, the local agent automatically retrieves relevant evidence, performs read-only diagnosis and prepares a proposed resolution. Mutating intervention requires the human's instruction and existing control authority; human approval remains an explicit interactive human action.
- The local assistance session is a centrally registered workflow activity. Its full observable conversation, tool calls/results, findings and artifacts join the canonical history, including during automatic read-only diagnosis. A final summary alone is insufficient.
