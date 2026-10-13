# recoverable-wiki-review Specification

## Purpose
Keep the NCG wiki review cursor aligned with the processed window, prove complete selected evidence, and retain protected provisional work across interruptions without advancing the official checkpoint prematurely.

## Requirements
### Requirement: Authoritative processed-window cursor
When a Processed window end field is present in the current memory header before historical review sections, the shared resolver MUST use its valid value as the sole session selection cutoff. It MUST ignore later Last review, Run time and scheduler Last run timestamps for selection. A malformed or ambiguous present processed cursor MUST fail closed without falling back. Historical processed fields MUST NOT supply or duplicate the current cursor. Legacy Last review or explicitly supplied trusted prompt boundaries MUST be considered only when the processed cursor is absent and MUST be visibly identified as legacy fallback. Cursor/carry/source-tip state MUST remain unchanged during implementation and incomplete reviews.

#### Scenario: Completion occurs after the captured window
- **WHEN** memory has processed end 06:15 and completion/Last review 07:07 and an indexed session at 06:40
- **THEN** the resolver selects the 06:40 session from the processed cutoff 06:15 rather than skipping it

#### Scenario: Invalid processed cursor with valid later legacy value
- **WHEN** a processed cursor exists but is invalid and Last review is valid
- **THEN** resolution fails without an eligible review window or successful checkpoint permission

### Requirement: Complete same-manifest extraction receipt
The local review helper MUST prove that all selected eligible summary pages belong to one immutable manifest and one stable selection scope, cover the page sequence through its final page, report zero omitted projections and leave no unhandled manual clone work. Identical page requests with unchanged bounds and bound source inputs MUST reuse their validated successful output and preserve the completeness identity, so a restart does not invalidate unchanged topic comparisons. Successful extractor process exit alone MUST NOT establish completeness. Missing pages, inconsistent counts, duplicate session IDs, foreign-manifest pages, output omissions and unresolved manual records MUST block the receipt. The automation MUST require the successful current receipt before its checkpoint patch.

#### Scenario: Last output page still omits projections
- **WHEN** a page reports has_more=false but omitted_sessions.count is positive
- **THEN** completeness validation fails and the checkpoint remains unchanged

#### Scenario: Missing middle page or unresolved clone
- **WHEN** the collected page sequence has a gap or a selected clone remains unresolved
- **THEN** completeness validation rejects the review even if all process exits were successful

#### Scenario: Complete bounded pages
- **WHEN** pages from the same pinned manifest and scope cover all eligible sessions without omissions or unresolved manual work
- **THEN** the helper emits a versioned complete receipt bound to that manifest and scope

#### Scenario: Repeat completed pages after interruption
- **WHEN** capture resumes and the same summary-page bounds are requested with unchanged advertised records
- **THEN** the existing successful page output and completeness identity are reused, and an otherwise unchanged topic comparison remains reusable

#### Scenario: Reuse a verified clone resolution
- **WHEN** resumed pages have an existing valid manual clone resolution
- **THEN** the automation validates that resolution through verify-pages and retains it, invoking clone follow-up only for a concrete unresolved-manual-clone blocker

### Requirement: Protected capture and interrupted-run resumption
A small local .NET helper MUST persist exact resolver outputs, numeric exit status and original index bytes in protected task-owned run storage outside the automation memory directory. It MUST preserve and verify original memory and bind reuse to the authoritative processed/carry/code-tip/Docs-tip bundle (legacy Last review only when no processed cursor exists), automation ID, definition, versions and original maintenance exclusion. Failure notes and Run time MUST NOT invalidate unchanged reuse. Reinvocation MUST adopt the captured snapshot and successful batches without new live-index selection; missing batches MAY resolve only their bounded slice of those exact verified bytes. Unsafe, incomplete or changed inputs MUST fail closed or be explicitly invalidated without advancing memory. Capture/resume MUST NOT alter the official checkpoint or perform Git/network/documentation writes.

#### Scenario: Model stops after selection
- **WHEN** selection files were persisted and the model stops before review completion
- **THEN** a later capture/resume returns the same snapshot and successful batches without another live-index read or repeated successful resolver work

#### Scenario: Original selection or checkpoint changes
- **WHEN** stored index/manifest hashes or current memory/definition no longer match the run
- **THEN** the helper refuses silent reuse and preserves the existing checkpoint and evidence

#### Scenario: A failure note is appended
- **WHEN** only failure prose or Run time changes and the authoritative checkpoint bundle remains identical
- **THEN** the original capture is reused while its stored full-memory snapshot remains immutable

#### Scenario: Legacy boundary exists only in historical notes
- **WHEN** no current-header Processed window end or Last review exists but a Last review field appears only in historical memory
- **THEN** protected capture fails closed rather than adopting a selection whose actual legacy boundary is not bound to the current header

