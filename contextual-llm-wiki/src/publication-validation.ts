import path from "node:path";
import { readFile } from "node:fs/promises";
import { checkConfig } from "./config.ts";
import { scan } from "./sources.ts";
import { hash } from "./storage.ts";

// Re-scan the same publication boundary; callers isolate only known dependencies.
export async function validatePublication(
  config: any,
  state: any,
  sources: any,
) {
  await checkConfig(config);
  const latest = await scan(config);
  const drift = [
    ...new Set([...Object.keys(sources), ...Object.keys(latest)]),
  ].filter((id) => latest[id]?.hash !== sources[id]?.hash);
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
  return { latest, drift };
}
