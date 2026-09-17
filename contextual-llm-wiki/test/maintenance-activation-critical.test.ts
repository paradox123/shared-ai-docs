import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn, execFileSync } from "node:child_process";
import { writeFile, readFile, access } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";
async function until(check: () => Promise<boolean> | boolean, timeout = 4000) {
  const end = Date.now() + timeout;
  while (!(await check())) {
    assert.ok(Date.now() < end, "bounded critical observation");
    await new Promise((r) => setTimeout(r, 20));
  }
}
const alive = (pid: number) => {
  const row = execFileSync("/bin/ps", ["-axo", "pid=,stat="], {
    encoding: "utf8",
  })
    .split("\n")
    .find((r) => Number(r.trim().split(/\s+/)[0]) === pid);
  return !!row && !row.trim().split(/\s+/)[1].startsWith("Z");
};
function invoke(script: string, args: string[], env: any) {
  const child = spawn(
    "python3",
    [new URL("../scripts/" + script, import.meta.url).pathname, ...args],
    { env: { ...process.env, ...env } },
  );
  let stdout = "",
    stderr = "";
  child.stdout.on("data", (b) => (stdout += b));
  child.stderr.on("data", (b) => (stderr += b));
  const started = Date.now();
  return {
    child,
    done: new Promise<any>((resolve, reject) => {
      child.on("error", reject);
      child.on("close", (code, signal) =>
        resolve({
          code,
          signal,
          elapsedMs: Date.now() - started,
          stdout,
          stderr,
        }),
      );
    }),
  };
}

test(
  "critical: killed rollout parent retains both locks until its own operation and grandchild are reclaimed",
  { timeout: 20000 },
  async () => {
    const f = await fixture(undefined, { timeoutMs: 8000 });
    const lock = path.join(f.dir, "maintenance.lock");
    const pids = path.join(f.dir, "pids.json");
    const script = path.join(f.dir, "operation.py");
    await writeFile(
      script,
      `import subprocess,os,json,pathlib,time\nc=subprocess.Popen(['python3','-c','import time;time.sleep(30)'])\npathlib.Path(${JSON.stringify(pids)}).write_text(json.dumps({'operation':os.getpid(),'grandchild':c.pid,'guardian':os.getpgrp()}))\ntime.sleep(30)\n`,
    );
    let guardian: number | undefined;
    let crashed: any;
    try {
      const run = invoke(
        "rollout-with-locks.py",
        [
          "--config",
          f.configPath,
          "--lock-file",
          lock,
          "--artifacts",
          path.join(f.dir, "rollout"),
          "--",
          "python3",
          script,
        ],
        f.env,
      );
      await until(() =>
        access(pids).then(
          () => true,
          () => false,
        ),
      );
      const owned = JSON.parse(await readFile(pids, "utf8"));
      guardian = owned.guardian;
      process.kill(guardian!, "SIGSTOP");
      run.child.kill("SIGKILL");
      // This stopped guardian still owns our running child and both maintenance paths must reject.
      const direct = await f.run("maintain");
      assert.equal(direct.ok, false);
      assert.match(direct.error, /locked by writer/);
      const contender = await invoke(
        "run-maintenance.py",
        [
          "--config",
          f.configPath,
          "--lock-file",
          lock,
          "--artifacts",
          path.join(f.dir, "contender"),
          "--qmd",
          "/usr/bin/true",
          "--reconcile",
          "/dev/null",
        ],
        f.env,
      ).done;
      const result = JSON.parse(contender.stdout.trim().split("\n").at(-1)!);
      assert.equal(result.ok, false);
      assert.match(result.report.error, /Resource temporarily unavailable/);
      const during = {
        operationAlive: alive(owned.operation),
        grandchildAlive: alive(owned.grandchild),
      };
      assert.equal(during.operationAlive, true);
      assert.equal(during.grandchildAlive, true);
      assert.equal(f.calls.length, 0);
      process.kill(guardian!, "SIGCONT");
      await until(() => !alive(owned.operation) && !alive(owned.grandchild));
      const after = {
        operationAlive: alive(owned.operation),
        grandchildAlive: alive(owned.grandchild),
      };
      crashed = await run.done;
      const next = await invoke(
        "rollout-with-locks.py",
        [
          "--config",
          f.configPath,
          "--lock-file",
          lock,
          "--artifacts",
          path.join(f.dir, "resumed"),
          "--",
          "/usr/bin/true",
        ],
        f.env,
      ).done;
      assert.equal(next.code, 0, next.stdout + next.stderr);
      const resumed = await f.run("maintain");
      assert.equal(resumed.ok, true, JSON.stringify(resumed));
      await writeFile(
        path.join(f.dir, "critical-rollout-crash.json"),
        JSON.stringify(
          {
            owned,
            during,
            after,
            direct,
            contender,
            result,
            crashed,
            next,
            resumed,
          },
          null,
          2,
        ),
      );
      console.log("Critical rollout crash: " + f.dir);
    } finally {
      if (guardian && alive(guardian)) {
        try {
          process.kill(guardian, "SIGCONT");
        } catch {}
      }
      await f.close();
    }
  },
);

