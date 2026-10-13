# Requirements verification: all six NCG wiki findings

Fixture verification date: 2026-10-12. Candidate base: shared-ai-docs main 780e874. Scope is the one
authorized follow-up ticket; the initial hardening change is already archived.
The historical W4 candidate and read-only dependency hashes are in content-manifest.json.
Real 2026-10-13 execution and semantic verification are recorded separately in
[live-run-verification.md](live-run-verification.md); the old memory digest below
is the implementation-only snapshot, not the current operational state.

## Expected versus observed

| Finding / requirement | Expected result | Observed public-interface evidence |
| --- | --- | --- |
| Lossless large windows | More than500 sessions resolve in slices≤100; unchanged snapshot/restart, full contiguous proof and legacy behavior. | Root ReviewRunBatchTests exits0, six groups:501-session capture/resume, actual aggregate→scoped page/proof, corrupt and missing-middle batches, exact approved/unapproved missing carry, bounded timeout retry. Python combined discovery:60 tests in9.471s, OK, including legacy resolver/extractor and additive batch regressions. |
| Timeout/known error recovery | End owned descendants after parent exit, retain bounded diagnostics, release lock; explicit retry only on valid failed evidence. | Root ReviewRunRecoveryTests exits0. Exit124 timeout kills orphan;125 retains outputlimit failure; successful3500-byte output under4000 ceiling remains complete. Failed attempt/unchanged range validation and historical failed receipt integrity reject corruption and missing retry flag. |
| Exact Docs revision | SHA/ancestry ranges include old-dated new work; first baseline explicit; four code pins stay separate. | Root NcgWikiDeliveryTests exits0:old-dated Docs candidate, complete first-baseline pages, missing disposition, pinned/dirty input distinction and code-tip change cases. Branch promotion previously reviewed on the other code branch is not selected again. |
| Efficient same-trust comparisons | Blockwise exact range hashes; one full proof per bounded topic batch; stale/changed/corrupt inputs still block. | Root Recovery suite:CRLF, EOF without newline, multiblock prefix/carry, append and truncation groups pass.12 individual public resume calls3702.908ms versus one equivalent batch263.066ms, one current proof.2,097,685-byte proof fixture8.392ms. These are local observations, not an automation-wide speed guarantee. |
| Owned delivery/finalization | Prior intent recognizes only exact own parent/paths/blobs; real delivery checked; all dispositions/proofs; narrow journal recovery and no foreign overwrite. | Root Delivery suite:seven groups, including UTF8/space target, matching plan reuse, failed push, own successful delivery, future source changes after already-written intent, foreign edits/changed code pins, symlink target before intent and exited-parent fetch deadline. Current proof/raw ranges and helper versions are integrity-bound. |
| Prompt integration | One ordered canonical owner, bootstrap exception, stable schedule/target, tested interfaces and unchanged official memory. | automation_update succeeded; direct TOML readback differs only prompt/updated_at. Prompt shrank22,546→6,557 characters. Definition SHA2562c31c985aa61ac4fc9ab2d70d2d1d8514d3d2525945a3bb7c6ddf0a0defeb812. Memory remains1c3fec3e3f8035bad1bcbdebc432b19ee8473c63ab080d9306c60f8d9c9958dd; no live active review receipt. |

## Composed evidence and regressions

[Integrated public CLI transcript](../../../../../.scratch/ncg-wiki-review-followup/verification/integration-486520de90344c92afcbca2caba3726a.log)
is a protected local artifact and is not included in repository delivery. It
contains15 successful invocations:three session batches, three complete summary
pages, exact four code sources, explicit empty code page and three Docs history
pages, six negative candidate dispositions, no-change completion and an identical
second finalization. Fixture memory stays unchanged until the complete final step,
then cursor07:02, separate Docs tip and active retirement are asserted. No docs
edit/commit occurs in that no-change scenario.

The shipped ReviewRunTests also exits0 on the current helper, retaining cursor,
complete pages, clone handling, stable replay, invalid input, snapshot corruption,
case-alias exclusion and explicit legacy-boundary cases. Its verbose tool output
was capped; success is the actual process exit plus the checked public assertions,
not a claim that every raw transcript line was displayed.

Behavioral red preceded repairs for missing retry, orphan-pipe hang, missing topic
batch, premature output ceiling, unproven discovery false-block and branch-promotion
reselection. Delivery red/green transcripts remain in protected local fixture
storage. Compile-only and integration selection_window harness repairs are not
reported as behavioral red.

