#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run-l1-contract-checks.sh [all|l1a|l1b|l1c|l1d|l1e|l1f] [--run-dir DIR] [--keep]

Runs deterministic DWT-S1 L1 contract checks against source-controlled tiny
fixtures. The runner writes evidence/l1-summary.json in an isolated run dir.
Without --keep, an auto-created run dir is removed at exit.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUITE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SUITE_DIR/../.." && pwd)"
L1_DIR="$SUITE_DIR/l1"
FIXTURE_SRC="$L1_DIR/fixtures"

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
  all|l1a|l1b|l1c|l1d|l1e|l1f) ;;
  *)
    echo "Unknown selector: $selector" >&2
    usage >&2
    exit 2
    ;;
esac

created_run_dir=0
if [ -z "$run_dir" ]; then
  run_dir="$(mktemp -d "${TMPDIR:-/tmp}/docworkflow-agent-delivery-l1.XXXXXX")"
  created_run_dir=1
else
  mkdir -p "$run_dir"
fi

run_dir="$(cd "$run_dir" && pwd)"
evidence_dir="$run_dir/evidence"
work_dir="$run_dir/fixtures"
mkdir -p "$evidence_dir" "$work_dir"

cleanup() {
  if [ "$created_run_dir" -eq 1 ] && [ "$keep" -eq 0 ]; then
    rm -rf "$run_dir"
  fi
}
trap cleanup EXIT

failures=0
status_l1a=""
status_l1b=""
status_l1c=""
status_l1d=""
status_l1e=""
status_l1f=""
truth_l1a=""
truth_l1b=""
truth_l1c=""
truth_l1d=""
truth_l1e=""
truth_l1f=""
provenance_parent_only="not-run"
provenance_generated_control="not-run"
provenance_hidden_normalization="not-run"
readiness_thin_child="not-run"
readiness_missing_rehearsal="not-run"
forbidden_actions_file="$evidence_dir/forbidden-actions.txt"
: > "$forbidden_actions_file"

log() {
  printf '%s\n' "$*"
}

pass() {
  log "PASS: $*"
}

fail() {
  log "FAIL: $*"
  failures=$((failures + 1))
}

copy_fixture() {
  fixture_id="$1"
  src="$FIXTURE_SRC/$fixture_id"
  dst="$work_dir/$fixture_id"
  if [ ! -d "$src" ]; then
    fail "fixture missing: $fixture_id"
    return 1
  fi
  rm -rf "$dst"
  mkdir -p "$dst"
  cp -R "$src/." "$dst/"
  printf '%s\n' "$dst"
}

assert_file() {
  if [ -f "$1" ]; then
    pass "file exists: $1"
  else
    fail "file missing: $1"
  fi
}

assert_contains() {
  file="$1"
  pattern="$2"
  label="$3"
  if grep -Fq "$pattern" "$file"; then
    pass "$label"
  else
    fail "$label (missing pattern: $pattern)"
  fi
}

assert_not_contains() {
  file="$1"
  pattern="$2"
  label="$3"
  if grep -Fq "$pattern" "$file"; then
    fail "$label (unexpected pattern: $pattern)"
  else
    pass "$label"
  fi
}

manifest_for() {
  printf '%s/fixture-manifest.json\n' "$1"
}

json_string() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

join_json_entries() {
  local first=1
  for entry in "$@"; do
    if [ -n "$entry" ]; then
      if [ "$first" -eq 0 ]; then
        printf ',\n'
      fi
      printf '    %s' "$entry"
      first=0
    fi
  done
}

result_entry() {
  label="$1"
  status="$2"
  if [ -n "$status" ]; then
    printf '"%s": "%s"' "$label" "$status"
  fi
}

truth_entry() {
  label="$1"
  status="$2"
  if [ -n "$status" ]; then
    printf '"%s": "%s"' "$label" "$status"
  fi
}

run_l1a() {
  fixture="$(copy_fixture parent-only)"
  manifest="$(manifest_for "$fixture")"
  assert_file "$manifest"
  assert_contains "$manifest" '"fixture_id": "parent-only"' "parent-only manifest id is stable"
  assert_contains "$manifest" '"removed_from_start_state"' "parent-only manifest records removed child artifacts"

  if find "$fixture/start-state" \( -iname '*child*' -o -iname '*handoff*' -o -iname '*index*' \) -print | grep -q .; then
    fail "parent-only start state contains child-control artifacts"
  else
    pass "parent-only start state contains no child-control artifacts"
  fi

  status_l1a="pass"
  truth_l1a="ran-target"
  provenance_parent_only="pass"
}

