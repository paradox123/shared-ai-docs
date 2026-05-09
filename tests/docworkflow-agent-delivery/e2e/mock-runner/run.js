#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { spawnSync } = require("child_process");

const SUMMARY_SCHEMA = "docworkflow-agent-delivery-mock-e2e-summary.v1";
const AGGREGATE_SCHEMA = "docworkflow-agent-delivery-mock-e2e-aggregate.v1";
const SESSION_SCHEMA = "docworkflow-agent-delivery-mock-session.v1";
const DIRECT_SCHEMA = "docworkflow-agent-delivery-mock-direct.v1";
const RUNNER_MODE = "local-mock-session-runner";
const LARGE_CHILDREN = ["ML-C1", "ML-C2", "ML-C3", "ML-C4", "ML-C5"];
const FORBIDDEN_SOURCE_PATHS = [
  "/Users/dh/Documents/DanielsVault/ki-fuer-kmu/**",
  "ki-fuer-kmu/**"
];
const EXTERNAL_DEPENDENCIES = {
  network: "not_used",
  docker: "not_used",
  codex_auth: "not_used",
  external_provider: "not_used",
  manual_start: "not_used"
};
const NEGATIVE_CASES = [
  "manual_start_required",
  "permanent_queued",
  "blocked",
  "failed",
  "output_mismatch",
  "forbidden_fixture_state",
  "external_dependency_attempted"
];

function usage() {
  console.error("Usage: run.js --repo-root DIR --selector large|small|all [--keep] [--run-id ID]");
}

function parseArgs(argv) {
  const options = { keep: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--repo-root") {
      options.repoRoot = argv[++index];
    } else if (arg === "--selector") {
      options.selector = argv[++index];
    } else if (arg === "--keep") {
      options.keep = true;
    } else if (arg === "--run-id") {
      options.runId = argv[++index];
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }
  if (!options.repoRoot || !options.selector) {
    usage();
    process.exit(2);
  }
  if (!["large", "small", "all"].includes(options.selector)) {
    throw new Error(`Unknown selector: ${options.selector}`);
  }
  if (options.runId) {
    assertRunId(options.runId);
  }
  options.repoRoot = path.resolve(options.repoRoot);
  options.suiteDir = path.join(options.repoRoot, "tests/docworkflow-agent-delivery");
  options.e2eDir = path.join(options.suiteDir, "e2e");
  options.mockDataDir = path.join(options.suiteDir, "mock-data");
  return options;
}

function assertRunId(runId) {
  if (!/^[A-Za-z0-9._-]+$/.test(runId) || runId.includes("..") || runId === "." || runId === "-") {
    throw new Error("--run-id must match ^[A-Za-z0-9._-]+$ and must not contain path traversal");
  }
}

function utcStamp() {
  return new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function writeJson(file, value) {
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeText(file, value) {
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, value);
}

function sha256File(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function relative(root, target) {
  return path.relative(root, target).split(path.sep).join("/");
}

function assertInside(parent, target, label) {
  const rel = path.relative(parent, target);
  if (rel.startsWith("..") || path.isAbsolute(rel)) {
    throw new Error(`${label} escapes run root: ${target}`);
  }
}

function loadManifest(options, fixtureDirName) {
  const fixtureDir = path.join(options.mockDataDir, fixtureDirName);
  const manifestPath = path.join(fixtureDir, "manifest.json");
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`Missing accepted fixture manifest: ${manifestPath}`);
  }
  return { fixtureDir, manifestPath, manifest: readJson(manifestPath) };
}

function runCommand(command, args, cwd) {
  const result = spawnSync(command, args, { cwd, encoding: "utf8" });
  return {
    status: result.status,
    stdout: result.stdout.trim(),
    stderr: result.stderr.trim()
  };
}

