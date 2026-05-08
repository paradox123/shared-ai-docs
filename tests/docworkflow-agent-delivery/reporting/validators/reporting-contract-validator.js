#!/usr/bin/env node
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");

const STATUS = new Set(["pass", "fail", "blocked", "warn", "planned"]);
const TRUTH = new Set(["ran-target", "ran-rehearsal", "blocked", "failed", "planned", "dry-run"]);
const STYLE = new Set(["pass", "fail", "warn"]);
const EFFICIENCY = new Set(["pass", "fail", "warn", "blocked"]);
const FORBIDDEN = new Set([
  "docker",
  "runtime-build",
  "runtime-test",
  "credential-copy",
  "ki-fuer-kmu-write",
  "deployment"
]);

const CASES = {
  "DWT-S4-R1": "dwt-s4-r1-baseline.json",
  "DWT-S4-R2": "dwt-s4-r2-summary-schema.json",
  "DWT-S4-R3": "dwt-s4-r3-telemetry.json",
  "DWT-S4-R4": "dwt-s4-r4-style.json",
  "DWT-S4-R5": "dwt-s4-r5-efficiency.json",
  "DWT-S4-R6": "dwt-s4-r6-downstream.json"
};

function usage() {
  console.error("Usage: reporting-contract-validator.js --fixtures DIR --evidence DIR --repo-root DIR [--selector all|baseline|summary|telemetry|style|efficiency|downstream]");
}

