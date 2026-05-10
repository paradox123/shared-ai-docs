#!/usr/bin/env node
const path = require("path");
const { spawnSync } = require("child_process");

const fixtureRoot = process.argv[2];
if (!fixtureRoot) {
  console.error("Usage: visible-app-session-evidence.js <fixture-root>");
  process.exit(2);
}

const repoRoot = path.resolve(__dirname, "../../../..");
const tool = path.join(repoRoot, "skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs");
const result = spawnSync("dotnet", ["run", tool, "--", "--fixture", path.resolve(fixtureRoot)], {
  cwd: repoRoot,
  encoding: "utf8"
});

if (result.stdout) process.stdout.write(result.stdout);
if (result.stderr) process.stderr.write(result.stderr);
process.exit(result.status ?? 2);
