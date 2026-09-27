# Completion: durable page-response resumption

Status: requirements and structural reviews verified; delivery pending.

## Scope and identity

- Repository: `/Users/dh/.codex/worktrees/shared-wiki-lean-requirements` (`shared-ai-docs`).
- OpenSpec umbrella: `operate-contextual-llm-wiki`; accepted sub-scope: `.scratch/lean-shared-wiki/spec.md`.
- Fixed base: `7cd82c7a1290a3e761fce55622921e44a98c00ae` (`origin/main` at review start).
- Candidate file-manifest SHA-256: `f4e2a67aed3b8c6c7814aa27cc6d1256457e52aa872b7ea1593a2388ec94c2b9`. It is SHA-256 over the sorted lines `path NUL SHA256(file) LF` for the 13 changed/new implementation, test, spec and evidence files listed by `git diff HEAD` plus `git ls-files --others --exclude-standard`; this completion record and later reviewer receipts are excluded to avoid self-reference.
- The separate main checkout is on `codex/scripted-ticket-coordination` and has unrelated edits to `skills-repo/skills/improve-skills/SKILL.md` and `skills-repo/skills/install-vendor-skills/SKILL.md`. They were not read for implementation, modified, staged or included.

## Applicability

Substantive behavior change: the pinned compiler can hand each complete page response to the host cache; the helper stores and reuses only compatible responses and continues through the ordinary validation/publication pipeline. DRY, SOLID and KISS review is required. Repository standards are in `AGENTS.md`, `docs/agents/issue-tracker.md`, `docs/specops`, the active OpenSpec requirement and the public maintenance contract.

## Requirements verification

The accepted tracker specification is the bounded acceptance source. Requirements 1–11 describe the existing shared-wiki contract and reuse the earlier real-config and public-interface evidence; this change does not redesign source selection, synthesis, citations, Markdown output, QMD, or no-op behavior. Requirements 12–15 concern durable model work and partial-run safety:

| Requirement | Expected behavior | Observed result and evidence |
|---|---|---|
| 1. Explicit source selection | Only configured Markdown repositories feed the common wiki. | Existing eight-repository production inventory and unchanged common config are recorded in `contextual-llm-wiki/evidence/resumable-maintenance-06.md`; production config SHA-256 remained `f878d6123252a7474a44d6cf0ba561bec9b21d7f1a14bb2cfaf1d73550d927cf` during this verification. |
| 2. Include the private repository | The configured private subject area participates in the common source set. | Existing production inventory/configuration evidence in `resumable-maintenance-06.md`; the implementation did not change source configuration. |
| 3. Include Meetings and Projects | Configured Markdown under both trees participates in the same source set. | Existing production inventory evidence in `resumable-maintenance-06.md`; configuration remained byte-identical during the live run. |
| 4. Preserve repository/path identity | Same-named sources remain distinguishable and citations resolve to originals. | Existing public CLI/source identity evidence in `evidence/shared-wiki-01.md` and `shared-wiki-02.md`; new cache key also binds source IDs and original paths. |
| 5. Keep originals unchanged | Maintenance must not write source Markdown. | New public-helper fixture records both source files before/after an interrupted run and source change; both remain byte-identical to the intended fixture contents. |
| 6. Combine relevant cross-repository evidence | A concept can synthesize relevant evidence from separate selected repositories. | Existing real compiler/CLI acceptance in `evidence/shared-wiki-01.md`; the new regression fixture exercises a concept owned by two temporary repositories. |
| 7. Cite original sources | Generated claims retain verifiable original references. | New regression asserts both source paths in the published page; existing real source/provenance acceptance is in `shared-wiki-01.md` and `shared-wiki-02.md`. |
| 8. Publish Markdown into the Vault | Valid completed pages become Markdown at the configured output. | New regression reads the generated page from the fixture Vault after resume; the production run itself stopped before full publication and is not counted as publication evidence. |
| 9. Expose pages through shared QMD | A completed article is searchable in the configured QMD collection. | New regression confirms `query.engine === "qmd"` and the expected page evidence; prior shared-wiki acceptance covers the real QMD integration. |
| 10. Rerun maintenance after source changes | The public helper is the repeatable maintenance entry point. | The new scenario invokes the public bounded helper for interruption, resume, no-op and source change; existing operations evidence covers the helper contract. |
| 11. No-op without new model work | An unchanged completed run makes no provider requests. | New regression checks an unchanged helper run is `noop` and the provider call count does not increase; prior acceptance is in `resumable-maintenance-01.md`. |
| 12. Preserve completed extraction work | A fresh process reuses compatible completed extraction responses. | Existing restart evidence in `resumable-maintenance-03.md` and `resumable-maintenance-06.md`; the live runs reused 2209 extractions. |
| 13. Preserve individual page responses | A fresh process reuses a valid page response saved before the batch completes. | The public-helper regression first reproduces the duplicate provider request, then proves reuse after a bounded stop. In production, run `20260927T135350-89197` saved 322 valid page responses; fresh run `20260927T141443-45826` reused all 322 and saved 8 more (`invalid: 0`). Reports are linked from `contextual-llm-wiki/evidence/page-response-resumption-2026-09-25.md`. |
| 14. Invalidate stale responses | Source/generation contract changes must cause a fresh request rather than reuse old output. | New regression changes Beta's original Markdown, verifies a fresh request and current generated content, and verifies the unrelated control page remains unchanged. Cache identity additionally includes request/model/provider/compiler/publication contract and current owner-source hashes. |
| 15. Report partial work honestly | A bounded run cannot claim success or publish an incomplete page. | New regression asserts `budget-exhausted`, pending work, no `lastCompleted`, and no incomplete page before resume. Both live invocations returned `ok:false`, exit 1 and pending compile/Wiki/QMD phases; neither is presented as full-import success. |

