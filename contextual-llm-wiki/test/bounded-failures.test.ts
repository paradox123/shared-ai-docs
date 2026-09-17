import { test } from "node:test";
import assert from "node:assert/strict";
import { writeFile, readFile } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";

test("a bounded generation failure publishes independent knowledge and resumes only unfinished work", async () => {
  let fail = false;
  const f = await fixture((body) => {
    const prompt = body.messages.map((m: any) => m.content).join("\n");
    if (!body.tools && prompt.includes('about "Freigabe"') && fail)
      return { role: "assistant", content: "" };
    if (!body.tools && prompt.includes('about "Kontrollseite"'))
      return {
        role: "assistant",
        content:
          "# Kontrollseite\n\n" +
          (prompt.includes("Kontrolle NEU")
            ? "Kontrolle NEU."
            : "Kontrolle ALT."),
      };
  });
  try {
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle ALT.\n",
    );
    assert.equal((await f.run("maintain")).ok, true);
    const page = (await f.run("status")).pages.find(
      (p: any) => p.id === "concepts/freigabe",
    );
    for (const [slug, evidence] of [
      ["direct", page],
      ["transitive", null],
    ] as const) {
      const dep =
        evidence ||
        (await f.run("status")).pages.find(
          (p: any) => p.id === "answers/direct",
        );
      const draft = path.join(f.dir, "draft.json");
      await writeFile(
        draft,
        JSON.stringify({
          slug,
          question: "Freigabe",
          answer: "Gespeicherte Freigabe.",
          evidence: [{ id: dep.id, hash: dep.hash }],
        }),
      );
      assert.equal((await f.run("save", "--draft", draft)).ok, true);
    }
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle NEU.\n",
    );
    fail = true;
    const partial = await f.run("maintain");
    assert.equal(partial.ok, false);
    assert.equal(partial.code, 1);
    assert.match(
      await readFile(
        path.join(f.config.output, "wiki/concepts/kontrollseite.md"),
        "utf8",
      ),
      /Kontrolle NEU/,
    );
    assert.equal(
      (await f.run("search", "--question", "Freigabe")).results.length,
      0,
    );
    const control = await f.run("query", "--question", "Kontrolle");
    assert.equal(control.ok, true, JSON.stringify(control));
    assert.equal(control.fallback, false);
    assert.deepEqual(
      control.evidence.map((e: any) => e.id),
      ["concepts/kontrollseite"],
    );
    assert.equal(partial.qmdSafe, true);
    assert.ok(partial.pending.length);
    const count = f.calls.length;
    fail = false;
    const repaired = await f.run("maintain");
    assert.equal(repaired.ok, true, JSON.stringify(repaired));
    assert.ok(
      !f.calls
        .slice(count)
        .some(
          (b: any) => b.tools && JSON.stringify(b).includes("Kontrolle NEU"),
        ),
    );
    assert.equal(
      (await f.run("status")).pages.filter((p: any) => !p.withdrawn).length,
      4,
    );
    const repairedCalls = f.calls.length;
    assert.equal((await f.run("maintain")).noop, true);
    assert.equal(f.calls.length, repairedCalls);
  } finally {
    await f.close();
  }
});

test("an answer provider failure retains the answer for repair while independent compilation completes", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    assert.equal(
      (await f.run("query", "--question", "Freigabe", "--save", "saved")).ok,
      true,
    );
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle.\n",
    );
    f.fail((body) => JSON.stringify(body).includes("--- EVIDENCE ---"));
    const partial = await f.run("maintain");
    assert.equal(partial.ok, false);
    assert.equal(partial.qmdSafe, true, JSON.stringify(partial));
    assert.ok(
      (await f.run("search", "--question", "Kontrollseite")).results.length,
    );
    const status = await f.run("status");
    assert.equal(
      status.pages.find((p: any) => p.id === "answers/saved").withdrawn,
      true,
    );
    f.fail(false);
    const count = f.calls.length;
    assert.equal((await f.run("maintain")).ok, true);
    assert.ok(!f.calls.slice(count).some((b: any) => b.tools));
    assert.notEqual(
      (await f.run("status")).pages.find((p: any) => p.id === "answers/saved")
        .withdrawn,
      true,
    );
  } finally {
    await f.close();
  }
});

test("a missing configured root is an incomplete scan, never a confirmed removal", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    const before = await readFile(
      path.join(f.config.output, "wiki/concepts/freigabe.md"),
      "utf8",
    );
    const { rename } = await import("node:fs/promises");
    await rename(path.join(f.dir, "alpha"), path.join(f.dir, "alpha-offline"));
    const failed = await f.run("maintain");
    assert.equal(failed.ok, false);
    assert.match(failed.error, /Incomplete scan/);
    assert.equal(
      await readFile(
        path.join(f.config.output, "wiki/concepts/freigabe.md"),
        "utf8",
      ),
      before,
    );
    assert.equal((await f.run("query", "--question", "Freigabe")).ok, false);
    await rename(path.join(f.dir, "alpha-offline"), path.join(f.dir, "alpha"));
    assert.equal((await f.run("maintain")).noop, true);
  } finally {
    await f.close();
  }
});

