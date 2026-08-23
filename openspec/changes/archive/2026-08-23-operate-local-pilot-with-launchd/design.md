## Context

The production `github-issue-pilot` entry point hosts the loopback FastAPI receiver and executes the workflow worker in one process. A separately installed named `cloudflared` Tunnel connects Cloudflare's Queue consumer to the exact receiver path. SQLite, LangGraph checkpoints, the semantic command ledger, workflow operation identities, and the macOS boot-session resolver already make receiver restart convergent and prevent another reconciliation in the same OS boot.

What is missing is a login-scoped owner for those two processes. The owner must work with macOS's per-user `launchd` domain, must not place secrets in a plist or repository file, and must produce useful local lifecycle evidence without capturing arbitrary child output. The direct acceptance surface spans launchd configuration, process lifecycle, signed HTTP acceptance, and public workflow read-back.

## Goals / Non-Goals

**Goals:**

- Install one per-user LaunchAgent that starts the complete local stack at login.
- Restart the stack after either the receiver/worker process or Tunnel process exits unexpectedly.
- Preserve the existing once-per-boot reconciliation and exact-once workflow semantics across supervisor restarts.
- Keep all credentials and runtime artifacts in user-private paths and expose only bounded, correlatable local lifecycle diagnostics.
- Enforce loopback receiver binding and validate the named Tunnel configuration before starting children.
- Make install, configuration verification, status inspection, explicit restart, and uninstall repeatable without root access.
- Verify launchd start and one managed crash/restart through signed HTTP and public workflow read-back with real SQLite persistence.

**Non-Goals:**

- Installing Homebrew, `cloudflared`, Python/`uv`, Codex, credentials, DNS, GitHub webhooks, Cloudflare Worker/Queue bindings, or Tunnel credentials on Daniel's behalf.
- Opening a router port, binding the pilot to a non-loopback address, placing Cloudflare Access before the machine endpoint, or replacing the named Tunnel.
- Adding a second worker process, a second reconciliation scheduler, periodic GitHub polling, payload logging, remote log shipping, or a general-purpose process manager.
- Guaranteeing delivery after the Cloudflare Free Queue's 24-hour retention boundary; the existing startup reconciliation remains the bounded fallback.
- Logging Daniel out and back in during automated verification.

## Decisions

### Install one user LaunchAgent around a two-child supervisor

An idempotent `pilotctl` command installs a plist in `~/Library/LaunchAgents` and a versioned copy of the supervisor in `~/Library/Application Support`. The plist uses `RunAtLoad`, the GUI user domain, and `KeepAlive` for unsuccessful exits. It contains only absolute non-secret paths and no environment values.

The supervisor starts exactly two children: the existing `github-issue-pilot` process, which remains both receiver and workflow worker, and `cloudflared tunnel --config ... run ...`. If either child exits unexpectedly, the supervisor terminates the sibling, records a bounded service/exit correlation, and exits unsuccessfully so launchd starts a fresh pair. A deliberate unload or stop terminates both children and exits cleanly.

Separate LaunchAgents were rejected because they cannot express stack-level readiness or make a Tunnel failure converge on one coherent, inspectable generation. Embedding process supervision in Python was rejected because receiver lifecycle ownership belongs outside the workflow process and must survive its crash.

### Load private environment at runtime, never through the plist

The supervisor reads one explicitly configured, user-owned regular environment file whose permissions deny group and other access. The file remains outside the repository and provides the existing pilot variables plus absolute executable and Tunnel configuration paths. The supervisor validates required variable presence but never writes values to stdout, stderr, state, or logs. The example file contains names and placeholders only.

Passing secrets through launchd `EnvironmentVariables` was rejected because `launchctl print` would expose them. Command strings and `eval` were rejected in favor of fixed argv construction from validated fields.

### Treat child output as untrusted and keep a bounded lifecycle log

Both child stdout and stderr are redirected away from the LaunchAgent lifecycle log. The supervisor emits only fixed-schema events containing timestamp, generation, service name, PID, exit code, and bounded outcome code. A private atomic state file contains the current generation and managed PIDs. `pilotctl status` combines `launchctl print` with that state and a loopback readiness request; workflow details remain available through the existing authenticated/local read-back surface.

Capturing and regex-redacting arbitrary child output was rejected because safe exhaustive redaction cannot be guaranteed for payloads, tokens, or personal data. Operators can reproduce a failing child interactively with private tooling when deeper diagnostics are necessary.

### Fail closed on the local network and Tunnel boundary

The supervisor overrides `PILOT_HOST` to `127.0.0.1`, requires a bounded local port, requires an HTTPS public receiver URL whose path is exactly `/webhooks/github`, requires absolute executable/configuration paths, and runs `cloudflared tunnel ingress validate` plus an exact URL routing check before starting either child. The committed Tunnel example retains the exact path rule followed by a `404` catch-all.

The LaunchAgent starts no local public listener other than the loopback receiver. `cloudflared` initiates outbound connections; neither install nor runtime changes router, firewall, DNS, Cloudflare Access, or system LaunchDaemon settings.

### Verify the public lifecycle rather than supervisor internals

Behavior tests drive the shipped command-line scripts and generated plist. The macOS acceptance harness bootstraps a uniquely labelled user LaunchAgent with the production supervisor, a controlled Tunnel stand-in, and the real FastAPI/SQLite workflow boundary. It waits for readiness, submits one signed delivery, reads the resulting workflow through HTTP, kills the managed pilot PID, waits for a new stack generation, repeats the delivery, and confirms the same run/effect rather than a duplicate. A controlled stable boot ID proves that the restart reuses the boot evaluation.

The login assertion is split into executable launchd bootstrap evidence plus plist inspection of `RunAtLoad` in the GUI user domain; automated verification does not force a destructive logout/login cycle.

## Risks / Trade-offs

- [A Tunnel crash restarts an otherwise healthy pilot] → Restart the pair intentionally so every generation has one coherent Tunnel/receiver relationship; existing recovery and semantic idempotency make the extra pilot restart convergent.
- [Repeated fast failures create a restart loop] → Use launchd throttling, preflight all static inputs before starting children, and record bounded generation/exit outcomes for local diagnosis.
- [A child emits sensitive output] → Discard child stdout/stderr in managed mode and retain only supervisor-authored fixed-schema events.
- [Private configuration syntax executes shell code] → Document that the file is trusted user-owned configuration, enforce ownership and restrictive permissions, and never accept a repository-owned or group/world-accessible file.
- [The repository or tool installation moves] → Copy the supervisor into a stable per-user application-support directory during installation and render absolute executable/configuration paths at runtime.
- [A process is killed after accepting a delivery but before all workflow transitions finish] → Reuse the same SQLite database and LangGraph state; startup recovery and durable operation identities resume the same run.
- [A real login cycle is not exercised by CI] → Prove GUI-domain bootstrap and `RunAtLoad` structure automatically, and document one bounded human logout/login observation before live activation.

## Migration Plan

1. Copy the environment example to a private configuration directory, set mode `600`, and complete executable, Tunnel, repository, database, worker, and secret values.
2. Validate the private configuration and exact-path Tunnel through `pilotctl verify-config`.
3. Install/bootstrap the user LaunchAgent and observe status plus one signed delivery/read-back before relying on it.
4. Kill one managed process and run the recovery proof before live activation.
5. Roll back with `pilotctl uninstall`; this unloads and removes only the user LaunchAgent and installed supervisor. It does not delete private configuration, Tunnel credentials, logs, SQLite, worktrees, Queue messages, or workflow state.

## Open Questions

None for the single-user, single-Mac pilot slice.
