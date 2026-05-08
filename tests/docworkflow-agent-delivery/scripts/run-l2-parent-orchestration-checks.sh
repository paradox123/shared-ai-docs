#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run-l2-parent-orchestration-checks.sh [all|agent|fallback|validate-output|style|telemetry] [--run-dir DIR] [--keep] [--output-bundle DIR]

Runs DWT-S2 L2 parent-first orchestration checks against source-controlled
fixtures. The runner writes evidence/dwt-s2-l2-summary.json in an isolated run
dir. Fallback artifact mode can validate deterministic contracts or report a
blocked agent path, but it is not accepted L2 agent proof without
agent_execution_status: ran-target.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUITE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SUITE_DIR/../.." && pwd)"
L2_DIR="$SUITE_DIR/l2/parent-first"
FIXTURE_SRC="$L2_DIR/fixtures"
VALIDATOR="$L2_DIR/validators/parent-first-validator.js"

selector="all"
run_dir=""
keep=0
output_bundle=""

if [ "$#" -gt 0 ] && [[ "$1" != --* ]]; then
  selector="$1"
  shift
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    --run-dir)
      run_dir="${2:?missing --run-dir value}"
      shift 2
      ;;
    --keep)
      keep=1
      shift
      ;;
    --output-bundle)
      output_bundle="${2:?missing --output-bundle value}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$selector" in
  all|agent|fallback|validate-output|style|telemetry) ;;
  *)
    echo "Unknown selector: $selector" >&2
    usage >&2
    exit 2
    ;;
esac

if [ "$selector" = "validate-output" ] && [ -z "$output_bundle" ]; then
  echo "validate-output requires --output-bundle DIR" >&2
  usage >&2
  exit 2
fi

created_run_dir=0
if [ -z "$run_dir" ]; then
  run_dir="$(mktemp -d "${TMPDIR:-/tmp}/docworkflow-agent-delivery-l2-parent-first.XXXXXX")"
  created_run_dir=1
else
  mkdir -p "$run_dir"
fi

run_dir="$(cd "$run_dir" && pwd)"
evidence_dir="$run_dir/evidence"
mkdir -p "$evidence_dir"

cleanup() {
  if [ "$created_run_dir" -eq 1 ] && [ "$keep" -eq 0 ]; then
    rm -rf "$run_dir"
  fi
}
trap cleanup EXIT

validator_args=(
  "$VALIDATOR"
  --fixtures "$FIXTURE_SRC"
  --evidence "$evidence_dir"
  --repo-root "$REPO_ROOT"
  --selector "$selector"
)

if [ -n "$output_bundle" ]; then
  validator_args+=(--output-bundle "$output_bundle")
fi

node "${validator_args[@]}"

echo "RESULT: PASS"
if [ "$keep" -eq 1 ] || [ "$created_run_dir" -eq 0 ]; then
  echo "Fixture: $run_dir"
fi
