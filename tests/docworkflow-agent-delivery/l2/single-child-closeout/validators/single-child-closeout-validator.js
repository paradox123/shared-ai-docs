#!/usr/bin/env node
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");

const CASES = {
  "DWT-S3-L2A": "dwt-s3-l2a-ready-kickoff.json",
  "DWT-S3-L2B": "dwt-s3-l2b-stale-handoff.json",
  "DWT-S3-L2C": "dwt-s3-l2c-closeout-sync.json",
  "DWT-S3-L2D": "dwt-s3-l2d-dwt-s5-blocked.json",
  "DWT-S3-L2E": "dwt-s3-l2e-blocked-agent.json",
  "DWT-S3-L2F": "dwt-s3-l2f-style-telemetry.json"
};

const REQUIRED_BUNDLE_FILES = [
  "source-manifest.json",
  "agent-output.md",
  "delivery-kickoff.md",
  "closeout-sync.md",
  "child-index-before.md",
  "child-index-after.md",
  "handoffs/dwt-s3-session-handoff.md",
  "handoffs/stale-dwt-s3-session-handoff.md",
  "agent-run-manifest.json",
  "evidence/dwt-s3-l2-summary.json"
];

const STATUS = new Set(["pass", "fail", "blocked", "warn", "planned"]);
const TRUTH = new Set(["ran-target", "ran-rehearsal", "blocked", "failed", "planned", "dry-run"]);
const AGENT_STATUS = new Set(["ran-target", "blocked_auth", "blocked_provider", "blocked_network", "blocked_runtime", "failed", "not-run"]);
const STYLE = new Set(["pass", "fail", "warn"]);
const TELEMETRY = new Set(["pass", "fail", "warn", "blocked"]);
const FORBIDDEN_COMMANDS = new Set(["docker", "runtime-build", "runtime-test", "credential-copy", "ki-fuer-kmu-write", "deployment"]);
const PARENT_COVERAGE = ["DWT-PR3", "DWT-PR4", "DWT-PR5", "DWT-PR7"];
const CURRENT_HANDOFF = "_specs/child-session-handoffs/dwt-s3-session-handoff.md";
const DWT_S2_SUMMARY = "tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/dwt-s2-l2-summary.json";
const DWT_S2_MANIFEST = "tests/docworkflow-agent-delivery/l2/parent-first/evidence/2026-05-08-ran-target/manifest.json";
const ALLOWED_WRITE_SET = [
  "_specs/2026-05-08 DocWorkflow Agent Delivery Testsuite DWT-S3 L2 Single-Child Delivery Closeout Gate Harness.md",
  "_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md",
  "_specs/child-session-handoffs/dwt-s3-session-handoff.md",
  "openspec/changes/docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness/**",
  "openspec/specs/docworkflow-agent-delivery-testsuite/spec.md",
  "tests/docworkflow-agent-delivery/l2/single-child-closeout/**",
  "tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh",
  "tests/docworkflow-agent-delivery/README.md",
  "tests/docworkflow-agent-delivery/testcases/tc2-single-child-delivery-next-handoff.md"
];

function usage() {
  console.error("Usage: single-child-closeout-validator.js --fixtures DIR --evidence DIR --repo-root DIR [--selector all|fallback|agent|validate-output|closeout|style|telemetry] [--output-bundle DIR]");
}

function parseArgs(argv) {
  const args = { selector: "all" };
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === "--fixtures") {
      args.fixtures = value;
      i += 1;
    } else if (key === "--evidence") {
      args.evidence = value;
      i += 1;
    } else if (key === "--repo-root") {
      args.repoRoot = value;
      i += 1;
    } else if (key === "--selector") {
      args.selector = value;
      i += 1;
    } else if (key === "--output-bundle") {
      args.outputBundle = value;
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
    selector: args.selector,
    outputBundle: args.outputBundle ? path.resolve(args.outputBundle) : null,
    runDir: path.dirname(path.resolve(args.evidence))
  };
}

function readText(file) {
  return fs.readFileSync(file, "utf8");
}

function readJson(file) {
  return JSON.parse(readText(file));
}

function exists(file) {
  return fs.existsSync(file);
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function assert(condition, failures, code, message) {
  if (!condition) {
    failures.push({ code, message });
  }
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function listFiles(dir) {
  if (!exists(dir)) {
    return [];
  }
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...listFiles(full));
    } else {
      out.push(full);
    }
  }
  return out;
}

function writeEvidence(evidenceDir, fileName, payload) {
  const file = path.join(evidenceDir, fileName);
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
  return file;
}

function copyTemplateFile(src, dest, replacements) {
  ensureDir(path.dirname(dest));
  const text = readText(src)
    .replaceAll("__RUN_DIR__", replacements.runDir)
    .replaceAll("__REPO_ROOT__", replacements.repoRoot);
  fs.writeFileSync(dest, text);
}

