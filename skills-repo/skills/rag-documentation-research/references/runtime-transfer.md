# RAG Runtime Transfer

Use this reference only when the user asks to move, package, reinstall, or explain the local DanielsVault RAG setup itself, not just search documentation with it.

Stable anchors:

1. runtime: `~/Documents/DanielsVault/_shared/danielsvault-rag`
2. deployment guide: `~/Documents/DanielsVault/_shared/danielsvault-rag/DEPLOYMENT.md`
3. installer helper: `~/Documents/DanielsVault/_shared/danielsvault-rag/scripts/install-target.sh`
4. supporting docs: `~/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/`
5. Codex skills to include or reference: `rag-documentation-research` and `qmd`

First-pass inventory:

```bash
cd ~/Documents/DanielsVault/_shared/danielsvault-rag
sed -n '1,220p' README.md
sed -n '1,260p' DEPLOYMENT.md
sed -n '1,180p' scripts/install-target.sh
rg -n "embedding|embedding-model|model|RAG_STORE_DIR|DANIELSVAULT_ROOT" README.md DEPLOYMENT.md pyproject.toml setup.py src scripts
```

Packaging rules:

1. Prefer the existing `DEPLOYMENT.md` instructions instead of rediscovering install steps from scratch.
2. Include the runtime, `.rag/store/` if the user wants the current generated store, `DEPLOYMENT.md`, `scripts/install-target.sh`, `shared-ai-docs/docs/rag/`, and the RAG/QMD skill files.
3. Treat `.rag/store/` as sensitive local data because it can contain private-scope chunks.
4. Exclude secrets, credentials, virtualenvs, caches, build outputs, `.git/`, and unrelated generated artifacts.
5. Before creating an archive, run a bounded secret-name inventory and report blockers instead of silently packaging them:

```bash
find . -maxdepth 4 \( -name '.env*' -o -name '*secret*' -o -name '*token*' -o -name '*key*' -o -name '*credential*' \) -print
```

Embedding/model questions are exact runtime-configuration questions. Check CLI/source arguments and deployment docs first with the `rg` command above; do not inspect every repository in the vault unless those anchors fail to answer.
