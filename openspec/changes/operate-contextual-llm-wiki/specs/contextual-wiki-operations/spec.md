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

### Requirement: Verified context adoption catalog
The delivery MUST catalog actual relevant maintained skills, AGENTS/README/CONTEXT and other agent entry files, with priority, intended role and adoption status. It MUST distinguish canonical files from aliases, history and vendor content. Proposed routing MUST use the common wiki with freshness validation, relevance to the concrete task, current-source fallback and original-source authority. Explicit task/source limits MUST be respected. The label `private` alone MUST NOT exclude evidence or require a separate query mode.

#### Scenario: Operator plans context adoption
- **WHEN** the operator reads the catalog
- **THEN** each proposed surface has an existing path, rationale and concrete intended change
- **AND** proposed entries are not represented as already installed routing
- **AND** private-domain evidence is selected or omitted by task relevance rather than an inferred access policy
