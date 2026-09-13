// Bounded public CLI probe. Production configuration is never accepted here.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fixture } from "../test/support.ts";

const [wrapper, phase, existing] = process.argv.slice(2);
const f = await fixture();
const configPath =
  phase === "prepare" ? f.configPath : path.join(existing, "config.json");
async function run(...args: string[]) {
  const result = await new Promise<any>((resolve, reject) => {
    const child = spawn(
      path.join(wrapper, "wiki-node"),
      [path.join(wrapper, "src/cli.ts"), ...args, "--config", configPath],
      { env: { ...process.env, ...f.env } },
    );
    let out = "",
      err = "";
    child.stdout.on("data", (b) => (out += b));
    child.stderr.on("data", (b) => (err += b));
    child.on("error", reject);
    child.on("close", (code) => {
      try {
        resolve({ code, ...JSON.parse(out), stderr: err });
      } catch {
        reject(Error(out + err));
      }
    });
  });
  assert.equal(result.code, 0, JSON.stringify(result));
  assert.equal(result.ok, true, JSON.stringify(result));
  return result;
}
async function knowledge(dir: string): Promise<Record<string, string>> {
  const result: Record<string, string> = {};
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (entry.name === "runs") continue;
    const name = path.join(dir, entry.name);
    if (entry.isDirectory()) Object.assign(result, await knowledge(name));
    else result[name] = (await readFile(name)).toString("base64");
  }
  return result;
}
try {
  const identity = await run("release-status");
  if (phase === "prepare") {
    await run("setup");
    await run("maintain");
    await run("query", "--question", "Freigabe", "--save", "activation-answer");
    console.log(JSON.stringify({ ok: true, fixture: f.dir, identity }));
  } else {
    const output = JSON.parse(await readFile(configPath, "utf8")).output;
    const before = await knowledge(output);
    const state = JSON.parse(
      await readFile(path.join(output, ".state/state.json"), "utf8"),
    );
    assert.ok(
      Object.values<any>(state.pages).some((page) => page.kind === "answer"),
    );
    const answer = await run("query", "--question", "Freigabe");
    assert.equal(answer.fallback, false);
    assert.match(answer.answer, /Alpha verlangt zwei Freigaben/);
    assert.match(answer.answer, /Beta verlangt drei Freigaben/);
    assert.deepEqual(answer.originals.map((s: any) => s.id).sort(), [
      "alpha/README.md",
      "beta/README.md",
    ]);
    assert.ok(
      answer.originals.every((s: any) => s.freshness === "checked-current"),
    );
    const maintained = await run("maintain");
    assert.equal(maintained.noop, true, JSON.stringify(maintained));
    await run("lint");
    assert.deepEqual(
      await knowledge(output),
      before,
      "Existing knowledge or state changed",
    );
    await writeFile(
      path.join(existing, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    await run("maintain");
    const refreshed = await run("query", "--question", "Freigabe");
    assert.match(refreshed.answer, /Alpha verlangt vier Freigaben/);
    assert.doesNotMatch(refreshed.answer, /Alpha verlangt zwei Freigaben/);
    for (const page of Object.values<any>(state.pages).filter(
      (page) => page.kind === "answer",
    )) {
      const text = await readFile(
        path.join(output, "wiki", page.id + ".md"),
        "utf8",
      );
      assert.match(text, /Alpha verlangt vier Freigaben/);
      assert.doesNotMatch(text, /Alpha verlangt zwei Freigaben/);
    }
    await run("lint");
    console.log(
      JSON.stringify({
        ok: true,
        identity,
        savedKnowledgePreserved: true,
        noop: true,
        updatedKnowledgeVerified: true,
        originals: answer.originals.map((s: any) => ({
          id: s.id,
          freshness: s.freshness,
        })),
      }),
    );
  }
} finally {
  await f.close();
}