#### Scenario: Approved deleted carry is the sole unsafe condition
- **WHEN** a captured resolver exit 2 contains only a task-approved deleted carried missing-rollout ID and otherwise valid input/output
- **THEN** only that exact allowlisted case is accepted and any unrelated unsafe condition still blocks

#### Scenario: Store aliases an excluded automation directory
- **WHEN** the requested run store resolves inside a definition or memory directory through a symlink or filesystem case alias
- **THEN** capture rejects it before creating run/active files or invoking the resolver, while genuinely separate case-sensitive directories remain distinct

### Requirement: Context-bound topic review receipts
The helper MUST store topic decisions with the immutable manifest, complete extraction receipt, exact authoritative source pins, candidate identities and reviewed wiki-input hashes. Docs-origin/main candidates MUST use a separate documentation pin bound to their concrete scoped repository and exact main tip; this topic input MUST NOT extend the official four-code-tip checkpoint map or substitute for Backend/STS source gates. Resumption MUST expose a receipt as reusable only when those inputs still match. Decisions requiring a documentation update MUST remain pending delivery; a cached comparison MUST NOT certify a successful commit/push or by itself permit checkpoint advancement. The existing full wiki review, final source-tip, migration, main-only and delivery gates MUST remain binding.

#### Scenario: Unchanged topic after restart
- **WHEN** current source pins and wiki file hashes match a stored topic review
- **THEN** the same comparison decision is available for reuse without reinterpreting its evidence

#### Scenario: Git-only topic without eligible session summaries
- **WHEN** an explicit complete zero-session extraction proof and valid authoritative Git candidate identities exist
- **THEN** the helper can store and reuse the Git-only topic without fabricating a session identity

#### Scenario: Docs-only Git topic
- **WHEN** a relevant docs-origin/main candidate belongs to the concrete scoped docs repository and has an explicit documentation pin
- **THEN** the helper can store and reuse its topic, while a changed docs pin makes that comparison stale and leaves the official four-code-tip map unchanged

#### Scenario: Wiki or source context changed
- **WHEN** a reviewed wiki file or source-pin context changes
- **THEN** the cached topic is stale and must be reviewed again

#### Scenario: Cached update lacks delivery
- **WHEN** a stored topic requires a documentation update but no successful required delivery is established
- **THEN** the final automation checkpoint remains blocked

### Requirement: Scoped automation integration and local verification
The NCG automation MUST invoke protected capture/resume and completeness checks through existing local tools. Its schedule, thread target and exact source/reachability/main-only delivery safeguards MUST remain unchanged. The temporary 500-total-session exception MUST remain until tested lossless batch processing is installed; its replacement MUST bound each resolution call to at most 100 sessions without discarding a larger window. Verification MUST exercise public resolver/helper CLIs on isolated fixtures across process restart, without changing live NCG systems or claiming a fresh successful wiki run.

#### Scenario: Update existing automation
- **WHEN** the new rules are installed
- **THEN** only the authorized workflow text changes and the current memory/checkpoint and unrelated repository edits remain intact

### Requirement: Lossless bounded snapshot resolution
The opt-in wiki flow MUST select from one immutable index snapshot with fixed original memory, exclusion, cutoff and window ceiling. Each resolver operation MUST resolve at most 100 selected sessions and emit a verifiable ordered plan identity and slice progression. The review helper MUST require contiguous full coverage, identical bindings, unique IDs and valid carry accounting before publishing its aggregate manifest. Successful batches MUST be reused after interruption; later live-index entries MUST wait for the next capture. No partial batch may grant official checkpoint permission. Existing resolver callers without opt-in batching MUST retain their previous limit and failure contracts.

#### Scenario: Large mixed-project window
- **WHEN** 501 or more sessions belong to a captured window
- **THEN** the wiki flow processes the complete selection in bounded batches without a global 100/500 saturation failure
- **AND** unrelated sessions cannot silently consume the limit and discard NCG work

#### Scenario: Resume after two batches
- **WHEN** two valid batches have been stored and the process stops
- **THEN** restart reuses both and resolves only the next missing bounded slice from the original snapshot

#### Scenario: Incomplete or foreign batch
- **WHEN** a batch is missing, duplicates an ID, changes plan digest/window bounds or uses different snapshot bytes
- **THEN** no complete aggregate manifest or checkpoint permission is issued

### Requirement: Bounded process and failed-page recovery
Resolver/extractor and delivery Git processes MUST have bounded duration and output with owned-descendant termination on timeout. Successful combined process output within the configured byte limit MUST remain complete; output exceeding that limit MUST return non-success with protected diagnostics. A timeout MUST persist protected diagnostics and return non-success. An explicit retry MAY supersede only a known failed extraction with unchanged manifest/scope/source binding while retaining its original evidence. Successful attempts MUST be reused. Corrupt evidence, changed advertised ranges and unapproved unsafe resolver conditions MUST remain blockers.