function materializeBundle(ctx, fixtureName) {
  const src = path.join(ctx.fixtures, fixtureName);
  const dest = path.join(ctx.evidence, "output-bundles", fixtureName);
  if (!exists(src)) {
    throw new Error(`Missing fixture: ${src}`);
  }
  fs.rmSync(dest, { recursive: true, force: true });
  for (const file of listFiles(src)) {
    const rel = path.relative(src, file);
    copyTemplateFile(file, path.join(dest, rel), ctx);
  }
  return dest;
}

function field(text, key) {
  const pattern = new RegExp(`^${key}:\\s*(.+)$`, "m");
  const match = text.match(pattern);
  return match ? match[1].trim() : "";
}

function hasUnsafeWriteSetTerm(value) {
  return /\b(TBD|likely|probably|expected|as needed|related files|etc\.?)\b/i.test(value);
}

function allTextForBundle(bundleDir) {
  return listFiles(bundleDir)
    .filter((file) => /\.(md|json|txt|yaml|yml)$/.test(file))
    .map((file) => readText(file))
    .join("\n");
}

function validateNoSecretLeak(bundleDir, failures) {
  const text = allTextForBundle(bundleDir);
  assert(!/(sk-[A-Za-z0-9]{16,}|api[_-]?key\s*[:=]\s*[A-Za-z0-9_-]{12,}|password\s*[:=]|secret\s*[:=])/i.test(text), failures, "secret_or_credential_leak", "bundle contains a secret-shaped value");
}

function validateRequiredBundleFiles(bundleDir, failures) {
  for (const rel of REQUIRED_BUNDLE_FILES) {
    assert(exists(path.join(bundleDir, rel)), failures, "stale_or_unprovenanced_output", `${rel} is required`);
  }
}

function validatePredecessor(ctx, failures) {
  const summaryPath = path.join(ctx.repoRoot, DWT_S2_SUMMARY);
  const manifestPath = path.join(ctx.repoRoot, DWT_S2_MANIFEST);
  assert(exists(summaryPath), failures, "missing_or_invalid_dwt_s2_dependency_evidence", "retained DWT-S2 summary is missing");
  assert(exists(manifestPath), failures, "missing_or_invalid_dwt_s2_dependency_evidence", "retained DWT-S2 manifest is missing");
  if (!exists(summaryPath) || !exists(manifestPath)) {
    return null;
  }
  const summary = readJson(summaryPath);
  const manifest = readJson(manifestPath);
  assert(summary.runner_mode === "promptfoo-codex", failures, "missing_or_invalid_dwt_s2_dependency_evidence", "DWT-S2 runner_mode must be promptfoo-codex");
  assert(summary.agent_execution_status === "ran-target", failures, "missing_or_invalid_dwt_s2_dependency_evidence", "DWT-S2 agent execution must be ran-target");
  assert(summary.overall_agent_proof_status === "pass", failures, "missing_or_invalid_dwt_s2_dependency_evidence", "DWT-S2 proof must pass");
  assert(manifest.proof_status && manifest.proof_status.agent_execution_status === "ran-target", failures, "missing_or_invalid_dwt_s2_dependency_evidence", "DWT-S2 manifest proof status must be ran-target");
  assert(Boolean(manifest.sha256 && manifest.sha256["dwt-s2-l2-summary.json"]), failures, "missing_or_invalid_dwt_s2_dependency_evidence", "DWT-S2 manifest must retain summary sha");
  return {
    summary_path: DWT_S2_SUMMARY,
    manifest_path: DWT_S2_MANIFEST,
    runner_mode: summary.runner_mode,
    agent_execution_status: summary.agent_execution_status,
    overall_agent_proof_status: summary.overall_agent_proof_status,
    manifest_sha_present: Boolean(manifest.sha256 && manifest.sha256["dwt-s2-l2-summary.json"]),
    summary_sha256: sha256(summaryPath)
  };
}

function validateManifest(bundleDir, failures) {
  const manifest = readJson(path.join(bundleDir, "source-manifest.json"));
  assert(manifest.fixture_id, failures, "stale_or_unprovenanced_output", "fixture_id is required");
  assert(manifest.source_child_spec_path && manifest.source_child_spec_path.includes("DWT-S3"), failures, "stale_or_unprovenanced_output", "source child spec must be DWT-S3");
  assert(manifest.source_handoff_path === CURRENT_HANDOFF, failures, "stale_or_unprovenanced_output", "source handoff must be current DWT-S3 handoff");
  assert(manifest.retained_dwt_s2_summary_path === DWT_S2_SUMMARY, failures, "stale_or_unprovenanced_output", "retained DWT-S2 summary path must be explicit");
  assert(Array.isArray(manifest.generated_artifacts) && manifest.generated_artifacts.includes("delivery-kickoff.md"), failures, "stale_or_unprovenanced_output", "generated artifacts must include delivery-kickoff.md");
  assert(Array.isArray(manifest.normalizations), failures, "stale_or_unprovenanced_output", "normalizations must be declared");
  return manifest;
}

