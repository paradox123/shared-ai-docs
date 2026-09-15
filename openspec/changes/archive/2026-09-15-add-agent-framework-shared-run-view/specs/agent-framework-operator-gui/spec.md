## ADDED Requirements

### Requirement: Shared run entry uses confirmed analysis state
The Operator Client SHALL open saved requirements in one shared run view with title, source and confirmed public analysis state. Result, history, files and immutable requirements SHALL remain directly accessible views of that run, preserving existing content, concrete diagnostics, selection and keyboard focus through updates and recovery.

#### Scenario: Open and observe one shared run view (UX-01)
- **WHEN** a human opens saved requirements, observes their analysis, changes the selection or reopens the same run
- **THEN** a common title, source and analysis state precede the selected result view; result, history, files and immutable requirements are directly selectable views of the same run
- **AND** list and header use confirmed public execution states: admitted without a run, queued, running, reconciling, completed analysis or failed; an unknown state remains unknown and a run ID alone never means running or started
- **AND** completed analysis claims neither implementation, review nor overall workflow completion; retained results or concrete failures are available without scrolling through the full requirements or long findings lists
- **AND** a reconciling execution retains its recorded diagnostic code and explanation until a result is available, without presenting the uncertain outcome as a terminal failure
- **AND** execution changes and reconnects update both displays consistently; connection loss labels the last confirmed state as stale, remains distinct from execution failure and result reconciliation, and retries without requiring a new selection
- **AND** late responses from a previous selection cannot replace the current run's contents; intake/start, all existing session/history/artifact/source data, the selected view and keyboard focus remain accessible through updates
- **AND** keyboard navigation has understandable names, and title, state and navigation remain readable at 390 and 1024 pixels without horizontal page scrolling
- **AND** acceptance compares real persisted public responses with browser opening, state transition and reopening on both viewports; controlled transport/state cases supplement rather than replace persisted-data evidence
