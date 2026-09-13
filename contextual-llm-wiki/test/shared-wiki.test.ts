import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdir, writeFile, readFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { fixture, invoke } from "./support.ts";

test("initial common inventory includes eight identities and recursive personal project and meeting sources", async () => {
  const f = await fixture();
  try {
    const vault = path.join(f.dir, "vault");
    const config = await invoke([
      "init-config",
      "--vault",
      vault,
      "--output",
      path.join(vault, "Projects/generated"),
    ]);
    for (const repo of config.repos) {
      await mkdir(repo.root, { recursive: true });
      execFileSync("git", ["init", "-q", repo.root]);
      await writeFile(path.join(repo.root, "README.md"), "# Fachquelle\n");
    }
    for (const file of [
      "Meetings/deep/meeting.md",
      "Projects/team/project.md",
      "Projects/Private/deep/portfolio.md",
      "Projects/generated/output.md",
      "Projects/runtime/log.md",
      "Projects/unselected/README.md",
      "Projects/worktree/README.md",
      "_shared/SpecOps/old.md",
    ]) {
      await mkdir(path.dirname(path.join(vault, file)), { recursive: true });
      await writeFile(path.join(vault, file), "# Fachquelle\n");
    }
    execFileSync("git", [
      "init",
      "-q",
      path.join(vault, "Projects/unselected"),
    ]);
    await writeFile(
      path.join(vault, "Projects/worktree/.git"),
      "gitdir: /unused/worktree\n",
    );
    await writeFile(f.configPath, JSON.stringify(config));
    const result = await f.run("inventory");
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.equal(
      result.selectedSources,
      11,
      "all eight README files and three selected vault zones",
    );
    assert.deepEqual(
      result.repositories.map((r: any) => r.id).sort(),
      [
        "vault-root",
        "meeting-assistant",
        "shared-ai-docs",
        "ki-fuer-kmu",
        "ncg-docs",
        "private",
        "probare-crm",
        "sparkle",
      ].sort(),
    );
    assert.deepEqual(
      result.repositories.find((r: any) => r.id === "vault-root").zones,
      { Meetings: 1, Projects: 1, "Projects/Private": 1 },
    );
    assert.equal(config.scope, "common");
    assert.equal(config.context, "common");
  } finally {
    await f.close();
  }
});

// The external model alone is deterministic; extraction, compilation, state,
// publication and retrieval all run through the pinned compiler and real QMD.
async function portfolioFixture() {
  const f = await fixture((body) => {
    const prompt = body.messages.map((m: any) => m.content).join("\n");
    if (body.tools) {
      const source = prompt.split("--- SOURCE DOCUMENT ---")[1] || "";
      const concept = source.includes("Designkatalog")
        ? "Projektportfolio"
        : "Liquiditaetsreserve";
      return {
        role: "assistant",
        tool_calls: [
          {
            id: "portfolio",
            type: "function",
            function: {
              name: "extract_concepts",
              arguments: JSON.stringify({
                concepts: [
                  {
                    concept,
                    summary: concept,
                    is_new: true,
                    confidence: 1,
                    provenance_state: "extracted",
                  },
                ],
              }),
            },
          },
        ],
      };
    }
    if (prompt.includes("--- RELEVANCE CANDIDATES ---")) {
      const candidates = JSON.parse(
        prompt.split("--- RELEVANCE CANDIDATES ---")[1],
      );
      return {
        role: "assistant",
        content: JSON.stringify({
          relevantIds: candidates
            .filter((e: any) =>
              /Liquiditaetsreserve|Zahlungseingang|verfuegbare Reserve/.test(
                e.body,
              ),
            )
            .map((e: any) => e.id),
        }),
      };
    }
    const material =
      prompt.split("--- SOURCE MATERIAL ---")[1] ||
      prompt.split("--- EVIDENCE ---")[1] ||
      "";
    const control = prompt.includes('about "Projektportfolio"');
    const facts = [
      ...new Set(
        material.match(
          /(?:Das private Portfolio hat \d+ Euro verfuegbare Reserve|Der Projektvertrag sieht 5000 Euro Zahlungseingang im Oktober vor)\./g,
        ) || [],
      ),
    ];
    const originals = [...material.matchAll(/--- SOURCE: (.*?) ---/g)].map(
      (m) => m[1],
    );
    const synthesis =
      facts.length === 2
        ? "Synthese: Bis zum Zahlungseingang im Oktober stuetzt nur die verfuegbare Reserve das Portfolio; die erwarteten Projekteinnahmen sind noch keine heutige Liquiditaet."
        : "Nur die vorliegenden Einzelbelege sind fuer diese Antwort zulaessig.";
    return {
      role: "assistant",
      content: control
        ? "# Projektportfolio\n\nPortfolio bezeichnet hier einen Designkatalog mit blauen Umschlaegen."
        : "# Liquiditaetsreserve fuer das Portfolio\n\n" +
          facts.join(" ") +
          "\n\n" +
          synthesis +
          "\n\n" +
          originals.map((id) => `Beleg ^[${id}:3-3]`).join("\n"),
    };
  });
  f.config.repos[0].id = "private";
  f.config.repos[0].scope = "private";
  f.config.repos[1].id = "probare-crm";
  await writeFile(
    path.join(f.dir, "alpha/README.md"),
    "# Portfolio\n\nDas private Portfolio hat 2000 Euro verfuegbare Reserve.\n",
  );
  await writeFile(
    path.join(f.dir, "beta/README.md"),
    "# Projekteinnahmen\n\nDer Projektvertrag sieht 5000 Euro Zahlungseingang im Oktober vor.\n",
  );
  await writeFile(
    path.join(f.dir, "alpha/control.md"),
    "# Portfolio\n\nPortfolio bezeichnet hier einen Designkatalog mit blauen Umschlaegen.\n",
  );
  await f.saveConfig();
  return f;
}

