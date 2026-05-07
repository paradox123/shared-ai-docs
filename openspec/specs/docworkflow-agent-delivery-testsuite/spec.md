# docworkflow-agent-delivery-testsuite Specification

## Purpose
Capture accepted DocWorkflow Agent Delivery Testsuite requirements that have been archived from OpenSpec changes. The current canonical requirement records the accepted DWT-S0 Promptfoo-first framework spike evidence gate.
## Requirements
### Requirement: DWT-S0 framework spike evidence

The system SHALL run or reproducibly block a one-time Promptfoo-first framework spike before recurring L1/L2/L3 testsuite implementation starts.

#### Scenario: Promptfoo adoption is evidence-gated

- **GIVEN** the parent testsuite spec and framework ADR
- **WHEN** `DWT-S0` is executed
- **THEN** the output SHALL include one of `ADOPT_PROMPTFOO`, `ADOPT_WITH_LIMITATIONS`, `FALLBACK_TO_INSPECT`, or `REOPEN_EVALUATION`
- **AND** the result SHALL be backed by isolated fixture evidence, runner/config evidence, stored output or blocker evidence, and deterministic assertion evidence or blocker rationale.

#### Scenario: Static fake output cannot adopt Promptfoo

- **GIVEN** the spike uses static fake outputs, manual-only steps, hidden fixture normalization, or non-reproducible workarounds instead of a reproducible agent/coding-agent path
- **WHEN** the ADR is re-evaluated
- **THEN** the result SHALL NOT be `ADOPT_PROMPTFOO`.
