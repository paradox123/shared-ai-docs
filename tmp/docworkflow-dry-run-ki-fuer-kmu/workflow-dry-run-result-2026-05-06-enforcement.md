# DocWorkflow Enforcement Trial Run: KI fuer KMU Free Entry v2 Parent Spec

## Session Briefing

- Modus/Skill: Spec Sizing Gate -> `spec-orchestrator` enforcement trial -> child readiness gate simulation.
- Source of Truth: temp-folder copies under `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/`.
- Ziel: Test whether the new enforcement layer blocks implementation until Child Index, Hardening Queue, Hardening Verdict, and Child Session Handoff are synchronized.
- Nicht-Ziele: No changes to original KI-fuer-KMU specs, no runtime implementation, no legacy backfill, no product redesign.
- In Scope: Parent/Child routing, Child Index enforcement, Hardening Queue, S3 next-session handoff, delivery/closeout blocking behavior.
- Verification/Review: source inspection with `rg`, line counts, and manual consistency review against the updated DocWorkflow.
- Offene Entscheidungen: none for the trial run.

## Commands Run

```sh
sed -n '1,260p' tmp/docworkflow-dry-run-ki-fuer-kmu/workflow-dry-run-result.md
sed -n '1,260p' tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-child-specs-index.md
sed -n '1,220p' tmp/ki-fuer-kmu-parallel-work-playbook/orchestrator-parallel-work-dry-run.md
sed -n '1,220p' tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md
rg -n "^## (Review Control Surface|Parent Scope Conformance|Decision Freeze Pack|Dependencies and Write-Set|Closeout Sync Targets|Child Session Handoff|Verification Commands|Definition of Ready|Definition of Done|History)|Readiness Status|IMPLEMENTATION READY|READY WITH NON-BLOCKING|NEEDS HARDENING|NEEDS PARENT/ORCHESTRATOR SYNC" tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s*.md
wc -l tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s*.md
```

Structural result:

- S0: 39 lines.
- S1: 607 lines, accepted historical child with strong implementation/evidence sections.
- S2: 371 lines, accepted historical child with closeout evidence.
- S3: 543 lines, deep active child draft.
- S4-S7: 48-50 lines each, thin child drafts.
- The strict section scan found no active child `Review Control Surface`, `Parent Scope Conformance`, `Dependencies and Write-Set`, `Closeout Sync Targets`, or `Child Session Handoff` headings; it only found `## History`.

## Sizing Gate Result

Verdict: **TRIGGERS PARENT/CHILD**

Reasoning stayed stable from the previous dry run:

1. The parent spec spans UX, survey delivery, provider activation, content bundles, local workbench, RAG/ROI, reporting, security, and harness behavior.
2. Delivery naturally splits into S0-S7 with separate Done signals.
3. Verification cycles are heterogeneous: local runner, Docker harness, survey service, bundle/manifest checks, provider readiness, RAG/ROI/reporting, and cross-slice replay.
4. A direct implementation run against the parent would create context pressure and scope drift.

Routing: `spec-orchestrator` remains the right first step. OpenSpec remains the default delivery ledger for later Parent/Child implementation, while Parent/Child artifacts remain the scope/readiness control layer.

## Enforcement Verdict

The new enforcement layer works and is stricter than the previous dry run.

Key change in outcome:

- Previous run: S3 could be described as `READY_CANDIDATE -> NEEDS HARDENING`.
- New enforcement run: S3 is **not deliverable** and should be reported as `NEEDS PARENT/ORCHESTRATOR SYNC` until the Child Index is upgraded, then `NEEDS HARDENING` until a documented Hardening Verdict and Child Session Handoff exist.

No active child is `IMPLEMENTATION READY` under the new rules.

## Child Index Assessment

Existing child index:

- Path: `_specs/2026-05-05-free-entry-v2-child-specs-index.md`
- Current shape: simple slice/status list.
- Enforcement result: **INSUFFICIENT AS OPERATIONAL CHILD INDEX**

Why:

1. It lacks Parent Coverage per child.
2. It lacks Readiness / Hardening Verdict.
3. It lacks OpenSpec / Ledger pointers.
4. It lacks dependencies and allowed write-sets.
5. It lacks verification summary and evidence/closeout links.
6. It lacks Backlog / Re-entry and Next Action.