#### Scenario: Extractor hangs
- **WHEN** an owned extractor or descendant exceeds its deadline
- **THEN** the owned processes stop, the store becomes available and protected diagnostics identify a non-successful timeout

#### Scenario: Successful Git output reaches the configured bound
- **WHEN** a delivery Git process returns complete combined output within its configured byte limit
- **THEN** the helper retains that successful output in full without reserving diagnostic space prematurely
- **AND** output exceeding the limit remains a protected failure and cannot advance the checkpoint

#### Scenario: Known failed page is retried
- **WHEN** an extractor attempt failed and an explicit retry uses unchanged authoritative inputs
- **THEN** its preserved failed evidence is superseded by the new attempt without recapturing the live index

### Requirement: Exact separate Docs reviewed tip
The official completion bundle MUST include a separate validated Docs reviewed tip naming the concrete ncg-docs root, exact origin/main ref and reviewed SHA. The four Backend/STS source-tip map MUST remain exactly four entries. Subsequent docs candidates MUST come from the ancestor-validated prior-to-pinned SHA range, never a commit-date substitute. Missing first state MUST use a proved accepted revision or bounded review of pinned main history before establishing a baseline. Invalid, duplicate, missing historical object or nonancestor state MUST block, not silently reset. The Docs tip MUST advance only with the complete successful review bundle.

#### Scenario: Newly delivered commit has an old date
- **WHEN** a docs commit newly reaches main but its author/commit date precedes the prior execution
- **THEN** ancestry-based selection still includes it

#### Scenario: No Docs baseline exists
- **WHEN** the new field is absent
- **THEN** baseline work is explicit and the current tip is not automatically declared reviewed

### Requirement: Owned delivery and recoverable finalization
Before changing docs, the flow MUST retain a protected delivery intent bound to the clean main base SHA, exact owned paths/base and intended content, original comparison receipts and authoritative source pins. Recovery MUST adopt only those exact own files/commit; foreign edits/commits, wrong branch, rewritten history or changed pins MUST block without reset, stash, amend, pull, rebase or force-push. Read-only delivery reconciliation MUST confirm actual remote state through the exact allowed ref checks; caller success booleans MUST NOT certify delivery. Unchanged topics MUST be compared against pinned delivered wiki content, while delivered topics MUST bind their original comparison to owned committed post-edit content.

Finalization MUST prove all candidate dispositions and required deliveries before preparing an immutable expected-old/intended-new completion intent. It MUST preserve non-checkpoint memory and write the whole bundle under the shared writer lock. Interrupted completion MUST accept only that exact old or intended new bundle and finish terminal receipt/active retirement idempotently. Unrelated official state MUST block; normal review-load validation MUST remain strict. This is not a universal atomic transaction against external writers ignoring the lock.

#### Scenario: Own commit exists after push failure
- **WHEN** a restart finds a local commit matching the stored parent, paths and intended content exactly
- **THEN** it reports the pending owned delivery instead of treating it as an unknown HEAD divergence

#### Scenario: Own push succeeded before interruption
- **WHEN** freshly verified origin/main confirms the owned commit but the delivery receipt was interrupted
- **THEN** reconciliation confirms delivery without a duplicate push

#### Scenario: Own edits changed the wiki comparison hash
- **WHEN** the intended reviewed content was delivered through the bound own commit
- **THEN** that delivery bridges original comparison and post-edit content without accepting unrelated changed files

#### Scenario: Manually resolved clone reaches finalization
- **WHEN** a selected clone has a valid protected resolution and complete page proof
- **THEN** delivery planning follows and verifies the resolution pointer to retain its exact source ranges
- **AND** the complete review can finalize without weakening clone integrity validation

#### Scenario: Finalization stops after memory replacement
- **WHEN** memory equals the protected intended new bundle but retirement did not finish
- **THEN** restart completes receipt/retirement without advancing the checkpoint again

### Requirement: Efficient proof validation and coherent prompt ownership
Bounded batch topic operations MUST validate one current complete proof per invocation and retain existing source/wiki staleness rules. Range hashing MUST process blocks while preserving exact advertised raw bytes, truncation detection and append-only behavior. Efficiency claims MUST be supported by repeatable observations. The live prompt MUST contain one ordered project contract and point to canonical mechanics/schema owners rather than duplicate them. The sole required helper README MUST be explicitly permitted during bootstrap. Mandatory Git-only comparisons and all source/privacy/complete-delivery safeguards MUST remain explicit.

#### Scenario: Several unchanged topics are resumed
- **WHEN** one bounded batch supplies their unchanged contexts
- **THEN** one current completeness validation supports their results with the same trust rules as separate operations

#### Scenario: Bootstrap needs helper schema
- **WHEN** capture inputs must be constructed
- **THEN** the named canonical helper README can be read without contradicting the bootstrap order
