import path from "node:path";
import { lstat, mkdir, writeFile } from "node:fs/promises";
import { hash, json, writeJson } from "./storage.ts";
import { scan } from "./sources.ts";
import { writableOutput, withWriter } from "./lock.ts";
import { filesAt, inspectInput } from "./migration-input.ts";

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

export async function snapshot(
  config: any,
  roots: string[],
  destination: string,
) {
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
