# NCG wiki automation prompt template

Render the five named placeholders from the existing private automation configuration;
the template is not an executable prompt. Preserve scheduler/target/notification fields.
The personal rendered prompt and its receipt stay outside shared Git files.

Keep the NCG wiki up to date from bounded Codex history and authoritative Git changes. Complete the full review, any required main-only docs delivery and the official checkpoint; a partial pass is not success.

Automation ID: keep-ncg-wiki-current
Automation memory: $CODEX_HOME/automations/keep-ncg-wiki-current/memory.md
Resolve CODEX_HOME as ${CODEX_HOME:-$HOME/.codex} at the start of every separate shell touching Codex state. Never assume shell variables survive another tool call.

Canonical workflow owner:
{{shared_ai_docs}}/skills-repo/skills/improve-skills/scripts/wiki-review-run/NCG-Automation.md
Request schemas:
{{shared_ai_docs}}/skills-repo/skills/improve-skills/scripts/wiki-review-run/README.md
Read and follow these two files; they are the explicit bootstrap README exception. Mandatory user/repository startup has precedence. Do not duplicate their parser, snapshot, completeness or delivery mechanics in inline scripts.

Run helpers from {{shared_ai_docs}} so SDK10 global.json applies:
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRun.cs -- <command> --request <protected-json-file>
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiDelivery.cs -- <command> --request <protected-json-file>
These are the canonical executable paths; use only their documented commands and validated returned schemas.

Configured repository candidates:
- Backend: {{backend_root}}
- STS: {{sts_root}}
- Docs/wiki: {{ncg_docs}}
After validated selection, resolve each exact Git root and use the returned roots plus basenames backend, ncg-security-token and ncg-docs as the one stable scope. The non-Git backend parent and title-only rows are not scope evidence.

Ordered execution:
1. Perform the contract's definition / bounded first-last memory / bounded index-tail bootstrap. The current-header valid Processed window end is the sole cutoff; malformed/ambiguous present state blocks. Scheduler or completion time never extends it. Require nonempty current CODEX_THREAD_ID directly; do not rediscover it from env dumps, titles or rollouts.
2. Use ReviewRun capture with batch_size:100, max_sessions:100, timeout_seconds:120 and max_output_bytes:16777216, private request files, canonical resolver and resolved state paths. Pass approved_missing_carry_ids:["{{approved_deleted_carry_id}}"] only for the previously approved deleted carry. Keep prompt_last_run empty whenever Processed is present. Reuse the exact returned run_directory/receipts. Follow resolve-batch next offsets until a terminal validated extraction_allowed:true aggregate. One live-index capture; completed batches are reused. The total window has no 100/500-session cap in this opt-in flow. Never rerun the resolver directly, refresh the live index or prune any other unsafe case.
3. Load the canonical ncg-documentation skill at {{ncg_docs}}/.agents/skills/ncg-documentation/SKILL.md before session projection or repository/QMD/docs work. If unavailable, report that once. Complete bounded page chains and verify-pages, retaining valid clone decisions and using exact clone follow-up only for unresolved manual blockers. QMD is the existing retrieval engine; skill-defined targeted rg fallback only. No legacy RAG repair/index maintenance or raw-history reader.
4. Use NcgWikiDelivery verify-sources and fully page both git-history and docs-history, including empty terminal pages. Backend/STS evidence is restricted to exact origin/develop and origin/production; docs history is exact origin/main. Preserve four-code-pin ancestry, combined newly-reachable ranges, migration-no-code-backfill, reachability and final-pin checks. Inspect implementation only through pinned Git objects; never checked-out code, feature/main/all-ref fallbacks or session claims. A production branch is not a deployment/runtime proof. Separate Docs reviewed tip uses ancestry/SHA history with explicit first-baseline review.
5. Account for every selected session and authorized Git candidate. Inspect/compare relevant eligible work with existing wiki/docs, including Git-only changes. Skip wiki comparison only when both completed passes yield no relevant eligible work. Use bound topics-batch or individual topic receipts; unchanged contexts may be reused. Unproven discovery is a terminal no-claim, not implementation evidence. A relevant unchecked/unresolved candidate or pending required delivery blocks completion.
6. Use plan-delivery to retain desired Markdown and exact ownership BEFORE edits. Resume its named plan pointer after interruption. delivery-status alone gates applying remaining intended files, scoped docs commit on main and push origin main. Run diff --check and inspect the scoped diff. Require the clean aligned main guard before a new edit; recover only exact planned own work. Wrong branch, unrelated edits/commits, rewritten history or changed code pins block without switch/reset/stash/amend/pull/rebase/force-push. Already delivered work is not pushed again.
7. finalize is the sole official bundle writer/retirement path. Omit caller new_checkpoint so values are derived. It requires full current proof, dispositions and actual required delivery; old/new intent recovery is narrow and idempotent. Never patch memory manually, advance after a partial Git pass or fabricate delivery. Use the same store lock for failure-note memory writes; prefer existing protected diagnostics. Keep Last review/Run time separate from Processed. A failed required step leaves the official bundle unchanged. Preserve protected evidence.

NCG production 10.1.0.0/16 and development 10.0.0.0/16, including CI/registry/management/public URLs, remain read-only. This automation does not authorize system changes. Local protected evidence and the narrowly guarded docs delivery are its permitted writes.

Final report in German, one prominent status banner on its own line:
✅ NCG-WIKI-LAUF ERFOLGREICH
✅ NCG-WIKI-LAUF ERFOLGREICH – KEINE ÄNDERUNG NÖTIG
❌ NCG-WIKI-LAUF FEHLGESCHLAGEN – BLOCKER: <short reason>
Briefly state loaded skill/lookup method, fully reviewed scope and source pins, candidate dispositions, changed files, actual delivery/checkpoint status and concrete remaining gaps. Do not equate captured receipts, Git inspection or QMD freshness with complete wiki review or deployed/runtime behavior.
