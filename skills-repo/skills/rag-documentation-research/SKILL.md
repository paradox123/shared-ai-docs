---
name: rag-documentation-research
description: RAG-first documentation research for DanielsVault. USE WHEN users ask to find, research, or narrow documentation sources before planning or implementation. MUST trigger on phrases like "durchsuche die dokumentation", "durchsuche docs", "research the documentation", "search the documentation", "find relevant docs", "welche dokumente sind relevant", and for `research-for-review` or `spec-closeout` source discovery. Prefer `rag` as default runtime and use `qmd` only as optional discovery add-on.
compatibility: Requires local `rag` runtime at `~/Documents/DanielsVault/_shared/danielsvault-rag`; optional `qmd` add-on.
---

# RAG Documentation Research

Use this skill whenever documentation retrieval is the first bottleneck.

## Operating Rule

1. `rag` is the default retrieval path.
2. `qmd` is optional for broader discovery.
3. Source-backed output is mandatory.

## Automation Session Guard

When this skill is loaded only as a support skill inside a session-review automation, do not run RAG preflight or documentation retrieval first. Defer startup order to the primary review skill, such as `improve-skills` and its Codex Desktop session-review reference, then use RAG only for docs, repos, services, or identifiers the bounded session evidence actually implicates.

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
cd ~/Documents/DanielsVault/_shared/danielsvault-rag
export PATH="$PWD/.venv/bin:$PATH"
command -v rag
rag --version
rag runtime health
```

## Local Runtime Transfer Mode

Use [runtime-transfer.md](references/runtime-transfer.md) when the user asks to move, package, reinstall, or explain the local DanielsVault RAG setup itself. Do not load that reference for ordinary documentation retrieval.

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
6. For exact env vars, secret names, route fragments, endpoint paths, certificate files, or other literal identifiers, do at most one structured pass and one hybrid/semantic pass before switching to `qmd search` or `rg`.

Recommended commands:

```bash
rag retrieve semantic --scope ncg/ncg-docs --query "<question>" --top-k 5 --format json
rag retrieve structured --scope ncg/ncg-docs --record-type ci_setting_fact --filter "setting_name=<EXACT_TERM>"
rag retrieve structured --scope ncg/ncg-docs --record-type ci_setting_fact --filter "setting_name~term1|term2|term3"
rag retrieve hybrid --scope ncg/ncg-docs --record-type ci_setting_fact --query "<question>" --top-k 5 --format json
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

Current JSON shapes:

- `rag retrieve semantic ... --format json` returns `hits[]`
- `rag retrieve hybrid ... --format json` returns `hits[]`
- `rag retrieve structured ... --format json` returns `facts[]`

Do not assume a generic `results[]` key unless you already inspected the raw output for the installed runtime.

Exact-term sequence:

```bash
rag retrieve structured --scope ncg/ncg-docs --record-type ci_setting_fact --filter "setting_name=<EXACT_TERM>" --top-k 10 --format json
rag retrieve hybrid --scope ncg/ncg-docs --record-type ci_setting_fact --query "<EXACT_TERM> <repo/service/context>" --top-k 7 --format json
qmd search "<EXACT_TERM>" -c ncg-docs -n 20 --files
rg -n -F "<EXACT_TERM>" ~/Documents/DanielsVault/ncg/ncg-docs/docs
```

If `rag retrieve structured` reports `unsupported filter expression`, rewrite once into `field=value` or `field~a|b` form and move on.
If `rag retrieve hybrid` errors because `--record-type` is missing, add it once and continue; do not iterate on multiple hybrid shapes first.
If the chunk store looks stale or schema-mismatched for the current runtime, fall back to `qmd` or `rg` instead of spending a routine documentation task debugging or mutating the shared RAG runtime/store.

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
4. Treat RAG store refresh, re-ingest, or schema repair as separate maintenance work unless the user explicitly asked to repair the retrieval runtime itself.
