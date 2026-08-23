## Why

The local pilot already persists deliveries, resumes interrupted workflows, and reconciles long Mac absences, but it still depends on a person starting both the receiver and its named Cloudflare Tunnel. A user LaunchAgent must make that existing stack available after Daniel signs in and restore crashed processes without creating another workflow, another boot reconciliation, or an unsafe network or logging surface.

## What Changes

- Add an installable per-user macOS LaunchAgent and a bounded supervisor that start the local pilot process and the named outbound `cloudflared` Tunnel together after login.
- Restart the managed stack after an unexpected child exit while retaining the existing database, boot-session identity, inbox idempotency, and workflow recovery contracts.
- Add local status and redacted correlation logs that expose service lifecycle, restart, and receiver-readiness outcomes without recording environment values, tokens, webhook bodies, or arbitrary child output.
- Keep the receiver bound to loopback and require the private, exact-path named Tunnel configuration; no router port, public local listener, or Cloudflare Access application is introduced.
- Provide idempotent install, status, verification, and uninstall operations with private configuration outside the repository.
- Prove clean start and crash recovery through an installed-plist/supervisor behavior harness, signed HTTP delivery, public workflow read-back, and exact-once effect observation.

## Capabilities

### New Capabilities

- `macos-local-pilot-operations`: Per-user login startup, bounded process supervision, secret-safe local diagnostics, outbound-only network constraints, and productive start/recovery verification for the local pilot stack.

### Modified Capabilities

None.

## Impact

- Write-set: `langgraph-github-issue-pilot/ops/macos/`, focused tests under `langgraph-github-issue-pilot/tests/`, `langgraph-github-issue-pilot/README.md`, `cloudflare-github-webhook-relay/README.md` only where the local operations hand-off changes, Issue 11, and this OpenSpec change.
- The installed plist, private environment file, Tunnel credentials/configuration, runtime state, and logs remain outside the repository under Daniel's user account.
- The existing `github-issue-pilot` process remains both receiver and workflow worker; the existing named `cloudflared` Tunnel remains the only external connection into the loopback receiver.
- Existing webhook, workflow read-back, SQLite, LangGraph, reconciliation, crash-recovery, Queue/DLQ, GitHub, merge, deploy, and release contracts are unchanged.
