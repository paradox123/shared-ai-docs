# NCG wiki review contract

This is the ordered contract for the personal NCG wiki automation. General
request schemas are in [README.md](README.md). The automation supplies its
explicit three repository roots and canonical helper paths; this document adds
no shared personal-path policy. Ordinary wiki maintenance and QMD index upkeep
retain their existing owners.

## Entrypoints and effects

Run from the owning shared-ai-docs Git root so its SDK10 global.json applies:

```bash
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRun.cs -- capture --request /private/capture.json
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiDelivery.cs -- verify-sources --request /private/sources.json
```

Replace the command/request with the use case below. Request directories are
0700; JSON files are 0600. Pass the actual canonical, symlink-free request path.
On macOS, mktemp may return a /var path whose existing file is under /private/var;
resolve that path before invoking NcgWikiDelivery. Keep the same request contents
and captured run; a rejected alias does not authorize recapture or weaker checks.
Keep returned named paths and receipt hashes across
tool yields. Do not scan state/temp roots to guess the latest run. New state and
desired Markdown remain in the protected run store outside the automation
definition/memory folders. Existing Python readers and .NET standard libraries
are the dependencies; a tiny existing-interpreter startup shim gives owned
subprocesses a separate Unix process group for bounded termination.

ReviewRun captures/resolves/extracts and writes local review receipts. It does
not use Git, change official memory or edit source/wiki files. NcgWikiDelivery
uses fixed read-only Git commands and exact allowed fetches, writes protected
delivery/finalization receipts and, only through finalize, replaces official
memory and retires the matching active pointer. prepare-workspace creates a
private run-owned independent docs checkout on main from the same verified
origin. It never changes the normal checkout's index, files or stashes.
Explicit protect-worktree and
restore-worktree requests also protect and restore the bound local docs worktree
and index. Fetch changes local remote refs; neither helper authors docs, commits,
pushes, resets, cleans, amends, pulls or rebases. The automation retains its
narrowly guarded docs edit/commit/push actions. Protection is explicit; other
callers retain the strict dirty-worktree gates. NCG production/development and
their management paths remain read-only.

## 1. Bootstrap and immutable selection

Honor mandatory user/repository startup first. For each separate shell touching
Codex state, redeclare CODEX_HOME_RESOLVED from CODEX_HOME or HOME/.codex. Read
the current definition, a first/last memory excerpt with an omission marker
included in the 16000-character cap, then the bounded 120-line index tail.
These displayed excerpts never supply the watermark. The canonical helper
README and this contract are explicitly permitted before capture; unrelated
repository/QMD sweeps wait until validated selection.

Processed window end in the current memory header is the sole cutoff. Invalid,
empty or ambiguous present state blocks. Last review or a trusted prompt boundary
is a visible legacy fallback only when Processed is absent. Require the actual
nonempty CODEX_THREAD_ID; never infer it from titles or print environment dumps.

Use capture with batch_size100, max_sessions100, timeout_seconds120 and
max_output_bytes16777216, and missing_session_policy:"ignore". Daniel authorizes
the NCG automation to treat missing sessions as deleted and irrelevant without
per-ID approval: only missing/path:null rows without storage metadata and with
matching missing_rollout diagnostics qualify, whether selected by the window,
carry-forward or both. Report ignored_missing_session_ids and preserve raw
resolver exit/safety evidence. Ambiguous, unreadable, malformed, incomplete,
changed or corrupt evidence and other unsafe diagnostics still block. The policy
is identity-bound; do not change it inside a captured run. The prompt_last_run
value is empty when Processed exists. Repeat an unchanged capture request to
adopt its original selection.
One live index read captures exact bytes. A resolving result supplies next_offset;
resolve-batch processes that next slice from those bytes only. Repeating a
successful offset reuses it. Never run the resolver separately or refresh the
index to repair context. Require a terminal captured/resumed result with
extraction_allowed true before further evidence work. No partial batch permits
checkpoint advancement, even though its data may be readable.

