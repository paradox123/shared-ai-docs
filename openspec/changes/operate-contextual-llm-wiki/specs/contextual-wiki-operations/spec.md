## ADDED Requirements

### Requirement: Prioritize ongoing wiki maintenance over the initial backlog
Scheduled maintenance MUST prioritize newly arriving and changed source documents over the unprocessed initial source inventory, with the freshness target of processing those updates in the wiki by the next day. The initial import MAY span multiple days. Outstanding initial work MUST remain visible and MUST NOT be reported as a completed production import. Existing source freshness checks and dependency validation remain required; this prioritization does not authorize publishing unverified or stale wiki evidence.

#### Scenario: Source updates arrive during the initial import
- **WHEN** the initial import still has unprocessed sources and new or changed sources arrive
- **THEN** ongoing updates receive priority over the initial backlog
- **AND** maintenance distinguishes completion of ongoing updates from completion of the initial import

#### Scenario: The freshness target is missed
- **WHEN** ongoing updates cannot be processed by the next day
- **THEN** the unprocessed updates and the missed freshness target remain visible
- **AND** the run does not claim those updates were completed on time

### Requirement: Bounded observable maintenance with durable resumption
Maintenance MUST execute with explicit finite work or time bounds and a finite termination grace period. It MUST persist validated reusable extraction results across process restarts, binding reuse to relevant source versions and generation inputs. It MUST NOT equate saved extraction work with published current wiki knowledge. A resumed run MUST reuse compatible successful work and retry only missing, invalidated or failed work and its required dependencies. Progress and failures MUST be durably observable before compilation returns. A run ending with pending requested work MUST remain distinguishable from complete success and MUST NOT advance the fully completed maintenance timestamp.

The automation MUST observe its owned run for a bounded period and use durable progress evidence for diagnosis; it MUST NOT keep polling indefinitely because a final report is absent. Shared provider failures MUST stop further dependent model dispatch while allowing independent safe work to retain progress. Source drift MUST invalidate affected work without discarding demonstrably independent reusable results. Unknown dependencies MUST block unsupported publication.

#### Scenario: Resume after a bounded or interrupted run
- **WHEN** a run ends after successful extraction results have been durably saved and work remains pending
- **THEN** a fresh process reuses those results when their evidence and generation inputs remain compatible
- **AND** incomplete or incompatible results are not treated as reusable successes
- **AND** the report distinguishes source-index completion, ongoing updates and initial-import backlog

#### Scenario: Validate extraction compatibility independently of publication
- **WHEN** a fresh process considers a previously saved extraction
- **THEN** it checks the source identity and content, resolved model/provider contract, actual prompt and tool schema including supplied context, and installed compiler contract
- **AND** a corrupt, incomplete or incompatible entry causes local recomputation without discarding other compatible entries
- **AND** every supplied field of a successful extraction satisfies the actual tool schema before durable storage or publication
- **AND** saved work survives a later source-drift or indexing failure without advancing the completed maintenance timestamp

#### Scenario: Source changes while work is running
- **WHEN** one source changes during generation and unrelated successful work can be proven independent
- **THEN** affected statements are withheld until revalidated against current evidence
- **AND** the independent successful work remains reusable after restart

#### Scenario: Shared provider failure during queued work
- **WHEN** maintenance detects a shared provider failure with further model work queued
- **THEN** no additional work depending on that failed provider is dispatched
- **AND** already running work is settled or terminated within the finite grace period with durable failure and pending-work evidence

#### Scenario: No final report is available within the observation bound
- **WHEN** the automation reaches its finite observation bound without a final report
- **THEN** it uses the known durable progress location for a bounded diagnosis and reports an incomplete or failed outcome
- **AND** it neither launches a duplicate collector nor enters another unbounded polling loop

#### Scenario: Public helper terminates held work and retains custody after owner death
- **WHEN** the public helper exhausts its finite wall-clock budget while a provider or owned subprocess is held
- **THEN** it stops dependent dispatch, terminates only its owned process groups within its finite grace and emits a non-success report with pending work
- **AND** the already persisted progress remains readable before termination without provider error payloads or document text
- **AND** abrupt death of the outer helper does not leave an unowned mutating compiler or detached provider process
- **AND** a fresh process reuses compatible durable extractions without moving the completed-maintenance timestamp for partial work


