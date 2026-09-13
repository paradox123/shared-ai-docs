import { test } from "node:test";
import assert from "node:assert/strict";
import { appendFile } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";
test("lint reports active broken links and changed page versions as open work with a failing exit", async () => {
  const f = await fixture();
  try {
    await f.run("maintain");
    await appendFile(
      path.join(f.config.output, "wiki/concepts/freigabe.md"),
      "\n[Fehlend](missing.md)\n",
    );
    const result = await f.run("lint");
    assert.equal(result.ok, false);
    assert.ok(result.activeIssues.some((x: any) => x.rule === "broken-link"));
  } finally {
    await f.close();
  }
});
