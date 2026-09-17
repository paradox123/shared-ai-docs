import { mkdir, open, readFile, readdir, rename, rm } from "node:fs/promises";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { execFileSync } from "node:child_process";
import { hash } from "./storage.ts";
import { compilerRoot, PIN } from "./runtime.ts";
import type { Source } from "./sources.ts";

type Request = {
  sourceFile: string;
  system: string;
  messages: { role: string; content: string }[];
  tools: unknown[];
};

// Include installed code (not just the upstream pin), so local prompt/schema,
// parsing, provider adapters and integration patch changes invalidate old work.
async function compilerDigest(dir: string): Promise<string> {
  const entries = await readdir(dir, { withFileTypes: true });
  const parts: string[] = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    if (entry.isDirectory())
      parts.push(
        entry.name + (await compilerDigest(path.join(dir, entry.name))),
      );
    else if (entry.name.endsWith(".js"))
      parts.push(entry.name + hash(await readFile(path.join(dir, entry.name))));
  }
  return hash(parts.join("\n"));
}

// Rename is atomic; fsync the complete file and its directory before reporting
// reusable progress. An interrupted temporary file is never a cache hit.
async function persist(file: string, value: unknown) {
  const dir = path.dirname(file);
  await mkdir(dir, { recursive: true, mode: 0o700 });
  const temporary = file + "." + randomUUID() + ".tmp";
  try {
    const fd = await open(temporary, "wx", 0o600);
    try {
      await fd.writeFile(JSON.stringify(value) + "\n");
      await fd.sync();
    } finally {
      await fd.close();
    }
    await rename(temporary, file);
    const directory = await open(dir, "r");
    try {
      await directory.sync();
    } finally {
      await directory.close();
    }
  } finally {
    await rm(temporary, { force: true });
  }
}

export async function extractionCache(
  config: any,
  sources: Record<string, Source>,
) {
  const provider = process.env.LLMWIKI_PROVIDER!;
  // Hash request-affecting settings only; never persist credentials or prompts.
  const settingNames = [
    "LLMWIKI_MAX_TOKENS",
    "LLMWIKI_OPENAI_TOKEN_PARAM",
    "LLMWIKI_OPENAI_REASONING_EFFORT",
    "LLMWIKI_OPENAI_EXTRA_BODY",
    "OPENAI_BASE_URL",
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_MODEL",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
    "AWS_REGION",
    "CLOUD_ML_REGION",
    "ANTHROPIC_VERTEX_PROJECT_ID",
  ];
  const settings = Object.fromEntries(
    settingNames.map((key) => [key, process.env[key]]),
  );
  const contract = hash(
    JSON.stringify({
      version: 1,
      pin: PIN,
      compiler: await compilerDigest(path.join(compilerRoot, "dist")),
      lock: hash(await readFile(path.join(compilerRoot, "package-lock.json"))),
      provider,
      settings,
      // Codex runs with --ignore-user-config. Its executable version determines
      // the default-model contract when no explicit model was selected.
      cli:
        provider === "codex-agent"
          ? execFileSync("codex", ["--version"], { encoding: "utf8" }).trim()
          : undefined,
    }),
  );
  const stats = { saved: 0, reused: 0, invalid: 0 };
  const run = async (
    request: Request,
    generate: () => Promise<string>,
    validate: (raw: string) => boolean,
  ) => {
    const source = sources[request.sourceFile];
    if (!source)
      throw Error("Unknown extraction source: " + request.sourceFile);
    const key = hash(
      JSON.stringify({
        contract,
        context: config.context,
        scope: config.scope,
        source: { id: source.id, original: source.original, hash: source.hash },
        request,
      }),
    );
    const file = path.join(config.output, ".state/extractions", key + ".json");
    try {
      const stored = JSON.parse(await readFile(file, "utf8"));
      if (
        stored &&
        stored.version === 1 &&
        stored.key === key &&
        typeof stored.raw === "string" &&
        stored.checksum === hash(stored.raw) &&
        validate(stored.raw)
      ) {
        stats.reused++;
        return stored.raw;
      }
      stats.invalid++;
    } catch (error: any) {
      if (error instanceof SyntaxError) stats.invalid++;
      else if (error.code !== "ENOENT")
        throw Object.assign(error, { sharedExtractionCache: true });
    }
    const raw = await generate();
    if (validate(raw)) {
      try {
        await persist(file, {
          version: 1,
          key,
          source: source.id,
          contract,
          raw,
          checksum: hash(raw),
        });
      } catch (error) {
        throw Object.assign(error as Error, { sharedExtractionCache: true });
      }
      stats.saved++;
    }
    return raw;
  };
  return { run, stats };
}
