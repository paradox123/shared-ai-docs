import { test } from "node:test";
import assert from "node:assert/strict";
import { writeFile, readFile, rename, unlink } from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";
import { fixture } from "./support.ts";

async function helper(f: any, name: string, seconds = 4) {
  const reconcile = path.join(f.dir, "reconcile.py");
  await writeFile(reconcile, `print('{"status":"ok"}')\n`);
  const started = Date.now();
  const child = spawn(
    "python3",
    [
      new URL("../scripts/maintain-index.py", import.meta.url).pathname,
      "--config",
      f.configPath,
      "--artifacts",
      path.join(f.dir, name),
      "--qmd",
      "/usr/bin/true",
      "--reconcile",
      reconcile,
      "--budget-seconds",
      String(seconds),
      "--termination-grace-seconds",
      "0.5",
    ],
    { env: { ...process.env, ...f.env }, detached: true },
  );
  let stdout = "",
    stderr = "";
  child.stdout.on("data", (b) => (stdout += b));
  child.stderr.on("data", (b) => (stderr += b));
  const timer = setTimeout(
    () => {
      try {
        process.kill(-child.pid!, "SIGKILL");
      } catch {}
    },
    (seconds + 5) * 1000,
  );
  return await new Promise<any>((resolve, reject) => {
    child.on("error", reject);
    child.on("close", (code, signal) => {
      clearTimeout(timer);
      try {
        resolve({
          code,
          signal,
          elapsedMs: Date.now() - started,
          report: JSON.parse(stdout.trim().split("\n").at(-1)!),
          stderr,
        });
      } catch {
        reject(Error(stdout + stderr));
      }
    });
  });
}

test(
  "critical: repeated held daily requests cannot silently displace every initial attempt across process budgets",
  { timeout: 35000 },
  async () => {
    let hold = false,
      release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    const f = await fixture(
      async (body) => {
        if (hold && body.tools && JSON.stringify(body).includes("Tagesquelle"))
          await gate;
      },
      { timeoutMs: 12000 },
    );
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    for (let i = 0; i < 1; i++)
      await writeFile(
        path.join(f.dir, `beta/zold${i}.md`),
        "# Kontrollseite\nKontrollseite.\n",
      );
    try {
      assert.equal((await f.run("maintain")).packageCompleted, true);
      await writeFile(
        path.join(f.dir, "alpha/daily.md"),
        "# Tagesquelle\nAlpha verlangt vier Freigaben.\n",
      );
      hold = true;
      const observations = [];
      for (let i = 0; i < 3; i++) {
        const before = f.calls.length;
        const result = await helper(f, "starvation" + i);
        assert.equal(result.report.outcome, "budget-exhausted");
        assert.ok(result.elapsedMs < 6500, JSON.stringify(result));
        const inventory = JSON.parse(
          await readFile(
            path.join(f.config.output, ".state/maintenance-inventory.json"),
            "utf8",
          ),
        );
        observations.push({
          result,
          inventory,
          requests: f.calls
            .slice(before)
            .filter((b) => b.tools)
            .map((b) => JSON.stringify(b)),
        });
      }
      assert.equal(observations[0].requests.length, 1);
      assert.equal(observations[1].requests.length, 1);
      assert.ok(
        observations[2].requests[0].includes("Kontrollseite"),
        "third run must attempt reserved initial work before the repeatedly held daily request",
      );
      const capacity =
        observations[2].result.report.contexts[0].maintenance.capacity;
      assert.equal(capacity.mode, "initial-recovery");
      assert.equal(capacity.insufficientTimeCapacity, true);
      assert.equal(
        capacity.backlogStalled,
        false,
        "last initial extraction resolved the measured stall",
      );
      assert.equal(capacity.reservedInitialSlots, 0);
      assert.equal(
        observations[2].result.report.contexts[0].maintenance.daily.pending,
        1,
      );
      const durableInitial = (inventory: any) =>
        Object.values<any>(inventory.sources).filter(
          (r) => r.classification === "initial" && r.extractedHash === r.hash,
        ).length;
      assert.equal(
        durableInitial(observations[1].inventory),
        durableInitial(observations[0].inventory),
      );
      assert.equal(
        durableInitial(observations[2].inventory),
        durableInitial(observations[1].inventory) + 1,
      );
      hold = false;
      release();
      const recovered = await helper(f, "after-starvation", 12);
      assert.notEqual(
        recovered.report.contexts[0].maintenance.capacity.mode,
        "initial-recovery",
        "recovery gets one attempt, never permanently suppresses daily priority",
      );
      await writeFile(
        path.join(f.dir, "critical-fairness.json"),
        JSON.stringify({ observations, recovered }, null, 2),
      );
      console.log("Critical fairness evidence: " + f.dir);
    } finally {
      hold = false;
      release();
      await f.close();
    }
  },
);