## W2 review repair: composed manual clone

DRY-W1-01 reopened the valid-manual-clone delivery requirement. A new public
resolve-clone → verify-pages → plan-delivery → finalize fixture failed against W1
with missing_source_pins despite one valid resolved clone. W2 verifies the existing
pointer file hash against complete proof, follows the within-run receipt and checks
its hash/session identity before retaining its source pins. The same fixture now
passes through retirement (exit0); corruption of the pointed receipt is still
rejected before an actionable delivery plan or memory write (exit2). Root inspected
the actual red/green transcript results; these are original CLI outputs.

Targeted command: NCG_WIKI_ONLY_MANUAL_CLONE=1 NCG_WIKI_KEEP_FIXTURE=1 dotnet run
--file skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiDeliveryTests.cs.
Protected local fixture IDs: red aacf39312e2f4a0d993fd32f6773000e; green
b0e91b790b18449f827ee027045e37a0. Root also ran the full affected Delivery suite on
W2: exit0, eight behavior groups plus the summary, fixture
4885f34713da4aebadf1991c51a3d85e. Unrelated resolver/recovery inputs retain their
previous verification. The active spec now names this composed scenario explicitly and
contains one copy of the existing case-alias scenario.

## W3 review repair: full configured Git output bound

KISS-W2-01 reopened delivery process-boundary coverage. With public capture
max_output_bytes4096, a real pinned 3841-byte Markdown blob failed W2 planning as
process_output_limit. W3 changes only the retained-byte ceiling and overflow
classification: keep the actual configured cap and check the limit task even when
a fast producer has already exited. No diagnostic reservation is needed because
delivery failure metadata is saved separately.

Targeted public CLI regression passes (exit0): the complete 3841-byte blob is
retained byte-for-byte, plan succeeds and delivery-status confirms delivered;
a 4097-byte fast Git producer still blocks plan with process_output_limit, private
bounded diagnostics and unchanged synthetic memory. Its process exits0 while
the supervisor correctly classifies overflow. Fixture requests pass limits only
through public capture, without rewriting bindings.

Command: NCG_WIKI_ONLY_OUTPUT_CAP=1 NCG_WIKI_KEEP_FIXTURE=1 dotnet run --file
skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiDeliveryTests.cs.
Root inspected actual public transcript results. Protected fixture IDs: red
80150a96da36455f8aa994b9f82257b4; green 5616410b68174b88b289793937f36994.
Root's full affected Delivery suite also exits0 with nine behavior groups plus
the summary. Its actual public-cli.log remains in protected local fixture
dcb1b4773c5849a8a55b18506d3c2872 (KEEP_FIXTURE enabled). Targeted independent
DRY/SOLID/KISS delta receipts carry unaffected coverage from its original candidate.

## Limits and scope

### 2026-10-13 delivery-package dependency check

The implementation write set excludes the pre-existing extractor-wrapper work.
Root therefore copied the current resolver/helpers/integration fixture into a
private isolated candidate and supplied the committed-base extractor from main
780e874. The actual composed public CLI fixture exits0: all four workflow groups
pass, including full batch/page proof, exact sources, paged Docs history and
idempotent completion. This checks the delivered contract independently of that
unrelated working-tree dependency diff. No real automation state was touched.
Protected candidate ID: ehq5gY; integration artifact ID:
d66b0371f9b347e6801834077521ec28. Base extractor plus current entrypoint contents
remain reproducible from the stated Git base and reviewed write set.

The 2026-10-12 execution probes used synthetic session stores and local bare Git remotes;
they establish tool/protocol behavior rather than current NCG semantics, deployment
or actual wiki publication. At that implementation-only stage no NCG
production/development operation, real checkpoint advance, fresh live wiki run,
repository push or archive was performed. The separately authorized 2026-10-13
automation execution now supplies real delivery/checkpoint and sampled original
source evidence; its semantic correction and final state are documented in the
linked live verification record. Runtime/deployment verification remains outside
this work.

Pre-existing extractor-wrapper/skill-install/link changes are preserved, excluded
from this implementation write set and included only as declared test dependencies
where used. Generated cache changes from our tests were removed without changing
source. The current effective prompt is private; the shared template contains no
personal repository paths. Applicable standards and structural reviews are recorded
separately in completion.md; this file alone is not a structural review approval.
