#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
selector="${1:-control-boundary}"

usage() {
  cat <<'USAGE'
Usage:
  run-visible-app-session-workflow-checks.sh control-boundary
  run-visible-app-session-workflow-checks.sh --run-id <id> --keep [options]

Selectors:
  control-boundary, fixtures
      Replay the accepted ADV-CAS-S4 control-boundary fixtures.

Live MD-E2E-5 options:
  --run-id <id>
      Required for the live visible Codex-App session gate. The id must contain
      only letters, numbers, dot, underscore, or hyphen.
  --keep
      Required. Retains the live run directory and summary evidence.
  --initiating-project-cwd <path>
      Optional expected visible Codex-App project cwd. Defaults to the repo root.
  --timeout-seconds <n>
      Optional timeout value recorded in not-ready summaries. Defaults to 1800.
  --help, -h, help
      Show this help.

Live warning:
  The --run-id mode is an opt-in MD-E2E-5 gate. It does not replace the
  mock-only standard gate. It passes only when retained live evidence proves
  parent plus five child visible Codex-App sessions, S2 validation, S4
  observed-only control behavior, S5 READY archive closeout, and exact final
  output 1\n2\n3\n4\n5\n.
USAGE
}

case "$selector" in
  control-boundary|fixtures)
    node "$repo_root/tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js" \
      "$repo_root/tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary"
    ;;
  --help|-h|help)
    usage
    ;;
  --run-id)
    node - "$repo_root" "$@" <<'NODE'
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { spawnSync } = require("child_process");

const repoRoot = process.argv[2];
const args = process.argv.slice(3);

const SUMMARY_SCHEMA = "docworkflow-agent-delivery-visible-app-e2e-summary.v1";
const EXPECTED_OUTPUT = "1\n2\n3\n4\n5\n";
const EXPECTED_SHA = "f6b49467f595b1a44e442c198b3df4d221e88efcaabc26254f8e0ad4f79b6242";
const RUN_ID_PATTERN = /^[A-Za-z0-9._-]+$/;
const childRoles = ["rsw-c1", "rsw-c2", "rsw-c3", "rsw-c4", "rsw-c5"];
const targetIds = {
  parent: "RSW-PARENT",
  "rsw-c1": "RSW-C1",
  "rsw-c2": "RSW-C2",
  "rsw-c3": "RSW-C3",
  "rsw-c4": "RSW-C4",
  "rsw-c5": "RSW-C5"
};

const options = parseArgs(args);
if (options.help) {
  process.exit(0);
}
if (options.setupErrors.length > 0) {
  for (const error of options.setupErrors) console.error(error);
  process.exit(2);
}

const runDir = path.join(repoRoot, "tests/docworkflow-agent-delivery/e2e/session-workflow-live", options.runId);
const relRunDir = rel(runDir);
const inputFixture = path.join(runDir, "input/test-parent.md");
const summaryPath = path.join(runDir, "visible-session-summary.json");
const outputPath = path.join(runDir, "target/output/count.txt");
const controlSummaryPath = path.join(runDir, "control/control-boundary-summary.json");
const archiveSummaryPath = path.join(runDir, "closeout/archive-summary.json");
const controllerSummaryPath = path.join(runDir, "controller/controller-summary.json");
const canonicalFixture = path.join(repoRoot, "tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md");

const setup = prepareRunDir();
if (!setup.ok) {
  for (const error of setup.errors) console.error(error);
  process.exit(2);
}

const result = evaluateRun();
writeJson(summaryPath, result.summary);
if (result.timeoutReport) {
  writeJson(path.join(runDir, "control/timeout-report.json"), result.timeoutReport);
}

for (const line of result.reportLines) {
  const stream = result.exitCode === 0 ? process.stdout : process.stderr;
  stream.write(`${line}\n`);
}
process.exit(result.exitCode);

