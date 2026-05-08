#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const cwd = process.cwd();
const pkg = path.join(cwd, "package.json");
if (!fs.existsSync(pkg)) {
  console.error("missing package.json");
  process.exit(1);
}

const parsed = JSON.parse(fs.readFileSync(pkg, "utf8"));
if (parsed.name !== "dwt-s5-synthetic-runtime-repo") {
  console.error("unexpected fixture package name");
  process.exit(1);
}

console.log(JSON.stringify({
  gate: "local-runtime",
  status: "pass",
  cwd,
  fixture: parsed.name
}));
