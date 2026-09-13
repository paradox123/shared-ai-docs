import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";

test("migration inventory distinguishes empty outputs and preserves backup-only answers and unmanaged text", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    assert.equal(
      (await f.run("query", "--question", "Freigabe", "--save", "historisch"))
        .ok,
      true,
    );
    const backup = path.join(f.dir, "old-backup");
    assert.equal((await f.run("backup", "--destination", backup)).ok, true);
    await writeFile(
      path.join(backup, "wiki/notiz.md"),
      "Einzigartige unverwaltete Gesprächsnotiz.\n",
    );
    const inventory = await f.run(
      "migration-inventory",
      "--from",
      path.join(f.dir, "empty-production"),
      "--from",
      backup,
    );
    assert.equal(inventory.ok, true, JSON.stringify(inventory));
    assert.equal(inventory.inputs[0].status, "absent");
    assert.equal(inventory.inputs[1].kind, "backup");
    assert.deepEqual(inventory.inputs[1].unmanaged, ["wiki/notiz.md"]);
    const answer = inventory.inputs[1].pages.find(
      (p: any) => p.id === "answers/historisch",
    );
    assert.equal(answer.kind, "answer");
    assert.deepEqual(Object.keys(answer.pageVersions), ["concepts/freigabe"]);
    assert.equal(answer.eligible, true);
  } finally {
    await f.close();
  }
});

test("migration preserves unique answer text and remaps a concept-to-answer-to-answer chain for managed query", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    const concept = (await f.run("status")).pages.find(
      (p: any) => p.kind === "concept",
    );
    const draft = path.join(f.dir, "conversation.json");
    await writeFile(
      draft,
      JSON.stringify({
        slug: "entscheidung",
        question: "Freigabe",
        answer:
          "Einzigartige Gesprächsformulierung: zuerst Rücksprache halten.",
        evidence: [{ id: concept.id, hash: concept.hash }],
      }),
    );
    assert.equal((await f.run("save", "--draft", draft)).ok, true);
    assert.equal(
      (await f.run("query", "--question", "Freigabe", "--save", "folge")).ok,
      true,
    );
    const legacy = f.config.output;
    const original = await readFile(
      path.join(legacy, "wiki/answers/entscheidung.md"),
      "utf8",
    );
    const backup = path.join(f.dir, "historical");
    assert.equal((await f.run("backup", "--destination", backup)).ok, true);
    // Same revisions in a live output and backup must converge, regardless of scope label.
    const raw = JSON.parse(
      await readFile(path.join(legacy, ".state/state.json"), "utf8"),
    );
    raw.scope = "private";
    await writeFile(
      path.join(legacy, ".state/state.json"),
      JSON.stringify(raw),
    );
    f.config.output = path.join(f.dir, "common");
    f.config.context = "common";
    await f.saveConfig();
    const snapshot = path.join(f.dir, "snapshot");
    const migrated = await f.run(
      "migrate",
      "--from",
      legacy,
      "--from",
      backup,
      "--snapshot",
      snapshot,
    );
    assert.equal(migrated.ok, true, JSON.stringify(migrated));
    const mapping = migrated.report.pages.find(
      (p: any) => p.origin === legacy && p.id === "answers/entscheidung",
    );
    const imported = await readFile(
      path.join(f.config.output, "wiki", mapping.target + ".md"),
      "utf8",
    );
    assert.ok(
      imported.includes(
        "Einzigartige Gesprächsformulierung: zuerst Rücksprache halten.",
      ),
    );
    assert.equal(
      await readFile(
        path.join(snapshot, "inputs/0/wiki/answers/entscheidung.md"),
        "utf8",
      ),
      original,
    );
    const status = await f.run("status");
    assert.equal(
      status.pages.filter((p: any) => p.kind === "answer").length,
      2,
    );
    assert.deepEqual(status.review, []);
    const query = await f.run("query", "--question", "Freigabe");
    assert.equal(query.ok, true, JSON.stringify(query));
    assert.ok(query.evidence.some((p: any) => p.id === mapping.target));
    const following = status.pages.find(
      (p: any) =>
        p.question === "Freigabe" &&
        p.id !== mapping.target &&
        p.kind === "answer",
    );
    assert.ok(following.pageVersions[mapping.target]);
    assert.equal((await f.run("lint")).ok, true);
    const repeat = await f.run("migrate", "--snapshot", snapshot);
    assert.equal(repeat.ok, true, JSON.stringify(repeat));
    assert.equal(repeat.noop, true);
  } finally {
    await f.close();
  }
});

