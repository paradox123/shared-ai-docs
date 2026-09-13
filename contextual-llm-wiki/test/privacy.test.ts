import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";
test("explicit private contexts remain separate in files, search and saved answers", async () => {
  const f = await fixture();
  try {
    f.config.repos[1].scope = "private";
    await writeFile(
      path.join(f.dir, "beta/README.md"),
      "# Privatmarker\n\nBeta verlangt vier Freigaben. Privatmarker.\n",
    );
    await f.saveConfig();
    assert.equal((await f.run("maintain")).ok, true);
    const general = f.config.output;
    assert.doesNotMatch(
      await readFile(path.join(general, "wiki/concepts/freigabe.md"), "utf8"),
      /Beta|Privatmarker/,
    );
    (f.config as any).scope = "private";
    f.config.context = "private";
    f.config.output = path.join(f.dir, "private-output");
    await f.saveConfig();
    const compiled = await f.run("maintain");
    assert.equal(compiled.ok, true, JSON.stringify(compiled));
    assert.match(
      await readFile(
        path.join(f.config.output, "wiki/concepts/freigabe.md"),
        "utf8",
      ),
      /Beta/,
    );
    assert.equal(
      (await f.run("query", "--question", "Freigabe", "--save", "privat")).ok,
      true,
    );
    (f.config as any).scope = "general";
    f.config.context = "test";
    f.config.output = general;
    await f.saveConfig();
    assert.equal((await f.run("search", "--question", "Beta")).rawMatches, 0);
    assert.ok(
      !(await f.run("status")).pages.some(
        (p: any) => p.id === "answers/privat",
      ),
    );
  } finally {
    await f.close();
  }
});

test("a context cannot reuse another scope output directory", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    (f.config as any).scope = "private";
    f.config.context = "private";
    await f.saveConfig();
    const conflict = await f.run("maintain");
    assert.equal(conflict.ok, false);
    assert.match(conflict.error, /scope|context/i);
  } finally {
    await f.close();
  }
});
