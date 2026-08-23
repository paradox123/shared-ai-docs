# macOS user LaunchAgent operations

This package runs the local pilot unattended after Daniel signs in to macOS. One user LaunchAgent owns one supervisor generation. That supervisor owns exactly two processes: `github-issue-pilot` (the loopback receiver and workflow worker) and the named `cloudflared` Tunnel. No root privilege or system LaunchDaemon is used.

## What remains a human setup step

The scripts deliberately do not install or authenticate external tools. Before installation, Daniel must:

1. Install the pilot environment, Codex CLI, and `cloudflared`, and identify their absolute executable paths.
2. Create/authenticate the named Cloudflare Tunnel, its DNS route, credentials file, exact-path ingress config, Worker, Queue, and DLQ as described in `../../../cloudflare-github-webhook-relay/README.md`.
3. Configure the GitHub webhook, allowlisted repository/events, GitHub token, Daniel's GitHub login, and distinct internal Tunnel-hop secret.
4. Choose private, disjoint repository/worktree paths, the persistent SQLite path, repository context, skills root, public observation surface, and deterministic verification command.
5. Perform the final live webhook and logout/login observation. Automation does not log the user out, create credentials, change DNS/router/firewall settings, merge pull requests, deploy, or release.

## Private configuration

Create a private declarative `NAME=value` file outside the repository. It is parsed as data and never sourced or executed. Values can be unquoted or enclosed in one matching pair of single or double quotes; interpolation and shell commands are not supported. The file must be owned by the current user, be a regular non-symlink file, and have no group/other permissions.

```bash
mkdir -p "$HOME/.config/danielsvault-github-issue-pilot"
install -m 600 ops/macos/pilot.env.example \
  "$HOME/.config/danielsvault-github-issue-pilot/pilot.env"
```

Edit the copy and replace every placeholder. Keep `PILOT_HOST='127.0.0.1'`, use an HTTPS `PILOT_PUBLIC_RECEIVER_URL` ending exactly in `/webhooks/github`, leave `GITHUB_WEBHOOK_SECRET` empty for this Tunnel path, and use the same `PILOT_INTERNAL_WEBHOOK_SECRET` as the Cloudflare Queue consumer. Do not commit the completed file.

Validate the complete boundary before installation:

```bash
ops/macos/pilotctl verify-config \
  "$HOME/.config/danielsvault-github-issue-pilot/pilot.env"
```

Validation checks permissions/ownership, required values, absolute executable and data paths, loopback host, bounded port, HTTPS exact path, internal authentication mode, `cloudflared tunnel ingress validate`, and the Tunnel rule selected for the public receiver URL. It never prints configured values or child command output.

## Install and operate

Set one convenience variable in the interactive shell, then use the public operator commands:

```bash
PILOT_ENV_FILE="$HOME/.config/danielsvault-github-issue-pilot/pilot.env"

ops/macos/pilotctl install "$PILOT_ENV_FILE"
ops/macos/pilotctl status "$PILOT_ENV_FILE"
ops/macos/pilotctl logs "$PILOT_ENV_FILE"
ops/macos/pilotctl restart "$PILOT_ENV_FILE"
ops/macos/pilotctl stop "$PILOT_ENV_FILE"
ops/macos/pilotctl start "$PILOT_ENV_FILE"
```

`install` is repeatable: it unloads the existing job, replaces the installed supervisor and plist, validates the rendered plist, and bootstraps one job in `gui/$UID`. `RunAtLoad` starts that same job at later Aqua logins. `restart` replaces the current generation. `stop` deliberately unloads both children; `start` loads the installed plist again.

Installed non-secret files live at:

- `~/Library/LaunchAgents/com.danielsvault.github-issue-pilot.plist`
- `~/Library/Application Support/DanielsVault GitHub Issue Pilot/bin/`
- `~/Library/Application Support/DanielsVault GitHub Issue Pilot/run/stack.state`
- `~/Library/Logs/DanielsVault GitHub Issue Pilot/lifecycle.log`

The plist contains paths only—not environment values. State is mode `600`; state and application-support directories are mode `700`. `status` reports the loaded job, current generation, managed PIDs, and a loopback `/openapi.json` readiness result. It does not trust stale, malformed, broadly readable, or dead-PID state. `logs` returns at most the latest 50 lines and emits only complete fixed-schema supervisor lifecycle events. Child stdout/stderr is discarded because arbitrary worker, GitHub, or Tunnel output cannot be exhaustively redacted.

For one workflow, use the local public read-back after a signed delivery:

```bash
curl --fail --silent --show-error \
  "http://127.0.0.1:8788/workflows/OWNER/probare-crm/issues/ISSUE_NUMBER"
```

This workflow GET, not a lifecycle log line, is the proof that the delivery produced or resumed the intended durable workflow.

## Crash recovery behavior

If either managed child exits unexpectedly, the supervisor terminates its sibling and exits with a restart-required status. launchd throttles and starts a fresh pair. The new pilot process reuses the same SQLite database, LangGraph thread, delivery/command ledger, operation identities, and macOS boot-session ID. Therefore a process crash cannot itself allocate another boot reconciliation or another issue run; an accepted delivery can be resubmitted with the same ID and must converge on `already_accepted`.

A bounded recovery check is:

1. Confirm `pilotctl status` reports `state=current receiver=ready` and retain the generation and pilot PID.
2. Submit one valid signed test delivery and retain the workflow GET response.
3. Terminate that exact pilot PID.
4. Wait for `status` to report a different generation with `state=current receiver=ready`.
5. Resubmit the identical signed delivery and require `200 already_accepted`.
6. Read the workflow again and compare run, claim, boot reconciliation, and controlled external-effect evidence. Lifecycle logs only corroborate the PID/generation transition.

## Availability boundary and diagnosis

Cloudflare Queues on Workers Free retains a message for 24 hours. Within that window the Queue retries delivery while the Mac, Tunnel, or receiver is temporarily unavailable. At or beyond 24 hours, delivery is no longer guaranteed. On the next qualifying Mac boot, the pilot performs at most one current-state startup reconciliation; process restarts in that boot do not start another. Current state cannot reconstruct every historical comment/event, so a manual GitHub webhook redelivery or DLQ investigation can still be required.

Use these surfaces in order:

1. `pilotctl status` for launchd, generation/PID, and local receiver readiness.
2. `pilotctl logs` for bounded `stack_start`, `child_exit`, and `stack_stop` correlations.
3. Local `GET /workflows/...` for workflow, checkpoint, recovery, and reconciliation state.
4. `npx wrangler tail` and the Cloudflare Queues dashboard for relay outcomes and primary/DLQ backlog, correlated by `delivery_id` without copying payloads or signatures.
5. GitHub delivery/redelivery UI for an event that expired or cannot be reconstructed from current state.

## Uninstall and rollback

```bash
ops/macos/pilotctl uninstall "$PILOT_ENV_FILE"
```

Uninstall unloads both children and removes only the user plist and installed supervisor files. It intentionally preserves the private environment file, Tunnel credentials/config, lifecycle log, runtime state, SQLite database, worktrees, Queue/DLQ messages, and workflow records. Remove preserved data only after separately confirming its exact path and retention need.
