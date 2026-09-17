import { test } from "node:test";
import assert from "node:assert/strict";
import { writeFile, readFile, access } from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";
import { fixture } from "./support.ts";

async function until(check: () => boolean) {
  const deadline = Date.now() + 8000;
  while (!check()) {
    if (Date.now() > deadline) throw Error("held provider not reached");
    await new Promise((r) => setTimeout(r, 20));
  }
}
async function save(f: any, slug: string, dependency: string) {
  const page = (await f.run("status")).pages.find(
    (p: any) => p.id === dependency,
  );
  const draft = path.join(f.dir, slug + ".json");
  await writeFile(
    draft,
    JSON.stringify({
      slug,
      question: slug,
      answer: "Gespeicherte " + slug,
      evidence: [{ id: page.id, hash: page.hash }],
    }),
  );
  assert.equal((await f.run("save", "--draft", draft)).ok, true);
}
async function helper(f: any, name: string) {
  const reconcile = path.join(f.dir, "reconcile.py");
  await writeFile(reconcile, `print('{"status":"ok"}')\n`);
  return new Promise<any>((resolve, reject) => {
    const p = spawn(
      "python3",
      [
        new URL("../scripts/maintain-index.py", import.meta.url).pathname,
        "--config",
        f.configPath,
        "--artifacts",
        path.join(f.dir, name),
        "--reconcile",
        reconcile,
        "--qmd",
        "/usr/bin/true",
        "--budget-seconds",
        "15",
        "--termination-grace-seconds",
        "0.5",
      ],
      { env: { ...process.env, ...f.env } },
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
          ...JSON.parse(out.trim().split("\n").at(-1)!),
          stderr: err,
        });
      } catch {
        reject(Error(out + err));
      }
    });
  });
}

test(
  "public helper isolates drift across a shared concept and answer chain while publishing independent work",
  { timeout: 60000 },
  async () => {
    const f = await fixture(
      (body) => {
        const prompt = body.messages.map((m: any) => m.content).join("\n");
        if (body.tools) {
          const source = prompt.split("--- SOURCE DOCUMENT ---")[1] || "";
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
                        concept: source.includes("Kontrollseite")
                          ? "Kontrollseite"
                          : "Freigabe",
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
        if (!body.tools && prompt.includes("--- EVIDENCE ---")) {
          const evidence = prompt.split("--- EVIDENCE ---")[1];
          const facts = [
            ...new Set(
              evidence.match(
                /(?:Alpha|Beta) verlangt (?:zwei|drei|vier) Freigaben\.|Kontrolle (?:NEU|ALT)\./g,
              ) || [],
            ),
          ];
          return { role: "assistant", content: facts.join(" ") };
        }
        if (!body.tools && prompt.includes('about "Kontrollseite"'))
          return {
            role: "assistant",
            content:
              "# Kontrollseite\n\nKontrolle " +
              (prompt.includes("NEU") ? "NEU" : "ALT"),
          };
      },
      { timeoutMs: 15000 },
    );
    let release = () => {};
    try {
      await writeFile(
        path.join(f.dir, "beta/control.md"),
        "# Kontrollseite\nKontrolle ALT.\n",
      );
      assert.equal((await f.run("maintain")).ok, true);
      await save(f, "direct", "concepts/freigabe");
      await save(f, "chain", "answers/direct");
      const beforeStatus = await f.run("status");
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      await writeFile(
        path.join(f.dir, "beta/control.md"),
        "# Kontrollseite\nKontrolle NEU.\n",
      );
      release = f.hold();
      const before = f.calls.length;
      const pending = helper(f, "drift-job");
      await until(() => f.calls.length > before);
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt drei Freigaben.\n",
      );
      release();
      const drift = await pending;
      assert.equal(drift.code, 1);
      const result = drift.contexts[0];
      assert.equal(result.ok, false);
      assert.ok(
        (result.completed || []).some((id: string) =>
          id.startsWith("source-notes/"),
        ),
        JSON.stringify(result),
      );
      for (const id of ["concepts/freigabe", "answers/direct", "answers/chain"])
        await assert.rejects(
          access(path.join(f.config.output, "wiki", id + ".md")),
        );
      const control = await f.run("query", "--question", "Kontrollseite");
      assert.equal(control.fallback, false, JSON.stringify(control));
      assert.match(control.answer, /Kontrolle NEU/);
      assert.doesNotMatch(control.answer, /Freigabe|Beide Repos/);
      assert.ok(
        control.evidence.every((e: any) => e.kind === "source-summary"),
      );
      assert.equal(result.sourceIndex.ok, false);
      assert.equal(result.sourceIndex.status, "stale");
      const current = await f.run("query", "--question", "Freigabe");
      assert.equal(current.fallback, true);
      assert.doesNotMatch(current.answer, /Alpha verlangt vier/);
      assert.equal(
        (await f.run("status")).lastCompleted,
        beforeStatus.lastCompleted,
      );
      const requests = f.calls.length;
      const repaired = await helper(f, "repair-job");
      assert.equal(repaired.code, 0, JSON.stringify(repaired));
      const verified = await f.run("query", "--question", "Freigabe");
      assert.ok(
        verified.evidence.some(
          (e: any) =>
            e.id === "concepts/freigabe" &&
            e.sourceVersions["alpha/README.md"] &&
            e.sourceVersions["beta/README.md"],
        ),
      );
      for (const id of ["answers/direct", "answers/chain"])
        await access(path.join(f.config.output, "wiki", id + ".md"));
      const newExtractions = f.calls.slice(requests).filter((b) => b.tools);
      assert.equal(newExtractions.length, 1, JSON.stringify(newExtractions));
      assert.match(JSON.stringify(newExtractions[0]), /Alpha verlangt drei/);
      const finalCalls = f.calls.length;
      const noop = await helper(f, "noop-job");
      assert.equal(noop.contexts[0].noop, true);
      assert.equal(f.calls.length, finalCalls);
      await writeFile(
        path.join(f.dir, "drift-acceptance.json"),
        JSON.stringify(
          { drift, control, current, repaired, verified, noop, newExtractions },
          null,
          2,
        ),
      );
      console.log("Drift evidence: " + f.dir);
    } finally {
      release();
      await f.close();
    }
  },
);

