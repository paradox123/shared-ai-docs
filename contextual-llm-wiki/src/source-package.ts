import path from "node:path";
import { mkdir, rm } from "node:fs/promises";
import { maintenanceInventory } from "./maintenance-inventory.ts";
import { validatePublication } from "./publication-validation.ts";
import { hash } from "./storage.ts";
import { renderConcept, publishPage, entry } from "./publish.ts";
import { saveState, reviewPages } from "./state.ts";
import { qmd } from "./qmd.ts";

export function sourceStatements(extracted: Map<string, any>, sources: any) {
  const pages: any = {},
    bodies: any = {};
  for (const [sourceId, raw] of extracted) {
    const id = "source-notes/" + hash(sourceId).slice(0, 24);
    const sourceVersions = { [sourceId]: sources[sourceId].hash };
    // Extraction summaries are plain text. Do not turn provider-supplied links
    // into extra, untracked dependencies or a fabricated global concept page.
    const plain = (text: string) => text.replace(/[<>\[\]`]/g, "");
    const body =
      `# Quellengebundene Aussagen: ${sourceId}\n\nGeltungsbereich: ausschließlich diese Originalquelle. Gemeinsame Synthese noch offen.\n\n` +
      raw.concepts
        .map((c: any) => `## ${plain(c.concept)}\n\n${plain(c.summary)}`)
        .join("\n\n");
    bodies[id] = renderConcept(body, sourceVersions, sources);
    pages[id] = {
      id,
      kind: "source-summary",
      publicationVersion: 2,
      title: sourceId,
      sourceVersions,
      pageVersions: {},
      hash: hash(bodies[id]),
    };
  }
  return { pages, bodies };
}

export async function publishSourcePackage(
  config: any,
  state: any,
  sources: any,
  extracted: Map<string, any>,
  inventory: any,
  progress: any,
  delta: any,
) {
  progress.phase = "validate-publication";
  progress.notify();
  const { latest, drift } = await validatePublication(config, state, sources);
  if (drift.length) {
    // This scan already observed the new versions. Preserve that observation
    // now, including in the caller's later failure report, not at next restart.
    Object.assign(inventory, await maintenanceInventory(config, latest));
    progress.maintenance = inventory.report(state);
    progress.sourceIndex = {
      ...progress.sourceIndex,
      ok: false,
      status: "stale",
      drift,
    };
    progress.failures.push({
      phase: "source-drift",
      sources: drift,
      error:
        "Sources changed during generation; current concept membership remains unknown",
    });
  }
  // Unknown membership can expand any global concept. Retain only explicitly
  // source-bounded evidence; propagate this hold through saved answer chains.
  const blocked = new Set(
    Object.values<any>(state.pages)
      .filter((p) => p.kind === "concept" || p.migration)
      .map((p) => p.id)
      .concat((await reviewPages(config, state, latest)).map((p) => p.id)),
  );
  let changed = true;
  while (changed) {
    changed = false;
    for (const p of Object.values<any>(state.pages))
      if (
        !blocked.has(p.id) &&
        Object.keys(p.pageVersions).some((id) => blocked.has(id))
      ) {
        blocked.add(p.id);
        changed = true;
      }
  }
  for (const id of blocked) {
    state.pages[id].withdrawn = true;
    await rm(path.join(config.output, "wiki", id + ".md"), { force: true });
  }
  progress.phase = "publish";
  progress.notify();
  const validExtractions = new Map(
    [...extracted].filter(([id]) => latest[id]?.hash === sources[id]?.hash),
  );
  const statements = sourceStatements(validExtractions, sources);
  for (const page of Object.values<any>(statements.pages)) {
    const old = state.pages[page.id];
    if (
      old &&
      !old.withdrawn &&
      Object.entries(old.sourceVersions).every(
        ([id, version]) => sources[id]?.hash === version,
      )
    ) {
      // A cache-contract change may produce new wording for the same original.
      // Keep the already verified bytes until common synthesis can also
      // regenerate dependent saved answers in order.
      delete statements.pages[page.id];
      continue;
    }
    await publishPage(config, page, statements.bodies[page.id]);
    state.pages[page.id] = page;
    const sourceId = Object.keys(page.sourceVersions)[0];
    inventory.value.sources[sourceId].summarizedHash = sources[sourceId].hash;
  }
  state.pending = [
    {
      phase: "dependency-discovery",
      sources: [
        ...new Set([
          ...delta.added,
          ...delta.changed,
          ...delta.removed,
          ...drift,
        ]),
      ],
      pages: Object.values<any>(state.pages)
        .filter((p) => p.withdrawn)
        .map((p) => p.id),
      reason:
        "Common synthesis incomplete; source statements do not close dependent work",
    },
  ];
  await inventory.save();
  await saveState(config, state);
  await entry(config, state);
  await mkdir(path.join(config.output, ".state/compiler/.llmwiki"), {
    recursive: true,
  });
  progress.phase = "wiki-index";
  progress.completed = Object.keys(statements.pages);
  progress.remaining = state.pending;
  progress.maintenance = inventory.report(state);
  progress.notify();
  await qmd(config, "update");
  return {
    ok: false,
    qmdSafe: true,
    packageCompleted: true,
    error: progress.failures.length
      ? progress.failures.map((f: any) => f.error).join("; ")
      : undefined,
    failures: progress.failures,
    pending: state.pending,
    completed: Object.keys(statements.pages),
    unchanged: Object.values<any>(state.pages)
      .filter((p) => !p.withdrawn && !statements.pages[p.id])
      .map((p) => p.id),
    pages: Object.values<any>(state.pages)
      .filter((p) => !p.withdrawn)
      .map((p) => p.id),
    changes: delta,
    maintenance: inventory.report(state),
  };
}
