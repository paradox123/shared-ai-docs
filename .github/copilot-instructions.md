# Copilot Instructions (shared-ai-docs)

## QMD Retrieval Preference

When working in this repository and the task is to search markdown docs/specs/notes:
1. Prefer `qmd` if available (`qmd status` succeeds).
2. If `qmd` is unavailable, use `rg` fallback and state that ranking is lexical fallback.

Fallback sequence:
- `rg --files` to scope candidates
- `rg -n "<query terms>"` for targeted lookup
- summarize results with file+line references

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