### Verification limits

The focused fixture uses temporary repositories and deterministic provider responses. Production verification used the changed worktree code against the real common configuration and production cache. It proves durable write/read and compatibility at process restart, but the bounded live invocations ended before the full compiler publication and QMD stages. The full first import and a later daily scheduler run remain separate open requirements in the umbrella OpenSpec.

## Existing verification reused

Before the final DRY refactor, the full serial Node suite `./wiki-node --test --test-concurrency=1 test/*.test.ts` passed 117/117, `npm run test:upstream` passed 59/59, `npm run test:operations` passed 14/14, and two consecutive `scripts/bootstrap.sh` executions succeeded. After the refactor, `./wiki-node --test --test-concurrency=1 test/maintenance-budget.test.ts` passed 12/12, `npm run typecheck` passed, and `git diff --check` plus strict OpenSpec validation passed. The original red-to-green regression and broader suite scope are in `contextual-llm-wiki/evidence/page-response-resumption-2026-09-25.md`.

After updating the acceptance evidence, `openspec validate operate-contextual-llm-wiki --strict --no-interactive`, `openspec validate --specs --strict --no-interactive` (46 specs) and `git diff --check` passed. The two production runners finished with no owned process remaining and the shared maintenance lock was free.

## Standards coverage

- OpenSpec and evidence accuracy (`AGENTS.md`, OpenSpec acceptance): reviewed in the SOLID/KISS passes; strict change/spec validation recorded above. The scoped tracker spec is accepted. The umbrella change is deliberately left active for independent incomplete work; no false full-import or scheduler claim is made.
- Keep fixture and generated runtime data out of the repository (`AGENTS.md`): verified by the staged-file review; only source patch, test, docs, OpenSpec/spec and evidence are in scope. Production `.local` run artifacts and generated page-response files stay in their configured ignored data locations. Required blank context markers in the saved upstream patch are exempted from trailing-whitespace checks by a file-scoped Git attribute.
- Preserve original repositories and change only the requested common wiki behavior: covered by the behavior fixture, existing acceptance evidence and the DRY/SOLID/KISS reviews.
- Formatting, type safety and behavior checks: `git diff --check`, TypeScript and the focused/full suites above.

## Structural review receipts

- DRY: `/root/review_dry`; no findings. The reviewer verified the final manifest `f4e2a67a…8ec94c2b9` and the whitespace rule; the prior duplicate cache read/validation and persistence path is shared by `readReusableResponse` and `saveValidatedResponse`, while extraction compatibility and page-source checks remain local.
- SOLID: `/root/review_solid`; no actionable findings. The reviewer verified the final manifest and confirmed the scoped Git attribute creates no responsibility-boundary issue; the host cache boundary and compiler/maintenance split remain coherent.
- KISS: `/root/review_kiss`; no actionable findings. The reviewer verified the final manifest and confirmed the narrow whitespace rule adds no avoidable complexity.
- Final stage hygiene delta: `.gitattributes` scopes `-blank-at-eol` to saved `.patch` files, whose unified-diff blank context lines require a leading space. This metadata addition does not alter implementation behavior; the final staged candidate manifest is `f4e2a67aed3b8c6c7814aa27cc6d1256457e52aa872b7ea1593a2388ec94c2b9`.

All three sequential full reviews completed against the same fixed base and implementation manifest; each reviewer then verified the final hygiene-only delta and final 13-file candidate manifest. No findings required reopening implementation checks.

## Delivery authorization

On 2026-09-27 Daniel explicitly accepted this scoped change and authorized commit, push and merge to `main` if needed, plus cleanup of implementation worktrees/artifacts. Planned branch: `codex/lean-shared-wiki-requirements`. The wider OpenSpec includes independent unchecked full-import, later-scheduler and upstream-release work; it remains active under the repository's archive rules. Delivery outcomes will be recorded here after they are verified.
