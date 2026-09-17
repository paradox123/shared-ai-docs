import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn, execFileSync } from "node:child_process";
import { writeFile, readFile, mkdir, rename } from "node:fs/promises";
import path from "node:path";
import { fixture } from "./support.ts";

async function helper(
  f: any,
  name: string,
  seconds = 4,
  options: { reconcile?: string; qmd?: string } = {},
) {
  const reconcile = options.reconcile || path.join(f.dir, "reconcile.py");
  if (!options.reconcile)
    await writeFile(reconcile, `print('{"status":"ok"}')\n`);
  const child = spawn(
    "python3",
    [
      new URL("../scripts/maintain-index.py", import.meta.url).pathname,
      "--config",
      f.configPath,
      "--artifacts",
      path.join(f.dir, name),
      "--qmd",
      options.qmd || "/usr/bin/true",
      "--reconcile",
      reconcile,
      "--budget-seconds",
      String(seconds),
      "--termination-grace-seconds",
      "0.5",
    ],
    { env: { ...process.env, ...f.env }, detached: true },
  );
  let stdout = "",
    stderr = "";
  child.stdout.on("data", (b) => (stdout += b));
  child.stderr.on("data", (b) => (stderr += b));
  const started = Date.now();
  const timer = setTimeout(() => {
    try {
      process.kill(-child.pid!, "SIGKILL");
    } catch {}
  }, 20000);
  const done = new Promise<any>((resolve) =>
    child.on("close", (code, signal) => {
      clearTimeout(timer);
      resolve({
        code,
        signal,
        elapsedMs: Date.now() - started,
        stdout,
        stderr,
        report: stdout.trim()
          ? JSON.parse(stdout.trim().split("\n").at(-1)!)
          : null,
      });
    }),
  );
  return { done, child, startedAt: started };
}
async function waitFor(check: () => Promise<boolean> | boolean) {
  const end = Date.now() + 10000;
  while (!(await check())) {
    assert.ok(Date.now() < end, "hard observation deadline");
    await new Promise((r) => setTimeout(r, 30));
  }
}

test(
  "bounded helper exposes durable progress while provider is held, releases locks and resumes saved extraction",
  { timeout: 40000 },
  async () => {
    let held = true,
      entered = false;
    let release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    const f = await fixture(
      async (body) => {
        if (held && body.tools && entered) await gate;
        if (body.tools) entered = true;
      },
      { timeoutMs: 15000 },
    );
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    try {
      const first = await helper(f, "budget");
      // Budget exists even when the compiler never returns.
      await waitFor(
        () =>
          f.calls.filter((b) => b.tools).length === 2 ||
          first.child.exitCode !== null,
      );
      assert.equal(
        first.child.exitCode,
        null,
        "helper must start real work, not reject budget flags",
      );
      const progressPath = path.join(
        f.dir,
        "budget",
        "maintain-test.progress.json",
      );
      await waitFor(
        async () =>
          JSON.parse(await readFile(progressPath, "utf8").catch(() => "{}"))
            .extractions?.saved === 1,
      );
      const during = JSON.parse(await readFile(progressPath, "utf8"));
      assert.equal(during.active, 1);
      assert.equal(during.extractions.saved, 1);
      assert.ok(during.remaining.length > 0);
      assert.equal(JSON.stringify(during).includes("local-test-only"), false);
      assert.equal(JSON.stringify(during).includes("Alpha verlangt"), false);
      const conflict = await helper(f, "conflict", 2);
      assert.equal(
        (await conflict.done).report.failedStep,
        "preflight-or-lock",
      );
      const stopped = await first.done;
      held = false;
      release();
      assert.equal(stopped.code, 1, JSON.stringify(stopped));
      assert.equal(stopped.report.ok, false);
      assert.equal(stopped.report.outcome, "budget-exhausted");
      assert.ok(stopped.elapsedMs < 6500, JSON.stringify(stopped));
      assert.ok(stopped.report.remaining.length > 0);
      assert.equal(stopped.report.contexts[0].sourceIndex.ok, true);
      assert.equal((await f.run("status")).lastCompleted, null);
      await assert.rejects(
        readFile(path.join(f.config.output, ".state/writer.lock")),
      );
      const query = await f.run("query", "--question", "Freigabe");
      assert.equal(query.fallback, true);
      const resumed = await helper(f, "resumed", 15);
      const result = await resumed.done;
      assert.equal(result.code, 0, JSON.stringify(result));
      assert.equal(f.calls.filter((b) => b.tools).length, 3);
      const count = f.calls.length;
      const noop = await helper(f, "noop", 15);
      assert.equal((await noop.done).report.contexts[0].noop, true);
      assert.equal(f.calls.length, count);
      const finalQuery = await f.run("query", "--question", "Freigabe");
      assert.equal(finalQuery.fallback, false);
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify({ during, stopped, result, query, finalQuery }, null, 2),
      );
      console.log("Budget evidence: " + f.dir);
    } finally {
      held = false;
      release();
      await f.close();
    }
  },
);