test("a real source extraction error preserves independent results and raw local evidence", async () => {
  const f = await fixture();
  try {
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle ALT.\n",
    );
    assert.equal((await f.run("maintain")).ok, true);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle NEU.\n",
    );
    f.fail((b) => b.tools && JSON.stringify(b).includes("Alpha verlangt vier"));
    const partial = await f.run("maintain");
    assert.equal(partial.ok, false);
    assert.equal(partial.qmdSafe, true, JSON.stringify(partial));
    assert.match(
      await readFile(partial.report, "utf8"),
      /controlled provider failure/,
    );
    assert.match(
      await readFile(
        path.join(partial.artifacts, "compiler-result.json"),
        "utf8",
      ),
      /controlled provider failure/,
    );
    assert.ok(
      (await f.run("search", "--question", "Kontrollseite")).results.length,
    );
    assert.equal(
      (await f.run("search", "--question", "Freigabe")).results.length,
      0,
    );
    f.fail(false);
    assert.equal((await f.run("maintain")).ok, true);
    assert.equal((await f.run("maintain")).noop, true);
  } finally {
    await f.close();
  }
});

test("an extraction failure with unknown dependencies cannot publish a purported independent result", async () => {
  const f = await fixture();
  try {
    f.fail((b) => b.tools && JSON.stringify(b).includes("Alpha verlangt zwei"));
    const failed = await f.run("maintain");
    assert.equal(failed.ok, false);
    assert.equal(failed.qmdSafe, false);
    assert.match(failed.error, /Unknown dependencies/);
    assert.equal((await f.run("status")).pages.length, 0);
    f.fail(false);
    assert.equal((await f.run("maintain")).ok, true);
  } finally {
    await f.close();
  }
});

test("missing saved-answer dependency records remain pending instead of silently disappearing", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    assert.equal(
      (await f.run("query", "--question", "Freigabe", "--save", "saved")).ok,
      true,
    );
    const file = path.join(f.config.output, ".state/state.json");
    const state = JSON.parse(await readFile(file, "utf8"));
    state.pages["answers/saved"].pageVersions["concepts/unknown"] = "unknown";
    await writeFile(file, JSON.stringify(state));
    const failed = await f.run("maintain");
    assert.equal(failed.ok, false);
    assert.ok((await f.run("status")).pending.length);
    assert.equal(
      (await f.run("status")).pages.find((p: any) => p.id === "answers/saved")
        .withdrawn,
      true,
    );
  } finally {
    await f.close();
  }
});

test("the public job reports a real wiki partial failure while safe retrieval steps finish", async () => {
  const { execFile } = await import("node:child_process");
  const { promisify } = await import("node:util");
  const { chmod } = await import("node:fs/promises");
  const run = promisify(execFile);
  const f = await fixture();
  try {
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle ALT.\n",
    );
    assert.equal((await f.run("maintain")).ok, true);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle NEU.\n",
    );
    // Only the global reconciler/embedding job are process-boundary peers.
    // Wiki maintain/status/lint, pinned compilation and its QMD DB are real.
    const reconcile = path.join(f.dir, "reconcile.py");
    const retrieval = path.join(f.dir, "retrieval");
    await writeFile(reconcile, 'print(\'{"status":"ok"}\')\n');
    await writeFile(retrieval, '#!/bin/sh\nprintf "finished %s\\n" "$1"\n');
    await chmod(retrieval, 0o755);
    const job = async (name: string) => {
      try {
        const p = await run(
          "python3",
          [
            new URL("../scripts/maintain-index.py", import.meta.url).pathname,
            "--config",
            f.configPath,
            "--artifacts",
            path.join(f.dir, name),
            "--wiki",
            new URL("../wiki", import.meta.url).pathname,
            "--qmd",
            retrieval,
            "--reconcile",
            reconcile,
          ],
          { env: { ...process.env, ...f.env } },
        );
        return {
          code: 0,
          report: JSON.parse(p.stdout.trim().split("\n").at(-1)!),
        };
      } catch (e: any) {
        return {
          code: e.code,
          report: JSON.parse(e.stdout.trim().split("\n").at(-1)!),
        };
      }
    };
    f.fail((b) => b.tools && JSON.stringify(b).includes("Alpha verlangt vier"));
    const partial = await job("partial-job");
    assert.equal(partial.code, 1);
    assert.equal(partial.report.ok, false);
    assert.deepEqual(
      partial.report.steps.slice(-3).map((s: any) => s.name),
      ["qmd-update", "qmd-embed", "qmd-status"],
      JSON.stringify(partial),
    );
    assert.ok(
      partial.report.contexts[0].completed.includes("concepts/kontrollseite"),
    );
    assert.match(
      await readFile(
        path.join(f.dir, "partial-job/02-maintain-test.stdout"),
        "utf8",
      ),
      /controlled provider failure/,
    );
    assert.equal(
      await readFile(
        path.join(f.dir, "partial-job/02-maintain-test.exitcode"),
        "utf8",
      ),
      "1\n",
    );
    assert.equal(
      (await f.run("query", "--question", "Kontrollseite")).fallback,
      false,
    );
    f.fail(false);
    assert.equal((await job("repair-job")).code, 0);
    const noop = await job("noop-job");
    assert.equal(noop.code, 0);
    assert.equal(noop.report.contexts[0].noop, true);
    if (process.env.WIKI_TEST_ROOT) console.log("Acceptance fixture: " + f.dir);
  } finally {
    await f.close();
  }
});

