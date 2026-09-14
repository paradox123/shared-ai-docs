# Preserve the submission source for derived issues

The Agent Framework pilot accepts both GitHub issues and local Markdown work mandates. A PRD submitted as a GitHub issue produces linked GitHub issues; a PRD submitted as a file produces linked local issue files. Both use the same implementation workflow and Operator run view, preserving the user's chosen issue source without requiring publication or migration to another tracker.

## Consequences

- Every submission, its admitted content/version and provenance, and its links to derived issues and runs are persisted in the application database. The database-backed overview and Run History do not require publishing local issues to GitHub and do not constitute a competing issue tracker.
- Issue identity, mandate ancestry, dependencies and closure must support both sources. A GitHub issue number cannot be the sole identity of every ImplementationRun.
- The issue source and implementation repository are distinct: a local issue still needs an explicit repository binding and the existing repository-derived authorization. Local issue storage does not imply an offline repository or an alternative approval policy.
- Issue creation and status changes are applied to the originating source and correlated into Run History. Restart must reconcile existing child issues before creating more; generated files must not overwrite unrelated content.
- Normalizing every file submission to a GitHub issue, or mirroring every GitHub issue into an independently writable local tracker, was rejected. Supporting two source adapters is an intentional cost of preserving the submitted workflow.
