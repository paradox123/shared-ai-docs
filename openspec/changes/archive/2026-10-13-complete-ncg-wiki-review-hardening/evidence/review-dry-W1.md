# DRY review receipt: W1

Reviewer: independent fresh-context agent `review_dry`, 2026-10-12.
Base: `780e87460de79d6bff2300bc7f1aeb96d9d28217`.
Identity: initial W1 content manifest and scoped tracked patch; new files were
read directly. The reviewer confirmed the two helper hashes match that manifest.

Coverage: canonical workflow/schema ownership, duplicated source/ref/cursor
decisions, equivalent topic-proof reuse, effective prompt consistency and existing
Python-reader/runtime binding. No new suites or remote actions were performed.

## DRY-W1-01: valid clone receipt cannot reach delivery

Concrete contract defect, P2; also assigned to subsequent SOLID contract coverage.
`NcgWikiDelivery.cs` RangePins reads the clone pointer as though it were the
resolution receipt. `ReviewRun.cs` writes that pointer as `{receipt,
receipt_sha256}`; `source_pins` belongs to the referenced `resolution.json`.
A valid manually resolved clone passes verify-pages but plan-delivery fails with
missing_source_pins, preventing finalization.

Accepted for repair: verify and dereference the existing pointer contract, and
prove the composed clone-resolution → plan → finalize path through the public CLI.
Affected requirements evidence is reopened until that regression passes.

No additional binding DRY violation or material heuristic suggestion. W1 is not
approved for completion; a delta receipt must cover this repair before SOLID.
