# MD-E2E-2 Local Mock Session Runner Design

## Scope

This change implements the local baseline runner only. It does not edit legacy standard gate scripts, README documentation, the canonical accepted OpenSpec spec, or the optional live-agent path.

## Runner Model

The public interface is a Bash wrapper at `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`. The wrapper validates selector/flag input, enforces repository cwd assumptions and delegates JSON/filesystem work to Node modules under `tests/docworkflow-agent-delivery/e2e/mock-runner/**`.

The runner reads the accepted MD-E2E-1 manifests directly. It must not synthesize a different large child list, expected output or small direct output. If the manifest contract is incompatible, the implementation must stop and document a compatibility fix instead of silently widening the runner.

## Evidence Model

With `--keep`, evidence is retained under `tests/docworkflow-agent-delivery/e2e/evidence/<run-id>/`. The large selector writes generated parent-control artifacts, five child session files, `count.txt`, hash evidence and a summary. The small selector writes direct-delivery evidence, `small-direct-result.json`, hash evidence and a summary. The `all` selector runs large and small in separate subdirectories and writes `aggregate-summary.json`.

## State Model

Large-path sessions must transition in order. `ML-C(n+1)` cannot start or resume until `ML-Cn` has `closed`. Positive large runs require each child to reach `ran-target` and `closed`. Permanent `queued`, `manual_start_required`, `blocked`, `failed` or `ran-rehearsal` cannot pass.

Small-path delivery has one `direct-delivery` step and no child artifacts.

## Boundaries

Network, Docker, Codex auth, external agent providers and manual starts are forbidden in the baseline. Command telemetry must record these as `not_used`; any attempt fails the positive run.
