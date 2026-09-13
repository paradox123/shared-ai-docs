import path from "node:path";
import os from "node:os";
import { execFileSync, spawn } from "node:child_process";
import { mkdir } from "node:fs/promises";
import { writeJson } from "./storage.ts";
export const collectionName = (c: any) => "contextual-wiki-" + c.context;
export async function runProcess(
  command: string,
  args: string[],
  input?: string,
  env: any = process.env,
): Promise<string> {
  return await new Promise((resolve, reject) => {
    const p = spawn(command, args, { env, stdio: ["pipe", "pipe", "pipe"] });
    let out = "",
      err = "";
    p.stdout.on("data", (b) => (out += b));
    p.stderr.on("data", (b) => (err += b));
    p.on("error", reject);
    p.on("close", (code) =>
      code === 0
        ? resolve(out)
        : reject(Error(`${command} failed (${code}): ${out || err}`)),
    );
    p.stdin.end(input);
  });
}
export async function qmd(config: any, operation: string, question?: string) {
  const q = config.qmd || {};
  const root = path.join(config.output, "wiki");
  await mkdir(root, { recursive: true });
  const env = {
    ...process.env,
    PATH: process.env.WIKI_QMD_PATH || process.env.PATH,
  };
  const npmRoot = q.module
    ? null
    : execFileSync("npm", ["root", "-g"], { env, encoding: "utf8" }).trim();
  const module = q.module || path.join(npmRoot!, "@tobilu/qmd/dist/index.js");
  const node =
    q.node || execFileSync("which", ["node"], { env, encoding: "utf8" }).trim();
  if ((operation === "update" || operation === "register") && !q.isolated) {
    const manifest = path.join(config.output, ".state/qmd-collections.json");
    await writeJson(manifest, {
      version: 1,
      collections: [
        {
          name: collectionName(config),
          path: root,
          pattern: "**/*.md",
          scopes: ["wiki", config.context],
          private: config.scope === "private",
        },
      ],
    });
    const script =
      q.reconcileScript ||
      path.join(
        config.vault,
        "_shared/danielsvault-rag/scripts/sync-qmd-collections.py",
      );
    await runProcess(q.python || "python3", [script, "--apply"], undefined, {
      ...env,
      QMD_COLLECTION_MANIFEST: manifest,
    });
    if (config.scope === "private")
      await runProcess(
        "qmd",
        ["collection", "exclude", collectionName(config)],
        undefined,
        env,
      );
  }
  if (operation === "register") return { registered: true };
  const dbPath =
    q.dbPath ||
    process.env.INDEX_PATH ||
    path.join(
      process.env.XDG_CACHE_HOME || path.join(os.homedir(), ".cache"),
      "qmd/index.sqlite",
    );
  const raw = await runProcess(
    node,
    [new URL("../scripts/qmd-bridge.mjs", import.meta.url).pathname],
    JSON.stringify({
      operation,
      module,
      dbPath,
      isolated: q.isolated,
      root,
      collection: collectionName(config),
      question,
    }),
    env,
  );
  const result = JSON.parse(raw);
  if (!result.ok) throw Error(result.error);
  return result.result;
}