function createRunRoot(options) {
  const runId = options.runId || `${utcStamp()}-${options.selector}`;
  let runRoot;
  let disposable = false;
  if (options.keep) {
    runRoot = path.join(options.e2eDir, "evidence", runId);
    if (fs.existsSync(runRoot)) {
      throw new Error(`Run evidence already exists: ${runRoot}`);
    }
  } else {
    runRoot = fs.mkdtempSync(path.join(fs.realpathSync("/tmp"), `docworkflow-agent-delivery-mock-${options.selector}.`));
    disposable = true;
  }
  ensureDir(runRoot);
  return { runId, runRoot, disposable };
}

function writePolicyEvidence(runRoot) {
  const file = path.join(runRoot, "forbidden-path-policy.json");
  writeJson(file, {
    schema_id: "docworkflow-agent-delivery-mock-forbidden-policy.v1",
    forbidden_source_paths: FORBIDDEN_SOURCE_PATHS,
    policy_source: "accepted-md-e2e-1"
  });
  return file;
}

function forbiddenRefs(runRoot, policyFile) {
  return [
    {
      policy_source: "accepted-md-e2e-1",
      policy_file: relative(runRoot, policyFile),
      forbidden_source_paths_count: FORBIDDEN_SOURCE_PATHS.length,
      forbidden_source_paths_sha256: crypto.createHash("sha256").update(JSON.stringify(FORBIDDEN_SOURCE_PATHS)).digest("hex")
    }
  ];
}

function writeTelemetry(runRoot, selector, runId) {
  const file = path.join(runRoot, "command-telemetry.json");
  writeJson(file, {
    schema_id: "docworkflow-agent-delivery-mock-command-telemetry.v1",
    run_id: runId,
    selector,
    runner_mode: RUNNER_MODE,
    external_dependencies: EXTERNAL_DEPENDENCIES,
    dependency_attempts: [],
    command_contract: {
      network: "not_used",
      docker: "not_used",
      codex_auth: "not_used",
      manual_start: "not_used"
    }
  });
  return file;
}

function writeNegativeFixtures(options) {
  const fixtureDir = path.join(options.e2eDir, "fixtures/mock-runner-negative");
  ensureDir(fixtureDir);
  const fixtureFile = path.join(fixtureDir, "negative-cases.json");
  if (!fs.existsSync(fixtureFile)) {
    writeJson(fixtureFile, {
      schema_id: "docworkflow-agent-delivery-mock-negative-fixtures.v1",
      cases: NEGATIVE_CASES.map((id) => ({
        id,
        expected_positive_pass: false
      }))
    });
  }
  return fixtureFile;
}

function evaluateNegativeCase(caseId) {
  const base = {
    schema_id: SUMMARY_SCHEMA,
    selector: "large",
    runner_mode: RUNNER_MODE,
    overall_workflow_status: "pass",
    evidence_truth: "ran-target",
    external_dependencies: { ...EXTERNAL_DEPENDENCIES },
    expected_outputs_status: "pass",
    forbidden_fixture_status: "pass",
    session_chain_status: "pass"
  };
  if (caseId === "manual_start_required") {
    base.session_evidence = [{ launch_status: "manual_start_required", final_status: "ran-target", closeout_status: "closed" }];
  } else if (caseId === "permanent_queued") {
    base.session_evidence = [{ launch_status: "queued", state_transitions: [{ state: "queued" }], final_status: "queued", closeout_status: "blocked" }];
  } else if (caseId === "blocked") {
    base.session_evidence = [{ launch_status: "blocked", final_status: "blocked", closeout_status: "blocked" }];
  } else if (caseId === "failed") {
    base.session_evidence = [{ launch_status: "failed", final_status: "failed", closeout_status: "failed" }];
  } else if (caseId === "output_mismatch") {
    base.expected_outputs_status = "fail";
  } else if (caseId === "forbidden_fixture_state") {
    base.forbidden_fixture_status = "fail";
  } else if (caseId === "external_dependency_attempted") {
    base.external_dependencies = { ...EXTERNAL_DEPENDENCIES, network: "attempted" };
  }
  const reasons = positivePassBlockers(base);
  return {
    id: caseId,
    status: reasons.length > 0 ? "pass" : "fail",
    expected_positive_pass: false,
    blocked_reasons: reasons
  };
}