An already captured run binds definition, tools, official checkpoint and original
exclusion. Changed authoritative inputs or corrupt evidence block adoption.
Explicitly invalidate only a confirmed stale named run with a concrete reason;
preserve its receipts and official checkpoint. An old pre-batch capture cannot
be silently converted into a new capture. A new task ID is a changed exclusion;
the normal daily heartbeat keeps its original target chat.

## 2. Complete scoped evidence

Load the canonical ncg-documentation skill, then resolve the three configured Git
roots with rev-parse --show-toplevel. Keep that one scope's concrete roots and
worktree basenames; a non-Git parent or title alone cannot enter it. QMD remains
the documentation retrieval engine, with targeted rg only under the skill's
existing failure/exact-term fallback. No legacy RAG store or index maintenance.

Use page from offset0, limit12, max_total_chars20000. Read each bounded output.
If projections were omitted, retry the same offset with smaller limits; otherwise
follow next_offset through the explicit terminal page, including an empty scope.
verify-pages must return complete, receipt and receipt_sha256. It proves the
whole same-manifest scope and validates stored clone resolutions. Only a concrete
unresolved_manual_clone result requires resolve-clone with actual exact
boundary/structural/suffix evidence. Do not regenerate valid clone decisions.

Known process failures retain their protected stdout/stderr/exit and named
failed-attempt receipt. Retry explicitly with retry_failed true only on unchanged
bindings; stop/report if the bounded retry fails. A corrupt successful output,
changed source bytes or other semantic unsafe resolver result is not a retry
excuse. Missing rows follow the bound capture policy, without per-ID approval
under ignore. Smaller output pages are still the same selection.

## 3. Authoritative Git sources and revision history

Use NcgWikiDelivery verify-sources with the bound review_request and concrete
repositories map. It runs only these source fetches and requires every command
and exact ref to succeed:

- Backend/STS: refs/remotes/origin/develop and refs/remotes/origin/production,
  fetched with quiet/no-tags/no-write-fetch-head and exact heads/refspecs.
- Docs: refs/remotes/origin/main, fetched only from the exact main head.

The four code tips remain exactly four repository|ref entries. Set
allow_source_advancement:true in this automation's verify-sources request.
Prior tips must
be ancestors; code candidates are the deduplicated per-repository union newly
reachable from both new tips excluding both old tips. The original missing-code-
baseline exception establishes four tips only, without code-derived backfill.
No HEAD/main/originHEAD/feature/tag/reflog/stash/all-ref fallback is permitted for
Backend/STS evidence. A production ref alone does not prove deployment/runtime.

Read git-history and docs-history from offset0 with limit100 through has_more
false. Even an empty range has a real terminal page. The protected source receipt
retains exact pins/ranges; stdout contains bounded discovery/metadata. Docs
review uses its separate Docs reviewed tip repository/ref/SHA, prior ancestry and
SHA range. Missing first state requires bounded pinned-main history review before
establishing a baseline, not a date-filter shortcut or automatic current-tip
acceptance. Invalid/missing/replaced history blocks reconciliation.

Inspect candidates only through Git objects rooted at validated candidate SHAs;
inspect delivered first-parent deltas for merges. Before use and again before
edits, prove reachability to the exact pinned allowed source tip. Do not read
Backend/STS checked-out files as implementation evidence. Session narratives are
discovery only; rederive Backend/STS facts from allowed Git objects. Neither a
session claim nor an uncommitted/feature SHA substantiates a docs update.

After verify-sources and both complete history chains, call prepare-workspace
with the common input and exact source_receipt/source_receipt_sha256. Retain its
workspace receipt and returned main checkout. Use this isolated checkout for
this automation's actual docs edits/commit/push. Keep the configured original
docs root as the review/Docs-checkpoint identity and QMD source. Existing changes
or concurrent work in that normal checkout are not delivery blockers and MUST
remain untouched. No feature branch is created. Compare wiki inputs against
pinned main blobs, not uncommitted local text. Use the owned workspace's physical
wiki paths in topic receipts after canonical
QMD routing; the delivery helper maps them to repository-relative pinned blobs.
The original dirty wiki page is not a comparison snapshot. Existing protect-worktree and
restore-worktree remain available for an intentionally in-place delivery, but
are not required when the isolated flow never moved prior work. Retain any older
protected stash/journal as a safety backup; never blindly reapply it over newer
user work.

