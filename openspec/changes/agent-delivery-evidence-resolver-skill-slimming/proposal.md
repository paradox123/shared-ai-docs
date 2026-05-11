## Why

Agent Delivery skills currently repeat detailed Launcher, Controller, and archive evidence rules in multiple places. This makes the skills hard to read and easy to drift out of sync when the workflow evolves.

This change introduces a small evidence-resolver gate so skills can stay focused on roles, stop conditions, and tool handoff while a deterministic tool validates the concrete evidence artifacts.

## What Changes

- Add a deterministic Agent Delivery evidence resolver gate, implemented either as a focused `WorkflowDoctor` mode or a small new tool.
- The resolver distinguishes launcher-only handoffs, controller-backed visible multi-session workflows, and closeout archive evidence.
- The resolver emits one machine-readable verdict for skills to obey: `pass`, `not_ready`, or `fail`, with blocker reasons and evidence paths.
- Slim the relevant skills so they call the resolver for evidence consistency instead of restating every Launcher/Controller/archive check.
- Preserve existing session-start behavior; this change only centralizes validation and skill wording.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `docworkflow-agent-delivery-testsuite`: add resolver-gate requirements for Launcher/Controller/archive evidence validation and skill-slimming conformance.

## Impact

- Affected docs: `docs/doc-workflow.md`.
- Affected skills: `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout`, and `agent-delivery-retro-review`.
- Affected tools: `skills-repo/tools/WorkflowDoctor.cs` or a new focused resolver under `skills-repo/tools/`.
- Affected tests: source-controlled positive and negative fixtures for launcher-only, controller-backed visible, and closeout archive evidence.
