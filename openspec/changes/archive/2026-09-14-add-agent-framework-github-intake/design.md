## Scope and acceptance

This is the accepted Ticket 01 slice extracted from [the active GUI change](../../add-agent-framework-operator-gui/design.md), following the user's 2026-09-14 acceptance and request to archive, commit, push, merge and clean up the ticket worktree. The intake requirement is transferred verbatim. Product-facing terminology is **Anforderungen**.

## Implementation

The browser uses the same-origin public API with the human's GitHub credential held only in memory. The API resolves the real issue and current repository access. PostgreSQL stores the redacted immutable snapshot and deduplicates provider issue identity. Admission has `state=admitted` and `runId=null`. The synthetic API/CLI admission path remains compatible.

The Azure deployment packages the same application behind HTTPS with loopback API/database listeners and persistent PostgreSQL/Caddy volumes. [Deployment evidence](azure-deployment-evidence.md) documents its ownership and limits; no new infrastructure changes occur during closeout.

## Verification and refactoring

See [intake evidence](issue-01-evidence.md) and [closeout checks](closeout.md). The final DRY/SOLID/KISS pass inspected endpoint authorization, shared provider/configuration boundaries, immutable storage, browser state and deployment configuration. Previously extracted `GitHubRequests` and `OperatorHttp` remove the identified duplication. No additional refactoring is justified for this scope.

## Deferred work

Tickets 02–16 and their twelve open parent tasks remain active. Ticket 16 owns the transferred distributed intake acceptance and the wider distributed lifecycle. The Azure smoke proof already demonstrates Mac-to-VM intake and container replacement/readback, but does not cover every Ticket 16 permission, identity, Handover or history scenario.
