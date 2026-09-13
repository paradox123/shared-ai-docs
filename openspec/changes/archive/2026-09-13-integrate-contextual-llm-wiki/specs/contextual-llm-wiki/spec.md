## ADDED Requirements

### Requirement: Pinned compiler integration

The integration MUST use Atomicstrata LLM-Wiki-Compiler at the selected baseline `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb` for knowledge compilation, initially using its default profile. It MUST expose an executable local interface for initialization, reconciliation/maintenance, status, query with optional persistence, and lint. It MUST verify compatible runtime and provider availability before content mutation and report the effective compiler version. It MUST NOT replace the actual compiler with a simulated implementation for acceptance.

#### Scenario: Setup and first compile
- **WHEN** a compatible runtime and configured provider are available and the operator initializes the integration
- **THEN** status identifies the pinned compiler and the real compiler processes the selected test sources
- **AND** an incompatible runtime or unavailable provider produces an actionable failure before active content changes

### Requirement: Initial DanielsVault source inventory

The delivered setup MUST include an explicit initial registration for the eight verified repository identities `vault-root`, `meeting-assistant`, `shared-ai-docs`, `ki-fuer-kmu`, `ncg-docs`, `private`, `probare-crm`, and `sparkle`, using the clone roots and source-zone filters defined in the local tracker input-repositories document and linked from the design. `private` and the vault's private project zone MUST be scoped to the private context. The vault root MUST ingest only its listed zones rather than recursively re-ingesting nested repositories. Existing extra worktrees and generated test repositories MUST NOT become additional sources.

Before the first compilation, setup MUST provide a read-only inventory of these configured entries, resolved roots, included Markdown counts, scope, exclusions, and missing inputs. Configuration of all eight entries MUST NOT imply that private sources are compiled into the general context. Both `Meetings` and `Projects` MUST be recursively included as initial Markdown source zones of the vault root. Meetings MUST NOT require additional per-meeting selection before ingestion. `Projects/Private` MUST also be ingested, using the private context rather than being omitted. Their mixed subject matter or lack of separate Git roots MUST NOT cause exclusion. General technical/runtime filters still apply. Only the historical SpecOps zone remains excluded from the initial configuration as documented.

#### Scenario: Bootstrap the actual vault source set
- **WHEN** the integration is set up against the verified DanielsVault layout
- **THEN** inventory lists the eight configured repository identities with the actual clone roots and their scope
- **AND** private inputs are listed separately without exposing private contents in the general report
- **AND** setup does not silently substitute a different checkout for a missing configured root

#### Scenario: Nested and duplicate checkouts do not duplicate input
- **WHEN** inventory encounters the selected nested repos, the additional shared-ai-docs checkout and generated plugin repos beneath test output
- **THEN** each selected Fachquelle belongs to one source identity only
- **AND** the extra checkout and generated test repos are excluded and reported as such

#### Scenario: Meetings and Projects are initial sources
- **WHEN** initial inventory and ingestion run with Markdown files in Meetings, Projects and Projects/Private
- **THEN** each file is inventoried and processed as a vault-root Fachquelle in its corresponding context
- **AND** generated knowledge can cite the original meeting or project file
- **AND** neither Meetings nor Projects is deferred as an optional future source

### Requirement: Explicit repository context and source isolation

The integration MUST identify context membership by stable repository identifiers and configured existing clone roots, with explicit recursive Markdown inclusion/exclusion rules. It MUST read original Fachquellen without modifying or moving them, preserve distinct identities for equal relative paths in different repos, and exclude generated output from its own input. Newly discovered unselected repos MUST NOT be silently included. Private contexts MUST require explicit selection and remain outside the general output and search scope.

#### Scenario: Two repositories with equal filenames
- **WHEN** two selected repos contain different documents at the same relative path and maintenance runs
- **THEN** both documents remain distinguishable by repository and path throughout source ingestion and citation
- **AND** original file hashes and repository working-tree state remain unchanged by the integration

#### Scenario: Unselected and private sources
- **WHEN** an unselected clone and a private test repo exist alongside the general context
- **THEN** neither their source contents nor derived knowledge appear in the general wiki or general-context query results

### Requirement: Directed source synchronization and provenance

The integration MUST provide real compiler-compatible source files through a directed adapter while retaining original repository identity, relative path, source hash, and observed source version. It MUST preserve source text and line mapping sufficiently for citations to resolve to the original Fachquelle. It MUST detect additions, changes, and confirmed removals and MUST NOT treat an incomplete or failed source scan as an authoritative empty source set.

