import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";
import { PIN } from "../src/runtime.ts";

test("release candidate supports managed query, provenance, freshness, saved answers and no-op maintenance", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("setup")).ok, true);
    const maintained = await f.run("maintain");
    assert.equal(maintained.ok, true, JSON.stringify(maintained));
    assert.equal(maintained.compiler, PIN);
    const current = await f.run(
      "query",
      "--question",
      "Freigabe",
      "--save",
      "release-answer",
    );
    assert.equal(current.ok, true, JSON.stringify(current));
    assert.equal(current.fallback, false);
    assert.match(current.answer, /Alpha verlangt zwei Freigaben/);
    assert.match(current.answer, /Beta verlangt drei Freigaben/);
    assert.deepEqual(current.originals.map((s: any) => s.id).sort(), [
      "alpha/README.md",
      "beta/README.md",
    ]);
    for (const original of current.originals) {
      assert.equal(original.freshness, "checked-current");
      assert.ok((await readFile(original.path, "utf8")).includes("Freigabe"));
      assert.equal(
        original.uri,
        "obsidian://open?path=" + encodeURIComponent(original.path),
      );
    }
    const source = await f.run("source", "--id", "alpha/README.md");
    assert.equal(source.ok, true, JSON.stringify(source));
    const calls = f.calls.length;
    assert.equal((await f.run("maintain")).noop, true);
    assert.equal(f.calls.length, calls);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    const changed = await f.run(
      "query",
      "--question",
      "Freigabe",
      "--repo",
      "alpha",
    );
    assert.equal(changed.ok, true, JSON.stringify(changed));
    assert.equal(changed.fallback, true);
    assert.ok(changed.review.length > 0);
    assert.match(changed.answer, /Alpha verlangt vier Freigaben/);
    assert.doesNotMatch(changed.answer, /Alpha verlangt zwei Freigaben/);
    assert.notEqual(
      changed.originals[0].hash,
      current.originals.find((s: any) => s.id === "alpha/README.md").hash,
    );
    assert.equal((await f.run("maintain")).ok, true);
    const refreshed = await f.run("query", "--question", "Freigabe");
    assert.equal(refreshed.ok, true, JSON.stringify(refreshed));
    assert.equal(refreshed.fallback, false);
    assert.match(refreshed.answer, /Alpha verlangt vier Freigaben/);
    assert.equal((await f.run("lint")).ok, true);
  } finally {
    await f.close();
  }
});
