# Scope Contract

## Change

Implement `MD-E2E-1` only: source-controlled mock fixture data, manifest contracts, mock target fixture roots and deterministic Node validators for manifest schema and forbidden real fixture detection.

## In Scope

- `tests/docworkflow-agent-delivery/mock-data/large-parent/mock-large-parent-spec.md`
- `tests/docworkflow-agent-delivery/mock-data/large-parent/manifest.json`
- `tests/docworkflow-agent-delivery/mock-data/large-parent/mock-target/README.md`
- `tests/docworkflow-agent-delivery/mock-data/small-direct/mock-small-direct-spec.md`
- `tests/docworkflow-agent-delivery/mock-data/small-direct/manifest.json`
- `tests/docworkflow-agent-delivery/mock-data/small-direct/mock-target/README.md`
- `tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js`
- `tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js`
- `tests/docworkflow-agent-delivery/e2e/fixtures/manifest-schema-valid-large/**`
- `tests/docworkflow-agent-delivery/e2e/fixtures/manifest-schema-valid-small/**`
- `tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture/**`
- OpenSpec task/evidence sync for this change.

## Out of Scope

- Local Mock Session Runner implementation.
- `run-mock-e2e-checks.sh`.
- Migration of `run-contract-checks.sh` or `setup-fixture.sh`.
- README or parent/canonical documentation closeout beyond the already hardened MD-E2E-1 control artifacts.
- Live-agent/Codex execution path.
- Any KI-fuer-KMU or real product compatibility fixture.

## Acceptance Targets

- Positive large and small manifests validate with the schema validator.
- The large fixture declares `parent_child`, exactly `ML-C1` through `ML-C5`, and expected `count.txt` content `1\n2\n3\n4\n5\n`.
- The small fixture declares `direct`, no expected children, and forbidden child-control outputs.
- Positive mock fixtures scan cleanly for forbidden real fixture paths and compatibility markers.
- Negative fixtures for source path, target workspace, write-set, evidence path and compatibility mode fail with machine-readable findings.
- OpenSpec change remains valid.

## Planned Verification

| Command | Expected Status |
|---|---|
| `node --version` | `ran-target` |
| `cd /tmp && dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- --index "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md" --child MD-E2E-1 --handoff "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/child-session-handoffs/md-e2e-1-session-handoff.md"` | `ran-target` |
| `node tests/docworkflow-agent-delivery/e2e/validators/mock-manifest-schema.js tests/docworkflow-agent-delivery/mock-data` | `ran-target` |
| `node tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js tests/docworkflow-agent-delivery/mock-data` | `ran-target` |
| `node tests/docworkflow-agent-delivery/e2e/validators/forbidden-real-fixture.js tests/docworkflow-agent-delivery/e2e/fixtures/forbidden-real-fixture && exit 1 || test "$?" -ne 0` | `ran-target` |
| `openspec validate docworkflow-agent-mock-e2e-md-e2e-1-mock-fixtures --strict` | `ran-target` |
| `git diff --check` | `ran-target` |

No runtime/container validation is required for this child because the hardened scope explicitly excludes runner/runtime execution.

## Pre-Implementation Analysis

- Formal markers: no `[MISSING]`, `[DECISION]` or `[BLOCKED]` markers found in the target child spec, handoff, orchestration pack or OpenSpec change.
- Code reality: existing Agent Delivery validators are Node scripts under `tests/docworkflow-agent-delivery/**/validators/`; this change follows that pattern.
- Existing target dirs: `tests/docworkflow-agent-delivery/mock-data/large-parent`, `tests/docworkflow-agent-delivery/mock-data/small-direct` and `tests/docworkflow-agent-delivery/e2e` exist and are empty/adoptable.
- Logical consistency: MD-E2E-1 owns fixture and validator contracts only; runner execution and standard-gate migration are delegated to later children.
- NCG build watcher: not applicable; this repository path and change do not touch the NCG backend or any NCG build.
