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

#### Scenario: Repair after an isolated failure
- **WHEN** an established dependency branch fails while an independent source is corrected
- **THEN** the independent page is published and indexed, but directly and transitively dependent concepts and saved answers remain unavailable as current wiki evidence
- **AND** local run evidence records completed, unchanged, failed and pending work with a non-success exit
- **AND** after repair only pending compilation is retried and the next unchanged run is a no-op

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
