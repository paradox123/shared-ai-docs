import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn, execFileSync } from "node:child_process";
import { writeFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fixture as createFixture } from "./support.ts";
const fixture = (respond?: (body: any) => any) =>
  createFixture(respond, { timeoutMs: 20000 });

async function waitFor(check: () => boolean | Promise<boolean>) {
  const deadline = Date.now() + 15000;
  while (!(await check())) {
    assert.ok(
      Date.now() < deadline,
      "test reached its bounded observation deadline",
    );
    await new Promise((r) => setTimeout(r, 25));
  }
}

async function startHelper(
  f: Awaited<ReturnType<typeof fixture>>,
  name: string,
  wiki?: string,
) {
  const reconcile = path.join(f.dir, "reconcile.py");
  await writeFile(reconcile, `print('{"status":"ok"}')\n`);
  const child = spawn(
    "python3",
    [
      new URL("../scripts/maintain-index.py", import.meta.url).pathname,
      "--config",
      f.configPath,
      "--artifacts",
      path.join(f.dir, name),
      ...(wiki ? ["--wiki", wiki] : []),
      "--qmd",
      "/usr/bin/false",
      "--reconcile",
      reconcile,
    ],
    { env: { ...process.env, ...f.env }, detached: true },
  );
  let stdout = "";
  child.stdout.on("data", (b) => (stdout += b));
  child.stderr.resume();
  const kill = () => {
    try {
      process.kill(-child.pid!, "SIGKILL");
    } catch (e: any) {
      if (e.code !== "ESRCH") throw e;
    }
  };
  const timer = setTimeout(kill, 30000);
  const done = new Promise<any>((resolve, reject) => {
    child.once("error", reject);
    child.once("close", (code, signal) => {
      clearTimeout(timer);
      resolve({ code, signal, stdout });
    });
  });
  return { kill, done, pid: child.pid };
}
const extractions = (f: Awaited<ReturnType<typeof fixture>>) =>
  f.calls.filter((b: any) => b.tools);

test(
  "fresh public-helper process reuses durable validated extractions after SIGKILL and WikiQuery sees the completed synthesis",
  { timeout: 60000 },
  async () => {
    let pageReached = false;
    let hold = true;
    let release!: () => void;
    const gate = new Promise<void>((resolve) => (release = resolve));
    const f = await fixture(async (body) => {
      if (!body.tools && hold) {
        pageReached = true;
        await gate;
      }
    });
    let first: Awaited<ReturnType<typeof startHelper>> | undefined;
    try {
      first = await startHelper(f, "interrupted");
      await waitFor(() => pageReached);
      const durableFiles = await readdir(
        path.join(f.config.output, ".state/extractions"),
      ).catch(() => []);
      first.kill();
      const stopped = await first.done;
      hold = false;
      release();
      assert.equal(stopped.signal, "SIGKILL");
      assert.equal((await f.run("status")).lastCompleted, null);
      const second = await startHelper(f, "resumed");
      const restarted = await second.done;
      const report = JSON.parse(restarted.stdout.trim().split("\n").at(-1)!);
      assert.equal(report.contexts[0]?.wiki.ok, true, JSON.stringify(report));
      assert.equal(
        extractions(f).length,
        2,
        "neither successful source may be extracted twice",
      );
      assert.equal(durableFiles.filter((p) => p.endsWith(".json")).length, 2);
      const query = await f.run("query", "--question", "Freigabe");
      assert.equal(query.ok, true);
      assert.equal(query.fallback, false);
      assert.match(query.answer, /Alpha verlangt zwei/);
      assert.match(query.answer, /Beta verlangt drei/);
      const count = f.calls.length;
      const noop = await f.run("maintain");
      assert.equal(noop.noop, true);
      assert.equal(f.calls.length, count);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          {
            stopped,
            durableFiles,
            report,
            query,
            noop,
            extractionRequests: extractions(f),
          },
          null,
          2,
        ),
      );
      console.log("Durable restart evidence: " + f.dir);
    } finally {
      first?.kill();
      release();
      await first?.done;
      await f.close();
    }
  },
);

