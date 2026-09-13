import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
const cli = new URL("../src/cli.ts", import.meta.url);
export function run(args: string[], env: Record<string, string> = {}) {
  const r = spawnSync(process.execPath, [cli.pathname, ...args], {
    env: { ...process.env, ...env },
    encoding: "utf8",
  });
  return {
    code: r.status,
    data: JSON.parse(r.stdout.trim()),
    stderr: r.stderr,
  };
}
test("preflight reports pinned runtime and refuses unavailable provider before creating a wiki", () => {
  const r = run(["preflight"], {
    LLMWIKI_PROVIDER: "openai",
    OPENAI_API_KEY: "",
  });
  assert.equal(r.code, 1);
  assert.equal(r.data.compiler, "34ca1df97b3e60a6700048c48c7cf70c92a9bfdb");
  assert.match(r.data.error, /OPENAI_API_KEY/);
});
