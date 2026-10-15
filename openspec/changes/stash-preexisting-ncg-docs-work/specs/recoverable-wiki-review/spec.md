## ADDED Requirements

### Requirement: Protected pre-existing docs work
The NCG wiki flow MUST NOT abort only because pre-existing docs changes exist. Explicit protected delivery commands MUST snapshot and stash staged, unstaged and untracked changes only in the bound docs main repository after aligned-base validation. The exact own stash, base, snapshots and operation identity MUST be journaled before mutation and retained through interruption. Foreign stashes MUST remain untouched. The workflow MUST commit/push only its planned Markdown and restore the protected prior work, including its staging state, before official completion. Successful restored stashes MAY remain as named safety backups.

#### Scenario: Existing mixed work does not block delivery
- **WHEN** a main-aligned docs tree has staged and unstaged changes plus untracked files
- **THEN** protected capture preserves them, own docs can be committed/pushed without them and restoration recovers their contents and index state
- **AND** the original memory remains unchanged until delivery and restoration are verified

#### Scenario: Restart does not create or apply another stash
- **WHEN** protection or restoration is interrupted after its Git operation
- **THEN** the saved exact operation identity and verified Git contents permit adoption without repeating the completed mutation

#### Scenario: Tracked changes overlap the own delivered file
- **WHEN** a clean three-way restoration combines protected tracked changes with the new committed Markdown
- **THEN** the expected staged and working trees are derived and checked without losing either change

#### Scenario: Conflict or foreign data appears
- **WHEN** restoration conflicts, untracked paths collide, or unknown state prevents exact verification
- **THEN** the stash, snapshots and diagnostics remain recoverable, no forced cleanup occurs and official completion is blocked by that concrete condition, not initial dirt alone

#### Scenario: Delivery or source verification fails after protection
- **WHEN** a push fails or authoritative pins change
- **THEN** narrowly owned restoration remains available without weakening the independent source/delivery/checkpoint gates

## MODIFIED Requirements

### Requirement: Owned delivery and recoverable finalization
Before changing docs, the flow MUST retain a protected delivery intent bound to the clean main base SHA, exact owned paths/base and intended content, original comparison receipts and authoritative source pins. The NCG automation MUST be able to deliver from a private run-owned main checkout of the exact same docs origin while the normal checkout remains dirty or is being used concurrently. The canonical repository identity, review scope and persisted Docs reviewed tip MUST remain the configured original repository, not the temporary checkout. Only the run-owned checkout MAY be edited or committed under this mode; no unrelated index/worktree/stash in the normal checkout may be changed. Explicit protected stashing remains supported for callers intentionally delivering in the normal checkout. Recovery MUST adopt only exact own files/commit and validated protected restoration where protection was used. Wrong branch, rewritten history, corrupt evidence and concrete ownership conflicts remain unsafe; ordinary new append-only source commits or activity in the normal docs checkout MUST trigger bounded refresh/replanning or next-window deferral, not terminal failure. Actual remote state MUST establish delivery/completion; caller booleans MUST NOT. Unchanged topics MUST match pinned delivered wiki content, while delivered topics bind original comparisons to owned committed post-edit content.

Finalization MUST prove all dispositions, required delivery and completed protection/restoration before an immutable expected-old/intended-new intent. It MUST preserve non-checkpoint memory and write the whole bundle under the existing lock. Narrow restart accepts only the exact old/new bundle, with verified restoration frozen before checkpoint replacement. Normal review validation remains strict.

#### Scenario: Push is delivered but protected work remains stashed
- **WHEN** origin/main contains the exact own commit but original work has not been restored
- **THEN** delivery can be identified but finalize cannot advance the official bundle

#### Scenario: Confirmed restoration precedes completion
- **WHEN** the exact own commit is delivered and restoration is verified against expected trees and untracked contents
- **THEN** the atomic review bundle may advance even though the restored prior work makes the docs worktree dirty

#### Scenario: Finalization recovery after memory replacement
- **WHEN** the official bundle already equals the protected intended new bundle
- **THEN** saved pre-write delivery/restoration proofs permit receipt/retirement recovery without treating later user edits as a reason to advance again

#### Scenario: Another task writes in the normal checkout
- **WHEN** the configured docs checkout contains mixed staged/unstaged/untracked work and another task changes or commits it during the review
- **THEN** the automation delivers its exact own Markdown from a verified run-owned checkout on main to the same origin
- **AND** the normal checkout, its index, unrelated files and stashes remain untouched by that delivery
- **AND** the official Docs reviewed tip still names the configured original root

#### Scenario: Authoritative code refs advance normally
- **WHEN** an explicitly opted-in bounded review's four pinned source tips remain ancestors of their freshly fetched matching exact refs
- **THEN** delivery and finalize may certify the fully reviewed pinned window
- **AND** the checkpoint retains the reviewed pins, so later newly reachable commits remain for the next window rather than being skipped
- **AND** missing refs or rewritten/nonancestor history still fail closed

#### Scenario: Docs main advances before an own push
- **WHEN** another writer pushes a new docs main commit after the original delivery base was selected
- **THEN** the automation preserves its old intended content/own commit as evidence and refreshes the exact docs main history and relevant comparisons in another owned checkout
- **AND** it performs only a normal fast-forward push of a newly validated own main commit, without force-push, reset, rebase or mutation of the normal checkout
