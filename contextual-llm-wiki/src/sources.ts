import { readdir, readFile, lstat, realpath } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { minimatch } from "minimatch";
import { hash } from "./storage.ts";
export type Source = {
  id: string;
  repo: string;
  relative: string;
  original: string;
  hash: string;
  commit: string;
  text: string;
};
export const excludedNames = new Set(
  ".git .obsidian node_modules .venv venv __pycache__ .cache .next .safe-test .scratch .tmp tmp temp .worktrees worktrees dist build bin obj coverage test-results playwright-report runtime .runtime logs .logs .local .rag .llmwiki .n8n n8n_data data backups .trash".split(
    " ",
  ),
);
const matches = (file: string, patterns: string[] = []) =>
  patterns.some((p) => minimatch(file, p, { dot: true, nocase: true }));
export async function inventory(config: any, includeText = false) {
  const sources: Record<string, Source> = {},
    repositories: any[] = [],
    commonDirs = new Set();
  for (const repo of config.repos) {
    const report: any = {
      id: repo.id,
      root: repo.root,
      include: [...repo.include, ...repo.privateInclude],
      exclude: repo.exclude,
      count: 0,
      missing: false,
      excluded: [],
      zones: {},
    };
    repositories.push(report);
    let rootStat;
    try {
      rootStat = await lstat(repo.root);
    } catch (e) {
      if ((e as any).code === "ENOENT") {
        report.missing = true;
        continue;
      }
      throw e;
    }
    if (rootStat.isSymbolicLink() || !rootStat.isDirectory())
      throw Error(`Incomplete scan: ${repo.id} root is not a real directory`);
    const git = (args: string[]) =>
      execFileSync("git", ["-C", repo.root, ...args], {
        encoding: "utf8",
        stdio: ["ignore", "pipe", "ignore"],
      }).trim();
    const root = git(["rev-parse", "--show-toplevel"]);
    if ((await realpath(root)) !== (await realpath(repo.root)))
      throw Error(`Incomplete scan: ${repo.id} is not its configured Git root`);
    const common = path.resolve(
      repo.root,
      git(["rev-parse", "--git-common-dir"]),
    );
    if (commonDirs.has(common))
      throw Error(`Duplicate checkout for ${repo.id}`);
    commonDirs.add(common);
    let commit = "unborn";
    try {
      commit = git(["rev-parse", "HEAD"]);
    } catch {}
    async function walk(dir: string) {
      for (const entry of await readdir(dir, { withFileTypes: true })) {
        const file = path.join(dir, entry.name),
          relative = path.relative(repo.root, file);
        const omit = (reason: string) =>
          report.excluded.push({ path: relative, reason });
        if (
          file === config.output ||
          file.startsWith(config.output + path.sep)
        ) {
          omit("generated-output");
          continue;
        }
        if (entry.isSymbolicLink()) {
          omit("symlink");
          continue;
        }
        if (entry.isDirectory()) {
          if (excludedNames.has(entry.name.toLowerCase())) {
            omit("runtime-filter");
            continue;
          }
          try {
            await lstat(path.join(file, ".git"));
            omit("nested-repository");
            continue;
          } catch (e) {
            if ((e as any).code !== "ENOENT") throw e;
          }
          // Vault zones are selected explicitly; prune unrelated subtrees before reading them.
          if (
            !report.include.some(
              (p: string) =>
                p.startsWith("**") ||
                p.startsWith(relative + "/") ||
                relative.startsWith(p.split("*")[0].replace(/\/$/, "")),
            )
          ) {
            omit("outside-included-zones");
            continue;
          }
          await walk(file);
        } else if (entry.isFile() && relative.toLowerCase().endsWith(".md")) {
          if (
            !matches(relative, report.include) ||
            matches(relative, report.exclude)
          )
            continue;
          report.count++;
          const zone = ["Meetings", "Projects/Private", "Projects"].find((z) =>
            relative.startsWith(z + "/"),
          );
          if (zone) report.zones[zone] = (report.zones[zone] || 0) + 1;
          const text = await readFile(file, "utf8"),
            id = repo.id + "/" + relative;
          sources[id] = {
            id,
            repo: repo.id,
            relative,
            original: file,
            hash: hash(text),
            commit,
            text,
          };
        }
      }
    }
    await walk(repo.root);
  }
  const report = {
    ok: true,
    context: config.context,
    scope: config.scope,
    selectedSources: Object.keys(sources).length,
    repositories,
    technicalExclusions: [...excludedNames],
    excludedCheckouts: config.excludedCheckouts || [],
  };
  return includeText ? { ...report, sources } : report;
}
export async function scan(config: any): Promise<Record<string, Source>> {
  const result = await inventory(config, true);
  const missing = result.repositories.filter((repo: any) => repo.missing);
  if (missing.length)
    throw Error(
      "Incomplete scan: configured roots unavailable: " +
        missing.map((repo: any) => repo.id).join(", "),
    );
  return (result as any).sources;
}