function positivePassBlockers(summary) {
  const blockers = [];
  if (summary.overall_workflow_status === "pass") {
    if (summary.expected_outputs_status !== "pass") blockers.push("expected_outputs_status");
    if (summary.forbidden_fixture_status !== "pass") blockers.push("forbidden_fixture_status");
    if (summary.evidence_truth !== "ran-target") blockers.push("evidence_truth");
    for (const [key, value] of Object.entries(summary.external_dependencies || {})) {
      if (value !== "not_used") blockers.push(`external_dependency:${key}`);
    }
    for (const session of summary.session_evidence || []) {
      if (["manual_start_required", "blocked", "failed"].includes(session.launch_status)) blockers.push(`launch_status:${session.launch_status}`);
      if (session.launch_status === "queued" && !(session.state_transitions || []).some((step) => step.state === "resumed")) {
        blockers.push("permanent_queued");
      }
      if (["queued", "manual_start_required", "blocked", "failed"].includes(session.final_status)) blockers.push(`final_status:${session.final_status}`);
      if (session.closeout_status !== "closed") blockers.push("closeout_not_closed");
    }
  }
  return blockers;
}

function writeNegativeEvidence(options, runRoot) {
  const fixtureFile = writeNegativeFixtures(options);
  const cases = NEGATIVE_CASES.map(evaluateNegativeCase);
  const evidence = {
    schema_id: "docworkflow-agent-delivery-mock-negative-guards.v1",
    status: cases.every((item) => item.status === "pass") ? "pass" : "fail",
    fixture: path.relative(options.repoRoot, fixtureFile).split(path.sep).join("/"),
    cases
  };
  writeJson(path.join(runRoot, "negative-guard-evidence.json"), evidence);
  if (evidence.status !== "pass") {
    throw new Error("Negative guard assertions failed");
  }
  return evidence;
}

function makeTransitionFactory() {
  let tick = 0;
  return function transition(state) {
    tick += 1;
    return {
      state,
      at: new Date(Date.UTC(2026, 4, 9, 8, 0, tick)).toISOString()
    };
  };
}

function renderChildIndex(children) {
  const lines = [
    "| Child | Target Output Action | Predecessor | Readiness State | Handoff Path | Allowed Write-Set | Final State |",
    "|---|---|---|---|---|---|---|"
  ];
  for (const child of children) {
    const index = Number(child.replace("ML-C", ""));
    const predecessor = index === 1 ? "parent-control" : `ML-C${index - 1}`;
    lines.push(`| ${child} | append_or_set_line:${index} | ${predecessor} | implementation-ready | large/parent-control/handoffs/${child}-handoff.md | large/mock-target/output/count.txt; large/sessions/${child}-delivery.json | ran-target + closed |`);
  }
  return `${lines.join("\n")}\n`;
}

