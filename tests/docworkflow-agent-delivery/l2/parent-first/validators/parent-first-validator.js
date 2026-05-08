#!/usr/bin/env node
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");

const CASES = {
  "DWT-S2-L2A": "dwt-s2-l2a-parent-first.json",
  "DWT-S2-L2B": "dwt-s2-l2b-control-surface.json",
  "DWT-S2-L2C": "dwt-s2-l2c-thin-child-block.json",
  "DWT-S2-L2D": "dwt-s2-l2d-next-state.json",
  "DWT-S2-L2E": "dwt-s2-l2e-blocked-agent.json",
  "DWT-S2-L2F": "dwt-s2-l2f-reporting-telemetry.json"
};

const CHILD_INDEX_HEADER = "| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |";
const STATUS = new Set(["pass", "fail", "blocked", "warn", "planned"]);
const TRUTH = new Set(["ran-target", "ran-rehearsal", "blocked", "failed", "planned", "dry-run"]);
const AGENT_STATUS = new Set(["ran-target", "blocked_auth", "blocked_provider", "blocked_network", "blocked_runtime", "failed", "not-run"]);
const NEXT_STATES = new Set(["ready_for_hardening", "implementation_ready", "blocked_by_dependency", "needs_user_decision", "needs_hardening"]);
const FORBIDDEN = new Set(["docker", "runtime-build", "runtime-test", "credential-copy", "ki-fuer-kmu-write", "deployment"]);
const STYLE = new Set(["pass", "fail", "warn"]);
const TELEMETRY = new Set(["pass", "fail", "warn", "blocked"]);

function usage() {
  console.error("Usage: parent-first-validator.js --fixtures DIR --evidence DIR --repo-root DIR [--selector all|fallback|agent|validate-output|style|telemetry] [--output-bundle DIR]");
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
    outputBundle: args.outputBundle ? path.resolve(args.outputBundle) : null
  };
}

function readText(file) {
  return fs.readFileSync(file, "utf8");
}

function readJson(file) {
  return JSON.parse(readText(file));
}

function tryReadJson(file) {
  try {
    return readJson(file);
  } catch (error) {
    return null;
  }
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
  fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
  return file;
}

function promptfooResultFromEval(evalJson) {
  const results = evalJson && evalJson.results && Array.isArray(evalJson.results.results)
    ? evalJson.results.results
    : [];
  return results[0] || null;
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
  if (/ENOENT|Cannot find module|command not found|spawn/i.test(text)) {
    return "blocked_runtime";
  }
  return "failed";
}

function persistPromptfooEvidence(ctx, evidence) {
  writeEvidence(ctx.evidence, "dwt-s2-agent-proof.json", evidence);
  return evidence;
}

