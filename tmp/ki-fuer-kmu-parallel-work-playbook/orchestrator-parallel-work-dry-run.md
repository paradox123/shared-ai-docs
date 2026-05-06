# KI fuer KMU Free Entry v2 - Orchestrator Parallel Work Dry Run

## Session Briefing

- Modus/Skill: `spec-orchestrator`
- Source of Truth: copied Free Entry v2 master spec, child-spec index, S0-S7 child specs, and slice plan in this temp folder
- Ziel: show how parent/child orchestration produces a Parallel Work Control Surface
- Nicht-Ziele: no runtime implementation, no production edits in `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`
- In Scope: readiness assessment, hardening queue, safe parallel lanes, trigger guidance
- Erwarteter Output: Delivery Orchestration Pack plus Parallel Work Control Surface
- Verification/Review: source inspection only; JSON/Markdown structure checked by review
- Offene Entscheidungen: none for the dry run

## Spec Orchestration Result

Parent:
- `_specs/2026-05-04-free-entry-v2-master-spec.md`

Child set:
- `_specs/2026-05-05-free-entry-v2-child-specs-index.md`
- `_specs/2026-05-05-free-entry-v2-s0-repo-freeze-legacy-quarantine-spec.md`
- `_specs/2026-05-05-free-entry-v2-s1-vertical-architecture-spike-spec.md`
- `_specs/2026-05-05-free-entry-v2-s2-survey-delivery-answer-handoff-spec.md`
- `_specs/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md`
- `_specs/2026-05-05-free-entry-v2-s4-provider-activation-guides-spec.md`
- `_specs/2026-05-05-free-entry-v2-s5-survey-v2-content-spec.md`
- `_specs/2026-05-05-free-entry-v2-s6-roi-rag-runtime-spec.md`
- `_specs/2026-05-05-free-entry-v2-s7-docker-safe-harness-spec.md`

Mode:
- Mode A: Orchestrate existing children
- Mode D: Parallelization plan, limited to hardening lanes until child readiness improves

## Parent/Child Inventory

| Child | Current Status | Orchestrator Reading |
|---|---|---|
| S0 Repo Freeze | `🔵 Implemented` | Already completed; not a parallel lane. |
| S1 Vertical Architecture Spike | `🟢 Accepted` | Accepted baseline and verification recipe for later slices. |
| S2 Survey Delivery / Answer Handoff | `🟢 Accepted` | Accepted baseline for survey artifacts, retention, Docker/local harness. |
| S3 Content Bundle / Managed-AI Channel | `🟡 Spec` | Deep contract exists; needs workflow-control cleanup before implementation. |
| S4 Provider Activation Guides | `🟡 Spec` | Thin child draft; needs hardening. |
| S5 Survey v2 Content | `🟡 Spec` | Thin child draft; needs hardening. |
| S6 ROI/RAG Runtime | `🟡 Spec` | Thin child draft and dependency-heavy; blocked until S3/S4/S5 are hardened/implemented enough. |
| S7 Docker/Safe Harness | `🟡 Spec` | Thin child draft; can be hardened in parallel as an integration harness plan, but implementation depends on S3-S6 contracts. |

## Coverage

- done: S0 freeze, S1 vertical spike, S2 survey delivery/handoff
- partial: starter/control flow, non-goals/security, artifact structure, run manifest, Docker harness, bundle/provider stubs
- pending: S3 content bundle, S4 provider guides, S5 survey content, S6 ROI/RAG, S7 full control-flow harness
- missing: no missing child destination found; pending parent scope has named S3-S7 destinations
- blocked: S6 implementation depends on S3/S4/S5 outputs and provider/readiness contracts

## Parent Scope Conformance

| Child | Parent Requirement Area | Conformance | Action |
|---|---|---|---|
| S3 | V2-FR-030/031/031a/031b/032, V2-FR-060/062, V2-NFR-001 | `extends` | Add Review Control Surface, Parent Scope Conformance table, and Dependencies/Write-Set control before implementation. |
| S4 | V2-FR-020/021/022/023/024/024a/053 | `preserves` as draft | Harden normative provider matrix, readiness contract, guide artifacts, visual source policy, and verification. |
| S5 | V2-FR-001/002/010/011/012/040 | `preserves` as draft | Harden survey catalog schema, routing cases, fixtures, local fallback, and server-rendering verification. |
| S6 | V2-FR-041/050/051/052/053/062 | `defers_to_child` via dependencies | Keep blocked until S3/S4/S5 contracts are stable enough to consume. |
| S7 | Docker harness, V2-FR-060/061/063, V2-NFR-001, leading flow paths | `extends` as harness target | Harden as cross-slice harness contract; implementation waits for sibling contracts. |

