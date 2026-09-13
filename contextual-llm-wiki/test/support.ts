import { spawn, execFileSync } from "node:child_process";
import {
  mkdtemp,
  writeFile,
  mkdir,
  readFile,
  realpath,
} from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import http from "node:http";
export async function invoke(
  args: string[],
  env: Record<string, string> = {},
  onSpawn?: (pid: number) => void,
) {
  return await new Promise<any>((resolve, reject) => {
    const p = spawn(
      process.execPath,
      [new URL("../src/cli.ts", import.meta.url).pathname, ...args],
      { env: { ...process.env, ...env } },
    );
    onSpawn?.(p.pid!);
    let out = "",
      err = "";
    p.stdout.on("data", (b) => (out += b));
    p.stderr.on("data", (b) => (err += b));
    p.on("error", reject);
    p.on("close", (code) => {
      try {
        resolve({ code, ...JSON.parse(out.trim()), stderr: err });
      } catch {
        reject(Error(out + "\n" + err));
      }
    });
  });
}
export async function fixture() {
  const dir = await realpath(
    await mkdtemp(path.join(os.tmpdir(), "wiki-behavior-")),
  );
  for (const repo of ["alpha", "beta"]) {
    await mkdir(path.join(dir, repo));
    execFileSync("git", ["init", "-q", path.join(dir, repo)]);
    execFileSync("git", [
      "-C",
      path.join(dir, repo),
      "-c",
      "user.name=Wiki Test",
      "-c",
      "user.email=wiki@example.invalid",
      "commit",
      "--allow-empty",
      "-qm",
      "fixture",
    ]);
  }
  await writeFile(
    path.join(dir, "alpha/README.md"),
    "# Freigabe\n\nAlpha verlangt zwei Freigaben.\n",
  );
  await writeFile(
    path.join(dir, "beta/README.md"),
    "# Freigabe\n\nBeta verlangt drei Freigaben.\n",
  );
  const config = {
    version: 1,
    context: "test",
    qmd: { isolated: true, dbPath: path.join(dir, "qmd.sqlite") },
    output: path.join(dir, "output"),
    repos: ["alpha", "beta"].map((id) => ({
      id,
      root: path.join(dir, id),
      include: ["**/*.md"],
      exclude: [],
      scope: "general",
    })),
  };
  const configPath = path.join(dir, "config.json");
  await writeFile(configPath, JSON.stringify(config));
  let calls: any[] = [];
  let failure = false;
  let delay = 0;
  const server = http.createServer(async (req, res) => {
    let raw = "";
    for await (const part of req) raw += part;
    const body = JSON.parse(raw);
    calls.push(body);
    if (delay) await new Promise((r) => setTimeout(r, delay));
    if (failure) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(
        JSON.stringify({ error: { message: "controlled provider failure" } }),
      );
      return;
    }
    const prompt = body.messages.map((m: any) => m.content).join("\n");
    let message: any;
    if (body.tools) {
      const source = prompt.split("--- SOURCE DOCUMENT ---")[1] || "";
      const control = source.includes("Kontrollseite");
      const concept = control ? "Kontrollseite" : "Freigabe";
      message = {
        role: "assistant",
        tool_calls: [
          {
            id: "call_test",
            type: "function",
            function: {
              name: "extract_concepts",
              arguments: JSON.stringify({
                concepts: [
                  {
                    concept,
                    summary: concept,
                    is_new: true,
                    confidence: 1,
                    provenance_state: "extracted",
                  },
                ],
              }),
            },
          },
        ],
      };
    } else {
      const material =
        prompt.split("--- SOURCE MATERIAL ---")[1] ||
        prompt.split("--- EVIDENCE ---")[1] ||
        "";
      const facts = [
        ...new Set(
          material.match(
            /(?:Alpha|Beta) verlangt (?:zwei|drei|vier) Freigaben\./g,
          ) || [],
        ),
      ];
      const sources = [...material.matchAll(/--- SOURCE: (.*?) ---/g)].map(
        (m) => m[1],
      );
      const control = prompt.includes('about "Kontrollseite"');
      const text = control
        ? "# Kontrollseite\n\nUnabhängige Kontrollseite."
        : "# Freigabe\n\n" +
          facts.join(" ") +
          "\n\nSynthese: Beide Repos verlangen eine explizite Freigabe; ihre Anzahl unterscheidet sich.";
      message = {
        role: "assistant",
        content:
          text + "\n\n" + sources.map((s) => `Beleg ^[${s}:3-3]`).join("\n\n"),
      };
    }
    if (body.stream) {
      res.writeHead(200, { "Content-Type": "text/event-stream" });
      res.end(
        "data: " +
          JSON.stringify({
            choices: [{ delta: { content: message.content } }],
          }) +
          "\n\ndata: [DONE]\n\n",
      );
    } else {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(
        JSON.stringify({
          id: "local-test",
          object: "chat.completion",
          choices: [{ index: 0, message, finish_reason: "stop" }],
        }),
      );
    }
  });
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  const env = {
    LLMWIKI_PROVIDER: "openai",
    OPENAI_API_KEY: "local-test-only",
    OPENAI_BASE_URL: `http://127.0.0.1:${(server.address() as any).port}/v1`,
    LLMWIKI_MODEL: "test-model",
  };
  return {
    dir,
    config,
    configPath,
    env,
    calls,
    fail: (value: boolean) => (failure = value),
    delay: (ms: number) => (delay = ms),
    close: () => new Promise<void>((r) => server.close(() => r())),
    run: (command: string, ...args: string[]) =>
      invoke([command, "--config", configPath, ...args], env),
    saveConfig: () => writeFile(configPath, JSON.stringify(config)),
  };
}
