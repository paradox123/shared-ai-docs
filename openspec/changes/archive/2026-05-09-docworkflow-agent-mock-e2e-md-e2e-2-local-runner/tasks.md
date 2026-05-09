# Tasks

- [x] Implement `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh` with `large`, `small`, `all`, `--keep`, `--run-id <id>` and `--help`.
- [x] Implement Node runner modules under `tests/docworkflow-agent-delivery/e2e/mock-runner/**`.
- [x] Implement `tests/docworkflow-agent-delivery/e2e/validators/mock-e2e-summary.js`.
- [x] Generate large retained evidence with parent-control artifacts, five session JSON files, `mock-target/output/count.txt`, output hash evidence and summary v1.
- [x] Generate small retained evidence with direct-delivery evidence, `mock-target/output/small-direct-result.json`, output hash evidence and summary v1.
- [x] Generate `all --keep` aggregate evidence and aggregate summary.
- [x] Wire accepted MD-E2E-1 `mock-manifest-schema.js` and `forbidden-real-fixture.js` validators into preflight and generated evidence validation.
- [x] Add negative guard fixtures or assertions for permanent `queued`, `manual_start_required`, `blocked`, `failed`, output mismatch, forbidden fixture paths and external dependency attempts.
- [x] Run `bash -n tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`.
- [x] Run `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep`.
- [x] Run `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh small --keep`.
- [x] Run `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`.
- [x] Run `openspec validate docworkflow-agent-mock-e2e-md-e2e-2-local-runner --strict`.
- [x] Run `git diff --check`.
- [x] Record retained evidence and closeout notes in `implementation-evidence.md`.
