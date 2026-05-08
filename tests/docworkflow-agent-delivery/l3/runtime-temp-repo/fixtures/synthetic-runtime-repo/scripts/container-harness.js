#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const cwd = process.cwd();
const manifest = path.join(cwd, "fixture-manifest.json");
if (!fs.existsSync(manifest)) {
  console.error("missing fixture manifest");
  process.exit(1);
}

console.log(JSON.stringify({
  gate: "container-harness",
  status: "pass",
  cwd,
  harness: "node-fixture"
}));