test(
  "shared authentication failure stops a filled provider queue and bounded source errors remain distinct",
  { timeout: 40000 },
  async () => {
    const f = await fixture(undefined, { timeoutMs: 15000 });
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    for (let i = 0; i < 4; i++)
      await writeFile(
        path.join(f.dir, `alpha/extra${i}.md`),
        `# Freigabe\nAlpha verlangt zwei Freigaben.\n`,
      );
    try {
      f.fail(true, 401);
      const stopped = await (await helper(f, "auth", 10)).done;
      assert.equal(stopped.code, 1);
      assert.equal(
        f.calls.length,
        1,
        "only one actual HTTP request may hit a rejected shared provider",
      );
      assert.equal(
        stopped.report.outcome,
        "shared-provider-failure",
        JSON.stringify(stopped),
      );
      const count = f.calls.length;
      f.fail(
        (body) =>
          !!body.tools && body.messages[0].content.includes("Beta verlangt"),
        400,
      );
      const sourceFailure = await (await helper(f, "source-error", 10)).done;
      assert.equal(sourceFailure.report.ok, false);
      assert.notEqual(sourceFailure.report.outcome, "shared-provider-failure");
      assert.equal(
        f.calls.slice(count).filter((b) => b.tools).length,
        6,
        "source-local failure must allow other queued extractions",
      );
      const progress = JSON.parse(
        await readFile(
          path.join(f.dir, "source-error/maintain-test.progress.json"),
          "utf8",
        ),
      );
      assert.equal(progress.extractions.saved, 5);
      assert.equal(
        JSON.stringify(progress).includes("controlled provider failure"),
        false,
      );
      f.fail(false);
      const resumed = await (await helper(f, "repaired", 15)).done;
      assert.equal(resumed.code, 0, JSON.stringify(resumed));
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          {
            stopped,
            sourceFailure,
            progress,
            resumed,
            observedRequests: f.calls.length,
          },
          null,
          2,
        ),
      );
      console.log("Shared failure evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "shared failure also bounds an already running held request",
  { timeout: 20000 },
  async () => {
    let release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    const f = await fixture(
      async () => {
        await gate;
      },
      { timeoutMs: 10000 },
    );
    for (let i = 0; i < 4; i++)
      await writeFile(
        path.join(f.dir, `beta/extra${i}.md`),
        `# Freigabe\nBeta verlangt drei Freigaben.\n`,
      );
    f.delay(100);
    f.fail(
      (body) =>
        body.messages.some((m: any) => m.content.includes("Alpha verlangt")),
      401,
    );
    try {
      const result = await (await helper(f, "held-auth", 10)).done;
      assert.equal(
        result.report.outcome,
        "shared-provider-failure",
        JSON.stringify(result),
      );
      assert.equal(result.code, 1);
      assert.equal(
        f.calls.length,
        2,
        "one failing and one already active request, no queued dispatch",
      );
      assert.ok(result.elapsedMs < 4500);
      await assert.rejects(
        readFile(path.join(f.config.output, ".state/writer.lock")),
      );
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify({ result, observedRequests: f.calls.length }, null, 2),
      );
      console.log("Held auth evidence: " + f.dir);
    } finally {
      release();
      await f.close();
    }
  },
);

