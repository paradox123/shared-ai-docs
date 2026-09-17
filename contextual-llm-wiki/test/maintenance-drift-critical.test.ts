import { test } from "node:test";
import assert from "node:assert/strict";
import {
  writeFile,
  readFile,
  rename,
  rm,
  mkdir,
  unlink,
  access,
} from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";

// Controlled provider: emit only facts and IDs actually present in this request.
// Never reuse the generic fixture's cross-repository narrative for scoped evidence.
function factsFromRequest(body: any) {
  const prompt = body.messages.map((m: any) => m.content).join("\n");
  if (prompt.includes("--- RELEVANCE CANDIDATES ---")) return;
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
  const material =
    prompt.split("--- EVIDENCE ---")[1] ||
    prompt.split("--- SOURCE MATERIAL ---")[1] ||
    "";
  const facts = [
    ...new Set(
      material.match(
        /(?:Alpha|Beta) verlangt (?:zwei|drei|vier) Freigaben\.|Unabhängige Kontrollseite(?: NEU)?\.|Kontrollseite Beta NEU\.|Kontrollseite Alpha tritt nun bei\./g,
      ) || [],
    ),
  ];
  const ids = [
    ...material.matchAll(/--- ([^@\n]+) @|--- SOURCE: (.*?) ---/g),
  ].map((m) => (m[1] || m[2]).trim());
  const title = prompt.match(/about "([^"]+)"/)?.[1] || "Geprüfte Aussagen";
  return {
    role: "assistant",
    content:
      "# " + title + "\n\n" + facts.join(" ") + "\n\nBelege: " + ids.join(", "),
  };
}
const answerRequest = (f: any) =>
  f.calls.findLast((b: any) => JSON.stringify(b).includes("--- EVIDENCE ---"));

async function until(check: () => boolean) {
  const deadline = Date.now() + 7000;
  while (!check()) {
    if (Date.now() > deadline)
      throw Error("controlled provider hold not reached");
    await new Promise((r) => setTimeout(r, 15));
  }
}
const inventory = async (f: any) =>
  JSON.parse(
    await readFile(
      path.join(f.config.output, ".state/maintenance-inventory.json"),
      "utf8",
    ),
  );
const record = async (f: any, name: string, value: any) => {
  await writeFile(
    path.join(f.dir, name + ".json"),
    JSON.stringify(value, null, 2),
  );
  console.log(name + ": " + f.dir);
};