function runLarge(options, runRoot, runId, policyFile) {
  const { fixtureDir, manifest } = loadManifest(options, "large-parent");
  const largeRoot = path.join(runRoot, "large");
  const parentRoot = path.join(largeRoot, "parent-control");
  const sessionsRoot = path.join(largeRoot, "sessions");
  const outputRoot = path.join(largeRoot, "mock-target/output");
  const outputEvidenceRoot = path.join(largeRoot, "output-evidence");
  ensureDir(parentRoot);
  ensureDir(sessionsRoot);
  ensureDir(outputRoot);
  ensureDir(outputEvidenceRoot);

  if (manifest.fixture_id !== "mock-large-parent-v1" || manifest.expected_delivery_mode !== "parent_child") {
    throw new Error("Large manifest contract mismatch");
  }
  if (JSON.stringify(manifest.expected_children) !== JSON.stringify(LARGE_CHILDREN)) {
    throw new Error("Large manifest child list mismatch");
  }

  writeText(path.join(parentRoot, "child-index.md"), renderChildIndex(LARGE_CHILDREN));
  const transition = makeTransitionFactory();
  const parentSummary = {
    schema_id: "docworkflow-agent-delivery-mock-parent-control.v1",
    fixture_id: manifest.fixture_id,
    state_transitions: [transition("started"), transition("ran-target"), transition("closed")],
    generated_children: LARGE_CHILDREN,
    final_status: "closed"
  };
  writeJson(path.join(parentRoot, "parent-control-summary.json"), parentSummary);

  const countFile = path.join(outputRoot, "count.txt");
  writeText(countFile, "");
  const sessionEvidence = [];
  for (let index = 0; index < LARGE_CHILDREN.length; index += 1) {
    const childId = LARGE_CHILDREN[index];
    const number = String(index + 1);
    const childSpecPath = path.join(parentRoot, `child-specs/${childId}.md`);
    const handoffPath = path.join(parentRoot, `handoffs/${childId}-handoff.md`);
    const sessionPath = path.join(sessionsRoot, `${childId}-delivery.json`);
    writeText(childSpecPath, [
      `# ${childId} Mock Child Spec`,
      "",
      `- Source fixture id: ${manifest.fixture_id}`,
      `- Child id: ${childId}`,
      `- Required number: ${number}`,
      `- Allowed Write-Set: large/mock-target/output/count.txt; large/sessions/${childId}-delivery.json`,
      `- Expected session evidence file: large/sessions/${childId}-delivery.json`,
      "- External dependencies: none"
    ].join("\n") + "\n");
    writeText(handoffPath, [
      `# ${childId} Mock Handoff`,
      "",
      `- Child Spec: large/parent-control/child-specs/${childId}.md`,
      `- Mock Target Root: large/mock-target`,
      `- Session Evidence: large/sessions/${childId}-delivery.json`,
      `- Allowed Write-Set: large/mock-target/output/count.txt; large/sessions/${childId}-delivery.json`
    ].join("\n") + "\n");

    const before = fs.readFileSync(countFile, "utf8");
    const expectedBefore = Array.from({ length: index }, (_value, itemIndex) => `${itemIndex + 1}\n`).join("");
    if (before !== expectedBefore) {
      throw new Error(`${childId} write boundary failed before write`);
    }
    fs.appendFileSync(countFile, `${number}\n`);
    const transitions = index % 2 === 1
      ? [transition("queued"), transition("resumed"), transition("ran-target"), transition("closed")]
      : [transition("started"), transition("ran-target"), transition("closed")];
    const session = {
      schema_id: SESSION_SCHEMA,
      fixture_id: manifest.fixture_id,
      session_step_id: `${childId}-delivery`,
      target_child_id: childId,
      sequence_index: index + 1,
      source_handoff: relative(runRoot, handoffPath),
      launch_status: index % 2 === 1 ? "queued" : "started",
      launch_mechanism: index % 2 === 1 ? "local-mock-session-runner-queue" : RUNNER_MODE,
      state_transitions: transitions,
      target_workspace: path.join(largeRoot, "mock-target"),
      allowed_write_set: [
        `large/mock-target/output/count.txt#line-${index + 1}`,
        `large/sessions/${childId}-delivery.json`,
        `large/parent-control/handoffs/${childId}-handoff.md`
      ],
      forbidden_paths_checked: forbiddenRefs(runRoot, policyFile),
      result_evidence: {
        output: "large/mock-target/output/count.txt",
        summary: "large/mock-e2e-summary.json",
        closeout: "large/parent-control/parent-control-summary.json",
        wrote_line: index + 1
      },
      final_status: "ran-target",
      closeout_status: "closed",
      child_output_action: manifest.child_output_contract[childId],
      write_boundary_status: "pass",
      external_dependency_status: "not_used"
    };
    assertInside(runRoot, session.target_workspace, `${childId} target_workspace`);
    writeJson(sessionPath, session);
    sessionEvidence.push(relative(runRoot, sessionPath));
  }

  const actualContent = fs.readFileSync(countFile, "utf8");
  if (actualContent !== manifest.expected_output_content) {
    throw new Error("Large output content mismatch");
  }
  const countSha = sha256File(countFile);
  const countShaFile = path.join(outputEvidenceRoot, "count.txt.sha256");
  writeText(countShaFile, `${countSha}  large/mock-target/output/count.txt\n`);

  const generatedArtifacts = {
    child_index_count: 1,
    child_spec_count: LARGE_CHILDREN.length,
    child_handoff_count: LARGE_CHILDREN.length,
    child_session_count: LARGE_CHILDREN.length
  };
  const summary = {
    schema_id: SUMMARY_SCHEMA,
    run_id: runId,
    selector: "large",
    fixture_id: manifest.fixture_id,
    fixture_version: manifest.fixture_version,
    spec_type: manifest.spec_type,
    sizing_decision: "parent_child",
    overall_workflow_status: "pass",
    session_chain_status: "pass",
    expected_outputs_status: "pass",
    forbidden_fixture_status: "pass",
    evidence_truth: "ran-target",
    runner_mode: RUNNER_MODE,
    session_strategy: manifest.session_strategy,
    mock_target_root: path.join(largeRoot, "mock-target"),
    session_evidence: sessionEvidence,
    output_evidence: [
      {
        path: "large/mock-target/output/count.txt",
        sha256_path: "large/output-evidence/count.txt.sha256",
        sha256: countSha
      }
    ],
    forbidden_paths_checked: forbiddenRefs(runRoot, policyFile),
    generated_artifacts: generatedArtifacts,
    external_dependencies: EXTERNAL_DEPENDENCIES,
    negative_cases: []
  };
  writeJson(path.join(largeRoot, "mock-e2e-summary.json"), summary);
  writeJson(path.join(runRoot, "mock-e2e-summary.json"), summary);
  return summary;
}

