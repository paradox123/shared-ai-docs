# Generated command messages

Routine command messages now come from `batch_state.py coordinate` using the phase text in [phase-messages.json](../assets/phase-messages.json). Use the returned immutable packet's `message`; supply only the task-specific instruction and inspected decision evidence. See [local-helpers.md](local-helpers.md). Do not load all phase templates into the model or recreate their common headers manually.

For an authorized recovery heartbeat, reference the absolute skill and ledger paths, frozen batch and explicit target. Request one compact `status` plus scoped live observation/reconciliation, processing actionable events and eligible work. End quietly if unchanged; do not start a repeated wait loop. Preserve notification settings. Pause only this heartbeat after verified batch delivery, closeout and cleanup. Configure it through build-codex-automations and the current automation tool.
