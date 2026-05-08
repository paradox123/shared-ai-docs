#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  run-contract-checks.sh [all|tc1|tc2|reporting] [--fixture DIR] [--keep] [--source-specs DIR]

Runs contract checks for the DocWorkflow Agent Delivery test suite.
If no fixture is supplied, a temp fixture is created and removed unless --keep is set.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUITE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SUITE_DIR/../.." && pwd)"

testcase="all"
fixture_dir=""
source_specs="/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs"
keep=0

if [ "$#" -gt 0 ] && [[ "$1" != --* ]]; then
  testcase="$1"
  shift
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    --fixture)
      fixture_dir="${2:?missing --fixture value}"
      shift 2
      ;;
    --source-specs)
      source_specs="${2:?missing --source-specs value}"
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

case "$testcase" in
  all|tc1|tc2|reporting) ;;
  *)
    echo "Unknown testcase: $testcase" >&2
    usage >&2
    exit 2
    ;;
esac

created_fixture=0
if [ -z "$fixture_dir" ]; then
  setup_output="$("$SCRIPT_DIR/setup-fixture.sh" --source-specs "$source_specs")"
  fixture_dir="$(printf '%s\n' "$setup_output" | sed -n 's/^FIXTURE_DIR=//p' | tail -n 1)"
  created_fixture=1
fi

fixture_dir="$(cd "$fixture_dir" && pwd)"
specs_dir="$fixture_dir/_specs"
index_file="$specs_dir/2026-05-05-free-entry-v2-child-specs-index.md"
parent_file="$specs_dir/2026-05-04-free-entry-v2-master-spec.md"
s3_spec="$specs_dir/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md"
s3_handoff="$specs_dir/child-session-handoffs/s3-session-handoff.md"
stale_s3_handoff="$fixture_dir/negative/stale-handoffs/s3-missing-target-repo.md"
target_repo="$fixture_dir/target-repo"
evidence_dir="$fixture_dir/evidence"
mkdir -p "$evidence_dir"

cleanup() {
  if [ "$created_fixture" -eq 1 ] && [ "$keep" -eq 0 ]; then
    rm -rf "$fixture_dir"
  fi
}
trap cleanup EXIT

current_evidence=""
failures=0

log() {
  printf '%s\n' "$*"
  if [ -n "$current_evidence" ]; then
    printf '%s\n' "$*" >> "$current_evidence"
  fi
}

pass() {
  log "PASS: $*"
}

fail() {
  log "FAIL: $*"
  failures=$((failures + 1))
}

assert_file() {
  if [ -f "$1" ]; then
    pass "file exists: $1"
  else
    fail "file missing: $1"
  fi
}

