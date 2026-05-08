# DocWorkflow Agent Delivery Testsuite Delta

## ADDED Requirements

### Requirement: DWT-S5 L3 runtime temp-repo delivery pilot

The testsuite SHALL provide an L3 runtime temp-repo delivery pilot that runs or reproducibly blocks one DWT-S5 delivery against a synthetic disposable repository while preserving DWT-PR3, DWT-PR4 and DWT-PR5 controls.

#### Scenario: Temp repo is synthetic and isolated

- **GIVEN** accepted DWT-S3 retained evidence and a DWT-S5 implementation-ready Child Index row with a persisted handoff
- **WHEN** the DWT-S5 L3 runner materializes the target repository
- **THEN** the target repository SHALL be generated under the isolated run directory from source-controlled synthetic fixtures
- **AND** KI-fuer-KMU original repositories SHALL NOT be named as runtime targets, copied, built, tested, deployed or modified.

#### Scenario: Delivery kickoff validates DWT-S5 controls

- **GIVEN** the current DWT-S5 child spec, Child Index row, persisted handoff and retained DWT-S3 evidence
- **WHEN** the DWT-S5 delivery kickoff runs
- **THEN** the result SHALL pass only if the output targets DWT-S5, validates the current handoff, uses a concrete allowed write-set and points runtime work at the generated temp repo.

#### Scenario: Local runtime gate stays inside temp repo

- **GIVEN** a generated synthetic temp repo
- **WHEN** local runtime validation runs
- **THEN** command cwd, output and evidence SHALL remain under the run directory
- **AND** any local runtime gate outside the generated temp repo SHALL fail.

#### Scenario: Container or harness gate is honest

- **GIVEN** a generated synthetic temp repo and container/harness gate contract
- **WHEN** the container/harness gate runs or preflight detects unavailable runtime support
- **THEN** a successful gate SHALL record target evidence from the generated temp repo
- **AND** unavailable runtime support SHALL be reported as `blocked_runtime`, not as accepted L3 pass proof.

#### Scenario: Forbidden targets and secrets fail

- **GIVEN** output that names an original repository as runtime target, writes outside the run directory, copies credentials or exposes secret values
- **WHEN** DWT-S5 validation runs
- **THEN** the harness SHALL fail or block that output
- **AND** the summary SHALL identify the forbidden action class without persisting secret values.

#### Scenario: Closeout preserves parent controls

- **GIVEN** DWT-S5 runtime-temp-repo evidence
- **WHEN** closeout validation runs
- **THEN** Parent Coverage for `DWT-PR3`, `DWT-PR4` and `DWT-PR5` SHALL remain present
- **AND** DWT-S5 evidence, retained DWT-S3 predecessor evidence and OpenSpec ledger state SHALL remain distinguishable
- **AND** no descendant child SHALL be implementation-authorized by DWT-S5 closeout.
