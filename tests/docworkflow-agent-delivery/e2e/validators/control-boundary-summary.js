#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const SUMMARY_SCHEMA = "docworkflow-agent-delivery-control-boundary-summary.v1";
const PASS_STATUSES = {
  control_session_status: "observed_only",
  session_chain_status: "pass",
  workflow_delivery_status: "pass",
  visible_session_status: "pass",
  overall_workflow_status: "pass"
};

const STATUS_VALUES = {
  control_session_status: new Set(["observed_only", "failed", "not_ready"]),
  session_chain_status: new Set(["pass", "fail", "not_ready"]),
  workflow_delivery_status: new Set(["pass", "fail", "not_ready"]),
  visible_session_status: new Set(["pass", "fail", "not_ready"]),
  overall_workflow_status: new Set(["pass", "fail", "not_ready"])
};

const PROHIBITED_CONTROL_WRITES = new Map([
  ["parent_orchestration", "direct_orchestration_write"],
  ["child_spec", "direct_hardening_write"],
  ["child_handoff", "direct_hardening_write"],
  ["child_delivery_evidence", "direct_delivery_write"],
  ["closeout_evidence", "direct_closeout_write"],
  ["target_output", "direct_output_write"]
]);

const REQUIRED_TOP_LEVEL = [
  "schema_id",
  "run_id",
  "control_session",
  "workflow_sessions",
  "write_observations",
  "control_session_status",
  "session_chain_status",
  "workflow_delivery_status",
  "visible_session_status",
  "overall_workflow_status"
];

const target = process.argv[2];
if (!target) {
  console.error("Usage: control-boundary-summary.js <summary-json|fixture-directory>");
  process.exit(2);
}

const targetPath = path.resolve(target);
const files = collectJsonFiles(targetPath);
let failures = 0;

for (const file of files) {
  const result = validateFile(file);
  if (result.errors.length > 0) {
    failures += 1;
    console.error(`FAIL ${path.relative(process.cwd(), file)}`);
    for (const error of result.errors) console.error(`- ${error}`);
  } else {
    console.log(`PASS ${path.relative(process.cwd(), file)} (${result.caseId})`);
  }
}

if (failures > 0) {
  console.error(`RESULT: FAIL (${failures}/${files.length} fixtures failed)`);
  process.exit(1);
}

console.log(`RESULT: PASS (${files.length} cases)`);

function collectJsonFiles(inputPath) {
  if (!fs.existsSync(inputPath)) {
    console.error(`Fixture path not found: ${inputPath}`);
    process.exit(2);
  }

  const stat = fs.statSync(inputPath);
  if (stat.isFile()) return [inputPath];
  if (!stat.isDirectory()) {
    console.error(`Fixture path must be a file or directory: ${inputPath}`);
    process.exit(2);
  }

  const entries = fs.readdirSync(inputPath)
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map((name) => path.join(inputPath, name));
  if (entries.length === 0) {
    console.error(`No JSON fixtures found in ${inputPath}`);
    process.exit(2);
  }
  return entries;
}

function validateFile(file) {
  const errors = [];
  let summary;
  try {
    summary = JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    return { caseId: path.basename(file), errors: [`invalid JSON: ${error.message}`] };
  }

  const expectation = summary.fixture_expectation || inferExpectation(file, summary);
  const caseId = expectation.case_id || summary.fixture_id || path.basename(file, ".json");

  for (const field of REQUIRED_TOP_LEVEL) {
    if (!(field in summary)) errors.push(`missing required field: ${field}`);
  }

  if (summary.schema_id !== SUMMARY_SCHEMA) {
    errors.push(`schema_id must be ${SUMMARY_SCHEMA}`);
  }

  validateStatuses(summary, expectation, errors);
  validateControlSession(summary, expectation, errors);
  validateWorkflowSessions(summary, expectation, errors);
  validateWriteObservations(summary, expectation, errors);
  validateExpectedViolations(summary, expectation, errors);
  validateNoSingleStatusShortcut(summary, errors);

  if (expectation.should_pass_boundary === true) {
    for (const [field, value] of Object.entries(PASS_STATUSES)) {
      if (summary[field] !== value) errors.push(`${field} must be ${value} for a passing boundary fixture`);
    }
    if (collectViolationCodes(summary).size > 0) {
      errors.push("passing boundary fixture must not include violation codes");
    }
  } else if (summary.overall_workflow_status === "pass") {
    errors.push("negative boundary fixture must not report overall_workflow_status=pass");
  }

  return { caseId, errors };
}

function inferExpectation(file, summary) {
  const name = path.basename(file, ".json");
  const shouldPass = name === "positive-observed-only" || summary.overall_workflow_status === "pass";
  return {
    case_id: name,
    should_pass_boundary: shouldPass,
    expected_control_session_status: shouldPass ? "observed_only" : undefined,
    expected_overall_workflow_status: shouldPass ? "pass" : undefined,
    expected_violation_codes: []
  };
}

