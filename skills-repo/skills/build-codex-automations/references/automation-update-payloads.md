# Codex App `automation_update` Payloads

Use these shapes when the Codex app exposes `automation_update`. They are verified for viewing and updating an existing cron automation. Read the current definition first and preserve every field the user did not ask to change.

## View

```json
{
  "mode": "view",
  "id": "<automation-id>"
}
```

Use `mode`, not `action`.

## Update An Existing Cron Automation

```json
{
  "mode": "update",
  "kind": "cron",
  "id": "<automation-id>",
  "name": "<name>",
  "prompt": "<complete prompt>",
  "status": "ACTIVE",
  "rrule": "<rrule>",
  "model": "<model>",
  "reasoningEffort": "<effort>",
  "executionEnvironment": "<environment>",
  "projectId": "<project-id>"
}
```

Rules:

- Send the complete required update object, not only the changed field.
- Use camelCase for `reasoningEffort`, `executionEnvironment`, and `projectId`.
- Keep `projectId` flat. Do not send TOML-shaped `target`, `cwds`, `reasoning_effort`, or `execution_environment` fields to this app tool.
- Keep schedule syntax internal; do not expose a raw RRULE to the user.
- Do not extrapolate this cron shape to heartbeat automations. Use the active tool contract for a heartbeat.
- If the tool rejects a previously verified shape, read the returned validation error or active tool declaration once and update this reference. Do not cycle through `action`/`mode`, snake_case/camelCase, or nested/flat guesses.