test(
  "critical: confirmed removal and concurrent source change preserve only current source statements and resume the remaining version",
  { timeout: 45000 },
  async () => {
    const f = await fixture(factsFromRequest, { timeoutMs: 12000 });
    let release = () => {};
    try {
      await writeFile(
        path.join(f.dir, "beta/control.md"),
        "# Kontrollseite\nUnabhängige Kontrollseite.\n",
      );
      assert.equal((await f.run("maintain")).ok, true);
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      await writeFile(
        path.join(f.dir, "beta/control.md"),
        "# Kontrollseite\nUnabhängige Kontrollseite NEU.\n",
      );
      const start = f.calls.length;
      release = f.hold();
      const pending = f.run("maintain");
      await until(() => f.calls.length > start);
      await unlink(path.join(f.dir, "beta/README.md"));
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt drei Freigaben.\n",
      );
      release();
      const partial = await pending;
      assert.equal(partial.ok, false);
      assert.equal(partial.packageCompleted, true);
      assert.deepEqual(
        new Set(partial.sourceIndex.drift),
        new Set(["alpha/README.md", "beta/README.md"]),
      );
      const observed = await inventory(f);
      assert.ok(observed.sources["beta/README.md"].removedAt);
      assert.equal(observed.sources["alpha/README.md"].classification, "daily");
      assert.equal(observed.sources["beta/control.md"].removedAt, null);
      const query = await f.run("query", "--question", "Freigabe");
      assert.equal(query.ok, true);
      assert.equal(query.fallback, true);
      assert.ok(
        query.originals.every(
          (o: any) =>
            o.id !== "beta/README.md" && o.freshness === "checked-current",
        ),
      );
      assert.match(query.answer, /Alpha verlangt drei Freigaben/);
      assert.doesNotMatch(
        query.answer,
        /Beta verlangt|Alpha verlangt vier|Beide Repos/,
      );
      const queryRequest = answerRequest(f);
      assert.match(
        JSON.stringify(queryRequest),
        /Alpha verlangt drei Freigaben/,
      );
      assert.doesNotMatch(
        JSON.stringify(queryRequest),
        /Beta verlangt|beta\/README|Beide Repos/,
      );
      const control = await f.run("query", "--question", "Kontrollseite");
      assert.equal(control.fallback, false);
      assert.ok(
        control.evidence.every((p: any) => p.kind === "source-summary"),
      );
      assert.match(control.answer, /Unabhängige Kontrollseite NEU/);
      assert.doesNotMatch(control.answer, /Freigabe|Beide Repos/);
      const controlRequest = answerRequest(f);
      assert.match(
        JSON.stringify(controlRequest),
        /Unabhängige Kontrollseite NEU/,
      );
      assert.doesNotMatch(
        JSON.stringify(controlRequest),
        /Alpha verlangt|beta\/README/,
      );
      const repairStart = f.calls.length;
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true, JSON.stringify(repaired));
      assert.equal(f.calls.slice(repairStart).filter((b) => b.tools).length, 1);
      assert.match(
        JSON.stringify(f.calls.slice(repairStart).filter((b) => b.tools)[0]),
        /Alpha verlangt drei/,
      );
      const final = await f.run("query", "--question", "Freigabe");
      assert.match(final.answer, /Alpha verlangt drei Freigaben/);
      assert.doesNotMatch(final.answer, /Beta verlangt|Beide Repos/);
      const finalRequest = answerRequest(f);
      assert.doesNotMatch(
        JSON.stringify(finalRequest),
        /Beta verlangt|beta\/README|Beide Repos/,
      );
      const concept = final.evidence.find(
        (p: any) => p.id === "concepts/freigabe",
      );
      assert.deepEqual(Object.keys(concept.sourceVersions), [
        "alpha/README.md",
      ]);
      const count = f.calls.length;
      assert.equal((await f.run("maintain")).noop, true);
      assert.equal(f.calls.length, count);
      await record(f, "critical-combined-removal", {
        partial,
        observed,
        query,
        control,
        repaired,
        final,
        queryRequest,
        controlRequest,
        finalRequest,
      });
    } finally {
      release();
      await f.close();
    }
  },
);

test(
  "critical: a configured root disappearing after scan cannot become confirmed removal or current query evidence",
  { timeout: 45000 },
  async () => {
    const f = await fixture(factsFromRequest, { timeoutMs: 12000 });
    let release = () => {};
    let moved = false;
    try {
      await writeFile(
        path.join(f.dir, "beta/control.md"),
        "# Kontrollseite\nUnabhängige Kontrollseite.\n",
      );
      assert.equal((await f.run("maintain")).ok, true);
      const controlFile = path.join(
        f.config.output,
        "wiki/concepts/kontrollseite.md",
      );
      const bytes = await readFile(controlFile, "utf8");
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      const start = f.calls.length;
      release = f.hold();
      const pending = f.run("maintain");
      await until(() => f.calls.length > start);
      const before = await inventory(f);
      await rename(path.join(f.dir, "beta"), path.join(f.dir, "beta-offline"));
      moved = true;
      release();
      const failed = await pending;
      assert.equal(failed.ok, false);
      assert.match(failed.error, /Incomplete scan/);
      const after = await inventory(f);
      for (const id of ["beta/README.md", "beta/control.md"])
        assert.deepEqual(after.sources[id], before.sources[id]);
      assert.equal(await readFile(controlFile, "utf8"), bytes);
      const unavailable = await f.run("query", "--question", "Kontrollseite");
      assert.equal(unavailable.ok, false);
      assert.match(unavailable.error, /Incomplete scan/);
      await rename(path.join(f.dir, "beta-offline"), path.join(f.dir, "beta"));
      moved = false;
      const repairStart = f.calls.length;
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true, JSON.stringify(repaired));
      assert.equal(f.calls.slice(repairStart).filter((b) => b.tools).length, 0);
      assert.equal(await readFile(controlFile, "utf8"), bytes);
      await record(f, "critical-late-scan-failure", {
        failed,
        before,
        after,
        unavailable,
        repaired,
      });
    } finally {
      release();
      if (moved)
        await rename(
          path.join(f.dir, "beta-offline"),
          path.join(f.dir, "beta"),
        );
      await f.close();
    }
  },
);