function validateStatuses(summary, expectation, errors) {
  for (const [field, allowedValues] of Object.entries(STATUS_VALUES)) {
    if (!allowedValues.has(summary[field])) {
      errors.push(`${field} has invalid value: ${summary[field]}`);
    }
  }

  if (expectation.expected_control_session_status &&
      summary.control_session_status !== expectation.expected_control_session_status) {
    errors.push(`control_session_status expected ${expectation.expected_control_session_status}, got ${summary.control_session_status}`);
  }

  if (expectation.expected_overall_workflow_status &&
      summary.overall_workflow_status !== expectation.expected_overall_workflow_status) {
    errors.push(`overall_workflow_status expected ${expectation.expected_overall_workflow_status}, got ${summary.overall_workflow_status}`);
  }

  if (summary.control_session_status !== "observed_only" && summary.overall_workflow_status === "pass") {
    errors.push("overall_workflow_status cannot pass unless control_session_status is observed_only");
  }
}

function validateControlSession(summary, expectation, errors) {
  const control = summary.control_session || {};
  if (!control.control_session_id && expectation.requires_distinct_sessions !== false) {
    errors.push("control_session.control_session_id is required");
  }
  if (!control.control_actor_kind) errors.push("control_session.control_actor_kind is required");
  if (!Array.isArray(control.allowed_actions)) errors.push("control_session.allowed_actions must be an array");
  if (!Array.isArray(control.prohibited_actions_observed)) {
    errors.push("control_session.prohibited_actions_observed must be an array");
  }
}

function validateWorkflowSessions(summary, expectation, errors) {
  const sessions = Array.isArray(summary.workflow_sessions) ? summary.workflow_sessions : [];
  if (!Array.isArray(summary.workflow_sessions)) {
    errors.push("workflow_sessions must be an array");
    return;
  }

  const controlId = summary.control_session && summary.control_session.control_session_id;
  const seenIds = new Set();
  const expectedCodes = new Set(expectation.expected_violation_codes || []);
  const requiresDistinct = expectation.requires_distinct_sessions !== false &&
    expectation.expected_control_session_status !== "not_ready";

  if (expectation.should_pass_boundary && !sessions.some((session) => session.session_role === "parent_workflow")) {
    errors.push("passing fixture must include a parent_workflow session");
  }
  if (expectation.should_pass_boundary && !sessions.some((session) => session.session_role === "child_workflow")) {
    errors.push("passing fixture must include a child_workflow session");
  }

  for (const session of sessions) {
    if (!session.session_role) errors.push("workflow session missing session_role");
    if (!session.session_id) {
      if (requiresDistinct) errors.push(`workflow session ${session.session_role || "<unknown>"} missing session_id`);
      continue;
    }
    if (requiresDistinct && controlId && session.session_id === controlId) {
      const expectedSameSession = session.session_role === "parent_workflow"
        ? expectedCodes.has("control_parent_same_session")
        : expectedCodes.has("control_child_same_session");
      if (!expectedSameSession) {
        errors.push(`workflow session ${session.session_role} reuses control_session_id`);
      }
    }
    if (seenIds.has(session.session_id)) {
      if (!expectedCodes.has("control_child_same_session")) {
        errors.push(`duplicate workflow session id: ${session.session_id}`);
      }
    }
    seenIds.add(session.session_id);
  }
}

function validateWriteObservations(summary, expectation, errors) {
  if (!Array.isArray(summary.write_observations)) {
    errors.push("write_observations must be an array");
    return;
  }

  const controlId = summary.control_session && summary.control_session.control_session_id;
  for (const observation of summary.write_observations) {
    for (const field of ["artifact_path", "artifact_class", "actor_role", "writer_session_id", "allowed"]) {
      if (!(field in observation)) errors.push(`write observation missing ${field}`);
    }

    const expectedViolation = PROHIBITED_CONTROL_WRITES.get(observation.artifact_class);
    const writtenByControl = observation.actor_role === "control" ||
      (controlId && observation.writer_session_id === controlId);

    if (expectedViolation && writtenByControl) {
      if (observation.allowed !== false) {
        errors.push(`${observation.artifact_class} written by control must be allowed=false`);
      }
      if (observation.violation_code !== expectedViolation) {
        errors.push(`${observation.artifact_class} control write must use violation_code=${expectedViolation}`);
      }
    }
  }

  if (expectation.should_pass_boundary &&
      summary.write_observations.some((observation) => observation.allowed === false)) {
    errors.push("passing boundary fixture must not contain disallowed write observations");
  }
}

function validateExpectedViolations(summary, expectation, errors) {
  const expected = expectation.expected_violation_codes || [];
  const actual = collectViolationCodes(summary);
  for (const code of expected) {
    if (!actual.has(code)) errors.push(`missing expected violation_code: ${code}`);
  }

  if (expected.length > 0 && summary.control_session_status === "observed_only") {
    errors.push("fixtures with expected violations cannot report observed_only");
  }
}

function collectViolationCodes(summary) {
  const codes = new Set();
  const prohibited = summary.control_session && summary.control_session.prohibited_actions_observed;
  if (Array.isArray(prohibited)) {
    for (const code of prohibited) codes.add(code);
  }
  if (Array.isArray(summary.write_observations)) {
    for (const observation of summary.write_observations) {
      if (observation.violation_code) codes.add(observation.violation_code);
    }
  }
  if (Array.isArray(summary.boundary_findings)) {
    for (const finding of summary.boundary_findings) {
      if (finding.violation_code) codes.add(finding.violation_code);
    }
  }
  return codes;
}

function validateNoSingleStatusShortcut(summary, errors) {
  if ("status" in summary) {
    errors.push("summary must not collapse boundary evidence into a single top-level status field");
  }
}
