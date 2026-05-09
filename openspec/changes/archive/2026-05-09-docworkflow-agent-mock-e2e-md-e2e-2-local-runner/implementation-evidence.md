# Implementation Evidence

## Scope

Implemented `MD-E2E-2` local mock session runner only:

- Bash entrypoint: `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- Node runner: `tests/docworkflow-agent-delivery/e2e/mock-runner/run.js`
- Summary validator: `tests/docworkflow-agent-delivery/e2e/validators/mock-e2e-summary.js`
- Negative guard fixture: `tests/docworkflow-agent-delivery/e2e/fixtures/mock-runner-negative/negative-cases.json`
- Retained evidence under `tests/docworkflow-agent-delivery/e2e/evidence/**`

No MD-E2E-1 compatibility fixture changes were made.

## Retained Evidence

Large selector:

- Root: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-large/`
- Summary: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-large/mock-e2e-summary.json`
- Large summary: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-large/large/mock-e2e-summary.json`
- Session files: `large/sessions/ML-C1-delivery.json` through `large/sessions/ML-C5-delivery.json`
- Output: `large/mock-target/output/count.txt`
- Hash evidence: `large/output-evidence/count.txt.sha256`
- Forbidden scan: `forbidden-real-fixture.json`
- Negative guards: `negative-guard-evidence.json`

Small selector:

- Root: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-small/`
- Summary: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-small/mock-e2e-summary.json`
- Small summary: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-small/small/mock-e2e-summary.json`
- Direct evidence: `small/direct-delivery.json`
- Output: `small/mock-target/output/small-direct-result.json`
- Hash evidence: `small/output-evidence/small-direct-result.json.sha256`
- Forbidden scan: `forbidden-real-fixture.json`
- Negative guards: `negative-guard-evidence.json`

All selector:

- Root: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-all/`
- Summary: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-all/mock-e2e-summary.json`
- Aggregate summary: `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-all/aggregate-summary.json`
- Large summary: `large/mock-e2e-summary.json`
- Small summary: `small/mock-e2e-summary.json`
- Five retained large session files under `large/sessions/`
- Large hash evidence: `large/output-evidence/count.txt.sha256`
- Small hash evidence: `small/output-evidence/small-direct-result.json.sha256`
- Forbidden scan: `forbidden-real-fixture.json`
- Negative guards: `negative-guard-evidence.json`

## Negative Guard Evidence

`negative-guard-evidence.json` records `status: pass` for bad states that cannot produce a positive pass summary:

- `manual_start_required`
- permanent `queued`
- `blocked`
- `failed`
- output mismatch
- forbidden fixture state
- external dependency attempted

The retained negative evidence uses sanitized case identifiers and blocker reasons so the positive generated run roots can still pass the MD-E2E-1 forbidden-real-fixture validator.

## Verification

Preflight / inherited contract:

- `node --version` -> `v22.12.0`
- `node tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js tests/docworkflow-agent-delivery/mock-data` -> pass
- `node tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js tests/docworkflow-agent-delivery/mock-data` -> pass
- `ValidateChildReadiness.cs` -> pass via temporary `/tmp/validate-child-readiness-runner` console wrapper because `dotnet script` is not installed
- `openspec validate docworkflow-agent-mock-e2e-md-e2e-2-local-runner --strict` -> pass
- `git diff --check` -> pass

Delivery gate:

- `bash -n tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh` -> pass
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep` -> pass
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh small --keep` -> pass
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep` -> pass
- `node tests/docworkflow-agent-delivery/e2e/validators/mock-e2e-summary.js ...` over retained large, small and all summaries -> pass
- `node tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js ...` over retained large, small and all roots -> pass
- `git diff --check` -> pass

## Closeout Notes

The runner remains local-only and records all external dependency classes as `not_used`. Literal MD-E2E-1 forbidden source path patterns are retained in `forbidden-path-policy.json` under the existing policy metadata key, while summaries and session evidence reference that policy by hash/count so generated positive evidence remains scannable by the accepted forbidden-real-fixture validator.
