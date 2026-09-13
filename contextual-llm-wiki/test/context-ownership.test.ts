import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";
test("a common context cannot silently reuse a legacy scope output directory", async () => {
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