function parseArgs(argv) {
  const args = {
    selector: "all"
  };
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const next = argv[i + 1];
    if (key === "--fixtures") {
      args.fixtures = next;
      i += 1;
    } else if (key === "--evidence") {
      args.evidence = next;
      i += 1;
    } else if (key === "--repo-root") {
      args.repoRoot = next;
      i += 1;
    } else if (key === "--selector") {
      args.selector = next;
      i += 1;
    } else if (key === "-h" || key === "--help") {
      usage();
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${key}`);
    }
  }
  if (!args.fixtures || !args.evidence || !args.repoRoot) {
    usage();
    process.exit(2);
  }
  return {
    fixtures: path.resolve(args.fixtures),
    evidence: path.resolve(args.evidence),
    repoRoot: path.resolve(args.repoRoot),
    selector: args.selector
  };
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function assert(condition, failures, code, message) {
  if (!condition) {
    failures.push({ code, message });
  }
}

function validateResultTruth(summary, failures) {
  assert(isObject(summary.test_results), failures, "missing_required_summary_field", "test_results must be an object");
  assert(isObject(summary.evidence_truth), failures, "invalid_evidence_truth", "evidence_truth must be an object");
  if (!isObject(summary.test_results) || !isObject(summary.evidence_truth)) {
    return;
  }
  for (const [caseId, status] of Object.entries(summary.test_results)) {
    assert(STATUS.has(status), failures, "missing_required_summary_field", `${caseId} has invalid status ${status}`);
    assert(Object.prototype.hasOwnProperty.call(summary.evidence_truth, caseId), failures, "invalid_evidence_truth", `${caseId} is missing evidence truth`);
    if (Object.prototype.hasOwnProperty.call(summary.evidence_truth, caseId)) {
      assert(TRUTH.has(summary.evidence_truth[caseId]), failures, "invalid_evidence_truth", `${caseId} has invalid evidence truth ${summary.evidence_truth[caseId]}`);
    }
  }
}

function validateLegacySummary(summary) {
  const failures = [];
  assert(summary.suite_level === "L1", failures, "missing_required_summary_field", "legacy baseline suite_level must be L1");
  assert(typeof summary.suite_version === "string" && summary.suite_version.length > 0, failures, "missing_required_summary_field", "suite_version must be non-empty");
  assert(path.isAbsolute(summary.repo_root || ""), failures, "missing_required_summary_field", "repo_root must be absolute");
  assert(path.isAbsolute(summary.fixture_root || ""), failures, "missing_required_summary_field", "fixture_root must be absolute");
  assert(summary.fixture_manifest !== undefined, failures, "missing_required_summary_field", "fixture_manifest must exist");
  validateResultTruth(summary, failures);
  assert(isObject(summary.provenance_checks), failures, "missing_required_summary_field", "provenance_checks must be an object");
  assert(isObject(summary.readiness_checks), failures, "missing_required_summary_field", "readiness_checks must be an object");
  assert(Array.isArray(summary.forbidden_actions_observed), failures, "missing_required_summary_field", "forbidden_actions_observed must be an array");
  if (Array.isArray(summary.forbidden_actions_observed)) {
    assert(summary.forbidden_actions_observed.length === 0, failures, "forbidden_runtime_command", "legacy baseline must not observe forbidden actions");
  }
  assert(isObject(summary.s0_dependency_context), failures, "missing_required_summary_field", "legacy baseline must keep S0 dependency context");
  assert(!Object.prototype.hasOwnProperty.call(summary, "schema_id"), failures, "legacy_compatibility_misused", "legacy baseline should not masquerade as v1");
  return failures;
}

function validateV1Summary(summary) {
  const failures = [];
  assert(summary.schema_id === "docworkflow-agent-delivery-summary.v1", failures, "missing_required_summary_field", "schema_id must be docworkflow-agent-delivery-summary.v1");
  assert(typeof summary.suite_level === "string" && summary.suite_level.length > 0, failures, "missing_required_summary_field", "suite_level must be non-empty");
  assert(typeof summary.suite_version === "string" && summary.suite_version.length > 0, failures, "missing_required_summary_field", "suite_version must be non-empty");
  assert(path.isAbsolute(summary.repo_root || ""), failures, "missing_required_summary_field", "repo_root must be absolute");
  assert(path.isAbsolute(summary.fixture_root || "") || summary.fixture_root === "planned", failures, "missing_required_summary_field", "fixture_root must be absolute or planned");
  assert(summary.fixture_manifest !== undefined, failures, "missing_required_summary_field", "fixture_manifest must exist");
  validateResultTruth(summary, failures);
  assert(isObject(summary.evidence_links) || Array.isArray(summary.evidence_links), failures, "missing_required_summary_field", "evidence_links must exist");
  assert(isObject(summary.runner_environment), failures, "missing_required_summary_field", "runner_environment must exist");
  assert(isObject(summary.provenance_checks), failures, "missing_required_summary_field", "provenance_checks must exist");
  assert(isObject(summary.readiness_checks), failures, "missing_required_summary_field", "readiness_checks must exist");
  assert(Array.isArray(summary.forbidden_actions_observed), failures, "missing_required_summary_field", "forbidden_actions_observed must be an array");
  if (isObject(summary.style_verdicts)) {
    for (const [caseId, verdict] of Object.entries(summary.style_verdicts)) {
      assert(STYLE.has(verdict), failures, "missing_required_summary_field", `${caseId} has invalid style verdict ${verdict}`);
    }
  }
  if (isObject(summary.telemetry_verdicts)) {
    for (const [caseId, verdict] of Object.entries(summary.telemetry_verdicts)) {
      assert(EFFICIENCY.has(verdict), failures, "missing_required_summary_field", `${caseId} has invalid telemetry verdict ${verdict}`);
    }
  }
  return failures;
}

function validateTelemetryManifest(manifest) {
  const failures = [];
  assert(typeof manifest.manifest_version === "string" && manifest.manifest_version.startsWith("docworkflow-agent-delivery-telemetry.v1"), failures, "missing_required_summary_field", "manifest_version must start with telemetry v1");
  assert(typeof manifest.run_id === "string" && manifest.run_id.length > 0, failures, "missing_required_summary_field", "run_id must exist");
  assert(typeof manifest.child_id === "string" && manifest.child_id.length > 0, failures, "missing_required_summary_field", "child_id must exist");
  assert(typeof manifest.skill_under_test === "string" && manifest.skill_under_test.length > 0, failures, "missing_required_summary_field", "skill_under_test must exist");
  assert(Array.isArray(manifest.commands), failures, "missing_required_summary_field", "commands must be an array");
  assert(isObject(manifest.file_reads), failures, "missing_required_summary_field", "file_reads must exist");
  assert(isObject(manifest.tool_calls), failures, "missing_required_summary_field", "tool_calls must exist");
  assert(Array.isArray(manifest.forbidden_command_classes), failures, "missing_required_summary_field", "forbidden_command_classes must be an array");
  assert(isObject(manifest.budget), failures, "missing_required_summary_field", "budget must exist");
  assert(EFFICIENCY.has(manifest.efficiency_verdict), failures, "missing_required_summary_field", "efficiency_verdict must use the frozen vocabulary");

  const forbidden = new Set(Array.isArray(manifest.forbidden_command_classes) ? manifest.forbidden_command_classes : []);
  const observedForbidden = [];
  if (Array.isArray(manifest.commands)) {
    for (const command of manifest.commands) {
      assert(typeof command.command_class === "string", failures, "missing_required_summary_field", "command_class must exist");
      assert(TRUTH.has(command.evidence_truth), failures, "invalid_evidence_truth", "command evidence_truth must use the frozen vocabulary");
      if (FORBIDDEN.has(command.command_class) || forbidden.has(command.command_class)) {
        observedForbidden.push(command.command_class);
      }
    }
  }

  const broadReads = Number(manifest.file_reads && manifest.file_reads.broad_scan_count || 0);
  const repeatedReads = Number(manifest.file_reads && manifest.file_reads.repeated_read_count || 0);
  const maxBroadReads = Number(manifest.budget && manifest.budget.max_broad_reads || 0);
  const maxRepeatedReads = Number(manifest.budget && manifest.budget.max_repeated_reads || 0);
  const hasJustification = Array.isArray(manifest.justifications) && manifest.justifications.length > 0;

  if (observedForbidden.length > 0) {
    assert(manifest.efficiency_verdict === "fail", failures, "forbidden_runtime_command", `forbidden command class observed: ${observedForbidden.join(", ")}`);
  }
  if ((broadReads > maxBroadReads || repeatedReads > maxRepeatedReads) && !hasJustification) {
    failures.push({ code: "unjustified_command_drift", message: "read drift exceeds budget without justification" });
  }
  if (manifest.efficiency_verdict === "warn") {
    assert(hasJustification, failures, "unjustified_command_drift", "warn verdict requires justification");
  }

  return {
    failures,
    observedForbidden,
    broadReads,
    repeatedReads
  };
}

function validateStyleFixture(fixture) {
  const failures = [];
  const sections = ["child_spec", "child_index_row", "persisted_handoff"];
  for (const section of sections) {
    assert(isObject(fixture[section]), failures, "missing_required_summary_field", `${section} must exist`);
  }
  if (failures.length > 0) {
    return failures;
  }

  const keys = ["child_id", "readiness_verdict", "target_repository", "handoff_pointer", "next_action"];
  for (const key of keys) {
    const values = sections.map((section) => fixture[section][key]);
    assert(values.every((value) => value === values[0]), failures, "stale_handoff_or_index_pointer", `${key} differs across child spec, index and handoff`);
  }
  for (const section of sections) {
    assert(Array.isArray(fixture[section].allowed_write_set) && fixture[section].allowed_write_set.length > 0, failures, "missing_required_summary_field", `${section} allowed_write_set must be concrete`);
    assert(Array.isArray(fixture[section].verification_commands) && fixture[section].verification_commands.length > 0, failures, "missing_required_summary_field", `${section} verification_commands must be concrete`);
    assert(TRUTH.has(fixture[section].evidence_truth), failures, "invalid_evidence_truth", `${section} evidence_truth must use the frozen vocabulary`);
    if (typeof fixture[section].next_action === "string") {
      assert(!/DWT-S[235].*ready|release DWT-S[235]|implement DWT-S[235]/i.test(fixture[section].next_action), failures, "descendant_child_released_without_own_verdict", `${section} next action releases a descendant`);
    }
  }
  return failures;
}

function writeEvidence(evidenceDir, fileName, payload) {
  const file = path.join(evidenceDir, fileName);
  fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
  return file;
}

function outcome(caseId, expectedFixtureStatus, harnessPassed, details) {
  return {
    case_id: caseId,
    expected_fixture_status: expectedFixtureStatus,
    harness_status: harnessPassed ? "pass" : "fail",
    evidence_truth: "ran-target",
    ...details
  };
}

function runBaseline(ctx) {
  const manifest = readJson(path.join(ctx.fixtures, "dwt-s1-retained-baseline", "fixture-manifest.json"));
  const baselinePath = manifest.external_summary_path;
  const beforeHash = sha256(baselinePath);
  const summary = readJson(baselinePath);
  const failures = validateLegacySummary(summary);
  const afterHash = sha256(baselinePath);
  if (beforeHash !== afterHash) {
    failures.push({ code: "missing_fixture_exercise_evidence", message: "retained baseline was mutated during validation" });
  }
  const payload = outcome("DWT-S4-R1", "pass", failures.length === 0, {
    baseline_path: baselinePath,
    baseline_hash_before: beforeHash,
    baseline_hash_after: afterHash,
    failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S4-R1"], payload);
  return payload;
}

function runSummary(ctx) {
  const positive = readJson(path.join(ctx.fixtures, "summary-v1-positive", "summary.json"));
  const negative = readJson(path.join(ctx.fixtures, "summary-missing-evidence-truth", "summary.json"));
  const positiveFailures = validateV1Summary(positive);
  const negativeFailures = validateV1Summary(negative);
  const expectedNegativeFailure = negativeFailures.some((failure) => failure.code === "invalid_evidence_truth");
  const harnessPassed = positiveFailures.length === 0 && expectedNegativeFailure;
  const payload = outcome("DWT-S4-R2", "fail", harnessPassed, {
    positive_summary_status: positiveFailures.length === 0 ? "pass" : "fail",
    negative_summary_status: negativeFailures.length === 0 ? "pass" : "fail",
    positive_failures: positiveFailures,
    negative_failures: negativeFailures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S4-R2"], payload);
  return payload;
}

function runTelemetry(ctx) {
  const manifest = readJson(path.join(ctx.fixtures, "telemetry-forbidden-runtime-command", "agent-run-manifest.json"));
  const result = validateTelemetryManifest(manifest);
  const expectedForbidden = result.observedForbidden.length > 0 && manifest.efficiency_verdict === "fail";
  const payload = outcome("DWT-S4-R3", "fail", expectedForbidden, {
    observed_forbidden_command_classes: result.observedForbidden,
    expected_failure: expectedForbidden ? "forbidden_runtime_command" : null,
    telemetry_failures: result.failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S4-R3"], payload);
  return payload;
}

function runStyle(ctx) {
  const fixture = readJson(path.join(ctx.fixtures, "style-stale-handoff-pointer", "style-fixture.json"));
  const failures = validateStyleFixture(fixture);
  const expectedStale = failures.some((failure) => failure.code === "stale_handoff_or_index_pointer");
  const payload = outcome("DWT-S4-R4", "fail", expectedStale, {
    style_failures: failures,
    stale_pointer_detected: expectedStale
  });
  writeEvidence(ctx.evidence, CASES["DWT-S4-R4"], payload);
  return payload;
}

function runEfficiency(ctx) {
  const manifest = readJson(path.join(ctx.fixtures, "efficiency-justified-broad-read-warn", "agent-run-manifest.json"));
  const result = validateTelemetryManifest(manifest);
  const harnessPassed = result.failures.length === 0 && manifest.efficiency_verdict === "warn" && manifest.justifications.length > 0;
  const payload = outcome("DWT-S4-R5", "warn", harnessPassed, {
    efficiency_verdict: manifest.efficiency_verdict,
    broad_reads: result.broadReads,
    repeated_reads: result.repeatedReads,
    justifications: manifest.justifications,
    efficiency_failures: result.failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S4-R5"], payload);
  return payload;
}

function runDownstream(ctx) {
  const fixture = readJson(path.join(ctx.fixtures, "downstream-s2-s3-blocked", "downstream-summary.json"));
  const failures = [];
  const downstream = fixture.downstream_children || {};
  for (const child of ["DWT-S2", "DWT-S3", "DWT-S5"]) {
    const status = downstream[child] && downstream[child].status;
    assert(status === "blocked" || status === "planned", failures, "descendant_child_released_without_own_verdict", `${child} must remain blocked or planned`);
  }
  const nextAction = fixture.next_action || "";
  const normalizedNextAction = nextAction.toLowerCase();
  const explicitlyBlocksRelease = normalizedNextAction.includes("do not release");
  assert(explicitlyBlocksRelease || !/release DWT-S[235]|implement DWT-S[235]|ready/i.test(nextAction), failures, "descendant_child_released_without_own_verdict", "next action must not release descendants");
  const payload = outcome("DWT-S4-R6", "blocked", failures.length === 0, {
    downstream_children: downstream,
    next_action: fixture.next_action,
    downstream_failures: failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S4-R6"], payload);
  return payload;
}

function writeSummary(ctx, results) {
  const byCase = Object.fromEntries(results.map((result) => [result.case_id, result]));
  const summary = {
    schema_id: "docworkflow-agent-delivery-summary.v1",
    suite_level: "DWT-S4",
    suite_version: "DWT-S4-reporting-contract-v1",
    repo_root: ctx.repoRoot,
    fixture_root: ctx.fixtures,
    fixture_manifest: path.join(ctx.fixtures, "summary-v1-positive", "fixture-manifest.json"),
    test_results: {
      "DWT-S4-R1": byCase["DWT-S4-R1"] ? byCase["DWT-S4-R1"].expected_fixture_status : "planned",
      "DWT-S4-R2": byCase["DWT-S4-R2"] ? byCase["DWT-S4-R2"].expected_fixture_status : "planned",
      "DWT-S4-R3": byCase["DWT-S4-R3"] ? byCase["DWT-S4-R3"].expected_fixture_status : "planned",
      "DWT-S4-R4": byCase["DWT-S4-R4"] ? byCase["DWT-S4-R4"].expected_fixture_status : "planned",
      "DWT-S4-R5": byCase["DWT-S4-R5"] ? byCase["DWT-S4-R5"].expected_fixture_status : "planned",
      "DWT-S4-R6": byCase["DWT-S4-R6"] ? byCase["DWT-S4-R6"].expected_fixture_status : "planned"
    },
    harness_case_results: Object.fromEntries(Object.entries(byCase).map(([caseId, result]) => [caseId, result.harness_status])),
    evidence_links: Object.fromEntries(Object.entries(CASES).map(([caseId, fileName]) => [caseId, path.join(ctx.evidence, fileName)])),
    evidence_truth: Object.fromEntries(Object.keys(CASES).map((caseId) => [caseId, byCase[caseId] ? "ran-target" : "planned"])),
    runner_environment: {
      os: `${os.type()} ${os.release()}`,
      shell: process.env.SHELL || "unknown",
      node: process.version,
      requires_agents: false,
      requires_docker: false
    },
    provenance_checks: {
      retained_dwt_s1_baseline: byCase["DWT-S4-R1"] && byCase["DWT-S4-R1"].harness_status === "pass" ? "pass" : "planned",
      summary_schema_v1: byCase["DWT-S4-R2"] && byCase["DWT-S4-R2"].harness_status === "pass" ? "pass" : "planned",
      telemetry_manifest_v1: byCase["DWT-S4-R3"] && byCase["DWT-S4-R3"].harness_status === "pass" ? "pass" : "planned"
    },
    readiness_checks: {
      style_handoff_index_sync: byCase["DWT-S4-R4"] && byCase["DWT-S4-R4"].harness_status === "pass" ? "pass" : "planned",
      efficiency_command_drift: byCase["DWT-S4-R5"] ? "warn" : "planned",
      downstream_release_guard: byCase["DWT-S4-R6"] ? "blocked" : "planned"
    },
    telemetry_verdicts: {
      "DWT-S4-R3": "fail",
      "DWT-S4-R5": "warn"
    },
    style_verdicts: {
      "DWT-S4-R4": "fail"
    },
    forbidden_actions_observed: [],
    downstream_children: {
      "DWT-S2": "blocked",
      "DWT-S3": "blocked",
      "DWT-S5": "planned"
    }
  };
  const summaryPath = path.join(ctx.evidence, "dwt-s4-reporting-summary.json");
  fs.writeFileSync(summaryPath, `${JSON.stringify(summary, null, 2)}\n`);
  return summaryPath;
}

function main() {
  const args = parseArgs(process.argv);
  fs.mkdirSync(args.evidence, { recursive: true });

  const runners = {
    baseline: runBaseline,
    summary: runSummary,
    telemetry: runTelemetry,
    style: runStyle,
    efficiency: runEfficiency,
    downstream: runDownstream
  };
  const order = ["baseline", "summary", "telemetry", "style", "efficiency", "downstream"];
  if (args.selector !== "all" && !runners[args.selector]) {
    throw new Error(`Unknown selector: ${args.selector}`);
  }
  const selected = args.selector === "all" ? order : [args.selector];
  const ctx = args;
  const results = selected.map((selector) => runners[selector](ctx));
  const summaryPath = writeSummary(ctx, results);
  const failures = results.filter((result) => result.harness_status !== "pass");

  for (const result of results) {
    console.log(`${result.harness_status.toUpperCase()}: ${result.case_id} expected fixture ${result.expected_fixture_status}`);
  }
  console.log(`SUMMARY: ${summaryPath}`);

  if (failures.length > 0) {
    process.exitCode = 1;
  }
}

main();
