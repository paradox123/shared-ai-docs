#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const fixtureRoot = process.argv[2];
if (!fixtureRoot) {
  console.error("Usage: visible-app-launcher-s1.js <fixture-root>");
  process.exit(2);
}

const manifestPath = path.join(fixtureRoot, "fixture-manifest.json");
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const failures = [];

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.join(fixtureRoot, file), "utf8"));
}

function readText(file) {
  return fs.readFileSync(path.join(fixtureRoot, file), "utf8");
}

function assert(condition, code, message) {
  if (!condition) failures.push(`${code}: ${message}`);
}

function sha256(text) {
  return crypto.createHash("sha256").update(text, "utf8").digest("hex");
}

function transcriptMethods(file) {
  return readText(file)
    .trim()
    .split(/\n+/)
    .filter(Boolean)
    .map((line) => JSON.parse(line))
    .filter((entry) => entry.direction === "client")
    .map((entry) => entry.method || entry.message?.method)
    .filter(Boolean);
}

function hasOrderedMethods(methods, expected) {
  let cursor = 0;
  for (const method of methods) {
    if (method === expected[cursor]) cursor += 1;
    if (cursor === expected.length) return true;
  }
  return false;
}

function validateCommon(testCase, evidence) {
  assert(evidence.schema_version === "agent-delivery.session-launch.v2", testCase.id, "schema_version must be v2");
  assert(evidence.target_id === "ADV-CAS-S1", testCase.id, "target_id must remain ADV-CAS-S1");
  assert(evidence.initiating_project_cwd === "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs", testCase.id, "initiating_project_cwd mismatch");
  assert(evidence.target_workspace === "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs", testCase.id, "target_workspace mismatch");
  assert(evidence.parent_spec_abbrev_and_number === "ADV-CAS-1", testCase.id, "parent prefix mismatch");
  assert(evidence.session_stage === "Implementation", testCase.id, "session_stage mismatch");
  assert(evidence.child_spec_designation === "ADV-CAS-S1 Launcher Visible-App Adapter", testCase.id, "child designation mismatch");
  assert(evidence.session_title === "ADV-CAS-1: Implementation - ADV-CAS-S1 Launcher Visible-App Adapter", testCase.id, "session title mismatch");
}

function validatePositive(testCase, evidence) {
  validateCommon(testCase, evidence);
  assert(evidence.status === "launched", testCase.id, "positive status must be launched");
  assert(evidence.execution_channel === "app_server", testCase.id, "positive execution_channel must be app_server");
  assert(evidence.adapter_id === "codex-app-server", testCase.id, "adapter_id must be codex-app-server");
  assert(/^[a-f0-9]{64}$/.test(evidence.prompt_sha256 || ""), testCase.id, "prompt_sha256 must be lowercase sha256");
  assert(evidence.prompt_sha256 === sha256(readText(testCase.prompt)), testCase.id, "prompt hash mismatch");
  assert(evidence.session_visibility?.class === "visible_codex_app_session", testCase.id, "visibility class must be visible");
  assert(evidence.session_visibility?.visible_in_codex_app === true, testCase.id, "visible flag must be true");
  assert(evidence.session_visibility?.source_kind_observed === "vscode", testCase.id, "source kind must be vscode");
  assert(evidence.session_visibility?.cwd_observed === evidence.initiating_project_cwd, testCase.id, "observed cwd must match initiating cwd");
  assert(evidence.session_visibility?.title_observed === evidence.session_title, testCase.id, "observed title must match session title");
  assert(Boolean(evidence.session_visibility?.rollout_path), testCase.id, "rollout_path required");
  assert(evidence.app_server?.thread_start_observed === true, testCase.id, "thread/start not observed");
  assert(evidence.app_server?.thread_name_set_observed === true, testCase.id, "thread/name/set not observed");
  assert(evidence.app_server?.turn_start_observed === true, testCase.id, "turn/start not observed");
  assert(evidence.app_server?.turn_completed_status === "completed", testCase.id, "turn must complete");
  assert(evidence.app_server?.thread_list_observed === true, testCase.id, "thread/list not observed");
  assert(hasOrderedMethods(transcriptMethods(testCase.transcript), ["initialize", "thread/start", "thread/name/set", "turn/start", "thread/list"]), testCase.id, "transcript method order mismatch");
}

function validateHeadless(testCase, evidence) {
  assert(evidence.execution_channel === "headless_cli", testCase.id, "headless channel required");
  assert(evidence.session_visibility?.class !== "visible_codex_app_session", testCase.id, "headless must not claim visible class");
  assert(evidence.session_visibility?.visible_in_codex_app === false, testCase.id, "headless visible flag must be false");
}

function validateBlockedSecret(testCase, evidence) {
  const raw = readText(testCase.evidence);
  assert(evidence.status === "blocked", testCase.id, "secret case must block");
  assert(evidence.secret_guard_blocked_prompt_persistence === true, testCase.id, "secret guard marker required");
  assert(!raw.includes("sk-live-secret"), testCase.id, "secret literal leaked into evidence");
  assert(evidence.session_visibility?.visible_in_codex_app !== true, testCase.id, "blocked secret cannot be visible");
}

function validateExpectedFailure(testCase, evidence) {
  const before = failures.length;
  validatePositive(testCase, evidence);
  if (failures.length > before) {
    failures.splice(before);
    return;
  }
  assert(false, testCase.id, "negative fixture unexpectedly satisfied positive contract");
}

for (const testCase of manifest.cases) {
  const evidence = readJson(testCase.evidence);
  const before = failures.length;
  if (testCase.expect === "pass") validatePositive(testCase, evidence);
  else if (testCase.expect === "headless") validateHeadless(testCase, evidence);
  else if (testCase.expect === "blocked-secret") validateBlockedSecret(testCase, evidence);
  else if (testCase.expect === "fail-positive-contract") validateExpectedFailure(testCase, evidence);
  else failures.push(`${testCase.id}: unknown expectation ${testCase.expect}`);
  const status = failures.length === before ? "PASS" : "CHECKED";
  console.log(`${status} ${testCase.id}`);
}

if (failures.length > 0) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log(`RESULT: PASS (${manifest.cases.length} S1 launcher cases)`);
