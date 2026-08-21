## Why

The former Spec-to-OpenSpec-to-implementation delivery workflow is no longer used. Keeping its canonical capabilities and validator makes obsolete process look mandatory and creates maintenance work without a current consumer.

## What Changes

- **BREAKING**: Remove the canonical `docworkflow-active-openspec-scope` capability.
- **BREAKING**: Remove the retired `docworkflow-agent-delivery-testsuite` capability.
- Delete `skills-repo/tools/ValidateActiveOpenSpecScope.cs`.
- Preserve archived changes and `_specs` material as historical records.
- Preserve general OpenSpec usage and repository-level OpenSpec guidance unrelated to this retired delivery workflow.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `docworkflow-active-openspec-scope`: Remove the remaining active-scope delivery requirements.
- `docworkflow-agent-delivery-testsuite`: Remove the retirement marker capability after deleting its last maintained validator.

## Impact

- `openspec/specs/docworkflow-active-openspec-scope/`
- `openspec/specs/docworkflow-agent-delivery-testsuite/`
- `skills-repo/tools/ValidateActiveOpenSpecScope.cs`
- No runtime application code or external service is affected.
