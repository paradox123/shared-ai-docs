import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, access } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";
test("two original repositories compile into a shared, cited Markdown page without wiki git or embeddings", async () => {
  const f = await fixture();
  try {
    const result = await f.run("maintain");
    assert.equal(result.ok, true, JSON.stringify(result));
    const page = await readFile(
      path.join(f.config.output, "wiki/concepts/freigabe.md"),
      "utf8",
    );
    assert.match(page, /Alpha verlangt zwei/);
    assert.match(page, /Beta verlangt drei/);
    assert.match(page, /alpha\/README.md/);
    assert.match(page, /beta\/README.md/);
    assert.equal(
      await readFile(path.join(f.dir, "alpha/README.md"), "utf8"),
      "# Freigabe\n\nAlpha verlangt zwei Freigaben.\n",
    );
    await assert.rejects(access(path.join(f.config.output, ".git")));
    assert.ok(!f.calls.some((c) => c.input));
  } finally {
    await f.close();
  }
});

test("recursive inventory reads dirty Markdown, preserves hidden docs, and includes personal sources and excludes runtime, nested repos and symlinks", async () => {
  const f = await fixture();
  try {
    const { mkdir, writeFile, symlink } = await import("node:fs/promises");
    for (const dir of [
      "docs/deep",
      ".codex",
      "node_modules",
      "runtime/logs",
      "nested/.git",
    ])
      await mkdir(path.join(f.dir, "alpha", dir), { recursive: true });
    for (const file of [
      "docs/deep/new.MD",
      ".codex/AGENTS.md",
      "node_modules/leak.md",
      "runtime/logs/leak.md",
      "nested/leak.md",
    ])
      await writeFile(path.join(f.dir, "alpha", file), "# Quelle\n");
    await symlink(path.join(f.dir, "beta"), path.join(f.dir, "alpha/alias"));
    f.config.repos[1].scope = "private";
    await f.saveConfig();
    const r = await f.run("inventory");
    assert.equal(r.ok, true, JSON.stringify(r));
    assert.equal(r.selectedSources, 4);
    assert.equal(r.repositories[1].count, 1);
    assert.ok(
      r.repositories[0].excluded.some(
        (e: any) => e.reason === "nested-repository",
      ),
    );
    assert.ok(
      r.repositories[0].excluded.some((e: any) => e.reason === "symlink"),
    );
  } finally {
    await f.close();
  }
});

test("correction revalidates the affected concept, preserves an independent page, and unchanged maintenance does no model work", async () => {
  const f = await fixture();
  try {
    const { writeFile } = await import("node:fs/promises");
    await writeFile(
      path.join(f.dir, "alpha/control.md"),
      "# Kontrollseite\n\nUnabhängige Kontrollseite.\n",
    );
    assert.equal((await f.run("maintain")).ok, true);
    const control = await readFile(
      path.join(f.config.output, "wiki/concepts/kontrollseite.md"),
      "utf8",
    );
    const count = f.calls.length;
    const noop = await f.run("maintain");
    assert.equal(noop.ok, true);
    assert.equal(f.calls.length, count);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    const pending = await f.run("status");
    assert.ok(pending.review.some((p: any) => p.id === "concepts/freigabe"));
    assert.equal((await f.run("maintain")).ok, true);
    const changed = await readFile(
      path.join(f.config.output, "wiki/concepts/freigabe.md"),
      "utf8",
    );
    assert.match(changed, /Alpha verlangt vier/);
    assert.doesNotMatch(changed, /Alpha verlangt zwei/);
    assert.equal(
      await readFile(
        path.join(f.config.output, "wiki/concepts/kontrollseite.md"),
        "utf8",
      ),
      control,
    );
  } finally {
    await f.close();
  }
});

test("setup probes the actual configured completion provider through the public compiler hook", async () => {
  const f = await fixture();
  try {
    const r = await f.run("setup");
    assert.equal(r.ok, true, JSON.stringify(r));
    assert.equal(r.providerProbe, "ok");
    assert.ok(f.calls.length > 0);
  } finally {
    await f.close();
  }
});