test("common maintenance synthesizes related personal and project evidence and query excludes a same-term control", async () => {
  const f = await portfolioFixture();
  try {
    const compiled = await f.run("maintain");
    assert.equal(compiled.ok, true, JSON.stringify(compiled));
    assert.equal(compiled.compiler, "34ca1df97b3e60a6700048c48c7cf70c92a9bfdb");
    const page = await readFile(
      path.join(f.config.output, "wiki/concepts/liquiditaetsreserve.md"),
      "utf8",
    );
    assert.match(page, /2000 Euro/);
    assert.match(page, /5000 Euro/);
    assert.match(page, /noch keine heutige Liquiditaet/);
    assert.match(page, /private\/README.md/);
    assert.match(page, /probare-crm\/README.md/);
    assert.doesNotMatch(page, /Designkatalog|control.md/);
    const queried = await f.run(
      "query",
      "--question",
      "Portfolio: Wie wirken Projekteinnahmen auf die Liquiditaetsreserve?",
    );
    assert.equal(queried.ok, true, JSON.stringify(queried));
    assert.equal(queried.fallback, false);
    assert.deepEqual(
      queried.evidence.map((e: any) => e.id),
      ["concepts/liquiditaetsreserve"],
    );
    assert.match(queried.answer, /noch keine heutige Liquiditaet/);
    assert.doesNotMatch(queried.answer, /Designkatalog/);
  } finally {
    await f.close();
  }
});

test("explicit repository and exact-source limits exclude mixed pages, transitive answers and disallowed fallbacks", async () => {
  const f = await portfolioFixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    assert.equal(
      (await f.run("query", "--question", "Portfolio", "--save", "shared")).ok,
      true,
    );
    assert.equal(
      (await f.run("query", "--question", "Portfolio", "--save", "followup"))
        .ok,
      true,
    );
    const before = f.calls.length;
    const limited = await f.run(
      "query",
      "--question",
      "Portfolio",
      "--repo",
      "private",
    );
    assert.equal(limited.ok, true, JSON.stringify(limited));
    assert.equal(limited.fallback, true);
    assert.deepEqual(
      limited.evidence.map((e: any) => e.id),
      ["sources/private/README.md"],
    );
    assert.match(limited.answer, /2000 Euro/);
    assert.doesNotMatch(limited.answer, /5000 Euro|Designkatalog/);
    assert.ok(
      f.calls
        .slice(before)
        .every((c: any) => !JSON.stringify(c.messages).includes("5000 Euro")),
      "limits apply before any provider call",
    );
    const exact = await f.run(
      "query",
      "--question",
      "Projektvertrag",
      "--source",
      "probare-crm/README.md",
      "--save",
      "limited",
    );
    assert.equal(exact.ok, true, JSON.stringify(exact));
    assert.deepEqual(Object.keys(exact.evidence[0].sourceVersions), [
      "probare-crm/README.md",
    ]);
    assert.doesNotMatch(exact.answer, /2000 Euro/);
    const search = await f.run(
      "search",
      "--question",
      "Liquiditaetsreserve",
      "--repo",
      "private",
    );
    assert.equal(search.ok, true, JSON.stringify(search));
    assert.deepEqual(search.results, []);
    const unknown = await f.run(
      "query",
      "--question",
      "Portfolio",
      "--repo",
      "privat",
    );
    assert.equal(unknown.ok, false);
    assert.match(unknown.error, /repo|limit/i);
    const missing = await f.run("query", "--question", "Portfolio", "--source");
    assert.equal(missing.ok, false);
    const draft = path.join(f.dir, "restricted-draft.json");
    const concept = (await f.run("status")).pages.find(
      (p: any) => p.id === "concepts/liquiditaetsreserve",
    );
    await writeFile(
      draft,
      JSON.stringify({
        slug: "disallowed",
        question: "Portfolio",
        answer: "Mixed evidence",
        evidence: [{ id: concept.id, hash: concept.hash }],
      }),
    );
    const saved = await f.run("save", "--draft", draft, "--repo", "private");
    assert.equal(saved.ok, false);
    assert.match(saved.error, /limit/i);
  } finally {
    await f.close();
  }
});