function runSmall(options, runRoot, runId, policyFile) {
  const { manifest } = loadManifest(options, "small-direct");
  const smallRoot = path.join(runRoot, "small");
  const outputRoot = path.join(smallRoot, "mock-target/output");
  const outputEvidenceRoot = path.join(smallRoot, "output-evidence");
  ensureDir(outputRoot);
  ensureDir(outputEvidenceRoot);

  if (manifest.fixture_id !== "mock-small-direct-v1" || manifest.expected_delivery_mode !== "direct") {
    throw new Error("Small manifest contract mismatch");
  }
  if (manifest.expected_children.length !== 0) {
    throw new Error("Small manifest cannot declare children");
  }

  const resultFile = path.join(outputRoot, "small-direct-result.json");
  writeJson(resultFile, manifest.expected_output_json);
  const resultSha = sha256File(resultFile);
  const resultShaFile = path.join(outputEvidenceRoot, "small-direct-result.json.sha256");
  writeText(resultShaFile, `${resultSha}  small/mock-target/output/small-direct-result.json\n`);

  const forbiddenChildArtifacts = [
    path.join(smallRoot, "child-index.md"),
    path.join(smallRoot, "child-specs"),
    path.join(smallRoot, "handoffs"),
    path.join(smallRoot, "child-session-handoffs"),
    path.join(smallRoot, "sessions")
  ];
  const existingForbidden = forbiddenChildArtifacts.filter((target) => fs.existsSync(target));
  if (existingForbidden.length > 0) {
    throw new Error(`Small run created forbidden child artifacts: ${existingForbidden.join(", ")}`);
  }

  const directEvidence = {
    schema_id: DIRECT_SCHEMA,
    fixture_id: manifest.fixture_id,
    sizing_decision: "direct",
    state_transitions: [
      { state: "started", at: new Date(Date.UTC(2026, 4, 9, 9, 0, 1)).toISOString() },
      { state: "ran-target", at: new Date(Date.UTC(2026, 4, 9, 9, 0, 2)).toISOString() },
      { state: "closed", at: new Date(Date.UTC(2026, 4, 9, 9, 0, 3)).toISOString() }
    ],
    final_status: "ran-target",
    closeout_status: "closed",
    child_artifact_status: "absent",
    output_evidence: {
      path: "small/mock-target/output/small-direct-result.json",
      sha256_path: "small/output-evidence/small-direct-result.json.sha256",
      sha256: resultSha
    },
    external_dependency_status: "not_used"
  };
  writeJson(path.join(smallRoot, "direct-delivery.json"), directEvidence);

  const summary = {
    schema_id: SUMMARY_SCHEMA,
    run_id: runId,
    selector: "small",
    fixture_id: manifest.fixture_id,
    fixture_version: manifest.fixture_version,
    spec_type: manifest.spec_type,
    sizing_decision: "direct",
    overall_workflow_status: "pass",
    session_chain_status: "not_applicable",
    expected_outputs_status: "pass",
    forbidden_fixture_status: "pass",
    evidence_truth: "ran-target",
    runner_mode: RUNNER_MODE,
    session_strategy: manifest.session_strategy,
    mock_target_root: path.join(smallRoot, "mock-target"),
    session_evidence: [],
    output_evidence: [
      {
        path: "small/mock-target/output/small-direct-result.json",
        sha256_path: "small/output-evidence/small-direct-result.json.sha256",
        sha256: resultSha
      }
    ],
    forbidden_paths_checked: forbiddenRefs(runRoot, policyFile),
    generated_artifacts: {
      child_index_count: 0,
      child_spec_count: 0,
      child_handoff_count: 0,
      child_session_count: 0
    },
    external_dependencies: EXTERNAL_DEPENDENCIES,
    negative_cases: []
  };
  writeJson(path.join(smallRoot, "mock-e2e-summary.json"), summary);
  writeJson(path.join(runRoot, "mock-e2e-summary.json"), summary);
  return summary;
}

