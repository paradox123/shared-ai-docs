## ADDED Requirements

### Requirement: Orchestration pack validation tool

The testsuite SHALL provide a deterministic local validator for Agent Delivery orchestration packs that rejects malformed Child Index structures, stale artifact pointers, inconsistent hardening queues, contradictory next actions, and unsupported workflow advancement claims.

#### Scenario: Valid orchestration pack passes

- **GIVEN** an orchestration pack with the exact operational Child Index columns
- **AND** every referenced child spec and handoff file exists
- **AND** the Hardening Queue agrees with the Child Index verdicts
- **WHEN** `ValidateOrchestrationPack.cs` validates the pack
- **THEN** it SHALL exit `0`
- **AND** JSON output SHALL include `schema: agent-delivery.validate-orchestration-pack.v1`
- **AND** JSON output SHALL include `valid: true`.

#### Scenario: Missing handoff fails

- **GIVEN** an orchestration pack whose Child Index references a missing Session Handoff file
- **WHEN** `ValidateOrchestrationPack.cs` validates the pack
- **THEN** it SHALL exit `1`
- **AND** JSON output SHALL include a finding with code `missing-handoff` and the affected child id.

#### Scenario: Stale next action fails

- **GIVEN** an orchestration pack whose Child Index row says `NEEDS HARDENING`
- **AND** that same row routes directly to `spec-change-delivery`
- **WHEN** `ValidateOrchestrationPack.cs` validates the pack
- **THEN** it SHALL exit `1`
- **AND** JSON output SHALL include `status-next-action-mismatch`.

#### Scenario: Compressed child index fails

- **GIVEN** an orchestration pack that uses compressed or aliased Child Index columns such as `Slice`, `Status`, or `Implementation Gate`
- **WHEN** `ValidateOrchestrationPack.cs` validates the pack
- **THEN** it SHALL exit non-zero
- **AND** output SHALL name the compressed or aliased Child Index columns.

#### Scenario: False advancement claim fails

- **GIVEN** an orchestration pack that explicitly claims the workflow advanced, hardening started, launch happened, delivery started, or closeout was accepted
- **AND** the pack contains only queue/handoff setup without matching evidence
- **WHEN** `ValidateOrchestrationPack.cs` validates the pack
- **THEN** it SHALL exit `1`
- **AND** JSON output SHALL include `false-advancement-claim`.