Minimal Child Index shape that the orchestrator should now create or patch:

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 Repo Freeze | `2026-05-05-free-entry-v2-s0-repo-freeze-legacy-quarantine-spec.md` | Legacy quarantine / repo freeze | `IMPLEMENTED; NEEDS CLOSEOUT DECISION` | historical/direct or prior evidence TBD | none for active next slice | none unless closeout sync | evidence review only | implemented status, closeout unclear | none visible | Decide whether to close/accept or leave historical implemented. |
| S1 Vertical Spike | `2026-05-05-free-entry-v2-s1-vertical-architecture-spike-spec.md` | Runtime skeleton, harness baseline, survey stub, bundle dummy | `REFERENCE_DONE / NO BACKFILL` | archived OpenSpec noted in spec history | none | no edits unless explicit reference lift | accepted verification replay recorded in spec | Accepted, archive noted | S2-S7 follow-ups already named | Use as verification recipe, do not migrate. |
| S2 Survey Handoff | `2026-05-05-free-entry-v2-s2-survey-delivery-answer-handoff-spec.md` | Survey delivery, answer artifact, import/retention | `REFERENCE_DONE / NO BACKFILL` | archived OpenSpec noted in closeout evidence | S1 baseline | no edits unless explicit reference lift | accepted verification replay recorded in spec | Accepted, archive path noted | later survey content in S5 | Use as verification recipe, do not migrate. |
| S3 Content Bundle | `2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md` | Bundle/manifest/readiness/workbench/plugin baseline | `NEEDS PARENT/ORCHESTRATOR SYNC -> NEEDS HARDENING` | OpenSpec default for later delivery | S1/S2 accepted patterns | S3 child spec only during hardening; parent/index read-only unless integrator | markdown/content review first; runtime commands later | none yet | S4/S6/S7 consume S3 outputs | Upgrade index row, then harden S3. |
| S4 Provider Guides | `2026-05-05-free-entry-v2-s4-provider-activation-guides-spec.md` | Provider activation, guides, readiness policy | `NEEDS HARDENING` | OpenSpec default later | S2 answers, S3 provider-guide content set | S4 child spec only during hardening | none yet | none yet | current provider-source freshness may be needed | Harden after/parallel with S3 as spec/doc lane. |
| S5 Survey Content | `2026-05-05-free-entry-v2-s5-survey-v2-content-spec.md` | Survey variants, routing, content catalog | `NEEDS HARDENING` | OpenSpec default later | S2 answer/API contract | S5 child spec only during hardening | none yet | none yet | final wording may require product decision | Harden survey schema/fixtures. |
| S6 ROI/RAG Runtime | `2026-05-05-free-entry-v2-s6-roi-rag-runtime-spec.md` | ROI/RAG/report runtime | `BLOCKED / NEEDS HARDENING LATER` | OpenSpec default later | S3/S4/S5 stable contracts | S6 child spec only during hardening | none yet | none yet | waits for upstream outputs | Keep blocked until S3/S4/S5 stabilize. |
| S7 Docker Safe Harness | `2026-05-05-free-entry-v2-s7-docker-safe-harness-spec.md` | Full harness/cross-slice replay | `NEEDS HARDENING` | OpenSpec default later | S1/S2 evidence and S3-S6 contracts | S7 child spec only during hardening | none yet | none yet | implementation waits for S3-S6 | Harden harness matrix late or as doc-only skeleton now. |

## Hardening Queue

| Child | Current Status | Required Hardening | Sources To Read | Blockers | Next Handoff Target |
|---|---|---|---|---|---|
| S3 | `NEEDS PARENT/ORCHESTRATOR SYNC -> NEEDS HARDENING` | First upgrade Child Index row. Then add Review Control Surface, Parent Scope Conformance, Decision Freeze Pack, Dependencies/Write-Set, Closeout Sync Targets, strict Hardening Verdict, and Child Session Handoff. | Parent V2-FR-030/031/031a/031b/032, S1/S2 accepted patterns, S3 spec. | No product blocker seen; index sync is now a workflow blocker. | `child-spec-hardening` for S3. |
| S4 | `NEEDS HARDENING` | Provider matrix contract, guide freshness contract, visual/source policy, readiness cases, redaction cases, verification commands, write-set. | Parent V2-FR-020-024a/053, S2 answer contract, S3 provider-guide content-set once stable. | Provider source freshness may require current-source verification before implementation. | `child-spec-hardening` for S4. |
| S5 | `NEEDS HARDENING` | Survey schema/fixture contract, A/B/C parity matrix, KRITIS routing cases, local/server rendering verification, question identity/versioning. | Parent V2-FR-001/002/010/011/012/040, S2 answer contract, old survey source as non-normative input. | Final wording may require user/product decision. | `child-spec-hardening` for S5. |
| S7 | `NEEDS HARDENING` | Cross-slice harness case matrix, exit-code mapping, secret-leak assertions, Docker/Compose command contract, replay strategy. | Parent harness section, S1/S2 evidence, S3-S6 drafts. | Full implementation waits for S3-S6 contracts. | `child-spec-hardening` for S7 doc lane. |
| S6 | `BLOCKED` | ROI/RAG status machine, report contract, blocked/prep report cases, source/redaction cases, verification commands. | Parent V2-FR-041/050/051/052/053/062, S3/S4/S5 hardened specs. | Blocked until S3/S4/S5 are stable enough. | Later hardening after upstream stabilization. |