## Child Readiness

| Child | Status | Main Gap | Required Hardening |
|---|---|---|---|
| S3 | `ready_candidate` | Deep implementation contract exists, but current workflow gates are not fully present. | Add Review Control Surface, explicit Parent Scope Conformance, Dependencies/Write-Set, closeout sync targets, and final readiness verdict. |
| S4 | `needs_hardening` | Thin acceptance prose; missing normative contract and verification depth. | Provider matrix schema, guide artifact contract, readiness test cases, redaction cases, verification commands. |
| S5 | `needs_hardening` | Thin content spec; missing executable survey catalog contract. | Survey schema, A/B/C routing, KRITIS conditional cases, fixtures, server/local fallback verification. |
| S6 | `blocked` | Depends on S3 bundle/workbench, S4 provider readiness, and S5 survey content. | Defer until upstream contracts are stable; then harden ROI/RAG statuses, report contract, source status, LLM guardrails. |
| S7 | `needs_hardening` | Harness target exists, but case matrix and cross-slice artifact contracts are not explicit. | Cross-slice scenario matrix, exit-code/artifact assertions, secret-leak checks, integration replay commands. |

## Hardening Queue

| Child | Current Status | Required Hardening | Sources To Read | Blockers |
|---|---|---|---|---|
| S3 | `ready_candidate` | Workflow-control cleanup: Review Control Surface, parent conformance, write-set, closeout sync, final readiness verdict. | Master spec, S1/S2 accepted specs, S3 spec, slice plan. | None for spec hardening. |
| S4 | `needs_hardening` | Provider-guide normative contract, readiness cases, visual guide artifact policy, redaction verification. | Master provider sections, S2 answers contract, S1 provider stub evidence. | Needs current provider-guide source freshness policy before implementation. |
| S5 | `needs_hardening` | Survey catalog schema, routing fixtures, KRITIS conditional behavior, local/server rendering commands. | Master survey sections, S2 survey API/fixture contract, old survey source as non-normative input. | None for hardening; implementation depends on accepted fixture strategy. |
| S7 | `needs_hardening` | Cross-slice harness matrix and verification replay contract. | Master harness section, S1/S2 evidence, S3-S6 drafts. | Full implementation waits for S3-S6 contracts. |
| S6 | `blocked` | ROI/RAG runtime and report contract after upstream readiness. | Master ROI/RAG sections, S3/S4/S5 hardened specs. | Blocked until S3/S4/S5 are stable enough. |

## Parallel Work Control Surface

This is the first daily trigger point: the orchestrator may propose this table, but parallel work starts only after the user or session lead explicitly says to run these lanes.

### Safe Now: Parallel Child-Spec Hardening

| Child/Arbeitsblock | Modus | Owner/Agent | Erlaubte Write-Sets | Shared Files / Read-only Files | Abhaengigkeiten | Verification Commands | Integrations-Owner | Merge-/Sync-Reihenfolge |
|---|---|---|---|---|---|---|---|---|
| S3 readiness cleanup | `spec/doc hardening` | Agent A | `_specs/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md` only | Read-only: master spec, child index, slice plan, S1/S2 specs, OpenSpec S1/S2 evidence | S1/S2 accepted | `rg` for required workflow sections; markdown review; no runtime commands | Lead/Integrator | Merge first, because S3 is recommended next implementation slice. |
| S4 hardening | `spec/doc hardening` | Agent B | `_specs/2026-05-05-free-entry-v2-s4-provider-activation-guides-spec.md` only | Read-only: master spec, child index, slice plan, S2/S3 specs | S2 answer contract; S3 provider-guide content-set awareness | `rg` for Review Control Surface, provider status values, redaction cases, verification commands | Lead/Integrator | Merge after S3 cleanup or independently if no S3 dependency text changed. |
| S5 hardening | `spec/doc hardening` | Agent C | `_specs/2026-05-05-free-entry-v2-s5-survey-v2-content-spec.md` only | Read-only: master spec, child index, slice plan, S2 spec, old survey source | S2 survey definition/API contract | `rg` for Review Control Surface, fixture paths, routing cases, verification commands | Lead/Integrator | Merge after S3 cleanup; independent of S4 unless shared survey/provider copy is introduced. |
| S7 harness hardening plan | `spec/doc hardening` | Agent D | `_specs/2026-05-05-free-entry-v2-s7-docker-safe-harness-spec.md` only | Read-only: master spec, child index, slice plan, S1/S2 accepted specs, S3/S4/S5 drafts | S1/S2 accepted; S3-S5 draft contracts | `rg` for case matrix, exit codes, secret assertions, cross-slice replay commands | Lead/Integrator | Merge last among hardening lanes, because it references sibling contracts. |

