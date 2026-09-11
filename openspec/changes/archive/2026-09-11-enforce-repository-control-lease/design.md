## Context

The issue, product PRD, CONTEXT.md and ADR 0007 require repository permission as the sole access authority. Existing Ticket 02 admission/history are PostgreSQL-owned and all process clients are separate. The current activity is completed admission; no writer head exists yet.

## Goals / Non-Goals

Goals: authenticate humans, observe with read permission, claim/release exclusively with contributor permission, fence all existing run mutations, survive disconnect/restart, expose typed audit and safe rejection state.

Non-goals: enterprise SSO, GitLab/Azure adapters, transfer/takeover, command delivery, new writer activities, live provider provisioning.

## Decisions

- GitHub bearer credentials are verified through GET /user and GET /repos/{owner}/{repo}. Use immutable provider user ID, not login or client identity. A trusted repository mapping also pins GitHub's numeric repository ID. Admission persists the complete binding; later configuration changes cannot retarget existing runs or disclose their correlation through admission conflicts. Historical fixture-only rows without a binding fail closed; this ticket does not infer a migration mapping. Read/push flags normalize to read/contribute. Missing/invalid responses and provider outages fail closed; no permission cache, token persistence or local members list exists. The synthetic fixture now defines issues, repository mappings and redaction only.
- Every public Operator route requires a provider credential plus the existing ephemeral loopback harness capability. Caller actor headers/payloads are never authority. The CLI reads credentials from environment, not command arguments. GitHub's origin is fixed by default; only an explicit loopback HTTP test origin is configurable, with redirects disabled.
- The mutation boundary is POST /runs/{id}/control/{claim|release}. Every request contains targetAttemptId, expectedRunVersion, expectedHeadSha (explicit null before a writer head), and leaseEpoch. Claim is the sole bootstrap exception to lease ownership; release requires the holder. No agent operation is implied.
- A PostgreSQL run row lock spans fresh provider authorization, fence evaluation, lease update and canonical event append. It serializes across API processes. History position is the current run version. The initial admission attempt is the explicit control context until later activity tickets extend it.
- Reads and mutations reconcile an observed holder permission revocation by clearing the lease and advancing epoch/version with a distinct ControlLeaseRevoked event. This security transition is separate from the rejected requested mutation. Provider unavailability never releases a lease. Regrant requires a new claim. An unidentifiable revoked token cannot authorize or release anything; no provider credential is retained for background checks.
- Denials append only sanitized security audit, never the requested mutation or a business event. Read-authorized callers receive current decision state; callers without read permission receive only permission status, never run content. Accepted human actions carry typed provider identity; process/evidence actors are explicitly service identities. Legacy start events keep their historical fixture origin.
- Direct verification uses real API/CLI/worker processes and disposable PostgreSQL with a controlled GitHub HTTP boundary. It exercises the actual GitHub adapter without live credentials or provider writes. This is not evidence of live three-human GitHub integration (Ticket 14).

## Risks / Trade-offs

Fresh provider calls while holding the per-run lock trade latency for revalidation after contention; use bounded HTTP timeout and fail closed. An external provider change after its response cannot participate in a PostgreSQL transaction; each next request revalidates. A human-owned credential used by automation is indistinguishable from that human at the provider: clients must keep human and worker credentials separate; installation/bot identities are rejected for control.

## References

- [GitHub authenticated user](https://docs.github.com/en/rest/users/users#get-the-authenticated-user)
- [GitHub repository](https://docs.github.com/en/rest/repos/repos#get-a-repository)
- `docs/adr/0007-derive-operator-access-from-repository-permissions.md`
