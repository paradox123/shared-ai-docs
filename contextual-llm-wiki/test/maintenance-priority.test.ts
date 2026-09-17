import { test } from "node:test";
import assert from "node:assert/strict";
import { writeFile, readFile } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";

function withFacts(body: any) {
  if (!body.tools) {
    const prompt = body.messages.map((m: any) => m.content).join("\n");
    if (!prompt.includes("--- EVIDENCE ---")) return;
    const evidence = prompt.split("--- EVIDENCE ---")[1];
    const facts = [
      ...new Set(
        evidence.match(
          /(?:Alpha|Beta) verlangt (?:zwei|drei|vier) Freigaben\./g,
        ) || [],
      ),
    ];
    const ids = [...evidence.matchAll(/--- ([^@]+) @/g)].map((m: any) =>
      m[1].trim(),
    );
    return {
      role: "assistant",
      content:
        "Aussagen ausschließlich aus der benannten Evidenz: " +
        facts.join(" ") +
        "\nBelege: " +
        ids.join(", "),
    };
  }
  const source =
    body.messages
      .map((m: any) => m.content)
      .join("\n")
      .split("--- SOURCE DOCUMENT ---")[1] || "";
  const concept = source.includes("Kontrollseite")
    ? "Kontrollseite"
    : "Freigabe";
  return {
    role: "assistant",
    tool_calls: [
      {
        id: "facts",
        type: "function",
        function: {
          name: "extract_concepts",
          arguments: JSON.stringify({
            concepts: [
              {
                concept,
                summary: source,
                is_new: true,
                confidence: 1,
                provenance_state: "extracted",
              },
            ],
          }),
        },
      },
    ],
  };
}

