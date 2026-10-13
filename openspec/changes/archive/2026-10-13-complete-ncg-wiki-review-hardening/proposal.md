## Why

The initial NCG review-cursor/completeness/resumption change is committed and archived at main 780e874. This follow-up implements all six subsequently authorized findings in one ticket: lossless large windows, owned-delivery recovery, bounded process/error recovery, a Docs revision checkpoint, efficient proof validation, and a smaller coherent prompt. It preserves the shipped safeguards and the current official checkpoint.

## What Changes

- Preserve the shipped authoritative processed cursor, complete evidence proof and protected resumption. Additive changes extend that contract without replacing the prior completion record.
- Add opt-in lossless bounded resolution of one immutable index snapshot; preserve legacy resolver behavior for other callers and prove all batches before official checkpoint permission.
- Bound subprocesses and permit explicit retries of known failed extraction attempts while preserving protected evidence.
- Persist a separate Docs reviewed tip with Git ancestry/range semantics; keep the four Backend/STS source-tip entries unchanged.
- Track owned delivery and finalize the checkpoint through recoverable, idempotent intent/receipt transitions. Foreign repository changes remain blockers.
- Batch topic proof validation and hash advertised ranges in blocks without weakening integrity checks.
- Replace duplicated prompt mechanics with an ordered contract and canonical references through automation_update. Preserve schedule, target, exact source/reachability gates and main-only delivery. Replace the temporary total-session cap only when verified lossless batch processing is installed.

## Capabilities

### Modified Capabilities

- `recoverable-wiki-review`: bounded full-window resolution, process recovery, Docs revision tracking, owned-delivery/finalization and efficient coherent integration. The general contextual-wiki-operations contract remains unchanged.

## Impact

Existing shared Python resolver and its CLI tests; canonical session-review reference; .NET file-based review/automation support helpers and public-CLI behavior tests; personal NCG automation definition. Existing dirty changes are preserved. The work changes local automation support, not NCG implementation or infrastructure. Verification uses isolated fixtures rather than a complete live wiki update; repository push and archive are outside this implementation request.

On 2026-10-13 Daniel additionally requested a real run in the existing automation
chat, independent result verification and change closeout. That later mandate
adds guarded ncg-docs main delivery and official checkpoint verification before
technical completion and the owning repository's established main delivery/archive.
It does not authorize NCG infrastructure or implementation changes.
