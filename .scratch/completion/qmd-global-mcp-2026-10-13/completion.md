# Global QMD MCP setup — 2026-10-13

## Scope and identity

Requested by Daniel: register QMD globally through MCP, prefer MCP in the QMD skill, and verify search without interrupting ongoing chats.

- Repository: `shared-ai-docs`; fixed base `e5130fac0115d6ed0779759fc4ce975a62c660b4`.
- Reviewed write set: `skills-repo/skills/qmd/SKILL.md`, `skills-repo/skills/rag-documentation-research/SKILL.md`, `docs/rag/operating-model-rag-qmd.md`, and the new `mcp_servers.qmd` section of Daniel's local Codex configuration. The adjacent research skill delegates transport to the QMD owner to resolve DRY-01; its source-verification responsibilities are unchanged.
- Skill baseline SHA256: `3b9501fbbdaa3a6235c3e14d13ee50ce3537b6ca5513f850e2765c1bc64ed932`; candidate: `613bf49a21df6417ac37bcedaa806e5b3c8bbeabaa0cd108c4695e63b055bf1a`.
- Operating-model baseline SHA256: `35f94652514ee67e5b1b44737a710a9aa132475380c896b87ed27a50af38e9c8`; candidate: `fc19651903e7311d4a5b959c52e4d8d32de1fb688c3211289a899448587fd15f`.
- Research-skill baseline SHA256: `e8e4185946c1bd457452c59639e5f33d05878786df37d2d32c413330340dea5b`; candidate: `809cc53f3a18be96e4cae4503fff431ba73bf9448866cea3d19c6c9aacdd3f61`.
- Local configuration candidate, normalized by `codex mcp get qmd --json | jq -S .`, SHA256: `ccbb0712dea4cdb4ecf977ff718dbf03a43bc5cfca8c87ce641077ef970c2a9a`. DRY/SOLID inspected an equivalent raw JSON receipt with SHA256 `f47308a0f26c394205d310e73c7747b626acda4d96fab71feb14920e52e13af5`; sorting its keys matches this candidate byte-for-byte. Canonical sorting avoids CLI map-order differences. Before this change, no QMD MCP entry existed. The new entry starts existing Node/QMD in stdio mode, pins the existing index/config directory, allows `query`, `get`, `multi_get`, `status`, and sets a 180-second tool timeout.
- Existing unrelated changes in improve-skills, install-vendor-skills, their evidence and caches are excluded and preserved. This record and reviewer receipts are evidence, excluded from the candidate identity.

## Applicability and requirements evidence

Substantive review applies to effective MCP configuration and binding skill routing. This is a narrow setup/wording maintenance change using the installed QMD server; no new OpenSpec change or helper is needed under the repository's narrow-maintenance exception. Sources: current user request, repository `AGENTS.md`, `docs/rag/operating-model-rag-qmd.md`, QMD skill, installed MCP tool schemas, and official Codex MCP configuration documentation.

| Requirement | Expected | Observed evidence and limits |
|---|---|---|
| Global connection | Same registered QMD server from different local projects | `codex mcp get qmd --json` returns an enabled stdio entry. Calls from codex-global and ncg-backend resolve identical configuration. No project-specific change. |
| Exact search | MCP lexical search on chosen originals | Installed MCP SDK connected using the saved configuration. `query` with `searches:[{type:"lex",query:"QMD"}]`, `collections:["danielsvault-rag"]`, `limit:3`, `rerank:false` returned README, deployment and runtime spec. All three belong to the selected collection. |
| Semantic search | Natural-language MCP vector search works | `query` with `searches:[{type:"vec",query:"How are QMD collections configured for DanielsVault?"}]`, the same collection, `limit:2`, `rerank:false` returned the QMD runtime README and collection-maintenance spec. Existing local model used; no model installation or index embedding job. |
| Document retrieval | A search hit can be read | `get` with `file:"#6b1baa"` returned a Markdown embedded resource containing the actual original README heading. The verification handles MCP resource blocks as well as text blocks. |
| Actual Codex connection | Tools are callable through Codex, not only an independent client | After normal registration, `mcp__qmd__query` was discovered in this current chat and returned the same three expected lexical results and two semantic results with a collection filter and intent. Original responses are in [mcp-search-results.json](mcp-search-results.json). `mcp__qmd__get` returned the README's first eight lines as a Markdown resource. No forced reload or chat interruption. |
| Empty result boundary | No fabricated matches | Lex query `qmd-check-no-such-identifier-01a1353a` in the same collection returned an empty results array without error. |
| MCP preferred | Ordinary retrieval does not need shell status | Skill explicitly prefers callable MCP query/get/multi_get, native collection filters, lexical no-rerank search and structured semantic search. Shell status guard remains only for explicit CLI/fallback/index work. Operating model matches. |
| Preserve maintenance and authority | No implicit maintenance or permission expansion | Existing scheduled index-maintenance reference and wiki source checks remain; four exposed read tools only. Project sandbox permissions were not changed. |
| Audit-chat connection | QMD MCP is callable in the named audit chat | On 2026-10-14, after Daniel explicitly authorized a read-only test message and the chat was confirmed idle, `Main: Audit-Tickets parallel starten` called MCP `status`, `query` and `get` successfully. Status returned 2,599 documents, zero pending embeddings and a vector index; the lexical query returned the runtime README and deployment document, and `get` returned the README's first eight lines. See [audit-mcp-verification.md](audit-mcp-verification.md). |
| Preserve running chats | No active audit interruption or application restart | Initial setup did not message or restart any chat. The later explicitly authorized test started one bounded turn in the idle audit chat; it finished successfully and the chat returned to idle. No running audit turn was interrupted, no audit files were changed, and no application restart or forced MCP reload was used. Independent verification clients were closed. |

