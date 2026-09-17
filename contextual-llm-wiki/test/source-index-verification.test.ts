import { test } from "node:test";
import assert from "node:assert/strict";
import { writeFile, readFile, rename, rm } from "node:fs/promises";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fixture } from "./support.ts";
const exec = promisify(execFile);

async function qmdDiagnostic(
  f: Awaited<ReturnType<typeof fixture>>,
  collection: string,
  operation = "search",
) {
  const env = {
    ...process.env,
    PATH: process.env.WIKI_QMD_PATH || process.env.PATH,
  };
  const npmRoot = (await exec("npm", ["root", "-g"], { env })).stdout.trim();
  const result = await exec(
    "node",
    [
      "--input-type=module",
      "-e",
      `
    const { createStore } = await import(process.argv[1]);
    const store = await createStore({ dbPath: process.argv[2] });
    try { console.log(JSON.stringify(process.argv[4] === "update" ? await store.update({ collections: [process.argv[3]] }) : await store.searchLex("Freigabe", { collection: process.argv[3], limit: 10 }))); }
    finally { await store.close(); }
  `,
      path.join(npmRoot, "@tobilu/qmd/dist/index.js"),
      f.config.qmd.dbPath,
      collection,
      operation,
    ],
    { env, timeout: 10000 },
  );
  return JSON.parse(result.stdout);
}

test(
  "critical verification: raw stale wiki entries cannot become current evidence or survive a later wiki reindex",
  { timeout: 30000 },
  async () => {
    const f = await fixture();
    try {
      assert.equal((await f.run("maintain")).ok, true);
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
      );
      f.env.OPENAI_API_KEY = "";
      const failed = await f.run("maintain");
      assert.equal(failed.sourceIndex.ok, true);
      assert.equal(failed.wiki.ok, false);
      // The old QMD row may still exist until the independent wiki collection updates.
      const staleRows = await qmdDiagnostic(f, "contextual-wiki-test");
      assert.ok(staleRows.length);
      f.env.OPENAI_API_KEY = "local-test-only";
      const checked = await f.run("query", "--question", "Freigabe");
      assert.equal(checked.fallback, true);
      assert.ok(checked.evidence.every((e: any) => e.kind === "source"));
      assert.doesNotMatch(checked.answer, /Alpha verlangt zwei/);
      const update = await qmdDiagnostic(f, "contextual-wiki-test", "update");
      const afterReindex = await qmdDiagnostic(f, "contextual-wiki-test");
      assert.equal(afterReindex.length, 0);
      const original = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/README.md",
      );
      assert.equal(original.sourceRetrieval, "qmd-source-index");
      await writeFile(
        path.join(f.dir, "critical-acceptance.json"),
        JSON.stringify(
          { failed, staleRows, checked, update, afterReindex, original },
          null,
          2,
        ),
      );
      console.log("Critical stale-index evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: a source snapshot storage error blocks index and model work and preserves recovery",
  { timeout: 20000 },
  async () => {
    const f = await fixture();
    try {
      assert.equal((await f.run("maintain")).ok, true);
      const lastCompleted = (await f.run("status")).lastCompleted;
      const sourceRoot = path.join(
        f.config.output,
        ".state/source-index/files",
      );
      await rename(sourceRoot, sourceRoot + "-preserved");
      await writeFile(sourceRoot, "controlled storage obstruction");
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
      );
      const calls = f.calls.length;
      const failed = await f.run("maintain");
      assert.equal(failed.ok, false);
      assert.equal(failed.sourceIndex.ok, false);
      const providerCallsDuringFailure = f.calls.length - calls;
      assert.equal(providerCallsDuringFailure, 0);
      assert.equal((await f.run("status")).lastCompleted, lastCompleted);
      assert.equal(
        await readFile(path.join(f.dir, "alpha/README.md"), "utf8"),
        "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
      );
      await rm(sourceRoot);
      await rename(sourceRoot + "-preserved", sourceRoot);
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true);
      await writeFile(
        path.join(f.dir, "critical-acceptance.json"),
        JSON.stringify(
          {
            failed,
            repaired,
            providerCallsDuringFailure,
          },
          null,
          2,
        ),
      );
      console.log("Critical storage evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: an unindexed allowed source remains available despite an out-of-scope indexed hit",
  { timeout: 20000 },
  async () => {
    const f = await fixture();
    try {
      assert.equal((await f.run("maintain")).ok, true);
      await writeFile(
        path.join(f.dir, "beta/new.md"),
        "# Freigabe\n\nBeta verlangt vier Freigaben.\n",
      );
      const answer = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "beta/new.md",
      );
      assert.equal(answer.ok, true, JSON.stringify(answer));
      assert.equal(answer.sourceRetrieval, "current-source-scan");
      assert.equal(answer.fallback, true);
      assert.deepEqual(
        answer.originals.map((o: any) => o.id),
        ["beta/new.md"],
      );
      assert.deepEqual(answer.sourceMatches, []);
      assert.match(answer.answer, /Beta verlangt vier/);
      await writeFile(
        path.join(f.dir, "critical-acceptance.json"),
        JSON.stringify(answer, null, 2),
      );
      console.log("Critical unindexed-scope evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);