Inputs exceeding an upstream ingestion limit MUST be ingested losslessly through a supported source path or explicitly rejected as incomplete; silent truncation MUST NOT be treated as successful synchronization.

#### Scenario: Original document is corrected
- **WHEN** a selected Markdown document changes and reconciliation completes its inventory
- **THEN** the compiler input reflects the new text and source version with a usable original-source reference
- **AND** affected outputs are scheduled for revalidation rather than merely assigning their metadata a new hash

#### Scenario: Source scan fails
- **WHEN** a root cannot be fully enumerated because of a read error
- **THEN** reconciliation reports failure or incompleteness without applying a mass removal from that incomplete inventory

#### Scenario: Large Markdown document
- **WHEN** a selected document exceeds the upstream text-ingest limit
- **THEN** the adapter either preserves its full content and original citation mapping or reports it as incomplete without publishing a falsely complete source state

### Requirement: Persistent cross-repository synthesis

The integration MUST generate and maintain interlinked Markdown knowledge using the real compiler, including a useful synthesis supported by multiple selected repos. It MUST preserve provenance, distinguish synthesized conclusions from source statements, and retain relevant differences or contradictions. Valid existing pages MUST remain available across queries and sessions without recompiling all sources for each question.

#### Scenario: Shared insight is reused
- **WHEN** two repo sources support a common conclusion and a later question asks about that topic
- **THEN** the wiki contains a coherent shared insight citing both original sources
- **AND** the later answer uses that active page as evidence without unnecessary recompilation

### Requirement: Dependency coverage for stored knowledge

Every active generated concept and persisted conversation synthesis MUST have sufficient recorded dependencies to trace its validity to the relevant source versions. Persisted answers based on generated pages MUST also record those page dependencies and their transitive source dependencies. Conservative dependency sets covering all actually supplied evidence are acceptable; silently treating unknown dependencies as absent is not. Unknown or incomplete provenance MUST prevent presentation as verified current knowledge.

#### Scenario: Save an answer based on a concept
- **WHEN** an answer uses a concept page derived from two repo sources and the operator requests persistence
- **THEN** the saved synthesis is linked to the concept version and both source versions
- **AND** it participates in the same change/removal checks as concept pages

#### Scenario: Incomplete dependency information
- **WHEN** a proposed saved answer lacks a defensible mapping to its evidence
- **THEN** it is not published as verified current knowledge and the unresolved provenance is reported

#### Scenario: Saved page changes independently of its original sources
- **WHEN** a saved synthesis is replaced while another saved synthesis depends on its previous page version
- **THEN** the dependent synthesis is ineligible as current evidence until revalidated
- **AND** saving a direct or indirect dependency cycle is rejected before replacing active content

### Requirement: Targeted direct and indirect revalidation

After reconciliation detects a changed Fachquelle, the integration MUST identify directly and transitively dependent active pages and provide a human-readable reason, including affected cited passages when available. Maintenance MUST revalidate those pages against current evidence, correct or withdraw unsupported statements, and propagate resulting changes through dependent saved syntheses. It MUST NOT consider merely updating source metadata to be revalidation. Unrelated valid pages MUST avoid unnecessary model recompilation or content revisions.

#### Scenario: Source concept and answer chain
- **WHEN** a source correction invalidates a claim in a concept page used by a persisted answer
- **THEN** the maintenance report identifies both affected pages and the changed evidence
- **AND** maintenance corrects or removes the old claim in both active outputs while leaving an independent control page unchanged

### Requirement: Context removal and reconstruction

When a complete inventory confirms removal of a selected source/repo or context configuration explicitly deselects it, knowledge depending on the removed input MUST disappear from the active wiki, its navigation, managed agent evidence, and managed QMD search results. An orphan flag alone MUST NOT satisfy this requirement. Mixed concept pages MUST be withdrawn pending regeneration from remaining sources; independently supported knowledge MUST remain or be republished after that regeneration. Persisted answers with a removed required dependency MUST be withdrawn. Restoring the repo MUST allow new generation from its current sources without assuming the old result remains valid.

#### Scenario: Remove one of two source repos
- **WHEN** one repo supporting a shared concept and saved answer leaves the context
- **THEN** no active access path returns the removed-source-dependent claim or saved answer
- **AND** an unrelated page stays active and any regenerated shared page is supported only by remaining inputs

