import path from "node:path";
import { readFile } from "node:fs/promises";
import { hash } from "./storage.ts";
export function initialConfig(vault: string, output: string) {
  const roots = {
    "vault-root": ".",
    "meeting-assistant": "_ops/meeting-assistant",
    "shared-ai-docs": "_shared/shared-ai-docs",
    "ki-fuer-kmu": "ki-fuer-kmu",
    "ncg-docs": "ncg/ncg-docs",
    private: "private",
    "probare-crm": "probare-crm",
    sparkle: "sparkle",
  };
  return {
    version: 1,
    context: "common",
    scope: "common",
    vault,
    output,
    repos: Object.entries(roots).map(([id, root]) => ({
      id,
      root: path.resolve(vault, root),
      domain: id === "private" ? "private" : "professional",
      include:
        id === "vault-root"
          ? [
              "*.md",
              "_ops/docs/**/*.md",
              "_ops/codex-global/**/*.md",
              "_shared/danielsvault-rag/**/*.md",
              "_shared/n8n/**/*.md",
              "Meetings/**/*.md",
              "Projects/**/*.md",
            ]
          : ["**/*.md"],
      exclude: [],
    })),
    excludedCheckouts: [
      "_shared/shared-ai-docs-ticket-08",
      "ki-fuer-kmu/.safe-test/**",
      "_shared/SpecOps/**",
    ],
  };
}
export async function loadConfig(file: string) {
  if (!file) throw Error("--config is required");
  const raw = await readFile(file, "utf8");
  const c = JSON.parse(raw);
  c.configFile = path.resolve(file);
  c.configHash = hash(raw);
  if (
    c.version !== 1 ||
    !/^[a-z0-9][a-z0-9-]*$/.test(c.context) ||
    !Array.isArray(c.repos)
  )
    throw Error("Invalid context configuration");
  c.scope ||= "common";
  if (c.scope !== "common")
    throw Error(
      "Legacy scope: create a common configuration with a fresh output; existing knowledge requires verified migration",
    );
  c.output = path.resolve(path.dirname(file), c.output);
  const ids = new Set();
  for (const r of c.repos) {
    if (!/^[a-z0-9][a-z0-9-]*$/.test(r.id) || ids.has(r.id))
      throw Error("Duplicate or invalid repository identity");
    ids.add(r.id);
    r.scope ||= "general";
    if (!["general", "private"].includes(r.scope))
      throw Error("Invalid repository scope: " + r.id);
    for (const field of ["include", "exclude", "privateInclude"]) {
      r[field] ||= [];
      if (
        !Array.isArray(r[field]) ||
        !r[field].every((p: unknown) => typeof p === "string")
      )
        throw Error("Invalid Markdown filters: " + r.id);
    }
    r.root = path.resolve(path.dirname(file), r.root);
    if (c.output === r.root || r.root.startsWith(c.output + path.sep))
      throw Error("Output cannot own a source root");
  }
  return c;
}

export async function checkConfig(config: any) {
  if (
    config.configFile &&
    hash(await readFile(config.configFile, "utf8")) !== config.configHash
  )
    throw Error("Context configuration changed during processing");
}
