#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run-mock-e2e-checks.sh [large|small|all] [--keep] [--run-id ID]
  run-mock-e2e-checks.sh --help

Runs deterministic local mock E2E checks for the DocWorkflow Agent Delivery
mock fixture family. The runner does not use network, Docker, Codex auth,
external agent providers or manual starts.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUITE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SUITE_DIR/../.." && pwd)"
RUNNER="$SUITE_DIR/e2e/mock-runner/run.js"

selector=""
keep=0
run_id=""

if [ "$#" -eq 0 ]; then
  usage >&2
  exit 2
fi

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
  --*)
    echo "Missing selector: large, small or all" >&2
    usage >&2
    exit 2
    ;;
  *)
    selector="$1"
    shift
    ;;
esac

while [ "$#" -gt 0 ]; do
  case "$1" in
    --keep)
      keep=1
      shift
      ;;
    --run-id)
      run_id="${2:?missing --run-id value}"
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
  large|small|all) ;;
  *)
    echo "Unknown selector: $selector" >&2
    usage >&2
    exit 2
    ;;
esac

if [ "$(pwd -P)" != "$REPO_ROOT" ]; then
  echo "Unsupported cwd: run from $REPO_ROOT" >&2
  exit 2
fi

node_args=(
  "$RUNNER"
  "--repo-root" "$REPO_ROOT"
  "--selector" "$selector"
)

if [ "$keep" -eq 1 ]; then
  node_args+=("--keep")
fi

if [ -n "$run_id" ]; then
  node_args+=("--run-id" "$run_id")
fi

node "${node_args[@]}"
