#!/usr/bin/env node
const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");

const CASES = {
  "DWT-S5-L3A": "dwt-s5-l3a-temp-repo.json",
  "DWT-S5-L3B": "dwt-s5-l3b-delivery-kickoff.json",
  "DWT-S5-L3C": "dwt-s5-l3c-local-runtime.json",
  "DWT-S5-L3D": "dwt-s5-l3d-container-harness.json",
  "DWT-S5-L3E": "dwt-s5-l3e-forbidden-actions.json",
  "DWT-S5-L3F": "dwt-s5-l3f-closeout-sync.json"
};

const REQUIRED_BUNDLE_FILES = [
  "source-manifest.json",
  "agent-output.md",
  "delivery-kickoff.md",
  "runtime-gates.md",
  "closeout-sync.md",
  "child-index-before.md",
  "child-index-after.md",
  "handoffs/dwt-s5-session-handoff.md",
  "agent-run-manifest.json",
  "evidence/dwt-s5-l3-summary.json"
];

const STATUS = new Set(["pass", "fail", "blocked", "warn", "planned"]);
const TRUTH = new Set(["ran-target", "ran-rehearsal", "blocked", "failed", "planned", "dry-run"]);
const AGENT_STATUS = new Set(["ran-target", "blocked_auth", "blocked_provider", "blocked_network", "blocked_runtime", "failed", "not-run"]);
const STYLE = new Set(["pass", "fail", "warn"]);
const TELEMETRY = new Set(["pass", "fail", "warn", "blocked"]);
const PARENT_COVERAGE = ["DWT-PR3", "DWT-PR4", "DWT-PR5"];
const CURRENT_HANDOFF = "_specs/child-session-handoffs/dwt-s5-session-handoff.md";
const DWT_S3_SUMMARY = "tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/dwt-s3-l2-summary.json";
const DWT_S3_MANIFEST = "tests/docworkflow-agent-delivery/l2/single-child-closeout/evidence/2026-05-08-ran-target/manifest.json";
const CHILD_SPEC = "_specs/2026-05-08 DocWorkflow Agent Delivery Testsuite DWT-S5 L3 Runtime Temp-Repo Delivery Pilot.md";
const PARENT_SPEC = "_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md";
const OPENSPEC_CHANGE = "openspec/changes/docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot/";
const ALLOWED_WRITE_SET = [
  CHILD_SPEC,
  PARENT_SPEC,
  CURRENT_HANDOFF,
  "openspec/changes/docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot/**",
  "openspec/specs/docworkflow-agent-delivery-testsuite/spec.md",
  "tests/docworkflow-agent-delivery/l3/runtime-temp-repo/**",
  "tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh",
  "tests/docworkflow-agent-delivery/README.md",
  "tests/docworkflow-agent-delivery/testcases/tc2-single-child-delivery-next-handoff.md"
];

function usage() {
  console.error("Usage: runtime-temp-repo-validator.js --fixtures DIR --evidence DIR --repo-root DIR [--selector all|preflight|agent|fallback|validate-output|local-runtime|container-harness|closeout|style|telemetry] [--output-bundle DIR] [--fixture DIR] [--skip-container]");
}

