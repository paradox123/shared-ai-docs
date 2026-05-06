# New Workflow Test: KI fuer KMU Free Entry v2

## Session Briefing

- Modus/Skill: Spec Sizing Gate -> `spec-orchestrator` -> `child-spec-hardening` readiness assessment.
- Source of Truth: `_specs/2026-05-04-free-entry-v2-master-spec.md`, `_specs/2026-05-05-free-entry-v2-child-specs-index.md`, copied S0-S7 child specs.
- Ziel: Die grosse Parent Spec automatisch als Parent/Child-Vorhaben behandeln und den naechsten session-faehigen Child-Handoff erzeugen.
- Nicht-Ziele: Keine Runtime-Implementierung, keine Originaldateien aendern, keine breite Alt-Spec-Migration.
- Erwarteter Output: Sizing Gate, Orchestration Pack, Hardening Queue, Parallel Work Control Surface, S3-Handoff.

## Spec Sizing Gate

Verdict: **TRIGGERS PARENT/CHILD**

Signals:

1. Mehrere Capability-Domains: UX, Survey, Provider, Bundle/Content, Vault/Workbench, RAG/ROI, Report, Security, Harness.
2. Mehrere Verification-Zyklen: .NET Build/Test, local harness, Docker harness, Survey service, S3 bundle verification, Provider readiness, RAG/ROI, cross-slice replay.
3. Natuerlicher Slice-Schnitt S0-S7 existiert bereits.
4. Kontextkomprimierung waere bei Umsetzung aus der Parent Spec als Ganzes wahrscheinlich.
5. Bestehende Child Specs haben unterschiedliche Reifegrade.

Routing:

- Parent/Child wird automatisch als fuehrender Workflow genutzt.
- OpenSpec ist Default-Ledger fuer spaetere Delivery, weil es ein mehrstufiges Parent/Child-Vorhaben ist.
- `refine-plan` wird nicht als zusaetzlicher Fortschritts-Ledger gestartet.

## Delivery Orchestration Pack

### Parent

| Field | Value |
|---|---|
| Parent Spec | `_specs/2026-05-04-free-entry-v2-master-spec.md` |
| Status | `🟠 Plan` |
| Role | Parent/Master Spec and scope control layer |
| Main next step named by parent | S3 Content Bundle and Managed-AI Channel |

### Child Readiness

| Child | Current Status | New Workflow Readiness | Required Next Skill |
|---|---|---|---|
| S0 | `🔵 Implemented` | `NEEDS CLOSEOUT DECISION` | `spec-closeout` or accept as prerequisite evidence |
| S1 | `🟢 Accepted` | `REFERENCE_DONE / NO BACKFILL` | none |
| S2 | `🟢 Accepted` | `REFERENCE_DONE / NO BACKFILL` | none |
| S3 | `🟡 Spec` | `READY_CANDIDATE -> NEEDS HARDENING` | `child-spec-hardening` |
| S4 | `🟡 Spec` | `NEEDS HARDENING` | `child-spec-hardening` |
| S5 | `🟡 Spec` | `NEEDS HARDENING` | `child-spec-hardening` |
| S6 | `🟡 Spec` | `NEEDS HARDENING` | `child-spec-hardening` |
| S7 | `🟡 Spec` | `NEEDS HARDENING` | `child-spec-hardening` |

### Coverage Matrix

| Parent Scope Area | Covered By | Coverage Status | Notes |
|---|---|---|---|
| Legacy quarantine / source freeze | S0 | done/implemented | Formal accepted decision open. |
| Vertical architecture baseline | S1 | accepted | Use as verification pattern. |
| Survey delivery and answer handoff | S2 | accepted | Use as API/artifact/harness pattern. |
| Bundle, manifest, managed AI channel | S3 | partial/ready candidate | Strong content, needs workflow hardening. |
| Provider activation and readiness | S4 | pending | Skeleton only. |
| Survey content and routing | S5 | pending | Skeleton only. |
| ROI/RAG/report | S6 | pending | Skeleton only. |
| Full Docker/Safe Harness | S7 | pending | Skeleton only; late integration lane. |

Missing parent coverage: **none at slice level**.

Blocking parent conformance issues: **none proven**, but S3-S7 need explicit conformance tables before implementation.

## Hardening Queue

| Child | Priority | Required Hardening | Blocker Type |
|---|---:|---|---|
| S3 | 1 | Review Control Surface, Goldstandard Status, Parent Scope Conformance, Decision Freeze Pack, Dependencies/Write-Set, Closeout Sync Targets, final readiness verdict, session handoff. | workflow/content hardening |
| S4 | 2 | Provider matrix contract, guide freshness policy, official-link/screenshot source policy, readiness tests, secret redaction cases, verification commands. | content and current-source hardening |
| S5 | 2 | Survey schema/fixture contract, A/B/C parity, KRITIS routing cases, local/server render verification, question identity/versioning. | product/content hardening |
| S6 | 3 | RAG status state machine, ROI assumptions/report contract, blocked/prep outputs, LLM-readiness guard, verification commands. | dependency hardening |
| S7 | 4 | Cross-slice harness matrix, Docker/Compose command contract, exit-code mapping, secret-leak assertions, replay gates. | integration hardening |

