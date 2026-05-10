## ADDED Requirements

### Requirement: Visible app-server launcher adapter

The Agent Delivery Session Launcher SHALL provide an operator-selectable Codex app-server adapter that creates traceable visible Codex-App sessions through the app-server protocol and SHALL preserve the existing `codex exec` path as headless evidence that cannot satisfy visible-session gates.

#### Scenario: App-server launch records visible evidence

- **GIVEN** a valid Agent Delivery handoff and an explicit initiating project cwd
- **WHEN** the launcher runs with `--adapter codex-app-server --mode launch`
- **THEN** it SHALL call `initialize`, `thread/start`, `thread/name/set`, `turn/start`, and `thread/list` through `codex app-server --listen stdio://`
- **AND** `thread/start.cwd` SHALL equal the initiating project cwd
- **AND** evidence SHALL include `execution_channel: app_server`, `adapter_id: codex-app-server`, a SHA-256 prompt hash, the deterministic Agent Delivery title, app-server transcript path, and `session_visibility.class: visible_codex_app_session` only after thread-list proof verifies the same thread id, title, cwd, source kind, completed turn and rollout path.

#### Scenario: Headless launch is downgraded

- **GIVEN** the launcher runs through the legacy `codex exec` adapter
- **WHEN** the process succeeds
- **THEN** evidence SHALL identify `execution_channel: headless_cli`
- **AND** it SHALL NOT report `session_visibility.class: visible_codex_app_session`
- **AND** it SHALL mark the session as traceable but not visible in the Codex App.

#### Scenario: Visible proof rejects false positives

- **GIVEN** app-server evidence with an empty thread, wrong title, wrong cwd, failed turn, prompt hash mismatch, missing app-server, or secret-like prompt content
- **WHEN** S1 launcher evidence validation runs
- **THEN** the case SHALL fail the positive visible-session contract or block before launch
- **AND** no secret-like literal SHALL be persisted in evidence or transcript files.
