# Acceptance Criteria Matrix

| Acceptance Criterion | Evidence |
|---|---|
| Missing handoff can be generated from a valid Child Index row with `--write`. | Passed: generated fixture command exited `0`, status `written`, and created `tests/sync-child-handoff/fixtures/generated/missing-session-handoff.md`. |
| `--check` exits `0` for current fixture. | Passed: current fixture command exited `0`, status `current`, no findings. |
| `--check` exits `1` with `FIELD_DRIFT` for stale verdict fixture. | Passed: stale verdict fixture command exited `1` with `FIELD_DRIFT` on `Aktueller Verdict`. |
| `--dry-run` prints proposed handoff and does not write. | Passed: SHA before/after matched and output contained proposed `IMPLEMENTATION READY` handoff. |
| `--write` synchronizes controlled fields and preserves manual notes. | Passed: preserve-notes fixture rewrote controlled fields and retained `Manual note that must survive sync`. |
| Approximate write-sets produce blocking `APPROX_WRITE_SET`. | Passed: approximate-write-set fixture command exited `1` with `APPROX_WRITE_SET`. |
| OpenSpec change validates strictly. | Passed: `openspec validate agent-delivery-sync-child-handoff --strict`. |
| `git diff --check` passes. | Passed. |
