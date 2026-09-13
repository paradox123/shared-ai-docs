# Copilot Instructions (shared-ai-docs)

## WikiQuery Context Entry

For knowledge-context searches, follow [the central WikiQuery research flow](../skills-repo/skills/rag-documentation-research/SKILL.md). Start with the common wiki, pass explicit task/source limits, inspect freshness and follow original-source references. QMD remains internal and available for index operations/diagnostics. Report unavailable WikiQuery instead of silently bypassing it. Already named primary files may be read directly; `private` is a subject domain.

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
