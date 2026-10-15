# Protected wiki review receipts

`ReviewRun.cs` is a local .NET file-based app for retaining one immutable Codex
selection, proving bounded summary-page completeness, and reusing provisional
topic comparisons after interruption. The existing Python resolver and extractor
remain the record readers. The helper uses only .NET standard libraries; it does
not run Git/network commands, edit wiki/source files, update automation memory,
or certify delivery. The separate NCG-specific `NcgWikiDelivery.cs` owns fixed
source fetches, delivery reconciliation and recoverable official completion;
follow [NCG-Automation.md](NCG-Automation.md) for that ordered workflow.

Run from the owning `shared-ai-docs` repository so `global.json` selects SDK
10.0.203 (an ambient Vault/NCG SDK8 cannot run a file-based app):

```bash
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRun.cs -- capture --request /private/capture.json
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRunTests.cs
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiIntegrationTests.cs -- --ignore-missing
```

Dependencies: .NET SDK10 with file-based apps, a Unix filesystem, and Python3 for
the existing sibling scripts. Request files contain private paths and review
context; their creator must use `0600`. The CLI emits one compact JSON response
on stdout; failure exits2. Capture also emits a compact `capture_started` path
receipt on stderr **before invoking the resolver**. Resolver/extractor stderr
and complete raw outputs remain in private files.

NcgWikiDelivery rejects symlink components in request paths as well as protected
evidence/target paths. Pass a canonical request path. On macOS, normalize an
existing mktemp `/var/...` file to its `/private/var/...` location with the existing
path-resolution tool; keep its bytes, permissions and original run unchanged.

## Capture and recovery

```json
{
  "automation_id": "keep-ncg-wiki-current",
  "codex_home": "/absolute/codex-home",
  "definition": "/absolute/automation-directory/automation.toml",
  "memory": "/absolute/automation-directory/memory.md",
  "resolver": "/absolute/scripts/resolve_codex_sessions.py",
  "python": "python3",
  "exclude_session_id": "current-maintenance-thread-id",
  "missing_session_policy": "ignore",
  "max_sessions": 100,
  "batch_size": 100,
  "timeout_seconds": 120,
  "max_output_bytes": 16777216
}
```

`store` is optional; its default is
`<codex_home>/automation-runs/keep-ncg-wiki-current`. It must be outside the
automation definition/memory directories and `<codex_home>/automations`,
including through symlinked ancestors. `prompt_last_run` is the resolver's
explicit legacy fallback when needed; the resolver owns cutoff validation.
Existing path components are canonicalized using actual filesystem entry names:
an exact ordinal name wins, otherwise only an existing, uniquely identifiable
case alias is accepted. Unresolved or ambiguous aliases block before store
creation. This rejects an uppercase alias of an excluded directory on a
case-insensitive filesystem while preserving genuinely distinct case-sensitive
directories; containment comparisons remain ordinal. The CLI regression exercises
whichever case behavior the fixture filesystem actually provides.

Capture reads the live index exactly once using `--save-index-snapshot`. With
optional `batch_size` (1–100), each resolver call resolves one bounded slice;
`resolve-batch` replays only the stored exact snapshot and original memory.
Without it, legacy `max_sessions` still limits the whole selection. Protected evidence includes
exact original index bytes, resolver stdout/stderr, numeric exit, full original
memory/definition/resolver snapshots and their digests. Directories are `0700`,
files `0600`. Atomic files and an exclusive store lock prevent partial publication
or competing selection; a racing caller may receive `store_busy_retry`.

