# Live automation verification

Date: 2026-10-13. Daniel explicitly requested execution in the existing
`Keep NCG wiki up-to-date` chat and result verification for change closeout.
The 2026-10-12 implementation-only grant and fixture observations remain
historical; this request authorizes the real guarded wiki delivery and checkpoint.

## First completed run

Automation chat: `01a06b05-c8a5-7972-b9d0-5a7295708d54`.
Native turn: `01a133da-f302-7ce2-b06c-052d6ae7f3e3`.
Protected run ID: `run-d0894e01812b4dc1a1836cf547beaebe` under
`$CODEX_HOME/automation-runs/keep-ncg-wiki-current/`.

One immutable capture resolved 394 sessions in four bounded batches; four
sessions were in scope. Full coverage included 120 Backend, one STS and 91 Docs
commits: 216 candidate dispositions (86 update_needed, 53 already_covered,
77 irrelevant). Sessions discovered topics; pinned Git objects established
implementation facts. Four code source tips remained separate from the Docs tip.

The first macOS request-path alias was rejected as symlink_not_allowed before
request processing. Reusing the same request through its physical /private/var
path succeeded without a recapture or relaxed validation. The workflow docs now
explain canonical private request paths; their sequential DRY/SOLID/KISS delta
reviews are in [review-live-usage-delta.md](review-live-usage-delta.md).

A concurrent docs metadata commit changed the clean aligned main revision from
d8432846527c24b4862d9e80509ad199ae6044be to
e0e6e1923cafb37e815c2d475d19d31bb0ef8fa7. Planning correctly blocked with
docs_pin_changed. The automation retained its capture and old receipts, pinned
the new clean main, reviewed the additional Docs commit and reused 13 unchanged
code-topic comparisons through the bounded batch interface. No reset, pull,
rebase or new index capture was used.

Nine Markdown files were delivered directly on ncg-docs main as
28429aa8696ff6862bc38c3faedc262b9b77f5aa. The official completion receipt reports
complete, delivered and active retirement. Processed window end became
2026-10-12T19:25:55.912455Z; Last review is the separate completion time
2026-10-13T07:27:35.9822670+00:00; Docs reviewed tip equals the delivered commit.

| Protected proof | SHA256 |
| --- | --- |
| Complete pages | 3fa8f0c146fb6934c6828a9c47b79a859a0b192d915da0ea0ce4258b3534d0ba |
| Plan | d1abdd9d841fb4fd1c86ce11f2d9c43e21c00104c3d0fa4a9f0cfae2775368e3 |
| Completed receipt | 676d1df1f338e86ceddb1cca2f283de4b0df2635c2cc27b5cab4b630a6db8f34 |
| Official memory after first completion | f91aa2b89b0014e5df255f8cdf72dda475ab2b3fe4201ebdfcfd55a7a8eca343 |

Root independently repeated the public finalize command with the exact original
request. It exited0 and returned complete/active_retired. Memory and completed
receipt hashes before/after were identical. The historical response field
checkpoint_changed:true describes the original transition; it does not indicate
that this repetition changed bytes. Private verification artifact ID: fH4OD9.

## Semantic verification and required correction

Independent original-code samples checked CustomerHash/Confirmation and
SendgridCache/CI/job/catalog additions at the exact pinned Git objects. Root
also read the delivered diff/new page and directly read the relevant vehicle
activity source. One material mismatch was found in Customer-Hash-Service.md:
the new prose said Confirmation bookings covered the preceding twelve months.
VehicleActivitySyncService.cs at develop
8765245d22de37d48844dfddf0a7c596c9fffdd8 defines AllBookingsSince as
2000-01-01 UTC and passes that value to GetBookingsSinceAsync. This file has no
diff against production 06e3067e6bb8c1c11efd217c0cf3313545bbb4b1.

The completed run remains historical evidence. A separate guarded follow-up in
the same automation chat delivered the one-line correction as
2115e5d857992d710cec5a4075c9140965b66cdb. Root read the actual committed diff and
original source again, verified live origin/main equals local HEAD/remote-tracking
main and confirmed the docs worktree is clean. No old topic, plan, intent or
memory was manually rewritten to turn the original result into a semantic success.

Corrective native turn: 01a13433-6aec-7eb1-bc82-2410e01dbcdf.
Protected run ID: run-77bb5b13c6d745e0809e46992fc35079. Its two scoped session
deltas were fully disposed; both exact Git-history chains were terminal and empty,
and all four code source pins remained unchanged. A new topic and one-file plan
were persisted before editing; delivery-status moved through own_edits to delivered.
Plan receipt SHA256: a8bee75f0d402b44d4cc6485fb4a73d5cf2dafebcdc2f92f88c4453e8ba45a51.

Official corrective completion returned complete/active_retired. Its completed
receipt SHA256 is 8060e9fe27ae2d5180ccdfeb6a02c6bbf0b2084e30aecd6f4c8d3d01a868a544.
The final bundle is Processed window end 2026-10-13T07:18:25.033931Z,
Last review 2026-10-13T07:50:06.3627690+00:00, three derived carry entries,
the unchanged four source pins and Docs reviewed tip equal to 2115e5d857992d710cec5a4075c9140965b66cdb.
Official memory SHA256: 49cdbfd8af2b4846de8424d96be0d25f5f3a2063f3056f29d6c68f086ccbb1c3.

Root independently repeated finalize with the exact corrective request, exit0.
The response remained complete/active_retired and before/after hashes of memory
and corrective completion receipt were identical. The first run's completion
receipt also retained its original hash. Both idempotent transcripts and the
requests remain protected outside Git; only these bounded verification results
are delivered. The final result has no outstanding actionable semantic finding
within the checked sample. Technical completion follows this actual correction.

## Practical limits

Live execution verifies real session batching, proof/topic reuse, guarded docs
delivery, checkpoint persistence and retirement. Samples verify selected source
claims, not every historical wiki statement. No production/development runtime,
deployment, migration, webhook delivery or job execution was tested.

The delegated supplemental context check used actual bounded local docs,
research and meeting retrieval plus terminal Notion/Slack result pages. QMD was
about ten days old; no index repair occurred. Notion had no relation-based current
sprint filter, ai_search required a plan, one rows route rejected its schema,
and content-search completeness remained unverified; archive/task bodies were
not all read. Six returned Daily summaries (Sep30, Oct2/5/7/9/12) were read;
other Dailies, mail and transcripts were not. The Oct2 local-meeting/Slack identity
was not dedup-proven. These sources do not establish the implementation facts
above; pinned original Git objects do.
