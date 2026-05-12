#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUNNER="$ROOT/tests/docworkflow-agent-delivery/e2e/active-openspec/runner/run.js"

cd "$ROOT"
node "$RUNNER" "$@"
