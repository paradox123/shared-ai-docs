import { readFile, mkdir, cp, rm, rename } from "node:fs/promises";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { maintenanceControl } from "./maintenance-control.ts";
import { createWiki, modelWork } from "../.runtime/compiler/dist/index.js";
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
import { indexSources } from "./source-index.ts";
import { lint } from "./inspection.ts";
import { checkConfig } from "./config.ts";
import { preflight } from "./runtime.ts";
import { extractionCache } from "./extraction-cache.ts";
import { failureScope } from "./failure-scope.ts";
export async function maintain(config: any) {
  const artifacts = path.join(config.output, ".state/runs", randomUUID());
  await mkdir(artifacts, { recursive: true, mode: 0o700 });
  let report: any;
  const progress: any = {
    completed: [],
    unchanged: [],
    failures: [],
    pages: [],
    sourceIndex: { ok: false, status: "blocked" },
  };
  const control = maintenanceControl(
    process.env.WIKI_MAINTENANCE_PROGRESS ||
      path.join(artifacts, "progress.json"),
    progress,
  );
  progress.notify = control.emit;
  try {
    report = await modelWork.run(control.run, () =>
      maintainRun(config, artifacts, progress),
    );
  } catch (error) {
    const message = String((error as Error).message);
    const pending = await readState(config)
      .then((s) => s.pending)
      .catch(() => []);
    report = {
      ...progress,
      ok: false,
      qmdSafe: false,
      error: message,
      failures: [...progress.failures, { phase: "shared", error: message }],
      pending: pending.length
        ? pending
        : [{ phase: "blocked", error: message }],
    };
  }
  await control.close();
  progress.phase = "finished";
  progress.remaining = report.pending || [];
  control.emit();
  delete report.notify;
  report = {
    ...report,
    outcome: control.reason || (report.ok ? "completed" : "incomplete"),
    sourceIndex: progress.sourceIndex,
    extractions: progress.extractions || { saved: 0, reused: 0, invalid: 0 },
    wiki: {
      ok: report.ok,
      status: report.ok ? (report.noop ? "noop" : "completed") : "incomplete",
    },
    artifacts,
    report: path.join(artifacts, "report.json"),
  };
  await writeJson(report.report, report);
  return report;
}