### Requirement: Automatically adopt verified upstream wiki revisions
The local wiki installation MUST follow published releases of the upstream LLM Wiki repository as a whole, resolving each adopted release to an exact commit and using the dependency versions defined by that revision's manifest and lockfile. It MUST NOT independently update compiler libraries or re-resolve their locked versions ahead of upstream. Independent Node, QMD and wrapper dependency updates are outside this update scope. A required build MUST reproduce the adopted upstream revision with the existing integration patch rather than introduce new dependency versions.

After a successful build and all required compatibility tests, the verified upstream update MUST be adopted automatically without renewed human review or merge approval. Required checks MUST cover the existing integration patch and managed wiki behavior. Missing, pending or failed required checks MUST block adoption. If Renovate and integration PRs are used, they MUST update only our upstream reference and MUST merge automatically after the required checks pass. This flow MUST NOT modify the upstream repository. Repository merge success MUST NOT be reported as successful Mac installation without verifying local activation separately.

#### Scenario: Upstream changes without a published release
- **WHEN** upstream has new main-branch commits, a tag without a published release or a draft release
- **THEN** the updater does not adopt those changes
- **AND** prereleases are excluded by default

#### Scenario: A compiler library publishes a new version
- **WHEN** Library X publishes a new version that the adopted upstream wiki revision has not incorporated
- **THEN** the local updater retains the version defined by that upstream revision
- **AND** it does not create a separate dependency update for Library X

#### Scenario: Upstream incorporates a library update
- **WHEN** a new adopted upstream wiki revision includes an updated Library X and its build and all required checks pass
- **THEN** the updater adopts that wiki revision with its upstream-defined dependency versions automatically
- **AND** it verifies local activation without requesting renewed human approval

#### Scenario: Update checks are incomplete or fail
- **WHEN** a required build or test fails, is missing or is still pending
- **THEN** the update is not adopted and any integration PR does not merge
- **AND** the previous working installation is retained and the incomplete or failed verification remains visible

### Requirement: Scheduled source indexing independent of wiki compilation
The existing local daily QMD automation MUST maintain the source retrieval index independently of successful wiki compilation and MUST maintain one common production wiki over all selected source repositories, including `private`, `Projects/Private`, Meetings and Projects. Pending or failed wiki generation alone MUST NOT prevent current original sources from becoming searchable through WikiQuery. Source indexing MUST NOT expose stale or unverified generated wiki content as current evidence; shared scan, storage or index failures MUST still block the operations that depend on them. It MUST preserve the existing schedule, model, project and notification settings. The name `private` MUST describe a subject domain only and MUST NOT cause a separate wiki, a maintenance exclusion, a special query approval or a confidentiality classification. The automation MUST NOT substitute acceptance fixtures for the full production inventory. No additional scheduler or watcher SHALL be installed.

#### Scenario: Successful daily run
- **WHEN** source reconciliation and wiki maintenance succeed
- **THEN** current original sources and verified generated wiki content are available through the managed retrieval interface
- **AND** the report distinguishes source index freshness, ongoing wiki updates, initial-import backlog, no-op work and failures

#### Scenario: Original source is searchable before wiki generation completes
- **WHEN** a new or changed original source has been indexed but its wiki generation is pending or has failed
- **THEN** WikiQuery can retrieve the relevant current original evidence with verified references and an explicit fallback indication
- **AND** it does not present outdated dependent wiki statements as current
- **AND** successful source indexing does not imply successful wiki generation or a completed initial import

#### Scenario: Personal and professional sources participate together
- **WHEN** scheduled maintenance encounters relevant sources in `private`, `Projects/Private` and another selected repository
- **THEN** these sources participate in the same maintained knowledge layer without renewed per-run approval
- **AND** the compiler can synthesize their supported relationships without a general/private partition

### Requirement: WikiQuery is the standard agent context entry
Agents MUST start knowledge-context searches through the managed WikiQuery interface of the common wiki. QMD MUST remain the internal persisted retrieval engine and MUST NOT be presented as a competing standard context-search route. WikiQuery MUST return relevant supported knowledge with navigable original-source references and freshness information, respecting explicit task/source limits. Agents MAY follow those references to inspect authoritative original documents directly.