## Parallel Work Control Surface

| Lane | Child/Work Block | Mode | Safe? | Allowed Write-Sets | Shared Files / Read-only Files | Dependencies | Verification Commands | Integration Owner | Merge/Sync Order |
|---|---|---|---|---|---|---|---|---|---|
| H1 | S3 hardening | spec/doc hardening | yes | S3 child spec copy, S3 handoff notes | Parent/index read-only | S1/S2 patterns | Review Control Surface + parent conformance review | Orchestrator | first |
| H2 | S4 hardening | spec/doc hardening | yes | S4 child spec copy | Parent/index read-only | provider source checks | content-quality review | Orchestrator | parallel after H1 starts |
| H3 | S5 hardening | spec/doc hardening | yes | S5 child spec copy | Parent/index read-only | S2 answer contract | fixture/schema review | Orchestrator | parallel after H1 starts |
| H4 | S6 hardening | spec/doc hardening | partial | S6 child spec copy | Parent/index read-only | S4/S5 outputs | state/report review | Orchestrator | after S4/S5 decisions |
| H5 | S7 hardening | spec/doc hardening | partial | S7 child spec copy | Parent/index read-only | S3-S6 contracts | harness matrix review | Orchestrator | late |
| I1 | S3 implementation | implementation | no | TBD after hardening | Parent/index read-only except integration owner | S3 `IMPLEMENTATION READY` | S3 Gate Verification | Integration owner | after H1 |

Parallel implementation verdict: **not safe yet**.

## Recommended Next Move

Next move: **Run `child-spec-hardening` on S3 in a focused session.**

Why:

1. Parent explicitly names S3 as next implementation step.
2. S3 has enough contract substance to become implementation-ready without major product invention.
3. S3 is prerequisite for later content, workbench, RAG/ROI, and harness integration.

## S3 Session-Start Handoff

- Target skill: `child-spec-hardening`
- Parent path: `tmp/docworkflow-comparison-ki-fuer-kmu/new/_specs/2026-05-04-free-entry-v2-master-spec.md`
- Child path: `tmp/docworkflow-comparison-ki-fuer-kmu/new/_specs/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md`
- Goal: Make S3 implementation-ready under the new workflow.
- Non-goals: No runtime code; no changes to original KI-fuer-KMU files; no product redesign; no S4-S7 hardening beyond dependency notes.
- OpenSpec mode: default for later delivery.
- Required hardening:
  - Add or patch Review Control Surface.
  - Set `Spec-Variante` and `Goldstandard Status`.
  - Add Parent Scope Conformance table for V2-FR-030/031/031a/031b/032.
  - Extract Decision Freeze Pack explicitly.
  - Add Dependencies and Write-Set.
  - Add Closeout Sync Targets.
  - Produce final readiness verdict.
- Stop conditions:
  - Parent contradiction.
  - Missing product/security/data-contract decision.
  - Verification commands cannot be made concrete without changing the target architecture.

## New Workflow Outcome

Strengths:

- Correctly refuses to implement from the Parent Spec as a whole.
- Makes S3 the next bounded child instead of a monolithic plan item.
- Separates accepted evidence (S1/S2) from active hardening (S3-S7).
- Produces a concrete next-session payload.
- Prevents duplicated `refine-plan`/OpenSpec/child-index task ledgers.

Weaknesses / Friction:

- Existing active child specs need targeted Review Control Surface and conformance patches before implementation.
- The child index is too thin for the new workflow; it should eventually carry readiness, dependencies, evidence links, and next-session handoffs.
- S0 status remains slightly awkward (`🔵 Implemented` but not `🟢 Accepted`).

## Final Verdict

`READY FOR CHILD-SPEC-HARDENING`

Not ready for runtime implementation until S3 hardening returns `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES`.

## Mini-Retro

- What was decided? New workflow treats the KI fuer KMU Master Spec as Parent/Child automatically.
- What changed? Temp orchestration result only.
- What remains open? S3 hardening, child index enrichment, S0 closeout decision.
- Which evidence/verification is missing? Actual S3 hardening edit run and later S3 verification commands.
- Which skill/workflow friction showed up? Existing child specs predate Review Control Surface, but this is targeted active-child hardening rather than broad migration.
- Session/context state: A fresh session is recommended for S3 implementation after hardening; current session can continue with hardening if desired.
