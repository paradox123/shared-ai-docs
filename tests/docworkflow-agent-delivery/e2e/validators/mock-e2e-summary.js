#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const SUMMARY_SCHEMA = "docworkflow-agent-delivery-mock-e2e-summary.v1";
const AGGREGATE_SCHEMA = "docworkflow-agent-delivery-mock-e2e-aggregate.v1";
const RUNNER_MODE = "local-mock-session-runner";
const NOT_USED_KEYS = ["network", "docker", "codex_auth", "external_provider", "manual_start"];

function usage() {
  console.error("Usage: mock-e2e-summary.js <summary-or-aggregate.json> [...]");
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function assert(condition, failures, code, message) {
  if (!condition) {
    failures.push({ code, message });
  }
}

function validateExternalDependencies(summary, failures) {
  assert(isObject(summary.external_dependencies), failures, "invalid_external_dependencies", "external_dependencies must be an object");
  if (!isObject(summary.external_dependencies)) return;
  for (const key of NOT_USED_KEYS) {
    assert(summary.external_dependencies[key] === "not_used", failures, "invalid_external_dependencies", `${key} must be not_used`);
  }
}

function validateOutputEvidence(summary, summaryFile, failures) {
  assert(Array.isArray(summary.output_evidence), failures, "invalid_output_evidence", "output_evidence must be an array");
  if (!Array.isArray(summary.output_evidence)) return;
  const runRoot = findRunRoot(summaryFile, summary.selector);
  for (const item of summary.output_evidence) {
    assert(typeof item.path === "string", failures, "invalid_output_evidence", "output evidence path must be a string");
    assert(typeof item.sha256_path === "string", failures, "invalid_output_evidence", "output evidence sha256_path must be a string");
    assert(typeof item.sha256 === "string" && /^[a-f0-9]{64}$/.test(item.sha256), failures, "invalid_output_evidence", "output sha256 must be hex");
    if (typeof item.path === "string") {
      assert(fs.existsSync(path.join(runRoot, item.path)), failures, "missing_output", `missing output ${item.path}`);
    }
    if (typeof item.sha256_path === "string") {
      assert(fs.existsSync(path.join(runRoot, item.sha256_path)), failures, "missing_output_hash", `missing output hash ${item.sha256_path}`);
    }
  }
}

function findRunRoot(summaryFile, selector) {
  const dir = path.dirname(path.resolve(summaryFile));
  if (selector === "large" && path.basename(dir) === "large") return path.dirname(dir);
  if (selector === "small" && path.basename(dir) === "small") return path.dirname(dir);
  return dir;
}

function validateSessionEvidence(summary, summaryFile, failures) {
  assert(Array.isArray(summary.session_evidence), failures, "invalid_session_evidence", "session_evidence must be an array");
  if (!Array.isArray(summary.session_evidence)) return;
  if (summary.selector === "large") {
    assert(summary.session_evidence.length === 5, failures, "invalid_session_evidence", "large summary must list five sessions");
  }
  if (summary.selector === "small") {
    assert(summary.session_evidence.length === 0, failures, "invalid_session_evidence", "small summary must list no sessions");
  }
  const runRoot = findRunRoot(summaryFile, summary.selector);
  let lastClosedAt = "";
  for (const relativePath of summary.session_evidence) {
    const file = path.join(runRoot, relativePath);
    assert(fs.existsSync(file), failures, "missing_session_evidence", `missing session evidence ${relativePath}`);
    if (!fs.existsSync(file)) continue;
    const session = readJson(file);
    assert(session.schema_id === "docworkflow-agent-delivery-mock-session.v1", failures, "invalid_session_schema", `${relativePath} schema mismatch`);
    assert(session.final_status === "ran-target", failures, "invalid_session_state", `${relativePath} final_status must be ran-target`);
    assert(session.closeout_status === "closed", failures, "invalid_session_state", `${relativePath} closeout_status must be closed`);
    assert(session.write_boundary_status === "pass", failures, "invalid_write_boundary", `${relativePath} write boundary must pass`);
    assert(session.external_dependency_status === "not_used", failures, "invalid_external_dependencies", `${relativePath} external dependencies must be not_used`);
    const transitions = Array.isArray(session.state_transitions) ? session.state_transitions : [];
    const states = transitions.map((item) => item.state);
    assert(!states.includes("manual_start_required"), failures, "invalid_session_state", `${relativePath} manual start is forbidden`);
    assert(!states.includes("blocked"), failures, "invalid_session_state", `${relativePath} blocked is forbidden in positive run`);
    assert(!states.includes("failed"), failures, "invalid_session_state", `${relativePath} failed is forbidden in positive run`);
    if (session.launch_status === "queued") {
      assert(states.includes("resumed"), failures, "invalid_session_state", `${relativePath} queued session must resume`);
    }
    assert(states.includes("ran-target") && states.includes("closed"), failures, "invalid_session_state", `${relativePath} must run target and close`);
    const closedAt = transitions.find((item) => item.state === "closed")?.at || "";
    const firstAt = transitions[0]?.at || "";
    if (lastClosedAt && firstAt) {
      assert(firstAt > lastClosedAt, failures, "invalid_session_order", `${relativePath} started before previous child closed`);
    }
    lastClosedAt = closedAt || lastClosedAt;
  }
}

function validateSummary(summary, summaryFile, failures) {
  const required = [
    "schema_id",
    "run_id",
    "selector",
    "fixture_id",
    "fixture_version",
    "spec_type",
    "sizing_decision",
    "overall_workflow_status",
    "session_chain_status",
    "expected_outputs_status",
    "forbidden_fixture_status",
    "evidence_truth",
    "runner_mode",
    "session_strategy",
    "mock_target_root",
    "session_evidence",
    "output_evidence",
    "forbidden_paths_checked",
    "generated_artifacts",
    "external_dependencies",
    "negative_cases"
  ];
  for (const field of required) {
    assert(Object.prototype.hasOwnProperty.call(summary, field), failures, "invalid_summary_schema", `missing field ${field}`);
  }
  assert(summary.schema_id === SUMMARY_SCHEMA, failures, "invalid_summary_schema", "summary schema_id mismatch");
  assert(["large", "small", "all"].includes(summary.selector), failures, "invalid_selector", "selector must be large, small or all");
  assert(summary.runner_mode === RUNNER_MODE, failures, "invalid_runner_mode", "runner_mode must be local-mock-session-runner");
  assert(summary.evidence_truth === "ran-target", failures, "invalid_evidence_truth", "positive summary evidence_truth must be ran-target");
  assert(summary.overall_workflow_status === "pass", failures, "invalid_workflow_status", "positive summary must pass");
  assert(summary.expected_outputs_status === "pass", failures, "invalid_output_status", "expected outputs must pass");
  assert(summary.forbidden_fixture_status === "pass", failures, "invalid_forbidden_status", "forbidden fixture status must pass");
  assert(Array.isArray(summary.forbidden_paths_checked) && summary.forbidden_paths_checked.length > 0, failures, "invalid_forbidden_paths_checked", "forbidden_paths_checked must be non-empty");
  assert(isObject(summary.generated_artifacts), failures, "invalid_generated_artifacts", "generated_artifacts must be an object");
  assert(Array.isArray(summary.negative_cases), failures, "invalid_negative_cases", "negative_cases must be an array");
  validateExternalDependencies(summary, failures);
  validateOutputEvidence(summary, summaryFile, failures);
  validateSessionEvidence(summary, summaryFile, failures);
  if (summary.selector === "large") {
    assert(summary.fixture_id === "mock-large-parent-v1", failures, "invalid_fixture_id", "large fixture id mismatch");
    assert(summary.sizing_decision === "parent_child", failures, "invalid_sizing_decision", "large sizing decision must be parent_child");
    assert(summary.session_chain_status === "pass", failures, "invalid_session_chain", "large session chain must pass");
    assert(summary.session_strategy === "auto-start-and-resume", failures, "invalid_session_strategy", "large session strategy mismatch");
    assert(summary.generated_artifacts.child_session_count === 5, failures, "invalid_generated_artifacts", "large must have five child sessions");
  }
  if (summary.selector === "small") {
    assert(summary.fixture_id === "mock-small-direct-v1", failures, "invalid_fixture_id", "small fixture id mismatch");
    assert(summary.sizing_decision === "direct", failures, "invalid_sizing_decision", "small sizing decision must be direct");
    assert(summary.session_chain_status === "not_applicable", failures, "invalid_session_chain", "small session chain must be not_applicable");
    assert(summary.session_strategy === "direct-no-child-session", failures, "invalid_session_strategy", "small session strategy mismatch");
    assert(summary.generated_artifacts.child_session_count === 0, failures, "invalid_generated_artifacts", "small must have no child sessions");
  }
  if (summary.selector === "all") {
    assert(summary.fixture_id === "mock-e2e-all-v1", failures, "invalid_fixture_id", "all fixture id mismatch");
    assert(summary.sizing_decision === "aggregate", failures, "invalid_sizing_decision", "all sizing decision must be aggregate");
    assert(summary.session_strategy === "aggregate", failures, "invalid_session_strategy", "all session strategy mismatch");
  }
}

function validateAggregate(aggregate, aggregateFile, failures) {
  const required = [
    "schema_id",
    "run_id",
    "large_summary",
    "small_summary",
    "large_status",
    "small_status",
    "overall_workflow_status",
    "forbidden_fixture_status",
    "created_at",
    "runner_mode"
  ];
  for (const field of required) {
    assert(Object.prototype.hasOwnProperty.call(aggregate, field), failures, "invalid_aggregate_schema", `missing aggregate field ${field}`);
  }
  assert(aggregate.schema_id === AGGREGATE_SCHEMA, failures, "invalid_aggregate_schema", "aggregate schema_id mismatch");
  assert(aggregate.runner_mode === RUNNER_MODE, failures, "invalid_runner_mode", "aggregate runner_mode mismatch");
  assert(aggregate.large_status === "pass", failures, "invalid_aggregate_status", "large_status must pass");
  assert(aggregate.small_status === "pass", failures, "invalid_aggregate_status", "small_status must pass");
  assert(aggregate.overall_workflow_status === "pass", failures, "invalid_aggregate_status", "aggregate must pass");
  assert(aggregate.forbidden_fixture_status === "pass", failures, "invalid_forbidden_status", "aggregate forbidden status must pass");
  const root = path.dirname(path.resolve(aggregateFile));
  for (const childSummary of [aggregate.large_summary, aggregate.small_summary]) {
    assert(typeof childSummary === "string" && fs.existsSync(path.join(root, childSummary)), failures, "missing_aggregate_summary", `missing ${childSummary}`);
  }
}

function main() {
  const files = process.argv.slice(2);
  if (files.length === 0) {
    usage();
    process.exit(2);
  }
  const results = [];
  const failures = [];
  for (const file of files) {
    let payload;
    try {
      payload = readJson(file);
    } catch (error) {
      failures.push({ code: "invalid_json", message: `${file}: ${error.message}` });
      continue;
    }
    if (payload.schema_id === AGGREGATE_SCHEMA) {
      validateAggregate(payload, file, failures);
    } else {
      validateSummary(payload, file, failures);
    }
    results.push({ file: path.resolve(file), schema_id: payload.schema_id });
  }
  const out = {
    status: failures.length === 0 ? "pass" : "fail",
    checked: results,
    failures
  };
  process.stdout.write(`${JSON.stringify(out, null, 2)}\n`);
  process.exit(failures.length === 0 ? 0 : 1);
}

main();
