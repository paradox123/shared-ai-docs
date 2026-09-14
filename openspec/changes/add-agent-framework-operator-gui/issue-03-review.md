# Ticket 03 — two-axis code review

Baseline `dded7d4`, implementation `f6f006e`, branch
`codex/operator-gui-issue-03`. The `code-review` skill dispatched independent
Standards and Spec reviewers. Reports are kept separate below.

## Standards

No hard documented-standard breaches found.

**P2 — Judgment call: possible Primitive Obsession at the SSE boundary.**
`workflow-view.js` tested the entire raw frame with
`frame.includes('event: access-revoked')`. A legitimate run-event containing
that phrase in a recorded message/tool result fabricated a 403, disconnected
the browser and cleared evidence. The reviewer reproduced this against the
production module with a controlled stream. Parse the actual `event:` field;
payload text remains data.

No additional actionable DRY/SOLID/KISS findings.

**Correction:** the production parser now compares only the exact `event:` field
and ingests data only for `run-event`. The public API/restart browser test retains
an assistant message containing the literal phrase while access remains granted.
It failed with premature disconnection, then passed with the real content shown.
The same test subsequently revokes actual provider rights and verifies clearing.

## Spec

**P2 — Refresh the projection after page catch-up and failed refreshes.**
History pages advanced the cursor without refreshing the graph/artifact manifest;
only new SSE events scheduled refresh. Completion between initial projection and
history read left the graph running because the live tail only had heartbeats.
Similarly, a failed final refresh was never retried after reconnect. Both were
reproduced in Chrome against the production module. Requirement: display actual
workflow progress and preserve correlation across reload/API restart.

No additional scope-creep or confirmed filter/access-revocation/artifact-correlation
findings. The suspected result-filter problem did not reproduce: canonical
`AgentResultObserved` has `payload.type: result`.

**Correction:** page catch-up schedules projection refresh when the committed
position is ahead. A single pending refresh retries failures and coalesces new
events until the graph catches up. Pending reconciliation remains visible.
The added public browser test holds an actual running projection response while
the worker finishes, then delivers final history and injects one temporary 503
for the completed projection. The initial implementation left the graph running;
the corrected client retries even without later events.

## Final verification

Both independent reviewers rechecked `f6f006e...eacce49` and nearby context.
Standards confirmed the exact SSE-field correction and found no remaining
standard or DRY/SOLID/KISS issues. Spec reran both original Chrome reproductions
and confirmed recovery without later events, plus normal handling of the literal
control phrase in content. **Remaining findings: Standards 0; Spec 0.**

Five public Chrome tests passed after correction in 39.877 seconds. The real
GitHub/Codex two-browser and API-replacement proof was repeated successfully at
`eacce49` in 135.909 seconds. Full discovery passed: 223 tests, 198 passed, 25 optional tests skipped, no failures
(939.937 seconds). The additional page-catchup race case, added after discovery
started, passed in the separate five-case focused run. Relevant real integrations
were explicitly enabled and passed separately. See [acceptance evidence](issue-03-evidence.md).
