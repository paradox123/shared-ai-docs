## MODIFIED Requirements

### Requirement: Observable serialized maintenance with bounded failures
Wiki maintenance MUST be explicitly requested and limited to the selected topics, sources or pages. The agent MUST avoid overlapping edits to the same selected pages, publish complete reviewed Markdown results and report unresolved pages or sources accurately. Independent reviewed pages MAY complete despite a different page needing review. The active workflow MUST NOT require compiler-owned processes, global extraction queues, transitive publication locks or a global import completion timestamp. An unchanged reviewed scope MUST avoid unnecessary knowledge rewriting. The existing daily QMD job MUST remain independent of manual wiki work.

#### Scenario: Independent selected pages
- **WHEN** one selected page can be verified and another lacks an original
- **THEN** the agent may finish the verified page and reports the other page as unresolved
- **AND** it does not claim complete success for the selected request

#### Scenario: Concurrent work targets one page
- **WHEN** two agent tasks would edit the same wiki page
- **THEN** they coordinate ownership before mutation and avoid overlapping replacements

## ADDED Requirements

### Requirement: Deterministic direct-source check and record interface
The shared skill MUST provide a public local helper `wiki_sources.py` with `check --vault PATH --wiki PATH [--page PAGE]` and `record --vault PATH --wiki PATH --page PAGE --source ORIGINAL`; the check page option and record source option MUST be repeatable. Default checking MUST cover curated Markdown under `notes/`; navigation and logs MUST NOT be treated as knowledge pages. Explicit page selection MUST restrict the checked scope. Check MUST be read-only, compare direct current originals with recorded SHA-256 values, and report per-page `unchanged`, `review` or `invalid`. Changed or missing originals MUST produce review need; malformed or missing dependency metadata and unsafe paths MUST be invalid. Check MUST exit 1 if any checked page requires review or is invalid and exit 0 only for unchanged valid selected pages. Paths outside the declared vault or wiki, wiki pages used as originals and technical source mirrors MUST NOT be accepted as direct original dependencies. No provider, compiler, index mutation or automatic page refresh MAY occur during check.

Record MUST validate the selected page and all supplied readable originals before updating the single JSON-valued `wiki_sources` field and `reviewed_at`. The field MUST contain objects with vault-relative `path` and content `sha256`. The caller MUST first verify the page against the current original text; helper success alone MUST NOT claim content correctness. Failed validation MUST leave the existing page unchanged.

#### Scenario: Compare selected original versions without writes
- **WHEN** check sees one unchanged page, one changed original and one missing original
- **THEN** it reports unchanged for the first and review for the others, exits 1 and leaves all files unchanged

#### Scenario: Reject invalid metadata or paths
- **WHEN** a selected note has malformed dependencies, an escaped path or an alleged original that is a wiki page or technical mirror
- **THEN** check reports invalid with non-success
- **AND** record does not replace existing page metadata for invalid supplied originals

#### Scenario: Limit check to one page
- **WHEN** the caller selects one valid unchanged note while a different note has stale sources
- **THEN** check reports only the selected page and exits 0

#### Scenario: Record after agent content review
- **WHEN** the agent has read all supplied current originals and checked the selected page
- **THEN** record stores their hashes and the review timestamp while preserving page prose
- **AND** a subsequent unchanged check reports unchanged without certifying the truth of the page

### Requirement: One shared wiki maintenance skill
The canonical `maintain-llm-wiki` skill MUST guide explicit ingestion, update and review work through direct original reading, selected-page editing, deterministic source checks and navigation/log upkeep. It MUST be available through the existing global shared-skill symlink arrangement. Ordinary questions MUST route through documentation research rather than silently invoke maintenance. The obsolete compiler implementation, entrypoints, dependencies and release scheduler MUST be removed from active delivery and routing. Obsolete test wikis, plans, tickets, worktrees and runtime files MUST be removed after preserving required historical knowledge outside indexed roots. Current original files, the maintained common wiki, its shared skill and the QMD-only job MUST remain available.

#### Scenario: User requests wiki maintenance
- **WHEN** the user asks to ingest, revise or review a named topic or page
- **THEN** the shared skill selects the relevant originals and produces reviewed Markdown with direct provenance
- **AND** completion reports the selected scope and any remaining needs

#### Scenario: Inspect the cleaned installation
- **WHEN** the operator inspects active repositories, wiki folders and scheduler jobs
- **THEN** no obsolete compiler implementation, entrypoint, test wiki or release scheduler remains
- **AND** the shared maintenance skill, curated common wiki and independent QMD index remain usable

### Requirement: Scheduled QMD index maintenance independent of wiki work
The existing local daily QMD automation MUST reconcile the checked-in QMD collection manifest and run QMD update, embedding and status independently of wiki content maintenance. It MUST NOT invoke the wiki skill, helper record command, legacy compiler, provider or runner. It MUST preserve its existing schedule, model, project and notification settings and MUST NOT add another scheduler. Indexing generated bytes MUST NOT be described as content review or current wiki knowledge. No daily wiki freshness target or global initial-import obligation applies. Each runner step MUST own its process group and terminate its owned descendants before reporting a timeout. A timed-out step MUST remain non-success and MUST NOT leave index-mutating child processes running.

#### Scenario: Daily QMD run while a note needs review
- **WHEN** a wiki note needs original-source review and the daily QMD job succeeds
- **THEN** the job reports index maintenance success and the note still needs content review
- **AND** no wiki generation or metadata update is started

#### Scenario: A QMD descendant outlives its immediate parent
- **WHEN** a runner step times out while its helper has launched a QMD child
- **THEN** the runner terminates the owned process group before reporting timeout completion
- **AND** the report remains non-success and the child cannot continue index mutation

### Requirement: Verified context adoption catalog
The adoption catalog MUST identify actual maintained skill and agent entry paths, their intended role and adoption status. It MUST distinguish canonical files from aliases, history and vendor content. Active routing MUST use task-relevant QMD original collections with optional curated wiki evidence and direct original verification. Explicit task limits MUST apply. Historical WikiQuery proposals MUST remain historical rather than current instructions.

#### Scenario: Read planned context adoption
- **WHEN** the operator reads the catalog
- **THEN** current central routing and proposed additional entry changes are clearly distinguished
- **AND** a proposal is not represented as already installed
