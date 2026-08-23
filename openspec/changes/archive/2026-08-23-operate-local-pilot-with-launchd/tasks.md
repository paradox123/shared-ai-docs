## 1. OpenSpec Contract and Configuration Gate

- [x] 1.1 Strictly validate the bounded proposal, new capability spec, design, write-set, task plan, and direct productive verification plan before production edits.
- [x] 1.2 Add one failing public-CLI test for private-file permissions, required variables, loopback/URL/path/port constraints, absolute executable/config paths, and Tunnel validation; implement the minimum secret-safe configuration gate and example.

## 2. User LaunchAgent Installation

- [x] 2.1 Add one failing public-CLI test for a generated per-user plist with `RunAtLoad`, unsuccessful-exit `KeepAlive`, throttling, no secrets/environment values, and stable application-support paths; implement deterministic plist rendering and linting.
- [x] 2.2 Add one failing public-CLI test for repeatable install/bootstrap, status, explicit restart, stop/start, and uninstall behavior with no second loaded job; implement `pilotctl` lifecycle commands in the GUI user domain.

## 3. Stack Supervision and Safe Diagnostics

- [x] 3.1 Add one failing supervisor-seam test proving exactly one pilot and one Tunnel child start, a child failure stops its sibling, a deliberate signal stops both cleanly, and child output never reaches lifecycle state/logs; implement the bounded two-child supervisor.
- [x] 3.2 Add one failing public-status test for private atomic generation state, launchd correlation, loopback readiness, bounded lifecycle events, and stale-state handling; implement safe local status and log access.

## 4. Productive Start and Recovery Evidence

- [x] 4.1 Add a macOS launchd behavior harness using a unique temporary user-agent label, controlled Tunnel stand-in, real FastAPI receiver/workflow boundary, real SQLite, stable boot ID, signed POST, and workflow GET; prove clean RunAtLoad/bootstrap start processes one delivery.
- [x] 4.2 Extend the launchd harness to terminate the managed pilot, observe a new stack generation, resubmit the same signed delivery, and prove one boot reconciliation identity, one workflow run/effect, and an `already_accepted` duplicate response.

## 5. Operations Guidance and Completion

- [x] 5.1 Document private setup, validation, install, status/readiness, bounded logs, explicit restart, uninstall/rollback, outbound-only Tunnel constraints, Free Queue 24-hour limit, startup reconciliation, DLQ/workflow diagnostics, and remaining human login/credential/Cloudflare/GitHub steps.
- [x] 5.2 Perform the required DRY/SOLID/KISS refactoring pass and rerun focused tests, the productive macOS harness, the full pilot suite, lint, lock validation, strict OpenSpec validation, and `git diff --check`.
- [x] 5.3 Record criterion-level implementation evidence and mark Issue 11 resolved only for behaviors proven through the installed LaunchAgent/supervisor and public HTTP seams; explicitly note any human login observation still pending.