test(
  "bounded inventory preserves initial age and publishes model-processed daily evidence before undiscovered backlog",
  { timeout: 45000 },
  async () => {
    const f = await fixture(withFacts, { timeoutMs: 15000 });
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    (f.config as any).concurrency = 4;
    await f.saveConfig();
    for (let i = 0; i < 5; i++)
      await writeFile(
        path.join(f.dir, `beta/old${i}.md`),
        "# Kontrollseite\nUnabhängige Kontrollseite.\n",
      );
    try {
      const first = await f.run("maintain");
      assert.equal(first.ok, false, "initial package must retain backlog");
      assert.equal(f.calls.filter((b) => b.tools).length, 2);
      assert.equal(first.maintenance.initial.pending, 7);
      assert.equal(first.maintenance.initial.unextracted, 5);
      const initial = JSON.parse(
        await readFile(
          path.join(f.config.output, ".state/maintenance-inventory.json"),
          "utf8",
        ),
      );
      await writeFile(
        path.join(f.dir, "alpha/new.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      await writeFile(
        path.join(f.dir, "beta/old4.md"),
        "# Freigabe\nBeta verlangt vier Freigaben.\n",
      );
      const before = f.calls.length;
      const second = await f.run("maintain");
      assert.equal(second.ok, false);
      const extracted = f.calls
        .slice(before)
        .filter((b) => b.tools)
        .map((b) => JSON.stringify(b));
      assert.ok(
        extracted[0].includes("Alpha verlangt vier"),
        "new daily source first",
      );
      assert.equal(
        second.maintenance.daily.pending,
        2,
        "source summary does not certify global synthesis complete",
      );
      assert.ok(second.maintenance.initial.unextracted > 0);
      const query = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/new.md",
      );
      assert.equal(query.fallback, false, JSON.stringify(query));
      assert.match(query.answer, /Alpha verlangt vier Freigaben/);
      assert.doesNotMatch(query.answer, /Beta|Beide Repos/);
      const queryRequest = f.calls.findLast((b) =>
        JSON.stringify(b).includes("--- EVIDENCE ---"),
      );
      assert.match(JSON.stringify(queryRequest), /Evidenztyp: source-summary/);
      assert.doesNotMatch(
        JSON.stringify(queryRequest),
        /Beta verlangt|beta\/README/,
      );
      assert.equal(second.maintenance.capacity.dailyOverCapacity, true);
      assert.ok(
        extracted[1].includes("Kontrollseite"),
        "reserved backlog slot survives configured concurrency four",
      );
      assert.equal(query.evidence[0].kind, "source-summary");
      assert.equal(query.originals[0].freshness, "checked-current");
      const next = JSON.parse(
        await readFile(
          path.join(f.config.output, ".state/maintenance-inventory.json"),
          "utf8",
        ),
      );
      assert.equal(
        next.sources["beta/old3.md"].firstSeenAt,
        initial.sources["beta/old3.md"].firstSeenAt,
      );
      assert.equal(next.sources["beta/old4.md"].classification, "daily");
      const thirdBefore = f.calls.length;
      const third = await f.run("maintain");
      const thirdRequests = f.calls.slice(thirdBefore).filter((b) => b.tools);
      assert.ok(
        JSON.stringify(thirdRequests[0]).includes("Beta verlangt vier"),
        "changed uncompiled initial source now has daily priority",
      );
      await writeFile(
        path.join(f.dir, "priority-acceptance.json"),
        JSON.stringify(
          { first, second, third, query, queryRequest, initial, next },
          null,
          2,
        ),
      );
      console.log("Priority evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "public helper resumes finite packages, reports Berlin overdue work, and completes shared concepts before no-op",
  { timeout: 60000 },
  async () => {
    const f = await fixture(withFacts, { timeoutMs: 15000 });
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    for (let i = 0; i < 6; i++)
      await writeFile(
        path.join(f.dir, `beta/old${i}.md`),
        "# Kontrollseite\nUnabhängige Kontrollseite.\n",
      );
    const { spawn } = await import("node:child_process");
    const reconcile = path.join(f.dir, "reconcile.py");
    await writeFile(reconcile, `print('{"status":"ok"}')\n`);
    const helper = (n: number, now: string) =>
      new Promise<any>((resolve, reject) => {
        const p = spawn(
          "python3",
          [
            new URL("../scripts/maintain-index.py", import.meta.url).pathname,
            "--config",
            f.configPath,
            "--artifacts",
            path.join(f.dir, "job" + n),
            "--qmd",
            "/usr/bin/true",
            "--reconcile",
            reconcile,
            "--budget-seconds",
            "12",
            "--termination-grace-seconds",
            "0.5",
          ],
          { env: { ...process.env, ...f.env, WIKI_MAINTENANCE_NOW: now } },
        );
        let out = "",
          err = "";
        p.stdout.on("data", (b) => (out += b));
        p.stderr.on("data", (b) => (err += b));
        p.on("error", reject);
        p.on("close", (code) => {
          try {
            resolve({
              code,
              report: JSON.parse(out.trim().split("\n").at(-1)!),
              stderr: err,
            });
          } catch {
            reject(Error(out + err));
          }
        });
      });
    try {
      const reports = [await helper(0, "2026-09-17T21:30:00Z")];
      assert.equal(
        reports[0].report.contexts[0].packageCompleted,
        true,
        JSON.stringify(reports[0]),
      );
      await writeFile(
        path.join(f.dir, "alpha/new.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      reports.push(await helper(1, "2026-09-17T22:30:00Z")); // Berlin Sep18
      assert.deepEqual(
        reports[1].report.contexts[0].maintenance.daily.overdue,
        [],
      );
      // Force a controlled source-local failure on the next day to retain daily work.
      f.fail(
        (body) =>
          !!body.tools && JSON.stringify(body).includes("Kontrollseite"),
      );
      reports.push(await helper(2, "2026-09-19T22:30:00Z")); // Berlin Sep20, deadline Sep19 elapsed
      assert.deepEqual(
        reports[2].report.contexts[0].maintenance.daily.overdue,
        ["alpha/new.md"],
      );
      f.fail(false);
      let n = 3;
      while (reports.at(-1).code !== 0 && n < 8)
        reports.push(await helper(n++, "2026-09-20T10:00:00Z"));
      assert.equal(reports.at(-1).code, 0, JSON.stringify(reports.at(-1)));
      assert.equal(
        reports.at(-1).report.contexts[0].maintenance.globalComplete,
        true,
      );
      const query = await f.run("query", "--question", "Freigabe");
      const concept = query.evidence.find(
        (e: any) => e.id === "concepts/freigabe",
      );
      assert.ok(concept, JSON.stringify(query));
      assert.ok(
        concept.sourceVersions["alpha/README.md"] &&
          concept.sourceVersions["beta/README.md"],
      );
      const before = f.calls.length;
      const noop = await helper(n, "2026-09-20T10:00:00Z");
      assert.equal(noop.report.contexts[0].noop, true);
      assert.equal(f.calls.length, before);
      await writeFile(
        path.join(f.dir, "helper-priority-acceptance.json"),
        JSON.stringify(
          {
            reports,
            query,
            noop,
            extractionRequests: f.calls.filter((b) => b.tools).length,
          },
          null,
          2,
        ),
      );
      console.log("Helper priority evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "inventory age survives scans, records confirmed removal only, and uses next Berlin calendar date across winter transition",
  { timeout: 30000 },
  async () => {
    const f = await fixture(withFacts, { timeoutMs: 12000 });
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    for (let i = 0; i < 4; i++)
      await writeFile(
        path.join(f.dir, `beta/old${i}.md`),
        "# Kontrollseite\nKontrollseite.\n",
      );
    const { invoke } = await import("./support.ts");
    const run = (date: string) =>
      invoke(
        ["maintain", "--config", f.configPath],
        { ...f.env, WIKI_MAINTENANCE_NOW: date },
        undefined,
        12000,
      );
    const inventoryPath = path.join(
      f.config.output,
      ".state/maintenance-inventory.json",
    );
    try {
      await run("2026-10-24T20:00:00Z");
      await writeFile(
        path.join(f.dir, "beta/old3.md"),
        "# Freigabe\nBeta verlangt vier Freigaben.\n",
      );
      const changed = await run("2026-10-24T22:30:00Z"); // Oct25 Berlin before DST ends
      const inventory = JSON.parse(await readFile(inventoryPath, "utf8"));
      assert.equal(inventory.sources["beta/old3.md"].dueDate, "2026-10-26");
      assert.equal(inventory.sources["beta/old3.md"].changedAt, null);
      assert.equal(inventory.sources["beta/old3.md"].classification, "daily");
      f.fail(true, 401);
      await run("2026-10-26T22:30:00Z"); // still Oct26 after DST -> not overdue
      const lastOnTime = JSON.parse(await readFile(inventoryPath, "utf8"));
      assert.deepEqual(
        lastOnTime.sources["beta/old3.md"],
        inventory.sources["beta/old3.md"],
      );
      const overdue = await run("2026-10-26T23:30:00Z");
      assert.deepEqual(overdue.maintenance.daily.overdue, ["beta/old3.md"]);
      const { rename, unlink } = await import("node:fs/promises");
      await rename(path.join(f.dir, "beta"), path.join(f.dir, "beta-away"));
      const bytes = await readFile(inventoryPath, "utf8");
      const unavailable = await run("2026-10-27T00:00:00Z");
      assert.match(unavailable.error, /Incomplete scan/);
      assert.equal(await readFile(inventoryPath, "utf8"), bytes);
      await rename(path.join(f.dir, "beta-away"), path.join(f.dir, "beta"));
      await unlink(path.join(f.dir, "beta/old3.md"));
      await run("2026-10-27T00:30:00Z");
      const removed = JSON.parse(await readFile(inventoryPath, "utf8"));
      assert.equal(
        removed.sources["beta/old3.md"].removedAt,
        "2026-10-27T00:30:00.000Z",
      );
      await writeFile(
        path.join(f.dir, "calendar-acceptance.json"),
        JSON.stringify(
          { changed, inventory, lastOnTime, overdue, unavailable, removed },
          null,
          2,
        ),
      );
      console.log("Calendar evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "partial source pages and saved answers remain available across unchanged packages and survive common synthesis",
  { timeout: 40000 },
  async () => {
    const f = await fixture(withFacts, { timeoutMs: 12000 });
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    for (let i = 0; i < 6; i++)
      await writeFile(
        path.join(f.dir, `beta/old${i}.md`),
        "# Kontrollseite\nKontrollseite.\n",
      );
    try {
      await f.run("maintain");
      const saved = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/README.md",
        "--save",
        "source-answer",
      );
      assert.equal(saved.ok, true, JSON.stringify(saved));
      const answerPath = path.join(
        f.config.output,
        "wiki/answers/source-answer.md",
      );
      const before = await readFile(answerPath, "utf8");
      const partial = await f.run("maintain");
      assert.equal(partial.ok, false);
      assert.equal(await readFile(answerPath, "utf8"), before);
      let result = partial;
      for (let i = 0; i < 5 && !result.ok; i++)
        result = await f.run("maintain");
      assert.equal(result.ok, true, JSON.stringify(result));
      assert.equal(await readFile(answerPath, "utf8"), before);
      assert.equal((await f.run("lint")).ok, true);
      await writeFile(
        path.join(f.dir, "saved-answer-acceptance.json"),
        JSON.stringify({ saved, partial, result }, null, 2),
      );
      console.log("Saved answer evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "cache-contract change during backlog cannot replace a current summary beneath a saved answer",
  { timeout: 30000 },
  async () => {
    let changed = false;
    const f = await fixture(
      (body: any) => {
        const response = withFacts(body);
        if (changed && body.tools && response?.tool_calls) {
          const args = JSON.parse(response.tool_calls[0].function.arguments);
          args.concepts[0].summary += " Neue Formulierung.";
          response.tool_calls[0].function.arguments = JSON.stringify(args);
        }
        return response;
      },
      { timeoutMs: 12000 },
    );
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    await f.saveConfig();
    await writeFile(
      path.join(f.dir, "beta/old.md"),
      "# Kontrollseite\nKontrollseite.\n",
    );
    try {
      const first = await f.run("maintain");
      assert.equal(first.packageCompleted, true);
      await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/README.md",
        "--save",
        "source-answer",
      );
      const before = await readFile(
        path.join(f.config.output, "wiki/answers/source-answer.md"),
        "utf8",
      );
      changed = true;
      f.env.LLMWIKI_MODEL = "different-test-model";
      const partial = await f.run("maintain");
      assert.equal(partial.packageCompleted, true, JSON.stringify(partial));
      const status = await f.run("status");
      assert.deepEqual(
        status.review,
        [],
        "saved answers must never remain active with obsolete page versions",
      );
      assert.equal(
        await readFile(
          path.join(f.config.output, "wiki/answers/source-answer.md"),
          "utf8",
        ),
        before,
      );
      await writeFile(
        path.join(f.dir, "cache-contract-answer.json"),
        JSON.stringify({ first, partial, status }, null, 2),
      );
      console.log("Cache contract answer evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);
