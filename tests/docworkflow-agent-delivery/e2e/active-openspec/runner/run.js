#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const args = parseArgs(process.argv.slice(2));
const repoRoot = path.resolve(__dirname, "../../../../..");
const activeE2eDir = path.resolve(__dirname, "..");
const fixturePath = path.join(activeE2eDir, "fixtures", "large-parent-spec.md");
const runId = args.runId || timestamp();
const runRoot = args.keep
  ? path.join(activeE2eDir, "runs", runId)
  : fs.mkdtempSync(path.join(os.tmpdir(), `active-openspec-e2e-${runId}-`));
const workspace = path.join(runRoot, "workspace");
const targetRoot = path.join(workspace, "target");
const outputDir = path.join(targetRoot, "output");
const partsDir = path.join(outputDir, "parts");

try {
  fs.rmSync(runRoot, { recursive: true, force: true });
  fs.mkdirSync(partsDir, { recursive: true });

  const parentSpec = fs.readFileSync(fixturePath, "utf8");
  const packages = parseWorkPackages(parentSpec);
  if (packages.length !== 5) {
    fail(`Expected 5 work packages, found ${packages.length}`);
  }

  const sliceSummaries = packages.map((pkg) => runSlice(pkg));
  const finalOutput = sliceSummaries
    .sort((a, b) => a.index - b.index)
    .map((summary) => fs.readFileSync(summary.part_path, "utf8").trim())
    .join("\n") + "\n";
  const finalPath = path.join(outputDir, "count.txt");
  fs.writeFileSync(finalPath, finalOutput);

  const expected = "1\n2\n3\n4\n5\n";
  if (finalOutput !== expected) {
    fail(`Final output mismatch. Expected ${JSON.stringify(expected)}, got ${JSON.stringify(finalOutput)}`);
  }

  const summary = {
    schema_id: "docworkflow-agent-delivery-active-openspec-e2e.v1",
    run_id: runId,
    runner_mode: "local-active-openspec-e2e",
    parent_spec: path.relative(repoRoot, fixturePath),
    workspace: path.relative(repoRoot, workspace),
    slice_count: sliceSummaries.length,
    slices: sliceSummaries.map((summary) => ({
      index: summary.index,
      change: summary.change,
      result_value: summary.result_value,
      status: summary.status,
      part_path: path.relative(repoRoot, summary.part_path),
      change_dir: path.relative(repoRoot, summary.change_dir)
    })),
    final_output: path.relative(repoRoot, finalPath),
    final_output_text: finalOutput,
    overall_workflow_status: "pass"
  };

  const summaryPath = path.join(runRoot, "active-openspec-e2e-summary.json");
  fs.writeFileSync(summaryPath, `${JSON.stringify(summary, null, 2)}\n`);
  console.log(JSON.stringify({
    status: "pass",
    run_id: runId,
    kept: args.keep,
    summary: args.keep ? path.relative(repoRoot, summaryPath) : "<temporary>",
    final_output: args.keep ? path.relative(repoRoot, finalPath) : "<temporary>",
    final_output_text: finalOutput
  }, null, 2));
} finally {
  if (!args.keep) {
    fs.rmSync(runRoot, { recursive: true, force: true });
  }
}

function runSlice(pkg) {
  const change = `active-openspec-e2e-slice-${pkg.index}`;
  const changeDir = path.join(workspace, "openspec", "changes", change);
  const specDir = path.join(changeDir, "specs", "active-openspec-e2e-slice");
  fs.mkdirSync(specDir, { recursive: true });

  fs.writeFileSync(path.join(changeDir, "proposal.md"), proposalFor(pkg));
  fs.writeFileSync(path.join(changeDir, "tasks.md"), tasksFor(pkg));
  fs.writeFileSync(path.join(specDir, "spec.md"), specFor(pkg));

  runCommand("openspec", ["validate", change, "--strict", "--no-interactive"], workspace);
  runCommand("dotnet", [
    "run",
    path.join(repoRoot, "skills-repo", "tools", "ValidateActiveOpenSpecScope.cs"),
    "--",
    "--change-dir",
    changeDir,
    "--root",
    workspace,
    "--parent",
    fixturePath
  ], repoRoot);

  const partPath = path.join(partsDir, `part-${pkg.index}.txt`);
  fs.writeFileSync(partPath, `${pkg.result}\n`);

  const summary = {
    schema_id: "docworkflow-agent-delivery-active-openspec-slice.v1",
    index: pkg.index,
    change,
    change_dir: changeDir,
    result_value: pkg.result,
    part_path: partPath,
    status: "pass",
    commands: [
      `openspec validate ${change} --strict --no-interactive`,
      "dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- --change-dir <slice>"
    ]
  };
  fs.writeFileSync(path.join(changeDir, "slice-summary.json"), `${JSON.stringify(summary, null, 2)}\n`);
  return summary;
}

