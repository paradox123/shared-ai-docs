## Context

The personal keep-ncg-wiki-current definition lives outside Git. Shared resolver and session-review guidance are in shared-ai-docs, currently main with pre-existing dirty changes. Existing resolver replay/pagination features from those changes must survive. This implementation adds only authorized review improvements 1–3.

## Goals / Non-Goals

Goals: remove the completion-time cutoff gap; provide deterministic evidence completeness; retain immutable selection and reusable topic comparisons across model interruption. Use the actual public CLIs for local behavior verification.

Non-goals: change the 100/500 limits, implement new Git work batching or a Docs-history cursor, relax source or delivery gates, execute a live wiki update, migrate existing Python tools, push or archive.

## Decisions

- Keep the existing Python resolver interface and tests; correct its cursor contract in place and in the canonical reference. The existing runtime is a concrete reason to retain Python for that fix.
- Use a .NET file-based app with only standard libraries for the new local run/receipt commands. Group each CLI use case and validation together. Existing repository global.json selects SDK 10.0.203; automation calls run from shared-ai-docs so ambient ncg/Vault SDK configuration cannot select an older SDK.
- Store immutable run input/output files and topic receipts under resolved Codex home automation-runs/keep-ncg-wiki-current, outside the automation definition/memory directory. Preserve the full original memory snapshot, but compare current reuse through the official processed/carry/source-tip bundle, so failure prose and Run time do not discard useful work. Private permissions, input digests and atomic local file replacement protect evidence. Active selection is adopted only if matching; changed authoritative input never reuses an old decision silently.
- The completeness validator consumes persisted extractor output with explicit immutable-manifest/scope binding and verifies the entire selected page sequence, counts/IDs, omissions and manual-resolution evidence. A blocked proof never writes the official memory.
- Topic cache receipts are provisional comparisons. Docs-origin/main candidates have a separate optional documentation pin bound to the scoped docs root; it is topic context only and does not add a Docs-history cursor or extend the official four-code-tip map. Original source reachability and final source-pin equality are still checked; required edits must be successfully delivered under the existing rules before the official atomic checkpoint advances.
- Existing work on main is snapshotted and modified only with scoped patches. No branch switch, destructive reset, delivery commit or push is part of this request. The intended later repository delivery target remains its original main context, subject to acceptance/closeout.

## Risks / Trade-offs

- Shared cutoff semantics affect other consumers → preserve explicit legacy fallback when no processed cursor exists, identify it in output, and test malformed present cursor.
- Cached evidence becomes stale → exact manifest/memory/definition/source/wiki digests gate reuse; incomplete receipts remain unusable.
- Model may stop anywhere → captured output is persisted before its result is emitted; final memory is never advanced by capture or topic-cache commands.
- Prompt instructions still own semantic wiki decisions and external delivery → cache success alone never claims domain correctness or successful publication.

## Migration Plan

Install helper/tests and shared cursor correction before updating the personal prompt. Preserve current memory bytes: the corrected selection starts at its already recorded Processed window end and naturally includes the potential 52-minute gap on the next review. Do not claim that gap or the complete backlog has now been reviewed. Keep implementation evidence separate from runtime selection files. If prompt integration cannot be validated, restore its saved definition without changing memory.