Configuration was read through Codex's own CLI rather than trusting TOML syntax alone. Initial functional checks use the installed MCP SDK because it is the QMD server's native protocol runtime; no helper was delivered. Actual Codex tool calls then confirmed live integration in this current chat and the named audit chat. These checks do not claim that every pre-existing chat has refreshed its own tool catalog. Arbitrary remote/cloud hosts were outside scope.

## Standards coverage

- DRY: consistent transport choice and collection filtering across skill and operating model; avoid duplicated machine-specific setup in shared skill text.
- SOLID: MCP/CLI/maintenance responsibilities, advertised tool schema, error boundaries, originals/wiki authority, and four-tool configuration contract.
- KISS: narrow change, preserved unrelated work, clear fallback language, no unnecessary daemon/helper/spec change, and runtime/path choices justified by installed dependencies.
- Automated/document checks: quick_validate on the QMD and research skills passed using the existing RAG virtual environment; scoped `git diff --check` passed; active skill symlink resolves to the canonical edited entry.

## Reviewer receipts

- DRY: initial receipt `/root/qmd_review_dry` found DRY-01, divergent CLI advice in the adjacent research skill. Repaired by delegation; the same reviewer checked `dry-repair.diff` and the complete research skill and returned pass with DRY-01 resolved. Prior unaffected coverage retained; reviewed research-skill SHA256 `809cc53f3a18be96e4cae4503fff431ba73bf9448866cea3d19c6c9aacdd3f61`.
- SOLID: `/root/qmd_review_solid` reviewed the fixed base and all four candidate identities above, complete surrounding content, requirements evidence and installed MCP implementation. Pass; no actionable findings. Covered transport/maintenance/source-verification ownership, advertised schemas, failure boundaries and four-read-tool configuration.
- KISS: `/root/qmd_review_kiss` reviewed the fixed base, all current candidate identities (including sorted config SHA256 `ccbb0712dea4cdb4ecf977ff718dbf03a43bc5cfca8c87ce641077ef970c2a9a`), complete surrounding content and requirements evidence. Pass; no actionable findings. Covered narrow scope, readable guidance, relative links, preserved boundaries, existing upstream runtime, and absence of unnecessary helpers/services/spec work.

## Final state and delivery

State: technically-complete and accepted by Daniel on 2026-10-14. Functional lexical/semantic retrieval through the actual Codex connection, document retrieval, empty-result boundary, configuration resolution and document checks pass. The named audit chat also passed its explicitly authorized read-only MCP test. DRY, SOLID and KISS reviews remain current: closeout rechecked all three file identities and the normalized configuration identity without changing the reviewed candidate. Local MCP configuration is installed and the active QMD/research skill symlinks resolve to the canonical edited files. Non-QMD values and formatting match the protected original copy; only the new QMD section is added. Codex's CLI had omitted an existing empty Node REPL argument list during serialization; its original representation was restored without changing the normalized QMD candidate.

Daniel authorized scoped commit, push and any necessary merge to `main`, plus cleanup. This record accompanies the acceptance commit; its Git identity is available from the containing commit instead of being embedded recursively. Publication to `origin/main` is checked after committing and reported in the closing Codex response. The local global configuration is outside this repository; only its safe QMD-specific receipt is versioned. No active OpenSpec change covers this narrow maintenance work, so no unrelated change is archived. No worktree was created for this task. The two task-owned temporary directories were already removed. The durable verification files are retained; unrelated working changes and other completion records are preserved. No deployment, automation change, index update/embed/rebuild or running-chat interruption is part of this closeout.
