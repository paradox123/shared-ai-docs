import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, writeFile, mkdir, symlink, readdir } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";

test("saved answer replacement invalidates dependent answers before another query", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    await f.run("query", "--question", "Freigabe", "--save", "a");
    await f.run("query", "--question", "Freigabe", "--save", "b");
    const state = await f.run("status");
    const concept = state.pages.find((p: any) => p.kind === "concept");
    const draft = path.join(f.dir, "draft.json");
    await writeFile(
      draft,
      JSON.stringify({
        slug: "a",
        question: "Freigabe",
        answer: "Neue Formulierung: Alpha verlangt zwei Freigaben, Beta drei.",
        evidence: [{ id: concept.id, hash: concept.hash }],
      }),
    );
    assert.equal((await f.run("save", "--draft", draft)).ok, true);
    assert.ok(
      (await f.run("status")).review.some((p: any) => p.id === "answers/b"),
    );
    const query = await f.run("query", "--question", "Freigabe");
    assert.ok(!query.evidence.some((p: any) => p.id === "answers/b"));
    assert.equal((await f.run("maintain")).ok, true);
    assert.deepEqual((await f.run("status")).review, []);
  } finally {
    await f.close();
  }
});

test("save rejects indirect answer cycles without replacing the valid answer", async () => {
  const f = await fixture();
  try {
    await f.run("maintain");
    await f.run("query", "--question", "Freigabe", "--save", "a");
    await f.run("query", "--question", "Freigabe", "--save", "b");
    const before = await readFile(
      path.join(f.config.output, "wiki/answers/a.md"),
      "utf8",
    );
    const b = (await f.run("status")).pages.find(
      (p: any) => p.id === "answers/b",
    );
    const draft = path.join(f.dir, "cycle.json");
    await writeFile(
      draft,
      JSON.stringify({
        slug: "a",
        question: "Freigabe",
        answer: "Zirkel",
        evidence: [{ id: b.id, hash: b.hash }],
      }),
    );
    const result = await f.run("save", "--draft", draft);
    assert.equal(result.ok, false);
    assert.match(result.error, /cycle|itself/i);
    assert.equal(
      await readFile(path.join(f.config.output, "wiki/answers/a.md"), "utf8"),
      before,
    );
  } finally {
    await f.close();
  }
});

test("restore checks provider availability before changing active content", async () => {
  const f = await fixture();
  try {
    await f.run("maintain");
    const dest = path.join(f.dir, "backup");
    await f.run("backup", "--destination", dest);
    const active = path.join(f.config.output, "wiki/concepts/freigabe.md");
    await writeFile(active, "Manuelle Änderung vor Wiederherstellung\n");
    f.env.OPENAI_API_KEY = "";
    const result = await f.run("restore", "--backup", dest);
    assert.equal(result.ok, false);
    assert.match(result.error, /provider/i);
    assert.equal(
      await readFile(active, "utf8"),
      "Manuelle Änderung vor Wiederherstellung\n",
    );
  } finally {
    await f.close();
  }
});

test("managed directories cannot redirect writes through nested symlinks into sources", async () => {
  const f = await fixture();
  try {
    await mkdir(f.config.output, { recursive: true });
    await symlink(
      path.join(f.dir, "alpha"),
      path.join(f.config.output, ".state"),
    );
    const before = await readdir(path.join(f.dir, "alpha"));
    const result = await f.run("maintain");
    assert.equal(result.ok, false);
    assert.match(result.error, /symlink/i);
    assert.deepEqual(await readdir(path.join(f.dir, "alpha")), before);
  } finally {
    await f.close();
  }
});
