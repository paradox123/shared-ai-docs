# DocWorkflow Dry Run: KI fuer KMU Free Entry v2 Parent Spec

## Session Briefing

- Modus/Skill: Spec Sizing Gate -> spec-orchestrator dry run -> child-spec-hardening readiness assessment.
- Source of Truth: `_specs/2026-05-04-free-entry-v2-master-spec.md`, `_specs/2026-05-05-free-entry-v2-child-specs-index.md`, copied S0-S7 child specs.
- Ziel: Testen, ob der aktualisierte DocWorkflow eine grosse Parent Spec automatisch in Child-Steuerung, Hardening Queue und naechste Session-Handoffs ueberfuehrt.
- Nicht-Ziele: Keine Originaldateien aendern, keine Runtime-Implementierung, keine produktbezogene Neubewertung des Free-Entry-Konzepts.
- Erwarteter Output: Orchestration Pack, Child Readiness, Hardening Queue, naechster Child-Handoff, Workflow-Reibung.

## Sizing Gate Result

Verdict: **TRIGGERS PARENT/CHILD**

Gruende:

1. Parent Spec hat 710 Zeilen und deckt viele Domains ab: UX, Survey, Provider, Bundle/Content, Vault/Workbench, RAG/ROI, Report, Security, Docker-Harness.
2. Child-Set umfasst S0-S7 mit insgesamt 2496 Zeilen Testmaterial.
3. Es gibt mehrere getrennte Verification-Zyklen: .NET Build/Test, lokale Harness, Docker-Harness, Survey-Service, Bundle/Manifest, Provider-Readiness, RAG/ROI, End-to-End-Harness.
4. Es existieren natuerliche Delivery-Slices mit eigenen Done-Signalen.
5. Kontextkomprimierung waere bei Umsetzung gegen die Parent Spec als Ganzes sehr wahrscheinlich; eine neue Session pro implementation-ready Child ist sinnvoll.

Workflow-Routing: Parent/Child bleibt fuehrend. OpenSpec ist als Default-Ledger plausibel, weil S1/S2 bereits OpenSpec-/Evidence-nahe Historie haben und das Vorhaben mehrstufig ist.

## Parent/Child Inventory

Parent:

- `_specs/2026-05-04-free-entry-v2-master-spec.md`
- Status: `🟠 Plan`
- Rolle: Parent/Master Spec, fachliches Zielbild und Kontrollschicht.

Child Index:

- `_specs/2026-05-05-free-entry-v2-child-specs-index.md`
- Statusmodell vorhanden, aber noch kein neuer Workflow-Index mit Readiness, Dependencies, Write-Sets, Evidence Links, Next Session Handoffs.

Children:

| Child | Current Status | Dry-Run Readiness | Main Reason |
|---|---|---|---|
| S0 Repo Freeze | `🔵 Implemented` | `NEEDS CLOSEOUT DECISION` | Implemented, aber nicht accepted; neuer Workflow wuerde klaeren, ob formal accepted oder historische Evidence ausreichend ist. |
| S1 Vertical Spike | `🟢 Accepted` | `REFERENCE_DONE / NO BACKFILL` | Akzeptiert; keine nachtraegliche Migration erforderlich. |
| S2 Survey Handoff | `🟢 Accepted` | `REFERENCE_DONE / NO BACKFILL` | Akzeptiert; keine nachtraegliche Migration erforderlich. |
| S3 Content Bundle | `🟡 Spec` | `READY_CANDIDATE -> NEEDS HARDENING` | Stark gehardet, aber nach neuem Standard fehlen Review Control Surface, Goldstandard Status, expliziter Parent Scope Conformance Table, Dependencies/Write-Set und Session-Handoff. |
| S4 Provider Guides | `🟡 Spec` | `NEEDS HARDENING` | Gute Skeleton-Spec, aber keine Umsetzungstiefe, keine Verification Commands, keine DoR/DoD, keine Parent Conformance. |
| S5 Survey Content | `🟡 Spec` | `NEEDS HARDENING` | Gute Skeleton-Spec, aber Survey-Definition-/Fixture-/Rendering-Vertrag fehlt. |
| S6 ROI/RAG Runtime | `🟡 Spec` | `NEEDS HARDENING` | Gute Skeleton-Spec, aber Agent-/Report-/RAG-Statusvertrag und Verification fehlen. |
| S7 Docker Safe Harness | `🟡 Spec` | `NEEDS HARDENING` | Gute Skeleton-Spec, aber Harness-Case-Matrix und command-level Gate fehlen. |

## Coverage Snapshot

| Parent Area | Coverage |
|---|---|
| Repo Freeze / Legacy Quarantine | covered by S0, needs closeout decision if formal acceptance matters |
| Architecture Spike / Runtime skeleton | accepted by S1 |
| Survey delivery / answer handoff | accepted by S2 |
| Bundle / Manifest / Managed-AI channel | strong S3 ready candidate, hardening hygiene remains |
| Provider activation / readiness | S4 skeleton, needs hardening |
| Survey v2 content | S5 skeleton, needs hardening |
| ROI/RAG/report | S6 skeleton, needs hardening |
| Full Docker/Safe Harness | S7 skeleton, needs hardening |

Missing coverage found: none at slice level. The parent scope is not falling through; the gaps are depth/readiness gaps in active children.

## Hardening Queue

