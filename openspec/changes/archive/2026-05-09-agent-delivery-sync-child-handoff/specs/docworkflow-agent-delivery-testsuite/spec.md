## ADDED Requirements

### Requirement: Child handoff synchronization tool

The testsuite SHALL provide a deterministic local .NET file-based tool that generates, checks and synchronizes one Child Session Handoff from one exact operational Child Index row.

#### Scenario: Missing handoff is generated from Child Index

- **GIVEN** a Child Index fixture with an exact operational row for a stable child id
- **AND** the requested handoff path is missing
- **WHEN** `SyncChildHandoff.cs` runs with `--write`
- **THEN** it SHALL create the requested handoff file
- **AND** the generated handoff SHALL include child id, child spec, Child Index / Queue, target repository, next skill, current verdict, allowed write-set, verification and evidence/OpenSpec fields derived from the row and CLI inputs.

#### Scenario: Current handoff passes check

- **GIVEN** an existing handoff whose controlled fields match the Child Index row and CLI inputs
- **WHEN** `SyncChildHandoff.cs` runs with `--check`
- **THEN** it SHALL exit `0`
- **AND** it SHALL report status `current`.

#### Scenario: Stale controlled field blocks check

- **GIVEN** an existing handoff whose current verdict differs from the Child Index row
- **WHEN** `SyncChildHandoff.cs` runs with `--check --format json`
- **THEN** it SHALL exit `1`
- **AND** the JSON findings SHALL include `FIELD_DRIFT` for `Aktueller Verdict`.

#### Scenario: Dry run does not write

- **GIVEN** an existing stale handoff
- **WHEN** `SyncChildHandoff.cs` runs with `--dry-run`
- **THEN** it SHALL print the proposed synchronized handoff
- **AND** it SHALL leave the existing handoff bytes unchanged.

#### Scenario: Manual notes are preserved by explicit section

- **GIVEN** an existing handoff with a section named `## Notes Preserved By Sync`
- **WHEN** `SyncChildHandoff.cs` runs with `--write`
- **THEN** it SHALL rewrite controlled fields from the Child Index row
- **AND** it SHALL preserve that section and all following text verbatim.

#### Scenario: Approximate write-set blocks synchronization

- **GIVEN** a Child Index row whose `Allowed Write-Set` contains approximate language such as `TBD`, `likely`, `as needed` or `etc.`
- **WHEN** `SyncChildHandoff.cs` runs without `--allow-approx-write-set`
- **THEN** it SHALL exit `1`
- **AND** it SHALL report `APPROX_WRITE_SET`.