Repeat the same `capture` request in a later process to adopt its original run.
A `resolving` result supplies `next_offset`; call `resolve-batch` with
`{"run_directory":"/absolute/captured-run","offset":100}` using that exact next
offset until complete. A repeated completed offset returns `batch_reused:true`.
No live-index refresh or successful batch repetition occurs. The aggregate
manifest is published only after full contiguous identity/carry validation;
require terminal `extraction_allowed:true`. Identity binds automation ID,
definition/resolver/helper contents, Codex home, exclusion, limits and checkpoint. Current
memory comparison uses top-level `Processed window end`, `Carry-forward
sessions`, `Authoritative source tips` and separate `Docs reviewed tip`; `Last review` participates only when
Processed is absent. Run time and appended failure prose may change. The original
full memory snapshot still must match its original byte digest.
When Processed is present, the ignored `prompt_last_run` scheduler value is
normalized to empty for capture/resume identity. When Processed is absent, that
explicit legacy boundary remains bound and a change blocks reuse.
If both `Processed window end` and `Last review` are absent from the current
header, but `Last review` occurs only in historical sections, capture fails
before creating a run with `historical_last_review_without_header_cutoff`.
Changing that historical timestamp cannot define or resume a selection. The
current header ends at the first `## ` heading, including a heading at file start;
the shared resolver's legacy behavior for other callers remains unchanged.

`<store>/active.json` is the named recovery entry after a yield. Captured failures
return the exact `run_directory` and resolver artifact paths plus raw numeric exit
when available. Missing/corrupt/incomplete captures and changed official inputs
block adoption; they never trigger an automatic fresh resolver invocation. After
an explicitly chosen discard/finished run, call `invalidate` with
`{"run_directory":"/absolute/captured-run","reason":"specific reason"}`.
It preserves evidence and frees the active pointer; it changes no checkpoint.

`missing_session_policy` defaults to `"block"`. The NCG automation uses the
task-authorized `"ignore"` policy: absent-storage rows selected by the window,
carry-forward or both are irrelevant when status is `missing`, path is null,
`meta`/`rollout_window` are absent/null and each ID has its exact `missing_rollout`
diagnostic. Capture reports `ignored_missing_session_ids`; the raw manifest,
exit2/safe=false fields and full selection remain preserved. Such rows have no
cwd and cannot enter scoped extraction. Every other unsafe condition still
blocks. The policy is part of capture identity and cannot change during resume.

Under the default block policy, `approved_missing_carry_ids` retains the existing
per-ID exception for carry-only missing rows. It does not authorize missing
window rows. `extraction_allowed:true` is never checkpoint permission. Ignored
missing carries are pruned only by successful atomic finalization. A previously
resolved/pinned rollout that disappears later remains changed source evidence;
this option never weakens stored snapshot, range or hash checks.

## Summary pages and completeness

`page`, `verify-pages`, `resolve-clone`, `record-topic`, `resume-topics` and
`topics-batch` share:

```json
{
  "run_directory": "/absolute/captured-run",
  "extractor": "/absolute/scripts/extract_codex_session_evidence.py",
  "python": "python3",
  "scope": {
    "cwd_roots": ["/absolute/existing-repository-root"],
    "worktree_tails": ["repository-name"]
  }
}
```

At least one bounded selector is required. Exact roots must have `.git`; worktree
tails follow the existing extractor's home/.codex/worktrees routing. The helper
independently derives eligible IDs in manifest order and pins this one scope and
extractor version for the run. A different scope/extractor cannot silently reuse
pages. The caller owns selection of the intended NCG roots/tails.

For `page`, add `offset` and positive `limit`. `max_total_chars` defaults20000
(allowed2000–2000000). The helper invokes the existing summary extractor and
returns `output` and `page_receipt`. Read that output and follow its next offset.
Offset, limit and the character bound are explicitly pinned in the page receipt.
An identical request with the same binding/scope/extractor and advertised bytes
returns `page_reused` with the exact existing successful output and pointer. The
complete-proof hash and matching provisional topic comparisons remain reusable
when the automation repeats the page chain after capture-resume.

A changed limit or character bound publishes `page_captured` with a new protected
output and pointer while retaining older evidence; smaller pages/higher bounds
after omissions still work. The earlier complete proof must be reverified, and
its previous topic context becomes stale. Damaged output or changed advertised
bytes block reuse instead of silently re-extracting or accepting stale evidence.

