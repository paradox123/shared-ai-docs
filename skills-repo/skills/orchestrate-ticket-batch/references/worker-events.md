# Worker reports

Use the generated command packet from your coordinator. It contains the assigned phase, request identity, target, coordinator, report directory and reserved subagent allowance. Follow its instruction and phase limits; it conveys the original authority, never new user consent.

At readiness or a changed blocker/error, write a concise result: current contents, measured expected/actual behavior, evidence links, changed scope, limitations and the needed decision. Link detailed logs. For integration, include candidate and actually tested target. For delivery, include remote merge and content mapping, closure and running processes. Large repetitive tasks should prove representative complete examples before broad replication.

Run the supplied skill's `scripts/batch_state.py report` with `--packet`, `--result`, `--status ready|blocked|error`, and `--content-ref` for ready. Ready integration/delivery reports also require `--target-ref`. The CLI allocates the sequence, copies the result and returns a durable event path plus a `callback` object for `send_message_to_thread`. All packet/report paths must be accessible on the participating hosts.

Send that callback once. For a transport retry reuse the existing callback/event; do not run report again merely to resend. A new report command denotes a new result. No periodic progress callbacks or acknowledgement loops. A denied/unavailable callback leaves the files for recovery: mention the limitation in your normal final result, do not evade denial or launch a substitute task.

After ready, make no further candidate changes until a new instruction. Report active processes; readiness alone does not prove quiescence. Registration precedes a bound worker packet: report real identity/worktree/base through the normal task result, never guess IDs. The coordinator verifies registration directly.