function parseArgs(argv) {
  const parsed = {
    runId: null,
    keep: false,
    initiatingProjectCwd: repoRoot,
    timeoutSeconds: 1800,
    help: false,
    setupErrors: []
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case "--run-id":
        parsed.runId = argv[++i];
        break;
      case "--keep":
        parsed.keep = true;
        break;
      case "--initiating-project-cwd":
        parsed.initiatingProjectCwd = path.resolve(requireValue(argv, ++i, arg, parsed));
        break;
      case "--timeout-seconds": {
        const raw = requireValue(argv, ++i, arg, parsed);
        const value = Number(raw);
        if (!Number.isInteger(value) || value <= 0) {
          parsed.setupErrors.push("--timeout-seconds must be a positive integer.");
        } else {
          parsed.timeoutSeconds = value;
        }
        break;
      }
      case "--help":
      case "-h":
      case "help":
        parsed.help = true;
        break;
      default:
        parsed.setupErrors.push(`Unsupported option for MD-E2E-5 live gate: ${arg}`);
        break;
    }
  }

  if (!parsed.runId) {
    parsed.setupErrors.push("--run-id <id> is required for the MD-E2E-5 live gate.");
  } else if (!RUN_ID_PATTERN.test(parsed.runId)) {
    parsed.setupErrors.push("--run-id must be path-safe: letters, numbers, dot, underscore, and hyphen only.");
  }
  if (!parsed.keep) {
    parsed.setupErrors.push("--keep is required so MD-E2E-5 retains live evidence.");
  }
  return parsed;
}

function requireValue(argv, index, option, parsed) {
  const value = argv[index];
  if (!value || value.startsWith("--")) {
    parsed.setupErrors.push(`${option} requires a value.`);
    return "";
  }
  return value;
}

function prepareRunDir() {
  const errors = [];
  try {
    fs.mkdirSync(path.dirname(inputFixture), { recursive: true });
    fs.mkdirSync(path.join(runDir, "control"), { recursive: true });
    fs.mkdirSync(path.join(runDir, "handoffs"), { recursive: true });
    fs.mkdirSync(path.join(runDir, "launches"), { recursive: true });
    fs.mkdirSync(path.join(runDir, "closeout"), { recursive: true });
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    if (!fs.existsSync(inputFixture)) {
      if (!fs.existsSync(canonicalFixture)) {
        errors.push(`Canonical parent fixture not found: ${canonicalFixture}`);
      } else {
        fs.copyFileSync(canonicalFixture, inputFixture);
      }
    }
  } catch (error) {
    errors.push(`Failed to prepare run directory: ${error.message}`);
  }
  return { ok: errors.length === 0, errors };
}

