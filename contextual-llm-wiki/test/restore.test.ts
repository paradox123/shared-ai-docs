import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, access, rm } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";
test("backup restores unique saved answers with provenance and filters a smaller current context before publishing", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    assert.equal(
      (await f.run("query", "--question", "Freigabe", "--save", "erhalten")).ok,
      true,
    );
    const original = await readFile(
      path.join(f.config.output, "wiki/answers/erhalten.md"),
      "utf8",
    );
    const dest = path.join(f.dir, "backup");
    const backed = await f.run("backup", "--destination", dest);
    assert.equal(backed.ok, true, JSON.stringify(backed));
    await rm(path.join(f.config.output, "wiki"), { recursive: true });
    const restored = await f.run("restore", "--backup", dest);
    assert.equal(restored.ok, true, JSON.stringify(restored));
    assert.equal(
      await readFile(
        path.join(f.config.output, "wiki/answers/erhalten.md"),
        "utf8",
      ),
      original,
    );
    f.config.repos.pop();
    await f.saveConfig();
    const smaller = await f.run("restore", "--backup", dest);
    assert.equal(smaller.ok, true, JSON.stringify(smaller));
    await assert.rejects(
      access(path.join(f.config.output, "wiki/answers/erhalten.md")),
    );
    assert.doesNotMatch(
      await readFile(
        path.join(f.config.output, "wiki/concepts/freigabe.md"),
        "utf8",
      ),
      /Beta/,
    );
    assert.equal((await f.run("search", "--question", "Beta")).rawMatches, 0);
  } finally {
    await f.close();
  }
});
