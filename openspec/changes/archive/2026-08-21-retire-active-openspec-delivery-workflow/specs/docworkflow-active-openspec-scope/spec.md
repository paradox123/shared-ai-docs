## REMOVED Requirements

### Requirement: Active OpenSpec scope

**Reason**: The Spec-to-OpenSpec-to-implementation workflow is no longer used.

**Migration**: Follow the current repository instructions and user request directly; no replacement delivery workflow is introduced.

### Requirement: Tool-enforced workflow gates

**Reason**: The retired workflow no longer needs a dedicated active-scope validator.

**Migration**: Use task-specific verification defined by the repository and the current change instead of `ValidateActiveOpenSpecScope.cs`.

### Requirement: Default session orchestration is deprecated

**Reason**: This requirement existed only to contrast the retired workflow with an even older session-orchestration workflow.

**Migration**: Historical session tooling remains historical and does not need a replacement normative requirement here.

### Requirement: No duplicate active-scope artifact

**Reason**: The active-scope workflow and its derived-view concept are being removed.

**Migration**: Do not create a replacement scope artifact solely for this retired workflow.