test(
  "outer budget terminates its detached Codex process group and held grandchild",
  { timeout: 20000 },
  async () => {
    const f = await fixture();
    const executable = path.join(f.dir, "codex");
    const identities = path.join(f.dir, "child-identities.json");
    await writeFile(
      executable,
      `#!/usr/bin/python3
import sys, os, signal, subprocess, time, json
if '--version' in sys.argv:
 print('codex-cli 0.0.0-fixture'); sys.exit(0)
if 'login' in sys.argv: sys.exit(0)
signal.signal(signal.SIGTERM, signal.SIG_IGN)
child = subprocess.Popen([sys.executable, '-c', 'import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'])
with open(${JSON.stringify(identities)}, 'w') as f: json.dump({'parent':os.getpid(), 'child':child.pid},f)
while True: time.sleep(1)
`,
      { mode: 0o755 },
    );
    Object.assign(f.env, {
      LLMWIKI_PROVIDER: "codex-agent",
      PATH: f.dir + ":" + process.env.PATH,
    });
    let ids: any;
    try {
      const running = await helper(f, "codex-budget", 4);
      await waitFor(async () => {
        try {
          ids = JSON.parse(await readFile(identities, "utf8"));
          return true;
        } catch {
          return false;
        }
      });
      const result = await running.done;
      assert.equal(
        result.report.outcome,
        "budget-exhausted",
        JSON.stringify(result),
      );
      assert.ok(result.elapsedMs < 6500);
      const helperEndedAt = Date.now();
      for (const pid of Object.values<number>(ids))
        await waitFor(() => {
          try {
            process.kill(pid, 0);
            return false;
          } catch {
            return true;
          }
        });
      const allProcessesGoneMs = result.elapsedMs + Date.now() - helperEndedAt;
      assert.ok(allProcessesGoneMs < 6500);
      await assert.rejects(
        readFile(path.join(f.config.output, ".state/writer.lock")),
      );
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(
          { result, allProcessesGoneMs, terminatedPids: ids },
          null,
          2,
        ),
      );
      console.log("Detached child evidence: " + f.dir);
    } finally {
      if (ids)
        for (const pid of Object.values<number>(ids)) {
          try {
            process.kill(pid, "SIGKILL");
          } catch {}
        }
      await f.close();
    }
  },
);

