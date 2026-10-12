# Completion: NCG wiki review improvements 1–3

Date: 2026-10-12. State: **technically-complete** for the accepted source candidate; authorized delivery is pending.

## Scope and identity

Owning repository: shared-ai-docs, `main`. Fixed base: `fc70c24fd7282516556040412bd098911c95f0df`. Accepted candidate V4: tree `bdadf6876c91b44a1d800bb4012854986656351a`; the eleven exact reviewed file hashes are in [evidence/content-manifest.json](evidence/content-manifest.json).

This substantive change implements the authoritative Processed cursor, complete same-manifest extraction proof, and protected capture/topic resumption. The resolver's existing snapshot API is a required included prerequisite. Review repairs R1 (stable page replay) and S1 (filesystem alias exclusion before effects) are included. Concurrent follow-up planning, batching/recovery/delivery code, pre-existing extractor-wrapper edits, skill-link edits, caches and unrelated scratch work are excluded and preserved. The personal automation definition was updated through its supported tool; private definitions, memory, request payloads and raw runtime logs remain outside Git.

Completion and evidence extracts are generated records excluded from the reviewed-content identity. Original private verifier/reviewer receipts and logs remain retained; [evidence/reviews.md](evidence/reviews.md) records their identities and attributable conclusions. Matching source hashes map their observations to V4 without claiming a new execution.

## Requirements: expected and observed

Source: accepted `specs/recoverable-wiki-review/spec.md`, hash `1649df3e6548913b87040f497532f8481d019af88197b3ebdfdd35a0b828b831`. Requirements verification V4 passed after direct eleven-file hash recomputation; V4 specification equals V2 plus the four-line S1 scenario, and tasks equal V2 with only 3.2 checked.

| Requirement | Expected | Observed evidence and limits |
| --- | --- | --- |
| Authoritative cursor | Current-header Processed end alone selects sessions; malformed present cursor blocks, absent cursor permits explicit legacy fallback. | Public resolver regression selects a 06:40 session from Processed 06:15 despite completion 07:07. Malformed/ambiguous and historical-header counterexamples pass. Resolver suite: 25 tests. No official checkpoint change. |
| Complete extraction | One immutable manifest/scope, contiguous terminal pages, exact IDs/counts, zero omissions and resolved manual clones; unchanged page replay retains proof. | Independent three-page restart across processes returns `page_reused`, equal proof `042f9424f1b0bf97fb3b82f07ebb1c56f563eede42273c51b3d2a15c90682177` before/after, reusable topic. Missing middle page, capped terminal omissions, corrupt/foreign outputs, changed bounds and unresolved clones block. Verified clone resolutions survive replay. R1 repaired and independently passed. |
| Protected capture/resumption | Retain exact selection/index/process evidence; changed authoritative input blocks adoption; no official-memory/Git/network/wiki writes. | Separate processes resume the same run despite a changed live index, ignored scheduler timestamp and failure prose. Snapshot/tool/definition/checkpoint tampering and concurrent selection cases pass. Exact approved carried-only missing case is narrow; unrelated unsafe conditions block. Actual filesystem case alias rejects before store/run/active/lock creation or resolver invocation; outside sibling succeeds. S1 repaired; distinct case-sensitive names were source-inspected, runtime unavailable on this filesystem. |
| Context-bound topics | Source/candidate/wiki/extraction changes invalidate comparisons; pending edits never certify delivery or checkpoint permission. | Unchanged comparisons are reusable; changed source/wiki/docs pin is stale. Explicit zero-session proof supports Git-only topics and separate docs-main pin without extending the four-code-tip map. `update_needed` remains `pending_delivery`. Synthetic pins prove contracts, not real reachability or semantic wiki correctness. |
| Scoped integration | Preserve schedule, target, 500 rule, source/migration/delivery gates and official memory. | Actual supported-tool readback changed only prompt/updated_at, with ACTIVE daily 08:00 and original target preserved. Installed definition SHA256 `4f49c7854a255ecc483673010db11a66cd0055cf9e35e37b52672306ca5d663a`; memory remains `1c3fec3e3f8035bad1bcbdebc432b19ee8473c63ab080d9306c60f8d9c9958dd`. No complete live automation/wiki run was performed. |