test(
  "corrupt one durable entry while preserving the other source's reusable work",
  { timeout: 30000 },
  async () => {
    const { readFile } = await import("node:fs/promises");
    const f = await fixture();
    try {
      f.fail((b) => !b.tools);
      assert.equal((await f.run("maintain")).ok, false);
      const cache = path.join(f.config.output, ".state/extractions");
      const files = await readdir(cache);
      const alpha = (
        await Promise.all(
          files.map(async (file) => ({
            file,
            entry: JSON.parse(await readFile(path.join(cache, file), "utf8")),
          })),
        )
      ).find(({ entry }) => entry.source === "alpha/README.md")!;
      await writeFile(path.join(cache, alpha.file), "null\n");
      f.fail(false);
      const recovered = await f.run("maintain");
      assert.equal(recovered.ok, true, JSON.stringify(recovered));
      assert.equal(extractions(f).length, 3);
      assert.equal(recovered.extractions.reused, 1);
      assert.equal(recovered.extractions.invalid, 1);
      assert.equal(
        (await f.run("query", "--question", "Freigabe")).fallback,
        false,
      );
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          { recovered, extractionRequests: extractions(f) },
          null,
          2,
        ),
      );
      console.log("Local cache corruption evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "source, resolved model and actual prompt changes invalidate only compatible pending extractions",
  { timeout: 60000 },
  async () => {
    const f = await fixture();
    try {
      f.fail((b) => !b.tools);
      const initial = await f.run("maintain");
      assert.equal(initial.ok, false);
      assert.equal(extractions(f).length, 2);
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
      );
      const sourceChanged = await f.run("maintain");
      assert.equal(sourceChanged.ok, false);
      assert.equal(extractions(f).length, 3);
      assert.equal(sourceChanged.extractions.reused, 1);
      // The next process resolves the actual provider default when the explicit override disappears.
      delete (f.env as any).LLMWIKI_MODEL;
      const modelChanged = await f.run("maintain");
      assert.equal(extractions(f).length, 5);
      assert.notEqual(extractions(f).at(-1).model, "test-model");
      (f.env as any).LLMWIKI_OUTPUT_LANG = "en";
      const promptChanged = await f.run("maintain");
      assert.equal(extractions(f).length, 7);
      assert.notEqual(
        extractions(f)[4].messages[0].content,
        extractions(f)[6].messages[0].content,
      );
      assert.equal((await f.run("status")).lastCompleted, null);
      f.fail(false);
      const recovered = await f.run("maintain");
      assert.equal(recovered.ok, true, JSON.stringify(recovered));
      assert.equal(extractions(f).length, 7);
      assert.equal(recovered.extractions.reused, 2);
      const query = await f.run("query", "--question", "Freigabe");
      assert.match(query.answer, /Alpha verlangt vier/);
      assert.doesNotMatch(query.answer, /Alpha verlangt zwei/);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          {
            initial,
            sourceChanged,
            modelChanged,
            promptChanged,
            recovered,
            query,
            extractionRequests: extractions(f),
          },
          null,
          2,
        ),
      );
      console.log("Extraction contract invalidation evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "source drift and a later real QMD failure preserve durable work without advancing completed maintenance",
  { timeout: 60000 },
  async () => {
    const { rm, rename } = await import("node:fs/promises");
    let fault: "drift" | "index" | undefined = "drift";
    const f = await fixture(async (body) => {
      if (!body.tools && fault === "drift") {
        fault = undefined;
        await writeFile(
          path.join(f.dir, "alpha/README.md"),
          "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
        );
      } else if (!body.tools && fault === "index") {
        fault = undefined;
        // The real SDK opens this path only after generation. Obstruct that open;
        // keep the original isolated database intact for recovery.
        await rename(f.config.qmd.dbPath, f.config.qmd.dbPath + ".preserved");
        await (await import("node:fs/promises")).mkdir(f.config.qmd.dbPath);
      }
    });
    try {
      const drift = await f.run("maintain");
      assert.equal(drift.ok, false);
      assert.match(drift.error, /Sources changed during generation/);
      assert.equal((await f.run("status")).lastCompleted, null);
      assert.equal(extractions(f).length, 2);
      fault = "index";
      const indexFailed = await f.run("maintain");
      assert.equal(indexFailed.ok, false);
      assert.equal(indexFailed.sourceIndex.ok, true);
      assert.equal(indexFailed.wiki.ok, false);
      assert.equal(extractions(f).length, 3);
      assert.equal(indexFailed.extractions.reused, 1);
      assert.equal((await f.run("status")).lastCompleted, null);
      await rm(f.config.qmd.dbPath, { recursive: true });
      await rename(f.config.qmd.dbPath + ".preserved", f.config.qmd.dbPath);
      const recovered = await f.run("maintain");
      assert.equal(recovered.ok, true, JSON.stringify(recovered));
      assert.equal(extractions(f).length, 3);
      const query = await f.run("query", "--question", "Freigabe");
      assert.equal(query.fallback, false);
      assert.match(query.answer, /Alpha verlangt vier/);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          {
            drift,
            indexFailed,
            recovered,
            query,
            extractionRequests: extractions(f),
          },
          null,
          2,
        ),
      );
      console.log("Drift and real QMD failure evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "legacy completed knowledge and saved answers survive introducing the optional cache",
  { timeout: 30000 },
  async () => {
    const { rm, readFile } = await import("node:fs/promises");
    const f = await fixture();
    try {
      assert.equal((await f.run("maintain")).ok, true);
      assert.equal(
        (await f.run("query", "--question", "Freigabe", "--save", "decision"))
          .ok,
        true,
      );
      const saved = path.join(f.config.output, "wiki/answers/decision.md");
      const before = await readFile(saved, "utf8");
      await rm(path.join(f.config.output, ".state/extractions"), {
        recursive: true,
      });
      const calls = f.calls.length;
      const noop = await f.run("maintain");
      assert.equal(noop.noop, true);
      assert.equal(f.calls.length, calls);
      const after = await readFile(saved, "utf8");
      assert.equal(after, before);
      const query = await f.run("query", "--question", "Freigabe");
      assert.equal(query.ok, true);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          { before, after, noop, query, providerRequestsBeforeNoop: calls },
          null,
          2,
        ),
      );
      console.log("Legacy state preservation evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "empty and incomplete extraction replies are retried while valid independent work and torn-file isolation survive",
  { timeout: 30000 },
  async () => {
    let bad = true;
    const f = await fixture((body) => {
      if (
        bad &&
        body.tools &&
        body.messages.some((m: any) => m.content.includes("Beta verlangt"))
      )
        return {
          role: "assistant",
          tool_calls: [
            {
              id: "empty",
              type: "function",
              function: {
                name: "extract_concepts",
                arguments: '{"concepts":[]}',
              },
            },
          ],
        };
    });
    try {
      const failed = await f.run("maintain");
      assert.equal(failed.ok, false);
      assert.equal(failed.extractions.saved, 1);
      assert.equal((await f.run("status")).lastCompleted, null);
      const dir = path.join(f.config.output, ".state/extractions");
      await writeFile(path.join(dir, "aborted.json.tmp"), '{"raw":');
      bad = false;
      const recovered = await f.run("maintain");
      assert.equal(recovered.ok, true, JSON.stringify(recovered));
      assert.equal(recovered.extractions.reused, 1);
      assert.equal(extractions(f).length, 3);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          { failed, recovered, extractionRequests: extractions(f) },
          null,
          2,
        ),
      );
      console.log("Empty reply and incomplete-file evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "partially malformed extraction is pending rather than publishing a silently filtered subset",
  { timeout: 30000 },
  async () => {
    let malformed = true;
    const f = await fixture((body) => {
      if (
        malformed &&
        body.tools &&
        body.messages.some((m: any) => m.content.includes("Alpha verlangt"))
      )
        return {
          role: "assistant",
          tool_calls: [
            {
              id: "partial",
              type: "function",
              function: {
                name: "extract_concepts",
                arguments: JSON.stringify({
                  concepts: [
                    { concept: "Freigabe", summary: "Alpha", is_new: true },
                    { concept: 42 },
                  ],
                }),
              },
            },
          ],
        };
    });
    try {
      const failed = await f.run("maintain");
      assert.equal(
        failed.ok,
        false,
        "a malformed extraction cannot publish a filtered subset",
      );
      assert.equal((await f.run("status")).lastCompleted, null);
      malformed = false;
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true);
      assert.equal(extractions(f).length, 3);
      assert.equal(repaired.extractions.reused, 1);
      console.log("Partial reply recovery evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "enabling diagnostics does not repeat compatible extraction work",
  { timeout: 30000 },
  async () => {
    const f = await fixture();
    try {
      f.fail((b) => !b.tools);
      assert.equal((await f.run("maintain")).ok, false);
      (f.env as any).LLMWIKI_DEBUG = "1";
      f.fail(false);
      const result = await f.run("maintain");
      assert.equal(result.ok, true);
      assert.equal(extractions(f).length, 2);
      assert.equal(result.extractions.reused, 2);
    } finally {
      await f.close();
    }
  },
);

test(
  "an installed schema/compiler change invalidates resumed extractions without upgrading the pinned compiler",
  { timeout: 45000 },
  async () => {
    const { readFile, mkdir, cp, symlink } = await import("node:fs/promises");
    const f = await fixture();
    try {
      f.fail((b) => !b.tools);
      assert.equal((await f.run("maintain")).ok, false);
      const app = new URL("..", import.meta.url).pathname;
      const runner = path.join(f.dir, "changed-installation");
      await mkdir(path.join(runner, ".runtime"), { recursive: true });
      for (const name of ["src", "scripts", "wiki", "wiki-node"])
        await cp(path.join(app, name), path.join(runner, name), {
          recursive: true,
        });
      // Clone only this test's compiler. The installed runtime under test stays unchanged.
      execFileSync("cp", [
        "-cR",
        path.join(app, ".runtime/compiler"),
        path.join(runner, ".runtime/compiler"),
      ]);
      for (const name of ["node_modules", ".runtime/node"])
        await symlink(path.join(app, name), path.join(runner, name), "dir");
      const bundle = path.join(runner, ".runtime/compiler/dist/index.js");
      const before = await readFile(bundle, "utf8");
      const after = before.replace(
        "Extract knowledge concepts from a source document",
        "Extract knowledge concepts from a source document with a revised tool contract",
      );
      assert.notEqual(after, before);
      await writeFile(bundle, after);
      f.fail(false);
      const changed = await startHelper(
        f,
        "schema-changed",
        path.join(runner, "wiki"),
      );
      const stopped = await changed.done;
      const report = JSON.parse(stopped.stdout.trim().split("\n").at(-1)!);
      assert.equal(report.contexts[0]?.wiki.ok, true, JSON.stringify(report));
      assert.equal(extractions(f).length, 4);
      assert.notDeepEqual(extractions(f)[0].tools, extractions(f)[2].tools);
      assert.equal(
        (await f.run("query", "--question", "Freigabe")).fallback,
        false,
      );
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify({ report, extractionRequests: extractions(f) }, null, 2),
      );
      console.log("Installed schema/compiler invalidation evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: schema-invalid optional fields cannot be saved or published as successful extraction",
  { timeout: 30000 },
  async () => {
    let malformed = true;
    const f = await fixture((body) => {
      if (
        malformed &&
        body.tools &&
        body.messages.some((m: any) => m.content.includes("Alpha verlangt"))
      )
        return {
          role: "assistant",
          tool_calls: [
            {
              id: "schema-invalid",
              type: "function",
              function: {
                name: "extract_concepts",
                arguments: JSON.stringify({
                  concepts: [
                    {
                      concept: "Freigabe",
                      summary: "Alpha",
                      is_new: true,
                      confidence: "certain",
                      tags: [42],
                    },
                  ],
                }),
              },
            },
          ],
        };
    });
    try {
      const failed = await f.run("maintain");
      assert.equal(
        failed.ok,
        false,
        "full tool schema must validate before success",
      );
      assert.equal(failed.extractions.saved, 1);
      assert.equal((await f.run("status")).lastCompleted, null);
      malformed = false;
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true);
      assert.equal(extractions(f).length, 3);
      assert.equal(repaired.extractions.reused, 1);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          { failed, repaired, extractionRequests: extractions(f) },
          null,
          2,
        ),
      );
      console.log("Critical schema validation evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: a real cache write failure after a valid reply is not durable success",
  { timeout: 30000 },
  async () => {
    const { rename, rm } = await import("node:fs/promises");
    let obstruct = true;
    const f = await fixture(async (body) => {
      if (
        obstruct &&
        body.tools &&
        body.messages.some((m: any) => m.content.includes("Beta verlangt"))
      ) {
        const cache = path.join(f.config.output, ".state/extractions");
        await rename(cache, cache + ".preserved");
        await writeFile(
          cache,
          "controlled filesystem obstruction after the valid model reply",
        );
        obstruct = false;
      }
    });
    try {
      (f.config as any).concurrency = 1;
      await f.saveConfig();
      const failed = await f.run("maintain");
      assert.equal(failed.ok, false);
      assert.match(failed.error, /EEXIST|ENOTDIR/);
      assert.equal(
        failed.extractions.saved,
        1,
        "only Alpha was fully persisted",
      );
      assert.equal((await f.run("status")).lastCompleted, null);
      assert.equal(extractions(f).length, 2);
      const cache = path.join(f.config.output, ".state/extractions");
      await rm(cache);
      await rename(cache + ".preserved", cache);
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true, JSON.stringify(repaired));
      assert.equal(repaired.extractions.reused, 1);
      assert.equal(repaired.extractions.saved, 1);
      assert.equal(extractions(f).length, 3);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          { failed, repaired, extractionRequests: extractions(f) },
          null,
          2,
        ),
      );
      console.log("Critical durable storage failure evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: source relocation and actual provider request options invalidate compatible keys",
  { timeout: 40000 },
  async () => {
    const { rename } = await import("node:fs/promises");
    const f = await fixture();
    try {
      f.fail((b) => !b.tools);
      assert.equal((await f.run("maintain")).ok, false);
      const relocated = path.join(f.dir, "alpha-relocated");
      await rename(path.join(f.dir, "alpha"), relocated);
      f.config.repos[0].root = relocated;
      await f.saveConfig();
      const identityChanged = await f.run("maintain");
      assert.equal(identityChanged.extractions.reused, 1);
      assert.equal(extractions(f).length, 3);
      (f.env as any).LLMWIKI_OPENAI_EXTRA_BODY = '{"temperature":0.25}';
      const requestChanged = await f.run("maintain");
      assert.equal(extractions(f).length, 5);
      assert.equal(extractions(f).at(-1).temperature, 0.25);
      f.fail(false);
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true);
      assert.equal(extractions(f).length, 5);
      assert.equal(repaired.extractions.reused, 2);
      const query = await f.run("query", "--question", "Freigabe");
      assert.equal(query.ok, true);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          {
            identityChanged,
            requestChanged,
            repaired,
            query,
            extractionRequests: extractions(f),
          },
          null,
          2,
        ),
      );
      assert.equal(
        query.originals.find((o: any) => o.id === "alpha/README.md")?.path,
        path.join(relocated, "README.md"),
      );
      console.log("Critical identity and provider options evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: SIGKILL after only one durable extraction resumes the unfinished source",
  { timeout: 45000 },
  async () => {
    let betaReached = false;
    let hold = true;
    let release!: () => void;
    const gate = new Promise<void>((resolve) => (release = resolve));
    const f = await fixture(async (body) => {
      if (
        hold &&
        body.tools &&
        body.messages.some((m: any) => m.content.includes("Beta verlangt"))
      ) {
        betaReached = true;
        await gate;
      }
    });
    let first: Awaited<ReturnType<typeof startHelper>> | undefined;
    try {
      (f.config as any).concurrency = 1;
      await f.saveConfig();
      first = await startHelper(f, "one-durable");
      await waitFor(() => betaReached);
      const durable = await readdir(
        path.join(f.config.output, ".state/extractions"),
      );
      assert.equal(durable.filter((name) => name.endsWith(".json")).length, 1);
      first.kill();
      const stopped = await first.done;
      hold = false;
      release();
      const lastCompletedAfterStop = (await f.run("status")).lastCompleted;
      assert.equal(lastCompletedAfterStop, null);
      const second = await startHelper(f, "unfinished-resumed");
      const result = await second.done;
      const report = JSON.parse(result.stdout.trim().split("\n").at(-1)!);
      assert.equal(report.contexts[0]?.wiki.ok, true, JSON.stringify(report));
      const requests = extractions(f);
      assert.equal(requests.length, 3);
      assert.equal(
        requests.filter((b) =>
          b.messages.some((m: any) => m.content.includes("Alpha verlangt")),
        ).length,
        1,
      );
      assert.equal(
        requests.filter((b) =>
          b.messages.some((m: any) => m.content.includes("Beta verlangt")),
        ).length,
        2,
      );
      const query = await f.run("query", "--question", "Freigabe");
      assert.equal(query.fallback, false);
      assert.equal(query.originals.length, 2);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          {
            stopped,
            durable,
            lastCompletedAfterStop,
            report,
            query,
            extractionRequests: requests,
          },
          null,
          2,
        ),
      );
      console.log("Critical single-durable restart evidence: " + f.dir);
    } finally {
      first?.kill();
      release();
      await first?.done;
      await f.close();
    }
  },
);
