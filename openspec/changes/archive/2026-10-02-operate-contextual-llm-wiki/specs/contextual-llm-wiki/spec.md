## REMOVED Requirements

### Requirement: Pinned compiler integration

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Initial DanielsVault source inventory

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Explicit repository context and source isolation

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Directed source synchronization and provenance

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Persistent cross-repository synthesis

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Dependency coverage for stored knowledge

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Targeted direct and indirect revalidation

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Context removal and reconstruction

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: QMD is the sole persisted retrieval engine

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Common human and agent entry

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Explicit maintenance and idempotence

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Observable failure and safe resumption

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: Local restoration respects current context

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

### Requirement: End-to-end acceptance evidence

**Reason**: The accepted decision of 2026-10-02 replaces the compiler architecture and its global state contracts. The previous compiler contracts are preserved in the verified external cleanup backup; current canonical specifications define direct Markdown maintenance.

**Migration**: Preserve legacy content and evidence in a verified backup, then maintain selected curated pages through direct original-source review under the replacement requirements below.

## ADDED Requirements

### Requirement: Direct agent-managed common Markdown wiki
The LLM wiki MUST be maintained as interlinked Markdown directly by the agent through the shared `maintain-llm-wiki` skill. Maintenance MUST start from an explicit task selecting topics, sources or pages, respect explicit source limits and preserve original files. All task-relevant subject domains MAY contribute to one common wiki, including cross-repository syntheses involving `private`. A domain name MUST NOT create an implicit exclusion. The active wiki MUST retain its existing `common/wiki` location without a separate Git repository, with curated knowledge in `notes/` and navigable `index.md` and `log.md`. Compiler execution, source mirrors, a global source import and a transitive saved-answer graph MUST NOT be prerequisites for maintaining a selected page.

#### Scenario: Maintain a selected cross-repository topic
- **WHEN** the user requests a topic supported by relevant personal and professional original documents
- **THEN** the agent reads those originals and maintains a common Markdown note citing them directly
- **AND** an unrelated source is not included merely because it belongs to the vault
- **AND** original files remain unchanged

#### Scenario: Repeat an already satisfied request
- **WHEN** selected sources and the checked page content need no correction
- **THEN** the agent reports that outcome without rewriting knowledge merely to create work
- **AND** it does not start a full import or compiler run

### Requirement: Direct original provenance and content review
Every curated knowledge page MUST document all direct original sources supporting its statements, including distinguishable vault-relative source paths, content SHA-256 hashes in the single JSON-valued `wiki_sources` frontmatter field and a `reviewed_at` timestamp. Page prose MUST link to the relevant originals and distinguish source statements from inferred conclusions, uncertainties and contradictions. If a wiki note informs another note, the agent MUST verify and record the actually supporting originals directly. Incomplete provenance MUST remain an explicit review need. Hash equality MUST NOT be treated as truth certification. The agent MUST read current original contents and verify the page before recording a reviewed source state; changing hashes alone MUST NOT count as review.

#### Scenario: Another note provides a useful lead
- **WHEN** an agent uses an existing wiki note to prepare a related note
- **THEN** it reads the relevant supporting originals and records those originals as direct dependencies
- **AND** it does not require a stored page-to-page graph

#### Scenario: A source changes or disappears
- **WHEN** a recorded original changes, is missing or cannot be read
- **THEN** the page has a visible review need and is not relied on as checked current evidence
- **AND** maintenance corrects, qualifies or removes unsupported selected-page statements after inspecting available originals

### Requirement: QMD retrieval with original authority
QMD MUST remain the sole persisted retrieval engine for wiki and source search. Agents MUST search task-relevant original-source collections and MAY include the curated common-wiki collection, then inspect relevant original passages before relying on a claim. An already named original MAY be read directly. Before relying on a wiki note, the agent MUST check its recorded original-source state; stale, invalid or unrecorded provenance MUST lead to original-source research with that limitation visible. Ordinary research MUST NOT implicitly persist answers, update metadata or maintain the wiki. WikiQuery MUST be retired from active routing. Source mirrors, legacy backups and acceptance fixtures MUST NOT be indexed as active wiki knowledge; unrelated collections MUST remain intact.

#### Scenario: A fresh-looking search result has a changed original
- **WHEN** QMD returns a note whose original has changed after its last review
- **THEN** the source check identifies review need and the agent reads the current original
- **AND** it does not certify the note from QMD status or index freshness

#### Scenario: Ordinary context research
- **WHEN** the user asks a question without requesting wiki maintenance or saving
- **THEN** the agent retrieves and verifies relevant evidence through QMD and direct original reading
- **AND** it creates no durable wiki page or new reviewed timestamp

### Requirement: Common navigation and page-local acceptance
Human and agent use MUST share the same active Markdown wiki and resolvable original links. Navigation MUST identify available curated pages and the log MUST describe completed selected work and remaining review needs. Success MUST be stated for the actual selected scope with content, provenance and link evidence. A successful selected page MUST NOT imply completion of other pages, a global import or a daily wiki freshness guarantee. Failed historical imports MUST remain recorded as failures. Requirements verification MUST distinguish helper checks, content review, migration evidence and any unexecuted criteria.

#### Scenario: Report a completed page while other work remains
- **WHEN** one selected page has been reviewed and another selected page lacks supporting evidence
- **THEN** the report identifies the completed page and the unresolved page separately
- **AND** it does not claim the full request or a global wiki import succeeded

### Requirement: Preserve legacy knowledge before replacement
Before legacy active content is retired, the migration MUST preserve all original legacy wiki bytes and required state in a verified backup outside indexed roots. The migration MUST inspect valuable notes and conversation syntheses, retain their original provenance in the backup, and only publish selected curated pages after current original-source review. Missing or unsupported historical evidence MUST stay inspectable with reasons rather than be presented as current. Source files MUST NOT be moved or changed. Active compiler output and wiki-owned obsolete source-mirror or acceptance collections MUST be retired while the active `contextual-wiki-common` collection and unrelated collections remain available. Restoration of historical bytes MUST NOT itself certify current knowledge.

#### Scenario: Preserve a valuable old synthesis
- **WHEN** a legacy conversation synthesis contains useful knowledge and stale original versions
- **THEN** the original synthesis and its historical state remain in the verified backup
- **AND** only a page reviewed against current originals enters the curated active wiki

#### Scenario: Read a restored historical page
- **WHEN** an old backup page is inspected or restored
- **THEN** its historic content remains distinguishable from a currently reviewed curated page
- **AND** it does not become checked current evidence solely because restoration succeeded