function scopedProvider(body: any) {
  const prompt = body.messages.map((m: any) => m.content).join("\n");
  if (body.tools) {
    const source = prompt.split("--- SOURCE DOCUMENT ---")[1] || "";
    const concept = source.includes("Kontrollseite")
      ? "Kontrollseite"
      : "Freigabe";
    return {
      role: "assistant",
      tool_calls: [
        {
          id: "extract",
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
  if (prompt.includes("--- EVIDENCE ---")) {
    const evidence = prompt.split("--- EVIDENCE ---")[1];
    const facts = [
      ...new Set(
        evidence.match(
          /(?:Alpha|Beta) verlangt (?:zwei|drei|vier) Freigaben\./g,
        ) || [],
      ),
    ];
    return {
      role: "assistant",
      content: "Nur benannte Evidenz: " + facts.join(" "),
    };
  }
}

test(
  "critical: changed source pages invalidate mixed saved answers while independent answers and bounded query scope remain current",
  { timeout: 45000 },
  async () => {
    const f = await fixture(scopedProvider, { timeoutMs: 12000 });
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    await f.saveConfig();
    for (let i = 0; i < 5; i++)
      await writeFile(
        path.join(f.dir, `beta/zold${i}.md`),
        "# Kontrollseite\nKontrollseite.\n",
      );
    try {
      await f.run("maintain");
      const mixed = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--save",
        "mixed",
      );
      assert.equal(mixed.fallback, false);
      assert.deepEqual(mixed.originals.map((s: any) => s.id).sort(), [
        "alpha/README.md",
        "beta/README.md",
      ]);
      const independent = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "beta/README.md",
        "--save",
        "independent",
      );
      assert.doesNotMatch(independent.answer, /Alpha|Beide/);
      const independentFile = path.join(
        f.config.output,
        "wiki/answers/independent.md",
      );
      const before = await readFile(independentFile, "utf8");
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      await writeFile(
        path.join(f.dir, "beta/new.md"),
        "# Freigabe\nBeta verlangt vier Freigaben.\n",
      );
      const changed = await f.run("maintain");
      assert.equal(changed.packageCompleted, true);
      await assert.rejects(
        readFile(path.join(f.config.output, "wiki/answers/mixed.md")),
        /ENOENT/,
      );
      assert.equal(await readFile(independentFile, "utf8"), before);
      const alpha = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/README.md",
      );
      assert.equal(alpha.fallback, false);
      assert.match(alpha.answer, /Alpha verlangt vier/);
      assert.doesNotMatch(alpha.answer, /zwei|Beta|Beide/);
      assert.ok(!alpha.evidence.some((e: any) => e.id === "answers/mixed"));
      const next = await f.run("maintain");
      const beta = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "beta/new.md",
      );
      assert.equal(beta.fallback, false);
      assert.match(beta.answer, /Beta verlangt vier/);
      assert.doesNotMatch(beta.answer, /Alpha|Beide/);
      assert.equal(await readFile(independentFile, "utf8"), before);
      const unknown = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "beta/README.md",
        "--save",
        "unknown",
      );
      assert.equal(unknown.ok, true);
      // Unknown stored dependency is a fault injection on otherwise current
      // evidence, never a new valid source and not merely an already stale page.
      const statePath = path.join(f.config.output, ".state/state.json");
      const state = JSON.parse(await readFile(statePath, "utf8"));
      state.pages["answers/unknown"].pageVersions["concepts/unknown"] =
        "not-a-valid-version";
      await writeFile(statePath, JSON.stringify(state));
      let blocked = await f.run("maintain");
      const discovery = [blocked];
      for (let i = 0; i < 5 && blocked.packageCompleted; i++) {
        blocked = await f.run("maintain");
        discovery.push(blocked);
      }
      assert.equal(blocked.ok, false);
      assert.match(
        blocked.error,
        /Unknown saved-answer dependencies: answers\/unknown/,
      );
      assert.equal(await readFile(independentFile, "utf8"), before);
      const safe = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "beta/README.md",
      );
      assert.ok(
        !safe.evidence.some((e: any) =>
          ["answers/mixed", "answers/unknown"].includes(e.id),
        ),
      );
      await assert.rejects(
        readFile(path.join(f.config.output, "wiki/answers/unknown.md")),
        /ENOENT/,
      );
      assert.doesNotMatch(safe.answer, /Alpha|vier|Beide/);
      await writeFile(
        path.join(f.dir, "critical-answer-scope.json"),
        JSON.stringify(
          {
            mixed,
            independent,
            changed,
            alpha,
            next,
            beta,
            unknown,
            discovery,
            blocked,
            safe,
          },
          null,
          2,
        ),
      );
      console.log("Critical answer scope evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical: unavailable scans preserve inventory but confirmed removal withdraws published source notes and answers from real query",
  { timeout: 35000 },
  async () => {
    const f = await fixture(scopedProvider, { timeoutMs: 12000 });
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    await f.saveConfig();
    for (let i = 0; i < 4; i++)
      await writeFile(
        path.join(f.dir, `beta/old${i}.md`),
        "# Kontrollseite\nKontrollseite.\n",
      );
    try {
      await f.run("maintain");
      const published = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/README.md",
        "--save",
        "alpha",
      );
      assert.equal(published.fallback, false);
      assert.match(published.answer, /Alpha verlangt zwei/);
      const inventoryPath = path.join(
        f.config.output,
        ".state/maintenance-inventory.json",
      );
      const inventoryBefore = await readFile(inventoryPath, "utf8");
      await rename(path.join(f.dir, "alpha"), path.join(f.dir, "alpha-away"));
      const unavailable = await f.run("maintain");
      assert.match(unavailable.error, /Incomplete scan/);
      assert.equal(await readFile(inventoryPath, "utf8"), inventoryBefore);
      const unavailableQuery = await f.run("query", "--question", "Freigabe");
      assert.equal(
        unavailableQuery.ok,
        false,
        "incomplete live scan cannot certify historical originals",
      );
      await rename(path.join(f.dir, "alpha-away"), path.join(f.dir, "alpha"));
      await unlink(path.join(f.dir, "alpha/README.md"));
      const removed = await f.run("maintain");
      const query = await f.run("query", "--question", "Freigabe");
      assert.equal(query.ok, true, JSON.stringify(query));
      assert.doesNotMatch(query.answer, /Alpha|Beide/);
      assert.ok(!query.originals.some((s: any) => s.id === "alpha/README.md"));
      assert.ok(!query.evidence.some((e: any) => e.id === "answers/alpha"));
      await assert.rejects(
        readFile(path.join(f.config.output, "wiki/answers/alpha.md")),
        /ENOENT/,
      );
      const inventoryAfter = JSON.parse(await readFile(inventoryPath, "utf8"));
      assert.ok(inventoryAfter.sources["alpha/README.md"].removedAt);
      await writeFile(
        path.join(f.dir, "critical-removal.json"),
        JSON.stringify(
          {
            published,
            unavailable,
            unavailableQuery,
            removed,
            query,
            inventoryAfter,
          },
          null,
          2,
        ),
      );
      console.log("Critical removal evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical: graceful budget completion keeps actual capacity failure in final report for initial-only work",
  { timeout: 18000 },
  async () => {
    let release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    let calls = 0;
    const f = await fixture(
      async (body) => {
        if (body.tools && ++calls === 1) await gate;
      },
      { timeoutMs: 12000 },
    );
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    await writeFile(
      path.join(f.dir, "beta/old.md"),
      "# Kontrollseite\nKontrollseite.\n",
    );
    let timer: ReturnType<typeof setTimeout> | undefined;
    try {
      const started = Date.now();
      timer = setTimeout(release, 4150);
      const result = await helper(f, "grace-capacity");
      assert.equal(result.report.outcome, "budget-exhausted");
      assert.equal(
        result.report.contexts[0].maintenance.capacity.insufficientTimeCapacity,
        true,
      );
      assert.equal(calls, 1);
      const progress = JSON.parse(
        await readFile(
          path.join(f.dir, "grace-capacity/maintain-test.progress.json"),
          "utf8",
        ),
      );
      assert.equal(
        progress.maintenance.capacity.insufficientTimeCapacity,
        true,
      );
      const stdout = await readFile(
        path.join(f.dir, "grace-capacity/02-maintain-test.stdout"),
        "utf8",
      );
      const inner = JSON.parse(stdout);
      assert.equal(
        inner.maintenance.capacity.insufficientTimeCapacity,
        true,
        "final report must retain latched budget cause after catch recomputes inventory",
      );
      assert.equal(inner.maintenance.daily.pending, 0);
      assert.ok(inner.maintenance.initial.pending > 0);
      await writeFile(
        path.join(f.dir, "critical-grace-capacity.json"),
        JSON.stringify(
          { result, progress, inner, totalMs: Date.now() - started },
          null,
          2,
        ),
      );
      console.log("Critical graceful capacity evidence: " + f.dir);
    } finally {
      clearTimeout(timer);
      release();
      await f.close();
    }
  },
);
