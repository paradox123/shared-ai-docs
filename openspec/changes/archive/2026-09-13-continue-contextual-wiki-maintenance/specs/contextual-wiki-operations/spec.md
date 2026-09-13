## ADDED Requirements

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
