## MODIFIED Requirements

### Requirement: Initial DanielsVault source inventory
The delivered setup MUST register the eight verified repository identities `vault-root`, `meeting-assistant`, `shared-ai-docs`, `ki-fuer-kmu`, `ncg-docs`, `private`, `probare-crm`, and `sparkle`, using their configured original clone roots and source-zone filters. All selected repositories MUST feed one common wiki. Both `Meetings` and `Projects`, including `Projects/Private`, MUST be recursively included. `private` is a subject-domain label and MUST NOT partition the compiled knowledge or exclude sources from ordinary managed retrieval. Historical SpecOps and technical/runtime exclusions remain as documented; extra worktrees MUST NOT become additional sources.

Before first compilation, setup MUST provide a read-only inventory of the configured entries, resolved roots, selected Markdown counts, exclusions and missing inputs. Configuration MUST NOT silently substitute another checkout for a missing root.

#### Scenario: Bootstrap the actual vault source set
- **WHEN** setup inventories the verified DanielsVault layout
- **THEN** it lists the eight configured repository identities and selected source counts
- **AND** sources from personal and professional domains belong to the same production input set

#### Scenario: Nested and duplicate checkouts do not duplicate input
- **WHEN** inventory encounters selected nested repos, additional checkouts and generated plugin repos beneath test output
- **THEN** each selected Fachquelle belongs to one source identity only
- **AND** extra checkouts and generated test repos are excluded and reported

#### Scenario: Meetings and Projects are initial sources
- **WHEN** Markdown exists in Meetings, Projects and Projects/Private
- **THEN** it is recursively inventoried and processed as vault-root Fachquellen in the common wiki
- **AND** derived knowledge can cite the original files without per-meeting or private-domain approval

### Requirement: Explicit repository context and source isolation
The integration MUST identify source membership by stable repository identifiers and explicitly configured original clone roots, with recursive Markdown inclusion/exclusion rules. It MUST read Fachquellen without modifying or moving them, preserve distinct identities for equal relative paths in different repos, and exclude generated output from its own input. Newly discovered unselected repos MUST NOT be silently included. The `private` repository and `Projects/Private` MUST be treated as subject areas within the common selected source set rather than as separate access scopes. Explicit task or source limits MUST still be respected; no access or disclosure policy SHALL be inferred solely from a domain name.

#### Scenario: Two repositories with equal filenames
- **WHEN** two selected repos contain documents at the same relative path and maintenance runs
- **THEN** both remain distinguishable by repository and path through ingestion and citation
- **AND** original files and repository working-tree state remain unchanged by maintenance

#### Scenario: Selected private domain and unselected repository
- **WHEN** the selected private repository and an unselected clone exist beside other selected sources
- **THEN** the private-domain sources participate in the common wiki while the unselected clone does not
- **AND** task-relevant evidence may link private-domain and other selected sources without special private-mode approval

### Requirement: Persistent cross-repository synthesis

The integration MUST generate and maintain interlinked Markdown knowledge using the real compiler, including a useful synthesis supported by multiple selected repos. It MUST preserve provenance, distinguish synthesized conclusions from source statements, and retain relevant differences or contradictions. Valid existing pages MUST remain available across queries and sessions without recompiling all sources for each question.

#### Scenario: Shared insight is reused
- **WHEN** two repo sources support a common conclusion and a later question asks about that topic
- **THEN** the wiki contains a coherent shared insight citing both original sources
- **AND** the later answer uses that active page as evidence without unnecessary recompilation

#### Scenario: Task-relevant synthesis across personal and professional domains
- **WHEN** a selected source about personal portfolio planning and a selected source about project income support a relationship relevant to the task
- **THEN** the common wiki can synthesize that relationship citing both original sources
- **AND** an unrelated control source is not used merely because it shares a term or belongs to the same domain

### Requirement: QMD is the sole persisted retrieval engine

The integration MUST use the existing QMD engine and explicit context-scoped collections for persisted search and embeddings. It MUST prevent creation/use of a separate compiler vector or persisted lexical retrieval index in all managed compile, query, and save paths. Markdown navigation, source manifests, dependency records, and operational hashes are not retrieval indexes and MUST remain supported. Source mirrors and runtime/history files MUST NOT be indexed as a second copy of active wiki knowledge. Wiki-owned collection changes MUST NOT silently repoint or remove unrelated collections.

#### Scenario: Compile query save and search
- **WHEN** a context is compiled, queried, and an answer saved
- **THEN** the active Markdown knowledge is searchable through QMD without a separate compiler embedding/search store
- **AND** the compiler Markdown index remains usable as the wiki navigation page

#### Scenario: Removed knowledge was previously indexed
- **WHEN** a formerly indexed page is withdrawn during context reconciliation
- **THEN** the managed QMD results no longer return its content after successful reconciliation
- **AND** an indexing failure is reported as incomplete maintenance rather than a successful removal

#### Scenario: Domain names do not hide common wiki evidence
- **WHEN** a common wiki page depends on a source in `private` or `Projects/Private`
- **THEN** the page remains eligible for ordinary managed retrieval when current and relevant to the task
- **AND** its domain label does not create a separate excluded wiki collection or a special private query requirement