function writeAggregate(runRoot, runId, largeSummary, smallSummary, policyFile) {
  const aggregate = {
    schema_id: AGGREGATE_SCHEMA,
    run_id: runId,
    large_summary: "large/mock-e2e-summary.json",
    small_summary: "small/mock-e2e-summary.json",
    large_status: largeSummary.overall_workflow_status,
    small_status: smallSummary.overall_workflow_status,
    overall_workflow_status: largeSummary.overall_workflow_status === "pass" && smallSummary.overall_workflow_status === "pass" ? "pass" : "fail",
    forbidden_fixture_status: largeSummary.forbidden_fixture_status === "pass" && smallSummary.forbidden_fixture_status === "pass" ? "pass" : "fail",
    created_at: new Date().toISOString(),
    runner_mode: RUNNER_MODE
  };
  writeJson(path.join(runRoot, "aggregate-summary.json"), aggregate);
  const summary = {
    schema_id: SUMMARY_SCHEMA,
    run_id: runId,
    selector: "all",
    fixture_id: "mock-e2e-all-v1",
    fixture_version: "1.0.0",
    spec_type: "aggregate",
    sizing_decision: "aggregate",
    overall_workflow_status: aggregate.overall_workflow_status,
    session_chain_status: aggregate.overall_workflow_status === "pass" ? "pass" : "fail",
    expected_outputs_status: aggregate.overall_workflow_status,
    forbidden_fixture_status: aggregate.forbidden_fixture_status,
    evidence_truth: aggregate.overall_workflow_status === "pass" ? "ran-target" : "failed",
    runner_mode: RUNNER_MODE,
    session_strategy: "aggregate",
    mock_target_root: {
      large: largeSummary.mock_target_root,
      small: smallSummary.mock_target_root
    },
    session_evidence: largeSummary.session_evidence,
    output_evidence: [
      ...largeSummary.output_evidence,
      ...smallSummary.output_evidence
    ],
    forbidden_paths_checked: forbiddenRefs(runRoot, policyFile),
    generated_artifacts: {
      large: largeSummary.generated_artifacts,
      small: smallSummary.generated_artifacts
    },
    external_dependencies: EXTERNAL_DEPENDENCIES,
    negative_cases: []
  };
  writeJson(path.join(runRoot, "mock-e2e-summary.json"), summary);
  return { aggregate, summary };
}