test(
  "a newly discovered source blocks global membership while a valid source answer survives a drift package",
  { timeout: 60000 },
  async () => {
    let held: Promise<void> | undefined;
    let release = () => {};
    let entered = false;
    const f = await fixture(
      async (body) => {
        const prompt = body.messages.map((m: any) => m.content).join("\n");
        if (body.tools && held && prompt.includes("Alpha verlangt vier")) {
          entered = true;
          await held;
        }
      },
      { timeoutMs: 15000 },
    );
    (f.config as any).concurrency = 1;
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    await f.saveConfig();
    try {
      await writeFile(
        path.join(f.dir, "beta/z-control.md"),
        "# Kontrollseite\nKontrolle stabil.\n",
      );
      const first = await f.run("maintain");
      assert.equal(first.packageCompleted, true);
      const summary = (await f.run("status")).pages.find(
        (p: any) =>
          p.kind === "source-summary" && p.sourceVersions["beta/README.md"],
      );
      await save(f, "stable-source-answer", summary.id);
      const file = path.join(
        f.config.output,
        "wiki/answers/stable-source-answer.md",
      );
      const bytes = await readFile(file, "utf8");
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      held = new Promise<void>((r) => {
        release = r;
      });
      const start = f.calls.length;
      const pending = f.run("maintain");
      await until(() => entered);
      // Stable beta is the queued cached candidate; introduce a separate new
      // source while alpha runs so global membership is also unknown.
      await writeFile(
        path.join(f.dir, "alpha/new.md"),
        "# Freigabe\nNeue unentdeckte Quelle.\n",
      );
      release();
      held = undefined;
      const partial = await pending;
      assert.equal(partial.ok, false);
      assert.equal(partial.packageCompleted, true);
      assert.ok(
        partial.maintenance.daily.sources.includes("alpha/new.md"),
        "discovered additions enter the current daily report",
      );
      assert.equal(await readFile(file, "utf8"), bytes);
      const query = await f.run(
        "query",
        "--question",
        "stable-source-answer",
        "--source",
        "beta/README.md",
      );
      assert.ok(
        query.evidence.some(
          (p: any) => p.id === "answers/stable-source-answer",
        ),
        JSON.stringify(query),
      );
      assert.equal(
        query.originals.every((o: any) => o.freshness === "checked-current"),
        true,
      );
      const repairStart = f.calls.length;
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true, JSON.stringify(repaired));
      assert.equal(f.calls.slice(repairStart).filter((b) => b.tools).length, 1);
      assert.equal(await readFile(file, "utf8"), bytes);
      await writeFile(
        path.join(f.dir, "drift-package-answer.json"),
        JSON.stringify(
          { first, partial, query, repaired, requests: f.calls.slice(start) },
          null,
          2,
        ),
      );
      console.log("Drift package answer evidence: " + f.dir);
    } finally {
      release();
      await f.close();
    }
  },
);