### Not Safe Yet: Parallel Implementation

| Child/Arbeitsblock | Safe? | Reason | Required Serial Prerequisite |
|---|---|---|---|
| S3 implementation | Not yet | S3 is close, but missing the current workflow-control gates and final readiness verdict. | Run S3 readiness cleanup via `child-spec-hardening` or equivalent doc-review/autoresolve first. |
| S4 implementation | No | Spec is too thin for implementation: missing normative guide/readiness/verification contract. | Harden S4. |
| S5 implementation | No | Spec is too thin for implementation: missing executable survey catalog and fixture contract. | Harden S5. |
| S6 implementation | No | Depends on S3/S4/S5. | Implement or at least stabilize upstream contracts. |
| S7 implementation | No | S7 is an integration harness; implementation depends on stable S3-S6 case contracts. | Harden S7 after S3-S5 hardening, then implement integration harness serially or as lead-owned integration lane. |

## Recommended Execution Order

1. Trigger `spec-orchestrator` on the parent/child set.
2. Accept or edit the Parallel Work Control Surface.
3. Trigger parallel `child-spec-hardening` for S3, S4, S5, and S7 as separate lanes.
4. Integrator merges hardening results in this order: S3, S4, S5, S7.
5. Trigger `spec-change-delivery` for S3 only after S3 is `IMPLEMENTATION READY`.
6. After S3 implementation, update parent coverage/index/slice plan through the integration owner.
7. Continue with S4/S5 implementation only when their hardened specs are implementation-ready.
8. Keep S6 and S7 implementation serial/integration-led until their dependencies are stable.

## Daily Trigger Map

| User Intent | Natural Prompt | Skill Triggered | Expected Output |
|---|---|---|---|
| Find next work and possible parallel lanes | "Orchestriere die Parent/Child Specs und zeig, was parallel gehen kann." | `spec-orchestrator` | Coverage/readiness, hardening queue, Parallel Work Control Surface. |
| Start parallel spec hardening | "Starte die Hardening-Lanes aus der Parallel Work Control Surface." | `child-spec-hardening` per lane | One child spec hardened per lane, respecting write-sets. |
| Implement one ready lane | "Implementiere S3 aus dem Scope Contract, nur diese Lane." | `spec-change-delivery` | One bounded implementation plus verification. |
| Integrate completed lanes | "Führe die Lanes zusammen und aktualisiere Parent/Index/Slice-Plan." | integration-owner run, usually `spec-orchestrator` or `spec-closeout` depending on status | Parent coverage, index, backlog, verification replay, final verdict. |
| Close accepted change | "S3 ist akzeptiert, mach Closeout." | `spec-closeout` | Verification replay, docs sync, status accepted. |

## Files To Update If This Were Real

For this dry run, no source files outside the temp folder are changed.

If this were the real KI-fuer-KMU workflow, the integration owner would eventually update:
- `_specs/2026-05-04-free-entry-v2-master-spec.md`
- `_specs/2026-05-05-free-entry-v2-child-specs-index.md`
- `v2/docs/FREE-ENTRY-V2-SLICE-PLAN.md`
- the specific child spec touched by each lane
- OpenSpec artifacts only when an implementation lane enters `spec-change-delivery`

## Mini-Retro

- What was decided? Parallel hardening is safe now for S3/S4/S5/S7 with disjoint spec write-sets; parallel implementation is not safe yet.
- What changed? Temp-folder copies and this orchestration dry-run were created.
- What remains open? S3 needs workflow-control cleanup; S4/S5/S7 need hardening; S6 remains blocked.
- Which evidence/verification is missing? No runtime verification was run; this was source inspection only.
- Which skill/workflow friction showed up? The daily trigger should be explicit: orchestrator may recommend parallel work, but the user/session lead starts it.
- Session/context state: continue here if we want to simulate one hardening lane; start a new session before real parallel implementation.
