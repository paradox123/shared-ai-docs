import path from "node:path";
import { lstat, readdir, readFile } from "node:fs/promises";
import { hash } from "./storage.ts";
import { scan } from "./sources.ts";

// A snapshot includes unmanaged notes and compiler state, not just active pages.
export async function filesAt(root: string): Promise<Record<string, Buffer>> {
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

export function inspectInput(
  root: string,
  files: Record<string, Buffer>,
  sources: any,
) {
  const kind = files["backup.json"] ? "backup" : "output";
  const saved = files[kind === "backup" ? "backup.json" : ".state/state.json"];
  const reasons: string[] = [];
  const record = (value: any) =>
    value && typeof value === "object" && !Array.isArray(value);
  let document: any = null;
  try {
    document = saved ? JSON.parse(saved.toString("utf8")) : null;
  } catch {
    reasons.push("malformed-state-json");
  }
  let state = kind === "backup" ? document?.state : document;
  if (
    saved &&
    !reasons.length &&
    (!record(state) ||
      !record(state.pages) ||
      !record(state.sources) ||
      !Array.isArray(state.pending))
  )
    reasons.push("malformed-state-record");
  if (!saved || reasons.length) state = { pages: {}, sources: {}, pending: [] };
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
      state.pages[p.id]?.id !== p.id ||
      !["concept", "answer"].includes(p.kind) ||
      !record(p.sourceVersions) ||
      !record(p.pageVersions) ||
      (p.kind === "answer" &&
        (typeof p.question !== "string" || !p.question.trim()))
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
    reasons,
    status: reasons.length
      ? "invalid-state"
      : saved
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
