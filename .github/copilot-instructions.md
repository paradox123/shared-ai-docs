# Copilot Instructions (shared-ai-docs)

## DanielsVault Documentation Retrieval

For DanielsVault documentation searches, follow [the central documentation research flow](../skills-repo/skills/rag-documentation-research/SKILL.md) and use QMD with task-relevant original-source collections as the standard retrieval entry. Verify findings against the original files and follow repository instructions and primary requirements. Optionally include curated `contextual-wiki-common` notes; check their direct source state before relying on them and read relevant current originals. Explicit wiki maintenance uses [maintain-llm-wiki](../skills-repo/skills/maintain-llm-wiki/SKILL.md); ordinary research does not save or maintain pages. WikiQuery is retired. Already named primary files may be read directly; `private` is a subject domain.

## Spec Review Auto-Resolve

For spec/doc review findings:
1. Collect findings with file/line references.
2. Auto-fix safe consistency issues immediately.
3. Re-review in the same run.
4. Escalate only true decision blockers (`[MISSING]`, `[DECISION]`, blocking `[REVIEW]`).

## Gate Authority

For DanielsVault RAG specs:
- treat child specs `01..05` as normative gate source.
- do not treat `source_precision` as a Phase-1 blocking metric unless child spec 04 explicitly changes that rule.