async function maintainRun(config: any, artifacts: string, progress: any) {
  const sources = await scan(config),
    state = await readState(config);
  const delta = changes(state, sources),
    review = await reviewPages(config, state, sources);
  progress.changes = delta;
  progress.remaining = [
    {
      phase: "compile",
      sources: [...delta.added, ...delta.changed],
      removed: delta.removed,
      pages: review.map((p) => p.id),
    },
  ];
  progress.phase = "source-index";
  progress.notify();
  const changedIds = new Set(review.map((p) => p.id));
  if (state.publicationVersion !== 2)
    for (const id of Object.keys(state.pages)) changedIds.add(id);
  // Withdraw stale wiki files before any index mutation, including a global update.
  for (const id of changedIds) {
    state.pages[id].withdrawn = true;
    await rm(path.join(config.output, "wiki", id + ".md"), { force: true });
  }
  if (changedIds.size) {
    await saveState(config, state);
    await entry(config, state);
  }
  progress.sourceIndex = await indexSources(config, sources);
  progress.notify();
  const runtime = preflight();
  const work =
    delta.added.length +
    delta.changed.length +
    delta.removed.length +
    review.length;
  if (!work && !state.pending.length && state.publicationVersion === 2)
    return {
      ok: true,
      ...runtime,
      noop: true,
      pages: Object.keys(state.pages),
      review: [],
      qmdSafe: true,
      completed: [],
      unchanged: Object.keys(state.pages),
      failures: [],
      pending: [],
    };
  await qmd(config, "register");
  const stage = path.join(artifacts, "staging"),
    root = path.join(stage, "compiler");
  const baseline = path.join(config.output, ".state/compiler");
  await mkdir(stage, { recursive: true });
  try {
    state.pending = [
      {
        phase: "compile",
        changes: delta,
        review: review.map((p) => ({ id: p.id, reasons: p.reasons })),
      },
    ];
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
    // Existing pages/index are unrecorded model context upstream. Generate from
    // current primary evidence only; restore unchanged compiler pages afterwards.
    const priorOwned = await json(path.join(root, ".llmwiki/state.json"), {
      sources: {},
    });
    if (state.publicationVersion !== 2) {
      const rebuild = structuredClone(priorOwned);
      for (const source of Object.values<any>(rebuild.sources))
        source.hash = "";
      await writeJson(path.join(root, ".llmwiki/state.json"), rebuild);
    }
    await rm(path.join(root, "wiki"), { recursive: true, force: true });
    const failures: any[] = progress.failures;
    const cache = await extractionCache(config, sources, () =>
      progress.notify(),
    );
    progress.extractions = cache.stats;
    const wiki = createWiki({ root });
    const result = await wiki.compile({
      embeddings: false,
      extractionCache: cache.run,
      concurrency: config.concurrency || 2,
      onBoundedFailure: (failure) => failures.push(failure),
    });
    await writeJson(path.join(artifacts, "compiler-result.json"), {
      result,
      failures,
    });
    if (
      !Array.isArray(result.errors) ||
      !Array.isArray(result.pages) ||
      !Array.isArray(result.concepts) ||
      !Number.isInteger(result.compiled) ||
      !Number.isInteger(result.skipped) ||
      !Number.isInteger(result.deleted)
    )
      throw Error("Incomplete compiler result contract");
    const unclassified = result.errors.filter(
      (error) =>
        !failures.some(
          (failure) =>
            error === failure.error ||
            (failure.phase === "extract" &&
              error === "No concepts extracted from " + failure.id),
        ),
    );
    if (unclassified.length)
      throw Error("Unclassified compiler failure: " + unclassified.join("; "));
    if (
      failures.some(
        (f) =>
          f.phase === "extract" && !priorOwned.sources[f.id]?.concepts?.length,
      )
    )
      throw Error(
        "Unknown dependencies after source extraction failure: " +
          failures.map((f) => f.id).join(", "),
      );
    const owned = await json(path.join(root, ".llmwiki/state.json"), {
      sources: {},
    });
    const { failedSources, blocked } = failureScope(
      priorOwned,
      owned,
      state.pages,
      failures,
    );
    const pages: any = {},
      bodies: any = {};
    for (const [sourceId, sourceState] of Object.entries<any>(owned.sources)) {
      if (!sources[sourceId]) continue;
      for (const slug of sourceState.concepts) {
        const id = "concepts/" + slug;
        if (failedSources.has(sourceId)) blocked.add(id);
        pages[id] ||= {
          id,
          kind: "concept",
          sourceVersions: {},
          pageVersions: {},
        };
        pages[id].sourceVersions[sourceId] = sources[sourceId].hash;
      }
    }
    for (const id of blocked) delete pages[id];
    await mkdir(path.join(root, "wiki/concepts"), { recursive: true });
    for (const page of Object.values<any>(pages)) {
      if (!result.pages.includes(page.id.slice(9))) {
        await cp(
          path.join(baseline, "wiki", page.id + ".md"),
          path.join(root, "wiki", page.id + ".md"),
        );
      }
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
        if (
          !Object.keys(old.sourceVersions).length ||
          deps.some((id) => !state.pages[id])
        )
          throw Error("Unknown saved-answer dependencies: " + old.id);
        if (deps.some((id) => remaining.some((p) => p.id === id))) continue;
        remaining.splice(remaining.indexOf(old), 1);
        progressed = true;
        if (blocked.has(old.id) || deps.some((id) => blocked.has(id))) {
          blocked.add(old.id);
          continue;
        }
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
        let text: string;
        try {
          text = await answer(question, evidence);
        } catch (error) {
          if ((error as any).sharedMaintenance) throw error;
          failures.push({
            phase: "answer",
            id: old.id,
            sources: [],
            error: String(error),
          });
          blocked.add(old.id);
          continue;
        }
        const sourceVersions: any = {},
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
    progress.phase = "validate-publication";
    progress.notify();
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
    progress.phase = "publish";
    progress.notify();
    for (const id of Object.keys(state.pages))
      if (!pages[id])
        await rm(path.join(config.output, "wiki", id + ".md"), { force: true });
    for (const page of Object.values<any>(pages))
      await publishPage(config, page, bodies[page.id]);
    for (const id of blocked) {
      await rm(path.join(config.output, "wiki", id + ".md"), { force: true });
      if (state.pages[id]) pages[id] = { ...state.pages[id], withdrawn: true };
    }
    for (const id of failedSources) {
      owned.sources[id] = {
        ...(owned.sources[id] || priorOwned.sources[id]),
        hash: "",
        concepts: [
          ...new Set([
            ...(priorOwned.sources[id]?.concepts || []),
            ...(owned.sources[id]?.concepts || []),
          ]),
        ],
      };
    }
    await writeJson(path.join(root, ".llmwiki/state.json"), owned);
    const pending: any[] = failures.length
      ? [
          {
            phase: "compile",
            sources: [...failedSources],
            pages: [...blocked],
            failures,
          },
        ]
      : [];
    const next = {
      migrations: state.migrations,
      publicationVersion: 2,
      context: config.context,
      scope: config.scope,
      sources: Object.fromEntries(
        Object.entries(sources).flatMap(([id, { text, ...s }]) =>
          failedSources.has(id)
            ? state.sources[id]
              ? [[id, state.sources[id]]]
              : []
            : [[id, s]],
        ),
      ),
      pages,
      lastCompleted: state.lastCompleted,
      pending: [...pending, { phase: "qmd" }],
    };
    await saveState(config, next);
    await entry(config, next);
    progress.completed = Object.keys(pages).filter(
      (id) => !pages[id].withdrawn && pages[id].hash !== state.pages[id]?.hash,
    );
    progress.unchanged = Object.keys(pages).filter(
      (id) => !pages[id].withdrawn && pages[id].hash === state.pages[id]?.hash,
    );
    progress.pages = Object.keys(pages).filter((id) => !pages[id].withdrawn);
    await rm(baseline, { recursive: true, force: true });
    await rename(root, baseline);
    progress.phase = "lint";
    progress.remaining = next.pending;
    progress.notify();
    const audit = await lint(config);
    if (audit.activeIssues.length || audit.unresolvedCompilerErrors.length)
      throw Error(
        "Active lint requires review: " +
          JSON.stringify([
            ...audit.activeIssues,
            ...audit.unresolvedCompilerErrors,
          ]),
      );
    progress.phase = "wiki-index";
    progress.notify();
    const index = await qmd(config, "update");
    if (!pending.length) next.lastCompleted = new Date().toISOString();
    next.pending = pending;
    (next as any).lint = {
      activeIssues: audit.activeIssues,
      compilerLinkSuggestions: audit.compilerLinkSuggestions,
    };
    await saveState(config, next);
    await entry(config, next);
    return {
      ok: !pending.length,
      qmdSafe: true,
      error: pending.length
        ? failures.map((f) => f.error).join("; ")
        : undefined,
      failures,
      pending,
      completed: progress.completed,
      unchanged: progress.unchanged,
      ...runtime,
      result,
      index,
      lint: { ...audit, ok: !pending.length, pending },
      changes: delta,
      review,
      pages: Object.keys(pages).filter((id) => !pages[id].withdrawn),
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
