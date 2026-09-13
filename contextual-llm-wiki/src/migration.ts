import path from "node:path";
import {
  lstat,
  readdir,
  readFile,
  mkdir,
  writeFile,
  rm,
} from "node:fs/promises";
import { hash, json, writeJson } from "./storage.ts";
import { scan } from "./sources.ts";
import { writableOutput, withWriter } from "./lock.ts";
import { readState, saveState } from "./state.ts";
import { maintain } from "./maintenance.ts";
import { entry, publishPage } from "./publish.ts";
import { qmd } from "./qmd.ts";
import { checkConfig } from "./config.ts";

// A snapshot includes unmanaged notes and compiler state, not just active pages.
async function filesAt(root: string): Promise<Record<string, Buffer>> {
  const files: Record<string, Buffer> = {};
  async function walk(directory: string) {
    let info;
    try {
      info = await lstat(directory);
    } catch (e) {
      if ((e as any).code === "ENOENT" && directory === root) return;
      throw e;
    }
    if (info.isSymbolicLink())
      throw Error("Migration input contains a symlink: " + directory);
    if (!info.isDirectory())
      throw Error("Migration input must be a directory: " + directory);
    for (const item of await readdir(directory, { withFileTypes: true })) {
      const file = path.join(directory, item.name),
        relative = path.relative(root, file);
      if (relative === ".state/writer.lock") continue;
      if (item.isSymbolicLink())
        throw Error("Migration input contains a symlink: " + file);
      if (item.isDirectory()) await walk(file);
      else if (item.isFile()) files[relative] = await readFile(file);
      else throw Error("Unsupported migration input: " + file);
    }
  }
  await walk(root);
  return files;
}

function inspectInput(
  root: string,
  files: Record<string, Buffer>,
  sources: any,
) {
  const kind = files["backup.json"] ? "backup" : "output";
  const saved = files[kind === "backup" ? "backup.json" : ".state/state.json"];
  const document = saved ? JSON.parse(saved.toString("utf8")) : null;
  const state = (kind === "backup" ? document?.state : document) || {
    pages: {},
    sources: {},
    pending: [],
  };
  if (!state.pages || !state.sources || !Array.isArray(state.pending))
    throw Error("Malformed migration state: " + root);
  const pages: any[] = Object.entries<any>(state.pages).map(([id, p]) => ({
    ...p,
    id,
    reasons: [],
  }));
  const byId = new Map<string, any>(pages.map((p) => [p.id, p]));
  for (const p of pages) {
    if (
      !/^(concepts|answers)\/[^/]+$/.test(p.id) ||
      p.id.includes("..") ||
      state.pages[p.id].id !== p.id ||
      !["concept", "answer"].includes(p.kind) ||
      !p.sourceVersions ||
      !p.pageVersions ||
      (p.kind === "answer" && !p.question?.trim())
    ) {
      p.reasons.push("malformed-page-record");
      continue;
    }
    const body = files["wiki/" + p.id + ".md"];
    if (!body || hash(body) !== p.hash)
      p.reasons.push("page-changed-or-missing");
    if (p.withdrawn) p.reasons.push("withdrawn");
    if (!Object.keys(p.sourceVersions).length)
      p.reasons.push("unknown-provenance");
    for (const [id, version] of Object.entries(p.sourceVersions)) {
      const old = state.sources[id],
        current = sources[id];
      if (!current) p.reasons.push("source-removed:" + id);
      else if (
        !old ||
        old.original !== current.original ||
        old.hash !== version
      )
        p.reasons.push("source-identity-or-version-unverified:" + id);
      else if (current.hash !== version) p.reasons.push("source-changed:" + id);
    }
    for (const [id, version] of Object.entries(p.pageVersions)) {
      const dep = byId.get(id);
      if (!dep || dep.hash !== version)
        p.reasons.push("page-dependency-version:" + id);
      for (const [source, h] of Object.entries(dep?.sourceVersions || {}))
        if (p.sourceVersions[source] !== h)
          p.reasons.push("incomplete-transitive-provenance:" + id);
    }
  }
  const visiting = new Set<string>(),
    done = new Set<string>();
  function visit(p: any) {
    if (done.has(p.id)) return;
    if (visiting.has(p.id)) {
      p.reasons.push("dependency-cycle");
      return;
    }
    visiting.add(p.id);
    for (const id of Object.keys(p.pageVersions || {})) {
      const dep = byId.get(id);
      if (dep) {
        visit(dep);
        if (dep.reasons.length) p.reasons.push("dependency-quarantined:" + id);
      }
    }
    visiting.delete(p.id);
    done.add(p.id);
  }
  for (const p of pages) visit(p);
  // Also propagates cycle invalidity to ancestors already visited in the cycle.
  let changed = true;
  while (changed) {
    changed = false;
    for (const p of pages.filter((p) => !p.reasons.length))
      if (
        Object.keys(p.pageVersions || {}).some(
          (id) => byId.get(id)?.reasons.length,
        )
      ) {
        p.reasons.push("dependency-quarantined");
        changed = true;
      }
  }
  const managed = new Set(pages.map((p) => "wiki/" + p.id + ".md"));
  managed.add("wiki/index.md");
  return {
    root,
    kind,
    status: saved
      ? "populated"
      : Object.keys(files).length
        ? "unmanaged"
        : "absent",
    context: state.context ?? document?.context,
    scope: state.scope ?? document?.scope,
    sources: state.sources,
    pending: state.pending,
    pages: pages.map((p) => ({ ...p, eligible: !p.reasons.length })),
    unmanaged: Object.keys(files).filter(
      (f) => f.startsWith("wiki/") && f.endsWith(".md") && !managed.has(f),
    ),
    files: Object.fromEntries(
      Object.entries(files).map(([f, body]) => [f, hash(body)]),
    ),
  };
}
export async function migrationInventory(config: any, roots: string[]) {
  if (!roots.length)
    throw Error("At least one --from output or backup directory is required");
  const sources = await scan(config),
    inputs = [];
  for (const root of [...new Set(roots.map((r) => path.resolve(r)))])
    inputs.push(inspectInput(root, await filesAt(root), sources));
  return { ok: true, inputs };
}