## Standards and independent reviews

Binding sources: root AGENTS.md/README, accepted OpenSpec change and shared change-accepted/code-review workflow. Sequential independent reviews use fresh dimension-specific contexts and bounded same-reviewer follow-up after repairs.

| Owner | Assigned coverage | Current result |
| --- | --- | --- |
| DRY, `/root/closeout_dry` | Canonical workflow/cutoff authority, resolver/extractor ownership, shared proof and topic context, stable replay | V4 clean; original V2 coverage retained, S1 delta and restored accepted scope directly rechecked. |
| SOLID, `/root/closeout_solid` | CLI/JSON/errors, immutable snapshot boundaries, coherent dependencies and local effects | V4 clean; S1 resolved through direct source/probe inspection, unchanged V2 coverage retained. |
| KISS, `/root/closeout_kiss` | C# file-based vertical slices, justified Python seam, naming/readability, truthful entrypoint/dependency/effect docs, public examples and private-data/scope discipline | V4 PASS; no binding violation or material blocker. Optional usage-list housekeeping is deferred. |
| Requirements verifier and automated checks | Public behavior/TDD, OpenSpec source/lifecycle, unchanged memory, read-only NCG boundary and whitespace/compilation | Requirements V4 passed; retained red/green public-CLI evidence and final validations below. |

## Final checks and limitations

Retained executable evidence: 51 Python tests (25 resolver, 26 base extractor), 24 helper behavior groups, independent 13 groups/70 public CLI calls, and one focused filesystem-alias CLI probe. The V3 helper/tests/README are byte-identical in V4; all other executable inputs match their respective proved candidates. Baseline extractor SHA256: `2f949cc434db2fb7f7e31e21d8eba72a3d842a5195cf438856a2c305ae705f84`. Unrelated working-tree wrapper changes were not tested or delivered as part of this candidate.

Repository verification entrypoints are the README's .NET file-based public CLI tests, Python unittest discovery with bytecode disabled, `openspec validate harden-ncg-wiki-review-checkpoints --strict`, and `git diff --cached --check`. Strict V4 validation and scoped whitespace check passed; the archive CLI validated and copied all five requirements. Canonical-spec strict validation and final staged correspondence are checked after this record is prepared.

No NCG production/development service was contacted. Real source reachability/final pin equality, semantic wiki review, successful wiki delivery and final atomic automation checkpoint were not exercised by these isolated acceptance probes. Technical helper completion does not claim those operational outcomes.

## Authorized delivery and archive mapping

The user explicitly accepted this implementation and authorized commit, push, merge if necessary and owned disposable-work cleanup. Target: existing shared-ai-docs `main`; no separate branch currently needs merging. This is the pre-delivery record: the verified commit/push outcome is recorded separately after execution in protected closeout evidence. Only the accepted snapshot was archived; the concurrent active future plan is preserved.

Archive path mapping: each reviewed `openspec/changes/harden-ncg-wiki-review-checkpoints/*` file maps to the same suffix under `openspec/changes/archive/2026-10-12-harden-ncg-wiki-review-checkpoints/`, with all five original bytes/hashes unchanged. The six shared guidance/code/test/README paths remain unchanged. Generated completion/evidence records are additional metadata.

Canonical requirements map to `openspec/specs/recoverable-wiki-review/spec.md`. The archive transformation replaces the ADDED heading with a specification/Purpose/Requirements header and a truthful editorial purpose; the complete requirement body is identical after normalizing only the terminal newline. Body SHA256 `1aeb20000bdc63cd647f031e605743b507855d3185cb675bcbe06d03c81d303f`; canonical-file SHA256 `77c542014ede2aeb073891305e2154daa0315479f80492d75f210c5968c9fcb3`. No substantive requirement or code changed after the reviews, so their coverage is retained.