function validateSummaries(options, runRoot, summaries) {
  const validator = path.join(options.e2eDir, "validators/mock-e2e-summary.js");
  for (const summaryPath of summaries) {
    const result = runCommand(process.execPath, [validator, summaryPath], options.repoRoot);
    if (result.status !== 0) {
      throw new Error(`Summary validation failed for ${summaryPath}\n${result.stdout}\n${result.stderr}`);
    }
  }
}

function runForbiddenScan(options, runRoot) {
  const validator = path.join(options.e2eDir, "validators/forbidden-real-fixture.js");
  const result = runCommand(process.execPath, [validator, runRoot], options.repoRoot);
  const payload = {
    schema_id: "docworkflow-agent-delivery-mock-forbidden-scan.v1",
    target: runRoot,
    validator: relative(options.repoRoot, validator),
    status: result.status === 0 ? "pass" : "fail",
    stdout_json: result.stdout ? JSON.parse(result.stdout) : null,
    stderr: result.stderr
  };
  writeJson(path.join(runRoot, "forbidden-real-fixture.json"), payload);
  if (result.status !== 0) {
    throw new Error(`Forbidden real fixture scan failed for ${runRoot}`);
  }
}

function emitKeepMessage(options, runRoot) {
  if (options.keep) {
    console.log(`Evidence: ${runRoot}`);
    console.log(`Summary: ${path.join(runRoot, "mock-e2e-summary.json")}`);
  }
}

function main() {
  let options;
  let run;
  try {
    options = parseArgs(process.argv.slice(2));
    run = createRunRoot(options);
    const policyFile = writePolicyEvidence(run.runRoot);
    writeTelemetry(run.runRoot, options.selector, run.runId);
    writeNegativeEvidence(options, run.runRoot);

    const summaryPaths = [];
    let largeSummary;
    let smallSummary;
    if (options.selector === "large") {
      largeSummary = runLarge(options, run.runRoot, run.runId, policyFile);
      summaryPaths.push(path.join(run.runRoot, "large/mock-e2e-summary.json"), path.join(run.runRoot, "mock-e2e-summary.json"));
    } else if (options.selector === "small") {
      smallSummary = runSmall(options, run.runRoot, run.runId, policyFile);
      summaryPaths.push(path.join(run.runRoot, "small/mock-e2e-summary.json"), path.join(run.runRoot, "mock-e2e-summary.json"));
    } else {
      largeSummary = runLarge(options, run.runRoot, `${run.runId}-large`, policyFile);
      smallSummary = runSmall(options, run.runRoot, `${run.runId}-small`, policyFile);
      writeAggregate(run.runRoot, run.runId, largeSummary, smallSummary, policyFile);
      summaryPaths.push(
        path.join(run.runRoot, "large/mock-e2e-summary.json"),
        path.join(run.runRoot, "small/mock-e2e-summary.json"),
        path.join(run.runRoot, "mock-e2e-summary.json"),
        path.join(run.runRoot, "aggregate-summary.json")
      );
    }
    validateSummaries(options, run.runRoot, summaryPaths);
    runForbiddenScan(options, run.runRoot);
    emitKeepMessage(options, run.runRoot);
    console.log("RESULT: PASS");
  } catch (error) {
    if (run && run.runRoot) {
      try {
        writeJson(path.join(run.runRoot, "mock-e2e-summary.json"), {
          schema_id: SUMMARY_SCHEMA,
          run_id: run.runId,
          selector: options ? options.selector : "unknown",
          overall_workflow_status: "fail",
          evidence_truth: "failed",
          runner_mode: RUNNER_MODE,
          error: error.message
        });
      } catch (_writeError) {
        // Keep the original failure visible.
      }
    }
    console.error(error.message);
    process.exit(1);
  } finally {
    if (run && run.disposable) {
      fs.rmSync(run.runRoot, { recursive: true, force: true });
    }
  }
}

main();
