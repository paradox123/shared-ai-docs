import { test } from "node:test";
import assert from "node:assert/strict";
import { writeFile, readFile, chmod } from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";
import { fixture } from "./support.ts";
function facts(body: any) {
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
  const material =
    prompt.split("--- SOURCE MATERIAL ---")[1] ||
    prompt.split("--- EVIDENCE ---")[1];
  if (!material) return;
  const lines = [
    ...new Set(
      material.match(
        /(?:Alpha|Beta) verlangt (?:zwei|drei|vier) Freigaben\./g,
      ) || [],
    ),
  ];
  const sources = [...material.matchAll(/--- SOURCE: (.*?) ---/g)].map(
    (m: any) => m[1],
  );
  return {
    role: "assistant",
    content:
      "# Geprüfte Aussagen\n" +
      lines.join("\n") +
      sources.map((s: string) => `\nBeleg ^[${s}:3-3]`).join(""),
  };
}
test(
  "activation: one observed public helper integrates provider stop, real source retrieval, priority, drift, restart and no-op",
  { timeout: 120000 },
  async () => {
    let mutate = false;
    const f = await fixture(
      async (body) => {
        if (mutate && body.tools) {
          mutate = false;
          await writeFile(
            path.join(f.dir, "beta/README.md"),
            "# Freigabe\nBeta verlangt vier Freigaben.\n",
          );
        }
        return facts(body);
      },
      { timeoutMs: 15000 },
    );
    (f.config as any).maintenance = { maxExtractionSources: 2 };
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    for (let i = 0; i < 4; i++)
      await writeFile(
        path.join(f.dir, `beta/old${i}.md`),
        "# Kontrollseite\nUnabhängige Kontrollseite.\n",
      );
    const reconcile = path.join(f.dir, "reconcile.py");
    await writeFile(reconcile, 'print(\'{"status":"ok"}\')\n');
    // External embeddings controlled; update/status operate the same real isolated SQLite store.
    const qmd = path.join(f.dir, "qmd.mjs");
    await writeFile(
      qmd,
      `#!/opt/homebrew/opt/node@22/bin/node\nconst {createStore}=await import('/opt/homebrew/lib/node_modules/@tobilu/qmd/dist/index.js');const store=await createStore({dbPath:${JSON.stringify(f.config.qmd.dbPath)}});try{const op=process.argv[2];console.log(JSON.stringify(op==='update'?await store.update():op==='status'?await store.getStatus():{controlledExternalEmbedding:true}));}finally{await store.close();}\n`,
    );
    await chmod(qmd, 0o755);
    const observations: any[] = [];
    async function run(name: string) {
      const start = Date.now();
      const value = await new Promise<any>((resolve, reject) => {
        const p = spawn(
          "python3",
          [
            new URL("../scripts/run-maintenance.py", import.meta.url).pathname,
            "--artifacts",
            path.join(f.dir, name),
            "--config",
            f.configPath,
            "--qmd",
            qmd,
            "--reconcile",
            reconcile,
            "--budget-seconds",
            "15",
            "--termination-grace-seconds",
            "0.5",
            "--observation-margin-seconds",
            "2",
            "--stall-seconds",
            "5",
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
              elapsedMs: Date.now() - start,
              stderr: err,
            });
          } catch {
            reject(Error(out + err));
          }
        });
      });
      observations.push(value);
      return value;
    }
    try {
      f.fail((body) => !!body.tools, 503, "service_unavailable");
      const first = await run("provider-stop");
      assert.equal(first.ok, false);
      assert.equal(first.report.contexts[0].sourceIndex.ok, true);
      assert.equal(f.calls.filter((b) => b.tools).length, 1);
      f.fail(false);
      const fallback = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/README.md",
      );
      assert.equal(fallback.fallback, true);
      assert.equal(fallback.sourceRetrieval, "qmd-source-index");
      assert.match(fallback.answer, /Alpha verlangt zwei/);
      assert.doesNotMatch(fallback.answer, /Beta|Beide Repos/);
      const packageRun = await run("initial-package");
      assert.equal(packageRun.report.contexts[0].packageCompleted, true);
      const before = f.calls.length;
      await writeFile(
        path.join(f.dir, "alpha/new.md"),
        "# Freigabe\nAlpha verlangt vier Freigaben.\n",
      );
      mutate = true;
      const drift = await run("daily-drift");
      assert.equal(drift.ok, false);
      assert.equal(drift.report.contexts[0].sourceIndex.ok, false);
      assert.match(
        JSON.stringify(f.calls.slice(before).find((b) => b.tools)),
        /Alpha verlangt vier/,
      );
      const query = await f.run(
        "query",
        "--question",
        "Freigabe",
        "--source",
        "alpha/new.md",
      );
      assert.equal(query.fallback, false);
      assert.match(query.answer, /Alpha verlangt vier/);
      assert.doesNotMatch(query.answer, /Beta|Beide Repos/);
      let complete = drift;
      for (let i = 0; i < 6 && !complete.ok; i++)
        complete = await run("resume-" + i);
      assert.equal(complete.ok, true, JSON.stringify(complete));
      const shared = await f.run("query", "--question", "Freigabe");
      assert.match(shared.answer, /Alpha verlangt zwei/);
      assert.match(shared.answer, /Beta verlangt vier/);
      const count = f.calls.length;
      const noop = await run("noop");
      assert.equal(noop.ok, true);
      assert.equal(noop.report.contexts[0].noop, true);
      assert.equal(f.calls.length, count);
      const inventory = JSON.parse(
        await readFile(
          path.join(f.config.output, ".state/maintenance-inventory.json"),
          "utf8",
        ),
      );
      await writeFile(
        path.join(f.dir, "activation-acceptance.json"),
        JSON.stringify(
          {
            observations,
            fallback,
            query,
            shared,
            inventory,
            requests: f.calls,
            limits: {
              budgetSeconds: 15,
              graceSeconds: 0.5,
              observationSeconds: 17.5,
              maxExtractionSources: 2,
            },
            embedding:
              "controlled external generation; no semantic-retrieval claim",
          },
          null,
          2,
        ),
      );
      console.log("Activation integrated evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);
