# Missing-session tolerance: implementation evidence

## Scope and identity

Source: Daniel's direct 2026-10-14 request to ignore absent/deleted sessions without individual approvals, so absence alone does not abort the NCG wiki automation.

Fixed shared-ai-docs base: `e5130fac0115d6ed0779759fc4ce975a62c660b4`. Work-in-progress identity: protected `candidate-manifest-v2.txt` in [the evidence directory](</private/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/ncg-missing-policy.IVhvdx>). Its nine SHA256 entries cover:

- `skills-repo/skills/improve-skills/scripts/wiki-review-run/{ReviewRun.cs,NcgWikiDelivery.cs,ReviewRunTests.cs,NcgWikiIntegrationTests.cs,README.md,NCG-Automation.md}`
- this change's `proposal.md` and `specs/recoverable-wiki-review/spec.md`
- protected intended effective `automation-update.json`.

`tasks.md` is progress only; this record, reviewer receipts and raw logs are evidence, excluded from behavior-bearing identity. Unrelated existing dirty RAG/QMD/skill/Python extractor/test changes and existing scratch/cache files were preserved and excluded. No NCG code/wiki files, infrastructure, CI or deployment systems are changed. Existing .NET file-based helpers remain the production implementation; Python is only the existing external resolver boundary and test response fixture.

Applicability: substantive policy/contract/configuration behavior; full requirements verification and independent sequential structural review required.

## Requirements verification

Detailed expected/observed/counterexample mapping: [requirements.md](</private/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/ncg-missing-policy.IVhvdx/requirements.md>). Requirement version: this active change's spec and the reviewed canonical contract/schema.

| Requirement | Observed outcome and direct evidence |
| --- | --- |
| Missing window, carry and combined selection are ignored without ID approval | Actual resolver/public capture tests and six one-session batches passed; exact ignored IDs reported, raw exit2/safe=false and original manifest retained. `capture-red.log` fails before implementation; `capture-regressions.log` passes afterward. |
| Strict default/legacy allowlist and fixed capture identity remain | Default/legacy, invalid enum, changed policy blocking and unchanged-policy snapshot resume tests pass. All-missing scope still needs its actual empty page. |
| Other unsafe data do not become acceptable | Actual malformed/unknown-timestamp histories and eight contradictory diagnostic/storage/safety responses reject; existing corruption, missing-middle batch/page and timeout/retry tests pass. Previously pinned source integrity checks are not relaxed. |
| Finalization alone prunes validated missing carries | Corrected public red test retains deleted IDs under old pruner; implemented green finalization removes them while retaining all three other objects/order, historical memory and required source/Docs proof. Repeated terminal finalize is idempotent. |
| Existing source and delivery protection remains | Default composed integration and NcgWikiDelivery regression fixtures pass: changed pins, migration/Docs completeness, clone proofs, ownership/symlink checks, failed-push/restart and bounded-process cleanup. All Git remotes are synthetic local bare repos. |
| Live automation, schedule and checkpoint preservation | Automation update returned success. Re-read stored definition: prompt equals reviewed payload; every other field matches observed baseline except the normal update timestamp. Official memory has identical SHA256 before/after update and capture invalidation. |

Commands from shared-ai-docs, all green:

```text
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRunTests.cs
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/ReviewRunBatchTests.cs
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiIntegrationTests.cs
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiIntegrationTests.cs -- --ignore-missing
dotnet run --file skills-repo/skills/improve-skills/scripts/wiki-review-run/NcgWikiDeliveryTests.cs
openspec validate ignore-deleted-ncg-review-sessions --strict
git diff --check -- skills-repo/skills/improve-skills/scripts/wiki-review-run openspec/changes/ignore-deleted-ncg-review-sessions
```

Raw test logs/status: protected evidence directory `capture-regressions`, `batch-regressions`, `integration-default`, `integration-ignore-final`, `delivery-regressions`. Finalizer red/green CLI artifact logs are retained respectively at:

- [red integration log](../../../.scratch/ncg-wiki-review-followup/verification/integration-a851dd1d651c4a3aa7f075d2fcaa73c2.log)
- [green integration log](../../../.scratch/ncg-wiki-review-followup/verification/integration-c21f4988e49c4ffda694d55b38e386b9.log).

Only branch-specific fixture expectations changed after the default integration run; default runtime inputs are unchanged. A later canonical-contract wording correction changed no runtime inputs, so these behavioral results are reused. No real full wiki review, remote NCG inspection or deployed/runtime behavior is verified by these isolated tests.

## Standards and independent review

AGENTS.md/README/OpenSpec ownership and no duplicated parser/workflow mechanics → DRY. Ownership/dependency/error/capture identity and guarded finalization contracts, C#/.NET slice preference and read-only infrastructure boundary → SOLID. Naming, smallest scoped structure, truthful commands/dependencies/side effects and scoped documentation → KISS. Whitespace/OpenSpec syntax/runtime are covered by actual tooling above.

- DRY: `/root/missing_policy_dry`, fresh context. Initial nine-entry identity reviewed. DRY-01 found stale approval-specific recovery wording in NCG-Automation; implementer repaired it. Same reviewer verified v2's sole contract delta and carried unaffected coverage forward. Current result clean; [receipt](</private/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/ncg-missing-policy.IVhvdx/dry-review.md>).
- SOLID: `/root/missing_policy_solid`, fresh context, v2 manifest all nine hashes verified. Policy/identity/default and diagnostic/storage/proof/finalization ownership plus dependency boundaries checked. No binding violations or material heuristic findings; [receipt](</private/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/ncg-missing-policy.IVhvdx/solid-review.md>).
- KISS: `/root/missing_policy_kiss`, fresh context, v2 all nine hashes verified. Scoped structure, naming/dependencies, truthful commands and intended config compared with observed baseline. No binding violations or actionable heuristic suggestions; [receipt](</private/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/ncg-missing-policy.IVhvdx/kiss-review.md>).

## State and delivery

State: `awaiting-acceptance`; requested implementation and live automation configuration delivered, requirements checks and sequential structural reviews complete. No shared-repository commit, push or OpenSpec archive is authorized/performed; ordinary implementation does not infer an acceptance/archive request.

The existing `keep-ncg-wiki-current` heartbeat was updated through automation_update with its full preserved fields. Protected observed [before](</private/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/ncg-missing-policy.IVhvdx/automation-before.toml>)/[after](</private/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/ncg-missing-policy.IVhvdx/automation-after.toml>) definitions prove the exact prompt-only policy change plus normal update timestamp; no manual TOML/memory edit.

The old exact blocked capture `run-1fab7bf2bbd944d5b6dbbc1bbad7124f` was explicitly invalidated through canonical ReviewRun under the store lock. Actual output says `evidence_preserved:true`, `checkpoint_changed:false`; its invalidation marker and absent active pointer were rechecked, with named raw batch stdout/stderr/exit files still present. This permits a fresh future capture, not reuse with altered helper/definition identity. [Invalidation output](</private/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/ncg-missing-policy.IVhvdx/invalidation.stdout>).

Official memory retained its complete pre-change SHA256 `49cdbfd8af2b4846de8424d96be0d25f5f3a2063f3056f29d6c68f086ccbb1c3`; cursor/carry/source/Docs bundle and run/review notes were not advanced. No new full live wiki run was executed. NCG project documentation/research/meetings, Daily/Notion and production runtime were not investigated for this local automation-policy task; no corresponding coverage or implementation/deployment claims are made.