function evaluateRun() {
  const reportLines = [];
  const visibleResults = validateVisibleSessions();
  const controllerResult = validateControllerSummary(visibleResults.controllerEvidenceMap);
  const outputResult = validateFinalOutput();
  const controlResult = validateControlBoundary();
  const archiveResult = validateArchiveSummary();
  const redactionResult = validateRedaction([
    summaryPath,
    controlSummaryPath,
    archiveSummaryPath,
    ...visibleResults.evidencePaths
  ]);

  const visibleStatus = visibleResults.ok ? "pass" : visibleResults.missingOnly ? "not_ready" : "fail";
  const finalOutputStatus = outputResult.ok ? "pass" : outputResult.exists ? "fail" : "not_ready";
  const controlStatus = controlResult.ok ? "observed_only" : controlResult.exists ? "failed" : "not_ready";
  const archiveStatus = archiveResult.status;
  const secretRedactionStatus = redactionResult.ok ? "pass" : "fail";

  const allPass = visibleStatus === "pass" &&
    controllerResult.ok &&
    finalOutputStatus === "pass" &&
    controlStatus === "observed_only" &&
    archiveStatus === "READY" &&
    secretRedactionStatus === "pass";

  const overallStatus = allPass ? "pass" :
    visibleStatus === "not_ready" || !controllerResult.exists || finalOutputStatus === "not_ready" || controlStatus === "not_ready" || archiveStatus === "READY_NO_SESSION_EVIDENCE"
      ? "not_ready"
      : "fail";

  const summary = {
    schema_id: SUMMARY_SCHEMA,
    run_id: options.runId,
    testcase_id: "MD-E2E-5",
    parent: "_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md",
    parent_identifier: "ADV-CAS-1",
    input_parent_fixture: rel(inputFixture),
    overall_workflow_status: overallStatus,
    visible_session_status: visibleStatus,
    control_session_status: controlStatus,
    archive_status: archiveStatus,
    final_output_status: finalOutputStatus,
    mock_gate_status: "not_applicable_live_md_e2e_5",
    final_output: {
      path: rel(outputPath),
      expected_text: EXPECTED_OUTPUT,
      expected_sha256: EXPECTED_SHA,
      actual_sha256: outputResult.actualSha256
    },
    parent_visible_session_evidence: visibleResults.parent,
    child_visible_session_evidence: visibleResults.children,
    control_boundary_summary: rel(controlSummaryPath),
    closeout_archive_summary: rel(archiveSummaryPath),
    s2_visible_validator: visibleResults.validatorProof,
    controller_summary: controllerResult.proof,
    s4_control_boundary_validator: controlResult.validatorProof,
    s5_archive_validator: archiveResult.validatorProof,
    failure_reasons: [
      ...controllerResult.failures,
      ...visibleResults.failures,
      ...outputResult.failures,
      ...controlResult.failures,
      ...archiveResult.failures,
      ...redactionResult.failures
    ],
    secret_redaction_status: secretRedactionStatus
  };

  if (overallStatus !== "pass") {
    reportLines.push(`MD-E2E-5 ${overallStatus}: ${relRunDir}`);
    for (const reason of summary.failure_reasons) reportLines.push(`- ${reason}`);
  } else {
    reportLines.push(`MD-E2E-5 pass: ${relRunDir}`);
  }

  return {
    exitCode: allPass ? 0 : 1,
    summary,
    reportLines,
    timeoutReport: overallStatus === "not_ready" ? {
      schema_id: "docworkflow-agent-delivery-visible-app-e2e-timeout.v1",
      run_id: options.runId,
      timeout_seconds: options.timeoutSeconds,
      status: "not_ready",
      reason: "Required live visible-session, control-boundary, archive, or output evidence was not complete at evaluation time."
    } : null
  };
}

function validateVisibleSessions() {
  const roles = ["parent", ...childRoles];
  const failures = [];
  const records = new Map();
  const threadIds = new Set();
  const evidencePaths = [];
  const validatorRuns = [];
  const controllerEvidenceMap = loadControllerEvidenceMap();
  let missingCount = 0;

  for (const role of roles) {
    const targetId = targetIds[role];
    const evidencePath = findEvidencePath(role, controllerEvidenceMap);
    const record = {
      target_id: targetId,
      evidence_path: evidencePath ? rel(evidencePath) : rel(path.join(runDir, "launches", role, "evidence.json")),
      visible_validator_status: "not_ready"
    };

    if (!evidencePath) {
      missingCount++;
      failures.push(`${targetId}: missing Launcher-created visible evidence.`);
      records.set(role, record);
      continue;
    }

    evidencePaths.push(evidencePath);
    const evidence = readJson(evidencePath);
    if (!evidence.ok) {
      failures.push(`${targetId}: evidence JSON is invalid: ${evidence.error}`);
      record.visible_validator_status = "fail";
      records.set(role, record);
      continue;
    }

    const threadId = evidence.value?.session_visibility?.thread_id || evidence.value?.app_server?.thread_id || "";
    if (!threadId) {
      failures.push(`${targetId}: visible evidence has no thread id.`);
    } else if (threadIds.has(threadId)) {
      failures.push(`${targetId}: duplicate visible thread id ${threadId}.`);
    } else {
      threadIds.add(threadId);
    }
    if (evidence.value?.target_id !== targetId) {
      failures.push(`${targetId}: evidence target_id is ${evidence.value?.target_id || "<missing>"}.`);
    }

    const validator = runVisibleValidator(evidencePath);
    validatorRuns.push({
      target_id: targetId,
      evidence_path: rel(evidencePath),
      exit_code: validator.status,
      stdout: validator.stdout.trim(),
      stderr: validator.stderr.trim()
    });
    if (validator.status === 0) {
      record.visible_validator_status = "pass";
    } else if (validator.status === 2) {
      record.visible_validator_status = "not_ready";
      failures.push(`${targetId}: S2 visible validator setup failed.`);
    } else {
      record.visible_validator_status = "fail";
      failures.push(`${targetId}: S2 visible validator rejected evidence.`);
    }

    records.set(role, record);
  }

  const control = readJson(controlSummaryPath);
  const controlId = control.ok ? control.value?.control_session?.control_session_id : null;
  if (controlId && threadIds.has(controlId)) {
    failures.push("A workflow visible thread id reuses the control session id.");
  }

  const children = childRoles.map((role) => records.get(role));
  const allPass = [records.get("parent"), ...children].every((record) => record.visible_validator_status === "pass");
  return {
    ok: allPass && failures.length === 0,
    missingOnly: missingCount > 0 && validatorRuns.length === 0,
    failures,
    evidencePaths,
    parent: records.get("parent"),
    children,
    validatorProof: validatorRuns
    ,
    controllerEvidenceMap
  };
}