`verify-pages` accepts the common request. It requires a contiguous chain from
offset0 to the true terminal page, exact expected IDs and all counts, successful
extractor exits, zero output omissions/skipped unresolved sessions, and explicit
resolution of every manual clone. `has_more:false` and process exit0 alone are
insufficient. Even an empty eligible scope requires a real offset0 summary page.
Success returns `status:complete`, counts and `receipt`/`receipt_sha256`; detailed
IDs/page/clone bindings stay in that versioned receipt.

Each extractor invocation also pins SHA256 of raw bytes in exactly the manifest's
advertised line ranges. The helper skips preceding bytes and stops at the end;
the Python extractor owns JSON parsing. Later append-only records beyond that
range are allowed; missing/truncated/changed advertised records block proof/reuse.

## Explicit clone resolutions

`resolve-clone` adds exact `session_id`, `kind`, and nonempty `reason` to the common
request. It always captures real, complete `--list-clone-boundaries` and
`--structural-projection` outputs for that selected clone, bound to the same
manifest/scope/range pins. `max_total_chars` defaults200000 with the same bounds.

- `kind:"reviewed_suffix"` also requires `suffix_start`. The helper invokes
  `--clone-suffix-start ID=LINE`; the line must appear in the complete boundary
  map as a substantive user line, and the real suffix output must contain a
  substantive turn with embedded history excluded and zero omissions. The caller
  still reviews and justifies ownership of that boundary.
- `kind:"clone_only"` requires `reviewed_boundary_line` from an actual outer/import
  metadata or task-completion boundary. The **entire advertised range must contain
  zero substantive user lines**. A late task completion cannot hide a preceding new
  user turn. Imported user records whose ownership is unproven remain manual and
  blocked; the helper does not reconstruct historical ownership.

Only the matching selected clone is cleared. Ordinary page omissions/count gaps
remain blocking. `clone_resolved` returns receipt and the actual projection paths;
run `verify-pages` again afterward.

## Provisional topics

After a current successful completeness receipt, `record-topic` adds:

```json
{
  "topic_id": "deployment",
  "source_pins": {
    "/absolute/source-repository|refs/remotes/origin/develop": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "/absolute/source-repository|refs/remotes/origin/production": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "session_ids": ["eligible-manifest-session-id"],
  "git_candidates": [
    {"repository":"/absolute/source-repository","sha":"cccccccccccccccccccccccccccccccccccccccc"}
  ],
  "wiki_files": ["/absolute/wiki-file.md"],
  "decision": "update_needed",
  "comparison": "Concrete evidence comparison and remaining update."
}
```

Source values and Git candidates require lowercase SHA40. Keys name an absolute
repository plus its origin develop/production ref; the automation owns its exact
required source map, original-source reachability, ancestry, final pin equality,
and source trust. Session IDs must be unique eligible IDs. Git candidates belong
to a source-pin repository; they support Git-only topics even with no eligible
sessions. At least one session or Git candidate is required.

For a docs-only Git topic, keep the official four-code-pin map unchanged and add
an optional, separate `documentation_pin`:

```json
{
  "documentation_pin": {
    "repository": "/absolute/ncg-docs-root",
    "ref": "refs/remotes/origin/main",
    "sha": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
  },
  "git_candidates": [
    {"repository":"/absolute/ncg-docs-root","sha":"ffffffffffffffffffffffffffffffffffffffff"}
  ]
}
```

The docs repository must be absolute, have `.git`, and equal one of the bound
scope's concrete `cwd_roots`; it cannot also be a repository from the code-pin
map. Only the exact origin/main ref and lowercase SHA40 are accepted. This
separate pin permits Git candidates from that docs root and participates in
topic reuse; a changed docs pin makes the comparison stale. The automation
verifies that this repository actually is ncg-docs and verifies reachability and
ancestry. This adds no Docs cursor or official source-tip key, and never replaces
backend/STS develop/production pins with main.

Wiki inputs are SHA256-pinned; an explicitly listed absent new page is pinned as
`missing`. `unchanged` requires an existing wiki input, or an explicit nonempty
`no_durable_doc_disposition` explaining why no durable page belongs to the topic.
The caller owns that semantic judgment. Decisions are `unchanged`, `update_needed`
or `blocked`. Update-needed stays `pending_delivery`; blocked is `topic_blocked`.

