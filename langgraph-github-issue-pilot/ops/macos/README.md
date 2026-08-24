# macOS user LaunchAgent operations

This package runs the local pilot unattended after Daniel signs in to macOS. One user LaunchAgent owns one supervisor generation. That supervisor owns exactly two processes: `github-issue-pilot` (the loopback receiver and workflow worker) and the named `cloudflared` Tunnel. No root privilege or system LaunchDaemon is used.

## What remains a human setup step

The scripts deliberately do not install or authenticate external tools. Before installation, Daniel must:

1. Install the pilot environment, Codex CLI, and `cloudflared`, and identify their absolute executable paths.
2. Create/authenticate the named Cloudflare Tunnel, its DNS route, credentials file, exact-path ingress config, Worker, Queue, and DLQ as described in `../../../cloudflare-github-webhook-relay/README.md`.
3. Configure the GitHub webhook, allowlisted repository/events, GitHub token, Daniel's GitHub login, repository-local Git author name plus GitHub noreply address, and distinct internal Tunnel-hop secret.
4. Choose private, disjoint repository/worktree paths, the persistent SQLite path, repository context, skills root, public observation surface, deterministic verification command, and the explicit `PILOT_CODEX_INTERVENTION_SURFACE='stable-app-server'` boundary.
5. Perform the final live webhook and logout/login observation. Automation does not log the user out, create credentials, change DNS/router/firewall settings, merge pull requests, deploy, or release.

## Private configuration

Create a private declarative `NAME=value` file outside the repository. It is parsed as data and never sourced or executed. Values can be unquoted or enclosed in one matching pair of single or double quotes; interpolation and shell commands are not supported. The file must be owned by the current user, be a regular non-symlink file, and have no group/other permissions.

```bash
mkdir -p "$HOME/.config/danielsvault-github-issue-pilot"
install -m 600 ops/macos/pilot.env.example \
  "$HOME/.config/danielsvault-github-issue-pilot/pilot.env"
```

Edit the copy and replace every placeholder. Keep `PILOT_HOST='127.0.0.1'`. Set `PILOT_GITHUB_WEBHOOK_URL` to the HTTPS Cloudflare Worker ingress and `PILOT_PUBLIC_RECEIVER_URL` to the distinct HTTPS Tunnel ingress; both URLs end exactly in `/webhooks/github`. Leave `GITHUB_WEBHOOK_SECRET` empty for the Tunnel hop, and use the same `PILOT_INTERNAL_WEBHOOK_SECRET` as the Cloudflare Queue consumer. Do not commit the completed file.

Validate the complete boundary before installation:

```bash
ops/macos/pilotctl verify-config \
  "$HOME/.config/danielsvault-github-issue-pilot/pilot.env"
```

Validation checks permissions/ownership, required values, absolute executable and data paths, loopback host, bounded port, HTTPS exact path, internal authentication mode, the exact stable Codex intervention surface, `cloudflared tunnel ingress validate`, and the Tunnel rule selected for the public receiver URL. Experimental Codex surfaces are rejected instead of silently enabled. Validation never prints configured values or child command output.

## Live activation gate

Live activation is a separate operator decision after static configuration validation. Keep the activation OpenSpec change active and strictly valid before enabling ingress:

```bash
openspec validate activate-probare-crm-live-pilot --strict

PILOT_ENV_FILE="$HOME/.config/danielsvault-github-issue-pilot/pilot.env"
ops/macos/pilotctl live-readiness "$PILOT_ENV_FILE"
```

`live-readiness` is read-only. It verifies that the checkout origin and base branch match the single `probare-crm` adapter, the repository-local author uses Daniel's GitHub noreply identity, the token has repository read/write and hook-administration access, all six workflow labels exist, one active webhook uses the exact Worker ingress and all required event groups, the distinct Tunnel route exists for the relay's local hop, and the complete unfiltered open backlog is visible. Its JSON output contains only adapter/version facts, counts, and hashes—no repository content, paths, URLs, credentials, or webhook bodies.

If readiness reports `workflow_labels_missing`, explicitly create only the missing repository label definitions and rerun the read-only gate:

```bash
ops/macos/pilotctl ensure-live-labels "$PILOT_ENV_FILE"
ops/macos/pilotctl live-readiness "$PILOT_ENV_FILE"
```

Label bootstrap is idempotent. It does not change issue assignments or start a workflow. Other readiness failures require correcting the reported category; do not weaken the adapter, event allowlist, blockers, or one-active-run limit.

After readiness passes, install or start the LaunchAgent and confirm the current generation:

```bash
ops/macos/pilotctl install "$PILOT_ENV_FILE"
ops/macos/pilotctl status "$PILOT_ENV_FILE"
```

Use a normal allowed GitHub action—typically applying `ready-for-agent` to the deterministic eligible frontier issue—to produce the live delivery. Do not synthesize a local bypass event. Observe the GitHub delivery ID, Cloudflare Queue/consumer outcome, local workflow GET, exact draft-PR head, and review labels through their productive surfaces. A ready backlog remains authorized without an additional product signal; blockers and repository serialization remain authoritative.

When the run reaches `verified` and `awaiting-review`, capture the bounded exact-head correlation manifest outside every repository and worktree:

```bash
LIVE_EVIDENCE="$HOME/Library/Application Support/DanielsVault GitHub Issue Pilot/evidence/issue-ISSUE_NUMBER.json"
ops/macos/pilotctl capture-live-evidence \
  "$PILOT_ENV_FILE" ISSUE_NUMBER "$LIVE_EVIDENCE"
```

Capture succeeds only when the local workflow, current draft PR, three independent reviews, criterion-appropriate direct evidence, current GitHub labels, and one 40-character head agree. UI criteria retain their screenshot requirement, REST criteria retain request/response/read-back, and document-only criteria retain rendered-document read-back; the manifest still correlates the signed delivery, run, checkpoint, worker, reviews, and current head. It writes an allowlisted mode-`600` JSON file. A new PR commit, missing review, insufficient evidence for its declared kind, `agent-running`, a merged PR, or sensitive output fails closed.

For rollback, disable the GitHub webhook first so the Queue does not gain new work, then stop the LaunchAgent with `pilotctl stop`. Disable the Cloudflare consumer as needed. Preserve the private configuration, SQLite database, Queue/DLQ, worktrees, branches, draft PR, and evidence until diagnosis and retention decisions are complete. Rollback does not merge, deploy, release, delete, or rewrite live work.

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

This workflow GET, not a lifecycle log line, is the proof that the delivery produced or resumed the intended durable workflow. Its `intervention` section exposes the persisted request, Codex task identity, first accepted answer, application state, and timestamps. An open request is answered in its uniquely named Codex App task; SQLite and lifecycle logs are not operator answer surfaces.

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
