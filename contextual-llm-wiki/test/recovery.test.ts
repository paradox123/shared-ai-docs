import { test } from "node:test";
import assert from "node:assert/strict";
import { writeFile, readFile, access } from "node:fs/promises";
import path from "node:path";
import { fixture, invoke } from "./support.ts";
async function until(check: () => boolean) {
  const deadline = Date.now() + 5000;
  while (!check()) {
    if (Date.now() > deadline) throw Error("provider request not observed");
    await new Promise((r) => setTimeout(r, 10));
  }
}

test("concurrent writers are serialized and a mid-generation source change stays pending", async () => {
  const f = await fixture();
  let releaseProvider = () => {};
  try {
    assert.equal((await f.run("maintain")).ok, true);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    releaseProvider = f.hold();
    const count = f.calls.length;
    const first = f.run("maintain");
    await until(() => f.calls.length > count);
    const concurrent = await f.run("maintain");
    assert.equal(concurrent.ok, false);
    assert.match(concurrent.error, /locked|writer/i);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt drei Freigaben.\n",
    );
    releaseProvider();
    const stale = await first;
    assert.equal(stale.ok, false);
    assert.match(stale.error, /changed during/);
    const resumed = await f.run("maintain");
    assert.equal(resumed.ok, true, JSON.stringify(resumed));
    assert.match(
      await readFile(
        path.join(f.config.output, "wiki/concepts/freigabe.md"),
        "utf8",
      ),
      /Alpha verlangt drei/,
    );
  } finally {
    releaseProvider();
    await f.close();
  }
});

test("provider failure preserves pending corrections and source index failure defers compilation", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    f.fail(true);
    const failed = await f.run("maintain");
    assert.equal(failed.ok, false);
    assert.match(failed.error, /provider failure/);
    assert.ok((await f.run("status")).pending.length);
    await assert.rejects(
      access(path.join(f.config.output, "wiki/concepts/freigabe.md")),
    );
    f.fail(false);
    assert.equal((await f.run("maintain")).ok, true);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt drei Freigaben.\n",
    );
    (f.config.qmd as any).module = path.join(f.dir, "missing-qmd-module.mjs");
    await f.saveConfig();
    const count = f.calls.length;
    const indexFailure = await f.run("maintain");
    assert.equal(indexFailure.ok, false);
    assert.match(indexFailure.error, /QMD|qmd|module/i);
    assert.equal(f.calls.length, count);
    delete (f.config.qmd as any).module;
    await f.saveConfig();
    const resumed = await f.run("maintain");
    assert.equal(resumed.ok, true, JSON.stringify(resumed));
    assert.ok(f.calls.length > count);
  } finally {
    await f.close();
  }
});

test("an incomplete scan never becomes mass source withdrawal", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    const body = await readFile(
      path.join(f.config.output, "wiki/concepts/freigabe.md"),
      "utf8",
    );
    const { rename } = await import("node:fs/promises");
    await rename(path.join(f.dir, "alpha"), path.join(f.dir, "alpha-moved"));
    await writeFile(path.join(f.dir, "alpha"), "not a directory");
    const failed = await f.run("maintain");
    assert.equal(failed.ok, false);
    assert.match(failed.error, /Incomplete scan/);
    assert.equal(
      await readFile(
        path.join(f.config.output, "wiki/concepts/freigabe.md"),
        "utf8",
      ),
      body,
    );
  } finally {
    await f.close();
  }
});

test("a context selection change during generation prevents publication under the old context", async () => {
  const f = await fixture();
  try {
    f.delay(500);
    const started = f.run("maintain");
    await until(() => f.calls.length > 0);
    f.config.repos.pop();
    await f.saveConfig();
    const stale = await started;
    assert.equal(stale.ok, false);
    assert.match(stale.error, /Context.*changed/i);
    await assert.rejects(
      access(path.join(f.config.output, "wiki/concepts/freigabe.md")),
    );
    f.delay(0);
    assert.equal((await f.run("maintain")).ok, true);
  } finally {
    await f.close();
  }
});

test("an index failure after save is visible and later maintenance indexes the saved answer without new model calls", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    // Use an external draft so the failure occurs specifically on Save's index operation.
    const page = (await f.run("status")).pages[0];
    const draft = path.join(f.dir, "draft.json");
    await writeFile(
      draft,
      JSON.stringify({
        slug: "index-pending",
        question: "Freigabe",
        answer: "Eine persistierte Antwort.",
        evidence: [{ id: page.id, hash: page.hash }],
      }),
    );
    (f.config.qmd as any).module = path.join(f.dir, "missing-qmd.mjs");
    await f.saveConfig();
    const saved = await f.run("save", "--draft", draft);
    assert.equal(saved.ok, false);
    assert.ok((await f.run("status")).pending.length);
    const count = f.calls.length;
    delete (f.config.qmd as any).module;
    await f.saveConfig();
    assert.equal((await f.run("maintain")).ok, true);
    assert.equal(f.calls.length, count);
    assert.ok(
      (await f.run("search", "--question", "persistierte")).results.length,
    );
  } finally {
    await f.close();
  }
});

test("an abruptly killed writer is recovered and cannot expose its stale page through query", async () => {
  const f = await fixture();
  try {
    await f.run("maintain");
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    f.delay(600);
    let pid = 0;
    const count = f.calls.length;
    const failed = invoke(
      ["maintain", "--config", f.configPath],
      f.env,
      (p) => (pid = p),
    ).catch(() => ({ ok: false }));
    await until(() => f.calls.length > count);
    process.kill(pid, "SIGKILL");
    await failed;
    f.delay(0);
    const query = await f.run("query", "--question", "Freigabe");
    assert.equal(query.ok, true);
    assert.equal(query.fallback, true);
    assert.doesNotMatch(query.answer, /Alpha verlangt zwei/);
    const resumed = await f.run("maintain");
    assert.equal(resumed.ok, true, JSON.stringify(resumed));
    assert.equal((await f.run("status")).pending.length, 0);
  } finally {
    await f.close();
  }
});

test("invalid scope configuration is rejected before it can withdraw valid knowledge", async () => {
  const f = await fixture();
  try {
    await f.run("maintain");
    const before = await readFile(
      path.join(f.config.output, "wiki/concepts/freigabe.md"),
      "utf8",
    );
    f.config.repos[0].scope = "genral";
    await f.saveConfig();
    const r = await f.run("maintain");
    assert.equal(r.ok, false);
    assert.match(r.error, /scope/i);
    assert.equal(
      await readFile(
        path.join(f.config.output, "wiki/concepts/freigabe.md"),
        "utf8",
      ),
      before,
    );
  } finally {
    await f.close();
  }
});
