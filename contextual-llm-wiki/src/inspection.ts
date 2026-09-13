import path from "node:path";
import { readFile, readdir, access } from "node:fs/promises";
import { createWiki } from "../.runtime/compiler/dist/index.js";
import { scan } from "./sources.ts";
import { readState, status } from "./state.ts";
import { hash } from "./storage.ts";
import { markdownProse } from "./markdown-prose.ts";
export async function source(config: any, id: string) {
  const state = await readState(config),
    record = state.sources[id];
  if (!record) throw Error("Unknown synchronized source identity");
  const current = await scan(config);
  if (current[id]?.hash !== record.hash)
    throw Error("Source is withdrawn or changed; maintenance required");
  const text = await readFile(
    path.join(config.output, ".state/compiler/sources", id),
    "utf8",
  );
  if (hash(text) !== record.hash)
    throw Error("Compiler source differs from checked original version");
  return { ok: true, ...record, text, lineOffset: 0 };
}
export async function lint(config: any) {
  const checked = await status(config);
  const upstream = await createWiki({
    root: path.join(config.output, ".state/compiler"),
  }).lint();
  const activeIssues: any[] = [];
  const state = await readState(config);
  for (const page of Object.values<any>(state.pages).filter(
    (p) => !p.withdrawn,
  )) {
    const file = path.join(config.output, "wiki", page.id + ".md");
    let body = "";
    try {
      body = await readFile(file, "utf8");
    } catch {
      activeIssues.push({ rule: "missing-page", page: page.id });
      continue;
    }
    const prose = markdownProse(body);
    for (const match of prose.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g)) {
      const target = match[2].replace(/^<|>$/g, "");
      if (/^(?:[a-z][a-z0-9+.-]*:|#)/i.test(target)) continue;
      try {
        await access(
          path.resolve(path.dirname(file), decodeURI(target.split("#")[0])),
        );
      } catch {
        activeIssues.push({ rule: "broken-link", page: page.id, target });
      }
    }
    for (const match of prose.matchAll(/\[\[([^\]]+)\]\]/g))
      activeIssues.push({
        rule: "unresolved-wikilink",
        page: page.id,
        target: match[1],
      });
  }
  const forbidden: string[] = [];
  async function inspect(dir: string) {
    let files;
    try {
      files = await readdir(dir, { withFileTypes: true });
    } catch (e) {
      if ((e as any).code === "ENOENT") return;
      throw e;
    }
    for (const f of files) {
      const file = path.join(dir, f.name);
      if (f.name === ".git" || /embedding|\.sqlite$|\.db$|vector/i.test(f.name))
        forbidden.push(file);
      if (f.isDirectory()) await inspect(file);
    }
  }
  await inspect(path.join(config.output, ".state/compiler"));
  const unresolvedCompilerErrors = upstream.results.filter(
    (r) => r.severity === "error" && r.rule !== "broken-wikilink",
  );
  return {
    ok:
      checked.review.length === 0 &&
      checked.pending.length === 0 &&
      forbidden.length === 0 &&
      activeIssues.length === 0 &&
      unresolvedCompilerErrors.length === 0,
    context: config.context,
    review: checked.review,
    pending: checked.pending,
    activeIssues,
    unresolvedCompilerErrors,
    upstream,
    compilerLinkSuggestions: upstream.results.filter(
      (r) => r.rule === "broken-wikilink",
    ).length,
    forbiddenStores: forbidden,
  };
}
