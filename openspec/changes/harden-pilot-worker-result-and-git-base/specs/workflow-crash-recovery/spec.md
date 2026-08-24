## MODIFIED Requirements

### Requirement: Make external transitions idempotent across uncertain crash boundaries
Every claim, implementation, draft-publication, review, repair, and human-feedback external transition MUST have a stable durable operation identity. A transition with a durably completed schema-valid result MUST NOT execute externally again, including when diagnostic JSONL beside that result was malformed. A transition whose effect is uncertain after a crash MUST reconcile deterministic worktree, immutable base SHA, Git, GitHub, head, and label state and MAY retry an opaque worker only under the same operation, batch, and round identity.

#### Scenario: Crash follows a valid result with degraded diagnostics
- **WHEN** a schema-valid final worker result is available but one diagnostic line is malformed before the next checkpoint
- **THEN** recovery reuses the retained result and bounded diagnostic-parse event instead of invoking the worker again

#### Scenario: Crash follows worktree creation before implementation persistence
- **WHEN** a run-owned worktree was created from a fetched base SHA but the process stopped before the implementation row was persisted
- **THEN** recovery adopts the same branch, worktree, and original base SHA without creating a second worktree or moving the branch
