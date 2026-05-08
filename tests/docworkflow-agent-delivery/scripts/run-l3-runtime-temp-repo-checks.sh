#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run-l3-runtime-temp-repo-checks.sh [all|preflight|agent|fallback|validate-output|local-runtime|container-harness|closeout|style|telemetry] [--run-dir DIR] [--keep] [--output-bundle DIR] [--fixture DIR] [--skip-container]

Runs DWT-S5 L3 runtime temp-repo checks against a source-controlled synthetic
fixture. The runner writes evidence/dwt-s5-l3-summary.json in an isolated run
dir and generated repositories under target-repos/.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUITE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SUITE_DIR/../.." && pwd)"
L3_DIR="$SUITE_DIR/l3/runtime-temp-repo"
FIXTURE_SRC="$L3_DIR/fixtures"
VALIDATOR="$L3_DIR/validators/runtime-temp-repo-validator.js"
PROMPTFOO_CONFIG="$L3_DIR/promptfooconfig.yaml"
PROMPTFOO_VERSION="${DWT_S5_PROMPTFOO_VERSION:-0.121.9}"
BUNDLED_NODE_DIR="/Users/dh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"

selector="all"
run_dir=""
keep=0
output_bundle=""
fixture_dir=""
skip_container=0

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
    --fixture)
      fixture_dir="${2:?missing --fixture value}"
      shift 2
      ;;
    --skip-container)
      skip_container=1
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
  all|preflight|agent|fallback|validate-output|local-runtime|container-harness|closeout|style|telemetry) ;;
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
  run_dir="$(mktemp -d "${TMPDIR:-/tmp}/docworkflow-agent-delivery-l3-runtime-temp-repo.XXXXXX")"
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

if [ -n "$fixture_dir" ]; then
  validator_args+=(--fixture "$fixture_dir")
fi

if [ "$skip_container" -eq 1 ]; then
  validator_args+=(--skip-container)
fi

run_promptfoo_agent=0
case "$selector" in
  agent)
    run_promptfoo_agent=1
    ;;
  all)
    if [ "${DWT_S5_ENABLE_AGENT:-0}" = "1" ]; then
      run_promptfoo_agent=1
    fi
    ;;
esac

if [ "$run_promptfoo_agent" -eq 1 ]; then
  promptfoo_eval_json="$evidence_dir/promptfoo-eval.json"
  promptfoo_eval_log="$evidence_dir/promptfoo-eval.txt"
  promptfoo_auth_status="missing"

  if [ -z "${CODEX_HOME_OVERRIDE:-}" ] && [ -z "${CODEX_HOME:-}" ] && [ -f "$HOME/.codex/auth.json" ]; then
    export CODEX_HOME_OVERRIDE="$HOME/.codex"
  elif [ -z "${CODEX_HOME_OVERRIDE:-}" ] && [ -n "${CODEX_HOME:-}" ]; then
    export CODEX_HOME_OVERRIDE="$CODEX_HOME"
  fi

  if [ -n "${CODEX_HOME_OVERRIDE:-}" ] && [ -f "$CODEX_HOME_OVERRIDE/auth.json" ]; then
    promptfoo_auth_status="codex-home"
  elif [ -n "${OPENAI_API_KEY:-}" ] || [ -n "${CODEX_API_KEY:-}" ]; then
    promptfoo_auth_status="api-key-env"
  fi

  export DWT_S5_FIXTURE_WORKSPACE="$run_dir/agent-workspace"
  export DWT_S5_AGENT_REPO_ROOT="$REPO_ROOT"
  export DWT_S5_TARGET_REPO="$run_dir/target-repos/dwt-s5-synthetic-runtime-repo"
  export DWT_S5_SYNTHETIC_FIXTURE="$FIXTURE_SRC/synthetic-runtime-repo"
  export DWT_S5_PROMPTFOO_EVAL_JSON="$promptfoo_eval_json"
  export DWT_S5_PROMPTFOO_EVAL_LOG="$promptfoo_eval_log"
  export DWT_S5_PROMPTFOO_VERSION="$PROMPTFOO_VERSION"
  export DWT_S5_PROMPTFOO_AUTH_STATUS="$promptfoo_auth_status"
  mkdir -p "$DWT_S5_FIXTURE_WORKSPACE" "$(dirname "$DWT_S5_TARGET_REPO")"
  rm -rf "$DWT_S5_TARGET_REPO"
  cp -R "$DWT_S5_SYNTHETIC_FIXTURE" "$DWT_S5_TARGET_REPO"

  if [ -d "$BUNDLED_NODE_DIR" ]; then
    export PATH="$BUNDLED_NODE_DIR:$PATH"
  fi

  {
    printf 'command: npx --yes --package promptfoo@%s promptfoo eval -c %s --no-cache -o %s --no-progress-bar\n' "$PROMPTFOO_VERSION" "$PROMPTFOO_CONFIG" "$promptfoo_eval_json"
    printf 'auth_source: %s\n' "$promptfoo_auth_status"
  } > "$promptfoo_eval_log"

  set +e
  npx --yes --package "promptfoo@$PROMPTFOO_VERSION" promptfoo eval -c "$PROMPTFOO_CONFIG" --no-cache -o "$promptfoo_eval_json" --no-progress-bar >> "$promptfoo_eval_log" 2>&1
  promptfoo_status=$?
  set -e

  export DWT_S5_PROMPTFOO_EXIT_STATUS="$promptfoo_status"
fi

node "${validator_args[@]}"

echo "RESULT: PASS"
if [ "$keep" -eq 1 ] || [ "$created_run_dir" -eq 0 ]; then
  echo "Fixture: $run_dir"
fi
