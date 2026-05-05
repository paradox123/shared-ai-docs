## Context

SpecOps already has:

1. an accepted `historical-001` slice,
2. a source inventory at `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md`,
3. a coverage dashboard at `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/backfill-coverage.md`,
4. 10 current spec entities and 3 document entities.

The remaining work spans narrative specs, completed narrative specs, OpenSpec canonical specs, OpenSpec change artefacts and document-like sources. A single uncontrolled import would create duplicates and low-confidence metadata. A long sequence of tiny Child-Specs would preserve control but add too much process overhead.

## Goals / Non-Goals

**Goals:**

- Use one OpenSpec control change as the workstream for remaining full historical backfill.
- Convert the accepted inventory into phased source groups with measurable acceptance gates.
- Keep narrative specs, documents and OpenSpec evidence distinct.
- Make duplicate prevention and metadata-quality signaling explicit.
- Allow future delivery runs to operate from Scope Contracts without creating a new Child-Spec per batch.

**Non-Goals:**

- No direct entity import in this change.
- No metadata reconstruction automation.
- No edits to historical source documents.
- No environment/release/learning model decisions.
- No NCG backend runtime/build validation.

## Decisions

1. **Control change over repeated Child-Specs**
   - Decision: Use this OpenSpec change as the ongoing execution frame for the remaining full backfill.
   - Alternative: Create one Child-Spec per 5-20 imported sources.
   - Rationale: The inventory already supplies the stable requirements baseline; OpenSpec tasks and evidence are a better fit for repeated execution.

2. **`historical-001` is immutable baseline**
   - Decision: Future tasks must detect and skip already-imported `historical-001` entities.
   - Alternative: Re-open and expand the accepted slice.
   - Rationale: The accepted slice has a clean closeout boundary and should remain auditable.

3. **Narrative source first, OpenSpec artefacts second**
   - Decision: Narrative and completed narrative specs may become primary `type: spec` entities; OpenSpec artefacts are related/canonical/evidence links unless explicitly promoted later.
   - Alternative: Import every OpenSpec file as a spec entity.
   - Rationale: OpenSpec artefacts are often derived plans/evidence and would otherwise duplicate user-authored specs.

4. **Documents stay documents**
   - Decision: ADRs, guides, runbooks and comparable knowledge artefacts become `type: document` unless they are themselves specs.
   - Alternative: Treat all backfilled Markdown as specs.
   - Rationale: SpecOps needs accurate entity semantics for dashboards and future workflow integration.

5. **Future execution by Scope Contract**
   - Decision: Each future delivery run chooses one bounded phase/task subset and records evidence in `implementation-evidence.md`.
   - Alternative: Leave tasks vague and batch ad hoc.
   - Rationale: Scope discipline remains visible without multiplying Child-Specs.

## Phases

| Phase | Source group | Expected count | Intended treatment |
|---|---:|---:|---|
| 0 | `historical-001` accepted baseline | 5 imported batch entities | Done; never re-import. |
| 1 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed/` | included in 42 shared specs | Primary `type: spec` candidates, with completed-path inference allowed. |
| 2 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/` active specs | included in 42 shared specs | Primary `type: spec` candidates, status from header/source context. |
| 3 | `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/` | 19 | Primary `type: spec` candidates; dedicated repository paths stay local. |
| 4 | `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/` | 29 | Primary `type: spec` candidates, likely separate NCG delivery runs. |
| 5 | `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/` and `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/openspec/` | 27 | Link as canonical/evidence relationships unless no narrative source exists. |
| 6 | `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/openspec/` | 87 | Link/dedupe against narrative Nebenkosten specs before entity creation. |
| 7 | `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_legacy/v1-node-prototype/openspec/` | 35 | Legacy evidence/relationship mapping; low priority. |
| 8 | Historical documents discovered during phases | variable | `type: document`, not `type: spec`, unless the source is actually a spec. |

## Risks / Trade-offs

- [Risk] The OpenSpec task list becomes too broad. -> Mitigation: future runs must select a bounded subset via Scope Contract and update evidence incrementally.
- [Risk] Narrative specs and OpenSpec change artefacts describe the same work. -> Mitigation: narrative source wins as primary entity; OpenSpec is linked as canonical/evidence.
- [Risk] Metadata looks more certain than it is. -> Mitigation: require `metadata_quality` and allow `inferred`, `missing` and `conflict`.
- [Risk] Private source paths leak outside the local vault. -> Mitigation: this is a local-only Obsidian control plane; no external sync in scope.

## Migration Plan

1. Create this OpenSpec control change.
2. Validate Control Spec verification commands and OpenSpec artefacts.
3. Future delivery runs select one phase/subset with a Scope Contract.
4. Each run creates/updates entities, updates coverage, and appends concrete evidence.
5. OpenSpec archive happens only when the remaining full backfill is accepted as complete.

## Open Questions

None blocking for the control change. Future delivery runs may surface source-specific classification questions and must record them as task evidence or backlog items.