test("recorded concept dependencies propagate a bounded failure beyond direct source ownership", async () => {
  const f = await fixture();
  try {
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle.\n",
    );
    assert.equal((await f.run("maintain")).ok, true);
    // Existing persisted knowledge may have page dependencies as well as source ownership.
    const file = path.join(f.config.output, ".state/state.json");
    const state = JSON.parse(await readFile(file, "utf8"));
    state.pages["concepts/kontrollseite"].pageVersions = {
      "concepts/freigabe": state.pages["concepts/freigabe"].hash,
    };
    await writeFile(file, JSON.stringify(state));
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    f.fail((b) => b.tools && JSON.stringify(b).includes("Alpha verlangt vier"));
    assert.equal((await f.run("maintain")).ok, false);
    assert.equal(
      (await f.run("search", "--question", "Kontrollseite")).results.length,
      0,
    );
    assert.equal(
      (await f.run("status")).pages.find(
        (p: any) => p.id === "concepts/kontrollseite",
      ).withdrawn,
      true,
    );
    f.fail(false);
    assert.equal((await f.run("maintain")).ok, true);
  } finally {
    await f.close();
  }
});

test("older publication provenance is rebuilt once before independent reuse is certified", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    const file = path.join(f.config.output, ".state/state.json");
    const state = JSON.parse(await readFile(file, "utf8"));
    state.publicationVersion = 1;
    await writeFile(file, JSON.stringify(state));
    const count = f.calls.length;
    const rebuilt = await f.run("maintain");
    assert.equal(rebuilt.ok, true);
    assert.ok(f.calls.length > count);
    assert.equal((await f.run("maintain")).noop, true);
  } finally {
    await f.close();
  }
});

test("a shared source index failure blocks dependent compilation and reports remaining work", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    (f.config.qmd as any).module = path.join(f.dir, "missing-qmd.mjs");
    await f.saveConfig();
    const failed = await f.run("maintain");
    assert.equal(failed.ok, false);
    assert.equal(failed.qmdSafe, false);
    assert.deepEqual(failed.completed, []);
    assert.equal(failed.sourceIndex.ok, false);
    assert.ok(failed.pending.length);
  } finally {
    await f.close();
  }
});

test("an unclassified compiler rejection alongside a bounded failure cannot lose pending sources", async () => {
  let oversized = false;
  const f = await fixture((body) => {
    const prompt = body.messages.map((m: any) => m.content).join("\n");
    if (oversized && !body.tools && prompt.includes('about "Kontrollseite"'))
      return {
        role: "assistant",
        content: "# Kontrollseite\n\n" + "Big page. ".repeat(150000),
      };
  });
  try {
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle ALT.\n",
    );
    assert.equal((await f.run("maintain")).ok, true);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    await writeFile(
      path.join(f.dir, "beta/control.md"),
      "# Kontrollseite\n\nKontrolle NEU.\n",
    );
    oversized = true;
    f.fail((b) => b.tools && JSON.stringify(b).includes("Alpha verlangt vier"));
    const failed = await f.run("maintain");
    assert.equal(failed.ok, false);
    assert.equal(failed.qmdSafe, false, JSON.stringify(failed));
    assert.match(failed.error, /floor:deny/);
    assert.ok(
      (await f.run("status")).changes.changed.includes("beta/control.md"),
    );
    oversized = false;
    f.fail(false);
    assert.equal((await f.run("maintain")).ok, true);
    assert.ok(
      (await f.run("search", "--question", "Kontrollseite")).results.length,
    );
    assert.equal((await f.run("maintain")).noop, true);
  } finally {
    await f.close();
  }
});