Call `resume-topics` with the common request, topic ID, current source pins,
session/Git candidates, wiki paths and any no-doc disposition; decision/comparison
need not be supplied. It revalidates capture, complete pages and clone proofs
**before** looking up a topic. Exact context returns `reusable` with its provisional
decision; changed pins/candidates/wiki inputs return `stale`, absent topics
`missing`, and blocked decisions remain `topic_blocked`. Creating a formerly
missing wiki file makes a pending receipt stale. There is no delivered state.

`topics-batch` adds `operation:"record"` or `operation:"resume"` and a `topics`
array of 1–64 topic field objects to the common request. Use at most12 topics per
model call. Top-level shared topic defaults are inherited; a nested topic cannot
override run/scope/extractor/python. All contexts are validated before recording,
and the complete source proof is validated once. Response `topics_complete`
contains per-topic `results` and `complete_proof_validations:1`. The aggregate
request is bounded to524288 bytes; individual topic commands remain supported.

Resolver/extractor startup uses the existing Python interpreter for its Unix
session boundary. Processes default to120 seconds and16 MiB combined output; capture
options are identity-bound. Page attempts may set timeout_seconds (1–120) and
max_output_bytes (2000–16777216). Timeout124, outputlimit125 and unsafe
termination126 retain protected diagnostics and return non-success. Explicit
`retry_failed:true` can supersede only a validated known failed attempt; its
original named evidence remains linked. Successful/corrupt/changed attempts
cannot be silently replaced. The store lock is released after bounded cleanup.

All ReviewRun receipts explicitly withhold checkpoint permission. The full semantic wiki
review, authorized missing-session handling, source/reachability/migration guards,
main-only delivery and successful required commit/push gates remain the caller's
responsibility. This app never advances official memory.

## NCG-specific source, delivery and completion requests

`NcgWikiDelivery.cs` is a separate file-based app. It requires the same SDK/Unix/
Python environment, actual Git and the POSIX `test` command for bounded regular-file checks; use local bare repositories for tests. It
performs fixed allowed fetches (local remote-ref updates), writes protected
receipts/content, and only `finalize` writes official memory/retirement. Explicit
`prepare-workspace` creates a protected independent main checkout of the same
docs origin, leaving the canonical checkout untouched. `retire-plan` preserves a
superseded owned plan/checkout for bounded same-run replanning after a docs push
race. `protect-worktree` and `restore-worktree` requests also stash and restore the
bound docs worktree and index. It does not author docs, commit or push. Callers
that do not invoke protection retain the existing strict dirty-worktree gates;
there is no automatic stash on a rejected plan. Its exact source/delivery gates
and restart order are owned by [NCG-Automation.md](NCG-Automation.md).

Common input for `verify-sources`, `protect-worktree`, first `plan-delivery` and
`restore-worktree`:

```json
{
  "run_directory": "/absolute/captured-run",
  "review_helper": "/absolute/ReviewRun.cs",
  "review_request": {
    "extractor": "/absolute/extract_codex_session_evidence.py",
    "python": "python3",
    "scope": {"cwd_roots":["/absolute/backend","/absolute/sts","/absolute/docs"],"worktree_tails":["backend","sts","docs"]}
  },
  "repositories": {"backend":"/absolute/backend","sts":"/absolute/sts","docs":"/absolute/docs"}
}
```

Source/planning commands require `review_helper` to match the capture and a
current proof. Repositories are exact Git roots; docs must belong to the bound
scope. `restore-worktree` uses the protection recovery contract below instead of
rerunning the source proof. `verify-sources` returns
`status:sources`, a protected `receipt`/`receipt_sha256`, four `source_pins`, a
separate `documentation_pin` and counts. Full candidate/range lists stay private.

