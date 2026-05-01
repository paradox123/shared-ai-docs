---
name: rag-documentation-research
description: RAG-first documentation research for DanielsVault. USE WHEN users ask to find, research, or narrow documentation sources before planning or implementation. MUST trigger on phrases like "durchsuche die dokumentation", "durchsuche docs", "research the documentation", "search the documentation", "find relevant docs", "welche dokumente sind relevant", and for `research-for-review` or `spec-closeout` source discovery. Prefer `rag` as default runtime and use `qmd` only as optional discovery add-on.
compatibility: Requires local `rag` runtime at /Users/dh/Documents/DanielsVault/_shared/danielsvault-rag; optional `qmd` add-on.
---

# RAG Documentation Research

Use this skill whenever documentation retrieval is the first bottleneck.

## Operating Rule

1. `rag` is the default retrieval path.
2. `qmd` is optional for broader discovery.
3. Source-backed output is mandatory.

## Trigger Phrases

Trigger immediately when users say or imply:

1. "durchsuche die dokumentation"
2. "durchsuche docs"
3. "research the documentation"
4. "search the documentation"
5. "find relevant docs"
6. "welche dokumente sind relevant"
7. "welche quellen sind relevant"

Also trigger for source discovery before:

1. `research-for-review`
2. `spec-closeout`

## Preflight

```bash
cd /Users/dh/Documents/DanielsVault/_shared/danielsvault-rag
export PATH="$PWD/.venv/bin:$PATH"
command -v rag
rag --version
rag runtime health
```

Default scope:

1. Start with `ncg/ncg-docs`.
2. Add broader scope only if the question requires it.
3. For workflow/skill/prompt governance questions (for example `doc-workflow`, `spec-change-delivery`, `spec-closeout`, `skills-repo`, `_prompts`), run with `--scope all` directly.

## Retrieval Flow

1. Run semantic retrieval for document questions.
2. Run structured retrieval for exact fact/setting/id questions.
3. Run workflow commands for delivery-oriented source sets.
4. Use `qmd` only when discovery looks too narrow or wording is too fuzzy.
5. When using `--scope all`, filter/de-prioritize generated artifact paths (for example `/.rag/`, `/.git/`, `/node_modules/`) in the final source shortlist.

Recommended commands:

```bash
rag retrieve semantic --scope ncg/ncg-docs --query "<question>" --top-k 5 --format json
rag retrieve structured --scope ncg/ncg-docs --record-type ci_setting_fact --filter "<filter>"
rag workflow research-for-review --scope ncg/ncg-docs --query "<question>" --top-k 5 --format json
rag workflow spec-closeout --scope ncg/ncg-docs --change "<change>" --top-k 5 --format json
```

Broader governance/docs sweep when needed:

```bash
rag retrieve semantic --scope all --query "<question>" --top-k 7 --format json
```

Optional discovery add-on:

```bash
qmd query "<question>" -c shared-ai-docs
```

## Output Contract

Always return:

1. prioritized source paths
2. section/chunk reference when available
3. short why-relevant rationale
4. explicit note whether results came from `rag`, `qmd`, or both
5. generated artifacts removed from shortlist (or explicitly marked as filtered)

## Guardrails

1. Do not claim functional/system validation from retrieval alone.
2. Do not replace exact structured lookups with fuzzy-only search when structured path is available.
3. If `rag` preflight fails, report blocker and only then fall back to `qmd`/`rg` with explicit label.
