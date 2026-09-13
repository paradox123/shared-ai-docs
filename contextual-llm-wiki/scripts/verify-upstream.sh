#!/usr/bin/env bash
set -euo pipefail
base=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$base/.runtime/compiler"
# Keep provider-guard tests independent of the host's Claude settings fallback.
export LLMWIKI_CLAUDE_SETTINGS_PATH=/dev/null
tests=()
while IFS= read -r test_file; do
  [[ -f "$test_file" ]] || { echo "Required upstream test missing: $test_file" >&2; exit 1; }
  tests+=("$test_file")
done < "$base/scripts/upstream-tests.txt"
[[ ${#tests[@]} -gt 0 ]] || { echo "No required upstream tests configured" >&2; exit 1; }
exec "$base/wiki-node" node_modules/vitest/vitest.mjs run "${tests[@]}" "$@"