test(
  "critical: a late index failure after confirmed drift preserves its first observation deadline and reusable extraction",
  { timeout: 45000 },
  async () => {
    let fault = true;
    const f = await fixture(
      async (body) => {
        if (fault && !body.tools) {
          fault = false;
          await writeFile(
            path.join(f.dir, "alpha/README.md"),
            "# Freigabe\nAlpha verlangt vier Freigaben.\n",
          );
          await rename(f.config.qmd.dbPath, f.config.qmd.dbPath + ".preserved");
          await mkdir(f.config.qmd.dbPath);
        }
        return factsFromRequest(body);
      },
      { timeoutMs: 12000 },
    );
    (f.env as any).WIKI_MAINTENANCE_NOW = "2026-09-17T12:00:00Z";
    try {
      const failed = await f.run("maintain");
      assert.equal(failed.ok, false);
      assert.equal(failed.sourceIndex.ok, false);
      assert.equal(failed.sourceIndex.status, "stale");
      assert.ok(failed.maintenance.daily.sources.includes("alpha/README.md"));
      const observed = (await inventory(f)).sources["alpha/README.md"];
      assert.equal(observed.dueDate, "2026-09-18");
      assert.equal(observed.observedAt, "2026-09-17T12:00:00.000Z");
      assert.equal((await f.run("status")).lastCompleted, null);
      assert.equal(f.calls.filter((b) => b.tools).length, 2);
      await rm(f.config.qmd.dbPath, { recursive: true });
      await rename(f.config.qmd.dbPath + ".preserved", f.config.qmd.dbPath);
      (f.env as any).WIKI_MAINTENANCE_NOW = "2026-09-20T12:00:00Z";
      f.fail(true, 401);
      const overdue = await f.run("maintain");
      assert.ok(overdue.maintenance.daily.overdue.includes("alpha/README.md"));
      assert.deepEqual(
        (await inventory(f)).sources["alpha/README.md"],
        observed,
      );
      f.fail(false);
      const repairStart = f.calls.length;
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true, JSON.stringify(repaired));
      assert.equal(f.calls.slice(repairStart).filter((b) => b.tools).length, 1);
      const query = await f.run("query", "--question", "Freigabe");
      assert.equal(query.fallback, false);
      assert.match(query.answer, /Alpha verlangt vier/);
      const count = f.calls.length;
      const noop = await f.run("maintain");
      assert.equal(noop.noop, true);
      assert.equal(f.calls.length, count);
      await record(f, "critical-drift-index-deadline", {
        failed,
        observed,
        overdue,
        repaired,
        query,
        noop,
      });
    } finally {
      await f.close();
    }
  },
);

test(
  "critical: a held query cannot certify or save evidence whose source changes during answer latency",
  { timeout: 30000 },
  async () => {
    let holdAnswer = false;
    let entered = false;
    let release = () => {};
    let held: Promise<void>;
    const f = await fixture(
      async (body) => {
        if (holdAnswer && JSON.stringify(body).includes("--- EVIDENCE ---")) {
          entered = true;
          await held;
        }
        return factsFromRequest(body);
      },
      { timeoutMs: 12000 },
    );
    try {
      assert.equal((await f.run("maintain")).ok, true);
      held = new Promise<void>((r) => {
        release = r;
      });
      holdAnswer = true;
      const pending = f.run(
        "query",
        "--question",
        "Freigabe",
        "--save",
        "stale-query",
      );
      await until(() => entered);
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      release();
      holdAnswer = false;
      const stale = await pending;
      assert.equal(stale.ok, false);
      assert.match(stale.error, /Evidence changed during query/);
      assert.equal(stale.originals, undefined);
      await assert.rejects(
        access(path.join(f.config.output, "wiki/answers/stale-query.md")),
      );
      const fresh = await f.run("query", "--question", "Freigabe");
      assert.equal(fresh.ok, true);
      assert.equal(fresh.fallback, true);
      assert.match(fresh.answer, /Alpha verlangt vier/);
      assert.ok(
        fresh.originals.every((o: any) => o.freshness === "checked-current"),
      );
      await record(f, "critical-query-latency", { stale, fresh });
    } finally {
      release();
      await f.close();
    }
  },
);

