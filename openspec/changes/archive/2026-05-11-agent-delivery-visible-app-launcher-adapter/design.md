# Design

## Approach

Extend `AgentDeliverySessionLauncher.cs` with an explicit `codex-app-server` adapter while preserving the existing `codex-exec` adapter as headless evidence.

The app-server adapter uses `codex app-server --listen stdio://` and records the ordered protocol transcript for:

- `initialize`
- `thread/start`
- `thread/name/set`
- `turn/start`
- `thread/list`

Visible-session success is granted only after the evidence proves the same thread id, title, cwd, source kind, completed turn, prompt hash, and rollout path. Headless `codex exec` success remains traceable but cannot satisfy visible Codex-App gates.

## Boundaries

- This change implements only the per-session launcher adapter.
- Multi-session orchestration remains outside this change and is handled by `AgentDeliveryVisibleSessionController.cs`.
- Live closeout archive behavior remains outside this change and is handled by `ArchiveVisibleCodexAppSession.cs`.

## Verification

Verification is evidence-first:

- launcher help exposes adapter options,
- app-server protocol availability is checked,
- fixture validation covers positive and negative visible-session evidence,
- a retained smoke launch proves visible app-server evidence,
- `openspec validate agent-delivery-visible-app-launcher-adapter --strict` passes.
