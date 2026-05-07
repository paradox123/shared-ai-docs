#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const summaryPath = resolve(process.argv[2] ?? 'tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json');
const raw = readFileSync(summaryPath, 'utf8');
const summary = JSON.parse(raw);

const allowedRunner = new Set(['ran-target', 'blocked', 'failed']);
const allowedAssertion = new Set(['pass', 'blocked', 'fail']);
const allowedResult = new Set([
  'ADOPT_PROMPTFOO',
  'ADOPT_WITH_LIMITATIONS',
  'FALLBACK_TO_INSPECT',
  'REOPEN_EVALUATION',
]);

const failures = [];

function requireField(name, predicate, message) {
  if (!predicate(summary[name])) {
    failures.push(`${name}: ${message}`);
  }
}

requireField('child', (value) => value === 'DWT-S0', 'must be DWT-S0');
requireField('promptfoo_version', (value) => value === null || typeof value === 'string', 'must be string or null');
requireField('node_executable', (value) => typeof value === 'string' && value.startsWith('/'), 'must be an absolute path');
requireField('node_version', (value) => typeof value === 'string' && value.startsWith('v'), 'must be a Node version string');
requireField('fixture_root', (value) => typeof value === 'string' && value.length > 0, 'must be present');
requireField('runner_status', (value) => allowedRunner.has(value), 'must be ran-target, blocked, or failed');
requireField('assertion_status', (value) => allowedAssertion.has(value), 'must be pass, blocked, or fail');
requireField('reevaluation_result', (value) => allowedResult.has(value), 'must be an allowed ADR result');
requireField('manual_steps_used', (value) => typeof value === 'boolean', 'must be boolean');
requireField('static_fake_outputs_used', (value) => typeof value === 'boolean', 'must be boolean');
requireField('hidden_normalizations_used', (value) => typeof value === 'boolean', 'must be boolean');
requireField('evidence_links', (value) => value && typeof value === 'object' && !Array.isArray(value), 'must be an object');

if (summary.reevaluation_result === 'ADOPT_PROMPTFOO') {
  if (summary.runner_status !== 'ran-target') {
    failures.push('ADOPT_PROMPTFOO requires runner_status ran-target');
  }
  if (summary.assertion_status !== 'pass') {
    failures.push('ADOPT_PROMPTFOO requires assertion_status pass');
  }
  if (summary.manual_steps_used || summary.static_fake_outputs_used || summary.hidden_normalizations_used) {
    failures.push('ADOPT_PROMPTFOO is forbidden when workaround flags are true');
  }
}

for (const key of ['runner', 'blocker', 'assertions', 'summary', 'adr']) {
  if (typeof summary.evidence_links[key] !== 'string' || summary.evidence_links[key].length === 0) {
    failures.push(`evidence_links.${key}: must be a non-empty path`);
  }
}

if (failures.length > 0) {
  console.error('DWT-S0 spike summary assertion failed:');
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log(`DWT-S0 spike summary assertion passed: ${summary.reevaluation_result}`);

