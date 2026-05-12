#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- \
  --change simplify-agent-delivery-active-openspec \
  --root "$ROOT"

dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- \
  --change-dir tests/docworkflow-agent-delivery/active-scope/fixtures/valid-slice \
  --root "$ROOT"

if dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- \
  --change missing-active-scope-fixture \
  --root "$ROOT" >/tmp/agent-delivery-missing-active-scope.json; then
  echo "Expected missing active scope fixture to fail" >&2
  exit 1
fi

dotnet run skills-repo/tools/ValidateAgentDeliveryCleanup.cs -- \
  --manifest openspec/changes/simplify-agent-delivery-active-openspec/cleanup-manifest.json \
  --root "$ROOT"

dotnet run skills-repo/tools/ValidateSkillProseBudget.cs -- \
  --root "$ROOT"

tests/docworkflow-agent-delivery/scripts/run-active-openspec-e2e-checks.sh
