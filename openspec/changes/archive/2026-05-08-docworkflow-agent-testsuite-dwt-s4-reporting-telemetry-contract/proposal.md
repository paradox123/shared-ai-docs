# DWT-S4 Reporting, Telemetry, Style and Summary Contract

## Why

The DocWorkflow Agent Delivery Testsuite needs a stable reporting contract before later L2/L3 agent outputs can be compared, reviewed or used as follow-up evidence.

## What

- Define a versioned summary artifact contract using the accepted DWT-S1 retained `l1-summary.json` as the legacy compatibility baseline.
- Define telemetry manifest fields for command/tool/read behavior, forbidden command classes, budget status and efficiency verdicts.
- Define style/usability and efficiency gates as machine-readable reporting outcomes.
- Require deterministic reporting fixtures and validators under `tests/docworkflow-agent-delivery/reporting/`.
- Keep DWT-S2, DWT-S3 and DWT-S5 unreleased until their own child specs and gates authorize them.

## Impact

- Enables consistent Evidence, Telemetry, Style and Efficiency reporting for later testsuite slices.
- Prevents prose-only or stale reporting from becoming false positive workflow evidence.
- Authorizes only the DWT-S4 reporting contract implementation, not agent execution or runtime delivery.
