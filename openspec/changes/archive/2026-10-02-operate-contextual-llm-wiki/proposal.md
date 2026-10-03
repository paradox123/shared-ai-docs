# Change: Direct Markdown wiki and removal of the obsolete compiler

## Why
The compiler-first import did not complete successfully and created expensive maintenance failures. On 2026-10-02 the user accepted selected direct Markdown maintenance and explicitly requested removal of obsolete implementation and working artifacts.

## What Changes
- Maintain one common curated Markdown wiki with the shared skill and deterministic direct-source helper.
- Use QMD for retrieval and independent daily index maintenance.
- Remove the compiler, entrypoints, dependencies, release scheduler, abandoned plans/tickets, test wikis and obsolete worktrees.
- Preserve useful historical knowledge in a verified backup outside indexed roots; retain concise current guidance and verification.

## Impact
- Replaces contextual-llm-wiki and contextual-wiki-operations requirements.
- Original documents and current QMD runtime/manifest remain authoritative.
- No full import, global queue or automatic content-review guarantee.