test("QMD indexes only active wiki pages and supplies current evidence to a saved follow-up answer", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    const result = await f.run(
      "query",
      "--question",
      "Freigabe",
      "--save",
      "erste-antwort",
    );
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.equal(result.engine, "qmd");
    assert.ok(result.evidence.some((p: any) => p.id === "concepts/freigabe"));
    assert.equal(result.saved, "answers/erste-antwort");
    assert.match(
      await readFile(
        path.join(f.config.output, "wiki/answers/erste-antwort.md"),
        "utf8",
      ),
      /Alpha verlangt zwei/,
    );
    const state = await f.run("status");
    const saved = state.pages.find((p: any) => p.id === result.saved);
    assert.ok(saved.pageVersions["concepts/freigabe"]);
    assert.equal(Object.keys(saved.sourceVersions).length, 2);
  } finally {
    await f.close();
  }
});

test("original changes are detected before sync and propagate through two saved answers", async () => {
  const f = await fixture();
  try {
    const { writeFile } = await import("node:fs/promises");
    assert.equal((await f.run("maintain")).ok, true);
    assert.equal(
      (await f.run("query", "--question", "Freigabe", "--save", "antwort-a"))
        .ok,
      true,
    );
    const second = await f.run(
      "query",
      "--question",
      "Freigabe",
      "--save",
      "antwort-b",
    );
    assert.equal(second.ok, true, JSON.stringify(second));
    const before = await f.run("status");
    assert.ok(
      before.pages.find((p: any) => p.id === "answers/antwort-b").pageVersions[
        "answers/antwort-a"
      ],
    );
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Freigabe\n\nAlpha verlangt vier Freigaben.\n",
    );
    const unsynced = await f.run("query", "--question", "Freigabe");
    assert.equal(unsynced.ok, true);
    assert.equal(unsynced.fallback, true);
    assert.ok(unsynced.review.some((p: any) => p.id === "answers/antwort-b"));
    assert.doesNotMatch(unsynced.answer, /Alpha verlangt zwei/);
    const maintained = await f.run("maintain");
    assert.equal(maintained.ok, true, JSON.stringify(maintained));
    for (const name of ["antwort-a", "antwort-b"]) {
      const body = await readFile(
        path.join(f.config.output, "wiki/answers", name + ".md"),
        "utf8",
      );
      assert.match(body, /Alpha verlangt vier/);
      assert.doesNotMatch(body, /Alpha verlangt zwei/);
    }
  } finally {
    await f.close();
  }
});

test("repo withdrawal deletes dependent knowledge from active files, navigation and real QMD; readdition compiles current input", async () => {
  const f = await fixture();
  try {
    const { writeFile } = await import("node:fs/promises");
    await writeFile(
      path.join(f.dir, "alpha/control.md"),
      "# Kontrollseite\n\nUnabhängige Kontrollseite.\n",
    );
    assert.equal((await f.run("maintain")).ok, true);
    const control = await readFile(
      path.join(f.config.output, "wiki/concepts/kontrollseite.md"),
      "utf8",
    );
    assert.equal(
      (
        await f.run(
          "query",
          "--question",
          "Freigabe",
          "--save",
          "entzogene-antwort",
        )
      ).ok,
      true,
    );
    const beta = f.config.repos.pop();
    await f.saveConfig();
    const removed = await f.run("maintain");
    assert.equal(removed.ok, true, JSON.stringify(removed));
    await assert.rejects(
      access(path.join(f.config.output, "wiki/answers/entzogene-antwort.md")),
    );
    const mixed = await readFile(
      path.join(f.config.output, "wiki/concepts/freigabe.md"),
      "utf8",
    );
    assert.match(mixed, /Alpha/);
    assert.doesNotMatch(mixed, /Beta/);
    assert.doesNotMatch(
      await readFile(path.join(f.config.output, "wiki/index.md"), "utf8"),
      /entzogene-antwort/,
    );
    assert.equal(
      await readFile(
        path.join(f.config.output, "wiki/concepts/kontrollseite.md"),
        "utf8",
      ),
      control,
    );
    const search = await f.run("search", "--question", "Beta");
    assert.equal(search.ok, true, JSON.stringify(search));
    assert.equal(search.results.length, 0);
    assert.equal(search.rawMatches, 0);
    f.config.repos.push(beta!);
    await writeFile(
      path.join(f.dir, "beta/README.md"),
      "# Freigabe\n\nBeta verlangt vier Freigaben.\n",
    );
    await f.saveConfig();
    assert.equal((await f.run("maintain")).ok, true);
    assert.match(
      await readFile(
        path.join(f.config.output, "wiki/concepts/freigabe.md"),
        "utf8",
      ),
      /Beta verlangt vier/,
    );
    await assert.rejects(
      access(path.join(f.config.output, "wiki/answers/entzogene-antwort.md")),
    );
  } finally {
    await f.close();
  }
});

