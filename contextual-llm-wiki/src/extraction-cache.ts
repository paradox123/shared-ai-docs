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

type PageRequest = {
  slug: string;
  sourceFiles: string[];
  model: string;
  rebuild: boolean;
  system: string;
  messages: { role: string; content: string }[];
};

type CacheStats = { saved: number; reused: number; invalid: number };
type CacheFailure = "sharedExtractionCache" | "sharedPageCache";

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

async function readReusableResponse(
  file: string,
  key: string,
  validate: (raw: string) => boolean,
  stats: CacheStats,
  notify: () => void,
  failure: CacheFailure,
): Promise<string | undefined> {
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
      notify();
      return stored.raw;
    }
    stats.invalid++;
  } catch (error: any) {
    if (error instanceof SyntaxError) stats.invalid++;
    else if (error.code !== "ENOENT")
      throw Object.assign(error, { [failure]: true });
  }
  return undefined;
}

async function saveValidatedResponse(
  file: string,
  key: string,
  contract: string,
  raw: string,
  validate: (raw: string) => boolean,
  stats: CacheStats,
  notify: () => void,
  failure: CacheFailure,
  metadata: Record<string, unknown> = {},
): Promise<void> {
  if (!validate(raw)) return;
  try {
    await persist(file, {
      version: 1,
      key,
      ...metadata,
      contract,
      raw,
      checksum: hash(raw),
    });
  } catch (error) {
    throw Object.assign(error as Error, { [failure]: true });
  }
  stats.saved++;
  notify();
}

// This compiler patch changes only page generation, not extraction prompts or
// schemas. Preserve validated extraction work from the immediately prior
// production compiler build, and no other compiler revision.
const PREVIOUS_EXTRACTION_COMPILER =
  "3e73d5bf221276d6a9b1cd7521a378375b06dea12f605008883e13fadbc9bb74";
const PAGE_CACHE_COMPILER =
  "48c07885fa82636b6914059eff6fd22f4547391133fb2dbf8c498e889822fb2b";

async function modelContract(compiler?: string) {
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
  return hash(
    JSON.stringify({
      version: 1,
      pin: PIN,
      compiler: compiler || await compilerDigest(path.join(compilerRoot, "dist")),
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
}

export async function extractionCache(
  config: any,
  sources: Record<string, Source>,
  notify: () => void = () => {},
) {
  const installedCompiler = await compilerDigest(path.join(compilerRoot, "dist"));
  const contract = await modelContract(installedCompiler);
  const compatibleContract = installedCompiler === PAGE_CACHE_COMPILER
    ? await modelContract(PREVIOUS_EXTRACTION_COMPILER)
    : undefined;
  const stats = { saved: 0, reused: 0, invalid: 0 };
  const run = async (
    request: Request,
    generate: () => Promise<string>,
    validate: (raw: string) => boolean,
  ) => {
    const source = sources[request.sourceFile];
    if (!source)
      throw Error("Unknown extraction source: " + request.sourceFile);
    // A queued request may reach the cache long after the initial scan. Never
    // label its old snapshot reusable after the authoritative original changed.
    let current: string;
    try {
      current = await readFile(source.original, "utf8");
    } catch (error) {
      throw Error("Extraction source unavailable before reuse: " + source.id, {
        cause: error,
      });
    }
    if (hash(current) !== source.hash)
      throw Error("Source changed before extraction reuse: " + source.id);
    const keyFor = (candidateContract: string) => hash(
      JSON.stringify({
        contract: candidateContract,
        context: config.context,
        scope: config.scope,
        source: { id: source.id, original: source.original, hash: source.hash },
        request,
      }),
    );
    const key = keyFor(contract);
    for (const candidateKey of [key, ...(compatibleContract ? [keyFor(compatibleContract)] : [])]) {
      const candidateFile = path.join(config.output, ".state/extractions", candidateKey + ".json");
      const cached = await readReusableResponse(
        candidateFile,
        candidateKey,
        validate,
        stats,
        notify,
        "sharedExtractionCache",
      );
      if (cached !== undefined) return cached;
    }
    const raw = await generate();
    const file = path.join(config.output, ".state/extractions", key + ".json");
    await saveValidatedResponse(
      file,
      key,
      contract,
      raw,
      validate,
      stats,
      notify,
      "sharedExtractionCache",
      { source: source.id },
    );
    return raw;
  };
  return { run, stats };
}

export async function pageResponseCache(
  config: any,
  sources: Record<string, Source>,
  publicationVersion: number | undefined,
  notify: () => void = () => {},
) {
  const contract = await modelContract();
  const stats = { saved: 0, reused: 0, invalid: 0 };
  const run = async (
    request: PageRequest,
    generate: () => Promise<string>,
    validate: (raw: string) => boolean,
  ) => {
    const evidence = [];
    for (const id of request.sourceFiles) {
      const source = sources[id];
      if (!source)
        throw Object.assign(Error("Unknown page source: " + id), { sharedPageCache: true });
      let current: string;
      try {
        current = await readFile(source.original, "utf8");
      } catch {
        // A missing original invalidates reuse; the full inventory check reports
        // the incomplete source tree before publication.
        return generate();
      }
      if (hash(current) !== source.hash)
        // Never reuse or save an answer against an outdated scan snapshot.
        return generate();
      evidence.push({ id, original: source.original, hash: source.hash });
    }
    const key = hash(JSON.stringify({
      contract,
      context: config.context,
      scope: config.scope,
      publicationVersion,
      evidence,
      request,
    }));
    const file = path.join(config.output, ".state/page-responses", key + ".json");
    const cached = await readReusableResponse(
      file,
      key,
      validate,
      stats,
      notify,
      "sharedPageCache",
    );
    if (cached !== undefined) return cached;
    const raw = await generate();
    await saveValidatedResponse(
      file,
      key,
      contract,
      raw,
      validate,
      stats,
      notify,
      "sharedPageCache",
    );
    return raw;
  };
  return { run, stats };
}
