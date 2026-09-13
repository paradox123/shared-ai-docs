import { readFile, mkdir, cp, rm, rename } from "node:fs/promises";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { createWiki } from "../.runtime/compiler/dist/index.js";
import { scan } from "./sources.ts";
import { atomic, json, hash, writeJson } from "./storage.ts";
import { readState, saveState, changes, reviewPages } from "./state.ts";
import {
  renderConcept,
  renderAnswer,
  publishPage,
  entry,
  normalizeLinks,
} from "./publish.ts";
import { answer } from "./completion.ts";
import { qmd } from "./qmd.ts";
import { lint } from "./inspection.ts";
import { checkConfig } from "./config.ts";
import { preflight } from "./runtime.ts";
export async function maintain(config: any) {
  const runtime = preflight(),
    sources = await scan(config),
    state = await readState(config);
  const delta = changes(state, sources),
    review = await reviewPages(config, state, sources);
  const work =
    delta.added.length +
    delta.changed.length +
    delta.removed.length +
    review.length;
  if (!work && !state.pending.length && state.publicationVersion === 1)
    return {
      ok: true,
      ...runtime,
      noop: true,
      pages: Object.keys(state.pages),
      review: [],
    };
  await qmd(config, "register");
  const stage = path.join(config.output, ".state/staging", randomUUID()),
    root = path.join(stage, "compiler");
  const baseline = path.join(config.output, ".state/compiler");
  await mkdir(stage, { recursive: true });
  const changedIds = new Set(review.map((p) => p.id));
  try {
    state.pending = [
      {
        phase: "compile",
        changes: delta,
        review: review.map((p) => ({ id: p.id, reasons: p.reasons })),
      },
    ];
    // Withdraw invalid pages before model/index work; metadata remains for resumption.
    for (const id of changedIds) {
      state.pages[id].withdrawn = true;
      await rm(path.join(config.output, "wiki", id + ".md"), { force: true });
    }
    await saveState(config, state);
    await entry(config, state);
    try {
      await cp(baseline, root, { recursive: true });
    } catch (e) {
      if ((e as any).code !== "ENOENT") throw e;
    }
    await rm(path.join(root, "sources"), { recursive: true, force: true });
    await writeJson(path.join(root, ".llmwiki/config.json"), {
      version: 1,
      sources: { recursive: true },
    });
    for (const source of Object.values(sources))
      await atomic(path.join(root, "sources", source.id), source.text);
    // Removed evidence must never enter the compiler again via an old page/index.
    if (delta.removed.length) {
      for (const id of changedIds)
        await rm(path.join(root, "wiki", id + ".md"), { force: true });
      await rm(path.join(root, "wiki/index.md"), { force: true });
    }
    const wiki = createWiki({ root });
    const result = await wiki.compile({
      embeddings: false,
      concurrency: config.concurrency || 2,
    });
    if (result.errors.length) throw Error(result.errors.join("; "));
    const owned = await json(path.join(root, ".llmwiki/state.json"), {
        sources: {},
      }),
      pages: any = {},
      bodies: any = {};
    for (const [sourceId, sourceState] of Object.entries<any>(owned.sources)) {
      if (!sources[sourceId]) continue;
      for (const slug of sourceState.concepts) {
        const id = "concepts/" + slug;
        pages[id] ||= {
          id,
          kind: "concept",
          sourceVersions: {},
          pageVersions: {},
        };
        pages[id].sourceVersions[sourceId] = sources[sourceId].hash;
      }
    }
    for (const page of Object.values<any>(pages)) {
      const body = await readFile(
        path.join(root, "wiki", page.id + ".md"),
        "utf8",
      );
      if (/^orphaned: true$/m.test(body))
        throw Error("Compiler returned an orphan as owned: " + page.id);
      const record = await wiki.getPage({
        pageDirectory: "concepts",
        slug: page.id.slice(9),
      });
      page.title = record?.title || page.id;
      bodies[page.id] = renderConcept(body, page.sourceVersions, sources);
    }
    for (const page of Object.values<any>(pages)) {
      bodies[page.id] = normalizeLinks(bodies[page.id], page.id, pages);
      page.hash = hash(bodies[page.id]);
    }
    // Revalidate saved syntheses in dependency order, including answers on answers.
    const remaining = Object.values<any>(state.pages).filter(
      (p) => p.kind === "answer" || p.migration,
    );
    while (remaining.length) {
      let progressed = false;
      for (const old of [...remaining]) {
        const deps = Object.keys(old.pageVersions);
        if (deps.some((id) => remaining.some((p) => p.id === id))) continue;
        remaining.splice(remaining.indexOf(old), 1);
        progressed = true;
        if (
          Object.keys(old.sourceVersions).some((id) => !sources[id]) ||
          deps.some((id) => !pages[id])
        )
          continue;
        const unchanged =
          !changedIds.has(old.id) &&
          deps.every((id) => pages[id].hash === old.pageVersions[id]);
        if (unchanged) {
          pages[old.id] = old;
          bodies[old.id] = await readFile(
            path.join(config.output, "wiki", old.id + ".md"),
            "utf8",
          );
          continue;
        }
        const evidence = deps.map((id) => ({ ...pages[id], body: bodies[id] }));
        const covered = new Set(
          evidence.flatMap((e) => Object.keys(e.sourceVersions)),
        );
        for (const id of Object.keys(old.sourceVersions))
          if (!covered.has(id))
            evidence.push({
              id: "sources/" + id,
              kind: "source",
              hash: sources[id].hash,
              body: sources[id].text,
              sourceVersions: { [id]: sources[id].hash },
            });
        const question = old.question || old.title || old.migration.originalId;
        const text = await answer(question, evidence),
          sourceVersions: any = {},
          pageVersions: any = {};
        for (const e of evidence) {
          Object.assign(sourceVersions, e.sourceVersions);
          if (e.kind !== "source") pageVersions[e.id] = e.hash;
        }
        bodies[old.id] = normalizeLinks(
          renderAnswer(question, text, evidence, sources),
          old.id,
          pages,
        );
        pages[old.id] = {
          ...old,
          withdrawn: false,
          id: old.id,
          kind: old.kind,
          question: old.question,
          sourceVersions,
          pageVersions,
          hash: hash(bodies[old.id]),
        };
      }
      if (!progressed)
        throw Error("Saved answer dependency cycle; restore a valid backup");
    }
    await checkConfig(config);
    const latest = await scan(config);
    if (
      Object.keys(latest).length !== Object.keys(sources).length ||
      Object.keys(sources).some((id) => latest[id]?.hash !== sources[id].hash)
    )
      throw Error(
        "Sources changed during generation; latest state remains pending",
      );
    for (const page of Object.values<any>(state.pages).filter(
      (p) => !p.withdrawn,
    )) {
      const actual = await readFile(
        path.join(config.output, "wiki", page.id + ".md"),
        "utf8",
      );
      if (hash(actual) !== page.hash)
        throw Error("Page changed during generation: " + page.id);
    }
    for (const id of Object.keys(state.pages))
      if (!pages[id])
        await rm(path.join(config.output, "wiki", id + ".md"), { force: true });
    for (const page of Object.values<any>(pages))
      await publishPage(config, page, bodies[page.id]);
    const next = {
      migrations: state.migrations,
      publicationVersion: 1,
      context: config.context,
      scope: config.scope,
      sources: Object.fromEntries(
        Object.entries(sources).map(([id, { text, ...s }]) => [id, s]),
      ),
      pages,
      lastCompleted: state.lastCompleted,
      pending: [{ phase: "qmd" }],
    };
    await saveState(config, next);
    await entry(config, next);
    await rm(baseline, { recursive: true, force: true });
    await rename(root, baseline);
    const audit = await lint(config);
    if (audit.activeIssues.length || audit.unresolvedCompilerErrors.length)
      throw Error(
        "Active lint requires review: " +
          JSON.stringify([
            ...audit.activeIssues,
            ...audit.unresolvedCompilerErrors,
          ]),
      );
    const index = await qmd(config, "update");
    next.lastCompleted = new Date().toISOString();
    next.pending = [];
    (next as any).lint = {
      activeIssues: audit.activeIssues,
      compilerLinkSuggestions: audit.compilerLinkSuggestions,
    };
    await saveState(config, next);
    await entry(config, next);
    return {
      ok: true,
      ...runtime,
      result,
      index,
      lint: { ...audit, ok: true, pending: [] },
      changes: delta,
      review,
      pages: Object.keys(pages),
    };
  } catch (error) {
    const actual = await readState(config);
    actual.pending.push({ error: (error as Error).message });
    await saveState(config, actual);
    await entry(config, actual);
    throw error;
  } finally {
    await rm(stage, { recursive: true, force: true });
  }
}
