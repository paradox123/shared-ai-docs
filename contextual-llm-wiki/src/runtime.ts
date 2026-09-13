import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
const release = JSON.parse(
  readFileSync(new URL("../compiler-release.json", import.meta.url), "utf8"),
);
export const PIN: string = release.commit;
export const compilerRoot = new URL("../.runtime/compiler/", import.meta.url)
  .pathname;
export function releaseIdentity() {
  const commit = execFileSync(
    "git",
    ["-C", compilerRoot, "rev-parse", "HEAD"],
    {
      encoding: "utf8",
    },
  ).trim();
  if (commit !== PIN)
    throw Error("Compiler pin mismatch; run scripts/bootstrap.sh");
  return {
    ok: true,
    repository: release.repository,
    release: release.release,
    commit,
    wrapper: new URL("../", import.meta.url).pathname.replace(/\/$/, ""),
    compilerRoot,
    node: process.execPath,
    runtime: process.versions.node,
  };
}
export function preflight() {
  if (process.versions.node !== "24.16.0")
    throw Error("Runtime: run scripts/bootstrap.sh to install Node 24.16.0");
  releaseIdentity();
  const provider = process.env.LLMWIKI_PROVIDER || "codex-agent";
  process.env.LLMWIKI_PROVIDER = provider;
  process.env.LLMWIKI_OUTPUT_LANG ||= "de";
  if (provider === "openai") {
    if (!process.env.OPENAI_API_KEY?.trim())
      throw Error("Provider unavailable: OPENAI_API_KEY required");
  } else if (provider === "claude-agent") {
    const auth = JSON.parse(
      execFileSync("claude", ["auth", "status"], { encoding: "utf8" }),
    );
    if (!auth.loggedIn)
      throw Error("Provider unavailable: run claude auth login");
  } else if (provider === "codex-agent") {
    execFileSync("codex", ["login", "status"], { stdio: "pipe" });
  } else
    throw Error(
      "Managed providers: claude-agent, codex-agent, openai (including compatible endpoints)",
    );
  return {
    runtime: process.versions.node,
    compiler: PIN,
    version: release.release.replace(/^v/, ""),
    provider,
    model: process.env.LLMWIKI_MODEL || "provider default",
    embeddings: false,
  };
}