test(
  "a cached extraction queued behind a held source is rejected after its original changes",
  { timeout: 45000 },
  async () => {
    const f = await fixture(undefined, { timeoutMs: 15000 });
    (f.config as any).concurrency = 1;
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    await f.saveConfig();
    (f.env as any).WIKI_MAINTENANCE_NOW = "2026-09-17T12:00:00Z";
    let release = () => {};
    try {
      await writeFile(
        path.join(f.dir, "beta/z.md"),
        "# Kontrollseite\nKontrolle.\n",
      );
      assert.equal((await f.run("maintain")).packageCompleted, true);
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      const start = f.calls.length;
      release = f.hold();
      const pending = f.run("maintain");
      await until(() => f.calls.length > start);
      await writeFile(
        path.join(f.dir, "beta/README.md"),
        "# Freigabe\nBeta verlangt vier Freigaben.\n",
      );
      release();
      const result = await pending;
      assert.equal(result.ok, false);
      assert.ok(
        result.maintenance.daily.sources.includes("beta/README.md"),
        "newly observed drift version must become daily in this report",
      );
      const inventoryFile = path.join(
        f.config.output,
        ".state/maintenance-inventory.json",
      );
      const observed = JSON.parse(await readFile(inventoryFile, "utf8"))
        .sources["beta/README.md"];
      assert.equal(observed.classification, "daily");
      assert.equal(observed.observedAt, "2026-09-17T12:00:00.000Z");
      assert.equal(observed.dueDate, "2026-09-18");
      assert.equal(
        result.extractions.reused,
        0,
        "stale queued beta cache must not be counted as reusable success",
      );
      assert.ok(
        result.failures.some((x: any) =>
          /before extraction reuse/.test(x.error),
        ),
        JSON.stringify(result),
      );
      assert.equal(
        (
          await f.run(
            "query",
            "--question",
            "Freigabe",
            "--source",
            "beta/README.md",
          )
        ).fallback,
        true,
      );
      (f.env as any).WIKI_MAINTENANCE_NOW = "2026-09-20T12:00:00Z";
      f.fail(true, 401);
      const overdue = await f.run("maintain");
      assert.ok(overdue.maintenance.daily.overdue.includes("beta/README.md"));
      const later = JSON.parse(await readFile(inventoryFile, "utf8")).sources[
        "beta/README.md"
      ];
      assert.deepEqual(
        later,
        observed,
        "restart must not move first observation or its deadline",
      );
      f.fail(false);
      const beforeRepair = f.calls.length;
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true, JSON.stringify(repaired));
      assert.equal(
        f.calls.slice(beforeRepair).filter((b) => b.tools).length,
        1,
      );
      await writeFile(
        path.join(f.dir, "queued-reuse.json"),
        JSON.stringify(
          {
            result,
            observed,
            overdue,
            later,
            repaired,
            requests: f.calls.slice(start),
          },
          null,
          2,
        ),
      );
      console.log("Queued reuse evidence: " + f.dir);
    } finally {
      release();
      await f.close();
    }
  },
);

test(
  "an isolated answer failure withholds its transitive chain and keeps an independent saved answer byte-identical and searchable",
  { timeout: 45000 },
  async () => {
    const f = await fixture(undefined, { timeoutMs: 15000 });
    try {
      await writeFile(
        path.join(f.dir, "beta/control.md"),
        "# Kontrollseite\nUnabhängige Kontrolle.\n",
      );
      assert.equal((await f.run("maintain")).ok, true);
      await save(f, "direct", "concepts/freigabe");
      await save(f, "chain", "answers/direct");
      await save(f, "stable-control", "concepts/kontrollseite");
      const file = path.join(f.config.output, "wiki/answers/stable-control.md");
      const bytes = await readFile(file, "utf8");
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      f.fail((b) => JSON.stringify(b).includes("--- EVIDENCE ---"));
      const failed = await f.run("maintain");
      assert.equal(failed.ok, false);
      for (const id of ["answers/direct", "answers/chain"])
        await assert.rejects(
          access(path.join(f.config.output, "wiki", id + ".md")),
        );
      assert.equal(await readFile(file, "utf8"), bytes);
      f.fail(false);
      const query = await f.run(
        "query",
        "--question",
        "stable-control",
        "--source",
        "beta/control.md",
      );
      assert.ok(
        query.evidence.some((e: any) => e.id === "answers/stable-control"),
        JSON.stringify(query),
      );
      const start = f.calls.length;
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true, JSON.stringify(repaired));
      assert.equal(f.calls.slice(start).filter((b) => b.tools).length, 0);
      assert.equal(await readFile(file, "utf8"), bytes);
      const count = f.calls.length;
      assert.equal((await f.run("maintain")).noop, true);
      assert.equal(f.calls.length, count);
      await writeFile(
        path.join(f.dir, "answer-chain.json"),
        JSON.stringify({ failed, query, repaired }, null, 2),
      );
      console.log("Answer chain evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);