test("colliding concepts remain distinct and source correction refreshes an imported answer chain without changing an independent answer", async () => {
  const f = await fixture();
  try {
    const repos = [...f.config.repos],
      outputs: string[] = [];
    for (const repo of repos) {
      f.config.repos = [repo];
      f.config.context = repo.id;
      f.config.output = path.join(f.dir, repo.id + "-wiki");
      outputs.push(f.config.output);
      await f.saveConfig();
      assert.equal((await f.run("maintain")).ok, true);
      assert.equal(
        (
          await f.run(
            "query",
            "--question",
            "Freigabe",
            "--save",
            "entscheidung",
          )
        ).ok,
        true,
      );
      if (repo.id === "alpha")
        assert.equal(
          (await f.run("query", "--question", "Freigabe", "--save", "folge"))
            .ok,
          true,
        );
    }
    f.config.repos = repos;
    f.config.context = "common";
    f.config.output = path.join(f.dir, "common");
    await f.saveConfig();
    const snapshot = path.join(f.dir, "snapshot");
    const migrated = await f.run(
      "migrate",
      "--from",
      outputs[0],
      "--from",
      outputs[1],
      "--snapshot",
      snapshot,
    );
    assert.equal(migrated.ok, true, JSON.stringify(migrated));
    const mapping = (origin: string, id: string) =>
      migrated.report.pages.find((p: any) => p.origin === origin && p.id === id)
        .target;
    const a = mapping(outputs[0], "concepts/freigabe"),
      b = mapping(outputs[1], "concepts/freigabe");
    assert.notEqual(a, b);
    assert.doesNotMatch(
      await readFile(path.join(f.config.output, "wiki", a + ".md"), "utf8"),
      /Beta verlangt/,
    );
    assert.doesNotMatch(
      await readFile(path.join(f.config.output, "wiki", b + ".md"), "utf8"),
      /Alpha verlangt/,
    );
    const independent = mapping(outputs[1], "answers/entscheidung");
    const independentFile = path.join(
      f.config.output,
      "wiki",
      independent + ".md",
    );
    const before = await readFile(independentFile, "utf8");
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    const staleQuery = await f.run("query", "--question", "Freigabe");
    assert.ok(staleQuery.review.some((p: any) => p.id === a));
    assert.ok(!staleQuery.evidence.some((p: any) => p.id === a));
    const maintained = await f.run("maintain");
    assert.equal(maintained.ok, true, JSON.stringify(maintained));
    const status = await f.run("status");
    for (const old of [
      "concepts/freigabe",
      "answers/entscheidung",
      "answers/folge",
    ]) {
      const id = mapping(outputs[0], old);
      assert.ok(
        status.pages.some((p: any) => p.id === id),
        "Imported page survives maintenance: " + old,
      );
      const text = await readFile(
        path.join(f.config.output, "wiki", id + ".md"),
        "utf8",
      );
      assert.match(text, /Alpha verlangt vier Freigaben/);
      assert.doesNotMatch(text, /Alpha verlangt zwei Freigaben/);
    }
    assert.equal(await readFile(independentFile, "utf8"), before);
    assert.deepEqual(status.review, []);
    assert.equal((await f.run("maintain")).noop, true);
    assert.equal((await f.run("migrate", "--snapshot", snapshot)).noop, true);
  } finally {
    await f.close();
  }
});