| Child | Current Status | Required Hardening | Sources To Read | Blockers |
|---|---|---|---|---|
| S3 | ready_candidate | Add Review Control Surface, Goldstandard Status, Parent Scope Conformance, explicit Decision Freeze Pack, Dependencies/Write-Set, Closeout Sync Targets, session-start handoff. Re-review against parent. | Parent V2-FR-030/031/031a/031b/032, S1/S2 verification style, ADR-001. | No product blocker seen; mostly workflow-hygiene and conformance hardening. |
| S4 | needs_hardening | Provider matrix contract, guide freshness contract, official-link/screenshot policy, readiness test cases, redaction cases, verification commands, write-set. | Parent V2-FR-020-024a/053, S2 handoff, provider docs if current links are needed. | Current provider screens/official links may need source verification. |
| S5 | needs_hardening | Survey schema/fixture contract, A/B/C parity matrix, conditional KRITIS routing cases, local/server rendering verification, question identity/versioning. | Parent V2-FR-001/002/010/011/012/040, S2 answer contract, survey-v1 source. | May require product decision on final survey wording. |
| S6 | needs_hardening | RAG status state machine, ROI assumptions/report contract, blocked/prep report cases, LLM-readiness guard, source/redaction cases, verification commands. | Parent V2-FR-041/050/051/052/053/062, S2 answers, S4 readiness. | Depends on S4/S5 artifacts and possibly S3 workbench layout. |
| S7 | needs_hardening | Full harness case matrix across leading paths, exit-code mapping, secret-leak assertions, Docker/Compose command contract, cross-slice replay. | Parent Harness section, S1/S2/S3 commands, active child DoD. | Should wait until S3-S6 contracts stabilize; can harden doc in parallel but implementation should be late. |

## Parallel Work Control Surface

| Lane | Child/Work Block | Mode | Safe? | Allowed Write-Sets | Shared Files / Read-only Files | Dependencies | Integration Owner | Merge/Sync Order |
|---|---|---|---|---|---|---|---|---|
| H1 | S3 hardening | spec/doc hardening | yes | S3 child spec copy, S3 hardening notes | Parent, index read-only | S1/S2 accepted patterns | Orchestrator | first |
| H2 | S4/S5 hardening | spec/doc hardening | yes, if split by file | S4 or S5 child spec copy | Parent, index read-only | S5 informs S4 copy only lightly | Orchestrator | after S3 or parallel with clear owners |
| H3 | S6 hardening | spec/doc hardening | partial | S6 child spec copy | Parent, index read-only | S4/S5 readiness details | Orchestrator | after S4/S5 contract decisions |
| H4 | S7 hardening | spec/doc hardening | partial | S7 child spec copy | Parent, index read-only | S3-S6 contracts | Orchestrator | late, or skeleton matrix now with placeholders |
| I1 | S3 implementation | implementation | not yet | runtime/code write-set TBD | Parent/index read-only except integration owner | S3 hardening complete | Integration owner | after S3 `IMPLEMENTATION READY` |

Parallel implementation verdict: **not safe yet**. Parallel spec/doc hardening is safe for independent child files if Parent/Index are read-only and one integration owner syncs.

## Recommended Next Slice

Next: **S3 child-spec-hardening**, not implementation yet.

Why:

1. Parent already names S3 as next implementation step.
2. S3 has the deepest active child content and likely only needs workflow-hardening rather than product redesign.
3. S3 is a prerequisite for later Workbench/Vault, Provider/Content, RAG/ROI and Harness paths.

## Session-Start Handoff For S3 Hardening

- Parent path: `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md`
- Child path: `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md`
- Mode: `child-spec-hardening`
- Goal: Make S3 implementation-ready under the new workflow without changing product intent.
- Non-goals: No runtime code, no new product decisions, no broad changes to S4-S7.
- Required fixes: Review Control Surface, Parent Scope Conformance, Decision Freeze Pack, Dependencies/Write-Set, Closeout Sync Targets, final readiness verdict.
- OpenSpec/direct mode: OpenSpec default recommended for later delivery.
- Fresh session recommended: yes for implementation; hardening can happen in current session if context remains stable.

## Dry-Run Verdict

The updated workflow is **substantially implementable** and catches the right thing:

- It identifies the Master Spec as too large.
- It preserves Parent/Child instead of flattening into one plan.
- It routes to orchestrator/hardening before implementation.
- It prevents S3 implementation until the new handoff/control surfaces exist.
- It treats accepted S1/S2 as evidence/reference instead of forcing backfill.

Main friction found:

1. OpenSpec default wording needs one more canonical clarification so "optional/user-decided" and "default for Parent/Child" do not read as contradictory.
2. `refine-plan` still has a local Scope Pressure Guardrail that can create split-plan behavior outside the new Sizing Gate unless it explicitly routes back to Parent/Child.
3. `spec-closeout` output still says "Documentation updates performed" generically; for child closeout it should say "Parent/Index/OpenSpec sync plus broad docs sync if triggered".
4. Existing active child specs without Review Control Surface become `needs_hardening`; that is correct, but the workflow should label this as targeted active-child hardening, not legacy migration.

## Mini-Retro

- Was wurde entschieden? KI-fuer-KMU Free Entry v2 ist ein validierender Parent/Child-Testfall fuer das neue Sizing Gate.
- Was wurde geaendert? Temp copies and this dry-run result only.
- Was bleibt offen? Whether to patch the three workflow frictions found above.
- Welche Evidenz/Verification fehlt? A real `child-spec-hardening` edit run for S3, then a fresh-session implementation rehearsal.
- Welche Skill-/Workflow-Reibung ist aufgefallen? OpenSpec-default wording, refine-plan split overlap, child-closeout output wording.
- Session-/Kontextzustand: Good to continue with targeted workflow cleanup or S3 hardening dry-run.