const overlap = (a: string, b: string) =>
  a === b || a.startsWith(b + path.sep) || b.startsWith(a + path.sep);
const checksums = (files: Record<string, Buffer>) =>
  Object.fromEntries(
    Object.entries(files)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([f, body]) => [f, hash(body)]),
  );
async function copyFiles(root: string, files: Record<string, Buffer>) {
  for (const [relative, body] of Object.entries(files)) {
    const file = path.join(root, relative);
    await mkdir(path.dirname(file), { recursive: true });
    await writeFile(file, body, { flag: "wx" });
  }
}

async function createSnapshot(
  config: any,
  roots: string[],
  destination: string,
) {
  const dest = path.resolve(destination);
  if (
    overlap(dest, config.output) ||
    roots.some((r) => overlap(r, dest) || overlap(r, config.output))
  )
    throw Error(
      "Migration inputs, snapshot and target must be separate directories",
    );
  for (const repo of config.repos)
    if (dest === repo.root || dest.startsWith(repo.root + path.sep))
      throw Error("Snapshot cannot be inside a source repository");
  await writableOutput({ output: dest });
  const existing = await json(path.join(dest, "manifest.json"), null);
  if (existing) {
    if (
      existing.version !== 1 ||
      existing.output !== config.output ||
      existing.context !== config.context
    )
      throw Error("Snapshot target mismatch");
    if (
      roots.length &&
      JSON.stringify(roots) !== JSON.stringify(existing.roots)
    )
      throw Error("Snapshot input mismatch");
    const files = await filesAt(dest);
    delete files["manifest.json"];
    if (JSON.stringify(checksums(files)) !== JSON.stringify(existing.files))
      throw Error("Snapshot checksum mismatch");
    return existing;
  }
  if (!roots.length) throw Error("New migration requires at least one --from");
  // Never reuse an incomplete snapshot: its bytes remain available for inspection.
  await mkdir(dest, { recursive: false });
  const all: Record<string, Buffer> = {},
    inputs = [];
  const sources = await scan(config);
  for (const [i, root] of roots.entries()) {
    const files = await filesAt(root);
    inputs.push(inspectInput(root, files, sources));
    for (const [f, body] of Object.entries(files))
      all[`inputs/${i}/${f}`] = body;
    const again = await filesAt(root);
    if (JSON.stringify(checksums(files)) !== JSON.stringify(checksums(again)))
      throw Error("Migration input changed during backup: " + root);
  }
  for (const [f, body] of Object.entries(await filesAt(config.output)))
    all["target/" + f] = body;
  await copyFiles(dest, all);
  if (
    JSON.stringify(checksums(await filesAt(dest))) !==
    JSON.stringify(checksums(all))
  )
    throw Error("Snapshot verification failed");
  const manifest = {
    version: 1,
    context: config.context,
    output: config.output,
    roots,
    inputs,
    files: checksums(all),
    created: new Date().toISOString(),
  };
  await writeJson(path.join(dest, "manifest.json"), manifest);
  return manifest;
}

