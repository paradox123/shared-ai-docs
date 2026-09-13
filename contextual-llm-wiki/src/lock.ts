import path from "node:path";
import { open, mkdir, readFile, rm, lstat, readdir } from "node:fs/promises";
import { execFileSync } from "node:child_process";
export async function writableOutput(config: any) {
  let cursor = path.resolve(config.output);
  while (true) {
    try {
      const info = await lstat(cursor);
      if (info.isSymbolicLink())
        throw Error("Managed output must not traverse symlinks: " + cursor);
    } catch (e) {
      if ((e as any).code !== "ENOENT") throw e;
    }
    if (path.dirname(cursor) === cursor) break;
    cursor = path.dirname(cursor);
  }
  const inspect = async (directory: string): Promise<void> => {
    let items;
    try {
      items = await readdir(directory, { withFileTypes: true });
    } catch (e) {
      if ((e as any).code === "ENOENT") return;
      throw e;
    }
    for (const item of items) {
      const file = path.join(directory, item.name);
      if (item.isSymbolicLink())
        throw Error("Managed output contains a symlink: " + file);
      if (item.isDirectory()) await inspect(file);
    }
  };
  await inspect(config.output);
  try {
    await lstat(path.join(config.output, ".git"));
    throw Error("Wiki output must not have a Git root");
  } catch (e) {
    if ((e as any).code !== "ENOENT") throw e;
  }
  // Any existing tracked ownership under the output is a configuration error.
  let parent = config.output;
  while (true) {
    try {
      await lstat(parent);
      break;
    } catch (e) {
      if ((e as any).code !== "ENOENT") throw e;
      parent = path.dirname(parent);
    }
  }
  let root = "";
  try {
    root = execFileSync("git", ["-C", parent, "rev-parse", "--show-toplevel"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {}
  if (root) {
    const files = execFileSync(
      "git",
      ["-C", root, "ls-files", "--", path.relative(root, config.output)],
      { encoding: "utf8" },
    );
    if (files.trim()) throw Error("Output overlaps tracked source ownership");
    try {
      execFileSync(
        "git",
        ["-C", root, "check-ignore", "--quiet", config.output],
        { stdio: "pipe" },
      );
    } catch {
      throw Error("Output inside Git must already be ignored");
    }
  }
}
export async function withWriter(
  config: any,
  operation: () => Promise<any>,
  options: { migration?: boolean } = {},
) {
  await writableOutput(config);
  await mkdir(path.join(config.output, ".state"), { recursive: true });
  const file = path.join(config.output, ".state/writer.lock");
  let handle;
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      handle = await open(file, "wx");
      break;
    } catch (e) {
      if ((e as any).code !== "EEXIST") throw e;
      let pid;
      try {
        pid = JSON.parse(await readFile(file, "utf8")).pid;
      } catch {
        throw Error(
          "Context locked: incomplete writer lock; inspect owner before removing it",
        );
      }
      if (!Number.isSafeInteger(pid) || pid < 1)
        throw Error("Context locked: invalid writer owner");
      try {
        process.kill(pid, 0);
        throw Error("Context locked by writer " + pid);
      } catch (err) {
        if ((err as any).code !== "ESRCH") throw err;
      }
      await rm(file);
    }
  }
  if (!handle) throw Error("Context locked by another writer");
  await handle.writeFile(
    JSON.stringify({ pid: process.pid, started: new Date().toISOString() }),
  );
  try {
    if (!options.migration) {
      try {
        const pending = JSON.parse(
          await readFile(
            path.join(config.output, ".state/migration-pending.json"),
            "utf8",
          ),
        );
        throw Error(
          "Resume pending migration with migrate --snapshot " +
            pending.snapshot,
        );
      } catch (e) {
        if ((e as any).code !== "ENOENT") throw e;
      }
    }
    return await operation();
  } finally {
    await handle.close();
    await rm(file, { force: true });
  }
}