`verify-sources` optionally accepts `allow_source_advancement:true`, bound into
its receipt. Default callers still require exact final code-pin equality.
Opted-in callers allow only append-only ancestry from each actually reviewed
pin to its freshly fetched matching develop/production ref. Finalization keeps
the reviewed four-pin map, never silently checkpoints unreviewed newer commits.
Missing refs, nonancestor histories and corrupt evidence still reject.

`prepare-workspace` takes common input plus the exact source receipt/SHA. It
returns `workspace_ready`, protected `receipt`/`receipt_sha256` and a payload
containing `workspace_root`, `canonical_docs_root`, `docs_base_sha` and `origin`.
The private independent Git checkout is owned by this run, on main, clean and
aligned to the selected Docs tip, with exactly the canonical docs origin.
`delivery/workspace.json` retains its receipt pointer for reuse. Existing dirty
or concurrent work in the canonical checkout is neither moved nor modified.
Keep the canonical root in selection scope, source topics and persisted Docs
reviewed tip; only actual edit/stage/commit/push operates in workspace_root.
After canonical QMD routing, use the clean owned workspace's physical wiki paths
for topic-input hashes/comparisons. An isolated plan maps those paths back to
repository-relative paths and proves them against the exact pinned main blobs;
dirty canonical text does not substitute for delivered wiki evidence.
No caller-chosen arbitrary checkout, foreign origin or feature branch is accepted.
When preparation's fresh main check detects an append-only advance, the command
instead returns successful nonterminal `refresh_required`. A push after that
check can instead reach a later pinned-workspace guard. For either normal
docs-main race before any plan exists, use the guarded pre-plan `retire-plan`
request below; it independently proves safe ownership/ancestry. Do not stop or
recapture sessions merely because main advanced.

`git-history` and `docs-history` take `run_directory`, `source_receipt`, optional
`source_receipt_sha256`, `offset` and `limit` (1–100). Their protected page payload
has offset/count/next_offset/has_more/selection_count plus bounded candidates or
commit SHAs. Follow both complete chains, including empty offset0 pages. Docs
missing baseline is explicit; no datetime substitutes for its SHA range.

`protect-worktree` takes the common input plus `source_receipt` and
`source_receipt_sha256`. Invoke it after both complete history chains and before
topic/wiki comparisons. It requires the validated source identity and main with
HEAD equal to the pinned docs tip. Existing staged, unstaged and untracked
regular files do not alone block the run: the helper retains protected raw
snapshots, journals the operation, and uses `stash --include-untracked` to obtain
its exact owned stash SHA. The resulting delivery worktree must be clean.
An initially clean worktree records protected clean state without creating a
stash. Ignored files remain untouched. Unsupported state or a concrete collision
still blocks with the protected data retained.
Tracked raw bytes and modes are retained as well as index/Git-tree identities.
Before mutation, unsupported clean/smudge, encoding/EOL or mode conversions and
changes to ignore/attribute files are rejected explicitly; ordinary `autocrlf=input`
with byte-identical LF contents is supported. Entries that Git does not include
in stash/status, such as FIFOs, remain untouched and are never opened as data.

The protected journal and snapshots live under the named run's `delivery/`
directory, outside the docs repository. Their identity binds run, repository,
base and helper; a plan freezes that immutable protection identity, while the
journal records recovery progress. An unchanged repeated request adopts only its
own operation, including interruption after stash creation. Never substitute
`stash@{0}`, another stash or a newly captured run for the saved identity.

`plan-delivery` adds the source receipt, `candidates` and `edits` to common input.
The optional exact `workspace_receipt`/`workspace_receipt_sha256` selects the
verified owned isolated checkout and freezes its identity in the plan. Without
it, existing in-place protection/strict worktree behavior remains unchanged.
Candidate objects have kind (`session` with id, or `git` with repository/sha),
disposition, concrete reason, and for relevant compared work `topic_receipt` plus
`topic_receipt_sha256`. Edits have repo-relative regular Markdown `path` and exact
desired UTF8 `content`. Expected full candidate coverage is derived independently.
Unproven session discovery is a terminal no-claim; eligible Git work cannot be
silently omitted. Plan receipts bind desired contents and original comparisons
before any edit, plus the immutable protection identity when protection was
explicitly requested. Nonconflicting overlaps with protected work are permitted
only through derived expected index/worktree trees; concrete merge conflicts or
untracked path collisions block. The named `delivery/plan.json` pointer supports
unchanged plan adoption after interruption. Changed intent blocks rather than
overwrites it.