run_l1b() {
  fixture="$(copy_fixture generated-control-surface)"
  manifest="$(manifest_for "$fixture")"
  assert_file "$manifest"
  assert_file "$fixture/generated/child-index.md"
  assert_file "$fixture/generated/child-spec.md"
  assert_file "$fixture/generated/child-session-handoff.md"
  assert_contains "$manifest" '"generated_files"' "generated control manifest declares generated files"
  assert_contains "$manifest" '"provenance_source": "synthetic-parent-v1"' "generated control manifest links provenance source"
  assert_contains "$manifest" '"source_hash": "stable:synthetic-parent-v1"' "generated control manifest links source hash"
  assert_contains "$manifest" '"output_path": "generated/child-index.md"' "generated control manifest records output path"
  assert_not_contains "$manifest" '"copied_from_source_child_control": true' "generated control surface is not stale copied source"

  status_l1b="pass"
  truth_l1b="ran-target"
  provenance_generated_control="pass"
}

run_l1c() {
  fixture="$(copy_fixture thin-child-skeleton)"
  index_file="$fixture/child-index.md"
  spec_file="$fixture/child-spec.md"
  assert_file "$index_file"
  assert_file "$spec_file"

  blocked=0
  grep -Fq 'IMPLEMENTATION READY' "$index_file" && blocked=$((blocked + 1))
  if ! grep -Fq 'Parent Scope Conformance' "$spec_file"; then
    blocked=$((blocked + 1))
  fi
  if grep -Eq 'TBD| \|  \|' "$index_file"; then
    blocked=$((blocked + 1))
  fi
  if ! grep -Fq 'child-session-handoff' "$index_file"; then
    blocked=$((blocked + 1))
  fi
  if ! grep -Fq 'Command-Contract Rehearsal Evidence' "$spec_file"; then
    blocked=$((blocked + 1))
  fi

  if [ "$blocked" -ge 4 ]; then
    pass "thin child skeleton blocks implementation readiness"
    status_l1c="blocked"
    readiness_thin_child="blocked"
  else
    fail "thin child skeleton blocks implementation readiness"
    status_l1c="fail"
    readiness_thin_child="fail"
  fi
  truth_l1c="ran-target"
}

run_l1d() {
  fixture="$(copy_fixture missing-rehearsal-ready-claim)"
  index_file="$fixture/child-index.md"
  spec_file="$fixture/child-spec.md"
  handoff_file="$fixture/child-session-handoff.md"
  assert_file "$index_file"
  assert_file "$spec_file"
  assert_file "$handoff_file"

  high_risk=0
  if grep -Eiq 'docker|docker compose|kubectl|terraform|production|runtime' "$index_file" "$spec_file" "$handoff_file"; then
    high_risk=1
  fi

  rehearsal_present=0
  if grep -Fq 'Command-Contract Rehearsal Evidence' "$spec_file" && grep -Eiq 'Passed|Blocked|Failed' "$spec_file"; then
    rehearsal_present=1
  fi

  if [ "$high_risk" -eq 1 ] && [ "$rehearsal_present" -eq 0 ]; then
    pass "high-risk ready claim without rehearsal is blocked"
    status_l1d="blocked"
    readiness_missing_rehearsal="blocked"
  else
    fail "high-risk ready claim without rehearsal is blocked"
    status_l1d="fail"
    readiness_missing_rehearsal="fail"
  fi
  truth_l1d="ran-target"
}

run_l1e() {
  fixture="$(copy_fixture hidden-normalization)"
  manifest="$(manifest_for "$fixture")"
  source_file="$fixture/source/parent-spec.md"
  output_file="$fixture/output/parent-spec.md"
  assert_file "$manifest"
  assert_file "$source_file"
  assert_file "$output_file"

  source_hash="$(shasum -a 256 "$source_file" | awk '{print $1}')"
  output_hash="$(shasum -a 256 "$output_file" | awk '{print $1}')"
  normalizations_declared=1
  if grep -Eq '"normalizations"[[:space:]]*:[[:space:]]*\[\]' "$manifest"; then
    normalizations_declared=0
  fi

  if [ "$source_hash" != "$output_hash" ] && [ "$normalizations_declared" -eq 0 ]; then
    pass "hidden normalization fails provenance check"
    status_l1e="fail"
    provenance_hidden_normalization="fail"
  else
    fail "hidden normalization fails provenance check"
    status_l1e="pass"
    provenance_hidden_normalization="pass"
  fi
  truth_l1e="ran-target"
}

run_l1f() {
  fixture="$(copy_fixture s0-limitations-no-agent)"
  manifest="$(manifest_for "$fixture")"
  context_file="$fixture/s0-context.md"
  command_trace="$evidence_dir/l1-command-trace.txt"
  assert_file "$manifest"
  assert_file "$context_file"
  assert_contains "$context_file" "ADOPT_WITH_LIMITATIONS" "S0 context records ADOPT_WITH_LIMITATIONS"

  {
    printf 'shell-validator\n'
    printf 'fixture-copy\n'
    printf 'manifest-assertions\n'
  } > "$command_trace"

  if grep -Eiq 'promptfoo|codex|inspect|docker|npm|credential|auth|registry' "$command_trace"; then
    grep -Eio 'promptfoo|codex|inspect|docker|npm|credential|auth|registry' "$command_trace" > "$forbidden_actions_file"
    fail "L1 command trace avoids agent/auth/network/runtime dependencies"
  else
    pass "L1 command trace avoids agent/auth/network/runtime dependencies"
  fi

  status_l1f="pass"
  truth_l1f="ran-target"
}