## Delivery Gate Simulation

`spec-change-delivery` should refuse implementation for every active child right now:

| Child | Delivery Allowed? | Reason |
|---|---|---|
| S3 | No | No synchronized Child Index row, no documented Hardening Verdict, no Child Session Handoff. |
| S4 | No | Thin draft; no normative contract, verification commands, DoR/DoD, or verdict. |
| S5 | No | Thin draft; no fixture/schema contract, verification commands, DoR/DoD, or verdict. |
| S6 | No | Dependency-blocked and thin draft. |
| S7 | No | Integration harness spec is not hardened; implementation depends on S3-S6. |

This is the desired enforcement behavior: implementation cannot bypass hardening by treating `ready_candidate` or a detailed draft as ready.

## Closeout Gate Simulation

`spec-closeout` should now enforce:

1. S0 cannot silently become accepted without verification/evidence review and Parent/Index sync.
2. S1/S2 accepted evidence can remain historical/reference evidence; no forced migration is required.
3. Any future S3 closeout must update Parent Coverage, Child Index/Slice Plan, Backlog/Re-entry, Evidence Links, OpenSpec Status, and next Child Session Handoff before S4/S5/S6/S7 becomes the leading child.
4. Broad project docs sync should wait for Parent closeout unless a child changes user-facing/project docs or public contract docs.

## Recommended Next Move

Next concrete workflow step:

1. Run `spec-orchestrator` against the temp parent/child set and update the temp Child Index into the operational format above.
2. Then run `child-spec-hardening` for S3.
3. Only after S3 has `IMPLEMENTATION READY` plus synchronized Child Index and Child Session Handoff should `spec-change-delivery` be allowed.

## Child Session Handoff

- Parent: `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md`
- Child: `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md`
- Child Index / Queue: `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-child-specs-index.md`
- Naechster Modus/Skill: `spec-orchestrator` integration-owner index upgrade, then `child-spec-hardening`
- Aktueller Verdict: `NEEDS PARENT/ORCHESTRATOR SYNC -> NEEDS HARDENING`
- Scope Summary: Make S3 ready as the content-bundle/manifest/workbench child without changing product intent.
- Non-Goals: No runtime code, no original KI-fuer-KMU edits, no S4-S7 broad hardening, no legacy migration.
- Allowed Write-Set: for the next temp trial, child index plus S3 temp spec if explicitly running hardening; otherwise report patches only.
- Shared / Read-only Files: parent spec, S1/S2 accepted specs, S4-S7 drafts, slice plan, OpenSpec evidence.
- Verification Commands: markdown/section scan and content-quality review; runtime commands are not allowed until S3 is implementation-ready.
- Evidence / OpenSpec: OpenSpec default recommended for later delivery; no active S3 OpenSpec change yet in this trial.
- Offene Blocker oder non-blocking Notes: Child Index is too thin; S3 lacks strict Hardening Verdict and Child Session Handoff.
- Fresh Session empfohlen: yes before real S3 implementation; not required for temp index/hardening simulation.

## Trial Verdict

**PASS with stronger blocking behavior.**

The enforcement layer catches the exact gap it was meant to catch:

- Parent/Child still routes correctly.
- Child Index is now recognized as insufficient, not merely "present".
- Hardening Queue is derived from the Child Index gap.
- S3 cannot move into implementation without synchronized index, verdict, and handoff.
- S1/S2 remain accepted evidence without forced legacy migration.
- Closeout has a clear future sync target.

## Mini-Retro

- Was wurde entschieden? The new enforcement layer should classify S3 as blocked from delivery until index sync and hardening verdict exist.
- Was wurde geaendert? This temp-folder trial report only.
- Was bleibt offen? Whether to run the next trial step that actually upgrades the temp Child Index and hardens S3.
- Welche Evidenz/Verification fehlt? A real temp `child-spec-hardening` pass for S3 and then a simulated `spec-change-delivery` refusal/allowance check.
- Welche Skill-/Workflow-Reibung ist aufgefallen? The old child index being "present" is not enough; the new operational columns are necessary to prevent accidental delivery.
- Session-/Kontextzustand: Good to inspect this result, then optionally continue with temp Child Index upgrade.
