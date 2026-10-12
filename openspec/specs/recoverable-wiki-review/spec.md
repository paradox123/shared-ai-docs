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
A small local .NET helper MUST persist exact resolver outputs, numeric exit status and original index bytes in protected task-owned run storage outside the automation memory directory. It MUST preserve and verify the original full memory snapshot, and bind current reuse to its authoritative processed/carry/source-tip checkpoint bundle (legacy Last review only when no processed cursor exists), automation ID, definition, resolver/helper version and maintenance-thread exclusion. Failure notes and Run time prose MUST NOT invalidate reuse when that bundle is unchanged. Reinvocation with unchanged inputs MUST adopt an existing captured run instead of resolving a new live index. Unsafe, incomplete or changed stored inputs MUST fail closed or be explicitly invalidated without advancing memory. Capture/resume MUST NOT alter the final cursor or perform Git/network/documentation writes.

#### Scenario: Model stops after selection
- **WHEN** selection files were persisted and the model stops before review completion
- **THEN** a later capture/resume with identical inputs returns the same run and manifest without a new resolver invocation

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
The NCG automation MUST invoke the protected capture/resume and completeness checks through existing local tools. Its daily schedule, thread target, temporary 500-session rule and source/reachability/documentation safeguards MUST remain unchanged. Verification MUST exercise the actual public resolver/helper CLIs on isolated fixtures, including interruption across separate processes, rather than changing live NCG systems or claiming a fresh successful wiki run.

#### Scenario: Update existing automation
- **WHEN** the new rules are installed
- **THEN** only the authorized workflow text changes and the current memory/checkpoint and unrelated repository edits remain intact
