# Design

## Runtime Target

DWT-S5 uses only a synthetic source-controlled fixture repository under `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/synthetic-runtime-repo/`. The runner copies that fixture into a generated run directory under `<run-dir>/target-repos/` before any edit-like or runtime action.

The fixture must not contain original project names, KI-fuer-KMU domain content, deployment endpoints, credentials or secret-shaped values.

## Runner Shape

`tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh` exposes `preflight`, `all`, `agent`, `fallback`, `validate-output`, `local-runtime`, `container-harness`, `closeout`, `style` and `telemetry` selectors.

`preflight` validates retained DWT-S3 evidence, fixture integrity, tool/runtime availability and temp directory creation without running runtime or Docker/container commands. `all` runs the full implementation proof once the runner and fixtures exist.

## Evidence Contract

The DWT-S5 summary uses `schema_id: docworkflow-agent-delivery-summary.v1` and records retained DWT-S3 evidence, generated temp repo provenance, local runtime gate status, container/harness gate status, forbidden-action assertions, closeout sync, style verdicts and telemetry verdicts.

Blocked runtime prerequisites are valid blocker evidence but not accepted L3 pass proof.