test("invalid historical evidence and its dependents stay quarantined with intact snapshot bytes", async () => {
  const f = await fixture();
  try {
    await f.run("maintain");
    await f.run("query", "--question", "Freigabe", "--save", "alt");
    const backup = path.join(f.dir, "legacy");
    await f.run("backup", "--destination", backup);
    const raw = JSON.parse(
      await readFile(path.join(backup, "backup.json"), "utf8"),
    );
    // External historic states can contain incomplete metadata; admission must validate them.
    delete raw.state.pages["answers/alt"].sourceVersions["beta/README.md"];
    await writeFile(path.join(backup, "backup.json"), JSON.stringify(raw));
    const invalidBytes = await readFile(
      path.join(backup, "wiki/answers/alt.md"),
      "utf8",
    );
    const live = f.config.output;
    await writeFile(
      path.join(live, "wiki/concepts/freigabe.md"),
      "Manipulierte Altbehauptung.\n",
    );
    f.config.output = path.join(f.dir, "common");
    f.config.context = "common";
    await f.saveConfig();
    const result = await f.run(
      "migrate",
      "--from",
      backup,
      "--from",
      live,
      "--snapshot",
      path.join(f.dir, "snapshot"),
    );
    assert.equal(result.ok, true, JSON.stringify(result));
    const report = result.report.pages;
    assert.ok(
      report
        .find((p: any) => p.origin === backup && p.id === "answers/alt")
        .reasons.some((r: string) =>
          r.startsWith("incomplete-transitive-provenance"),
        ),
    );
    assert.equal(
      report.find((p: any) => p.origin === live && p.id === "concepts/freigabe")
        .action,
      "quarantined",
    );
    assert.equal(
      report.find((p: any) => p.origin === live && p.id === "answers/alt")
        .action,
      "quarantined",
    );
    assert.equal(
      (await f.run("status")).pages.filter((p: any) => p.kind === "answer")
        .length,
      0,
    );
    assert.equal(
      await readFile(
        path.join(f.dir, "snapshot/inputs/0/wiki/answers/alt.md"),
        "utf8",
      ),
      invalidBytes,
    );
    assert.equal(
      (await f.run("search", "--question", "Manipulierte Altbehauptung"))
        .rawMatches,
      0,
    );
  } finally {
    await f.close();
  }
});

test("index failure resumes the verified snapshot and rechecks sources before declaring completion", async () => {
  const f = await fixture();
  try {
    await f.run("maintain");
    await f.run("query", "--question", "Freigabe", "--save", "alt");
    const backup = path.join(f.dir, "legacy");
    await f.run("backup", "--destination", backup);
    f.config.output = path.join(f.dir, "common");
    f.config.context = "common";
    await f.saveConfig();
    assert.equal((await f.run("maintain")).ok, true);
    (f.config.qmd as any).node = "/missing-qmd-runtime";
    await f.saveConfig();
    const snapshot = path.join(f.dir, "snapshot");
    const failed = await f.run(
      "migrate",
      "--from",
      backup,
      "--snapshot",
      snapshot,
    );
    assert.equal(failed.ok, false);
    assert.match((await f.run("maintain")).error, /Resume pending migration/);
    assert.equal(
      (await f.run("status")).pages.filter((p: any) => p.kind === "answer")
        .length,
      1,
    );
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    delete (f.config.qmd as any).node;
    await f.saveConfig();
    const resumed = await f.run("migrate", "--snapshot", snapshot);
    assert.equal(resumed.ok, true, JSON.stringify(resumed));
    const current = await f.run("status");
    assert.deepEqual(current.review, []);
    assert.deepEqual(current.pending, []);
    assert.equal(
      current.pages.filter((p: any) => p.kind === "answer").length,
      1,
    );
    const imported = current.pages.find((p: any) => p.kind === "answer");
    assert.match(
      await readFile(
        path.join(f.config.output, "wiki", imported.id + ".md"),
        "utf8",
      ),
      /Alpha verlangt vier Freigaben/,
    );
    assert.equal((await f.run("migrate", "--snapshot", snapshot)).noop, true);
    await writeFile(
      path.join(snapshot, "inputs/0/wiki/answers/alt.md"),
      "Beschädigte Sicherung",
    );
    const tampered = await f.run("migrate", "--snapshot", snapshot);
    assert.equal(tampered.ok, false);
    assert.match(tampered.error, /checksum/);
    assert.equal(
      (await f.run("status")).pages.filter((p: any) => p.kind === "answer")
        .length,
      1,
    );
  } finally {
    await f.close();
  }
});

