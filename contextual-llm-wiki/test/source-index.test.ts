import { test } from "node:test";
import assert from "node:assert/strict";
import { writeFile, readFile } from "node:fs/promises";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fixture } from "./support.ts";
const exec = promisify(execFile);

async function helper(
  f: Awaited<ReturnType<typeof fixture>>,
  name: string,
  reconcile: string,
) {
  let output;
  try {
    output = await exec(
      "python3",
      [
        new URL("../scripts/maintain-index.py", import.meta.url).pathname,
        "--config",
        f.configPath,
        "--artifacts",
        path.join(f.dir, name),
        "--qmd",
        "/usr/bin/false",
        "--reconcile",
        reconcile,
      ],
      { env: { ...process.env, ...f.env }, timeout: 30000 },
    );
  } catch (error: any) {
    output = error;
  }
  return JSON.parse(output.stdout.trim().split("\n").at(-1));
}

test(
  "the public helper indexes originals before a failing first compilation and WikiQuery uses real QMD hits",
  { timeout: 45000 },
  async () => {
    const f = await fixture();
    try {
      const reconcile = path.join(f.dir, "reconcile.py");
      await writeFile(reconcile, 'print(\'{"status":"ok"}\')\n');
      f.fail((body) => !!body.tools);
      const report = await helper(f, "job", reconcile);
      assert.equal(report.ok, false);
      assert.equal(
        report.contexts[0]?.sourceIndex?.ok,
        true,
        JSON.stringify(report),
      );
      assert.equal(report.contexts[0].wiki.ok, false);
      const answer = await f.run("query", "--question", "Freigabe");
      assert.equal(answer.ok, true, JSON.stringify(answer));
      assert.equal(answer.fallback, true);
      assert.equal(answer.sourceRetrieval, "qmd-source-index");
      assert.equal(answer.sourceMatches.length, 2);
      assert.equal(answer.originals.length, 2);
      assert.ok(
        answer.originals.every((o: any) => o.freshness === "checked-current"),
      );
      assert.equal((await f.run("status")).lastCompleted, null);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify({ report, answer }, null, 2),
      );
      console.log("Source index evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "updated originals exclude stale synthesis, respect private/source limits and retain no-op searchability",
  { timeout: 45000 },
  async () => {
    const f = await fixture();
    try {
      f.config.repos[1].id = "private";
      await f.saveConfig();
      assert.equal((await f.run("maintain")).ok, true);
      const before = await f.run("status");
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
      );
      f.fail((b) => !!b.tools);
      const failed = await f.run("maintain");
      assert.equal(failed.ok, false);
      assert.equal(failed.sourceIndex.ok, true);
      assert.equal((await f.run("status")).lastCompleted, before.lastCompleted);
      assert.equal(
        (await f.run("search", "--question", "Freigabe")).results.length,
        0,
      );
      const updated = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/README.md",
      );
      assert.equal(updated.sourceRetrieval, "qmd-source-index");
      assert.match(updated.answer, /vier Freigaben/);
      assert.doesNotMatch(updated.answer, /zwei Freigaben/);
      assert.deepEqual(
        updated.originals.map((o: any) => o.id),
        ["alpha/README.md"],
      );
      const personal = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--repo",
        "private",
      );
      assert.deepEqual(
        personal.originals.map((o: any) => o.id),
        ["private/README.md"],
      );
      // A subsequent edit must never be certified using the older indexed version.
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\n\nAlpha verlangt zwei Freigaben.\n",
      );
      const drift = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/README.md",
      );
      assert.match(drift.answer, /zwei Freigaben/);
      assert.equal(drift.sourceMatches.length, 0);
      f.fail(false);
      assert.equal((await f.run("maintain")).ok, true);
      const count = f.calls.length;
      const noop = await f.run("maintain");
      assert.equal(noop.noop, true);
      assert.equal(noop.sourceIndex.status, "unchanged");
      assert.equal(f.calls.length, count);
      assert.equal(
        (await f.run("query", "--question", "Freigabe")).fallback,
        false,
      );
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify({ failed, updated, personal, drift, noop }, null, 2),
      );
      console.log("Source freshness evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "incomplete scans preserve indexed originals and confirmed removal retracts only the missing source",
  { timeout: 45000 },
  async () => {
    const { rename, rm } = await import("node:fs/promises");
    const f = await fixture();
    try {
      assert.equal((await f.run("maintain")).ok, true);
      await rename(path.join(f.dir, "alpha"), path.join(f.dir, "offline"));
      const failed = await f.run("maintain");
      assert.equal(failed.sourceIndex.ok, false);
      assert.match(failed.error, /Incomplete scan/);
      await rename(path.join(f.dir, "offline"), path.join(f.dir, "alpha"));
      const restored = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/README.md",
      );
      assert.equal(restored.sourceRetrieval, "qmd-source-index");
      assert.equal(restored.sourceMatches.length, 1);
      await rm(path.join(f.dir, "alpha/README.md"));
      const removed = await f.run("maintain");
      assert.equal(removed.sourceIndex.sourceCount, 1);
      const remaining = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "beta/README.md",
      );
      assert.deepEqual(
        remaining.originals.map((o: any) => o.id),
        ["beta/README.md"],
      );
    } finally {
      await f.close();
    }
  },
);