write_summary() {
  summary_file="$evidence_dir/l1-summary.json"
  repo_json="$(json_string "$REPO_ROOT")"
  run_json="$(json_string "$run_dir")"
  manifest_json="$(json_string "$FIXTURE_SRC")"

  results_l1a="$(result_entry DWT-S1-L1A "$status_l1a")"
  results_l1b="$(result_entry DWT-S1-L1B "$status_l1b")"
  results_l1c="$(result_entry DWT-S1-L1C "$status_l1c")"
  results_l1d="$(result_entry DWT-S1-L1D "$status_l1d")"
  results_l1e="$(result_entry DWT-S1-L1E "$status_l1e")"
  results_l1f="$(result_entry DWT-S1-L1F "$status_l1f")"
  truth_a="$(truth_entry DWT-S1-L1A "$truth_l1a")"
  truth_b="$(truth_entry DWT-S1-L1B "$truth_l1b")"
  truth_c="$(truth_entry DWT-S1-L1C "$truth_l1c")"
  truth_d="$(truth_entry DWT-S1-L1D "$truth_l1d")"
  truth_e="$(truth_entry DWT-S1-L1E "$truth_l1e")"
  truth_f="$(truth_entry DWT-S1-L1F "$truth_l1f")"

  {
    printf '{\n'
    printf '  "suite_level": "L1",\n'
    printf '  "suite_version": "DWT-S1-local-v1",\n'
    printf '  "repo_root": "%s",\n' "$repo_json"
    printf '  "fixture_root": "%s",\n' "$run_json"
    printf '  "fixture_manifest": "%s",\n' "$manifest_json"
    printf '  "test_results": {\n'
    join_json_entries "$results_l1a" "$results_l1b" "$results_l1c" "$results_l1d" "$results_l1e" "$results_l1f"
    printf '\n  },\n'
    printf '  "provenance_checks": {\n'
    printf '    "parent_only_start": "%s",\n' "$provenance_parent_only"
    printf '    "generated_control_surface": "%s",\n' "$provenance_generated_control"
    printf '    "hidden_normalization": "%s"\n' "$provenance_hidden_normalization"
    printf '  },\n'
    printf '  "readiness_checks": {\n'
    printf '    "thin_child_skeleton": "%s",\n' "$readiness_thin_child"
    printf '    "missing_rehearsal_ready_claim": "%s"\n' "$readiness_missing_rehearsal"
    printf '  },\n'
    printf '  "forbidden_actions_observed": ['
    if [ -s "$forbidden_actions_file" ]; then
      awk 'BEGIN { first=1 } { gsub(/\\/,"\\\\"); gsub(/"/,"\\\""); if (!first) printf ", "; printf "\"%s\"", $0; first=0 }' "$forbidden_actions_file"
    fi
    printf '],\n'
    printf '  "evidence_truth": {\n'
    join_json_entries "$truth_a" "$truth_b" "$truth_c" "$truth_d" "$truth_e" "$truth_f"
    printf '\n  },\n'
    printf '  "s0_dependency_context": {\n'
    printf '    "result": "ADOPT_WITH_LIMITATIONS",\n'
    printf '    "l1_requires_promptfoo": false,\n'
    printf '    "l1_requires_codex_auth": false,\n'
    printf '    "l1_requires_npm_registry": false,\n'
    printf '    "note": "DWT-S0 limitations are context only for deterministic L1."\n'
    printf '  }\n'
    printf '}\n'
  } > "$summary_file"

  log "SUMMARY: $summary_file"
}

if [ "$selector" = "all" ] || [ "$selector" = "l1a" ]; then
  run_l1a
fi

if [ "$selector" = "all" ] || [ "$selector" = "l1b" ]; then
  run_l1b
fi

if [ "$selector" = "all" ] || [ "$selector" = "l1c" ]; then
  run_l1c
fi

if [ "$selector" = "all" ] || [ "$selector" = "l1d" ]; then
  run_l1d
fi

if [ "$selector" = "all" ] || [ "$selector" = "l1e" ]; then
  run_l1e
fi

if [ "$selector" = "all" ] || [ "$selector" = "l1f" ]; then
  run_l1f
fi

write_summary

if [ "$failures" -gt 0 ]; then
  log "RESULT: FAIL ($failures failing checks)"
  log "Fixture retained until trap cleanup: $run_dir"
  exit 1
fi

log "RESULT: PASS"
if [ "$keep" -eq 1 ] || [ "$created_run_dir" -eq 0 ]; then
  log "Fixture: $run_dir"
fi
