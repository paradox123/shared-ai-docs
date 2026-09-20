# Token-efficient ticket batches

Status: implemented locally and verified on 2026-09-18; see token-efficiency-verification.md. The bounded implementation assumption is local mechanical helpers only. A larger execution engine was offered as an optional scope expansion and was not selected. No new runtime authority is introduced.

The later [completion-contract-design.md](completion-contract-design.md) supersedes the review ownership, acceptance timing and former Standards/Spec roles described below. This document and its original evidence retain the first token-efficiency implementation baseline.

## Source and scope

The supplied analysis describes `Wiki-Maintenance-Tickets implement` (`01a0af21-127f-7833-b0c1-136e653dc476`). The user also linked `Ticket 8 bearbeiten und mergen` (`01a0af3f-b5ba-7d80-8fcb-514121c60182`). These are distinct tasks; the reported token counts are not attributed to the latter. The requested seven recommendations, rather than an unverified cost estimate, define this extension.

Continue the existing change and shared skill. Preserve explicit target selection, isolated worktrees, independent review, acceptance evidence, serialized merge, pending-action recovery and guarded cleanup. Do not modify the application pilots, existing live batches, vendor skills or global model defaults.

## Decisions and implementation assumptions

1. Implementation → separate critical verification and repairs → independent Standards/Spec review → focused repairs and reviewer follow-up → final relevant full suite → acceptance and integration. Local commits on the owned branch are checkpoints, not delivery authority.
2. Review records preserve base/head or manifest, reviewer identity, requirement coverage, findings and disposition. Reuse the same reviewers for deltas; broaden only with a concrete reason. A final record identifies current contents and retained earlier coverage.
3. A Python standard-library CLI performs local JSON checkpoints, meaningful snapshot comparison, assignment comparison, SHA-256 manifests and non-overwriting evidence copies. Codex still calls task/Git/automation tools and makes scheduling, acceptance and cleanup decisions. No database or new workflow engine is needed.
4. Use revision-checked atomic writes under an exclusive local lock. An interrupted lock is an explicit blocker requiring inspection, not an excuse to overwrite another writer. Existing Markdown/arbitrary JSON ledgers require explicit adoption preserving all known facts and uncertain actions.
5. Record delivered ticket facts immediately; collect pure versioned status/archival work into one batch closeout change. Per-ticket activation evidence and repository-required pre-merge docs remain required. A blocked batch may flush a clearly labelled partial closeout.
6. Workers and reviewers receive self-contained scoped packets; subagents use fresh context. Default role profile: Sol/medium coordination and Standards; Astra/high implementation, critical verification and Spec. Honor explicit user choices and runtime model restrictions. A skill cannot itself change its running coordinator's model: report the mismatch once and continue authorized work.
7. Establish semantically valid fixtures during implementation, use narrow checks during repair, and run the relevant full suite on final repaired contents. Later substantive or integration changes require affected revalidation; required CI remains.

## Verification and limits

Test the public CLI using temporary files and subprocesses, including repeated unchanged observations, stale writers, identity mismatches, missing/tampered artifacts and retention conflicts. Forward-test instructions with realistic worker results, then perform independent Standards/Spec review. No live batch, merge or productive activation is launched solely to evaluate this skill. A comparable future real batch is needed to measure token savings and model-quality effects; no percentage is promised.
