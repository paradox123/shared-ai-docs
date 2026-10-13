## Context

The personal keep-ncg-wiki-current definition lives outside Git. The original three improvements are now committed and archived at shared-ai-docs main 780e874. This distinct follow-up covers all six subsequent findings in one implementation ticket. Preserve the shipped baseline, earlier follow-up edits and unrelated dirty work.

## Goals / Non-Goals

Goals: remove the completion-time cutoff gap; prove evidence completeness; retain review comparisons across interruption; process large windows losslessly with bounded operations; recover owned failed deliveries; persist an exact Docs checkpoint; make failures bounded and retryable; reduce repeated proof work and prompt duplication. Use the actual public CLIs for behavior verification.

Non-goals: relax exact source or main-only delivery gates, execute a live wiki update during implementation validation, migrate existing Python readers, change scheduler/target/model settings, write to NCG infrastructure, push this implementation or archive the change.

## Decisions

- Keep the existing Python resolver interface and tests; correct its cursor contract in place and in the canonical reference. The existing runtime is a concrete reason to retain Python for that fix.
- Use a .NET file-based app with only standard libraries for the new local run/receipt commands. Group each CLI use case and validation together. Existing repository global.json selects SDK 10.0.203; automation calls run from shared-ai-docs so ambient ncg/Vault SDK configuration cannot select an older SDK.
- Store immutable run input/output files and topic receipts under resolved Codex home automation-runs/keep-ncg-wiki-current, outside the automation definition/memory directory. Preserve the full original memory snapshot, but compare current reuse through the official processed/carry/source-tip bundle, so failure prose and Run time do not discard useful work. Private permissions, input digests and atomic local file replacement protect evidence. Active selection is adopted only if matching; changed authoritative input never reuses an old decision silently.
- The completeness validator consumes persisted extractor output with explicit immutable-manifest/scope binding and verifies the entire selected page sequence, counts/IDs, omissions and manual-resolution evidence. A blocked proof never writes the official memory.
- Topic receipts remain provisional comparisons. Docs-origin/main candidates retain a separate documentation pin. Add a separate Docs reviewed tip to the official completion bundle, never a fifth entry to the four-code-tip map. Original reachability and final source-pin equality are still checked; required edits must be successfully delivered before the bundle advances.
- Existing work on main is snapshotted and modified only with scoped patches. No branch switch, destructive reset, delivery commit or push is part of this request. The intended later repository delivery target remains its original main context, subject to acceptance/closeout.

## Follow-up design assumptions

The six reviewed findings define scope and failure policy. The grilling exit audit finds no unresolved product/safety choice; internal parameters can be settled during implementation. Daniel explicitly requested a single combined implementation ticket in the same session; that ticket inherits the complete mandate and no further breakdown gate remains.

- Python remains the existing index/rollout reader. Add only an opt-in bounded selection-slice contract; .NET owns capture, progress and proof. This parser/runtime binding justifies retaining Python for that extension. New orchestration uses C#/.NET vertical slices and file-based apps where practical.
- Capture the live index once. Later resolver operations replay only verified original bytes with original memory, exclusion, cutoff and ceiling. Prove contiguous complete selection identity before publishing an aggregate manifest. Successful batches are reused. Legacy resolver callers retain their total-limit behavior.
- Timeout/cancellation terminates owned descendants, retains protected diagnostics and returns non-success. Explicit retry supersedes only a known failed attempt with unchanged bindings. Corrupt evidence, changed source ranges and unapproved unsafe conditions remain blockers.
- Docs reviewed tip joins checkpoint identity/completion separately from the four code pins. Validate prior-tip ancestry and SHA ranges. On first use, do not call the current tip reviewed or derive a baseline from dates: use a provable accepted revision, otherwise inspect pinned main history in bounded packages before establishing the first reviewed tip. Preserve the existing code-source migration exception.
- Before edits, retain desired Markdown in private run storage with docs base SHA, exact owned paths/base and intended hashes, and comparison receipt identities. Reconcile only exact own edits/commit/delivery. Foreign changes, wrong branch, rewritten history or changed authoritative pins block without reset/stash/amend/pull/rebase. Validate unchanged comparisons against pinned docs objects; validate delivered topics against their owned committed post-edit content.
- Keep generic review receipts separate from NCG-specific Git/delivery orchestration. Only the latter may collect exact allowed ref proofs; guarded Git writes retain the automation's explicit target/action authority. No broad Git/network mutation capability is added silently to the generic helper.
- Prepare a protected finalization intent before memory changes. Compare-and-swap the expected completion bundle. Narrow recovery accepts only its exact old or intended new bundle, then completes terminal receipt and active retirement idempotently. Normal review-load validation stays strict.
- Batch bounded topic operations validate one current completeness proof. Blockwise hashing preserves exact advertised-byte/line boundaries and append-only semantics. Measure the effect on a repeatable fixture; claim no unmeasured speedup.
- The prompt becomes an ordered project contract linking tested canonical mechanics. Explicitly allow the required helper README during bootstrap. Preserve Git-only comparisons, exact source refs, approved deleted carry, privacy, complete disposition and delivery rules. Install lossless batches before replacing the temporary total-cap override.

## Verification seams

Use the existing resolver and .NET request/response CLI with private synthetic sessions and local bare Git remotes. Prove normal/empty, timeout/owned-descendant, failed page/retry, interrupted batch, corrupt snapshot, old-dated newly reachable docs commit, own failed push/recovery, foreign edit and interrupted finalization cases. Use separate processes for restart. No live NCG fetch, wiki edit, commit/push or checkpoint advancement is needed for implementation validation.

## Risks / Trade-offs

- Shared cutoff semantics affect other consumers → preserve explicit legacy fallback when no processed cursor exists, identify it in output, and test malformed present cursor.
- Cached evidence becomes stale → exact manifest/memory/definition/source/wiki digests gate reuse; incomplete receipts remain unusable.
- Model may stop anywhere → captured output is persisted before its result is emitted; final memory is never advanced by capture or topic-cache commands.
- Prompt instructions still own semantic wiki decisions and external delivery → cache success alone never claims domain correctness or successful publication.

## Migration Plan

Install helper/tests and shared cursor correction before updating the personal prompt. Preserve current memory bytes: the corrected selection starts at its already recorded Processed window end and naturally includes the potential 52-minute gap on the next review. Do not claim that gap or the complete backlog has now been reviewed. Keep implementation evidence separate from runtime selection files. If prompt integration cannot be validated, restore its saved definition without changing memory.
