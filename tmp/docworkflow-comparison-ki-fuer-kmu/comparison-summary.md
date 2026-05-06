# DocWorkflow Comparison Summary: Legacy vs New Workflow

## Test Setup

Source copied from:

- `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md`
- `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-child-specs-index.md`
- `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s*.md`

Temp lanes:

- `legacy/`: Workflow 1 / `refine-plan` simulation.
- `new/`: Spec Sizing Gate -> Parent/Child orchestration -> child hardening readiness.

Original files were not changed.

## Headline Result

The new workflow better supports the intended vision.

Legacy creates a readable plan, but still concentrates too much scope and context in one ledger. The new workflow turns the same Parent Spec into a controlled child delivery system and identifies S3 as the next bounded hardening target.

## Side-by-Side

| Question | Legacy Workflow | New Workflow |
|---|---|---|
| Does it detect oversized scope? | Yes, but as plan risk. | Yes, as canonical Sizing Gate. |
| What artifact becomes leading? | One iterative plan. | Parent/Child control layer plus OpenSpec default ledger. |
| Does it prevent implementation from Parent as a whole? | Only by warning/blocking in plan. | Yes, by routing to child hardening. |
| Does it produce session-ready child handoff? | No, only a next tranche note. | Yes, S3 handoff is explicit. |
| Does it avoid duplicate ledgers? | Weak; plan duplicates child index/status. | Stronger; One Delivery Ledger rule applies. |
| Does it use accepted S1/S2 correctly? | Yes, as done actions. | Yes, as reference/evidence without backfill. |
| Does it expose S3 gaps? | Yes, as `[MISSING SPEC ...]`. | Yes, as hardening queue and stop-before-code gate. |
| Does it support parallel work safely? | Only if plan author remembers to define lanes. | Yes, explicit Parallel Work Control Surface. |
| Implementation readiness result | `NOT IMPLEMENTATION READY AS ONE LEGACY RUN` | `READY FOR CHILD-SPEC-HARDENING`, not implementation yet. |

## What The Test Shows

### Legacy Workflow

Useful when:

- the spec is small or already tightly bounded,
- the user wants a human-readable action plan,
- one session can realistically finish the change,
- no parent/child control layer is needed.

Problem in this Parent Spec:

- It creates a second control surface beside the child index.
- It keeps the context burden high.
- It does not automatically harden S3 before implementation.
- It relies on the implementing agent to respect plan warnings.

### New Workflow

Useful when:

- the scope is large enough to threaten context quality,
- several child slices exist or naturally emerge,
- each child should be independently handoffable into a fresh session,
- accepted prior slices should be reused as evidence without migrating all old specs.

Result in this Parent Spec:

- Sizing Gate fires correctly.
- Parent/Child stays leading.
- S3 is selected as next child.
- S3 is not allowed into implementation yet.
- The workflow produces a practical S3 hardening handoff.

## Recommendation

For the KI fuer KMU Free Entry v2 Parent Spec, use the new workflow.

Next concrete step:

1. Run `child-spec-hardening` on S3 in the temp lane.
2. Enrich the child index with readiness/dependencies/evidence links.
3. Only after S3 gets `IMPLEMENTATION READY`, start a fresh implementation session for S3.

Legacy should stay available for smaller specs and explicit Workflow 1 cases, but it should not be the default for this Parent Spec.

## Files

- Legacy result: `legacy/legacy-workflow-result.md`
- New workflow result: `new/new-workflow-result.md`
