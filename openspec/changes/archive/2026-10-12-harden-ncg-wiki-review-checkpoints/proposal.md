## Why

The NCG wiki automation can select a later completion timestamp than its actual processed window, can treat a capped extraction as complete, and loses reusable review work after a model interruption. The user authorized review improvements 1–3 on 2026-10-12.

## What Changes

- **BREAKING**: an existing valid Processed window end becomes the sole authoritative session cutoff; newer completion/scheduler timestamps cannot replace it. Malformed present processed cursors fail closed; explicit legacy sources apply only when the processed cursor is absent.
- Require a deterministic same-manifest, fully accounted extraction receipt before checkpoint advancement, including pagination, zero output omissions and resolution of manual clone work.
- Persist the original index/manifest and topic review receipts outside the automation memory directory; resume only when memory, selection, source pins and reviewed wiki inputs still match. The final cursor remains unchanged until the full review finishes.
- Update the existing keep-ncg-wiki-current prompt through automation_update, preserving schedule, target, temporary 500 limit, source/reachability, migration and documentation delivery guards.

## Capabilities

### New Capabilities

- `recoverable-wiki-review`: explicit processed cursor, complete extraction proof, and protected bounded review resumption.

### Modified Capabilities

None. contextual-wiki-operations governs selected LLM-wiki content maintenance; this change governs the NCG Codex history review/checkpoint orchestration.

## Impact

Existing shared Python resolver and its CLI tests; canonical session-review reference; a small .NET file-based local receipt/resumption helper and behavior tests; personal NCG automation definition. Existing dirty changes are preserved. No NCG implementation or operational changes, no complete live wiki run, no Git push or archive. Points 4–6 of the review remain outside this implementation.
