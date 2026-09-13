## ADDED Requirements

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

### Requirement: Observable serialized maintenance with bounded failures
The maintenance helper MUST serialize runs, persist command stdout, stderr and exit status in a unique local artifact directory, and emit a compact machine-readable final report. It MUST validate result contracts rather than trusting exit codes alone. A bounded failure MUST block affected outputs and dependent work while permitting independent maintenance and safely executable QMD maintenance to continue. A partial run MUST report non-success, the failed work and what remains pending. Missing evidence, invalid responses and incomplete scans MUST NOT be treated as valid current knowledge or confirmed source removal. Shared failures MUST block every dependent operation. Repeated successful runs MUST preserve no-op behavior.

#### Scenario: Bounded source or compilation failure
- **WHEN** one source or dependent synthesis cannot be processed but other work is independent
- **THEN** affected knowledge is not exposed as verified current evidence
- **AND** independent maintenance can complete with a partial-failure report
- **AND** QMD work proceeds only over states whose eligibility can be established

#### Scenario: Shared failure or unknown dependencies
- **WHEN** a shared runtime or index fails, or the affected work cannot be safely separated
- **THEN** the operations depending on that failed prerequisite stop visibly
- **AND** neither empty output nor an incomplete scan is interpreted as success or mass removal

#### Scenario: Unchanged or concurrent run
- **WHEN** an unchanged wiki is maintained again
- **THEN** the no-op outcome is reported and QMD maintenance still completes
- **AND** a concurrent invocation fails visibly without overlapping mutations

### Requirement: Verified context adoption catalog
The delivery MUST catalog actual relevant maintained skills, AGENTS/README/CONTEXT and other agent entry files, with priority, intended role and adoption status. It MUST distinguish canonical files from aliases, history and vendor content. Proposed routing MUST use the common wiki with freshness validation, relevance to the concrete task, current-source fallback and original-source authority. Explicit task/source limits MUST be respected. The label `private` alone MUST NOT exclude evidence or require a separate query mode.

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