function getPromptfooEvidence(ctx) {
  const evalPath = process.env.DWT_S2_PROMPTFOO_EVAL_JSON || "";
  const logPath = process.env.DWT_S2_PROMPTFOO_EVAL_LOG || "";
  const exitStatus = process.env.DWT_S2_PROMPTFOO_EXIT_STATUS || "not-run";
  const authStatus = process.env.DWT_S2_PROMPTFOO_AUTH_STATUS || "missing";
  const evidence = {
    runner_mode: evalPath ? "promptfoo-codex" : "fallback-artifact",
    agent_execution_status: "not-run",
    overall_agent_proof_status: "blocked",
    promptfoo_eval_json: evalPath || null,
    promptfoo_eval_log: logPath || null,
    promptfoo_exit_status: exitStatus,
    promptfoo_version: process.env.DWT_S2_PROMPTFOO_VERSION || "not-run",
    auth_status: authStatus,
    session_id_present: false,
    assertion_status: "not-run",
    output_contract_status: "not-run",
    failure_reason: null
  };

  if (!evalPath) {
    evidence.agent_execution_status = authStatus === "missing" ? "blocked_auth" : "not-run";
    return persistPromptfooEvidence(ctx, evidence);
  }

  const evalJson = exists(evalPath) ? tryReadJson(evalPath) : null;
  const logText = logPath && exists(logPath) ? readText(logPath) : "";
  if (!evalJson) {
    evidence.agent_execution_status = classifyPromptfooBlocker(logText);
    evidence.failure_reason = "Promptfoo eval JSON is missing or invalid.";
    return persistPromptfooEvidence(ctx, evidence);
  }

  const result = promptfooResultFromEval(evalJson);
  const output = result && result.response ? String(result.response.output || "") : "";
  const hasFinalStatus = output.includes("FINAL_STATUS:") || /\*\*Final Status\*\*/.test(output);
  const implementationBlocked = /implementation_allowed=false/.test(output)
    || /implementation_allowed:\s*false/i.test(output)
    || /Implementation permission:\s*`?BLOCKED/i.test(output)
    || /RUNTIME_IMPLEMENTATION=FORBIDDEN_NOT_ATTEMPTED/.test(output);
  const writesBlocked = /writes_performed=false/.test(output)
    || /not written to disk/i.test(output)
    || /WRITES_BLOCKED_READ_ONLY/.test(output)
    || /ARTIFACT_PERSISTENCE=BLOCKED_READ_ONLY_WORKSPACE/.test(output);
  evidence.session_id_present = Boolean(result && result.response && result.response.sessionId);
  evidence.assertion_status = result && result.success === true ? "pass" : "fail";
  evidence.output_contract_status = output.includes("Child Index")
    && output.includes("Coverage Matrix")
    && output.includes("Dependencies")
    && output.includes("Hardening Queue")
    && hasFinalStatus
    && implementationBlocked
    && writesBlocked
    ? "pass"
    : "fail";
  evidence.promptfoo_eval_id = evalJson.evalId || null;
  evidence.promptfoo_shareable_url = evalJson.shareableUrl || null;
  evidence.promptfoo_cost = result && typeof result.cost === "number" ? result.cost : null;
  evidence.promptfoo_token_usage = result && result.response ? result.response.tokenUsage || null : null;
  evidence.agent_execution_status = evidence.session_id_present || output.length > 0
    ? "ran-target"
    : classifyPromptfooBlocker(`${result && result.failureReason || ""}\n${logText}`);
  evidence.failure_reason = result && result.gradingResult && result.gradingResult.reason
    ? result.gradingResult.reason
    : result && result.failureReason
      ? String(result.failureReason)
      : null;

  if (
    evidence.agent_execution_status === "ran-target"
    && evidence.assertion_status === "pass"
    && evidence.output_contract_status === "pass"
    && String(exitStatus) === "0"
  ) {
    evidence.overall_agent_proof_status = "pass";
  } else if (evidence.agent_execution_status === "ran-target") {
    evidence.overall_agent_proof_status = "failed";
  }

  return persistPromptfooEvidence(ctx, evidence);
}

function validateSummaryShape(summary, failures) {
  assert(summary.schema_id === "docworkflow-agent-delivery-summary.v1", failures, "invalid_dwt_s4_summary_or_telemetry", "summary schema_id must be v1");
  assert(summary.suite_level === "DWT-S2", failures, "invalid_dwt_s4_summary_or_telemetry", "suite_level must be DWT-S2");
  assert(typeof summary.suite_version === "string" && summary.suite_version.length > 0, failures, "invalid_dwt_s4_summary_or_telemetry", "suite_version must exist");
  assert(path.isAbsolute(summary.repo_root || "") || summary.repo_root === "planned", failures, "invalid_dwt_s4_summary_or_telemetry", "repo_root must be absolute or planned");
  assert(path.isAbsolute(summary.fixture_root || "") || summary.fixture_root === "planned", failures, "invalid_dwt_s4_summary_or_telemetry", "fixture_root must be absolute or planned");
  assert(summary.runner_mode === "promptfoo-codex" || summary.runner_mode === "fallback-artifact", failures, "invalid_dwt_s4_summary_or_telemetry", "runner_mode must be frozen");
  assert(AGENT_STATUS.has(summary.agent_execution_status), failures, "invalid_dwt_s4_summary_or_telemetry", "agent_execution_status must be frozen");
  assert(isObject(summary.test_results), failures, "invalid_dwt_s4_summary_or_telemetry", "test_results must exist");
  assert(isObject(summary.evidence_truth), failures, "invalid_evidence_truth", "evidence_truth must exist");
  if (isObject(summary.test_results) && isObject(summary.evidence_truth)) {
    for (const [caseId, status] of Object.entries(summary.test_results)) {
      assert(STATUS.has(status), failures, "invalid_dwt_s4_summary_or_telemetry", `${caseId} status is invalid`);
      assert(TRUTH.has(summary.evidence_truth[caseId]), failures, "invalid_evidence_truth", `${caseId} evidence truth is invalid`);
    }
  }
  assert(isObject(summary.evidence_links) || Array.isArray(summary.evidence_links), failures, "invalid_dwt_s4_summary_or_telemetry", "evidence_links must exist");
  assert(isObject(summary.runner_environment), failures, "invalid_dwt_s4_summary_or_telemetry", "runner_environment must exist");
  assert(isObject(summary.provenance_checks), failures, "invalid_dwt_s4_summary_or_telemetry", "provenance_checks must exist");
  assert(isObject(summary.readiness_checks), failures, "invalid_dwt_s4_summary_or_telemetry", "readiness_checks must exist");
  assert(isObject(summary.style_verdicts), failures, "invalid_dwt_s4_summary_or_telemetry", "style_verdicts must exist");
  assert(isObject(summary.telemetry_verdicts), failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry_verdicts must exist");
  assert(Array.isArray(summary.forbidden_actions_observed), failures, "invalid_dwt_s4_summary_or_telemetry", "forbidden_actions_observed must be an array");
  for (const verdict of Object.values(summary.style_verdicts || {})) {
    assert(STYLE.has(verdict), failures, "invalid_dwt_s4_summary_or_telemetry", `invalid style verdict ${verdict}`);
  }
  for (const verdict of Object.values(summary.telemetry_verdicts || {})) {
    assert(TELEMETRY.has(verdict), failures, "invalid_dwt_s4_summary_or_telemetry", `invalid telemetry verdict ${verdict}`);
  }
  if (summary.agent_execution_status !== "ran-target") {
    const values = Object.values(summary.test_results || {});
    assert(values.includes("blocked"), failures, "blocked_agent_misreported_as_pass", "blocked agent summary must expose a blocked test result");
  }
}

function validateTelemetryManifest(manifest, failures) {
  assert(typeof manifest.manifest_version === "string" && manifest.manifest_version.startsWith("docworkflow-agent-delivery-telemetry.v1"), failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry version must be v1");
  assert(manifest.child_id === "DWT-S2", failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry child_id must be DWT-S2");
  assert(Array.isArray(manifest.commands), failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry commands must be an array");
  assert(isObject(manifest.file_reads), failures, "invalid_dwt_s4_summary_or_telemetry", "file_reads must exist");
  assert(isObject(manifest.tool_calls), failures, "invalid_dwt_s4_summary_or_telemetry", "tool_calls must exist");
  assert(Array.isArray(manifest.forbidden_command_classes), failures, "invalid_dwt_s4_summary_or_telemetry", "forbidden classes must exist");
  assert(isObject(manifest.budget), failures, "invalid_dwt_s4_summary_or_telemetry", "budget must exist");
  assert(TELEMETRY.has(manifest.efficiency_verdict), failures, "invalid_dwt_s4_summary_or_telemetry", "efficiency verdict must be frozen");
  const forbiddenSeen = [];
  for (const command of manifest.commands || []) {
    assert(TRUTH.has(command.evidence_truth), failures, "invalid_evidence_truth", "command evidence truth must be frozen");
    if (FORBIDDEN.has(command.command_class)) {
      forbiddenSeen.push(command.command_class);
    }
    for (const value of Object.values(command)) {
      if (typeof value === "string" && /(sk-[a-z0-9]|api[_-]?key|password|secret=)/i.test(value)) {
        failures.push({ code: "secret_or_credential_leak", message: "telemetry contains a secret-shaped value" });
      }
    }
  }
  if (forbiddenSeen.length > 0) {
    assert(manifest.efficiency_verdict === "fail", failures, "forbidden_runtime_or_repo_write", "forbidden command classes require fail verdict");
  }
  const broadReads = Number(manifest.file_reads && manifest.file_reads.broad_scan_count || 0);
  const maxBroadReads = Number(manifest.budget && manifest.budget.max_broad_reads || 0);
  const hasJustification = Array.isArray(manifest.justifications) && manifest.justifications.length > 0;
  if (broadReads > maxBroadReads && !hasJustification) {
    failures.push({ code: "invalid_dwt_s4_summary_or_telemetry", message: "broad read drift needs justification" });
  }
  return forbiddenSeen;
}

function validateBundle(bundleDir, options = {}) {
  const failures = [];
  const required = [
    "source-manifest.json",
    "agent-output.md",
    "child-index.md",
    "coverage-matrix.md",
    "dependencies.md",
    "hardening-queue.md",
    "orchestration-state.json",
    "agent-run-manifest.json",
    "evidence/dwt-s2-l2-summary.json"
  ];
  for (const rel of required) {
    assert(exists(path.join(bundleDir, rel)), failures, "missing_child_control_surface", `${rel} is required`);
  }
  assert(exists(path.join(bundleDir, "child-specs")) && listFiles(path.join(bundleDir, "child-specs")).length > 0, failures, "missing_child_control_surface", "child-specs must contain generated specs");
  if (failures.length > 0) {
    return { failures, forbiddenSeen: [], leading: [] };
  }

  const manifest = readJson(path.join(bundleDir, "source-manifest.json"));
  const index = readText(path.join(bundleDir, "child-index.md"));
  const output = readText(path.join(bundleDir, "agent-output.md"));
  const state = readJson(path.join(bundleDir, "orchestration-state.json"));
  const telemetry = readJson(path.join(bundleDir, "agent-run-manifest.json"));
  const summary = readJson(path.join(bundleDir, "evidence/dwt-s2-l2-summary.json"));

  assert(index.split(/\r?\n/).includes(CHILD_INDEX_HEADER), failures, "invalid_child_index_header", "child index header must be exact");
  assert(/DWT-C[0-9]/.test(index), failures, "missing_child_control_surface", "child index must include generated children");
  assert(readText(path.join(bundleDir, "coverage-matrix.md")).includes("DWT-PR1"), failures, "missing_coverage_matrix", "coverage matrix must map DWT-PR1");
  assert(readText(path.join(bundleDir, "dependencies.md")).includes("DWT-C"), failures, "missing_dependencies", "dependencies must name generated child ids");
  assert(readText(path.join(bundleDir, "hardening-queue.md")).includes("leading_next"), failures, "missing_hardening_queue", "hardening queue must mark leading next state");
  assert(Array.isArray(manifest.generated_artifacts) && manifest.generated_artifacts.length >= 4, failures, "stale_or_unprovenanced_output", "generated artifacts must be declared");
  assert(manifest.copied_from_source_child_control !== true, failures, "stale_or_unprovenanced_output", "copied child-control artifacts are not allowed");
  assert(Array.isArray(manifest.normalizations), failures, "stale_or_unprovenanced_output", "normalizations must be declared");

  const forbiddenText = /(docker|docker compose|kubectl|terraform|credential copy|copy credential|deploy|ki-fuer-kmu write|runtime implementation)/i;
  if (forbiddenText.test(output)) {
    failures.push({ code: "forbidden_runtime_or_repo_write", message: "agent output contains forbidden runtime or repo write action" });
  }
  const forbiddenSeen = validateTelemetryManifest(telemetry, failures);
  validateSummaryShape(summary, failures);

  const children = Array.isArray(state.children) ? state.children : [];
  const leading = children.filter((child) => child.leading_next === true);
  assert(leading.length === 1, failures, "missing_or_ambiguous_next_child_state", "exactly one leading next child is required");
  for (const child of children) {
    assert(NEXT_STATES.has(child.next_state), failures, "missing_or_ambiguous_next_child_state", `${child.child_id} has invalid next state`);
    if (child.next_state !== "implementation_ready") {
      assert(!/spec-change-delivery/i.test(child.next_action || ""), failures, "skeleton_released_as_ready", `${child.child_id} must not name spec-change-delivery`);
    }
    if (child.next_state === "implementation_ready") {
      const handoffPath = child.handoff_path && path.join(bundleDir, child.handoff_path);
      const evidencePath = child.validator_evidence_path && path.join(bundleDir, child.validator_evidence_path);
      assert(handoffPath && exists(handoffPath), failures, "missing_ready_child_handoff", `${child.child_id} missing handoff`);
      assert(Array.isArray(child.allowed_write_set) && child.allowed_write_set.length > 0, failures, "missing_ready_child_handoff", `${child.child_id} needs concrete write-set`);
      assert(!JSON.stringify(child.allowed_write_set || []).match(/TBD|likely|probably|as needed|etc/i), failures, "missing_ready_child_handoff", `${child.child_id} write-set must be concrete`);
      assert(evidencePath && exists(evidencePath), failures, "readiness_validator_missing_or_failed", `${child.child_id} missing validator evidence`);
      if (evidencePath && exists(evidencePath)) {
        const evidence = readJson(evidencePath);
        assert(evidence.status === "pass", failures, "readiness_validator_missing_or_failed", `${child.child_id} validator evidence must pass`);
      }
      assert(index.includes(child.child_id) && index.includes("IMPLEMENTATION READY") && index.includes(child.handoff_path || ""), failures, "missing_ready_child_handoff", `${child.child_id} index row must match handoff`);
    }
  }

  if (options.expectBlockedAgent) {
    assert(summary.agent_execution_status !== "ran-target", failures, "blocked_agent_misreported_as_pass", "blocked fixture must not claim ran-target");
    assert(Object.values(summary.test_results || {}).includes("blocked"), failures, "blocked_agent_misreported_as_pass", "blocked fixture must report blocked");
  }

  return { failures, forbiddenSeen, leading };
}

function validateParentOnly(ctx) {
  const fixture = path.join(ctx.fixtures, "oversized-parent-only");
  const manifestPath = path.join(fixture, "source-manifest.json");
  const failures = [];
  assert(exists(manifestPath), failures, "missing_child_control_surface", "parent-only source manifest must exist");
  if (exists(manifestPath)) {
    const manifest = readJson(manifestPath);
    assert(manifest.fixture_id === "oversized-parent-only", failures, "stale_or_unprovenanced_output", "parent fixture id must be stable");
    assert(Array.isArray(manifest.removed_from_start_state) && manifest.removed_from_start_state.includes("child-index.md"), failures, "missing_child_control_surface", "removed child-control artifacts must be declared");
  }
  const startFiles = listFiles(path.join(fixture, "start-state")).map((file) => path.relative(path.join(fixture, "start-state"), file));
  const childArtifact = startFiles.find((file) => /child|handoff|index/i.test(file));
  assert(!childArtifact, failures, "direct_parent_implementation", "parent-only fixture must not contain child artifacts at start");
  return failures;
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

function runL2A(ctx) {
  const parentFailures = validateParentOnly(ctx);
  const direct = validateBundle(path.join(ctx.fixtures, "direct-implementation-attempt"));
  const valid = validateBundle(path.join(ctx.fixtures, "valid-orchestration-output"));
  const directForbidden = direct.failures.some((failure) => failure.code === "forbidden_runtime_or_repo_write");
  const passed = parentFailures.length === 0 && directForbidden && valid.failures.length === 0;
  const payload = outcome("DWT-S2-L2A", "pass", passed, {
    parent_only_failures: parentFailures,
    direct_attempt_failures: direct.failures,
    direct_forbidden_detected: directForbidden,
    valid_output_failures: valid.failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S2-L2A"], payload);
  return payload;
}

function runL2B(ctx) {
  const result = validateBundle(path.join(ctx.fixtures, "valid-orchestration-output"));
  const payload = outcome("DWT-S2-L2B", "pass", result.failures.length === 0, {
    generated_control_surface_hash: sha256(path.join(ctx.fixtures, "valid-orchestration-output", "child-index.md")),
    leading_next_child: result.leading[0] && result.leading[0].child_id,
    failures: result.failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S2-L2B"], payload);
  return payload;
}

function runL2C(ctx) {
  const result = validateBundle(path.join(ctx.fixtures, "thin-child-ready-claim"));
  const blocked = result.failures.some((failure) => failure.code === "skeleton_released_as_ready" || failure.code === "missing_ready_child_handoff" || failure.code === "readiness_validator_missing_or_failed");
  const payload = outcome("DWT-S2-L2C", "blocked", blocked, {
    expected_blocker_detected: blocked,
    failures: result.failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S2-L2C"], payload);
  return payload;
}

function runL2D(ctx) {
  const result = validateBundle(path.join(ctx.fixtures, "ready-child-output"));
  const leading = result.leading[0];
  const passed = result.failures.length === 0 && leading && leading.next_state === "implementation_ready";
  const payload = outcome("DWT-S2-L2D", "pass", passed, {
    leading_next_child: leading && leading.child_id,
    leading_next_state: leading && leading.next_state,
    failures: result.failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S2-L2D"], payload);
  return payload;
}

function runL2E(ctx) {
  const result = validateBundle(path.join(ctx.fixtures, "blocked-agent-output"), { expectBlockedAgent: true });
  const summary = readJson(path.join(ctx.fixtures, "blocked-agent-output", "evidence/dwt-s2-l2-summary.json"));
  const passed = result.failures.length === 0 && summary.agent_execution_status !== "ran-target";
  const payload = outcome("DWT-S2-L2E", "blocked", passed, {
    agent_execution_status: summary.agent_execution_status,
    runner_mode: summary.runner_mode,
    failures: result.failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S2-L2E"], payload);
  return payload;
}

function runL2F(ctx) {
  const result = validateBundle(path.join(ctx.fixtures, "style-efficiency-output"));
  const summary = readJson(path.join(ctx.fixtures, "style-efficiency-output", "evidence/dwt-s2-l2-summary.json"));
  const downstream = summary.downstream_children || {};
  const descendantsBlocked = ["DWT-S3", "DWT-S5"].every((child) => downstream[child] === "blocked" || downstream[child] === "planned");
  const passed = result.failures.length === 0 && descendantsBlocked;
  const payload = outcome("DWT-S2-L2F", "warn", passed, {
    style_verdicts: summary.style_verdicts,
    telemetry_verdicts: summary.telemetry_verdicts,
    downstream_children: downstream,
    failures: result.failures
  });
  writeEvidence(ctx.evidence, CASES["DWT-S2-L2F"], payload);
  return payload;
}

function writeSummary(ctx, results, selector) {
  const byCase = Object.fromEntries(results.map((result) => [result.case_id, result]));
  const agentProof = ctx.agentEvidence || getPromptfooEvidence(ctx);
  const evidenceLinks = Object.fromEntries(Object.entries(CASES).map(([caseId, file]) => [caseId, path.join(ctx.evidence, file)]));
  evidenceLinks.agent_proof = path.join(ctx.evidence, "dwt-s2-agent-proof.json");
  if (agentProof.promptfoo_eval_json) {
    evidenceLinks.promptfoo_eval = agentProof.promptfoo_eval_json;
  }
  if (agentProof.promptfoo_eval_log) {
    evidenceLinks.promptfoo_log = agentProof.promptfoo_eval_log;
  }
  const summary = {
    schema_id: "docworkflow-agent-delivery-summary.v1",
    suite_level: "DWT-S2",
    suite_version: "DWT-S2-l2-parent-first-v1",
    repo_root: ctx.repoRoot,
    fixture_root: ctx.fixtures,
    fixture_manifest: path.join(ctx.fixtures, "oversized-parent-only", "source-manifest.json"),
    runner_mode: agentProof.runner_mode,
    agent_execution_status: agentProof.agent_execution_status,
    overall_agent_proof_status: agentProof.overall_agent_proof_status,
    selector,
    test_results: Object.fromEntries(Object.keys(CASES).map((caseId) => [caseId, byCase[caseId] ? byCase[caseId].expected_fixture_status : "planned"])),
    harness_case_results: Object.fromEntries(Object.entries(byCase).map(([caseId, result]) => [caseId, result.harness_status])),
    evidence_truth: Object.fromEntries(Object.keys(CASES).map((caseId) => [caseId, byCase[caseId] ? "ran-target" : "planned"])),
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
      promptfoo_exit_status: agentProof.promptfoo_exit_status
    },
    provenance_checks: {
      parent_only_start: byCase["DWT-S2-L2A"] && byCase["DWT-S2-L2A"].harness_status === "pass" ? "pass" : "planned",
      generated_control_surface: byCase["DWT-S2-L2B"] && byCase["DWT-S2-L2B"].harness_status === "pass" ? "pass" : "planned",
      no_stale_output_reuse: byCase["DWT-S2-L2B"] && byCase["DWT-S2-L2B"].harness_status === "pass" ? "pass" : "planned"
    },
    readiness_checks: {
      thin_child_blocked: byCase["DWT-S2-L2C"] && byCase["DWT-S2-L2C"].harness_status === "pass" ? "blocked" : "planned",
      valid_next_child_state: byCase["DWT-S2-L2D"] && byCase["DWT-S2-L2D"].harness_status === "pass" ? "pass" : "planned",
      blocked_agent_honesty: byCase["DWT-S2-L2E"] && byCase["DWT-S2-L2E"].harness_status === "pass" ? "blocked" : "planned"
    },
    style_verdicts: {
      "DWT-S2-L2F": byCase["DWT-S2-L2F"] ? "pass" : "planned"
    },
    telemetry_verdicts: {
      "DWT-S2-L2F": byCase["DWT-S2-L2F"] ? "warn" : "planned",
      "DWT-S2-L2E": byCase["DWT-S2-L2E"] ? "blocked" : "planned"
    },
    forbidden_actions_observed: [],
    downstream_children: {
      "DWT-S3": "blocked",
      "DWT-S5": "planned"
    }
  };
  return writeEvidence(ctx.evidence, "dwt-s2-l2-summary.json", summary);
}

function runValidateOutput(ctx) {
  if (!ctx.outputBundle) {
    throw new Error("validate-output requires --output-bundle DIR");
  }
  const result = validateBundle(ctx.outputBundle);
  const payload = outcome("DWT-S2-VALIDATE-OUTPUT", "pass", result.failures.length === 0, {
    output_bundle: ctx.outputBundle,
    failures: result.failures
  });
  writeEvidence(ctx.evidence, "dwt-s2-validate-output.json", payload);
  return [payload];
}

function runAgent(ctx) {
  const proof = ctx.agentEvidence || getPromptfooEvidence(ctx);
  const payload = {
    case_id: "DWT-S2-AGENT",
    expected_fixture_status: proof.overall_agent_proof_status === "pass" ? "pass" : proof.overall_agent_proof_status,
    harness_status: proof.overall_agent_proof_status === "pass" ? "pass" : "fail",
    evidence_truth: proof.agent_execution_status === "ran-target" ? "ran-target" : "blocked",
    runner_mode: proof.runner_mode,
    agent_execution_status: proof.agent_execution_status,
    overall_agent_proof_status: proof.overall_agent_proof_status,
    failure_reason: proof.failure_reason
  };
  writeEvidence(ctx.evidence, "dwt-s2-agent-result.json", payload);
  return [payload];
}

function main() {
  const args = parseArgs(process.argv);
  fs.mkdirSync(args.evidence, { recursive: true });
  const ctx = args;
  ctx.agentEvidence = getPromptfooEvidence(ctx);
  const runners = {
    "DWT-S2-L2A": runL2A,
    "DWT-S2-L2B": runL2B,
    "DWT-S2-L2C": runL2C,
    "DWT-S2-L2D": runL2D,
    "DWT-S2-L2E": runL2E,
    "DWT-S2-L2F": runL2F
  };
  const selectorMap = {
    all: Object.values(runners),
    fallback: [runL2A, runL2B, runL2C, runL2D, runL2E, runL2F],
    style: [runL2F],
    telemetry: [runL2E, runL2F]
  };

  let results;
  if (args.selector === "validate-output") {
    results = runValidateOutput(ctx);
  } else if (args.selector === "agent") {
    results = runAgent(ctx);
  } else if (selectorMap[args.selector]) {
    results = selectorMap[args.selector].map((runner) => runner(ctx));
  } else {
    throw new Error(`Unknown selector: ${args.selector}`);
  }

  const summaryPath = writeSummary(ctx, results, args.selector);
  for (const result of results) {
    console.log(`${result.harness_status.toUpperCase()}: ${result.case_id} expected fixture ${result.expected_fixture_status}`);
  }
  console.log(`SUMMARY: ${summaryPath}`);

  const failures = results.filter((result) => result.harness_status !== "pass");
  if ((args.selector === "all" || args.selector === "agent") && ctx.agentEvidence.overall_agent_proof_status !== "pass") {
    failures.push({
      case_id: "DWT-S2-AGENT",
      harness_status: "fail",
      failure_reason: ctx.agentEvidence.failure_reason || ctx.agentEvidence.agent_execution_status
    });
  }
  if (failures.length > 0) {
    process.exitCode = 1;
  }
}

main();