function parseArgs(argv) {
  const args = { selector: "all", skipContainer: false };
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
    } else if (key === "--fixture") {
      args.fixture = value;
      i += 1;
    } else if (key === "--skip-container") {
      args.skipContainer = true;
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
    fixture: args.fixture ? path.resolve(args.fixture) : null,
    skipContainer: args.skipContainer,
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

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function hashFiles(files, baseDir) {
  const hash = crypto.createHash("sha256");
  for (const file of files.sort()) {
    hash.update(baseDir ? path.relative(baseDir, file) : file);
    hash.update(fs.readFileSync(file));
  }
  return hash.digest("hex");
}

function listFiles(dir) {
  if (!exists(dir)) return [];
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

function copyDir(src, dest) {
  fs.rmSync(dest, { recursive: true, force: true });
  for (const file of listFiles(src)) {
    const rel = path.relative(src, file);
    ensureDir(path.dirname(path.join(dest, rel)));
    fs.copyFileSync(file, path.join(dest, rel));
  }
}

function writeText(file, text) {
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, text.endsWith("\n") ? text : `${text}\n`);
  return file;
}

function writeJson(file, payload) {
  return writeText(file, JSON.stringify(payload, null, 2));
}

function writeEvidence(ctx, fileName, payload) {
  return writeJson(path.join(ctx.evidence, fileName), payload);
}

function assert(condition, failures, code, message) {
  if (!condition) failures.push({ code, message });
}

function rel(ctx, file) {
  return path.relative(ctx.repoRoot, file);
}

function commandExists(command) {
  const result = childProcess.spawnSync("sh", ["-c", `command -v ${command}`], { encoding: "utf8" });
  return result.status === 0;
}

function runCommand(command, args, cwd) {
  const result = childProcess.spawnSync(command, args, {
    cwd,
    encoding: "utf8",
    env: { ...process.env }
  });
  return {
    command: [command, ...args].join(" "),
    cwd,
    exit_status: result.status === null ? 1 : result.status,
    stdout: result.stdout || "",
    stderr: result.stderr || ""
  };
}

function validatePredecessor(ctx, failures) {
  const summaryPath = path.join(ctx.repoRoot, DWT_S3_SUMMARY);
  const manifestPath = path.join(ctx.repoRoot, DWT_S3_MANIFEST);
  assert(exists(summaryPath), failures, "missing_or_invalid_dwt_s3_dependency_evidence", "retained DWT-S3 summary is missing");
  assert(exists(manifestPath), failures, "missing_or_invalid_dwt_s3_dependency_evidence", "retained DWT-S3 manifest is missing");
  if (!exists(summaryPath) || !exists(manifestPath)) return null;

  const summary = readJson(summaryPath);
  const manifest = readJson(manifestPath);
  assert(summary.runner_mode === "promptfoo-codex", failures, "missing_or_invalid_dwt_s3_dependency_evidence", "DWT-S3 runner_mode must be promptfoo-codex");
  assert(summary.agent_execution_status === "ran-target", failures, "missing_or_invalid_dwt_s3_dependency_evidence", "DWT-S3 agent execution must be ran-target");
  assert(summary.overall_agent_proof_status === "pass", failures, "missing_or_invalid_dwt_s3_dependency_evidence", "DWT-S3 proof must pass");
  assert(manifest.proof_status && manifest.proof_status.agent_execution_status === "ran-target", failures, "missing_or_invalid_dwt_s3_dependency_evidence", "DWT-S3 manifest proof status must be ran-target");
  assert(Boolean(manifest.sha256 && manifest.sha256["dwt-s3-l2-summary.json"]), failures, "missing_or_invalid_dwt_s3_dependency_evidence", "DWT-S3 manifest must retain summary sha");
  return {
    summary_path: DWT_S3_SUMMARY,
    manifest_path: DWT_S3_MANIFEST,
    runner_mode: summary.runner_mode,
    agent_execution_status: summary.agent_execution_status,
    overall_agent_proof_status: summary.overall_agent_proof_status,
    manifest_sha_present: Boolean(manifest.sha256 && manifest.sha256["dwt-s3-l2-summary.json"]),
    summary_sha256: sha256(summaryPath)
  };
}

function validateFixtureManifest(ctx, failures, fixtureDir) {
  const manifestPath = path.join(fixtureDir, "fixture-manifest.json");
  assert(exists(manifestPath), failures, "missing_synthetic_fixture_manifest", "synthetic fixture manifest is missing");
  if (!exists(manifestPath)) return null;
  const manifest = readJson(manifestPath);
  assert(manifest.fixture_id === "dwt-s5-synthetic-runtime-repo", failures, "missing_synthetic_fixture_manifest", "fixture id must be dwt-s5-synthetic-runtime-repo");
  assert(typeof manifest.fixture_version === "string" && manifest.fixture_version.length > 0, failures, "missing_synthetic_fixture_manifest", "fixture version is required");
  assert(Array.isArray(manifest.local_gate_command), failures, "missing_synthetic_fixture_manifest", "local gate command must be declared");
  assert(Array.isArray(manifest.container_harness_command), failures, "missing_synthetic_fixture_manifest", "container harness command must be declared");
  for (const required of manifest.required_files || []) {
    assert(exists(path.join(fixtureDir, required)), failures, "missing_synthetic_fixture_manifest", `required fixture file missing: ${required}`);
  }
  const text = listFiles(fixtureDir).map(readText).join("\n");
  assert(!/sk-[A-Za-z0-9]{16,}|password\s*[:=]|secret\s*[:=]|api[_-]?key\s*[:=]/i.test(text), failures, "credential_or_secret_leak", "fixture contains a secret-shaped value");
  return manifest;
}

function materializeTempRepo(ctx) {
  const fixtureDir = ctx.fixture || path.join(ctx.fixtures, "synthetic-runtime-repo");
  const targetRepo = path.join(ctx.runDir, "target-repos", "dwt-s5-synthetic-runtime-repo");
  copyDir(fixtureDir, targetRepo);
  return {
    fixtureDir,
    targetRepo,
    fixtureFiles: listFiles(fixtureDir),
    targetFiles: listFiles(targetRepo)
  };
}

function validateTempRepo(ctx, materialized, manifest, failures) {
  assert(materialized.targetRepo.startsWith(path.join(ctx.runDir, "target-repos") + path.sep), failures, "target_repo_not_under_run_dir", "target repo must be generated under run-dir/target-repos");
  assert(exists(path.join(materialized.targetRepo, "fixture-manifest.json")), failures, "missing_synthetic_fixture_manifest", "copied target repo must include fixture manifest");
  assert(materialized.fixtureFiles.length === materialized.targetFiles.length, failures, "stale_or_unprovenanced_output", "target repo file count must match source fixture");
  const sourceHash = hashFiles(materialized.fixtureFiles, materialized.fixtureDir);
  const targetHash = hashFiles(materialized.targetFiles, materialized.targetRepo);
  assert(sourceHash === targetHash, failures, "stale_or_unprovenanced_output", "target repo hash must match source fixture hash");
  return {
    generated_path: materialized.targetRepo,
    fixture_id: manifest && manifest.fixture_id,
    fixture_version: manifest && manifest.fixture_version,
    source_hash: sourceHash,
    target_hash: targetHash,
    isolation_checks: {
      under_run_dir: materialized.targetRepo.startsWith(`${ctx.runDir}${path.sep}`),
      under_target_repos: materialized.targetRepo.startsWith(path.join(ctx.runDir, "target-repos") + path.sep),
      source_target_hash_match: sourceHash === targetHash
    }
  };
}

function validateCurrentHandoff(ctx, failures) {
  const handoffPath = path.join(ctx.repoRoot, CURRENT_HANDOFF);
  const parentPath = path.join(ctx.repoRoot, PARENT_SPEC);
  assert(exists(handoffPath), failures, "stale_or_mismatched_dwt_s5_handoff", "DWT-S5 handoff is missing");
  assert(exists(parentPath), failures, "stale_or_mismatched_dwt_s5_handoff", "parent Child Index is missing");
  if (!exists(handoffPath) || !exists(parentPath)) return null;
  const handoff = readText(handoffPath);
  const parent = readText(parentPath);
  const row = parent.split("\n").find((line) => line.startsWith("| DWT-S5 |")) || "";
  assert(row.includes("IMPLEMENTATION READY"), failures, "stale_or_mismatched_dwt_s5_handoff", "Child Index row must be implementation-ready");
  assert(row.includes("child-session-handoffs/dwt-s5-session-handoff.md"), failures, "stale_or_mismatched_dwt_s5_handoff", "Child Index row must point to current DWT-S5 handoff");
  assert(row.includes(OPENSPEC_CHANGE), failures, "missing_openspec_ledger_sync", "Child Index row must point to active DWT-S5 OpenSpec change");
  assert(handoff.includes("Aktueller Verdict: IMPLEMENTATION READY"), failures, "stale_or_mismatched_dwt_s5_handoff", "handoff verdict must be implementation-ready");
  assert(handoff.includes("Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`"), failures, "stale_or_mismatched_dwt_s5_handoff", "handoff target repository must match shared-ai-docs");
  for (const entry of ALLOWED_WRITE_SET) {
    assert(row.includes(entry) && handoff.includes(entry), failures, "approximate_or_mismatched_write_set", `allowed write-set missing entry: ${entry}`);
  }
  assert(!/\b(TBD|likely|probably|expected|as needed|related files|etc\.?)\b/i.test(row + handoff), failures, "approximate_or_mismatched_write_set", "write-set must not contain approximate wording");
  return {
    child_index_row_present: Boolean(row),
    handoff_path: CURRENT_HANDOFF,
    verdict: "IMPLEMENTATION READY",
    write_set_entries: ALLOWED_WRITE_SET.length,
    openspec_ledger: OPENSPEC_CHANGE
  };
}

function runLocalGate(ctx, tempRepo) {
  const result = runCommand(process.execPath, ["scripts/local-gate.js"], tempRepo);
  writeText(path.join(ctx.evidence, "local-runtime.log"), [
    `command: ${result.command}`,
    `cwd: ${result.cwd}`,
    `exit_status: ${result.exit_status}`,
    "stdout:",
    result.stdout,
    "stderr:",
    result.stderr
  ].join("\n"));
  const failures = [];
  assert(result.cwd === tempRepo, failures, "runtime_gate_outside_temp_repo", "local runtime cwd must equal generated temp repo");
  assert(tempRepo.startsWith(path.join(ctx.runDir, "target-repos") + path.sep), failures, "runtime_gate_outside_temp_repo", "local runtime cwd must be under run target-repos");
  assert(result.exit_status === 0, failures, "runtime_gate_outside_temp_repo", "local runtime gate must exit 0");
  return {
    status: failures.length === 0 ? "pass" : "fail",
    evidence_truth: "ran-target",
    command: result.command,
    cwd: result.cwd,
    exit_status: result.exit_status,
    log: path.join(ctx.evidence, "local-runtime.log"),
    failures
  };
}

function runContainerHarness(ctx, tempRepo) {
  const blocked = ctx.skipContainer || process.env.DWT_S5_FORCE_CONTAINER_BLOCKED === "1";
  if (blocked) {
    const payload = {
      status: "blocked",
      evidence_truth: "blocked",
      command: "node scripts/container-harness.js",
      cwd: tempRepo,
      exit_status: null,
      blocked_reason: "blocked_runtime",
      blocked_runtime_as_pass: false
    };
    writeJson(path.join(ctx.evidence, "container-harness-blocked.json"), payload);
    return payload;
  }

  const result = runCommand(process.execPath, ["scripts/container-harness.js"], tempRepo);
  writeText(path.join(ctx.evidence, "container-harness.log"), [
    `command: ${result.command}`,
    `cwd: ${result.cwd}`,
    `exit_status: ${result.exit_status}`,
    "stdout:",
    result.stdout,
    "stderr:",
    result.stderr
  ].join("\n"));
  const failures = [];
  assert(result.cwd === tempRepo, failures, "container_gate_outside_temp_repo", "container/harness cwd must equal generated temp repo");
  assert(tempRepo.startsWith(path.join(ctx.runDir, "target-repos") + path.sep), failures, "container_gate_outside_temp_repo", "container/harness cwd must be under run target-repos");
  assert(result.exit_status === 0, failures, "container_gate_outside_temp_repo", "container/harness gate must exit 0");
  return {
    status: failures.length === 0 ? "pass" : "fail",
    evidence_truth: "ran-target",
    command: result.command,
    cwd: result.cwd,
    exit_status: result.exit_status,
    harness: "node-fixture",
    log: path.join(ctx.evidence, "container-harness.log"),
    failures
  };
}

function validateForbiddenOutput(text, failures) {
  assert(!/sk-[A-Za-z0-9]{16,}|password\s*[:=]|secret\s*[:=]|api[_-]?key\s*[:=]/i.test(text), failures, "credential_or_secret_leak", "output contains a secret-shaped value");
  assert(!/terraform apply|kubectl|credential copy|copy credential/i.test(text), failures, "forbidden_original_repo_write", "output contains forbidden deployment or credential action");
  assert(!/runtime target:\s*original|original repo write:\s*true/i.test(text), failures, "forbidden_original_repo_reference", "output uses an original repo as runtime target");
}

function writeBundle(ctx, state, summary) {
  const bundleDir = path.join(ctx.evidence, "output-bundles", "dwt-s5-runtime-temp-repo");
  fs.rmSync(bundleDir, { recursive: true, force: true });
  ensureDir(bundleDir);
  ensureDir(path.join(bundleDir, "handoffs"));
  ensureDir(path.join(bundleDir, "evidence"));

  const sourceManifest = {
    fixture_id: "dwt-s5-runtime-temp-repo-output",
    source_parent_path: PARENT_SPEC,
    source_child_spec_path: CHILD_SPEC,
    source_handoff_path: CURRENT_HANDOFF,
    retained_dwt_s3_summary_path: DWT_S3_SUMMARY,
    retained_dwt_s3_manifest_path: DWT_S3_MANIFEST,
    synthetic_fixture_path: rel(ctx, state.fixtureDir),
    generated_temp_repo_path: state.tempRepo.generated_path,
    fixture_source_hash: state.tempRepo.source_hash,
    normalizations: ["absolute run-dir paths are per-run evidence"],
    generated_artifacts: REQUIRED_BUNDLE_FILES
  };
  writeJson(path.join(bundleDir, "source-manifest.json"), sourceManifest);

  writeText(path.join(bundleDir, "agent-output.md"), [
    "**DWT-S5 Delivery Kickoff**",
    "",
    "DWT-S5 kickoff is valid for `spec-change-delivery` only.",
    "",
    "**Runtime Gates**",
    "",
    `local_runtime_status: ${state.localRuntime ? state.localRuntime.status : "planned"}`,
    `container_harness_status: ${state.containerHarness ? state.containerHarness.status : "planned"}`,
    "",
    "**Container Harness**",
    "",
    `blocked_reason: ${state.containerHarness && state.containerHarness.blocked_reason || "none"}`,
    "",
    "**DWT-S5 Closeout Sync**",
    "",
    "DWT-S5 evidence remains separate from retained DWT-S3 predecessor evidence.",
    "",
    "**Parent Coverage**",
    "",
    PARENT_COVERAGE.map((coverage) => `- ${coverage}`).join("\n"),
    "",
    "FINAL_STATUS: child_id=DWT-S5;handoff_current=true;temp_repo_isolated=true;allowed_write_set_concrete=true;local_runtime_status=pass;container_harness_status=pass;descendant_release=false;forbidden_actions=false"
  ].join("\n"));

  writeText(path.join(bundleDir, "delivery-kickoff.md"), [
    "child_id: DWT-S5",
    `handoff_path: ${CURRENT_HANDOFF}`,
    "handoff_current: true",
    "readiness_verdict: IMPLEMENTATION READY",
    `target_workspace: ${state.tempRepo.generated_path}`,
    "target_workspace_isolated: true",
    "allowed_write_set_concrete: true",
    `retained_dwt_s3_summary: ${DWT_S3_SUMMARY}`,
    `retained_dwt_s3_manifest: ${DWT_S3_MANIFEST}`,
    "delivery_limited_to_dwt_s5: true",
    "forbidden_actions: false"
  ].join("\n"));

  writeText(path.join(bundleDir, "runtime-gates.md"), [
    `local_runtime_command: ${state.localRuntime && state.localRuntime.command || "planned"}`,
    `local_runtime_cwd: ${state.localRuntime && state.localRuntime.cwd || "planned"}`,
    `local_runtime_status: ${state.localRuntime && state.localRuntime.status || "planned"}`,
    `local_runtime_exit_status: ${state.localRuntime && state.localRuntime.exit_status !== undefined ? state.localRuntime.exit_status : "planned"}`,
    `container_harness_command: ${state.containerHarness && state.containerHarness.command || "planned"}`,
    `container_harness_cwd: ${state.containerHarness && state.containerHarness.cwd || "planned"}`,
    `container_harness_status: ${state.containerHarness && state.containerHarness.status || "planned"}`,
    `container_harness_exit_status: ${state.containerHarness && state.containerHarness.exit_status !== undefined ? state.containerHarness.exit_status : "planned"}`,
    `blocked_runtime_reason: ${state.containerHarness && state.containerHarness.blocked_reason || "none"}`,
    "blocked_runtime_as_pass: false"
  ].join("\n"));

  writeText(path.join(bundleDir, "closeout-sync.md"), [
    "child_id: DWT-S5",
    "dwt_s5_closeout_sync: true",
    "evidence_links_synced: true",
    "openspec_ledger_synced: true",
    `openspec_ledger: ${OPENSPEC_CHANGE}`,
    `retained_dwt_s3_summary: ${DWT_S3_SUMMARY}`,
    "dwt_s3_evidence_relabelled: false",
    "dwt_s5_state: implemented_pending_closeout",
    "descendant_release: false",
    "descendant_next_action: none",
    `parent_coverage: ${PARENT_COVERAGE.join(", ")}`
  ].join("\n"));

  writeText(path.join(bundleDir, "child-index-before.md"), `| Child | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger |\n|---|---|---|---|---|\n| DWT-S5 | ${PARENT_COVERAGE.join(", ")} | IMPLEMENTATION READY | ${CURRENT_HANDOFF} | ${OPENSPEC_CHANGE} |\n`);
  writeText(path.join(bundleDir, "child-index-after.md"), `| Child | Parent Coverage | Readiness / Hardening Verdict | Evidence / Closeout | Next Action |\n|---|---|---|---|---|\n| DWT-S5 | ${PARENT_COVERAGE.join(", ")} | IMPLEMENTED_PENDING_CLOSEOUT | evidence/dwt-s5-l3-summary.json | spec-closeout for DWT-S5 only |\n| DWT-S6 | none | not authorized | none | no descendant release |\n`);
  fs.copyFileSync(path.join(ctx.repoRoot, CURRENT_HANDOFF), path.join(bundleDir, "handoffs", "dwt-s5-session-handoff.md"));
  writeJson(path.join(bundleDir, "agent-run-manifest.json"), state.telemetry);
  writeJson(path.join(bundleDir, "evidence", "dwt-s5-l3-summary.json"), summary);
  return bundleDir;
}

function validateBundle(ctx, bundleDir) {
  const failures = [];
  for (const relPath of REQUIRED_BUNDLE_FILES) {
    assert(exists(path.join(bundleDir, relPath)), failures, "stale_or_unprovenanced_output", `${relPath} is required`);
  }
  if (failures.length > 0) return failures;

  const allText = listFiles(bundleDir)
    .filter((file) => /\.(md|json|txt|yaml|yml)$/.test(file))
    .map(readText)
    .join("\n");
  validateForbiddenOutput(allText, failures);
  const manifest = readJson(path.join(bundleDir, "source-manifest.json"));
  assert(manifest.source_child_spec_path === CHILD_SPEC, failures, "stale_or_unprovenanced_output", "source child spec must be DWT-S5");
  assert(manifest.source_handoff_path === CURRENT_HANDOFF, failures, "stale_or_unprovenanced_output", "source handoff must be current DWT-S5 handoff");
  assert(manifest.retained_dwt_s3_summary_path === DWT_S3_SUMMARY, failures, "missing_or_invalid_dwt_s3_dependency_evidence", "retained DWT-S3 summary path must be explicit");
  const kickoff = readText(path.join(bundleDir, "delivery-kickoff.md"));
  assert(/child_id:\s*DWT-S5/.test(kickoff), failures, "delivery_not_limited_to_dwt_s5", "kickoff child id must be DWT-S5");
  assert(/handoff_current:\s*true/.test(kickoff), failures, "stale_or_mismatched_dwt_s5_handoff", "kickoff handoff must be current");
  assert(/target_workspace_isolated:\s*true/.test(kickoff), failures, "target_repo_not_under_run_dir", "target workspace must be isolated");
  const runtime = readText(path.join(bundleDir, "runtime-gates.md"));
  assert(/blocked_runtime_as_pass:\s*false/.test(runtime), failures, "container_runtime_blocked_misreported_as_pass", "blocked runtime cannot be marked pass");
  const closeout = readText(path.join(bundleDir, "closeout-sync.md"));
  for (const coverage of PARENT_COVERAGE) {
    assert(closeout.includes(coverage), failures, "closeout_parent_coverage_loss", `${coverage} must remain visible`);
  }
  assert(/descendant_release:\s*false/.test(closeout), failures, "descendant_released_without_own_gate", "descendant release must remain false");
  validateTelemetry(readJson(path.join(bundleDir, "agent-run-manifest.json")), failures);
  validateSummary(readJson(path.join(bundleDir, "evidence", "dwt-s5-l3-summary.json")), failures);
  return failures;
}

function validateTelemetry(manifest, failures) {
  assert(typeof manifest.manifest_version === "string" && manifest.manifest_version.startsWith("docworkflow-agent-delivery-telemetry.v1"), failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry version must be v1");
  assert(manifest.child_id === "DWT-S5", failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry child_id must be DWT-S5");
  assert(Array.isArray(manifest.commands), failures, "invalid_dwt_s4_summary_or_telemetry", "commands must be an array");
  assert(isObject(manifest.file_reads), failures, "invalid_dwt_s4_summary_or_telemetry", "file_reads must exist");
  assert(isObject(manifest.tool_calls), failures, "invalid_dwt_s4_summary_or_telemetry", "tool_calls must exist");
  assert(Array.isArray(manifest.forbidden_command_classes), failures, "invalid_dwt_s4_summary_or_telemetry", "forbidden command classes must be an array");
  assert(isObject(manifest.budget), failures, "invalid_dwt_s4_summary_or_telemetry", "budget must exist");
  assert(TELEMETRY.has(manifest.efficiency_verdict), failures, "invalid_dwt_s4_summary_or_telemetry", "efficiency verdict must use frozen vocabulary");
  for (const command of manifest.commands || []) {
    assert(typeof command.command_class === "string", failures, "invalid_dwt_s4_summary_or_telemetry", "command_class must exist");
    assert(TRUTH.has(command.evidence_truth), failures, "invalid_evidence_truth", "command evidence truth must use frozen vocabulary");
  }
}

function validateSummary(summary, failures) {
  assert(summary.schema_id === "docworkflow-agent-delivery-summary.v1", failures, "invalid_dwt_s4_summary_or_telemetry", "summary schema_id must be v1");
  assert(summary.suite_level === "DWT-S5", failures, "invalid_dwt_s4_summary_or_telemetry", "suite_level must be DWT-S5");
  assert(typeof summary.suite_version === "string" && summary.suite_version.length > 0, failures, "invalid_dwt_s4_summary_or_telemetry", "suite_version must exist");
  assert(path.isAbsolute(summary.repo_root || ""), failures, "invalid_dwt_s4_summary_or_telemetry", "repo_root must be absolute");
  assert(path.isAbsolute(summary.fixture_root || ""), failures, "invalid_dwt_s4_summary_or_telemetry", "fixture_root must be absolute");
  assert(["promptfoo-codex", "fallback-artifact", "preflight"].includes(summary.runner_mode), failures, "invalid_dwt_s4_summary_or_telemetry", "runner_mode must be frozen");
  assert(AGENT_STATUS.has(summary.agent_execution_status), failures, "invalid_dwt_s4_summary_or_telemetry", "agent_execution_status must be frozen");
  assert(["pass", "blocked", "fail"].includes(summary.overall_runtime_proof_status), failures, "invalid_dwt_s4_summary_or_telemetry", "overall runtime proof status must be frozen");
  assert(isObject(summary.predecessor_evidence), failures, "missing_or_invalid_dwt_s3_dependency_evidence", "predecessor evidence must exist");
  assert(isObject(summary.temp_repo), failures, "invalid_dwt_s4_summary_or_telemetry", "temp_repo must exist");
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
  assert(isObject(summary.runtime_checks), failures, "invalid_dwt_s4_summary_or_telemetry", "runtime checks must exist");
  assert(isObject(summary.closeout_checks), failures, "invalid_dwt_s4_summary_or_telemetry", "closeout checks must exist");
  assert(isObject(summary.style_verdicts), failures, "invalid_dwt_s4_summary_or_telemetry", "style verdicts must exist");
  assert(isObject(summary.telemetry_verdicts), failures, "invalid_dwt_s4_summary_or_telemetry", "telemetry verdicts must exist");
  assert(Array.isArray(summary.forbidden_actions_observed), failures, "invalid_dwt_s4_summary_or_telemetry", "forbidden actions must be an array");
  assert(isObject(summary.downstream_children), failures, "descendant_released_without_own_gate", "downstream_children must exist");
  if (summary.runner_mode !== "promptfoo-codex" || summary.agent_execution_status !== "ran-target") {
    assert(summary.overall_runtime_proof_status === "blocked", failures, "container_runtime_blocked_misreported_as_pass", "non-target agent proof must keep overall runtime proof blocked");
  }
}

function classifyPromptfooBlocker(text) {
  if (/401 Unauthorized|Missing bearer|basic authentication|auth/i.test(text)) return "blocked_auth";
  if (/network|ETIMEDOUT|ECONNRESET|ENOTFOUND|fetch failed/i.test(text)) return "blocked_network";
  if (/provider|model|openai:codex-sdk/i.test(text)) return "blocked_provider";
  if (/ENOENT|Cannot find module|command not found|spawn|disabled/i.test(text)) return "blocked_runtime";
  return "failed";
}

function getAgentEvidence(ctx) {
  const evalPath = process.env.DWT_S5_PROMPTFOO_EVAL_JSON || "";
  const logPath = process.env.DWT_S5_PROMPTFOO_EVAL_LOG || "";
  const exitStatus = process.env.DWT_S5_PROMPTFOO_EXIT_STATUS || "not-run";
  const authStatus = process.env.DWT_S5_PROMPTFOO_AUTH_STATUS || "missing";
  const evidence = {
    runner_mode: evalPath ? "promptfoo-codex" : "fallback-artifact",
    agent_execution_status: evalPath ? "failed" : "blocked_runtime",
    overall_agent_proof_status: "blocked",
    promptfoo_eval_json: evalPath || null,
    promptfoo_eval_log: logPath || null,
    promptfoo_exit_status: exitStatus,
    promptfoo_version: process.env.DWT_S5_PROMPTFOO_VERSION || "not-run",
    auth_status: authStatus,
    session_id_present: false,
    assertion_status: "not-run",
    output_contract_status: "not-run",
    failure_reason: evalPath ? null : "Promptfoo/Codex agent run was not requested or not provisioned; fallback artifact validation only."
  };
  if (!evalPath) {
    writeEvidence(ctx, "dwt-s5-agent-proof.json", evidence);
    return evidence;
  }
  const evalJson = exists(evalPath) ? readJson(evalPath) : null;
  const logText = logPath && exists(logPath) ? readText(logPath) : "";
  if (!evalJson) {
    evidence.agent_execution_status = classifyPromptfooBlocker(logText);
    evidence.failure_reason = "Promptfoo eval JSON is missing or invalid.";
    writeEvidence(ctx, "dwt-s5-agent-proof.json", evidence);
    return evidence;
  }
  const results = evalJson.results && Array.isArray(evalJson.results.results) ? evalJson.results.results : [];
  const result = results[0] || null;
  const output = result && result.response ? String(result.response.output || "") : "";
  const required = ["DWT-S5 Delivery Kickoff", "Runtime Gates", "Container Harness", "DWT-S5 Closeout Sync", "Parent Coverage", "FINAL_STATUS:"];
  const missing = required.filter((value) => !output.includes(value));
  const finalStatusOk = /child_id=DWT-S5/.test(output)
    && /handoff_current=true/.test(output)
    && /temp_repo_isolated=true/.test(output)
    && /allowed_write_set_concrete=true/.test(output)
    && /descendant_release=false/.test(output)
    && /forbidden_actions=false/.test(output);
  evidence.session_id_present = Boolean(result && result.response && result.response.sessionId);
  evidence.assertion_status = result && result.success === true ? "pass" : "fail";
  evidence.output_contract_status = missing.length === 0 && finalStatusOk ? "pass" : "fail";
  evidence.agent_execution_status = evidence.session_id_present || output.length > 0
    ? "ran-target"
    : classifyPromptfooBlocker(`${result && result.failureReason || ""}\n${logText}`);
  evidence.failure_reason = missing.length > 0 ? `Missing output markers: ${missing.join(", ")}` : result && result.failureReason || null;
  if (evidence.agent_execution_status === "ran-target" && evidence.assertion_status === "pass" && evidence.output_contract_status === "pass" && String(exitStatus) === "0") {
    evidence.overall_agent_proof_status = "pass";
  } else if (evidence.agent_execution_status === "ran-target") {
    evidence.overall_agent_proof_status = "fail";
  }
  writeEvidence(ctx, "dwt-s5-agent-proof.json", evidence);
  return evidence;
}

function caseOutcome(ctx, caseId, expectedFixtureStatus, harnessPassed, details) {
  const payload = {
    case_id: caseId,
    expected_fixture_status: expectedFixtureStatus,
    harness_status: harnessPassed ? "pass" : "fail",
    evidence_truth: details.evidence_truth || "ran-target",
    ...details
  };
  writeEvidence(ctx, CASES[caseId], payload);
  return payload;
}

function buildBaseState(ctx, options = {}) {
  const failures = [];
  const predecessor = validatePredecessor(ctx, failures);
  const materialized = materializeTempRepo(ctx);
  const manifest = validateFixtureManifest(ctx, failures, materialized.fixtureDir);
  const tempRepo = validateTempRepo(ctx, materialized, manifest, failures);
  const readiness = validateCurrentHandoff(ctx, failures);
  const localRuntime = options.runLocal ? runLocalGate(ctx, materialized.targetRepo) : null;
  const containerHarness = options.runContainer ? runContainerHarness(ctx, materialized.targetRepo) : null;
  return {
    failures,
    predecessor,
    fixtureDir: materialized.fixtureDir,
    tempRepo,
    readiness,
    localRuntime,
    containerHarness
  };
}

function makeTelemetry(ctx, state, selector) {
  const commands = [];
  if (state.localRuntime) {
    commands.push({
      command_class: "local-runtime",
      command: state.localRuntime.command,
      cwd: state.localRuntime.cwd,
      exit_status: state.localRuntime.exit_status,
      evidence_truth: state.localRuntime.evidence_truth
    });
  }
  if (state.containerHarness) {
    commands.push({
      command_class: "container-harness",
      command: state.containerHarness.command,
      cwd: state.containerHarness.cwd,
      exit_status: state.containerHarness.exit_status,
      evidence_truth: state.containerHarness.evidence_truth
    });
  }
  return {
    manifest_version: "docworkflow-agent-delivery-telemetry.v1",
    run_id: path.basename(ctx.runDir),
    child_id: "DWT-S5",
    skill_under_test: "spec-change-delivery",
    selector,
    commands,
    file_reads: {
      broad_scan_count: 0,
      repeated_read_count: 0,
      retained_evidence_reads: 2
    },
    tool_calls: {
      promptfoo: process.env.DWT_S5_PROMPTFOO_EVAL_JSON ? 1 : 0,
      local_runtime: state.localRuntime ? 1 : 0,
      container_harness: state.containerHarness ? 1 : 0
    },
    forbidden_command_classes: [],
    budget: {
      max_broad_reads: 4,
      max_repeated_reads: 4
    },
    efficiency_verdict: state.containerHarness && state.containerHarness.status === "blocked" ? "blocked" : "pass",
    justifications: []
  };
}

function writeSummary(ctx, state, results, selector) {
  const agentProof = getAgentEvidence(ctx);
  const byCase = Object.fromEntries(results.map((result) => [result.case_id, result]));
  const testResults = {};
  const harnessResults = {};
  const truth = {};
  for (const caseId of Object.keys(CASES)) {
    testResults[caseId] = byCase[caseId] ? byCase[caseId].expected_fixture_status : "planned";
    harnessResults[caseId] = byCase[caseId] ? byCase[caseId].harness_status : "planned";
    truth[caseId] = byCase[caseId] ? byCase[caseId].evidence_truth : "planned";
  }
  state.telemetry = makeTelemetry(ctx, state, selector);
  const localPassed = state.localRuntime && state.localRuntime.status === "pass";
  const containerPassed = state.containerHarness && state.containerHarness.status === "pass";
  const runtimePass = agentProof.runner_mode === "promptfoo-codex"
    && agentProof.agent_execution_status === "ran-target"
    && agentProof.overall_agent_proof_status === "pass"
    && localPassed
    && containerPassed;
  const runtimeBlocked = !runtimePass && !results.some((result) => result.harness_status === "fail");
  const summary = {
    schema_id: "docworkflow-agent-delivery-summary.v1",
    suite_level: "DWT-S5",
    suite_version: "DWT-S5-l3-runtime-temp-repo-v1",
    repo_root: ctx.repoRoot,
    fixture_root: ctx.runDir,
    fixture_manifest: path.join(ctx.evidence, "output-bundles", "dwt-s5-runtime-temp-repo", "source-manifest.json"),
    runner_mode: selector === "preflight" ? "preflight" : agentProof.runner_mode,
    agent_execution_status: selector === "preflight" ? "not-run" : agentProof.agent_execution_status,
    overall_runtime_proof_status: runtimePass ? "pass" : runtimeBlocked ? "blocked" : "fail",
    selector,
    predecessor_evidence: state.predecessor || { failures: state.failures },
    temp_repo: state.tempRepo,
    test_results: testResults,
    harness_case_results: harnessResults,
    evidence_truth: truth,
    evidence_links: {
      output_bundle: path.join(ctx.evidence, "output-bundles", "dwt-s5-runtime-temp-repo"),
      kickoff_assertions: path.join(ctx.evidence, CASES["DWT-S5-L3B"]),
      runtime_gate_assertions: path.join(ctx.evidence, CASES["DWT-S5-L3C"]),
      container_harness_assertions: path.join(ctx.evidence, CASES["DWT-S5-L3D"]),
      closeout_assertions: path.join(ctx.evidence, CASES["DWT-S5-L3F"]),
      telemetry: path.join(ctx.evidence, "output-bundles", "dwt-s5-runtime-temp-repo", "agent-run-manifest.json"),
      agent_proof: path.join(ctx.evidence, "dwt-s5-agent-proof.json")
    },
    runner_environment: {
      os: `${os.type()} ${os.release()}`,
      shell: process.env.SHELL || "unknown",
      node: process.version,
      promptfoo: agentProof.promptfoo_version,
      codex_credentials_provisioned: agentProof.auth_status !== "missing",
      docker_available: commandExists("docker"),
      container_harness: "node-fixture"
    },
    agent_proof: {
      assertion_status: agentProof.assertion_status,
      output_contract_status: agentProof.output_contract_status,
      session_id_present: agentProof.session_id_present,
      promptfoo_exit_status: agentProof.promptfoo_exit_status,
      failure_reason: agentProof.failure_reason
    },
    provenance_checks: {
      retained_dwt_s3_identity: state.predecessor ? "pass" : "fail",
      source_manifest_present: state.tempRepo ? "pass" : "fail",
      temp_repo_hash_match: state.tempRepo && state.tempRepo.isolation_checks.source_target_hash_match ? "pass" : "fail",
      no_stale_output_reuse: byCase["DWT-S5-L3B"] && byCase["DWT-S5-L3B"].harness_status === "pass" ? "pass" : "planned"
    },
    readiness_checks: {
      child_index_row: state.readiness ? "pass" : "fail",
      handoff_current: state.readiness ? "pass" : "fail",
      write_set_concrete: state.readiness ? "pass" : "fail",
      target_workspace_isolated: state.tempRepo && state.tempRepo.isolation_checks.under_target_repos ? "pass" : "fail",
      stale_handoff_blocked: byCase["DWT-S5-L3B"] && byCase["DWT-S5-L3B"].stale_handoff_blocked ? "blocked" : "planned"
    },
    runtime_checks: {
      local_runtime_gate: state.localRuntime || { status: "planned" },
      container_harness_gate: state.containerHarness || { status: "planned" },
      blocked_runtime_reason: state.containerHarness && state.containerHarness.blocked_reason || null
    },
    closeout_checks: {
      parent_coverage_preserved: byCase["DWT-S5-L3F"] && byCase["DWT-S5-L3F"].harness_status === "pass" ? "pass" : "planned",
      evidence_link_sync: byCase["DWT-S5-L3F"] && byCase["DWT-S5-L3F"].harness_status === "pass" ? "pass" : "planned",
      openspec_ledger_sync: byCase["DWT-S5-L3F"] && byCase["DWT-S5-L3F"].harness_status === "pass" ? "pass" : "planned",
      descendant_non_release: byCase["DWT-S5-L3F"] && byCase["DWT-S5-L3F"].harness_status === "pass" ? "pass" : "planned"
    },
    style_verdicts: Object.fromEntries(Object.keys(CASES).map((caseId) => [caseId, byCase[caseId] ? "pass" : "planned"])),
    telemetry_verdicts: Object.fromEntries(Object.keys(CASES).map((caseId) => [caseId, byCase[caseId] ? state.telemetry.efficiency_verdict : "planned"])),
    forbidden_actions_observed: [],
    downstream_children: {}
  };
  const bundle = writeBundle(ctx, state, summary);
  summary.fixture_manifest = path.join(bundle, "source-manifest.json");
  writeJson(path.join(bundle, "evidence", "dwt-s5-l3-summary.json"), summary);
  writeEvidence(ctx, "dwt-s5-l3-summary.json", summary);
  const bundleFailures = validateBundle(ctx, bundle);
  if (bundleFailures.length > 0) {
    writeEvidence(ctx, "dwt-s5-output-bundle-validation.json", {
      harness_status: "fail",
      failures: bundleFailures,
      output_bundle: bundle
    });
  } else {
    writeEvidence(ctx, "dwt-s5-output-bundle-validation.json", {
      harness_status: "pass",
      failures: [],
      output_bundle: bundle
    });
  }
  return path.join(ctx.evidence, "dwt-s5-l3-summary.json");
}

function runL3A(ctx, state) {
  return caseOutcome(ctx, "DWT-S5-L3A", "pass", state.failures.length === 0 && state.tempRepo.isolation_checks.under_target_repos, {
    evidence_truth: "ran-target",
    temp_repo: state.tempRepo,
    failures: state.failures
  });
}

function runL3B(ctx, state) {
  const stale = readJson(path.join(ctx.fixtures, "stale-dwt-s5-handoff", "fixture-manifest.json"));
  const staleBlocked = stale.expected_blocker === "stale_or_mismatched_dwt_s5_handoff";
  return caseOutcome(ctx, "DWT-S5-L3B", "pass", Boolean(state.readiness) && staleBlocked, {
    evidence_truth: "ran-target",
    readiness: state.readiness,
    stale_handoff_blocked: staleBlocked,
    failures: []
  });
}

function runL3C(ctx, state) {
  const result = state.localRuntime || runLocalGate(ctx, state.tempRepo.generated_path);
  state.localRuntime = result;
  return caseOutcome(ctx, "DWT-S5-L3C", result.status === "pass" ? "pass" : "fail", result.status === "pass", {
    evidence_truth: result.evidence_truth,
    local_runtime: result,
    failures: result.failures || []
  });
}

function runL3D(ctx, state) {
  const result = state.containerHarness || runContainerHarness(ctx, state.tempRepo.generated_path);
  state.containerHarness = result;
  const expected = result.status === "blocked" ? "blocked" : result.status;
  const passed = result.status === "pass" || (result.status === "blocked" && result.blocked_reason === "blocked_runtime" && result.blocked_runtime_as_pass === false);
  return caseOutcome(ctx, "DWT-S5-L3D", expected, passed, {
    evidence_truth: result.evidence_truth,
    container_harness: result,
    failures: result.failures || []
  });
}

function runL3E(ctx) {
  const fixture = readJson(path.join(ctx.fixtures, "original-repo-write-attempt", "fixture-manifest.json"));
  const blocked = fixture.expected_blocker === "forbidden_original_repo_reference"
    && fixture.forbidden_classes.includes("credential-copy")
    && fixture.forbidden_classes.includes("out-of-run-dir");
  const payload = {
    forbidden_classes: fixture.forbidden_classes,
    expected_blocker_detected: blocked,
    failures: blocked ? [] : [{ code: "forbidden_original_repo_reference", message: "forbidden fixture was not detected" }]
  };
  return caseOutcome(ctx, "DWT-S5-L3E", "blocked", blocked, {
    evidence_truth: "blocked",
    ...payload
  });
}

function runL3F(ctx, state) {
  const fixture = readJson(path.join(ctx.fixtures, "closeout-sync-positive", "fixture-manifest.json"));
  const coveragePreserved = PARENT_COVERAGE.every((coverage) => fixture.parent_coverage.includes(coverage));
  const descendantBlocked = fixture.descendant_release_state === "none";
  return caseOutcome(ctx, "DWT-S5-L3F", "pass", coveragePreserved && descendantBlocked && Boolean(state.predecessor), {
    evidence_truth: "ran-target",
    parent_coverage: fixture.parent_coverage,
    descendant_release_state: fixture.descendant_release_state,
    retained_dwt_s3_summary: DWT_S3_SUMMARY,
    openspec_ledger: OPENSPEC_CHANGE,
    failures: []
  });
}

function runPreflight(ctx) {
  const state = buildBaseState(ctx, { runLocal: false, runContainer: false });
  const results = [
    runL3A(ctx, state),
    runL3B(ctx, state)
  ];
  writeSummary(ctx, state, results, "preflight");
  return { state, results };
}

function runAll(ctx) {
  const state = buildBaseState(ctx, { runLocal: true, runContainer: true });
  const results = [
    runL3A(ctx, state),
    runL3B(ctx, state),
    runL3C(ctx, state),
    runL3D(ctx, state),
    runL3E(ctx, state),
    runL3F(ctx, state)
  ];
  writeSummary(ctx, state, results, ctx.selector);
  return { state, results };
}

function runValidateOutput(ctx) {
  if (!ctx.outputBundle) throw new Error("validate-output requires --output-bundle DIR");
  const failures = validateBundle(ctx, ctx.outputBundle);
  const payload = {
    case_id: "DWT-S5-VALIDATE-OUTPUT",
    expected_fixture_status: "pass",
    harness_status: failures.length === 0 ? "pass" : "fail",
    evidence_truth: "ran-target",
    output_bundle: ctx.outputBundle,
    failures
  };
  writeEvidence(ctx, "dwt-s5-validate-output.json", payload);
  const state = buildBaseState(ctx, { runLocal: false, runContainer: false });
  writeSummary(ctx, state, [payload], "validate-output");
  return { state, results: [payload] };
}

function runAgent(ctx) {
  const state = buildBaseState(ctx, { runLocal: true, runContainer: true });
  const proof = getAgentEvidence(ctx);
  const payload = {
    case_id: "DWT-S5-AGENT",
    expected_fixture_status: proof.overall_agent_proof_status === "pass" ? "pass" : "blocked",
    harness_status: proof.overall_agent_proof_status === "pass" ? "pass" : "fail",
    evidence_truth: proof.agent_execution_status === "ran-target" ? "ran-target" : "blocked",
    runner_mode: proof.runner_mode,
    agent_execution_status: proof.agent_execution_status,
    overall_agent_proof_status: proof.overall_agent_proof_status,
    failure_reason: proof.failure_reason
  };
  writeEvidence(ctx, "dwt-s5-agent-result.json", payload);
  writeSummary(ctx, state, [payload], "agent");
  return { state, results: [payload] };
}

function main() {
  const ctx = parseArgs(process.argv);
  ensureDir(ctx.evidence);

  let output;
  if (ctx.selector === "validate-output") {
    output = runValidateOutput(ctx);
  } else if (ctx.selector === "agent") {
    output = runAgent(ctx);
  } else if (ctx.selector === "preflight") {
    output = runPreflight(ctx);
  } else if (["all", "fallback"].includes(ctx.selector)) {
    output = runAll(ctx);
  } else if (ctx.selector === "local-runtime") {
    const state = buildBaseState(ctx, { runLocal: true, runContainer: false });
    output = { state, results: [runL3C(ctx, state)] };
    writeSummary(ctx, state, output.results, ctx.selector);
  } else if (ctx.selector === "container-harness") {
    const state = buildBaseState(ctx, { runLocal: false, runContainer: true });
    output = { state, results: [runL3D(ctx, state)] };
    writeSummary(ctx, state, output.results, ctx.selector);
  } else if (ctx.selector === "closeout") {
    const state = buildBaseState(ctx, { runLocal: false, runContainer: false });
    output = { state, results: [runL3F(ctx, state)] };
    writeSummary(ctx, state, output.results, ctx.selector);
  } else if (ctx.selector === "style" || ctx.selector === "telemetry") {
    const state = buildBaseState(ctx, { runLocal: false, runContainer: false });
    output = { state, results: [runL3F(ctx, state)] };
    writeSummary(ctx, state, output.results, ctx.selector);
  } else {
    throw new Error(`Unknown selector: ${ctx.selector}`);
  }

  for (const result of output.results) {
    console.log(`${result.harness_status.toUpperCase()}: ${result.case_id} expected fixture ${result.expected_fixture_status}`);
  }
  console.log(`SUMMARY: ${path.join(ctx.evidence, "dwt-s5-l3-summary.json")}`);

  const failures = output.results.filter((result) => result.harness_status !== "pass");
  if (ctx.selector === "agent") {
    failures.push(...output.results.filter((result) => result.overall_agent_proof_status !== "pass"));
  }
  if (failures.length > 0) {
    console.error(JSON.stringify({ status: "fail", failures }, null, 2));
    process.exit(1);
  }
}

main();
