## Context

UX-01 was implemented as part of the active GUI change on `codex/operator-gui-ux-01`, based on the locally verified GUI-03 commit `a46a133`. The user accepted implementation commit `2da12a4` on 2026-09-15 and requested OpenSpec closure, commit and push on the established feature branch.

## Goals / Non-Goals

**Goals:** Archive the accepted shared run entry with its full evidence and publish its contract canonically.

**Non-Goals:** New runtime behavior, whole-parent completion, GUI-03 acceptance, UX-02–04 refinement, Azure deployment or separate-machine acceptance. No merge to `main` is part of this closeout.

## Decisions

UX-01 applies the approved shared-view hierarchy from [the approved UX plan](../../add-agent-framework-operator-gui/ux-ticket-plan.md) within
this change. The saved submission opens on Result; History, Files and Requirements
are labelled keyboard tabs beneath one title, source and confirmed analysis state.
Existing readable history/artifact renderers and immutable content are reused.
The GUI reads analysis disposition from the public submission execution endpoint,
not from run identity or the broader workflow state. A lost connection marks the
last confirmed disposition as stale and retries; it does not manufacture execution
failure. Selection-scoped reads are cancelled and fenced, and observation updates
retain the selected tab, expanded evidence and keyboard focus. No persistence or
wire-contract change is needed for this slice.

The accepted scenario is extracted into the narrowly named requirement “Shared run entry uses confirmed analysis state”. Its behavior is unchanged; the broader unfinished workflow requirement remains in the parent. The OpenSpec CLI owns the canonical spec update and dated archive move.

## Closeout refactoring pass

The 2026-09-15 DRY/SOLID/KISS pass inspected the UX-01 diff from `a46a133` and nearby code in analysis-state, execution-view, operator, run-tabs, workflow-view, HTML and CSS. State mapping and polling already share one source; command, observation and selected-view lifetimes are separated; stable DOM nodes retain focus and expanded evidence. No additional runtime abstraction or stylesheet rewrite is warranted. Extract the accepted scenario and design once, keeping short parent links instead of duplicate requirements.

## Verification

Rerun the ten public shared-view browser cases and the timeout/reconciliation case after this pass; retain the accepted 239-test regression (213 passed, 26 opt-in skipped) and real GitHub/Codex desktop/mobile proof. See [acceptance evidence](ux-01-evidence.md) and [reviews](ux-01-review.md). Validate the child before archive and every active change/canonical spec afterward; verify evidence hashes and moved links.