test("large Markdown remains lossless through the supported compiler source path and original line mapping", async () => {
  const f = await fixture();
  try {
    const { writeFile } = await import("node:fs/promises");
    const text =
      "# Freigabe\n\nAlpha verlangt zwei Freigaben.\n" +
      "Fachlicher Absatz.\n".repeat(7000) +
      "ENDMARKER-LOSSLESS\n";
    await writeFile(path.join(f.dir, "alpha/README.md"), text);
    assert.equal((await f.run("maintain")).ok, true);
    const source = await f.run("source", "--id", "alpha/README.md");
    assert.equal(source.ok, true, JSON.stringify(source));
    assert.equal(source.text, text);
    assert.equal(source.lineOffset, 0);
    assert.equal(source.original, path.join(f.dir, "alpha/README.md"));
  } finally {
    await f.close();
  }
});

test("save refuses unknown or changed evidence instead of publishing unsupported knowledge", async () => {
  const f = await fixture();
  try {
    const { writeFile } = await import("node:fs/promises");
    assert.equal((await f.run("maintain")).ok, true);
    const draft = path.join(f.dir, "draft.json");
    await writeFile(
      draft,
      JSON.stringify({
        slug: "unbelegt",
        question: "Freigabe",
        answer: "Behauptung ohne Beleg",
        evidence: [],
      }),
    );
    const missing = await f.run("save", "--draft", draft);
    assert.equal(missing.ok, false);
    assert.match(missing.error, /provenance|evidence/i);
    await assert.rejects(
      access(path.join(f.config.output, "wiki/answers/unbelegt.md")),
    );
  } finally {
    await f.close();
  }
});

test("uppercase Markdown extensions are compiled as initial Markdown input", async () => {
  const f = await fixture();
  try {
    const { rename } = await import("node:fs/promises");
    await rename(
      path.join(f.dir, "alpha/README.md"),
      path.join(f.dir, "alpha/README.MD"),
    );
    const result = await f.run("maintain");
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.match(
      await readFile(
        path.join(f.config.output, "wiki/concepts/freigabe.md"),
        "utf8",
      ),
      /Alpha verlangt zwei/,
    );
  } finally {
    await f.close();
  }
});

test("active publication resolves known wiki links and leaves unknown concepts as plain text", async () => {
  const f = await fixture();
  try {
    const { writeFile } = await import("node:fs/promises");
    await f.run("maintain");
    const page = (await f.run("status")).pages[0];
    const draft = path.join(f.dir, "links.json");
    await writeFile(
      draft,
      JSON.stringify({
        slug: "links",
        question: "Verweise",
        answer: "Siehe [[Freigabe]] und [[Nicht-vorhanden]].",
        evidence: [{ id: page.id, hash: page.hash }],
      }),
    );
    assert.equal((await f.run("save", "--draft", draft)).ok, true);
    const body = await readFile(
      path.join(f.config.output, "wiki/answers/links.md"),
      "utf8",
    );
    assert.match(body, /\[Freigabe\]\(\.\.\/concepts\/freigabe.md\)/);
    assert.match(body, /\[concepts\/freigabe\]\(\.\.\/concepts\/freigabe.md\)/);
    assert.match(body, /\[alpha\/README.md\]\(obsidian:\/\/open\?path=/);
    assert.doesNotMatch(body, /\[\[Nicht-vorhanden\]\]/);
    assert.equal((await f.run("lint")).ok, true);
  } finally {
    await f.close();
  }
});

test("natural language questions reuse wiki evidence before falling back to originals", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    const queried = await f.run(
      "query",
      "--question",
      "Freigabe: Welche gemeinsame Regel gilt in beiden Repositories?",
    );
    assert.equal(queried.ok, true, JSON.stringify(queried));
    assert.equal(queried.fallback, false);
    assert.equal(queried.evidence[0].kind, "concept");
  } finally {
    await f.close();
  }
});