test(
  "critical: a drifting source can join the old control concept without its old ownership concealing the new dependency",
  { timeout: 40000 },
  async () => {
    const f = await fixture(factsFromRequest, { timeoutMs: 12000 });
    let release = () => {};
    try {
      await writeFile(
        path.join(f.dir, "beta/control.md"),
        "# Kontrollseite\nUnabhängige Kontrollseite.\n",
      );
      assert.equal((await f.run("maintain")).ok, true);
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      await writeFile(
        path.join(f.dir, "beta/control.md"),
        "# Kontrollseite\nKontrollseite Beta NEU.\n",
      );
      release = f.hold();
      const start = f.calls.length;
      const pending = f.run("maintain");
      await until(() => f.calls.length > start);
      await writeFile(
        path.join(f.dir, "alpha/README.md"),
        "# Kontrollseite\nKontrollseite Alpha tritt nun bei.\n",
      );
      release();
      const partial = await pending;
      assert.equal(partial.ok, false);
      await assert.rejects(
        access(path.join(f.config.output, "wiki/concepts/kontrollseite.md")),
      );
      const scoped = await f.run(
        "query",
        "--question",
        "Kontrollseite",
        "--source",
        "beta/control.md",
      );
      assert.equal(scoped.fallback, false);
      assert.ok(
        scoped.evidence.every(
          (e: any) =>
            e.kind === "source-summary" &&
            Object.keys(e.sourceVersions).join() === "beta/control.md",
        ),
      );
      assert.deepEqual(
        scoped.originals.map((o: any) => o.id),
        ["beta/control.md"],
      );
      assert.match(scoped.answer, /Kontrollseite Beta NEU/);
      assert.doesNotMatch(scoped.answer, /Alpha|Freigabe|Beide Repos/);
      const scopedRequest = answerRequest(f);
      assert.match(JSON.stringify(scopedRequest), /Kontrollseite Beta NEU/);
      assert.doesNotMatch(
        JSON.stringify(scopedRequest),
        /Alpha|alpha\/README|Freigabe|Beide Repos/,
      );
      const repairStart = f.calls.length;
      const repaired = await f.run("maintain");
      assert.equal(repaired.ok, true, JSON.stringify(repaired));
      assert.equal(f.calls.slice(repairStart).filter((b) => b.tools).length, 1);
      const common = await f.run("query", "--question", "Kontrollseite");
      assert.match(common.answer, /Kontrollseite Beta NEU/);
      assert.match(common.answer, /Kontrollseite Alpha tritt nun bei/);
      assert.match(common.answer, /concepts\/kontrollseite/);
      assert.doesNotMatch(common.answer, /Freigabe|Beide Repos/);
      const commonRequest = answerRequest(f);
      assert.match(JSON.stringify(commonRequest), /Kontrollseite Beta NEU/);
      assert.match(
        JSON.stringify(commonRequest),
        /Kontrollseite Alpha tritt nun bei/,
      );
      assert.match(
        JSON.stringify(commonRequest),
        /alpha\/README\.md, beta\/control\.md|beta\/control\.md, alpha\/README\.md/,
      );
      const concept = common.evidence.find(
        (e: any) => e.id === "concepts/kontrollseite",
      );
      assert.deepEqual(
        new Set(Object.keys(concept.sourceVersions)),
        new Set(["alpha/README.md", "beta/control.md"]),
      );
      await record(f, "critical-new-ownership", {
        partial,
        scoped,
        repaired,
        common,
        scopedRequest,
        commonRequest,
        extractionRequests: f.calls.slice(repairStart).filter((b) => b.tools),
      });
    } finally {
      release();
      await f.close();
    }
  },
);
