## 1. OpenSpec and Scope Alignment

- [x] 1.1 Finalize scope contract, proposal, design, and spec delta for the metric-gate consistency change.
- [x] 1.2 Define acceptance matrix and implementation evidence structure aligned with spec-only scope.

## 2. Specification Implementation

- [x] 2.1 Patch parent RAG spec to remove any residual ambiguity around `source_precision` and gate authority.
- [x] 2.2 Patch child spec 04 to explicitly classify optional monitoring metrics as non-blocking.
- [x] 2.3 Append required history entries while preserving existing SessionId lines.

## 3. Verification and Closeout Evidence

- [x] 3.1 Execute all planned verification commands for this change with per-command status (`ran`/`failed`/`blocked`).
- [x] 3.2 Capture `check-build-watcher` evidence for NCG build monitoring.
- [x] 3.3 Re-review affected sections and update acceptance matrix + implementation evidence.
