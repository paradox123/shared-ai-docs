import { test } from "node:test";
import assert from "node:assert/strict";
import { writeFile, readFile, access } from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";
import { fixture } from "./support.ts";
test(
  "rollout holds both maintenance and direct wiki writer ownership before touching the deployment",
  { timeout: 15000 },
  async () => {
    const f = await fixture();
    const lock = path.join(f.dir, "maintenance.lock");
    const entered = path.join(f.dir, "entered");
    const release = path.join(f.dir, "release");
    const operation = path.join(f.dir, "operation.py");
    await writeFile(
      operation,
      `import pathlib,time\npathlib.Path(${JSON.stringify(entered)}).write_text('locked')\nend=time.monotonic()+8\nwhile not pathlib.Path(${JSON.stringify(release)}).exists() and time.monotonic()<end: time.sleep(.03)\n`,
    );
    const run = (script: string, args: string[]) =>
      new Promise<any>((resolve, reject) => {
        const p = spawn(
          "python3",
          [new URL("../scripts/" + script, import.meta.url).pathname, ...args],
          { env: { ...process.env, ...f.env } },
        );
        let out = "",
          err = "";
        p.stdout.on("data", (b) => (out += b));
        p.stderr.on("data", (b) => (err += b));
        p.on("error", reject);
        p.on("close", (code) => {
          try {
            resolve({
              code,
              ...JSON.parse(out.trim().split("\n").at(-1)!),
              stderr: err,
            });
          } catch {
            reject(Error(out + err));
          }
        });
      });
    try {
      const owned = run("rollout-with-locks.py", [
        "--config",
        f.configPath,
        "--lock-file",
        lock,
        "--artifacts",
        path.join(f.dir, "rollout"),
        "--",
        "python3",
        operation,
      ]);
      const deadline = Date.now() + 4000;
      while (
        !(await access(entered).then(
          () => true,
          () => false,
        ))
      ) {
        assert.ok(Date.now() < deadline);
        await new Promise((r) => setTimeout(r, 30));
      }
      const direct = await f.run("maintain");
      assert.equal(direct.ok, false);
      assert.match(direct.error, /locked by writer/);
      const scheduled = await run("run-maintenance.py", [
        "--config",
        f.configPath,
        "--lock-file=" + lock,
        "--artifacts",
        path.join(f.dir, "contender"),
        "--qmd",
        "/usr/bin/true",
        "--reconcile",
        "/dev/null",
      ]);
      assert.equal(scheduled.ok, false);
      assert.match(scheduled.report.error, /Resource temporarily unavailable/);
      assert.equal(f.calls.length, 0);
      await writeFile(release, "");
      const result = await owned;
      assert.equal(result.ok, true, JSON.stringify(result));
      assert.equal(
        await access(path.join(f.config.output, ".state/writer.lock")).then(
          () => true,
          () => false,
        ),
        false,
      );
      await writeFile(
        path.join(f.dir, "rollout-locks.json"),
        JSON.stringify({ result, direct, scheduled }, null, 2),
      );
      console.log("Rollout locking evidence: " + f.dir);
    } finally {
      await writeFile(release, "");
      await f.close();
    }
  },
);
