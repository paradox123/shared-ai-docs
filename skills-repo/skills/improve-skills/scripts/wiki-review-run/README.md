# Protected wiki review receipts

`ReviewRun.cs` is a local .NET file-based app for retaining one immutable Codex
selection, proving bounded summary-page completeness, and reusing provisional
topic comparisons after interruption. The existing Python resolver and extractor
remain the record readers. The helper uses only .NET standard libraries; it does
not run Git/network commands, edit wiki/source files, update automation memory,
or certify delivery.

Run from the owning `shared-ai-docs` repository so `global.json` selects SDK
10.0.203 (an ambient Vault/NCG SDK8 cannot run a file-based app):

```bash
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRun.cs -- capture --request /private/capture.json
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRunTests.cs
```

Dependencies: .NET SDK10 with file-based apps, a Unix filesystem, and Python3 for
the existing sibling scripts. Request files contain private paths and review
context; their creator must use `0600`. The CLI emits one compact JSON response
on stdout; failure exits2. Capture also emits a compact `capture_started` path
receipt on stderr **before invoking the resolver**. Resolver/extractor stderr
and complete raw outputs remain in private files.

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
  "max_sessions": 500
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

Capture owns exactly one invocation with `--save-index-snapshot`, compact
manifest and the supplied current-thread exclusion. Protected evidence includes
exact original index bytes, resolver stdout/stderr, numeric exit, full original
memory/definition/resolver snapshots and their digests. Directories are `0700`,
files `0600`. Atomic files and an exclusive store lock prevent partial publication
or competing selection; a racing caller may receive `store_busy_retry`.

Repeat the same `capture` request in a later process to receive `resumed` with
the same run directory and manifest/index SHA256s. It does not read the live index
again. Identity binds automation ID, definition/resolver/helper contents, Codex
home, exclusion, limits and the official memory checkpoint bundle. Current
memory comparison uses top-level `Processed window end`, `Carry-forward
sessions`, and `Authoritative source tips`; `Last review` participates only when
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

Only an explicit `approved_missing_carry_ids` array admits the existing approved
deleted-carry exception: exit2, safe=false, missing/path:null rows with exactly
`selection_reasons:["carry_forward"]`, matching memory carry and `missing_rollout`
diagnostics, and no other unsafe cause. The caller owns concrete authorization
for those IDs. New window+carry missing rows remain blocked. Raw exit/safe fields
remain false/2; `extraction_allowed:true` is no checkpoint permission.

## Summary pages and completeness

`page`, `verify-pages`, `resolve-clone`, `record-topic` and `resume-topics` share:

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

All receipts explicitly withhold checkpoint permission. The full semantic wiki
review, approved deleted-carry handling, source/reachability/migration guards,
main-only delivery and successful required commit/push gates remain the caller's
responsibility. This app never advances official memory.