test("migration remaps mutual navigation links to the preserved revisions rather than newly compiled names", async () => {
  const f = await fixture();
  try {
    await writeFile(
      path.join(f.dir, "beta/README.md"),
      "# Kontrollseite\n\nUnabhängige Kontrollseite.\n",
    );
    await f.run("maintain");
    const legacy = f.config.output;
    const file = path.join(legacy, ".state/state.json");
    const state = JSON.parse(await readFile(file, "utf8"));
    const ids = ["concepts/freigabe", "concepts/kontrollseite"];
    const { createHash } = await import("node:crypto");
    for (const [i, id] of ids.entries()) {
      const pageFile = path.join(legacy, "wiki", id + ".md");
      const text =
        (await readFile(pageFile, "utf8")) +
        `\n[Weitere Seite](../${ids[1 - i]}.md)\n`;
      await writeFile(pageFile, text);
      state.pages[id].hash = createHash("sha256").update(text).digest("hex");
    }
    await writeFile(file, JSON.stringify(state));
    f.config.output = path.join(f.dir, "common");
    f.config.context = "common";
    await f.saveConfig();
    const result = await f.run(
      "migrate",
      "--from",
      legacy,
      "--snapshot",
      path.join(f.dir, "snapshot"),
    );
    assert.equal(result.ok, true, JSON.stringify(result));
    for (const [i, id] of ids.entries()) {
      const target = result.report.pages.find((p: any) => p.id === id).target;
      const other = result.report.pages.find(
        (p: any) => p.id === ids[1 - i],
      ).target;
      assert.ok(
        (
          await readFile(
            path.join(f.config.output, "wiki", target + ".md"),
            "utf8",
          )
        ).includes(path.basename(other) + ".md"),
      );
    }
    assert.equal((await f.run("lint")).ok, true);
  } finally {
    await f.close();
  }
});

test("migration refuses a legacy output owned by a live writer before creating its snapshot", async () => {
  const f = await fixture();
  try {
    await f.run("maintain");
    const legacy = f.config.output;
    await writeFile(
      path.join(legacy, ".state/writer.lock"),
      JSON.stringify({ pid: process.pid, started: new Date().toISOString() }),
    );
    f.config.output = path.join(f.dir, "common");
    f.config.context = "common";
    await f.saveConfig();
    const result = await f.run(
      "migrate",
      "--from",
      legacy,
      "--snapshot",
      path.join(f.dir, "snapshot"),
    );
    assert.equal(result.ok, false);
    assert.match(result.error, /locked/i);
    await assert.rejects(readFile(path.join(f.dir, "snapshot/manifest.json")));
    assert.deepEqual((await f.run("status")).pages, []);
  } finally {
    await f.close();
  }
});

test("retry removes unpublished imports after a source changes during publication", async () => {
  const f = await fixture();
  let watcher: any;
  try {
    await f.run("maintain");
    const concept = (await f.run("status")).pages.find(
      (p: any) => p.kind === "concept",
    );
    const draft = path.join(f.dir, "unique.json");
    await writeFile(
      draft,
      JSON.stringify({
        slug: "unikat",
        question: "Freigabe",
        answer: "ErhaltenswertesUnikat",
        evidence: [{ id: concept.id, hash: concept.hash }],
      }),
    );
    await f.run("save", "--draft", draft);
    const backup = path.join(f.dir, "old");
    await f.run("backup", "--destination", backup);
    f.config.output = path.join(f.dir, "common");
    f.config.context = "common";
    await f.saveConfig();
    await f.run("maintain");
    const { watch, writeFileSync } = await import("node:fs");
    let changed = false;
    watcher = watch(
      path.join(f.config.output, "wiki"),
      { recursive: true },
      (_event, file) => {
        if (!changed && file?.includes("import-") && file.endsWith(".md")) {
          changed = true;
          writeFileSync(
            path.join(f.dir, "alpha/README.md"),
            "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
          );
        }
      },
    );
    const snapshot = path.join(f.dir, "snapshot");
    const failed = await f.run(
      "migrate",
      "--from",
      backup,
      "--snapshot",
      snapshot,
    );
    watcher.close();
    assert.equal(
      changed,
      true,
      "Source changed at the public output publication boundary",
    );
    assert.equal(failed.ok, false);
    assert.match(failed.error, /Sources changed/);
    const resumed = await f.run("migrate", "--snapshot", snapshot);
    assert.equal(resumed.ok, true, JSON.stringify(resumed));
    assert.equal(
      (await f.run("search", "--question", "ErhaltenswertesUnikat")).rawMatches,
      0,
    );
    const { readdir } = await import("node:fs/promises");
    assert.ok(
      !(await readdir(path.join(f.config.output, "wiki/answers"))).some((f) =>
        f.startsWith("import-"),
      ),
    );
    assert.equal(
      await readFile(
        path.join(snapshot, "inputs/0/wiki/answers/unikat.md"),
        "utf8",
      ).then((t) => t.includes("ErhaltenswertesUnikat")),
      true,
    );
  } finally {
    watcher?.close();
    await f.close();
  }
});
