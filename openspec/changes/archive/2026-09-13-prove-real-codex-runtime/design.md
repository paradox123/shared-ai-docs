## Context

The accepted controlled adapter proves product semantics but is not real Codex.
The installed runtime is initially codex-cli 0.153.4. The app-server protocol is
generated from the pinned binary, with experimental capabilities disabled.

## Goals / Non-Goals

Prove real runtime behavior before product repositories are connected. Preserve
the canonical result contract and the existing control-plane boundaries. Do not
claim that protocol discovery, a fake provider, or a successful process start
proves interactive lease enforcement. No native app database editing or private
IPC integration is permitted. No cloud infrastructure or remote Git writes.

## Decisions

- A separate executable gate owns temporary repositories and isolated Codex state.
  It receives no arbitrary worktree path or arbitrary user prompt.
- SHA-256 pins identify the binary and schema contract. Drift fails before session
  creation. Version strings alone do not qualify an executable.
- The complete worker-result-v3 contract is vendored as a versioned fixture from
  the LangGraph sibling, without modifying that sibling. An endpoint-only schema
  removes unsupported restrictions; complete local validation remains mandatory.
- Real protocol probes and controlled process-failure tests are separately labelled.
  Session-start intent is persisted before dispatch. Ambiguous recovery is terminal
  unsafe unless an exact existing receipt can be adopted; it never starts again.
- Missing safe same-session display or confirmed handoff with write fencing is a
  no-go, not permission to silently fork or bypass the Control Lease. Partial
  capability evidence is retained; later acceptance tasks stay open.

## Risks / Trade-offs

Native Codex clients may accept direct input without an external lease check.
Session notifications are not authorization hooks. The real endpoint may reject
schemas that are locally valid. An isolated session store may not be visible to
the desktop app; visibility alone would still not prove safe write ownership.

## Validation

The real adapter uses an isolated app-server behind a run-scoped gateway. The
official remote Codex TUI opens the exact persisted session. The gateway accepts
native prompts through the existing fenced Operator write command and dispatches
only while that command is delivered under the run lock. Mutating execution is
available only through a controlled MCP tool; the model's native environment is
read-only, with network and unrelated integrations disabled. Each MCP execution
is independently authorized through the same command boundary. The gateway
rejects client requests that change sandbox, tools, configuration or session
identity. Desktop sidebar visibility is reported separately from native TUI
opening. This is an implementation of same-session access, not a handoff or an
implicit new session.

Public Python gate CLI tests cover preflight, contract projection, restart and
process cleanup. Separate HTTP/Operator CLI process tests verify that failure and
provenance survive API/worker replacement under the same run. Real probes record
which runtime operations actually ran, with IDs and explicit not-executed reasons.
