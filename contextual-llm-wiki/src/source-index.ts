import path from "node:path";
import { mkdir, readdir, rm } from "node:fs/promises";
import { atomic, json, hash, writeJson } from "./storage.ts";
import { qmd, sourceCollectionName, sourceIndexRoot } from "./qmd.ts";
import type { Source } from "./sources.ts";

const manifestPath = (c: any) =>
  path.join(c.output, ".state/source-index/manifest.json");

// Copies contain only selected originals. Wiki publication is never in this collection.
// Caller owns the context writer lock; the manifest certifies only a completed QMD update.
export async function indexSources(
  config: any,
  sources: Record<string, Source>,
) {
  const root = sourceIndexRoot(config);
  const entries = Object.fromEntries(
    Object.values(sources).map((s) => [
      hash(s.id) + ".md",
      { id: s.id, hash: s.hash },
    ]),
  );
  const previous = await json(manifestPath(config), {});
  await mkdir(root, { recursive: true });
  for (const [file, source] of Object.entries(entries))
    await atomic(path.join(root, file), sources[source.id].text);
  for (const file of await readdir(root))
    if (!entries[file]) await rm(path.join(root, file));
  const index = await qmd(config, "update", undefined, true);
  const result = {
    ok: true,
    status:
      JSON.stringify(previous.entries) === JSON.stringify(entries)
        ? "unchanged"
        : "updated",
    collection: sourceCollectionName(config),
    sourceCount: Object.keys(entries).length,
    checkedAt: new Date().toISOString(),
    index,
  };
  await writeJson(manifestPath(config), { entries, ...result });
  return result;
}

export async function sourceMatches(
  config: any,
  question: string,
  sources: Record<string, Source>,
) {
  const manifest = await json(manifestPath(config), null);
  if (!manifest?.ok) return [];
  const hits = await qmd(config, "search", question, true);
  const prefix = "qmd://" + sourceCollectionName(config) + "/";
  return hits.flatMap((hit: any) => {
    const uri = hit.file || hit.filepath || hit.displayPath;
    const entry =
      uri?.startsWith(prefix) && manifest.entries[uri.slice(prefix.length)];
    return entry && sources[entry.id]?.hash === entry.hash
      ? [{ ...entry, uri, score: hit.score }]
      : [];
  });
}
