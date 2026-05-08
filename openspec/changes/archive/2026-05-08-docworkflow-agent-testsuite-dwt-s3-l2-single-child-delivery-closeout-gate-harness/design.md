# DWT-S3 L2 Single-Child Delivery and Closeout Gate Harness Design

## Scope

DWT-S3 implements the L2 proof for single-child delivery kickoff and closeout gating. It does not implement DWT-S5, perform L3 runtime delivery, execute Docker/container verification, or mutate KI-fuer-KMU original repositories.

## Runner Strategy

Promptfoo/Codex is the primary runner path, reusing accepted DWT-S0 limitations and accepted DWT-S2 `ran-target` proof. Fallback artifact mode validates stored kickoff and closeout bundles, stale-handoff fixtures, DWT-S5 auto-release attempts and reporting/telemetry fields. Fallback mode cannot produce accepted L2 agent proof unless the summary records `agent_execution_status: ran-target`.

## Output Contract

The runner writes an output bundle with source manifest, raw agent output, delivery kickoff artifact, closeout sync artifact, before/after Child Index fixtures, handoff fixtures, telemetry manifest and DWT-S4-compatible summary.

The validator fails missing or invalid DWT-S2 dependency evidence, stale DWT-S3 handoff, missing or non-isolated target workspace, approximate or mismatched write-set, delivery outside DWT-S3, forbidden runtime/repo writes, closeout Parent Coverage loss, missing evidence/OpenSpec ledger sync, DWT-S5 release without its own gate, stale output provenance, blocked-agent-as-pass reporting and invalid DWT-S4 summary or telemetry fields.

## Boundaries

DWT-S3 may close only its own implementation evidence and may keep DWT-S5 queued or blocked. DWT-S5 remains responsible for runtime temp-repo delivery proof after its own hardening and handoff gates pass.