Keep the named protection journal across interruptions. It binds run, repository,
base, helper and raw snapshots; an unchanged request resumes the same operation.
Literal tracked bytes/modes and staged Git-tree identities are retained. Unsupported
filter/EOL/mode conversions or changing ignore/attribute files block before stash
mutation. Git-excluded special entries remain untouched rather than being read.
Never guess stash@{0}, adopt a foreign stash or create a second stash to recover
an uncertain first attempt. Protection is not an evidence source for Backend/STS.

## 4. Compare every candidate and record the delivery intent

Both session and Git passes must finish before a skip/no-change decision. For
every selected session and authorized Git candidate record a concrete reason and
one disposition: irrelevant, unproven discovery, already_covered or update_needed.
An unproven discovery statement is a terminal no-claim result; unchecked relevant
eligible Git work, unresolved comparisons and required delivery remain blockers.
Genuinely irrelevant tooling/ephemeral work need not invent wiki pages. Skip
QMD/wiki comparison only if neither completed pass yielded relevant eligible work.

Group relevant work into topics and compare against the existing wiki/docs.
Use record-topic/resume-topics or bounded topics-batch (at most12 per model call,
helper maximum64) with exact source pins, candidate identities and wiki inputs.
A docs Git topic also has its separate documentation_pin; code evidence never
uses main. Reuse only a current reusable comparison. New/missing/stale topics
need actual inspection. A cached update_needed decision is pending delivery.

plan-delivery requires complete session/Git/history coverage and actual bound
topic receipts for relevant candidates. Already-covered Wiki inputs must match
pinned delivered main blobs; dirty local text cannot substantiate delivery.
Supply the exact workspace receipt to bind the isolated delivery checkout.
Before an edit it requires that checkout's clean main with HEAD equal to the
pinned docs tip; the normal checkout is not required to be clean/aligned. Desired
Markdown is written privately first and bound to base SHA, exact owned paths,
old/intended blobs, original comparisons and the immutable protection identity.
Paths must be regular safe Markdown targets. Nonconflicting overlaps with the
protected initial work are allowed only through derived expected staging and
worktree trees; concrete merge conflicts and untracked path collisions block.
No required update may be omitted. Use the named delivery/plan.json pointer after
interruption; a matching stored plan is adopted, not recreated from post-edit
wiki hashes or caller ownership claims. Mutable restoration progress remains in
the protection journal, separate from frozen comparison evidence.

## 5. Guarded own delivery and recovery

Call delivery-status before applying the desired files and before each next
delivery action. It rechecks the exact allowed refs and actual owned checkout.
Under the explicit opt-in, newly fetched code tips may advance normally provided
each reviewed pin is still its corresponding tip's ancestor. Keep the reviewed
pins in the successful checkpoint; newly reachable work belongs to the next
window, not a fabricated current review. Missing refs, rewritten/nonancestor
history or corrupt evidence remain unsafe. New activity in the normal checkout
does not affect delivery ownership.
Only status planned or own_edits permits applying the remaining exact intended
content and preparing the scoped commit. Run diff --check and inspect the entire
scoped Markdown diff; stage only the plan's files. Commit directly on main with a
concise docs subject. Only an exact own_commit permits push origin main; freshly
confirmed delivered means no duplicate push. Never switch to another branch or
reset/clean/amend/pull/rebase/force-push to repair a blocker. Stash/restore is
limited to the explicit protection journal, not a general blocker-repair action.

