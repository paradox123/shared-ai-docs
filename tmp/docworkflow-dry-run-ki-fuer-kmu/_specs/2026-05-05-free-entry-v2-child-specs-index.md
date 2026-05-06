# Free Entry v2 Child Specs - Operational Child Index

Diese Temp-Datei operationalisiert den vorherigen Slice-Index fuer den DocWorkflow-Dry-Run vom 2026-05-06. Sie ist eine Temp-Kopie und aendert keine originalen KI-fuer-KMU-Specs.

Fuehrend bleiben:

1. `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md`
2. `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-child-specs-index.md`
3. Child specs unter `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/`
4. Persistierte Child Session Handoffs unter `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/child-session-handoffs/`

## Operational Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 Repo Freeze | [2026-05-05-free-entry-v2-s0-repo-freeze-legacy-quarantine-spec.md](2026-05-05-free-entry-v2-s0-repo-freeze-legacy-quarantine-spec.md) | Legacy quarantine / repo freeze. | `🔵 Implemented`; closeout decision still unclear in this temp run. | `not_created; historical closeout decision pending` | Historical/direct or prior evidence TBD. | None for active next slice. | None unless closeout sync is explicitly opened. | Evidence review only. | Implemented status visible; accepted closeout not established in this temp run. | None visible. | Decide whether to close/accept or leave as historical implemented. |
| S1 Vertical Spike | [2026-05-05-free-entry-v2-s1-vertical-architecture-spike-spec.md](2026-05-05-free-entry-v2-s1-vertical-architecture-spike-spec.md) | Runtime skeleton, harness baseline, survey stub, bundle dummy. | `REFERENCE_DONE / NO BACKFILL`. | `not_required; accepted historical reference` | Archived OpenSpec noted in spec history. | None. | No edits unless explicit reference lift. | Accepted verification replay recorded in spec. | Accepted, archive noted. | S2-S7 follow-ups already named. | Use as verification recipe; do not migrate. |
| S2 Survey Handoff | [2026-05-05-free-entry-v2-s2-survey-delivery-answer-handoff-spec.md](2026-05-05-free-entry-v2-s2-survey-delivery-answer-handoff-spec.md) | Survey delivery, answer artifact, import/retention. | `REFERENCE_DONE / NO BACKFILL`. | `not_required; accepted historical reference` | Archived OpenSpec noted in closeout evidence. | S1 baseline. | No edits unless explicit reference lift. | Accepted verification replay recorded in spec. | Accepted, archive path noted. | Later survey content in S5. | Use as verification recipe; do not migrate. |
| S3 Content Bundle | [2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md](2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md) | Bundle/manifest/readiness/workbench/plugin baseline for V2-FR-030/031/031a/031b/032. | `NEEDS HARDENING`; index sync and handoff now exist, but no strict Hardening Verdict exists in the S3 spec. | [child-session-handoffs/s3-session-handoff.md](child-session-handoffs/s3-session-handoff.md) | OpenSpec default for later delivery; no active S3 change in this temp run. | S1/S2 accepted verification patterns. | During hardening: S3 child spec and S3 handoff; parent/index only by integration owner. During implementation: not allowed yet. | Markdown/section scan and content-quality review only until hardening verdict exists; runtime commands are not allowed yet. | None yet. | S4/S6/S7 consume S3 outputs; remaining provider/runtime/report scope stays in named children. | Run `child-spec-hardening` for S3; do not implement. |
| S4 Provider Guides | [2026-05-05-free-entry-v2-s4-provider-activation-guides-spec.md](2026-05-05-free-entry-v2-s4-provider-activation-guides-spec.md) | Provider activation, guides, readiness policy. | `NEEDS HARDENING`. | `pending; create when S4 becomes leading` | OpenSpec default later. | S2 answers, S3 provider-guide content set. | S4 child spec only during hardening. | None yet. | None yet. | Current provider-source freshness may be needed. | Harden after S3 or as a separate spec/doc lane if integration owner holds index sync. |
| S5 Survey Content | [2026-05-05-free-entry-v2-s5-survey-v2-content-spec.md](2026-05-05-free-entry-v2-s5-survey-v2-content-spec.md) | Survey variants, routing, content catalog. | `NEEDS HARDENING`. | `pending; create when S5 becomes leading` | OpenSpec default later. | S2 answer/API contract. | S5 child spec only during hardening. | None yet. | None yet. | Final wording may require product decision. | Harden survey schema/fixtures. |
| S6 ROI/RAG Runtime | [2026-05-05-free-entry-v2-s6-roi-rag-runtime-spec.md](2026-05-05-free-entry-v2-s6-roi-rag-runtime-spec.md) | ROI/RAG/report runtime. | `BLOCKED / NEEDS HARDENING LATER`. | `blocked; create after upstream contracts stabilize` | OpenSpec default later. | S3/S4/S5 stable contracts. | S6 child spec only during hardening. | None yet. | None yet. | Waits for upstream outputs. | Keep blocked until S3/S4/S5 stabilize. |
| S7 Docker Safe Harness | [2026-05-05-free-entry-v2-s7-docker-safe-harness-spec.md](2026-05-05-free-entry-v2-s7-docker-safe-harness-spec.md) | Full harness/cross-slice replay. | `NEEDS HARDENING`. | `pending; create when S7 becomes leading` | OpenSpec default later. | S1/S2 evidence and S3-S6 contracts. | S7 child spec only during hardening. | None yet. | None yet. | Implementation waits for S3-S6. | Harden harness matrix late or as doc-only skeleton now. |

