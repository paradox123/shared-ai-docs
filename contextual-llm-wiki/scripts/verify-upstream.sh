#!/usr/bin/env bash
set -euo pipefail
base=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$base/.runtime/compiler"
# Keep provider-guard tests independent of the host's Claude settings fallback.
export LLMWIKI_CLAUDE_SETTINGS_PATH=/dev/null
exec "$base/wiki-node" node_modules/vitest/vitest.mjs run \
  test/source-selection.test.ts \
  test/compile-source-deletion-reconciliation.test.ts \
  test/freshness.test.ts \
  test/sdk/create-wiki-root.test.ts \
  test/provider-codex-agent.test.ts \
  test/utils/provider-guard.test.ts