test("common queries reuse valid knowledge without saving and reject stale synthesis before synchronization", async () => {
  const f = await portfolioFixture();
  try {
    assert.equal((await f.run("maintain")).ok, true);
    const before = await f.run("status");
    const extractionCount = () => f.calls.filter((c: any) => c.tools).length;
    const compiled = extractionCount();
    for (let i = 0; i < 2; i++) {
      const query = await f.run("query", "--question", "Portfolio");
      assert.equal(query.ok, true, JSON.stringify(query));
      assert.equal(query.fallback, false);
    }
    const unchanged = await f.run("status");
    assert.deepEqual(unchanged.pages, before.pages);
    assert.equal(extractionCount(), compiled);
    const calls = f.calls.length;
    assert.equal((await f.run("maintain")).noop, true);
    assert.equal(f.calls.length, calls);
    await writeFile(
      path.join(f.dir, "alpha/README.md"),
      "# Portfolio\n\nDas private Portfolio hat 800 Euro verfuegbare Reserve.\n",
    );
    const stale = await f.run(
      "query",
      "--question",
      "Portfolio Liquiditaetsreserve",
    );
    assert.equal(stale.ok, true, JSON.stringify(stale));
    assert.equal(stale.fallback, true);
    assert.ok(
      stale.review.some((p: any) => p.id === "concepts/liquiditaetsreserve"),
    );
    assert.ok(stale.evidence.every((e: any) => e.kind === "source"));
    assert.match(stale.answer, /800 Euro/);
    assert.doesNotMatch(stale.answer, /2000 Euro|Designkatalog/);
    assert.equal((await f.run("maintain")).ok, true);
    const fresh = await f.run("query", "--question", "Portfolio");
    assert.equal(fresh.fallback, false);
    assert.match(fresh.answer, /800 Euro/);
  } finally {
    await f.close();
  }
});

test("common QMD registration stays in default retrieval and leaves an unrelated collection unchanged", async () => {
  const f = await portfolioFixture();
  try {
    Object.assign(f.env, {
      INDEX_PATH: f.config.qmd.dbPath,
      QMD_CONFIG_DIR: path.join(f.dir, "qmd-config"),
    });
    const env = {
      ...process.env,
      ...f.env,
      PATH: process.env.WIKI_QMD_PATH || process.env.PATH,
    };
    const qmd = (...args: string[]) =>
      execFileSync("qmd", args, {
        env,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"],
      });
    const foreign = path.join(f.dir, "foreign");
    await mkdir(foreign);
    await writeFile(
      path.join(foreign, "original.md"),
      "# Fremdbeleg\n\nUnberuehrter Fremdbeleg.\n",
    );
    qmd("collection", "add", foreign, "--name", "unrelated");
    const before = qmd("collection", "show", "unrelated");
    f.config.qmd.isolated = false;
    Object.assign(f.config.qmd, {
      reconcileScript: new URL(
        "../../../danielsvault-rag/scripts/sync-qmd-collections.py",
        import.meta.url,
      ).pathname,
    });
    await f.saveConfig();
    const maintained = await f.run("maintain");
    assert.equal(maintained.ok, true, JSON.stringify(maintained));
    assert.equal(qmd("collection", "show", "unrelated"), before);
    const hits = JSON.parse(qmd("search", "Liquiditaetsreserve", "--json"));
    assert.ok(
      hits.some((h: any) =>
        h.file.includes("contextual-wiki-test/concepts/liquiditaetsreserve"),
      ),
    );
    const manifest = JSON.parse(
      await readFile(
        path.join(f.config.output, ".state/qmd-collections.json"),
        "utf8",
      ),
    );
    assert.deepEqual(
      manifest.collections.map((c: any) => c.name),
      ["contextual-wiki-test"],
    );
    assert.equal(manifest.collections[0].private, false);
    assert.match(
      qmd("search", "Fremdbeleg", "-c", "unrelated", "--json"),
      /Unberuehrter/,
    );
  } finally {
    await f.close();
  }
});

