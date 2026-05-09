#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const FORBIDDEN_PATTERNS = [
  {
    id: "absolute_ki_fuer_kmu",
    regex: /\/Users\/dh\/Documents\/DanielsVault\/ki-fuer-kmu(?:\/|\b)/i
  },
  {
    id: "relative_ki_fuer_kmu",
    regex: /(?:^|["'\s:])ki-fuer-kmu(?:\/|\b)/i
  },
  {
    id: "compatibility_fixture",
    regex: /\bcompatibility_fixture\b/i
  },
  {
    id: "real_product_fixture",
    regex: /\breal_product_fixture\b/i
  },
  {
    id: "kmu_fixture_fallback",
    regex: /\bkmu_fixture_fallback\b/i
  }
];

const TEXT_EXTENSIONS = new Set([".json", ".md", ".txt", ".yaml", ".yml"]);
const POLICY_KEYS = new Set(["forbidden_source_paths", "forbidden_patterns"]);

function usage() {
  console.error("Usage: forbidden-real-fixture.js <file-or-directory> [file-or-directory...]");
}

function listFiles(target) {
  if (!fs.existsSync(target)) {
    return [];
  }
  const stat = fs.statSync(target);
  if (stat.isFile()) {
    return [target];
  }
  if (!stat.isDirectory()) {
    return [];
  }
  const out = [];
  for (const entry of fs.readdirSync(target, { withFileTypes: true })) {
    const full = path.join(target, entry.name);
    if (entry.isDirectory()) {
      out.push(...listFiles(full));
    } else {
      out.push(full);
    }
  }
  return out;
}

function shouldScan(file) {
  return TEXT_EXTENSIONS.has(path.extname(file).toLowerCase());
}

function lineAndColumn(text, index) {
  const before = text.slice(0, index);
  const lines = before.split("\n");
  return {
    line: lines.length,
    column: lines[lines.length - 1].length + 1
  };
}

function scanText(text, file) {
  const findings = [];
  for (const pattern of FORBIDDEN_PATTERNS) {
    const match = pattern.regex.exec(text);
    if (match) {
      findings.push({
        code: pattern.id === "compatibility_fixture" || pattern.id === "real_product_fixture" || pattern.id === "kmu_fixture_fallback"
          ? "compatibility_fixture_detected"
          : "forbidden_real_fixture_path",
        pattern: pattern.id,
        file,
        ...lineAndColumn(text, match.index),
        match: match[0].trim()
      });
    }
  }
  return findings;
}

function scanJsonValue(value, file, pointer) {
  const findings = [];
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      findings.push(...scanJsonValue(item, file, `${pointer}/${index}`));
    });
    return findings;
  }
  if (value && typeof value === "object") {
    for (const [key, item] of Object.entries(value)) {
      if (POLICY_KEYS.has(key)) {
        continue;
      }
      findings.push(...scanJsonValue(item, file, `${pointer}/${key}`));
    }
    return findings;
  }
  if (typeof value === "string") {
    for (const finding of scanText(value, file)) {
      findings.push({ ...finding, field: pointer || "/" });
    }
  }
  return findings;
}

function scanFile(file) {
  if (!shouldScan(file)) {
    return [];
  }
  const text = fs.readFileSync(file, "utf8");
  if (path.extname(file).toLowerCase() === ".json") {
    try {
      return scanJsonValue(JSON.parse(text), file, "");
    } catch (_error) {
      return scanText(text, file);
    }
  }
  return scanText(text, file);
}

function main() {
  const targets = process.argv.slice(2);
  if (targets.length === 0) {
    usage();
    process.exit(2);
  }

  const checked = [];
  const findings = [];
  for (const target of targets) {
    const resolved = path.resolve(target);
    const files = listFiles(resolved);
    if (files.length === 0 && !fs.existsSync(resolved)) {
      findings.push({
        code: "input_not_found",
        pattern: "input_not_found",
        file: resolved,
        line: 0,
        column: 0,
        match: ""
      });
      continue;
    }
    for (const file of files) {
      if (!shouldScan(file)) {
        continue;
      }
      checked.push(file);
      findings.push(...scanFile(file));
    }
  }

  const payload = {
    status: findings.length === 0 ? "pass" : "fail",
    checked_paths: checked,
    forbidden_patterns: FORBIDDEN_PATTERNS.map((pattern) => pattern.id),
    findings
  };
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(findings.length === 0 ? 0 : 1);
}

main();
