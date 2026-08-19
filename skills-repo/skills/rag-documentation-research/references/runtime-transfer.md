# QMD Runtime Transfer

Use this reference only when moving, packaging, reinstalling, or explaining the DanielsVault retrieval setup.

## Stable Anchors

- Collection manifest: `~/Documents/DanielsVault/_shared/danielsvault-rag/qmd-collections.json`
- Reconciliation helper: `~/Documents/DanielsVault/_shared/danielsvault-rag/scripts/sync-qmd-collections.py`
- Compatibility CLI: `~/Documents/DanielsVault/_shared/danielsvault-rag`
- Operating guidance: `~/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/`
- QMD database: `${INDEX_PATH:-${XDG_CACHE_HOME:-$HOME/.cache}/qmd/index.sqlite}`

## Target Requirements

- Node.js supported by the installed QMD release.
- QMD installed globally: `npm install -g @tobilu/qmd`.
- A DanielsVault checkout containing every manifest path that should be enabled.
- Python 3.9+ only when the compatibility CLI or reconciliation helper is required.

## Installation and Reconciliation

```bash
npm install -g @tobilu/qmd
cd ~/Documents/DanielsVault/_shared/danielsvault-rag
python3 scripts/sync-qmd-collections.py --apply
qmd update
qmd embed
qmd status
```

Set `DANIELSVAULT_ROOT` when the vault lives elsewhere. The manifest uses vault-relative paths.

## Packaging Rules

- Package the manifest, helper, compatibility source, OpenSpec change/specs, operating docs, and relevant Codex skills.
- Do not package `.venv`, caches, `.git`, build outputs, secrets, or historical `.rag/store` files as the active index.
- Treat the QMD SQLite database as sensitive local data because it can contain embeddings and text-derived index data from the private collection.
- Prefer rebuilding the QMD database from the manifest on the target machine instead of transferring it.

## Verification

```bash
python3 scripts/sync-qmd-collections.py
qmd status
qmd search "documentation retrieval" -c shared-ai-docs -n 3 --json
rag runtime health
```

The reconciliation check must report no missing collections or conflicts. The compatibility health command must identify QMD as its engine.
