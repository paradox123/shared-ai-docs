#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const REQUIRED_FIELDS = [
  "fixture_id",
  "fixture_version",
  "spec_type",
  "expected_delivery_mode",
  "runner_mode",
  "session_strategy",
  "source_spec",
  "target_repo",
  "expected_children",
  "expected_outputs",
  "forbidden_outputs",
  "expected_sessions",
  "expected_closeout_state",
  "forbidden_source_paths"
];

const LARGE_CHILDREN = ["ML-C1", "ML-C2", "ML-C3", "ML-C4", "ML-C5"];
const LARGE_CONTENT = "1\n2\n3\n4\n5\n";
const FORBIDDEN_SOURCE_PATHS = [
  "/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**",
  "ki-fuer-kmu/**"
];

function usage() {
  console.error("Usage: mock-manifest-schema.js <mock-data-dir>");
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function arraysEqual(left, right) {
  return Array.isArray(left)
    && Array.isArray(right)
    && left.length === right.length
    && left.every((value, index) => value === right[index]);
}

function assert(condition, failures, code, message) {
  if (!condition) {
    failures.push({ code, message });
  }
}

function validateCommon(root, manifest, failures) {
  for (const field of REQUIRED_FIELDS) {
    assert(Object.prototype.hasOwnProperty.call(manifest, field), failures, "invalid_manifest_schema", `missing field ${field}`);
  }
  assert(typeof manifest.fixture_id === "string" && manifest.fixture_id.length > 0, failures, "invalid_manifest_schema", "fixture_id must be a non-empty string");
  assert(typeof manifest.fixture_version === "string" && manifest.fixture_version.length > 0, failures, "invalid_manifest_schema", "fixture_version must be a non-empty string");
  assert(manifest.runner_mode === "local-mock-session-runner", failures, "invalid_manifest_schema", "runner_mode must be local-mock-session-runner");
  assert(typeof manifest.source_spec === "string" && fs.existsSync(path.join(root, manifest.source_spec || "")), failures, "missing_source_spec", `source_spec is missing: ${manifest.source_spec}`);
  assert(manifest.target_repo === "mock-target" && fs.existsSync(path.join(root, "mock-target")), failures, "invalid_manifest_schema", "target_repo must be existing mock-target");
  assert(Array.isArray(manifest.expected_children), failures, "invalid_manifest_schema", "expected_children must be an array");
  assert(Array.isArray(manifest.expected_outputs), failures, "invalid_manifest_schema", "expected_outputs must be an array");
  assert(Array.isArray(manifest.forbidden_outputs), failures, "invalid_manifest_schema", "forbidden_outputs must be an array");
  assert(Array.isArray(manifest.expected_sessions), failures, "invalid_manifest_schema", "expected_sessions must be an array");
  assert(isObject(manifest.expected_closeout_state), failures, "invalid_manifest_schema", "expected_closeout_state must be an object");
  assert(arraysEqual(manifest.forbidden_source_paths, FORBIDDEN_SOURCE_PATHS), failures, "invalid_manifest_schema", "forbidden_source_paths must contain frozen KI-fuer-KMU patterns");
}

function validateLarge(root, manifest, failures) {
  assert(manifest.fixture_id === "mock-large-parent-v1", failures, "invalid_manifest_schema", "large fixture_id mismatch");
  assert(manifest.spec_type === "large-parent", failures, "invalid_manifest_schema", "large spec_type mismatch");
  assert(manifest.expected_delivery_mode === "parent_child", failures, "invalid_manifest_schema", "large expected_delivery_mode mismatch");
  assert(manifest.session_strategy === "auto-start-and-resume", failures, "invalid_manifest_schema", "large session_strategy mismatch");
  assert(manifest.mock_sizing_directive === "force_parent_child", failures, "invalid_manifest_schema", "large mock_sizing_directive mismatch");
  assert(arraysEqual(manifest.expected_children, LARGE_CHILDREN), failures, "invalid_large_children", "large expected_children must be ML-C1..ML-C5");
  assert(arraysEqual(manifest.expected_outputs, ["mock-target/output/count.txt"]), failures, "invalid_manifest_schema", "large expected_outputs mismatch");
  assert(manifest.expected_output_content === LARGE_CONTENT, failures, "invalid_manifest_schema", "large expected_output_content mismatch");
  assert(isObject(manifest.child_output_contract), failures, "invalid_manifest_schema", "large child_output_contract must exist");
  if (isObject(manifest.child_output_contract)) {
    for (let i = 0; i < LARGE_CHILDREN.length; i += 1) {
      assert(manifest.child_output_contract[LARGE_CHILDREN[i]] === `append_or_set_line:${i + 1}`, failures, "invalid_manifest_schema", `large child_output_contract mismatch for ${LARGE_CHILDREN[i]}`);
    }
  }
  assert(manifest.expected_sessions.length === 5, failures, "invalid_manifest_schema", "large expected_sessions must have five entries");
  for (let i = 0; i < manifest.expected_sessions.length; i += 1) {
    const session = manifest.expected_sessions[i];
    assert(session.child_id === LARGE_CHILDREN[i], failures, "invalid_manifest_schema", `session child mismatch at ${i}`);
    assert(session.sequence_index === i + 1, failures, "invalid_manifest_schema", `session sequence mismatch for ${LARGE_CHILDREN[i]}`);
    assert(session.expected_final_status === "ran-target", failures, "invalid_manifest_schema", `session final status mismatch for ${LARGE_CHILDREN[i]}`);
    assert(session.handoff_required === true, failures, "invalid_manifest_schema", `session handoff requirement mismatch for ${LARGE_CHILDREN[i]}`);
  }
}

function validateSmall(root, manifest, failures) {
  assert(manifest.fixture_id === "mock-small-direct-v1", failures, "invalid_manifest_schema", "small fixture_id mismatch");
  assert(manifest.spec_type === "small-direct", failures, "invalid_manifest_schema", "small spec_type mismatch");
  assert(manifest.expected_delivery_mode === "direct", failures, "invalid_manifest_schema", "small expected_delivery_mode mismatch");
  assert(manifest.session_strategy === "direct-no-child-session", failures, "invalid_manifest_schema", "small session_strategy mismatch");
  assert(arraysEqual(manifest.expected_children, []), failures, "invalid_small_direct_contract", "small expected_children must be empty");
  assert(arraysEqual(manifest.expected_outputs, ["mock-target/output/small-direct-result.json"]), failures, "invalid_small_direct_contract", "small expected_outputs mismatch");
  assert(arraysEqual(manifest.expected_sessions, []), failures, "invalid_small_direct_contract", "small expected_sessions must be empty");
  for (const output of ["child-index.md", "child-session-handoffs/**", "child-specs/**"]) {
    assert(manifest.forbidden_outputs.includes(output), failures, "invalid_small_direct_contract", `small forbidden_outputs missing ${output}`);
  }
  assert(isObject(manifest.expected_output_json), failures, "invalid_small_direct_contract", "small expected_output_json must exist");
  if (isObject(manifest.expected_output_json)) {
    assert(manifest.expected_output_json.mode === "direct", failures, "invalid_small_direct_contract", "small output mode mismatch");
    assert(manifest.expected_output_json.result === "ok", failures, "invalid_small_direct_contract", "small output result mismatch");
    assert(manifest.expected_output_json.source === "mock-small-direct", failures, "invalid_small_direct_contract", "small output source mismatch");
  }
}

function runForbiddenScan(mockDataDir, failures) {
  const validator = path.join(__dirname, "forbidden-real-fixture.js");
  const result = spawnSync(process.execPath, [validator, mockDataDir], { encoding: "utf8" });
  if (result.status !== 0) {
    failures.push({
      code: "forbidden_real_fixture_path",
      message: "forbidden-real-fixture validator failed for positive mock data",
      stdout: result.stdout.trim(),
      stderr: result.stderr.trim()
    });
  }
}

function main() {
  const mockDataDir = process.argv[2];
  if (!mockDataDir) {
    usage();
    process.exit(2);
  }

  const root = path.resolve(mockDataDir);
  const fixtures = [
    { id: "mock-large-parent-v1", dir: path.join(root, "large-parent"), validator: validateLarge },
    { id: "mock-small-direct-v1", dir: path.join(root, "small-direct"), validator: validateSmall }
  ];
  const failures = [];
  const manifests = [];

  for (const fixture of fixtures) {
    const manifestPath = path.join(fixture.dir, "manifest.json");
    if (!fs.existsSync(manifestPath)) {
      failures.push({ code: "missing_manifest", message: `missing ${manifestPath}` });
      continue;
    }
    let manifest;
    try {
      manifest = readJson(manifestPath);
    } catch (error) {
      failures.push({ code: "invalid_manifest_schema", message: `${manifestPath} is not valid JSON: ${error.message}` });
      continue;
    }
    validateCommon(fixture.dir, manifest, failures);
    fixture.validator(fixture.dir, manifest, failures);
    manifests.push({ fixture_id: manifest.fixture_id, path: manifestPath });
  }

  runForbiddenScan(root, failures);

  const payload = {
    status: failures.length === 0 ? "pass" : "fail",
    checked_manifests: manifests,
    failures
  };
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(failures.length === 0 ? 0 : 1);
}

main();