An append-only docs-main race can also occur before a plan exists:
`prepare-workspace` then returns successful nonterminal `refresh_required`.
If main advances after its fetch, a later pinned-workspace guard can detect the
race instead; attempt the same guarded pre-plan retirement rather than stopping
on this normal main advance. Retirement itself verifies clean ownership/ancestry.
Call `retire-plan` with common review input and the old source receipt/SHA,
plus the exact workspace receipt/SHA if returned; omit plan_receipt. It retains
the clean owned preparation/checkout and archives only active pointers. Reuse
the same captured session run, obtain fresh source proof, complete both history
chains, prepare a fresh main workspace and redo relevant topic comparisons.
Do not recapture the index or treat this normal advance as a terminal blocker.

After a docs-main race or non-fast-forward push, retain any plan, intended bytes
and exact own commit. Use the helper's explicit plan-retirement/replanning path,
re-fetch only exact main, complete the new docs history and relevant comparisons,
prepare the new owned main checkout, and deliver a newly validated normal
fast-forward commit/push. Do not stop just because another task committed.
If the exact own commit is already reachable from remote main, certify its
delivery without another push. Never force-push, reset or rebase away foreign
work. This is a bounded refresh of Git proof, not a live session-index refresh.

After failed commit/push retain the plan and preserved phase. Restart
reconciles exact owned parent/paths/blobs against the prior intent; unknown work
is never adopted. The delivery receipt links original topic comparisons to the
automation's own post-edit committed content. Own intended edits must not be
mistaken for foreign comparison staleness. No-change delivery remains explicit.

For an in-place protected plan only: after delivered status, including a no-change plan, call restore-worktree with
common input and the exact optional plan_receipt/plan_receipt_sha256. The helper
validates the protected stash identity and original base or exact planned own
commit, then applies only its saved SHA with --index. It derives expected index
and worktree trees with merge-tree and verifies actual tracked/index/untracked
restoration. Protected clean state is verified without an apply. Reconciliation
tolerates only that validated restored initial work; new or unrelated changes
remain blockers. The owned restored stash stays as a
safety backup, and foreign stash entries are untouched. Never pop or drop an
unknown stash.

On any failed step after protection, attempt the same safe restore before
reporting failure. Restoration does not require remote access, current code pins,
definition or memory, so changed source state cannot alone strand protected work.
If a concrete conflict, collision or incompatible worktree prevents restoration,
retain the stash, snapshots and journal, report the exact preserved phase and
leave completion blocked. Never reset, clean or replay an already verified apply.

## 6. Complete, journal and retire

finalize is the sole official checkpoint writer in this flow. Do not patch memory
manually or pass caller success booleans/arbitrary cursor/pins. It requires current
complete pages/clones, all dispositions, exact permitted sources, successful
required delivery and exact verified restored worktree/index state where an
in-place protection was used, then derives cursor/carry/reviewed four code tips/
separate canonical Docs tip. An isolated plan certifies the clean owned checkout
and actual remote delivery without moving/restoring the normal checkout's work.
All missing IDs validated under the ignore policy are removed from the derived
carry array only in this successful atomic write. Remaining objects and order
are retained. Capture alone never prunes the official carry or advances memory.

Under the shared store writer lock, prepare the expected-old/intended-new intent
with the frozen delivery and verified restoration proofs, replace the whole
completion header while retaining other memory, publish terminal
receipt and retire only its own active pointer. Last review is completion time;
Processed is the immutable window watermark. A failure before complete proof,
delivery or verified restoration leaves the official bundle unchanged. Memory
writers in this workflow must share the same lock; there is no universal
transaction against writers that ignore it.

Restart finalization only with its named protected plan/intent. The exact old
bundle requires fresh pre-write delivery and restoration validation. The exact
intended new bundle permits receipt/retirement completion from the saved
pre-write delivery/restoration proofs; newly arriving work then belongs to the
next review. A third official bundle blocks. A completed retired result is
idempotent. Preserve all run evidence.

Report one outcome banner: successful, successful with no update, or failed with
the concrete blocker. Include reviewed scope/pins, dispositions, lookup method,
changed files, protection/restoration phase, retained owned stash and actual
delivery/checkpoint status. Do not label source inspection as deployed/runtime
behavior or a partial Git pass as a complete wiki review.