`delivery-status` takes `run_directory`, `plan_receipt` and its optional SHA256.
Results are planned, own_edits, own_commit or delivered. In isolated mode, a
verified append-only docs race returns nonterminal refresh_required for the
explicit retirement/replanning path. Actual unsafe ownership failures return exit2
without adopting unrelated files/commits. Actual guarded edit/stage/commit/push
remains the automation's action, based on this exact own-work reconciliation.

`retire-plan` takes the exact plan identity plus common review input for a known
docs-main advance. It preserves the old intent/checkout/own commit and archives
only the active plan/workspace pointer, returning `refresh_required` for new
source/history/topic comparisons and a fresh owned main workspace in the same
captured session run. It never resets, rebases, force-pushes or touches the
canonical checkout. If the exact own commit is already reachable from freshly
verified origin/main, reconciliation returns delivered instead of repeating its
push. Unowned edits or rewritten history are not a safe replanning state.

Before a plan exists, `retire-plan` instead takes common input plus the **old**
`source_receipt`/`source_receipt_sha256`, with optional exact
`workspace_receipt`/`workspace_receipt_sha256` when a workspace was returned.
Omit `plan_receipt`. It proves an append-only docs advance and clean owned
workspace/preparation, archives only its active pointers and preserves the
checkout. A repeated unchanged request is idempotent. Then run `verify-sources`,
both complete history chains, `prepare-workspace` and relevant topic comparisons
again within the same captured session run before recording a new plan.

`restore-worktree` takes common input and, if a plan exists, its `plan_receipt`
and `plan_receipt_sha256`. Invoke it after delivery, including a no-change result,
and attempt safe restoration after a failed step before reporting. It validates
the protected run/repository/stash identity and either the original base or the
exact planned own commit, then applies only the saved stash SHA with `--index`
when a stash was needed. Protected clean state needs verification but no apply.
Recovery does not depend on remote access, current code pins, automation
definition or memory. Expected staged/worktree trees are derived with
`merge-tree`, and actual tracked/index/untracked state must match before the
journal can record verified restoration. A repeated request adopts an already
verified restore; it does not apply the stash twice. Conflicts, collisions or new
unrelated work preserve the stash and data and block completion. The restored
owned stash remains as a safety backup; foreign stash entries are untouched.
Never pop/drop an unknown stash or use reset, clean or rebase for recovery.

`finalize` takes the plan identity and common `review_helper`/`review_request`
for current pre-write proof. Omit optional `new_checkpoint`: cursor/carry/code
tips/Docs tip are derived from evidence. If supplied, exactly five named header
keys and their derived values are required. First finalize verifies before the
shared writer lock. A protected plan also requires exact verified restoration,
including no-change delivery, before any checkpoint replacement.
Isolated delivery which never stashed user work instead certifies its exact
owned checkout and remote commit; it does not require moving/restoring unrelated
canonical work. The canonical repository identity stays in the Docs checkpoint.
The protected expected-old/intended-new intent freezes its restoration proof along with the
delivery proof: old-bundle recovery revalidates before writing, while intended-
new-bundle recovery completes receipt/retirement from those saved proofs.
`complete` requires actual needed delivery and exact full bundle persistence plus
active retirement. Repetition of an already completed plan is idempotent. Memory
of a third bundle blocks; other memory prose is retained.

All receipt reuse binds the current delivery-helper source identity. Old tools,
corrupt files, changed candidate/proof inputs and foreign state cannot certify
completion. This is a cooperating-writer lock contract, not a universal CAS
against independent writers ignoring that lock.
Narrow restoration is the ownership-only exception: changed tools/definition,
memory or active pointer cannot strand the saved user work. It validates the
original run, journal, exact stash and any own commit without certifying review.
