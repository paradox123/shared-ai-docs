# Proposal

Implement `ADV-CAS-S1` by adding an explicit visible Codex App adapter to `AgentDeliverySessionLauncher.cs`.

The adapter uses `codex app-server --listen stdio://` and JSON-RPC calls for `initialize`, `thread/start`, `thread/name/set`, `turn/start`, and `thread/list`. It preserves the existing `codex exec` path as headless evidence and prevents headless success from being reported as a visible Codex-App session.