function proposalFor(pkg) {
  return `# Active OpenSpec E2E Slice ${pkg.index}

## Why

The large parent fixture requires result value ${pkg.result}, but implementation
must start from one narrow active OpenSpec change instead of the parent spec.

## What Changes

- Write result value ${pkg.result} for work package ${pkg.index}.
- Keep all other work packages out of this slice.

## Impact

- Write-set: target/output/parts/part-${pkg.index}.txt.
- Final aggregation may read this part after all five slices pass.

## Non-Goals

- Do not write result files for other work packages.
- Do not use child specs, handoff files, launch queues, or visible-session evidence.

## Verification

- openspec validate active-openspec-e2e-slice-${pkg.index} --strict --no-interactive
- dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- --change-dir <slice>
- Final aggregate output must equal 1 through 5, one value per line.
`;
}

function tasksFor(pkg) {
  return `## Tasks

- [x] 1. Create active OpenSpec slice for result value ${pkg.result}.
- [x] 2. Validate the slice with OpenSpec strict validation.
- [x] 3. Validate the slice with the active-scope validator.
- [x] 4. Write only target/output/parts/part-${pkg.index}.txt.
`;
}

function specFor(pkg) {
  return `## ADDED Requirements

### Requirement: Slice ${pkg.index} writes its result

The active OpenSpec E2E workflow SHALL write result value ${pkg.result} for
work package ${pkg.index} without relying on child-spec or session handoff
artifacts.

#### Scenario: Slice ${pkg.index} writes one isolated part

- **GIVEN** the large parent fixture is reference-only context
- **WHEN** active-openspec-e2e-slice-${pkg.index} is implemented
- **THEN** target/output/parts/part-${pkg.index}.txt SHALL contain ${pkg.result}
- **AND** other slice part files SHALL remain out of scope for this slice.
`;
}

function parseWorkPackages(text) {
  const headers = [...text.matchAll(/^### Work Package (\d+): ([^\n]+)$/gm)];
  return headers.map((match, position) => {
    const next = headers[position + 1];
    const bodyStart = match.index + match[0].length;
    const bodyEnd = next ? next.index : text.length;
    const body = text.slice(bodyStart, bodyEnd);
    const index = Number(match[1]);
    const result = Number((body.match(/Result value:\s*(\d+)/) || [])[1]);
    if (!Number.isInteger(index) || !Number.isInteger(result)) {
      fail(`Invalid work package marker near ${match[0].slice(0, 80)}`);
    }
    return { index, title: match[2].trim(), result };
  }).sort((a, b) => a.index - b.index);
}

function runCommand(command, commandArgs, cwd) {
  const result = spawnSync(command, commandArgs, {
    cwd,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });

  if (result.status !== 0) {
    process.stderr.write(result.stdout || "");
    process.stderr.write(result.stderr || "");
    fail(`${command} ${commandArgs.join(" ")} failed with exit ${result.status}`);
  }
}

function parseArgs(argv) {
  const parsed = { keep: false, runId: "" };
  for (let i = 0; i < argv.length; i += 1) {
    switch (argv[i]) {
      case "--keep":
        parsed.keep = true;
        break;
      case "--run-id":
        parsed.runId = argv[++i] || "";
        if (!parsed.runId) fail("Missing --run-id value");
        break;
      case "-h":
      case "--help":
        usage(0);
        break;
      default:
        fail(`Unknown argument: ${argv[i]}`);
    }
  }
  return parsed;
}

function timestamp() {
  return new Date().toISOString().replace(/[-:]/g, "").replace(/\..+/, "Z");
}

function usage(exitCode) {
  const stream = exitCode === 0 ? process.stdout : process.stderr;
  stream.write(`Usage: run-active-openspec-e2e-checks.sh [--keep] [--run-id ID]

Creates a local deterministic E2E run from a large parent fixture, derives five
active OpenSpec changes, validates each slice, and writes count.txt with 1..5.
`);
  process.exit(exitCode);
}

function fail(message) {
  console.error(message);
  process.exit(1);
}