function validateKickoff(bundleDir, failures) {
  const kickoff = readText(path.join(bundleDir, "delivery-kickoff.md"));
  const target = field(kickoff, "target_workspace");
  const runDir = path.dirname(path.dirname(path.dirname(bundleDir)));
  assert(field(kickoff, "child_id") === "DWT-S3", failures, "delivery_not_limited_to_dwt_s3", "kickoff child_id must be DWT-S3");
  assert(field(kickoff, "handoff_path") === CURRENT_HANDOFF, failures, "stale_or_mismatched_dwt_s3_handoff", "kickoff must use current DWT-S3 handoff");
  assert(field(kickoff, "handoff_current") === "true", failures, "stale_or_mismatched_dwt_s3_handoff", "handoff_current must be true");
  assert(field(kickoff, "readiness_verdict") === "IMPLEMENTATION READY", failures, "stale_or_mismatched_dwt_s3_handoff", "readiness verdict must be implementation-ready");
  assert(path.isAbsolute(target), failures, "missing_target_workspace", "target workspace must be absolute");
  assert(target.startsWith(`${runDir}${path.sep}`), failures, "target_workspace_not_isolated", "target workspace must be under the isolated run directory");
  assert(field(kickoff, "target_workspace_isolated") === "true", failures, "target_workspace_not_isolated", "target_workspace_isolated must be true");
  assert(field(kickoff, "allowed_write_set_concrete") === "true", failures, "approximate_or_mismatched_write_set", "allowed write-set must be concrete");
  assert(!hasUnsafeWriteSetTerm(kickoff), failures, "approximate_or_mismatched_write_set", "allowed write-set contains unsafe approximate wording");
  for (const allowed of ALLOWED_WRITE_SET) {
    assert(kickoff.includes(allowed), failures, "approximate_or_mismatched_write_set", `kickoff missing allowed write-set entry: ${allowed}`);
  }
  assert(kickoff.includes(DWT_S2_SUMMARY) && kickoff.includes(DWT_S2_MANIFEST), failures, "missing_or_invalid_dwt_s2_dependency_evidence", "kickoff must cite retained DWT-S2 evidence");
  assert(field(kickoff, "dwt_s5_delivery_started") === "false", failures, "dwt_s5_released_without_own_gate", "DWT-S5 delivery must not start");
  assert(field(kickoff, "forbidden_actions") === "false", failures, "forbidden_runtime_or_repo_write", "forbidden actions must be false");
}

function validateCloseout(bundleDir, failures) {
  const closeout = readText(path.join(bundleDir, "closeout-sync.md"));
  const after = readText(path.join(bundleDir, "child-index-after.md"));
  assert(field(closeout, "child_id") === "DWT-S3", failures, "delivery_not_limited_to_dwt_s3", "closeout child_id must be DWT-S3");
  assert(field(closeout, "dwt_s3_closeout_sync") === "true", failures, "missing_closeout_evidence_sync", "DWT-S3 closeout sync must be true");
  assert(field(closeout, "evidence_links_synced") === "true", failures, "missing_closeout_evidence_sync", "DWT-S3 evidence links must be synced");
  assert(field(closeout, "openspec_ledger_synced") === "true", failures, "missing_openspec_ledger_sync", "OpenSpec ledger sync must be visible");
  for (const coverage of PARENT_COVERAGE) {
    assert(closeout.includes(coverage) && after.includes(coverage), failures, "closeout_parent_coverage_loss", `${coverage} coverage must remain visible`);
  }
  assert(closeout.includes(DWT_S2_SUMMARY), failures, "missing_closeout_evidence_sync", "retained DWT-S2 evidence must stay cited");
  assert(field(closeout, "dwt_s2_evidence_relabelled") === "false", failures, "missing_closeout_evidence_sync", "DWT-S2 evidence must not be relabelled");
  assert(field(closeout, "dwt_s5_state") === "blocked_by_dependency", failures, "dwt_s5_released_without_own_gate", "DWT-S5 must remain blocked_by_dependency");
  assert(field(closeout, "dwt_s5_next_action") !== "spec-change-delivery", failures, "dwt_s5_released_without_own_gate", "DWT-S5 must not name spec-change-delivery");
  assert(/DWT-S3.*(ACCEPTED|CLOSED|IMPLEMENTED)/i.test(after), failures, "missing_closeout_evidence_sync", "child index after must show DWT-S3 closed/accepted/implemented");
  assert(/DWT-S5.*(BLOCKED BY DEPENDENCY|blocked_by_dependency)/i.test(after), failures, "dwt_s5_released_without_own_gate", "child index after must show DWT-S5 blocked");
}