#### Scenario: Repo returns later
- **WHEN** the repo is selected and available again and maintenance runs
- **THEN** its current source version can produce new concept and answer content with fresh provenance
- **AND** no historical page is silently restored as current solely because its old filename exists

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

### Requirement: Common human and agent entry

The integration MUST expose a Markdown entry page usable in the existing Obsidian vault and a managed agent workflow using the same active wiki. Generated content MUST live without initializing its own Git repository or placing generated files under existing tracked source ownership. Wiki and original-source links MUST resolve. The agent workflow MUST validate context/freshness eligibility and prefer relevant active wiki evidence, using source fallback for gaps. Pending or contradictory knowledge MUST be visibly distinguished from checked current statements.

Before using a page as current evidence, the managed agent workflow MUST verify its relevant original-source availability and versions against the recorded dependencies, not merely inspect unchanged mirror files. A detected difference MUST expose pending maintenance or use current source evidence without certifying the stale page.

#### Scenario: Browse and ask
- **WHEN** a person opens the wiki in Obsidian and an agent asks about the same topic through the integration
- **THEN** both can reach the same active synthesized page and the original supporting files
- **AND** the entry page shows last completed maintenance and outstanding review needs

#### Scenario: Query before source synchronization
- **WHEN** an original source has changed since the last successful maintenance but its compiler mirror has not yet been updated
- **THEN** a managed query does not present the dependent wiki page as verified current evidence
- **AND** it reports pending maintenance or answers from current original sources with that distinction visible

### Requirement: Explicit maintenance and idempotence

The initial integration MUST run reconciliation, affected-page refresh, lint, and search synchronization through an explicit maintenance invocation. It MUST NOT require or install a filesystem watcher or new scheduler as part of this change. Repeating a successful invocation without changed inputs MUST avoid model recompilation, duplicate pages, and unnecessary knowledge revisions. Queries without a save request MUST NOT create new durable answer pages.

#### Scenario: Repeat unchanged operation
- **WHEN** maintenance is invoked twice against the same successful source/context state
- **THEN** the second invocation reports no content work and creates no duplicate page, knowledge revision, or model compile request

### Requirement: Observable failure and safe resumption

The integration MUST expose source, page, and indexing progress with actionable failure details and a non-success result when required work remains. It MUST publish only complete prepared page results; a partial generation MUST NOT appear as a completed current page. It MUST retain enough pending-work state to resume without losing source changes, serialize concurrent writes to the same context, and detect input changes during processing. Managed agent retrieval MUST reject withdrawn or unverified content even after an interrupted refresh/removal.

#### Scenario: Provider or indexing failure
- **WHEN** a provider or QMD operation fails during maintenance
- **THEN** status distinguishes completed work from pending work and no false successful completion is reported
- **AND** a subsequent invocation finishes from the actual source state without lost changes or duplicate outputs

#### Scenario: Input changes while generation runs
- **WHEN** the current source hash differs from the captured generation input before publication
- **THEN** that result is not published as checked against the newer source and the latest change remains pending

### Requirement: Local restoration respects current context

The delivered operating workflow MUST support a local backup/restore of wiki pages and their dependency state without requiring a wiki Git repository. Restored content MUST be reconciled with the currently selected available repos before becoming active evidence. Restoring unique conversation syntheses MUST retain their provenance; exact reproduction of LLM text from raw sources alone MUST NOT be promised.

#### Scenario: Restore into a smaller context
- **WHEN** a saved local state contains an answer depending on a repo that is no longer selected
- **THEN** restoration preserves the ability to inspect the backup but does not publish that answer into the active wiki or search

#### Scenario: Restore cannot run its required reconciliation
- **WHEN** the runtime or configured provider is unavailable before restoration
- **THEN** restoration fails before changing active wiki content

### Requirement: End-to-end acceptance evidence

Completion MUST include a concise human-readable acceptance overview linking each requirement to expected behavior, observed result, and supporting evidence. Tests MUST exercise the public integration interface and real compiler; deterministic provider substitution is limited to the provider boundary, with at least one real-provider synthesis run. Actual QMD search and Obsidian browsing MUST be verified. Unexecuted or failed criteria MUST remain explicit and MUST NOT be represented as passed by document validation or startup checks.

#### Scenario: Implementation is presented for acceptance
- **WHEN** the integration is reported ready
- **THEN** evidence covers source isolation, synthesis reuse, source correction through a saved answer, repo removal/readdition, QMD-only retrieval, interruption recovery, and Obsidian navigation
- **AND** unmet criteria, including missing provider or UI access, are stated with the lower-level verification actually performed