function findEvidencePath(role, controllerEvidenceMap) {
  const targetId = targetIds[role];
  if (controllerEvidenceMap.has(targetId)) return controllerEvidenceMap.get(targetId);
  const canonical = path.join(runDir, "launches", role, "evidence.json");
  if (fs.existsSync(canonical)) return canonical;
  const roleRoot = path.join(runDir, "launches", role);
  const searchRoots = [];
  if (fs.existsSync(roleRoot)) searchRoots.push(roleRoot);
  const controllerChildRoot = path.join(runDir, "launches", "children");
  if (role !== "parent" && fs.existsSync(controllerChildRoot)) searchRoots.push(controllerChildRoot);
  const matches = searchRoots.flatMap((root) => walk(root))
    .filter((file) => path.basename(file) === "evidence.json")
    .filter((file) => {
      const evidence = readJson(file);
      return evidence.ok && evidence.value?.target_id === targetId;
    })
    .sort();
  return matches.length === 1 ? matches[0] : null;
}

function loadControllerEvidenceMap() {
  const evidence = new Map();
  if (!fs.existsSync(controllerSummaryPath)) return evidence;
  const summary = readJson(controllerSummaryPath);
  if (!summary.ok) return evidence;

  const parentPath = resolveMaybe(summary.value?.parent?.evidence_path);
  if (parentPath && fs.existsSync(parentPath)) evidence.set("RSW-PARENT", parentPath);

  const requests = Array.isArray(summary.value?.requests) ? summary.value.requests : [];
  for (const request of requests) {
    const responsePath = resolveMaybe(request.response_path);
    if (!responsePath || !fs.existsSync(responsePath)) continue;
    const response = readJson(responsePath);
    if (!response.ok) continue;
    const targetId = response.value?.request_id;
    const evidencePath = resolveMaybe(response.value?.launcher?.evidence_path);
    if (targetId && evidencePath && fs.existsSync(evidencePath)) evidence.set(targetId, evidencePath);
  }
  return evidence;
}

