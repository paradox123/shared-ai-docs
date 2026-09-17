import {
  writeFileSync,
  renameSync,
  openSync,
  closeSync,
  fsyncSync,
} from "node:fs";
import path from "node:path";

// Progress contains counts/identities only, never request text or provider errors.
export function maintenanceControl(file: string, progress: any) {
  const deadline = Number(process.env.WIKI_MAINTENANCE_DEADLINE_MS || Infinity);
  const active = new Set<Promise<string>>();
  let stopped: string | undefined;
  let successful = 0,
    failed = 0;
  const emit = () => {
    const value = {
      runId: path.basename(path.dirname(file)),
      pid: process.pid,
      phase: progress.phase || "scan",
      active: active.size,
      modelResponses: successful,
      modelErrors: failed,
      extractions: progress.extractions || { saved: 0, reused: 0, invalid: 0 },
      sourceIndex: progress.sourceIndex,
      remaining: (progress.remaining || [{ phase: "scan" }]).map(
        (item: any) => ({
          phase: item.phase || "pending",
          ...(item.sources ? { sources: item.sources } : {}),
          ...(item.pages ? { pages: item.pages } : {}),
        }),
      ),
      stopReason: stopped,
      lastProgressAt: new Date().toISOString(),
    };
    const temporary = file + ".tmp";
    try {
      writeFileSync(temporary, JSON.stringify(value), { mode: 0o600 });
      const fd = openSync(temporary, "r");
      try {
        fsyncSync(fd);
      } finally {
        closeSync(fd);
      }
      renameSync(temporary, file);
    } catch {
      stopped = "shared-storage-failure";
      throw Object.assign(Error("Cannot persist maintenance progress"), {
        sharedMaintenance: true,
      });
    }
  };
  const stop = (reason: string) => {
    stopped ||= reason;
    emit();
  };
  const interrupted = () => stop("budget-exhausted");
  process.on("SIGTERM", interrupted);
  const stoppedError = () =>
    Object.assign(Error(stopped || "Maintenance stopped"), {
      sharedMaintenance: true,
    });
  const run = async (phase: string, invoke: () => Promise<string>) => {
    if (Date.now() >= deadline) stop("budget-exhausted");
    if (stopped) throw stoppedError();
    progress.phase = phase;
    // Invoke only after both deadline and shared-failure gate have passed.
    let start!: () => void;
    const pending = new Promise<string>((resolve, reject) => {
      start = () => {
        invoke().then(resolve, reject);
      };
    });
    active.add(pending);
    try {
      emit();
      if (Date.now() >= deadline) {
        stop("budget-exhausted");
        throw stoppedError();
      }
      start();
      const value = await pending;
      successful++;
      return value;
    } catch (error: any) {
      failed++;
      if (error?.sharedMaintenance) throw error;
      const status = Number(
        error?.status || /^(\d{3})\b/.exec(error?.message || "")?.[1],
      );
      // Only explicit request-local codes or payload size establish source isolation. Transport,
      // auth, quota and provider service failures affect the shared dependency.
      const code = error?.code || error?.error?.code;
      const sourceLocal =
        status === 413 ||
        ([400, 422].includes(status) &&
          [
            "context_length_exceeded",
            "input_too_long",
            "content_filter",
            "source_error",
          ].includes(code));
      if (!sourceLocal) {
        stop("shared-provider-failure");
        throw stoppedError();
      }
      throw error;
    } finally {
      active.delete(pending);
      emit();
    }
  };
  emit();
  return {
    run,
    emit,
    stop,
    async close() {
      // Keep writer ownership until all in-flight work settles. The external
      // supervisor enforces the grace bound if a provider never returns.
      await Promise.allSettled([...active]);
      process.removeListener("SIGTERM", interrupted);
    },
    get reason() {
      return stopped;
    },
  };
}
