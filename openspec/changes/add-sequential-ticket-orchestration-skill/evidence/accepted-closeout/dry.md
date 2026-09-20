# DRY review receipt

- Date: 2026-09-20.
- Reviewer: independent fresh-context agent `/root/migration_dry`.
- Candidate: `0fb7150329f2e1321d1bd934ca4284c1e19804dc95d61ddd7baa8f1f201e4ed1` from [candidate.json](candidate.json).
- Result: **clean**. No actionable binding-rule violations or DRY heuristic findings. No source repairs requested or performed.

## Pinned bases and scope

| Repository | Pinned base |
| --- | --- |
| shared-ai-docs | `d6898ead386a36f2439b09326c25418f9578c695` |
| NCG backend | `6a6444baad35cbc2a882f81b45568778bd5ebefb` |
| probare-crm | `22d8e1a64eb8ca2a7fc94ace8f171b47d4114570` |
| ki-fuer-kmu | `dcbcc184544e141e26cc2d01fcf5eea619cb4b02` |

Reviewed the supplied scoped diff and relevant surrounding/current contents for the 37-file manifest. The NCG project-parent AGENTS.md is outside its Git root; its complete current content is covered by the manifest hash, not represented as having a separate Git baseline. Independently recomputed SHA-256 for all 37 files: zero mismatches. The three adopted skill directories were also compared with their preserved vendor originals where needed to distinguish changes from historical content.

Excluded the unrelated dirty paths listed in the candidate. Reports, fixture applications and historical review receipts served as evidence, not as another production implementation. Delivery target changes or later integration contents are not certified by this receipt without an explicit correspondence/delta check.

## Assigned coverage

Read the active canonical code-review skill and its review-criteria reference, [requirements.md](requirements.md), both relevant OpenSpec delta specs and the migration/design documents. Applied only the assigned DRY dimension and standards:

| Property | Observed result |
| --- | --- |
| Single executable owner of review policy | `code-review` and its own references define the review sequence, criteria, follow-up and receipt schema. `change-accepted` references that owner; requirements verification has its own linked owner. No competing active review recipe found in the scoped callers. |
| Caller, adapter and template duplication | Inspected implement, ask-matt, orchestrator and its message/context/state/delivery references, shared/project AGENTS, write-agents-md, both archive adapters and KI closeout/issue entrypoints. Their shared completion paragraphs are invocation/delegation references; local operational duties remain local. They do not copy the three-pass methodology. |
| Shared helper knowledge and logic | Manifest/verify/retain use the same artifact-path and digest logic; retain reuses verify for source, staging and destination. Checkpoint validates ledger semantics through one validator. The existing task-candidate helper has a distinct read-only identity-recovery contract. No repeated domain decision warrants a new abstraction. |
| Test duplication | Public CLI tests share document/snapshot/process setup where meaning agrees. Repeated evidence setup and explicit expected statuses support distinct observable cases; consolidating them further has no demonstrated maintenance benefit. |
| Requirements, history and provenance | OpenSpec requirements and ADR/design explanations document the contract; preserved vendor files document provenance. They are not treated as competing executable owners. |

## Evidence reuse and limits

Inspected the requirement-level expected/observed verification and its stated limits, plus [checks.json](checks.json): 21 public CLI tests, strict OpenSpec validation and whitespace checks passed. Did not rerun unchanged suites. This receipt certifies only DRY coverage for the pinned candidate; it neither supplies SOLID/KISS results nor declares full technical completion or delivery authority.
