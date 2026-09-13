import path from "node:path";
import { evidenceEligibility, type EvidenceLimits } from "./evidence-limits.ts";
import { readFile } from "node:fs/promises";
import { checkConfig } from "./config.ts";
import { qmd, collectionName } from "./qmd.ts";
import { entry, renderAnswer, normalizeLinks } from "./publish.ts";
import { answer, relevantEvidence } from "./completion.ts";
import { readState, saveState, reviewPages } from "./state.ts";
import { scan } from "./sources.ts";
import { json, atomic, hash } from "./storage.ts";
export async function query(
  config: any,
  question: string,
  save?: string,
  limits: EvidenceLimits = {},
) {
  if (!question?.trim()) throw Error("--question is required");
  const state = await readState(config),
    sources = await scan(config),
    review = await reviewPages(config, state, sources);
  const eligible = evidenceEligibility(config, state, sources, limits);
  const ineligible = new Set(review.map((p) => p.id));
  const results = await qmd(config, "search", question);
  let evidence: any[] = [];
  for (const hit of results) {
    const uri = hit.file || hit.filepath || hit.displayPath;
    const prefix = "qmd://" + collectionName(config) + "/";
    if (!uri?.startsWith(prefix)) continue;
    const id = uri.slice(prefix.length).replace(/\.md$/, "");
    const page = state.pages[id];
    if (!page || ineligible.has(id) || !eligible.page(id)) continue;
    evidence.push({
      ...page,
      body: await readFile(
        path.join(config.output, "wiki", id + ".md"),
        "utf8",
      ),
    });
  }
  evidence = await relevantEvidence(question, evidence);
  if (!evidence.length) {
    const terms = question.toLowerCase().match(/[\p{L}\p{N}]{3,}/gu) || [];
    for (const source of Object.values<any>(sources))
      if (
        eligible.source(source.id) &&
        terms.some((t) => source.text.toLowerCase().includes(t))
      ) {
        evidence.push({
          id: "sources/" + source.id,
          hash: source.hash,
          kind: "source",
          body: source.text,
          sourceVersions: { [source.id]: source.hash },
          pageVersions: {},
        });
      }
    evidence = await relevantEvidence(question, evidence);
  }
  const text = await answer(question, evidence);
  await checkConfig(config);
  const latest = await scan(config);
  for (const e of evidence) {
    if (
      Object.entries(e.sourceVersions).some(([id, h]) => latest[id]?.hash !== h)
    )
      throw Error("Evidence changed during query; retry with current sources");
    if (
      e.kind !== "source" &&
      hash(
        await readFile(path.join(config.output, "wiki", e.id + ".md"), "utf8"),
      ) !== e.hash
    )
      throw Error("Page changed during query");
  }
  let saved;
  if (save)
    saved = await saveAnswer(
      config,
      state,
      save,
      question,
      text,
      evidence,
      sources,
    );
  return {
    ok: true,
    engine: "qmd",
    answer: text,
    evidence: evidence.map(({ body, ...e }) => e),
    originals: [
      ...new Set(evidence.flatMap((e) => Object.keys(e.sourceVersions))),
    ].map((id) => ({
      id,
      path: latest[id].original,
      uri: "obsidian://open?path=" + encodeURIComponent(latest[id].original),
      hash: latest[id].hash,
      freshness: "checked-current",
    })),
    review,
    saved,
    fallback: evidence.some((e) => e.kind === "source"),
  };
}
export async function saveAnswer(
  config: any,
  state: any,
  slug: string,
  question: string,
  body: string,
  evidence: any[],
  sources: any,
) {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(slug)) throw Error("Invalid answer name");
  if (!evidence.length) throw Error("Missing evidence provenance");
  if (!question?.trim() || !body?.trim())
    throw Error("Question and answer must be nonempty");
  const id = "answers/" + slug,
    sourceVersions: any = {},
    pageVersions: any = {};
  const visited = new Set<string>();
  const dependsOnAnswer = (pageId: string): boolean => {
    if (pageId === id) return true;
    if (visited.has(pageId)) return false;
    visited.add(pageId);
    return Object.keys(state.pages[pageId]?.pageVersions || {}).some(
      dependsOnAnswer,
    );
  };
  for (const e of evidence) {
    Object.assign(sourceVersions, e.sourceVersions);
    if (e.kind !== "source") pageVersions[e.id] = e.hash;
  }
  await checkConfig(config);
  const current = await scan(config);
  for (const [pageId, version] of Object.entries(pageVersions)) {
    const currentBody = await readFile(
      path.join(config.output, "wiki", pageId + ".md"),
      "utf8",
    );
    if (hash(currentBody) !== version || state.pages[pageId]?.withdrawn)
      throw Error("Page evidence changed before save");
    if (dependsOnAnswer(pageId))
      throw Error("Answer dependency cycle: answer cannot depend on itself");
  }
  if (
    Object.keys(sourceVersions).some(
      (id) => current[id]?.hash !== sourceVersions[id],
    )
  )
    throw Error("Evidence changed before save");
  if (!Object.keys(sourceVersions).length)
    throw Error("Missing source provenance");
  const rendered = normalizeLinks(
    renderAnswer(question, body, evidence, current),
    id,
    state.pages,
  );
  const page = {
    id,
    kind: "answer",
    question,
    sourceVersions,
    pageVersions,
    hash: hash(rendered),
  };
  await atomic(path.join(config.output, "wiki", id + ".md"), rendered);
  state.pages[id] = page;
  const pending = { phase: "qmd-save", id };
  state.pending.push(pending);
  await saveState(config, state);
  await entry(config, state);
  await qmd(config, "update");
  state.pending = state.pending.filter((p: any) => p !== pending);
  await saveState(config, state);
  await entry(config, state);
  return id;
}