assert_dir() {
  if [ -d "$1" ]; then
    pass "directory exists: $1"
  else
    fail "directory missing: $1"
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

row_for_child() {
  child="$1"
  awk -v child="$child" '
    BEGIN { FS = "|" }
    /^\|/ {
      cell = $2
      gsub(/^[ \t]+|[ \t]+$/, "", cell)
      if (cell == child) print
    }
  ' "$index_file" | head -n 1
}

assert_child_row_contains() {
  child="$1"
  pattern="$2"
  label="$3"
  row="$(row_for_child "$child")"
  if [ -n "$row" ] && printf '%s\n' "$row" | grep -Fq "$pattern"; then
    pass "$label"
  else
    fail "$label"
  fi
}

extract_handoff_target() {
  handoff="$1"
  sed -n 's/^- Target Repository \/ Working Directory: `\{0,1\}\([^`]*\)`\{0,1\}$/\1/p' "$handoff" | head -n 1
}

extract_handoff_write_set() {
  handoff="$1"
  sed -n 's/^- Allowed Write-Set: //p' "$handoff" | head -n 1
}

write_set_is_concrete() {
  value="$1"
  if printf '%s\n' "$value" | grep -Eiq 'voraussichtlich|likely|probably|expected|TBD|to be decided|as needed|related files|and related|etc\.?|unknown|todo'; then
    return 1
  fi
  printf '%s\n' "$value" | grep -Eq '[[:alnum:]_.-]+/[[:alnum:]_./*{}-]+'
}

fallback_validate_s3_ready() {
  handoff="$1"
  label="$2"
  local_errors=0

  required_header='| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |'
  grep -Fxq "$required_header" "$index_file" || local_errors=$((local_errors + 1))

  s3_row="$(row_for_child S3)"
  [ -n "$s3_row" ] || local_errors=$((local_errors + 1))
  printf '%s\n' "$s3_row" | grep -Fq 'IMPLEMENTATION READY' || local_errors=$((local_errors + 1))
  printf '%s\n' "$s3_row" | grep -Fq 'child-session-handoffs/s3-session-handoff.md' || local_errors=$((local_errors + 1))
  printf '%s\n' "$s3_row" | grep -Fq 'spec-change-delivery' || local_errors=$((local_errors + 1))

  [ -f "$handoff" ] || local_errors=$((local_errors + 1))
  grep -Fq -- '- Child: `S3`' "$handoff" || local_errors=$((local_errors + 1))
  grep -Fq -- '- Aktueller Verdict: IMPLEMENTATION READY' "$handoff" || local_errors=$((local_errors + 1))

  target="$(extract_handoff_target "$handoff")"
  if [ -z "$target" ] || [[ "$target" != /* ]] || [ ! -d "$target" ]; then
    local_errors=$((local_errors + 1))
  fi

  write_set="$(extract_handoff_write_set "$handoff")"
  if ! write_set_is_concrete "$write_set"; then
    local_errors=$((local_errors + 1))
  fi

  if [ "$local_errors" -eq 0 ]; then
    pass "$label"
    return 0
  fi

  fail "$label"
  return 1
}

fallback_expect_s3_stale() {
  handoff="$1"
  label="$2"
  target="$(extract_handoff_target "$handoff" || true)"
  if [ -z "$target" ]; then
    pass "$label"
  else
    fail "$label (unexpected target repo: $target)"
  fi
}

run_dotnet_validator_if_available() {
  child="$1"
  handoff="$2"
  label="$3"
  validator="$REPO_ROOT/skills-repo/tools/ValidateChildReadiness.cs"
  if ! command -v dotnet >/dev/null 2>&1; then
    log "BLOCKED(optional): $label (dotnet missing)"
    return 0
  fi
  if ! dotnet --list-sdks 2>/dev/null | grep -Eq '^10\.'; then
    log "BLOCKED(optional): $label (.NET 10 SDK missing; fallback validator already ran)"
    return 0
  fi
  if (cd /tmp && dotnet run "$validator" -- --index "$index_file" --child "$child" --handoff "$handoff") >> "$current_evidence" 2>&1; then
    pass "$label"
  else
    fail "$label"
  fi
}

run_tc1() {
  current_evidence="$evidence_dir/tc1-contract-checks.txt"
  : > "$current_evidence"
  log "TC1 evidence"
  log "Fixture: $fixture_dir"

  assert_file "$parent_file"
  assert_file "$index_file"
  assert_file "$s3_spec"
  assert_file "$s3_handoff"
  assert_contains "$REPO_ROOT/docs/doc-workflow.md" "## Spec Sizing Gate" "Spec Sizing Gate is documented"
  assert_contains "$REPO_ROOT/docs/doc-workflow.md" "Large Spec / Child Spec Pipeline" "Large Spec / Child Spec Pipeline is documented"
  assert_contains "$REPO_ROOT/skills-repo/skills/spec-orchestrator/SKILL.md" "Minimum Child Index columns" "spec-orchestrator requires minimum Child Index columns"
  assert_contains "$REPO_ROOT/skills-repo/skills/child-spec-hardening/SKILL.md" "command-contract rehearsals" "child-spec-hardening requires command-contract rehearsals"

  required_header='| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |'
  if grep -Fxq "$required_header" "$index_file"; then
    pass "Child Index has exact operational header"
  else
    fail "Child Index has exact operational header"
  fi

  for child in S0 S1 S2 S3 S4 S5 S6 S7; do
    if [ -n "$(row_for_child "$child")" ]; then
      pass "Child row exists: $child"
    else
      fail "Child row exists: $child"
    fi
  done

  fallback_validate_s3_ready "$s3_handoff" "S3 passes fallback readiness gate"
  run_dotnet_validator_if_available S3 "$s3_handoff" "S3 passes .NET readiness validator"

  for child in S4 S5 S6 S7; do
    assert_child_row_contains "$child" "NEEDS HARDENING" "$child remains in hardening queue"
    row="$(row_for_child "$child")"
    if printf '%s\n' "$row" | grep -Fq 'spec-change-delivery'; then
      fail "$child is not auto-released to spec-change-delivery"
    else
      pass "$child is not auto-released to spec-change-delivery"
    fi
  done

  assert_contains "$s3_spec" "Preflight" "S3 spec documents verification preflight"
  assert_contains "$s3_spec" "Docker-Gate" "S3 spec documents Docker gate"
  assert_contains "$s3_spec" "Anti-Loop-Regel" "S3 spec documents anti-loop verification rule"
  assert_contains "$s3_handoff" "Verification Commands" "S3 handoff persists verification commands"
}

run_tc2() {
  current_evidence="$evidence_dir/tc2-contract-checks.txt"
  : > "$current_evidence"
  log "TC2 evidence"
  log "Fixture: $fixture_dir"

  assert_file "$index_file"
  assert_file "$s3_spec"
  assert_file "$s3_handoff"
  assert_dir "$target_repo"

  fallback_validate_s3_ready "$s3_handoff" "S3 delivery kickoff gate passes in temp fixture"
  run_dotnet_validator_if_available S3 "$s3_handoff" "S3 delivery kickoff passes .NET readiness validator"

  target="$(extract_handoff_target "$s3_handoff")"
  target_canonical="$target"
  if [ -d "$target" ]; then
    target_canonical="$(cd "$target" && pwd)"
  fi
  case "$target_canonical" in
    "$fixture_dir"/*) pass "Handoff Target Repository is inside fixture" ;;
    *) fail "Handoff Target Repository is inside fixture" ;;
  esac

  source_root="${source_specs%/_specs}"
  assert_not_contains "$s3_handoff" "$source_root" "S3 handoff does not point verification commands at original repo"

  write_set="$(extract_handoff_write_set "$s3_handoff")"
  if write_set_is_concrete "$write_set"; then
    pass "Allowed Write-Set is concrete"
  else
    fail "Allowed Write-Set is concrete"
  fi

  assert_contains "$s3_handoff" "dotnet restore" "Handoff keeps dotnet restore gate"
  assert_contains "$s3_handoff" "dotnet build" "Handoff keeps dotnet build gate"
  assert_contains "$s3_handoff" "dotnet test" "Handoff keeps dotnet test gate"
  assert_contains "$s3_handoff" "run-harness.sh --case s3" "Handoff keeps local S3 harness gate"
  assert_contains "$s3_handoff" "docker build" "Handoff keeps Docker build gate"
  assert_contains "$s3_handoff" "docker run" "Handoff keeps Docker run gate"
  assert_contains "$s3_spec" "Secret-Leak-Assertions" "S3 spec requires secret-leak assertions"

  assert_file "$stale_s3_handoff"
  fallback_expect_s3_stale "$stale_s3_handoff" "Stale S3 handoff without Target Repository blocks"

  assert_child_row_contains S4 "NEEDS HARDENING" "S4 remains not implementation-ready"
  row="$(row_for_child S4)"
  if printf '%s\n' "$row" | grep -Fq 'spec-change-delivery'; then
    fail "S4 is not auto-implemented"
  else
    pass "S4 is not auto-implemented"
  fi

  assert_contains "$REPO_ROOT/skills-repo/skills/spec-change-delivery/SKILL.md" "Before editing a child implementation, check the Child Index" "spec-change-delivery requires Child Index gate"
  assert_contains "$REPO_ROOT/skills-repo/skills/spec-change-delivery/SKILL.md" "Target Repository / Working Directory" "spec-change-delivery requires target repository handoff validation"
  assert_contains "$REPO_ROOT/skills-repo/skills/spec-closeout/SKILL.md" "Child closeout must sync Parent Coverage" "spec-closeout requires Parent/Index/Evidence/Handoff sync"

  log "DRY-RUN: Runtime verification commands are contract-checked only; no implementation is executed in this harness."
}

if [ "$testcase" = "all" ] || [ "$testcase" = "tc1" ]; then
  run_tc1
fi

if [ "$testcase" = "all" ] || [ "$testcase" = "tc2" ]; then
  run_tc2
fi

if [ "$testcase" = "all" ] || [ "$testcase" = "reporting" ]; then
  "$SCRIPT_DIR/run-reporting-contract-checks.sh" all
fi

if [ "$failures" -gt 0 ]; then
  log "RESULT: FAIL ($failures failing checks)"
  log "Fixture retained until trap cleanup: $fixture_dir"
  exit 1
fi

log "RESULT: PASS"
if [ "$keep" -eq 1 ] || [ "$created_fixture" -eq 0 ]; then
  log "Fixture: $fixture_dir"
fi
