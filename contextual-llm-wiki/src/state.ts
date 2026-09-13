import path from "node:path";
import { readFile } from "node:fs/promises";
import { json, hash, writeJson } from "./storage.ts";
import { scan } from "./sources.ts";
export const statePath = (c: any) => path.join(c.output, ".state/state.json");
export async function readState(c: any) {
  const state = await json(statePath(c), {
    context: c.context,
    scope: c.scope,
    sources: {},
    pages: {},
    pending: [],
    lastCompleted: null,
  });
  if (
    state.context !== undefined &&
    (state.context !== c.context || state.scope !== c.scope)
  )
    throw Error("Output already belongs to another context/scope");
  return state;
}
export const saveState = (c: any, s: any) => writeJson(statePath(c), s);
export function changes(state: any, sources: any) {
  return {
    added: Object.keys(sources).filter((id) => !state.sources[id]),
    changed: Object.keys(sources).filter(
      (id) => state.sources[id] && sources[id].hash !== state.sources[id].hash,
    ),
    removed: Object.keys(state.sources).filter((id) => !sources[id]),
  };
}
export async function reviewPages(config: any, state: any, sources: any) {
  const review: any[] = [];
  for (const page of Object.values<any>(state.pages)) {
    const reasons = Object.entries(page.sourceVersions)
      .filter(([id, version]) => sources[id]?.hash !== version)
      .map(([id]) => ({
        source: id,
        reason: sources[id] ? "source-changed" : "source-removed",
      }));
    let body = "";
    try {
      body = await readFile(
        path.join(config.output, "wiki", page.id + ".md"),
        "utf8",
      );
    } catch (e) {
      if ((e as any).code !== "ENOENT") throw e;
    }
    if (hash(body) !== page.hash)
      reasons.push({ source: page.id, reason: "page-changed-or-withdrawn" });
    if (!Object.keys(page.sourceVersions).length)
      reasons.push({ source: page.id, reason: "unknown-provenance" });
    if (reasons.length)
      review.push({
        id: page.id,
        reasons,
        passages: body
          .split("\n")
          .filter((line) => reasons.some((r) => line.includes(r.source))),
      });
  }
  // A saved page can change independently of its original sources. Propagate
  // invalidity through the page graph, including dependencies whose bytes changed.
  let progressed = true;
  while (progressed) {
    progressed = false;
    for (const page of Object.values<any>(state.pages)) {
      if (review.some((p) => p.id === page.id)) continue;
      const reasons = Object.entries(page.pageVersions)
        .filter(
          ([id, version]) =>
            state.pages[id]?.hash !== version ||
            state.pages[id]?.withdrawn ||
            review.some((p) => p.id === id),
        )
        .map(([id]) => ({
          source: id,
          reason: "page-dependency-changed-or-unverified",
        }));
      if (reasons.length) {
        review.push({ id: page.id, reasons, passages: [] });
        progressed = true;
      }
    }
  }
  return review;
}
export async function status(config: any) {
  const state = await readState(config),
    sources = await scan(config);
  return {
    ok: true,
    context: config.context,
    lastCompleted: state.lastCompleted,
    pending: state.pending,
    changes: changes(state, sources),
    review: await reviewPages(config, state, sources),
    pages: Object.values(state.pages),
    sourceCount: Object.keys(sources).length,
  };
}
