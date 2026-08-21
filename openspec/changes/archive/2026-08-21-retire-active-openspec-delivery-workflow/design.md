## Context

The earlier Agent Delivery workflow was already reduced to two canonical capabilities and one C# validator. The user has confirmed that the entire Spec-to-OpenSpec-to-implementation workflow is obsolete. Historical artifacts remain useful only as records of past experiments.

## Goals / Non-Goals

**Goals:**

- Remove all active normative requirements belonging to the retired workflow.
- Remove its last executable validator.
- Leave no current code or canonical spec reference to that validator or either capability.

**Non-Goals:**

- Delete historical `_specs` documents or archived OpenSpec changes.
- Remove OpenSpec itself or general repository guidance for creating and maintaining OpenSpec changes.
- Change unrelated skill or automation behavior.

## Decisions

Delete both capability directories after applying removal deltas. An empty canonical capability would falsely suggest that the workflow still has an active contract.

Delete the validator rather than preserving a deprecated wrapper. It has no maintained consumer after both capabilities are removed.

Use negative path and reference checks as the direct verification surface. A permanent test for the absence of a retired workflow would create another artifact devoted to maintaining the thing being removed.

## Risks / Trade-offs

- **Historical documents retain stale command examples** → Keep dated retrospectives, `_specs`, and archived changes as historical evidence; limit absence checks to active code, canonical specs, and current entry-point documentation.
- **General OpenSpec guidance could be removed accidentally** → Bound deletion to the two named capability directories and one named validator.
- **The previous uncommitted archive work could be disturbed** → Build this change on top of it without rewriting or moving that archive.
