// Internal half of rollout-with-locks.py: the standard wiki writer lock remains
// owned for the whole supplied deployment operation; it does not run maintenance.
import { readFile } from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";
import { withWriter } from "../src/lock.ts";
const [configPath, ...command] = process.argv.slice(2);
if (!configPath || !command.length)
  throw Error("Config and rollout command required");
const config = JSON.parse(await readFile(configPath, "utf8"));
config.output = path.resolve(path.dirname(configPath), config.output);
await withWriter(config, async () => {
  const code = await new Promise<number>((resolve, reject) => {
    const child = spawn(command[0], command.slice(1), { stdio: "inherit" });
    child.on("error", reject);
    child.on("close", (code) => resolve(code ?? 1));
  });
  process.exitCode = code;
});