Scheduled maintenance MUST NOT replace query-time checks of relevant original-source versions. WikiQuery MUST reject stale wiki evidence and expose maintenance needs or fall back to appropriate current original sources within the same interface. Ordinary context queries MUST NOT trigger compilation or durable answer creation without a save request. Unavailable WikiQuery MUST be reported rather than silently bypassed through an unvalidated QMD context search. Direct QMD remains available for index operations and diagnostics.

#### Scenario: Agent starts a context investigation
- **WHEN** an agent needs contextual knowledge for a task
- **THEN** it calls WikiQuery and receives relevant knowledge with original-source references
- **AND** it can inspect those original sources without selecting a second retrieval product or manually assembling QMD collections

#### Scenario: Original source changes after scheduled maintenance
- **WHEN** an original source has changed since the last successful scheduled run
- **THEN** WikiQuery does not certify the dependent wiki statement as current
- **AND** it reports the gap or uses suitable current original evidence through the same entry

### Requirement: Verified context adoption catalog
The delivery MUST catalog actual relevant maintained skills, AGENTS/README/CONTEXT and other agent entry files, with priority, intended role and adoption status. It MUST distinguish canonical files from aliases, history and vendor content. Proposed routing MUST use WikiQuery as the standard context entry with freshness validation, relevance to the concrete task, current-source fallback and original-source authority. Explicit task/source limits MUST be respected. The label `private` alone MUST NOT exclude evidence or require a separate query mode.

#### Scenario: Operator plans context adoption
- **WHEN** the operator reads the catalog
- **THEN** each proposed surface has an existing path, rationale and concrete intended change
- **AND** proposed entries are not represented as already installed routing
- **AND** private-domain evidence is selected or omitted by task relevance rather than an inferred access policy

### Requirement: Lossless verified knowledge migration
Before replacing any existing knowledge, migration MUST inventory actual output and backup contents, including saved answers, page dependencies, untracked Markdown and empty configured outputs. It MUST preserve original bytes and required state in a checksummed local snapshot whose completeness can be verified before publication. Original inputs MUST remain available. Import into a fresh output MUST NOT require full source compilation; selected sources outside valid imports MUST remain visible as pending source additions for subsequent maintenance. Valid unique texts MUST be carried without model rewriting; only navigational links and dependency version references may be remapped with an explicit report. Equal names with different texts or provenance MUST remain distinct. Identical page revisions and dependency graphs MAY be deduplicated with recorded origins.

Migration MUST validate current original source identities and hashes, page hashes, complete transitive source coverage and dependency versions. Missing, withdrawn, stale, malformed or cyclic evidence MUST be quarantined in the snapshot with reasons, never published as current knowledge. Imported concepts and answer chains MUST participate in ordinary maintenance and query freshness checks. An unrelated saved answer MUST remain unchanged when an independent source changes.

Migration MUST be repeatable from its verified snapshot after interruption or indexing failure, without duplicate active answers or overwriting subsequent valid maintenance. Incomplete migration MUST block competing writes and report non-success. QMD MUST index eligible imports in the common collection without changing unrelated collections. Productive activation and retirement of legacy outputs remain a separate operation.

#### Scenario: Inventory and preserve historical knowledge
- **WHEN** the operator supplies empty production outputs, populated legacy outputs and older backups
- **THEN** inventory distinguishes them and records pages, unique answers, dependency versions and untracked content
- **AND** migration snapshots their original bytes and state before changing the destination

#### Scenario: Merge colliding names and dependent answers
- **WHEN** two valid pages share a name but differ in content or provenance and answers depend on concepts and other answers
- **THEN** migration preserves distinct texts, remaps links and dependency versions, and reports each origin and destination
- **AND** managed query retrieves the valid imported answer with original-source provenance without a private-domain exclusion

#### Scenario: Quarantine unsupported historical knowledge
- **WHEN** a historical page has stale, removed, incomplete, tampered or cyclic evidence
- **THEN** it and dependent pages remain inspectable in the snapshot with explicit reasons
- **AND** neither active Markdown nor managed QMD retrieval presents them as current knowledge

#### Scenario: Maintain and resume imported knowledge
- **WHEN** migration is interrupted or indexing fails
- **THEN** retry uses the verified snapshot and finishes without duplicate active answers or lost saved content
- **AND** later source correction reaches imported concepts and dependent answer chains while an independent answer remains byte-identical