test(
  "a shared index failure blocks compilation and cannot advance source or wiki success",
  { timeout: 15000 },
  async () => {
    const f = await fixture();
    try {
      (f.config.qmd as any).module = path.join(f.dir, "missing-qmd.mjs");
      await f.saveConfig();
      const failed = await f.run("maintain");
      assert.equal(failed.ok, false);
      assert.equal(failed.sourceIndex.ok, false);
      assert.equal(failed.wiki.ok, false);
      assert.equal(f.calls.length, 0);
      assert.equal((await f.run("status")).lastCompleted, null);
    } finally {
      await f.close();
    }
  },
);

test(
  "a concurrent public helper is rejected before source indexing and the owner remains queryable",
  { timeout: 45000 },
  async () => {
    const f = await fixture();
    const release = f.hold();
    let owner: Promise<any> | undefined;
    try {
      const reconcile = path.join(f.dir, "reconcile.py");
      await writeFile(reconcile, 'print(\'{"status":"ok"}\')\n');
      f.fail((body) => !!body.tools);
      owner = helper(f, "owner", reconcile);
      const deadline = Date.now() + 15000;
      while (!f.calls.length && Date.now() < deadline)
        await new Promise((r) => setTimeout(r, 25));
      assert.ok(
        f.calls.length,
        "owner reached controlled provider after real source indexing",
      );
      // Query the real QMD SDK directly: isolated collections live in SQLite,
      // whereas the global CLI resolves collection names through its YAML config.
      const qmdEnv = {
        ...process.env,
        PATH: process.env.WIKI_QMD_PATH || process.env.PATH,
      };
      const npmRoot = (
        await exec("npm", ["root", "-g"], { env: qmdEnv })
      ).stdout.trim();
      const raw = await exec(
        "node",
        [
          "--input-type=module",
          "-e",
          `
      const { createStore } = await import(process.argv[1]);
      const store = await createStore({ dbPath: process.argv[2] });
      try { console.log(JSON.stringify(await store.searchLex("Freigabe", { collection: "contextual-wiki-test-sources", limit: 10 }))); }
      finally { await store.close(); }
    `,
          path.join(npmRoot, "@tobilu/qmd/dist/index.js"),
          f.config.qmd.dbPath,
        ],
        { env: qmdEnv, timeout: 10000 },
      );
      const beforeProviderFailure = JSON.parse(raw.stdout);
      assert.equal(beforeProviderFailure.length, 2);
      const blocked = await helper(f, "contender", reconcile);
      assert.equal(blocked.ok, false);
      assert.equal(blocked.failedStep, "preflight-or-lock");
      assert.deepEqual(blocked.steps, []);
      // A different outer lock directory must still respect the context writer.
      const contextBlocked = await helper(
        f,
        "separate-lock/contender",
        reconcile,
      );
      assert.equal(contextBlocked.ok, false);
      assert.equal(contextBlocked.failedStep, "maintain-test");
      const ownerConflict = JSON.parse(
        await readFile(contextBlocked.steps.at(-1).output, "utf8"),
      );
      assert.match(ownerConflict.error, /Context locked by writer/);

      release();
      assert.equal((await owner).contexts[0].sourceIndex.ok, true);
      const result = await f.run("query", "--question", "Freigabe");
      assert.equal(result.sourceMatches.length, 2);
      assert.equal(result.sourceRetrieval, "qmd-source-index");
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          {
            beforeProviderFailure,
            blocked,
            contextBlocked,
            owner: await owner,
            result,
          },
          null,
          2,
        ),
      );
      console.log("Source lock/order evidence: " + f.dir);
    } finally {
      release();
      await owner;
      await f.close();
    }
  },
);

test(
  "new indexed originals remain available even with five relevant current wiki pages",
  { timeout: 60000 },
  async () => {
    const f = await fixture();
    try {
      assert.equal((await f.run("maintain")).ok, true);
      for (let i = 0; i < 4; i++)
        assert.equal(
          (
            await f.run(
              "query",
              "--question",
              "Freigabe",
              "--save",
              "prior-" + i,
            )
          ).ok,
          true,
        );
      await writeFile(
        path.join(f.dir, "alpha/new.md"),
        "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
      );
      f.fail((b) => !!b.tools);
      assert.equal((await f.run("maintain")).sourceIndex.ok, true);
      const answer = await f.run("query", "--question", "Freigabe");
      assert.equal(answer.ok, true, JSON.stringify(answer));
      assert.ok(
        answer.evidence.some((e: any) => e.id === "sources/alpha/new.md"),
      );
      assert.equal(answer.fallback, true);
      assert.match(answer.answer, /vier Freigaben/);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          { answer, pages: (await f.run("status")).pages.length },
          null,
          2,
        ),
      );
      console.log("Source mixed-evidence budget: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "provider authentication failure leaves independent public helper source indexing successful",
  { timeout: 15000 },
  async () => {
    const f = await fixture();
    try {
      const reconcile = path.join(f.dir, "reconcile.py");
      await writeFile(reconcile, 'print(\'{"status":"ok"}\')\n');
      f.env.OPENAI_API_KEY = "";
      const report = await helper(f, "auth-failed", reconcile);
      assert.equal(report.ok, false);
      assert.equal(
        report.contexts[0]?.sourceIndex?.ok,
        true,
        JSON.stringify(report),
      );
      assert.equal(report.contexts[0]?.wiki.ok, false);
      assert.equal(f.calls.length, 0);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify({ report, calls: f.calls.length }, null, 2),
      );
      console.log("Source auth-independent evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);
