#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run-reporting-contract-checks.sh [all|baseline|summary|telemetry|style|efficiency|downstream] [--run-dir DIR] [--keep]

Runs deterministic DWT-S4 reporting contract checks against source-controlled
fixtures and the retained DWT-S1 l1-summary.json compatibility baseline.
The runner writes evidence/dwt-s4-reporting-summary.json in an isolated run dir.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUITE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SUITE_DIR/../.." && pwd)"
REPORTING_DIR="$SUITE_DIR/reporting"
FIXTURE_SRC="$REPORTING_DIR/fixtures"
VALIDATOR="$REPORTING_DIR/validators/reporting-contract-validator.js"

selector="all"
run_dir=""
keep=0

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
  all|baseline|summary|telemetry|style|efficiency|downstream) ;;
  *)
    echo "Unknown selector: $selector" >&2
    usage >&2
    exit 2
    ;;
esac

created_run_dir=0
if [ -z "$run_dir" ]; then
  run_dir="$(mktemp -d "${TMPDIR:-/tmp}/docworkflow-agent-delivery-reporting.XXXXXX")"
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

node "$VALIDATOR" \
  --fixtures "$FIXTURE_SRC" \
  --evidence "$evidence_dir" \
  --repo-root "$REPO_ROOT" \
  --selector "$selector"

echo "RESULT: PASS"
if [ "$keep" -eq 1 ] || [ "$created_run_dir" -eq 0 ]; then
  echo "Fixture: $run_dir"
fi
