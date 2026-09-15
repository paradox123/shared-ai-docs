## Why

The user accepted UX-01 on 2026-09-15 and requested OpenSpec closure, commit and push. Extract its completed contract from the wider GUI change using the established Ticket 01/02 closeout pattern, so the accepted slice can be archived while unfinished GUI and UX work remains active.

## What Changes

- Publish the implemented common run entry, result-first navigation and confirmed analysis-state contract in the canonical Operator GUI spec.
- Retain explicit uncertainty, reconciling diagnostics, late-read cancellation, existing evidence and stable keyboard interaction.
- Archive the accepted implementation, review and browser/live evidence with this slice; replace parent duplication with links.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `agent-framework-operator-gui`: Add the accepted UX-01 shared entry and observation contract to the existing intake/background-analysis baseline.

## Impact

Documentation and contract extraction only; no runtime, persistence or wire-format changes. Implementation commit `2da12a4` is unchanged. Original GUI Tickets 03–16 and UX-02–04 retain their existing status and scope in `add-agent-framework-operator-gui`. This acceptance does not infer acceptance of GUI-03, distributed deployment or the entire workflow.
