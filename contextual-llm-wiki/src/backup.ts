import path from "node:path";
import { cp, mkdir, readFile, rm } from "node:fs/promises";
import { readState, saveState } from "./state.ts";
import { scan } from "./sources.ts";
import { hash, json, writeJson, atomic } from "./storage.ts";
import { maintain } from "./maintenance.ts";
import { entry } from "./publish.ts";
import { preflight } from "./runtime.ts";
export async function backup(config: any, destination: string) {
  const state = await readState(config);
  if (state.pending.length)
    throw Error("Finish pending maintenance before backup");
  const dest = path.resolve(destination);
  for (const r of config.repos)
    if (dest === r.root || dest.startsWith(r.root + path.sep))
      throw Error("Backup cannot be written inside a Fachquelle repository");
  if (
    dest === config.output ||
    dest.startsWith(path.join(config.output, "wiki") + path.sep) ||
    dest.startsWith(path.join(config.output, ".state/compiler"))
  )
    throw Error("Backup must be outside active wiki and compiler");
  await mkdir(dest, { recursive: false });
  for (const p of Object.values<any>(state.pages)) {
    const body = await readFile(
      path.join(config.output, "wiki", p.id + ".md"),
      "utf8",
    );
    if (hash(body) !== p.hash)
      throw Error("Page version changed before backup: " + p.id);
    await atomic(path.join(dest, "wiki", p.id + ".md"), body);
  }
  await cp(
    path.join(config.output, ".state/compiler"),
    path.join(dest, "compiler"),
    { recursive: true },
  );
  await writeJson(path.join(dest, "backup.json"), {
    version: 1,
    context: config.context,
    scope: config.scope,
    state,
  });
  return { ok: true, backup: dest, pages: Object.keys(state.pages).length };
}
export async function restore(config: any, backupPath: string) {
  preflight();
  const source = path.resolve(backupPath),
    saved = await json(path.join(source, "backup.json"));
  if (
    saved.version !== 1 ||
    saved.context !== config.context ||
    saved.scope !== config.scope
  )
    throw Error("Backup context/scope mismatch");
  const state = saved.state,
    sources = await scan(config),
    bodies: any = {};
  // Verify every page before touching active state. Only a checked subset is copied.
  for (const p of Object.values<any>(state.pages)) {
    if (!/^(concepts|answers)\/[^/]+$/.test(p.id) || p.id.includes(".."))
      throw Error("Invalid backup page identity");
    const body = await readFile(
      path.join(source, "wiki", p.id + ".md"),
      "utf8",
    );
    if (hash(body) !== p.hash)
      throw Error("Backup page hash mismatch: " + p.id);
    if (
      Object.keys(p.sourceVersions).length &&
      Object.entries(p.sourceVersions).every(
        ([id, h]) => sources[id]?.hash === h,
      )
    )
      bodies[p.id] = body;
    else p.withdrawn = true;
  }
  for (const p of Object.values<any>(state.pages))
    if (Object.keys(p.pageVersions).some((id) => !bodies[id])) {
      delete bodies[p.id];
      p.withdrawn = true;
    }
  await rm(path.join(config.output, "wiki"), { recursive: true, force: true });
  for (const [id, body] of Object.entries<string>(bodies))
    await atomic(path.join(config.output, "wiki", id + ".md"), body);
  const compiler = path.join(config.output, ".state/compiler");
  await rm(compiler, { recursive: true, force: true });
  await cp(path.join(source, "compiler"), compiler, { recursive: true });
  state.pending = [{ phase: "restore-reconcile" }];
  await saveState(config, state);
  await entry(config, state);
  const result = await maintain(config);
  return { ...result, restoredFrom: source };
}