function validateSummaryShape(summary, failures) {
  assert(summary.schema_id === "docworkflow-agent-delivery-summary.v1", failures, "invalid_dwt_s4_summary_or_telemetry", "summary schema_id must be v1");
  assert(summary.suite_level === "DWT-S3", failures, "invalid_dwt_s4_summary_or_telemetry", "suite_level must be DWT-S3");
  assert(typeof summary.suite_version === "string" && summary.suite_version.length > 0, failures, "invalid_dwt_s4_summary_or_telemetry", "suite_version must exist");
  assert(path.isAbsolute(summary.repo_root || "") || summary.repo_root === "planned", failures, "invalid_dwt_s4_summary_or_telemetry", "repo_root must be absolute or planned");
  assert(path.isAbsolute(summary.fixture_root || "") || summary.fixture_root === "planned", failures, "invalid_dwt_s4_summary_or_telemetry", "fixture_root must be absolute or planned");
  assert(summary.runner_mode === "promptfoo-codex" || summary.runner_mode === "fallback-artifact", failures, "invalid_dwt_s4_summary_or_telemetry", "runner_mode must be frozen");
  assert(AGENT_STATUS.has(summary.agent_execution_status), failures, "invalid_dwt_s4_summary_or_telemetry", "agent_execution_status must be frozen");
  assert(["pass", "blocked", "fail"].includes(summary.overall_agent_proof_status), failures, "invalid_dwt_s4_summary_or_telemetry", "overall proof status must be frozen");
  assert(isObject(summary.predecessor_evidence), failures, "missing_or_invalid_dwt_s2_dependency_evidence", "predecessor_evidence must exist");
  assert(isObject(summary.test_results), failures, "invalid_dwt_s4_summary_or_telemetry", "test_results must exist");
  assert(isObject(summary.harness_case_results), failures, "invalid_dwt_s4_summary_or_telemetry", "harness_case_results must exist");
  assert(isObject(summary.evidence_truth), failures, "invalid_evidence_truth", "evidence_truth must exist");
  for (const [caseId, status] of Object.entries(summary.test_results || {})) {
    assert(STATUS.has(status), failures, "invalid_dwt_s4_summary_or_telemetry", `${caseId} status is invalid`);
    assert(TRUTH.has(summary.evidence_truth && summary.evidence_truth[caseId]), failures, "invalid_evidence_truth", `${caseId} evidence truth is invalid`);
  }
  assert(isObject(summary.evidence_links), failures, "invalid_dwt_s4_summary_or_telemetry", "evidence_links must exist");
  assert(isObject(summary.runner_environment), failures, "invalid_dwt_s4_summary_or_telemetry", "runner_environment must exist");
  assert(isObject(summary.provenance_checks), failures, "invalid_dwt_s4_summary_or_telemetry", "provenance_checks must exist");
  assert(isObject(summary.readiness_checks), failures, "invalid_dwt_s4_summary_or_telemetry", "readiness_checks must exist");
  assert(isObject(summary.closeout_checks), failures, "invalid_dwt_s4_summary_or_telemetry", "closeout_checks must exist");
  assert(isObject(summary.style_verdicts), failures, "invalid_dwt_s4_summary_or_telemetry", "style_verdicts must exist");
  assert(isObject(summary.telemetry_verdicts), failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry_verdicts must exist");
  assert(Array.isArray(summary.forbidden_actions_observed), failures, "invalid_dwt_s4_summary_or_telemetry", "forbidden actions must be an array");
  assert(summary.downstream_children && summary.downstream_children["DWT-S5"] === "blocked_by_dependency", failures, "dwt_s5_released_without_own_gate", "DWT-S5 downstream state must remain blocked_by_dependency");
  for (const verdict of Object.values(summary.style_verdicts || {})) {
    assert(STYLE.has(verdict), failures, "invalid_dwt_s4_summary_or_telemetry", `invalid style verdict ${verdict}`);
  }
  for (const verdict of Object.values(summary.telemetry_verdicts || {})) {
    assert(TELEMETRY.has(verdict), failures, "invalid_dwt_s4_summary_or_telemetry", `invalid telemetry verdict ${verdict}`);
  }
  if (summary.agent_execution_status !== "ran-target") {
    assert(summary.overall_agent_proof_status === "blocked", failures, "blocked_agent_misreported_as_pass", "blocked agent proof must report overall blocked");
  }
}

function validateTelemetryManifest(manifest, failures) {
  assert(typeof manifest.manifest_version === "string" && manifest.manifest_version.startsWith("docworkflow-agent-delivery-telemetry.v1"), failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry version must be v1");
  assert(manifest.child_id === "DWT-S3", failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry child_id must be DWT-S3");
  assert(Array.isArray(manifest.commands), failures, "invalid_dwt_s4_summary_or_telemetry", "commands must be an array");
  assert(isObject(manifest.file_reads), failures, "invalid_dwt_s4_summary_or_telemetry", "file_reads must exist");
  assert(isObject(manifest.tool_calls), failures, "invalid_dwt_s4_summary_or_telemetry", "tool_calls must exist");
  assert(Array.isArray(manifest.forbidden_command_classes), failures, "invalid_dwt_s4_summary_or_telemetry", "forbidden command classes must be an array");
  assert(isObject(manifest.budget), failures, "invalid_dwt_s4_summary_or_telemetry", "budget must exist");
  assert(TELEMETRY.has(manifest.efficiency_verdict), failures, "invalid_dwt_s4_summary_or_telemetry", "efficiency verdict must use frozen vocabulary");
  const observedForbidden = [];
  for (const command of manifest.commands || []) {
    assert(typeof command.command_class === "string", failures, "invalid_dwt_s4_summary_or_telemetry", "command_class must exist");
    assert(TRUTH.has(command.evidence_truth), failures, "invalid_evidence_truth", "command evidence truth must use frozen vocabulary");
    if (FORBIDDEN_COMMANDS.has(command.command_class)) {
      observedForbidden.push(command.command_class);
    }
  }
  if (observedForbidden.length > 0) {
    assert(manifest.efficiency_verdict === "fail", failures, "forbidden_runtime_or_repo_write", "forbidden commands require fail verdict");
  }
  const broadReads = Number(manifest.file_reads.broad_scan_count || 0);
  const maxBroadReads = Number(manifest.budget.max_broad_reads || 0);
  const hasJustification = Array.isArray(manifest.justifications) && manifest.justifications.length > 0;
  if (broadReads > maxBroadReads) {
    assert(hasJustification, failures, "invalid_dwt_s4_summary_or_telemetry", "broad read drift requires justification");
    assert(manifest.efficiency_verdict === "warn", failures, "invalid_dwt_s4_summary_or_telemetry", "justified broad read drift must warn");
  }
}

function validateBundle(ctx, bundleDir) {
  const failures = [];
  validateRequiredBundleFiles(bundleDir, failures);
  if (failures.length > 0) {
    return failures;
  }
  validateNoSecretLeak(bundleDir, failures);
  validatePredecessor(ctx, failures);
  validateManifest(bundleDir, failures);
  validateKickoff(bundleDir, failures);
  validateCloseout(bundleDir, failures);
  validateTelemetryManifest(readJson(path.join(bundleDir, "agent-run-manifest.json")), failures);
  validateSummaryShape(readJson(path.join(bundleDir, "evidence/dwt-s3-l2-summary.json")), failures);
  return failures;
}

function validateExpectedBundle(ctx, fixtureName) {
  const bundle = materializeBundle(ctx, fixtureName);
  return {
    bundle,
    failures: validateBundle(ctx, bundle)
  };
}

function outcome(ctx, caseId, expectedFixtureStatus, harnessPassed, details) {
  const payload = {
    case_id: caseId,
    expected_fixture_status: expectedFixtureStatus,
    harness_status: harnessPassed ? "pass" : "fail",
    evidence_truth: caseId === "DWT-S3-L2E" ? "blocked" : "ran-target",
    ...details
  };
  writeEvidence(ctx.evidence, CASES[caseId], payload);
  return payload;
}

function runL2A(ctx) {
  const result = validateExpectedBundle(ctx, "dwt-s3-ready-kickoff");
  const outside = validateExpectedBundle(ctx, "out-of-workspace-write-attempt");
  const outsideBlocked = outside.failures.some((failure) => failure.code === "target_workspace_not_isolated" || failure.code === "forbidden_runtime_or_repo_write");
  return outcome(ctx, "DWT-S3-L2A", "pass", result.failures.length === 0 && outsideBlocked, {
    output_bundle: result.bundle,
    isolation_negative_bundle: outside.bundle,
    isolation_negative_blocked: outsideBlocked,
    failures: result.failures,
    isolation_negative_failures: outside.failures
  });
}

function runL2B(ctx) {
  const result = validateExpectedBundle(ctx, "stale-dwt-s3-handoff");
  const blocker = result.failures.some((failure) => failure.code === "stale_or_mismatched_dwt_s3_handoff" || failure.code === "missing_target_workspace" || failure.code === "approximate_or_mismatched_write_set");
  return outcome(ctx, "DWT-S3-L2B", "blocked", blocker, {
    output_bundle: result.bundle,
    expected_blocker_detected: blocker,
    failures: result.failures
  });
}

function runL2C(ctx) {
  const result = validateExpectedBundle(ctx, "closeout-sync-positive");
  return outcome(ctx, "DWT-S3-L2C", "pass", result.failures.length === 0, {
    output_bundle: result.bundle,
    failures: result.failures
  });
}

function runL2D(ctx) {
  const result = validateExpectedBundle(ctx, "dwt-s5-auto-release-attempt");
  const blocked = result.failures.some((failure) => failure.code === "dwt_s5_released_without_own_gate");
  return outcome(ctx, "DWT-S3-L2D", "blocked", blocked, {
    output_bundle: result.bundle,
    expected_blocker_detected: blocked,
    failures: result.failures
  });
}

function runL2E(ctx) {
  const result = validateExpectedBundle(ctx, "blocked-agent-output");
  const summary = readJson(path.join(result.bundle, "evidence/dwt-s3-l2-summary.json"));
  const blocked = summary.runner_mode === "fallback-artifact"
    && summary.agent_execution_status !== "ran-target"
    && summary.overall_agent_proof_status === "blocked"
    && !result.failures.some((failure) => failure.code === "blocked_agent_misreported_as_pass");
  return outcome(ctx, "DWT-S3-L2E", "blocked", blocked, {
    output_bundle: result.bundle,
    runner_mode: summary.runner_mode,
    agent_execution_status: summary.agent_execution_status,
    failures: result.failures
  });
}

function runL2F(ctx) {
  const result = validateExpectedBundle(ctx, "style-efficiency-output");
  const summary = readJson(path.join(result.bundle, "evidence/dwt-s3-l2-summary.json"));
  const warnOrPass = ["pass", "warn"].includes(summary.test_results["DWT-S3-L2F"]);
  return outcome(ctx, "DWT-S3-L2F", summary.test_results["DWT-S3-L2F"], result.failures.length === 0 && warnOrPass, {
    output_bundle: result.bundle,
    style_verdicts: summary.style_verdicts,
    telemetry_verdicts: summary.telemetry_verdicts,
    failures: result.failures
  });
}

function classifyPromptfooBlocker(text) {
  if (/401 Unauthorized|Missing bearer|basic authentication|auth/i.test(text)) {
    return "blocked_auth";
  }
  if (/network|ETIMEDOUT|ECONNRESET|ENOTFOUND|fetch failed/i.test(text)) {
    return "blocked_network";
  }
  if (/provider|model|openai:codex-sdk/i.test(text)) {
    return "blocked_provider";
  }
  if (/ENOENT|Cannot find module|command not found|spawn|disabled/i.test(text)) {
    return "blocked_runtime";
  }
  return "failed";
}

function promptfooResultFromEval(evalJson) {
  const results = evalJson && evalJson.results && Array.isArray(evalJson.results.results)
    ? evalJson.results.results
    : [];
  return results[0] || null;
}

function getAgentEvidence(ctx) {
  const evalPath = process.env.DWT_S3_PROMPTFOO_EVAL_JSON || "";
  const logPath = process.env.DWT_S3_PROMPTFOO_EVAL_LOG || "";
  const exitStatus = process.env.DWT_S3_PROMPTFOO_EXIT_STATUS || "not-run";
  const authStatus = process.env.DWT_S3_PROMPTFOO_AUTH_STATUS || "missing";
  const evidence = {
    runner_mode: evalPath ? "promptfoo-codex" : "fallback-artifact",
    agent_execution_status: evalPath ? "failed" : "blocked_runtime",
    overall_agent_proof_status: "blocked",
    promptfoo_eval_json: evalPath || null,
    promptfoo_eval_log: logPath || null,
    promptfoo_exit_status: exitStatus,
    promptfoo_version: process.env.DWT_S3_PROMPTFOO_VERSION || "not-run",
    auth_status: authStatus,
    session_id_present: false,
    assertion_status: "not-run",
    output_contract_status: "not-run",
    failure_reason: evalPath ? null : "Promptfoo/Codex agent run was not requested or not provisioned; fallback artifact validation only."
  };
  if (!evalPath) {
    writeEvidence(ctx.evidence, "dwt-s3-agent-proof.json", evidence);
    return evidence;
  }
  const evalJson = exists(evalPath) ? readJson(evalPath) : null;
  const logText = logPath && exists(logPath) ? readText(logPath) : "";
  if (!evalJson) {
    evidence.agent_execution_status = classifyPromptfooBlocker(logText);
    evidence.failure_reason = "Promptfoo eval JSON is missing or invalid.";
    writeEvidence(ctx.evidence, "dwt-s3-agent-proof.json", evidence);
    return evidence;
  }
  const result = promptfooResultFromEval(evalJson);
  const output = result && result.response ? String(result.response.output || "") : "";
  const required = [
    "DWT-S3 Delivery Kickoff",
    "DWT-S3 Closeout Sync",
    "Parent Coverage",
    "DWT-S5 State",
    "FINAL_STATUS:"
  ];
  const missing = required.filter((value) => !output.includes(value));
  const finalStatusOk = /child_id=DWT-S3/.test(output)
    && /handoff_current=true/.test(output)
    && /target_workspace_isolated=true/.test(output)
    && /dwt_s5_state=blocked_by_dependency/.test(output)
    && /dwt_s5_delivery_started=false/.test(output)
    && /forbidden_actions=false/.test(output);
  evidence.session_id_present = Boolean(result && result.response && result.response.sessionId);
  evidence.assertion_status = result && result.success === true ? "pass" : "fail";
  evidence.output_contract_status = missing.length === 0 && finalStatusOk ? "pass" : "fail";
  evidence.agent_execution_status = evidence.session_id_present || output.length > 0
    ? "ran-target"
    : classifyPromptfooBlocker(`${result && result.failureReason || ""}\n${logText}`);
  evidence.failure_reason = missing.length > 0 ? `Missing output markers: ${missing.join(", ")}` : result && result.failureReason || null;
  if (
    evidence.agent_execution_status === "ran-target"
    && evidence.assertion_status === "pass"
    && evidence.output_contract_status === "pass"
    && String(exitStatus) === "0"
  ) {
    evidence.overall_agent_proof_status = "pass";
  } else if (evidence.agent_execution_status === "ran-target") {
    evidence.overall_agent_proof_status = "fail";
  }
  writeEvidence(ctx.evidence, "dwt-s3-agent-proof.json", evidence);
  return evidence;
}

function writeSummary(ctx, results, selector) {
  const predecessorFailures = [];
  const predecessor = validatePredecessor(ctx, predecessorFailures);
  const byCase = Object.fromEntries(results.map((result) => [result.case_id, result]));
  const agentProof = getAgentEvidence(ctx);
  const evidenceLinks = Object.fromEntries(Object.entries(CASES).map(([caseId, file]) => [caseId, path.join(ctx.evidence, file)]));
  evidenceLinks.agent_proof = path.join(ctx.evidence, "dwt-s3-agent-proof.json");
  if (agentProof.promptfoo_eval_json) {
    evidenceLinks.promptfoo_eval = agentProof.promptfoo_eval_json;
  }
  if (agentProof.promptfoo_eval_log) {
    evidenceLinks.promptfoo_log = agentProof.promptfoo_eval_log;
  }
  const testResults = {};
  const harnessResults = {};
  const truth = {};
  for (const caseId of Object.keys(CASES)) {
    testResults[caseId] = byCase[caseId] ? byCase[caseId].expected_fixture_status : "planned";
    harnessResults[caseId] = byCase[caseId] ? byCase[caseId].harness_status : "planned";
    truth[caseId] = byCase[caseId] ? byCase[caseId].evidence_truth : "planned";
  }
  const summary = {
    schema_id: "docworkflow-agent-delivery-summary.v1",
    suite_level: "DWT-S3",
    suite_version: "DWT-S3-l2-single-child-closeout-v1",
    repo_root: ctx.repoRoot,
    fixture_root: ctx.runDir,
    fixture_manifest: path.join(ctx.evidence, "output-bundles", "dwt-s3-ready-kickoff", "source-manifest.json"),
    runner_mode: agentProof.runner_mode,
    agent_execution_status: agentProof.agent_execution_status,
    overall_agent_proof_status: agentProof.overall_agent_proof_status,
    selector,
    predecessor_evidence: predecessor || { failures: predecessorFailures },
    test_results: testResults,
    harness_case_results: harnessResults,
    evidence_truth: truth,
    evidence_links: evidenceLinks,
    runner_environment: {
      os: `${os.type()} ${os.release()}`,
      shell: process.env.SHELL || "unknown",
      node: process.version,
      promptfoo: agentProof.promptfoo_version,
      credentials_provisioned: agentProof.auth_status !== "missing",
      requires_agents_for_acceptance: true,
      requires_docker: false
    },
    agent_proof: {
      assertion_status: agentProof.assertion_status,
      output_contract_status: agentProof.output_contract_status,
      session_id_present: agentProof.session_id_present,
      promptfoo_exit_status: agentProof.promptfoo_exit_status,
      failure_reason: agentProof.failure_reason
    },
    provenance_checks: {
      retained_dwt_s2_identity: predecessorFailures.length === 0 ? "pass" : "fail",
      source_manifest_present: byCase["DWT-S3-L2A"] ? "pass" : "planned",
      no_stale_output_reuse: byCase["DWT-S3-L2B"] && byCase["DWT-S3-L2B"].harness_status === "pass" ? "pass" : "planned"
    },
    readiness_checks: {
      child_index_row: byCase["DWT-S3-L2A"] && byCase["DWT-S3-L2A"].harness_status === "pass" ? "pass" : "planned",
      handoff_current: byCase["DWT-S3-L2A"] && byCase["DWT-S3-L2A"].harness_status === "pass" ? "pass" : "planned",
      stale_handoff_blocked: byCase["DWT-S3-L2B"] && byCase["DWT-S3-L2B"].harness_status === "pass" ? "blocked" : "planned",
      write_set_concrete: byCase["DWT-S3-L2A"] && byCase["DWT-S3-L2A"].harness_status === "pass" ? "pass" : "planned",
      target_workspace_isolated: byCase["DWT-S3-L2A"] && byCase["DWT-S3-L2A"].harness_status === "pass" ? "pass" : "planned"
    },
    closeout_checks: {
      parent_coverage_preserved: byCase["DWT-S3-L2C"] && byCase["DWT-S3-L2C"].harness_status === "pass" ? "pass" : "planned",
      evidence_link_sync: byCase["DWT-S3-L2C"] && byCase["DWT-S3-L2C"].harness_status === "pass" ? "pass" : "planned",
      openspec_ledger_sync: byCase["DWT-S3-L2C"] && byCase["DWT-S3-L2C"].harness_status === "pass" ? "pass" : "planned",
      dwt_s5_blocked_state: byCase["DWT-S3-L2D"] && byCase["DWT-S3-L2D"].harness_status === "pass" ? "blocked" : "planned"
    },
    style_verdicts: {
      "DWT-S3-L2A": byCase["DWT-S3-L2A"] ? "pass" : "planned",
      "DWT-S3-L2B": byCase["DWT-S3-L2B"] ? "pass" : "planned",
      "DWT-S3-L2C": byCase["DWT-S3-L2C"] ? "pass" : "planned",
      "DWT-S3-L2D": byCase["DWT-S3-L2D"] ? "pass" : "planned",
      "DWT-S3-L2E": byCase["DWT-S3-L2E"] ? "warn" : "planned",
      "DWT-S3-L2F": byCase["DWT-S3-L2F"] ? "pass" : "planned"
    },
    telemetry_verdicts: {
      "DWT-S3-L2A": byCase["DWT-S3-L2A"] ? "pass" : "planned",
      "DWT-S3-L2B": byCase["DWT-S3-L2B"] ? "pass" : "planned",
      "DWT-S3-L2C": byCase["DWT-S3-L2C"] ? "pass" : "planned",
      "DWT-S3-L2D": byCase["DWT-S3-L2D"] ? "pass" : "planned",
      "DWT-S3-L2E": byCase["DWT-S3-L2E"] ? "blocked" : "planned",
      "DWT-S3-L2F": byCase["DWT-S3-L2F"] ? "warn" : "planned"
    },
    forbidden_actions_observed: [],
    downstream_children: {
      "DWT-S5": "blocked_by_dependency"
    }
  };
  return writeEvidence(ctx.evidence, "dwt-s3-l2-summary.json", summary);
}

function runValidateOutput(ctx) {
  if (!ctx.outputBundle) {
    throw new Error("validate-output requires --output-bundle DIR");
  }
  const failures = validateBundle(ctx, ctx.outputBundle);
  const payload = {
    case_id: "DWT-S3-VALIDATE-OUTPUT",
    expected_fixture_status: "pass",
    harness_status: failures.length === 0 ? "pass" : "fail",
    evidence_truth: "ran-target",
    output_bundle: ctx.outputBundle,
    failures
  };
  writeEvidence(ctx.evidence, "dwt-s3-validate-output.json", payload);
  return [payload];
}

function runAgent(ctx) {
  const proof = getAgentEvidence(ctx);
  const payload = {
    case_id: "DWT-S3-AGENT",
    expected_fixture_status: proof.overall_agent_proof_status === "pass" ? "pass" : "blocked",
    harness_status: proof.overall_agent_proof_status === "pass" ? "pass" : "fail",
    evidence_truth: proof.agent_execution_status === "ran-target" ? "ran-target" : "blocked",
    runner_mode: proof.runner_mode,
    agent_execution_status: proof.agent_execution_status,
    overall_agent_proof_status: proof.overall_agent_proof_status,
    failure_reason: proof.failure_reason
  };
  writeEvidence(ctx.evidence, "dwt-s3-agent-result.json", payload);
  return [payload];
}

function main() {
  const args = parseArgs(process.argv);
  ensureDir(args.evidence);
  const runners = {
    all: [runL2A, runL2B, runL2C, runL2D, runL2E, runL2F],
    fallback: [runL2A, runL2B, runL2C, runL2D, runL2E, runL2F],
    closeout: [runL2C, runL2D],
    style: [runL2F],
    telemetry: [runL2E, runL2F]
  };

  let results;
  if (args.selector === "validate-output") {
    results = runValidateOutput(args);
  } else if (args.selector === "agent") {
    results = runAgent(args);
  } else if (runners[args.selector]) {
    results = runners[args.selector].map((runner) => runner(args));
  } else {
    throw new Error(`Unknown selector: ${args.selector}`);
  }

  const summaryPath = writeSummary(args, results, args.selector);
  for (const result of results) {
    console.log(`${result.harness_status.toUpperCase()}: ${result.case_id} expected fixture ${result.expected_fixture_status}`);
  }
  console.log(`SUMMARY: ${summaryPath}`);

  const failures = results.filter((result) => result.harness_status !== "pass");
  if (args.selector === "agent") {
    const agent = results[0];
    if (agent.overall_agent_proof_status !== "pass") {
      failures.push(agent);
    }
  }
  if (failures.length > 0) {
    console.error(JSON.stringify({ status: "fail", failures }, null, 2));
    process.exit(1);
  }
}

main();
