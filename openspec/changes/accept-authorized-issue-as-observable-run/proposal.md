## Why

The managed-DTS gate now permits the isolated Microsoft Agent Framework pilot, but the pilot can only prove a framework workflow—not the product’s central user-facing work unit. Ticket 02 establishes the first control-plane vertical slice: an authorized issue must become one durable, independently observable implementation run before later worker, authorization, or control features can build on it.

## What Changes

- Add a separate, local control-plane pilot surface that accepts an authorized synthetic issue command and creates one persistent `ImplementationRun` with stable issue, repository, command, and run correlation.
- Make start-command idempotency explicit: duplicate deliveries converge to the original run and conflicting reuse of a command identity is publicly rejected before any additional effect.
- Persist a redacted, ordered canonical run history and read model that a separate Operator Client can retrieve solely through the public operator API.
- Preserve stable run identity and already-confirmed history across API and worker process restarts, while recording API/worker lifecycle evidence as supplemental correlated history.
- Expose distinct run, attempt, process, and heartbeat time axes plus source, package, configuration, and contract provenance without treating framework or Durable Task history as the canonical product record.
- Redact controlled secret canaries before events, projections, artifacts, or operator output are durably written.

## Capabilities

### New Capabilities

- `authorized-issue-observable-run`: Public, durable acceptance and independent observation of one redacted implementation run per authorized issue.

### Modified Capabilities

None.

## Impact

- Adds the first control-plane implementation and black-box tests under the isolated `microsoft-agent-framework-work-package-pilot/` sibling workspace.
- Introduces only controlled synthetic issue, repository-provider, worker, and operator-client fixtures; no real GitHub issue, worktree, Codex session, or external business effect is started in this slice.
- Builds on the completed `go-managed-pilot` gate while preserving its historical OSS no-go and leaving the LangGraph pilot, Cloudflare relay, macOS services, and ProBara configuration untouched.
