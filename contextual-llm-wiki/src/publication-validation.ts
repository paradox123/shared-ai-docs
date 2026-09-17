import path from "node:path";
import { readFile } from "node:fs/promises";
import { checkConfig } from "./config.ts";
import { scan } from "./sources.ts";
import { hash } from "./storage.ts";

// Both complete synthesis and source-bounded packages use this conservative
// barrier. Ticket 05 may isolate drift only when dependencies prove it safe.
export async function validatePublication(
  config: any,
  state: any,
  sources: any,
) {
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
}