function validateControllerSummary(controllerEvidenceMap) {
  const failures = [];
  if (!fs.existsSync(controllerSummaryPath)) {
    return { ok: false, exists: false, failures: ["Controller summary is missing."], proof: null };
  }

  const summary = readJson(controllerSummaryPath);
  if (!summary.ok) {
    return { ok: false, exists: true, failures: [`Controller summary JSON is invalid: ${summary.error}`], proof: null };
  }

  if (summary.value.schema_id !== "agent-delivery.visible-session-controller.summary.v1") {
    failures.push("Controller summary schema_id is invalid.");
  }
  if (summary.value.status !== "pass") {
    failures.push(`Controller summary status is ${summary.value.status || "<missing>"}.`);
  }
  if (!controllerEvidenceMap.has("RSW-PARENT")) {
    failures.push("Controller summary does not resolve RSW-PARENT evidence.");
  }

  const requests = Array.isArray(summary.value.requests) ? summary.value.requests : [];
  for (const role of childRoles) {
    const targetId = targetIds[role];
    const request = requests.find((item) => item.request_id === targetId);
    if (!request) {
      failures.push(`Controller summary has no request for ${targetId}.`);
      continue;
    }
    if (request.status !== "launched") {
      failures.push(`Controller request ${targetId} status is ${request.status || "<missing>"}.`);
    }
    if (!controllerEvidenceMap.has(targetId)) {
      failures.push(`Controller response does not resolve evidence for ${targetId}.`);
    }
  }
  if (requests.filter((item) => /^RSW-C[1-5]$/.test(String(item.request_id || ""))).length !== 5) {
    failures.push("Controller summary must include exactly five RSW child requests.");
  }

  return {
    ok: failures.length === 0,
    exists: true,
    failures,
    proof: {
      path: rel(controllerSummaryPath),
      status: summary.value.status,
      request_count: requests.length
    }
  };
}

function resolveMaybe(raw) {
  if (!raw) return null;
  return path.isAbsolute(raw) ? raw : path.resolve(repoRoot, raw);
}

function runVisibleValidator(evidencePath) {
  const dir = path.dirname(evidencePath);
  const args = [
    "run",
    path.join(repoRoot, "skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs"),
    "--",
    "--evidence",
    evidencePath,
    "--expect-initiating-project-cwd",
    options.initiatingProjectCwd
  ];

  const evidence = readJson(evidencePath);
  if (evidence.value?.session_title) args.push("--expect-title", evidence.value.session_title);
  const prompt = resolveEvidencePath(evidence.value, dir, "prompt") || path.join(dir, "start-prompt.md");
  const transcript = resolveEvidencePath(evidence.value, dir, "app_server_transcript") || path.join(dir, "app-server-transcript.jsonl");
  if (fs.existsSync(prompt)) args.push("--prompt", prompt);
  if (fs.existsSync(transcript)) args.push("--transcript", transcript);

  return spawnSync("dotnet", args, { cwd: repoRoot, encoding: "utf8" });
}

function resolveEvidencePath(evidence, evidenceDir, key) {
  const raw = evidence?.evidence_paths?.[key] || evidence?.app_server?.transcript_path;
  if (!raw) return null;
  if (path.isAbsolute(raw)) return raw;
  const fromEvidenceDir = path.resolve(evidenceDir, raw);
  if (fs.existsSync(fromEvidenceDir)) return fromEvidenceDir;
  return path.resolve(repoRoot, raw);
}

function validateFinalOutput() {
  const failures = [];
  if (!fs.existsSync(outputPath)) {
    failures.push("Final output is missing.");
    return { ok: false, exists: false, actualSha256: "", failures };
  }
  const bytes = fs.readFileSync(outputPath);
  const text = bytes.toString("utf8");
  const actualSha256 = sha256(bytes);
  if (text !== EXPECTED_OUTPUT) failures.push("Final output text does not match exact expected bytes.");
  if (actualSha256 !== EXPECTED_SHA) failures.push("Final output SHA-256 does not match frozen hash.");
  return { ok: failures.length === 0, exists: true, actualSha256, failures };
}

function validateControlBoundary() {
  const failures = [];
  if (!fs.existsSync(controlSummaryPath)) {
    failures.push("S4 control-boundary summary is missing.");
    return { ok: false, exists: false, failures, validatorProof: null };
  }
  const run = spawnSync("node", [
    path.join(repoRoot, "tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js"),
    controlSummaryPath
  ], { cwd: repoRoot, encoding: "utf8" });
  if (run.status !== 0) failures.push("S4 control-boundary validator rejected the live summary.");
  const summary = readJson(controlSummaryPath);
  if (!summary.ok) {
    failures.push(`S4 control-boundary summary JSON is invalid: ${summary.error}`);
  } else if (summary.value.control_session_status !== "observed_only") {
    failures.push(`S4 control_session_status is ${summary.value.control_session_status || "<missing>"}.`);
  }
  return {
    ok: run.status === 0 && failures.length === 0,
    exists: true,
    failures,
    validatorProof: {
      path: rel(controlSummaryPath),
      exit_code: run.status,
      stdout: run.stdout.trim(),
      stderr: run.stderr.trim()
    }
  };
}

