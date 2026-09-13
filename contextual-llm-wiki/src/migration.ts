import path from "node:path";
import { readFile, rm } from "node:fs/promises";
import { hash, json, writeJson, atomic } from "./storage.ts";
import { scan } from "./sources.ts";
import { readState, saveState, reviewPages, changes } from "./state.ts";
import { maintain } from "./maintenance.ts";
import { entry, publishPage } from "./publish.ts";
import { qmd } from "./qmd.ts";
import { checkConfig } from "./config.ts";
import { lint } from "./inspection.ts";
import { preflight } from "./runtime.ts";
import { filesAt, inspectInput } from "./migration-input.ts";
import { snapshot } from "./migration-snapshot.ts";
import { planImport } from "./migration-plan.ts";
export { migrationInventory } from "./migration-input.ts";

export async function migrate(
  config: any,
  from: string[],
  destination: string,
) {
  const dest = path.resolve(destination),
    journal = path.join(config.output, ".state/migration-pending.json");
  const pending = await json(journal, null);
  if (pending && pending.snapshot !== dest)
    throw Error("Resume pending migration with --snapshot " + pending.snapshot);
  const roots = [...new Set(from.map((r) => path.resolve(r)))];
  const saved = await snapshot(config, roots, dest);
  const stateBefore = await readState(config);
  for (const provisional of pending?.provisional || []) {
    if (stateBefore.pages[provisional.id]) continue;
    if (!/^(concepts|answers)\/import-[a-f0-9]{64}$/.test(provisional.id))
      throw Error("Invalid provisional migration identity");
    const file = path.join(config.output, "wiki", provisional.id + ".md");
    const body = await readFile(file).catch((e) => {
      if (e.code === "ENOENT") return null;
      throw e;
    });
    if (body && hash(body) !== provisional.hash)
      throw Error("Unpublished migration page changed; inspect " + file);
    await rm(file, { force: true });
  }
  const key = hash(JSON.stringify(saved));
  let state = await readState(config);
  const previous = state.migrations?.[key];
  if (previous?.complete) {
    await rm(journal, { force: true });
    return { ok: true, noop: true, snapshot: dest, report: previous.report };
  }
  const progress: any = { snapshot: dest, provisional: [] };
  await writeJson(journal, progress);
  try {
    if (!previous) {
      preflight();
      const fresh =
        !Object.keys(state.sources).length && !Object.keys(state.pages).length;
      if (!fresh) {
        await maintain(config);
        state = await readState(config);
      } else {
        state.publicationVersion = 1;
        state.pending = [];
        await writeJson(
          path.join(config.output, ".state/compiler/.llmwiki/config.json"),
          { version: 1, sources: { recursive: true } },
        );
      }
      const sources = await scan(config),
        reports: any[] = [],
        inputs = [];
      for (const [i, root] of saved.roots.entries()) {
        const files = await filesAt(path.join(dest, "inputs", String(i)));
        const input = inspectInput(root, files, sources);
        inputs.push(input);
        const plan = planImport(
          input,
          files,
          state.pages,
          path.join(dest, "inputs", String(i)),
          dest,
        );
        for (const { page, body } of plan.publications) {
          progress.provisional.push({ id: page.id, hash: page.hash });
          await writeJson(journal, progress);
          for (const id of Object.keys(page.sourceVersions)) {
            if (!state.sources[id]) {
              const { text, ...record } = sources[id];
              state.sources[id] = record;
              await atomic(
                path.join(config.output, ".state/compiler/sources", id),
                text,
              );
            }
          }
          state.pages[page.id] = page;
          await publishPage(config, page, body);
        }
        reports.push(...plan.reports);
      }
      await checkConfig(config);
      const latest = await scan(config);
      if (
        JSON.stringify(
          Object.entries(latest).map(([id, s]) => [id, s.hash]),
        ) !==
        JSON.stringify(Object.entries(sources).map(([id, s]) => [id, s.hash]))
      )
        throw Error("Sources changed during migration; retry snapshot");
      const report = { inputs, pages: reports };
      state.migrations ||= {};
      state.migrations[key] = { complete: false, snapshot: dest, report };
      state.pending = [{ phase: "migration-qmd", snapshot: dest }];
      await saveState(config, state);
      await entry(config, state);
    }
    if (previous) {
      const current = await scan(config),
        delta = changes(state, current);
      if (
        delta.changed.length ||
        delta.removed.length ||
        (await reviewPages(config, state, current)).length
      )
        await maintain(config);
    }
    const audit = await lint(config);
    if (
      audit.review.length ||
      audit.activeIssues.length ||
      audit.forbiddenStores.length ||
      audit.unresolvedCompilerErrors.length
    )
      throw Error(
        "Migration requires review: " +
          JSON.stringify({ review: audit.review, issues: audit.activeIssues }),
      );
    await qmd(config, "update");
    state = await readState(config);
    state.migrations[key].complete = true;
    state.pending = [];
    await saveState(config, state);
    await entry(config, state);
    await rm(journal, { force: true });
    return { ok: true, snapshot: dest, report: state.migrations[key].report };
  } catch (e) {
    const error = (e as Error).message;
    await writeJson(journal, { ...progress, error });
    const failed = await readState(config);
    failed.pending = [{ phase: "migration", snapshot: dest, error }];
    await saveState(config, failed);
    await entry(config, failed);
    throw e;
  }
}
