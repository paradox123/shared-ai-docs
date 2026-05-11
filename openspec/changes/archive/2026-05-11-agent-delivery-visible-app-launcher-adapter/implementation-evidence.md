# Implementation Evidence

## Scope

Implemented the `ADV-CAS-S1` Launcher visible app-server adapter contract.

## Changed Behavior

- `AgentDeliverySessionLauncher.cs` now writes `agent-delivery.session-launch.v2` evidence.
- `--adapter codex-app-server` records `execution_channel: app_server`, derives the `ADV-CAS-1: Implementation - ADV-CAS-S1 Launcher Visible-App Adapter` title, uses the initiating project cwd for `thread/start`, and retains an app-server transcript path.
- `--adapter codex-exec` remains available and records `execution_channel: headless_cli` with a non-visible `headless_cli_session` visibility class.
- S1-local fixture validation covers app-server positive shape, headless downgrade, empty thread, wrong title, wrong cwd, failed turn, prompt hash mismatch, app-server unavailable, and secret redaction.

## Verification

| Command | Status | Evidence |
|---|---|---|
| `cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- --index /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-10\ Agent\ Delivery\ Visible\ Codex\ App\ Sessions\ Orchestration\ Pack.md --child ADV-CAS-S1 --handoff /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/adv-cas-s1-session-handoff.md` | pass | Child readiness validation passed for `ADV-CAS-S1`. |
| `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help` | pass | Help lists `--adapter codex-app-server`, `--initiating-project-cwd`, and app-server timeout options. |
| `codex app-server --help` | pass | App-server command and `--listen stdio://` option are available. |
| `codex app-server generate-ts --out /tmp/codex-app-schema-adv-cas-s1` | pass | TypeScript protocol schema generated. |
| canonical S1 JSON example parse | pass | Embedded canonical JSON block parsed successfully. |
| `openspec validate agent-delivery-visible-app-launcher-adapter --strict` | pass | OpenSpec ledger validates. |
| `node tests/docworkflow-agent-delivery/e2e/validators/visible-app-launcher-s1.js tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-launcher-s1` | pass | All 9 S1 launcher fixture cases passed. |
| `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --handoff _specs/agent-delivery-session-launches/adv-cas-s1-visible-smoke-handoff.md --target-id ADV-CAS-S1 --mode launch --adapter codex-app-server --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs --out _specs/agent-delivery-session-launches --app-server-timeout-minutes 5` | pass | `_specs/agent-delivery-session-launches/20260510T081130Z-adv-cas-s1/evidence.json` reports `visible_codex_app_session` with matching cwd/title and completed turn. |
| `git diff --check` | pass | Patch whitespace clean. |

## Retained Evidence

- S1 fixture validator: `tests/docworkflow-agent-delivery/e2e/validators/visible-app-launcher-s1.js`
- S1 fixtures: `tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-launcher-s1/`
- Generated protocol rehearsal: `/tmp/codex-app-schema-adv-cas-s1`
- Visible app-server smoke: `_specs/agent-delivery-session-launches/20260510T081130Z-adv-cas-s1/evidence.json`
- Visible app-server transcript: `_specs/agent-delivery-session-launches/20260510T081130Z-adv-cas-s1/app-server-transcript.jsonl`