function validateArchiveSummary() {
  const failures = [];
  if (!fs.existsSync(archiveSummaryPath)) {
    failures.push("S5 archive summary is missing.");
    return { status: "READY_NO_SESSION_EVIDENCE", failures, validatorProof: null };
  }

  const summary = readJson(archiveSummaryPath);
  if (!summary.ok) {
    failures.push(`S5 archive summary JSON is invalid: ${summary.error}`);
    return { status: "NOT_READY", failures, validatorProof: null };
  }

  const status = summary.value.overall_archive_status || "NOT_READY";
  if (status !== "READY") {
    failures.push(`S5 overall_archive_status is ${status}.`);
  }

  const records = Array.isArray(summary.value.session_records) ? summary.value.session_records : [];
  for (const role of ["parent", ...childRoles]) {
    const target = targetIds[role];
    const launchPathFragment = `launches/${role}/`;
    const hasTarget = records.some((record) => {
      const evidencePath = String(record.evidence_path || "").toLowerCase();
      return record.target_id === target ||
        evidencePath.includes(target.toLowerCase()) ||
        evidencePath.includes(launchPathFragment);
    });
    if (!hasTarget) failures.push(`S5 archive summary has no explicit session record for ${target}.`);
  }
  if (records.length < 6) failures.push("S5 archive summary must include at least six parent/child session records.");

  const run = spawnSync("dotnet", [
    "run",
    path.join(repoRoot, "skills-repo/tools/ArchiveVisibleCodexAppSession.cs"),
    "--",
    "--validate-summary",
    archiveSummaryPath,
    "--mode",
    "validate"
  ], { cwd: repoRoot, encoding: "utf8" });

  return {
    status: status === "READY" && failures.length === 0 ? "READY" : status === "READY_NO_SESSION_EVIDENCE" ? "READY_NO_SESSION_EVIDENCE" : "NOT_READY",
    failures,
    validatorProof: {
      path: rel(archiveSummaryPath),
      exit_code: run.status,
      stdout: run.stdout.trim(),
      stderr: run.stderr.trim()
    }
  };
}

function validateRedaction(files) {
  const failures = [];
  const patterns = [
    /sk-[A-Za-z0-9_-]{20,}/,
    /(OPENAI|CODEX|ANTHROPIC|GITHUB|SENTRY|CLOUDFLARE)_[A-Z0-9_]*(KEY|TOKEN|SECRET)["'\s:=]+[A-Za-z0-9_.-]{8,}/i,
    /Authorization:\s*Bearer\s+[A-Za-z0-9_.-]+/i
  ];

  for (const file of files.filter(Boolean)) {
    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) continue;
    const text = fs.readFileSync(file, "utf8");
    if (patterns.some((pattern) => pattern.test(text))) {
      failures.push(`Secret-like material appears in retained evidence: ${rel(file)}.`);
    }
  }
  return { ok: failures.length === 0, failures };
}

function walk(root) {
  const entries = [];
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const full = path.join(root, entry.name);
    if (entry.isDirectory()) entries.push(...walk(full));
    else entries.push(full);
  }
  return entries;
}

function readJson(file) {
  try {
    return { ok: true, value: JSON.parse(fs.readFileSync(file, "utf8")) };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function rel(file) {
  return path.relative(repoRoot, file).split(path.sep).join("/");
}
NODE
    ;;
  *)
    echo "Unsupported selector for visible app session workflow checks: $selector" >&2
    echo "Use: control-boundary or --run-id <id> --keep" >&2
    exit 2
    ;;
esac
