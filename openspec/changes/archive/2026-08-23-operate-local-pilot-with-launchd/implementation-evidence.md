# Implementation Evidence

## Outcome

Issue 11 is implemented as a per-user macOS LaunchAgent plus a bounded two-child supervisor. The job starts one `github-issue-pilot` receiver/worker and one named `cloudflared` Tunnel in Daniel's GUI domain. Unexpected child exit tears down the sibling and makes launchd create one fresh generation. Static configuration errors exit cleanly instead of creating a restart loop.

Private configuration is parsed as declarative data, never sourced as shell code, and is accepted only from a user-owned regular non-symlink file with no group/other permissions. The plist contains no environment values. Child output is discarded; private state and filtered lifecycle logs expose only bounded correlations. The receiver is forced to loopback and the HTTPS exact-path Tunnel route is validated before either child starts.

## Criterion Evidence

| Behavior | Verification | Observation | Status |
|---|---|---|---|
| Active OpenSpec change bounded before production edits | `openspec validate operate-local-pilot-with-launchd --strict` before implementation | Proposal, new capability spec, design, explicit write-set, task plan, and productive launchd/HTTP verification plan were complete and strictly valid | proven |
| User login-domain stack startup | `test_real_user_launch_agent_starts_and_processes_one_signed_delivery` | A uniquely labelled plist was bootstrapped in `gui/$UID`; `RunAtLoad=true` and `LimitLoadToSessionType=Aqua` were linted, and status exposed one supervisor, pilot, and Tunnel generation | proven through the non-destructive login-domain seam |
| Valid delivery after managed start | Same productive macOS test | The real FastAPI application and real SQLite accepted a correctly internally signed `POST /webhooks/github` with `202 accepted`; workflow GET exposed one issue-41 run and controlled GitHub claim effect | proven |
| Receiver crash recovery | `test_real_user_launch_agent_recovers_a_killed_pilot_exactly_once` | The managed pilot PID was sent `SIGKILL`; the supervisor recorded pilot exit 137, terminated the sibling Tunnel, and launchd started a different generation with different pilot and Tunnel PIDs | proven |
| No new boot reconciliation | Same recovery test | Workflow read-back before/after restart retained boot ID `controlled-macos-boot`, the original reconciliation start, and `first_start` outcome | proven |
| Delivery and workflow exact-once convergence | Same recovery test | Repeating the identical signed delivery after restart returned `200 already_accepted`; delivery, run, and claim stayed correlated and the controlled `agent-running` GitHub effect occurred once | proven |
| Tunnel crash and deliberate stop | `test_supervisor_starts_one_pair_and_converts_child_crash_to_bounded_failure` and `test_supervisor_signal_stops_both_children_without_requesting_restart` | Either child failure requests stack restart; operator signal stops both children and exits successfully so launchd does not recreate an intentionally stopped/unloaded job | proven |
| Secret-safe configuration | Configuration contract tests | Missing/unsafe files, permissions, variables, paths, host, URL, port, authentication, and Tunnel rules fail by bounded category. An appended shell command is rejected as data and is never executed | proven |
| Secret-safe state and logs | Supervisor/status/log tests | State is atomic mode `600` under mode-`700` runtime storage; child token/payload-like output never reached stdout/stderr, state, lifecycle logs, or filtered log read-back | proven |
| Local status and stale-state handling | `test_status_and_logs_report_only_live_bounded_supervisor_observations` | Status correlated the loaded job with non-zombie managed PIDs and loopback HTTP readiness; a dead PID changed state to `stale` and suppressed all stored identifiers | proven |
| Outbound-only network boundary | Configuration tests, generated plist test, Tunnel example | Receiver host is fixed to `127.0.0.1`; public URL must be HTTPS with exact `/webhooks/github`; `cloudflared` validates config and selected ingress; no LaunchDaemon, router/firewall mutation, or other route was added | proven at local configuration/install seam |
| Repeatable lifecycle and rollback | `test_lifecycle_commands_converge_on_one_gui_user_job` | Two installs converged on one loaded GUI job; status, restart, stop/start, and uninstall succeeded; uninstall retained data while removing the plist and installed supervisor | proven |
| Operations guidance | `langgraph-github-issue-pilot/ops/macos/README.md` | Documents private setup, validation, lifecycle commands, readiness/logs/workflow/DLQ diagnosis, 24-hour Free Queue limit, once-per-boot reconciliation, rollback, and human steps | proven by documentation review |

## Verification Commands

- `uv run pytest -o addopts='' -q tests/test_macos_launch_agent.py` in `langgraph-github-issue-pilot` → 20 passed, including two real temporary user LaunchAgents.
- `uv run pytest -o addopts='' -q` in `langgraph-github-issue-pilot` → 230 passed; one existing upstream FastAPI/Starlette TestClient deprecation warning.
- `uvx ruff check .` in `langgraph-github-issue-pilot` → all checks passed.
- `uv lock --check` in `langgraph-github-issue-pilot` → 54 packages resolved and the lockfile is valid.
- `/bin/bash -n` for `pilot-common.sh`, `pilotctl`, and `pilot-supervisor` → syntax valid under the system Bash 3.2 contract.
- `openspec validate operate-local-pilot-with-launchd --strict` → change valid.
- `git diff --check` plus no-index checks for every untracked change file → no whitespace errors.

## Refactoring Review

- **DRY:** one common declarative variable list drives clearing and allowlisting; one required subset drives presence checks; one non-zombie process-liveness function is shared by supervisor and status. The two productive launchd tests share fixture construction and bounded readiness diagnostics.
- **SOLID:** launchd owns restart policy, the supervisor owns only the two-child lifecycle, `pilot-common.sh` owns configuration/process validation, `pilotctl` owns operator installation/status, and the existing application continues to own workflow recovery/idempotency.
- **KISS:** one plist, one supervisor, two fixed child argv lists, one fixed-schema state file, and three lifecycle event forms satisfy the slice. No general scheduler, daemon framework, payload redactor, public listener, second worker, or periodic poller was added.

## Human Activation Boundary

Automated acceptance deliberately used a controlled Tunnel stand-in and controlled GitHub adapter while exercising real launchd, FastAPI, signed HTTP, SQLite, workflow, and restart behavior. Daniel must still install/authenticate real external tools and credentials, complete Cloudflare/GitHub configuration, and observe one later physical logout/login plus live delivery before Issue 12's live activation. The automated proof validates the exact GUI-domain bootstrap action and `RunAtLoad` plist contract without forcing a disruptive logout during implementation.

## Known Warning

The full suite emits the existing upstream FastAPI/Starlette warning that the current TestClient integration uses `httpx` and should eventually migrate to `httpx2`. It does not affect launchd, signed HTTP, SQLite persistence, workflow recovery, or exact-once observations.