async function snapshot(config: any, roots: string[], destination: string) {
  // Source writers are held only while copying. Backups and absent outputs are read-only.
  const ordered = [...roots].sort();
  async function lockNext(index: number): Promise<any> {
    if (index === ordered.length)
      return createSnapshot(config, roots, destination);
    const root = ordered[index];
    let active = false;
    try {
      await lstat(path.join(root, ".state"));
      active = true;
    } catch (e) {
      if ((e as any).code !== "ENOENT") throw e;
    }
    return active
      ? withWriter({ output: root }, () => lockNext(index + 1))
      : lockNext(index + 1);
  }
  return lockNext(0);
}

function remapBody(body: string, page: any, mapping: Map<string, any>) {
  // Preserve prose exactly. Only actual local page links and evidence-version suffixes change.
  return body.replace(
    /\[([^\]]+)\]\(([^)]+)\)( @ [a-f0-9]{64})?/g,
    (whole, label, target, version) => {
      if (/^(?:[a-z][a-z0-9+.-]*:|#)/i.test(target)) return whole;
      const [file, anchor] = target.replace(/^<|>$/g, "").split("#");
      let decoded;
      try {
        decoded = decodeURI(file);
      } catch {
        return whole;
      }
      const id = path.posix
        .normalize(path.posix.join(path.posix.dirname(page.id), decoded))
        .replace(/\.md$/, "");
      const resolved = mapping.get(id);
      if (!resolved) return whole;
      const relative = path.posix.relative(
        path.posix.dirname(page.id),
        resolved.id + ".md",
      );
      return `[${label}](${encodeURI(relative)}${anchor ? "#" + anchor : ""})${version ? " @ " + resolved.hash : ""}`;
    },
  );
}

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
  const roots = [...new Set(from.map((r) => path.resolve(r)))];
  const saved = await snapshot(config, roots, dest);
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
      await maintain(config);
      state = await readState(config);
      const sources = await scan(config),
        reports: any[] = [],
        inputs = [];
      for (const [i, root] of saved.roots.entries()) {
        const files = await filesAt(path.join(dest, "inputs", String(i)));
        const input = inspectInput(root, files, sources);
        inputs.push(input);
        const remaining = input.pages.filter((p) => p.eligible),
          mapping = new Map<string, any>();
        for (const p of input.pages.filter((p) => !p.eligible))
          reports.push({
            origin: root,
            id: p.id,
            action: "quarantined",
            reasons: p.reasons,
          });
        const ordered: any[] = [];
        while (remaining.length) {
          const p = remaining.find((p) =>
            Object.keys(p.pageVersions).every((id) => mapping.has(id)),
          );
          if (!p) throw Error("Unresolved migration dependency graph");
          remaining.splice(remaining.indexOf(p), 1);
          const dependencies = Object.fromEntries(
            Object.keys(p.pageVersions)
              .sort()
              .map((id) => [id, mapping.get(id).migration.revision]),
          );
          const revision = hash(
            JSON.stringify([
              p.id,
              p.hash,
              Object.entries(p.sourceVersions).sort(),
              dependencies,
            ]),
          );
          const id = p.id.split("/")[0] + "/import-" + revision;
          const page: any = {
            ...p,
            id,
            migration: {
              revision,
              originalId: p.id,
              originalHash: p.hash,
              snapshot: dest,
            },
          };
          delete page.reasons;
          delete page.eligible;
          const existing = state.pages[id];
          if (existing && existing.migration?.revision !== revision)
            throw Error("Migration page identity conflict: " + id);
          mapping.set(p.id, existing || page);
          ordered.push(p);
        }
        // Resolve all navigation targets first; dependency hashes are updated in topological order.
        for (const p of ordered) {
          const page = mapping.get(p.id),
            existing = state.pages[page.id];
          if (!existing) {
            page.pageVersions = Object.fromEntries(
              Object.keys(p.pageVersions).map((id) => [
                mapping.get(id).id,
                mapping.get(id).hash,
              ]),
            );
            const body = remapBody(
              files["wiki/" + p.id + ".md"].toString("utf8"),
              p,
              mapping,
            );
            progress.provisional.push({ id: page.id, hash: hash(body) });
            await writeJson(journal, progress);
            state.pages[page.id] = page;
            await publishPage(config, page, body);
          }
          reports.push({
            origin: root,
            id: p.id,
            target: page.id,
            originalHash: p.hash,
            hash: page.hash,
            action: existing ? "deduplicated" : "preserved",
          });
        }
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
    if (previous) await maintain(config);
    await qmd(config, "update");
    state = await readState(config);
    state.migrations[key].complete = true;
    state.pending = [];
    await saveState(config, state);
    await entry(config, state);
    await rm(journal, { force: true });
    return { ok: true, snapshot: dest, report: state.migrations[key].report };
  } catch (e) {
    await writeJson(journal, { ...progress, error: (e as Error).message });
    throw e;
  }
}