export async function search(
  config: any,
  question: string,
  limits: EvidenceLimits = {},
) {
  const state = await readState(config),
    sources = await scan(config),
    review = await reviewPages(config, state, sources);
  const eligible = evidenceEligibility(config, state, sources, limits);
  const rejected = new Set(review.map((p) => p.id));
  const hits = await qmd(config, "search", question);
  const prefix = "qmd://" + collectionName(config) + "/";
  const results = hits.filter((h: any) => {
    const file = h.file || h.filepath || h.displayPath;
    const id = file?.startsWith(prefix)
      ? file.slice(prefix.length).replace(/\.md$/, "")
      : "";
    return eligible.page(id) && !rejected.has(id);
  });
  return {
    ok: true,
    engine: "qmd",
    rawMatches: hits.length,
    results,
    review,
    pending: state.pending,
  };
}

export async function saveDraft(
  config: any,
  draftPath: string,
  limits: EvidenceLimits = {},
) {
  const draft = await json(draftPath),
    state = await readState(config),
    sources = await scan(config);
  const eligible = evidenceEligibility(config, state, sources, limits);
  if (!Array.isArray(draft.evidence) || !draft.evidence.length)
    throw Error("Missing evidence provenance");
  const review = await reviewPages(config, state, sources),
    invalid = new Set(review.map((p) => p.id));
  const evidence = draft.evidence.map((ref: any) => {
    if (typeof ref.id !== "string" || typeof ref.hash !== "string")
      throw Error("Incomplete evidence provenance");
    if (ref.id.startsWith("sources/")) {
      const id = ref.id.slice(8),
        source = sources[id];
      if (!eligible.source(id))
        throw Error("Source evidence outside task limits");
      if (!source || source.hash !== ref.hash)
        throw Error("Source evidence changed or unavailable");
      return {
        id: ref.id,
        kind: "source",
        hash: source.hash,
        body: source.text,
        sourceVersions: { [id]: source.hash },
      };
    }
    if (!eligible.page(ref.id))
      throw Error("Page evidence outside task limits or unknown provenance");
    const page = state.pages[ref.id];
    if (!page || page.hash !== ref.hash || invalid.has(ref.id))
      throw Error("Page evidence changed or unavailable");
    return page;
  });
  const saved = await saveAnswer(
    config,
    state,
    draft.slug,
    draft.question,
    draft.answer,
    evidence,
    sources,
  );
  return { ok: true, saved };
}