## Hardening Queue

| Child | Current Status | Required Hardening | Sources To Read | Blockers | Next Handoff Target |
|---|---|---|---|---|---|
| S3 | `NEEDS HARDENING` | Add or verify Review Control Surface, Parent Scope Conformance, Decision Freeze Pack, Dependencies/Write-Set, Closeout Sync Targets, strict Hardening Verdict, and implementation-run handoff freshness. | Parent V2-FR-030/031/031a/031b/032, S1/S2 accepted patterns, S3 spec, S3 handoff. | No product blocker seen; strict verdict and Child Index/Spec/Handoff agreement still missing. | `child-spec-hardening` for S3 using [child-session-handoffs/s3-session-handoff.md](child-session-handoffs/s3-session-handoff.md). |
| S4 | `NEEDS HARDENING` | Provider matrix contract, guide freshness contract, visual/source policy, readiness cases, redaction cases, verification commands, write-set. | Parent V2-FR-020-024a/053, S2 answer contract, S3 provider-guide content set once stable. | Provider source freshness may require current-source verification before implementation. | Create S4 handoff when S4 becomes leading. |
| S5 | `NEEDS HARDENING` | Survey schema/fixture contract, A/B/C parity matrix, KRITIS routing cases, local/server rendering verification, question identity/versioning. | Parent V2-FR-001/002/010/011/012/040, S2 answer contract, old survey source as non-normative input. | Final wording may require user/product decision. | Create S5 handoff when S5 becomes leading. |
| S7 | `NEEDS HARDENING` | Cross-slice harness case matrix, exit-code mapping, secret-leak assertions, Docker/Compose command contract, replay strategy. | Parent harness section, S1/S2 evidence, S3-S6 drafts. | Full implementation waits for S3-S6 contracts. | Create S7 handoff when S7 becomes leading. |
| S6 | `BLOCKED` | ROI/RAG status machine, report contract, blocked/prep report cases, source/redaction cases, verification commands. | Parent V2-FR-041/050/051/052/053/062, S3/S4/S5 hardened specs. | Blocked until S3/S4/S5 are stable enough. | Create S6 handoff after upstream stabilization. |

## Slice-Regeln

- Keine Child Spec darf Anforderungen aus der Master-Spec still streichen.
- Jede Child Spec muss ihre Master-Spec-Abdeckung nennen.
- ADR-Entscheidungen werden nicht in Child Specs neu verhandelt.
- Alte Specs und `_legacy/v1-node-prototype` duerfen nur als historische Detailquellen genutzt werden.
- Wenn eine Child Spec einen Exit-Code verwendet, muss sie auf die fuehrende Exit-Code-Liste in der Master-Spec verweisen.
- `ready_candidate` ist keine Implementierungsfreigabe.
- `spec-change-delivery` darf fuer einen Child erst starten, wenn der Child ein dokumentiertes `IMPLEMENTATION READY` oder explizit akzeptiertes `READY WITH NON-BLOCKING NOTES` hat, der Child Index denselben Verdict spiegelt und der `Session Handoff`-Pointer aktuell ist.