test("an invalid model relevance choice cannot introduce unknown evidence or a saved answer", async () => {
  const f = await fixture((body) =>
    body.messages.some((m: any) =>
      m.content.includes("--- RELEVANCE CANDIDATES ---"),
    )
      ? {
          role: "assistant",
          content: '{"relevantIds":["sources/unselected/secret.md"]}',
        }
      : undefined,
  );
  try {
    assert.equal((await f.run("maintain")).ok, true);
    const query = await f.run(
      "query",
      "--question",
      "Freigabe",
      "--save",
      "invalid",
    );
    assert.equal(query.ok, false);
    assert.match(query.error, /relevance selection/);
    assert.ok(
      !(await f.run("status")).pages.some((p: any) => p.kind === "answer"),
    );
  } finally {
    await f.close();
  }
});

test("fallback can reach later relevant sources when the provider only accepts bounded candidate batches", async () => {
  const f = await fixture((body) => {
    const prompt = body.messages.map((m: any) => m.content).join("\n");
    if (!prompt.includes("--- RELEVANCE CANDIDATES ---")) return;
    const candidates = JSON.parse(
      prompt.split("--- RELEVANCE CANDIDATES ---")[1],
    );
    if (candidates.length > 10)
      return { role: "assistant", content: "Provider context limit exceeded" };
    return {
      role: "assistant",
      content: JSON.stringify({
        relevantIds: candidates
          .filter((e: any) => e.body.includes("Beta verlangt drei"))
          .map((e: any) => e.id),
      }),
    };
  });
  try {
    for (let i = 0; i < 14; i++)
      await writeFile(
        path.join(f.dir, "alpha", `control-${i}.md`),
        "# Freigabe\n\nFreigabe eines Designkatalogs ohne fachlichen Zusammenhang.\n",
      );
    const query = await f.run("query", "--question", "Freigabe");
    assert.equal(query.ok, true, JSON.stringify(query));
    assert.equal(query.fallback, true);
    assert.deepEqual(
      query.evidence.map((e: any) => e.id),
      ["sources/beta/README.md"],
    );
    assert.match(query.answer, /Beta verlangt drei/);
  } finally {
    await f.close();
  }
});

test("WikiQuery returns directly navigable checked originals for wiki evidence and current-source fallback", async () => {
  const f = await fixture();
  try {
    await f.run("maintain");
    const result = await f.run(
      "query",
      "--question",
      "Freigabe",
      "--repo",
      "alpha",
    );
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.deepEqual(
      result.originals.map((s: any) => s.id),
      ["alpha/README.md"],
    );
    assert.equal(result.originals[0].path, path.join(f.dir, "alpha/README.md"));
    assert.equal(
      result.originals[0].uri,
      "obsidian://open?path=" +
        encodeURIComponent(path.join(f.dir, "alpha/README.md")),
    );
    assert.equal(result.originals[0].freshness, "checked-current");
    assert.equal(
      await readFile(result.originals[0].path, "utf8"),
      "# Freigabe\n\nAlpha verlangt zwei Freigaben.\n",
    );
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
    assert.equal(changed.originals[0].freshness, "checked-current");
    assert.notEqual(changed.originals[0].hash, result.originals[0].hash);
    assert.deepEqual(
      changed.originals.map((s: any) => s.id),
      ["alpha/README.md"],
    );
  } finally {
    await f.close();
  }
});