test(
  "unsupported provider model and service outage stop after one observed request without SDK retries",
  { timeout: 20000 },
  async () => {
    const f = await fixture(undefined, { timeoutMs: 10000 });
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    try {
      const observations = [];
      for (const [status, code] of [
        [400, "model_not_found"],
        [503, "unavailable"],
      ] as const) {
        f.fail(true, status, code);
        const before = f.calls.length;
        const result = await (await helper(f, "failure-" + status, 5)).done;
        assert.equal(
          result.report.outcome,
          "shared-provider-failure",
          JSON.stringify(result),
        );
        assert.equal(f.calls.length - before, 1);
        observations.push({
          status,
          code,
          result,
          requests: f.calls.length - before,
        });
      }
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify(observations, null, 2),
      );
      console.log("Provider classification evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "progress storage failure latches a shared stop before the next provider dispatch",
  { timeout: 15000 },
  async () => {
    let f: any;
    f = await fixture(
      async (body) => {
        if (!body.tools) return;
        const file = path.join(f.dir, "storage/maintain-test.progress.json");
        await rename(file, file + ".before-failure");
        await mkdir(file);
      },
      { timeoutMs: 10000 },
    );
    f.config.concurrency = 1;
    await f.saveConfig();
    try {
      const result = await (await helper(f, "storage", 5)).done;
      assert.equal(result.code, 1);
      assert.equal(result.report.ok, false);
      assert.equal(
        f.calls.length,
        1,
        "shared progress storage failure must stop the other source",
      );
      await writeFile(
        path.join(f.dir, "acceptance.json"),
        JSON.stringify({ result, requests: f.calls.length }, null, 2),
      );
      console.log("Progress storage failure evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: held reconciliation and final QMD commands obey the whole helper deadline",
  { timeout: 30000 },
  async () => {
    const f = await fixture(undefined, { timeoutMs: 10000 });
    const observations = [];
    try {
      for (const phase of ["reconcile", "qmd-update"]) {
        const executable = path.join(f.dir, phase + "-held.py");
        const identities = path.join(f.dir, phase + "-pids.json");
        await writeFile(
          executable,
          `#!/usr/bin/python3
import os, signal, subprocess, sys, time, json
signal.signal(signal.SIGTERM, signal.SIG_IGN)
child = subprocess.Popen([sys.executable, '-c', 'import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'])
with open(${JSON.stringify(identities)}, 'w') as f: json.dump([os.getpid(),child.pid],f)
while True: time.sleep(1)
`,
          { mode: 0o755 },
        );
        const job = await helper(
          f,
          phase + "-budget",
          phase === "reconcile" ? 1 : 5,
          phase === "reconcile"
            ? { reconcile: executable }
            : { qmd: executable },
        );
        await waitFor(async () => {
          try {
            await readFile(identities);
            return true;
          } catch {
            return false;
          }
        });
        const during = JSON.parse(
          await readFile(
            path.join(f.dir, phase + "-budget/progress.json"),
            "utf8",
          ),
        );
        assert.equal(during.phase, phase);
        assert.equal(during.active, true);
        const result = await job.done;
        assert.equal(result.code, 1, JSON.stringify(result));
        assert.equal(result.report.ok, false);
        assert.equal(result.report.outcome, "budget-exhausted");
        assert.equal(result.report.failedStep, phase);
        assert.ok(result.elapsedMs < (phase === "reconcile" ? 3500 : 7500));
        assert.deepEqual(
          result.report,
          JSON.parse(
            await readFile(
              path.join(f.dir, phase + "-budget/report.json"),
              "utf8",
            ),
          ),
        );
        const helperEndedAt = Date.now();
        const ids = JSON.parse(await readFile(identities, "utf8"));
        for (const pid of ids)
          await waitFor(() => {
            try {
              process.kill(pid, 0);
              return false;
            } catch {
              return true;
            }
          });
        const allProcessesGoneMs =
          result.elapsedMs + Date.now() - helperEndedAt;
        assert.ok(allProcessesGoneMs < (phase === "reconcile" ? 3500 : 7500));
        assert.ok(result.report.remaining.length > 0);
        if (phase === "reconcile") assert.equal(f.calls.length, 0);
        if (phase === "qmd-update") {
          assert.equal(result.report.contexts[0].wiki.ok, true);
          assert.ok(result.report.contexts[0].lastCompleted);
          assert.deepEqual(
            result.report.remaining.map((item: any) => item.phase),
            ["qmd-update", "qmd-embed", "qmd-status"],
          );
          assert.ok(
            !result.report.steps.some((step: any) => step.name === "qmd-embed"),
          );
        }
        observations.push({
          phase,
          during,
          result,
          terminatedPids: ids,
          allProcessesGoneMs,
        });
      }
      const beforeResume = f.calls.length;
      const repaired = await (await helper(f, "after-outer-budget", 10)).done;
      assert.equal(repaired.code, 0, JSON.stringify(repaired));
      assert.equal(f.calls.length, beforeResume);
      assert.equal(
        repaired.report.contexts[0].lastCompleted,
        observations[1].result.report.contexts[0].lastCompleted,
      );
      await writeFile(
        path.join(f.dir, "critical-outer-budget.json"),
        JSON.stringify({ observations, repaired }, null, 2),
      );
      console.log("Critical outer budget evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: stopped guardian retains flock after helper SIGKILL until child cleanup",
  { timeout: 30000 },
  async () => {
    let hold = true,
      seen = 0,
      release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    const f = await fixture(
      async (body) => {
        if (body.tools && ++seen === 2 && hold) await gate;
      },
      { timeoutMs: 10000 },
    );
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    let guardian: number | undefined;
    try {
      const first = await helper(f, "owner-crash", 15);
      await waitFor(() => f.calls.filter((body) => body.tools).length === 2);
      const owner = JSON.parse(
        await readFile(
          path.join(f.dir, "owner-crash/maintain-test.children.owner"),
          "utf8",
        ),
      );
      guardian = Number(
        execFileSync("/bin/ps", ["-o", "ppid=", "-p", String(owner.pid)], {
          encoding: "utf8",
        }).trim(),
      );
      assert.ok(guardian > 1);
      process.kill(guardian, "SIGSTOP");
      const exited = new Promise((resolve) =>
        first.child.once("exit", resolve),
      );
      process.kill(first.child.pid!, "SIGKILL");
      await exited;
      const conflict = await (
        await helper(f, "while-guardian-stopped", 2)
      ).done;
      assert.equal(
        conflict.report.failedStep,
        "preflight-or-lock",
        JSON.stringify(conflict),
      );
      assert.deepEqual(conflict.report.steps, []);
      process.kill(guardian, "SIGCONT");
      const crashed = await first.done;
      guardian = undefined;
      assert.equal(crashed.signal, "SIGKILL");
      await waitFor(() => {
        try {
          process.kill(owner.pid, 0);
          return false;
        } catch {
          return true;
        }
      });
      hold = false;
      release();
      const resumed = await (
        await helper(f, "after-guardian-cleanup", 10)
      ).done;
      assert.equal(resumed.code, 0, JSON.stringify(resumed));
      assert.equal(f.calls.filter((body) => body.tools).length, 3);
      await writeFile(
        path.join(f.dir, "critical-owner-crash.json"),
        JSON.stringify(
          { owner, conflict, crashed, resumed, extractionRequests: 3 },
          null,
          2,
        ),
      );
      console.log("Critical flock custody evidence: " + f.dir);
    } finally {
      if (guardian) {
        try {
          process.kill(guardian, "SIGCONT");
        } catch {}
      }
      hold = false;
      release();
      await f.close();
    }
  },
);

test(
  "critical verification: unavailable helper progress storage still returns a parseable failure report",
  { timeout: 15000 },
  async () => {
    const f = await fixture();
    const reconcile = path.join(f.dir, "break-progress.py");
    const progress = path.join(f.dir, "outer-storage/progress.json");
    await writeFile(
      reconcile,
      `import os\nos.unlink(${JSON.stringify(progress)})\nos.mkdir(${JSON.stringify(progress)})\nprint('{"status":"ok"}')\n`,
    );
    try {
      const result = await (
        await helper(f, "outer-storage", 5, { reconcile })
      ).done;
      assert.equal(result.code, 1);
      assert.equal(result.report.ok, false, JSON.stringify(result));
      assert.ok(result.report.artifactErrors.length > 0);
      assert.equal(f.calls.length, 0);
      assert.deepEqual(
        result.report,
        JSON.parse(
          await readFile(path.join(f.dir, "outer-storage/report.json"), "utf8"),
        ),
      );
      await writeFile(
        path.join(f.dir, "critical-outer-storage.json"),
        JSON.stringify({ result, requests: f.calls.length }, null, 2),
      );
      console.log("Critical outer storage evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: failed final report persistence cannot leave successful progress",
  { timeout: 15000 },
  async () => {
    const f = await fixture(undefined, { timeoutMs: 10000 });
    const reconcile = path.join(f.dir, "break-report.py");
    const reportFile = path.join(f.dir, "report-storage/report.json");
    await writeFile(
      reconcile,
      `import os\nos.mkdir(${JSON.stringify(reportFile)})\nprint('{"status":"ok"}')\n`,
    );
    try {
      const result = await (
        await helper(f, "report-storage", 10, { reconcile })
      ).done;
      assert.equal(result.code, 1);
      assert.equal(result.report.ok, false);
      assert.equal(result.report.contexts[0].wiki.ok, true);
      assert.deepEqual(result.report.artifactErrors, [
        { artifact: "report.json", code: "persist-failed" },
      ]);
      const progress = JSON.parse(
        await readFile(
          path.join(f.dir, "report-storage/progress.json"),
          "utf8",
        ),
      );
      assert.equal(progress.ok, false);
      assert.equal(progress.outcome, "shared-storage-failure");
      await writeFile(
        path.join(f.dir, "critical-report-storage.json"),
        JSON.stringify({ result, progress }, null, 2),
      );
      console.log("Critical report storage evidence: " + f.dir);
    } finally {
      await f.close();
    }
  },
);

test(
  "critical verification: budget stop permits settling active work but no queued provider dispatch",
  { timeout: 20000 },
  async () => {
    let release!: () => void,
      requests = 0;
    const gate = new Promise<void>((r) => (release = r));
    const f = await fixture(
      async (body) => {
        if (body.tools && ++requests === 2) await gate;
      },
      { timeoutMs: 10000 },
    );
    (f.config as any).concurrency = 1;
    await f.saveConfig();
    await writeFile(
      path.join(f.dir, "beta/extra1.md"),
      "# Freigabe\nBeta verlangt drei Freigaben.\n",
    );
    await writeFile(
      path.join(f.dir, "beta/extra2.md"),
      "# Freigabe\nBeta verlangt drei Freigaben.\n",
    );
    let timer: ReturnType<typeof setTimeout> | undefined;
    try {
      const job = await helper(f, "settle-after-budget", 4);
      await waitFor(() => requests === 2);
      timer = setTimeout(
        release,
        Math.max(0, job.startedAt + 4200 - Date.now()),
      );
      const result = await job.done;
      assert.equal(
        result.report.outcome,
        "budget-exhausted",
        JSON.stringify(result),
      );
      assert.equal(result.code, 1);
      assert.equal(
        requests,
        2,
        "two queued sources must not reach the provider after budget stop",
      );
      assert.equal(
        result.report.contexts[0].extractions.saved,
        2,
        "active valid reply may finish within grace",
      );
      const resumed = await (await helper(f, "resume-settled-budget", 10)).done;
      assert.equal(resumed.code, 0, JSON.stringify(resumed));
      assert.equal(
        requests,
        4,
        "both durable pre-stop and settled results reused by fresh process",
      );
      await writeFile(
        path.join(f.dir, "critical-budget-dispatch.json"),
        JSON.stringify(
          { result, resumed, totalExtractionRequests: requests },
          null,
          2,
        ),
      );
      console.log("Critical budget dispatch evidence: " + f.dir);
    } finally {
      clearTimeout(timer);
      release();
      await f.close();
    }
  },
);