test(
  "critical: observer artifact failure after starting a real helper reclaims owned child work and returns parseable failure",
  { timeout: 18000 },
  async () => {
    const f = await fixture();
    const artifacts = path.join(f.dir, "observed");
    const pids = path.join(f.dir, "pids.json");
    const reconcile = path.join(f.dir, "reconcile.py");
    const lock = path.join(f.dir, "maintenance.lock");
    await writeFile(
      reconcile,
      `import pathlib,subprocess,os,json,time\np=pathlib.Path(${JSON.stringify(artifacts)});(p/'diagnosis.json').mkdir()\nc=subprocess.Popen(['python3','-c','import time;time.sleep(30)'])\npathlib.Path(${JSON.stringify(pids)}).write_text(json.dumps({'child':os.getpid(),'grandchild':c.pid}))\ntime.sleep(30)\n`,
    );
    try {
      const observed = await invoke(
        "run-maintenance.py",
        [
          "--config",
          f.configPath,
          "--lock-file",
          lock,
          "--artifacts",
          artifacts,
          "--qmd",
          "/usr/bin/true",
          "--reconcile",
          reconcile,
          "--budget-seconds",
          "5",
          "--termination-grace-seconds",
          "0.2",
          "--observation-margin-seconds",
          "1",
          "--stall-seconds",
          "0.4",
        ],
        f.env,
      ).done;
      const value = JSON.parse(observed.stdout.trim().split("\n").at(-1)!);
      const owned = JSON.parse(await readFile(pids, "utf8"));
      assert.equal(value.ok, false);
      assert.equal(value.outcome, "observer-failed");
      assert.equal(value.helper.starts, 1);
      assert.equal(value.helper.running, false);
      assert.ok(observed.elapsedMs < 4000);
      assert.ok(value.remaining.length);
      await until(() => !alive(owned.child) && !alive(owned.grandchild));
      const after = {
        childAlive: alive(owned.child),
        grandchildAlive: alive(owned.grandchild),
      };
      assert.equal(f.calls.length, 0);
      const next = await invoke(
        "rollout-with-locks.py",
        [
          "--config",
          f.configPath,
          "--lock-file",
          lock,
          "--artifacts",
          path.join(f.dir, "after-storage-failure"),
          "--",
          "/usr/bin/true",
        ],
        f.env,
      ).done;
      assert.equal(next.code, 0, next.stdout + next.stderr);
      await writeFile(
        path.join(f.dir, "critical-observer-storage.json"),
        JSON.stringify({ observed, value, owned, after, next }, null, 2),
      );
      console.log("Critical observer storage: " + f.dir);
    } finally {
      await f.close();
    }
  },
);
