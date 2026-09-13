## ADDED Requirements

### Requirement: Automatically adopt verified upstream wiki revisions
The local wiki installation MUST follow regular published releases of the upstream LLM Wiki repository as a whole. Candidates MUST satisfy the canonical "Reproducible upstream wiki release qualification" requirement before adoption. Release detection and local activation MUST preserve the candidate's exact commit and upstream-defined dependency versions, without independently updating compiler libraries, Node, QMD or wrapper dependencies.

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

### Requirement: Transactional local activation of qualified releases
The public update command MUST activate only the concrete candidate whose required checks all passed and whose full runtime contents still match qualification. Changes to wrapper, compiler build, installed dependencies or runtime MUST require renewed qualification. Adoption MUST require no renewed human approval. The active runtime MUST be a separate verified snapshot selected atomically, preserving the prior working runtime.

Activation MUST verify the actually selected release and commit through the running runtime and a bounded public wiki operation, including preserved pages, saved synthesis, provenance and reusable state from the prior runtime. An identity manifest alone MUST NOT prove activation. Existing production wiki data MUST remain unchanged during activation. Releases needing unsupported data migration MUST fail compatibility verification; any future supported data migration MUST include recoverable affected data before activation is allowed.

Concurrent updates and public wiki use MUST share an exclusive process-lifetime lock so no mixed runtime or overlapping state changes occur. Repeated activation of the same unchanged qualified runtime MUST be a no-op. Failed switching or functional verification MUST restore the prior selection and clearly report non-success and the retained active identity. Interrupted provisional activation MUST be recovered before subsequent public use. Success, no-op and deliberate activation failure MUST be demonstrated on the Mac without modifying knowledge maintenance or its scheduler.

#### Scenario: Activate only unchanged qualified bytes
- **WHEN** a candidate passes every check and its complete runtime matches the recorded qualification
- **THEN** the updater snapshots and activates that exact runtime without another human approval
- **AND** any changed candidate or incomplete check is rejected before replacing the prior runtime

#### Scenario: Verify activation and preserve knowledge
- **WHEN** the selection switches to the candidate
- **THEN** the running runtime reports the expected release and commit and reads prior-runtime fixture knowledge with checked original-source provenance
- **AND** saved synthesis and reusable state survive a no-op maintenance run and a controlled source correction is propagated using the prior compiler state, while production data remain untouched

#### Scenario: Fail or interrupt activation
- **WHEN** switching or the activation probe fails or is interrupted
- **THEN** the prior runtime is restored before ordinary use and the result reports failure and the retained identity

#### Scenario: Repeat or overlap activation
- **WHEN** the same unchanged candidate is supplied again
- **THEN** activation reports a no-op
- **AND** overlapping updates and wiki commands fail visibly as busy without overlapping runtime or state changes

### Requirement: Scheduled wiki maintenance before global retrieval maintenance
The existing local daily QMD automation MUST maintain one common production wiki over all selected source repositories, including `private`, `Projects/Private`, Meetings and Projects, before subsequent QMD retrieval maintenance. It MUST preserve the existing schedule, model, project and notification settings. The name `private` MUST describe a subject domain only and MUST NOT cause a separate wiki, a maintenance exclusion, a special query approval or a confidentiality classification. The automation MUST NOT substitute acceptance fixtures for the full production inventory. No additional scheduler or watcher SHALL be installed.

#### Scenario: Successful daily run
- **WHEN** source reconciliation and wiki maintenance succeed
- **THEN** the common wiki is maintained and checked before global QMD update, embed and status
- **AND** the report distinguishes compiled content, no-op work and retrieval maintenance

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
