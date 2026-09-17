import path from "node:path";
import { json, writeJson } from "./storage.ts";

export function maintenanceNow(config: any) {
  const override = process.env.WIKI_MAINTENANCE_NOW;
  if (override && !config.qmd?.isolated)
    throw Error("Maintenance clock override requires isolated QMD");
  const now = new Date(override || Date.now());
  if (!Number.isFinite(now.getTime())) throw Error("Invalid maintenance clock");
  return now.toISOString();
}
const berlinDate = (iso: string) =>
  new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Berlin",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(iso));
function nextDate(iso: string) {
  const date = new Date(berlinDate(iso) + "T12:00:00Z");
  date.setUTCDate(date.getUTCDate() + 1);
  return date.toISOString().slice(0, 10);
}
export async function maintenanceInventory(config: any, sources: any) {
  const file = path.join(config.output, ".state/maintenance-inventory.json");
  const now = maintenanceNow(config);
  const inventory = await json(file, null);
  const current = inventory || { version: 1, createdAt: now, sources: {} };
  if (current.version !== 1 || !current.sources)
    throw Error("Invalid maintenance inventory");
  for (const source of Object.values<any>(sources)) {
    const old = current.sources[source.id];
    if (!old || old.hash !== source.hash || old.removedAt) {
      current.sources[source.id] = {
        ...old,
        hash: source.hash,
        firstSeenAt: old?.firstSeenAt || now,
        observedAt: now,
        changedAt: null,
        classification: inventory ? "daily" : "initial",
        dueDate: inventory ? nextDate(now) : null,
        removedAt: null,
      };
    }
  }
  for (const [id, record] of Object.entries<any>(current.sources))
    if (!sources[id] && !record.removedAt) record.removedAt = now;
  await writeJson(file, current);
  let writes = Promise.resolve();
  return {
    value: current,
    save: () => {
      writes = writes.then(() => writeJson(file, current));
      return writes;
    },
    async order(limit: number) {
      const active = Object.keys(sources);
      const pending = active.filter(
        (id) => current.sources[id].extractedHash !== sources[id].hash,
      );
      const older = (a: string, b: string) =>
        current.sources[a].observedAt.localeCompare(
          current.sources[b].observedAt,
        ) || a.localeCompare(b);
      const daily = pending
        .filter((id) => current.sources[id].classification === "daily")
        .sort(older);
      const initial = pending
        .filter((id) => current.sources[id].classification === "initial")
        .sort(older);
      // Reconcile the previous started attempt from durably saved extraction
      // hashes, even when SIGKILL prevented its final report. After two rounds
      // without initial progress, reserve the FIRST attempt once; then return
      // to daily-first regardless of its outcome. This guarantees an attempt,
      // not success from an unavailable/too-slow provider.
      const previous = current.fairness?.attempt;
      const priorInitial = Object.entries<string>(
        previous?.initial || {},
      ).filter(
        ([id, version]) =>
          sources[id]?.hash === version &&
          current.sources[id].classification === "initial",
      );
      const madeProgress = priorInitial.some(
        ([id, version]) => current.sources[id].extractedHash === version,
      );
      const missed =
        !priorInitial.length ||
        madeProgress ||
        previous?.mode === "initial-recovery"
          ? 0
          : (current.fairness?.missedInitialRounds || 0) + 1;
      const recovery = initial.length > 0 && daily.length > 0 && missed >= 2;
      current.fairness = {
        missedInitialRounds: missed,
        backlogStalled:
          initial.length > 0 &&
          (missed > 0 ||
            (previous?.mode === "initial-recovery" && !madeProgress)),
        attempt: {
          startedAt: now,
          dailyCount: daily.length,
          reservedInitialSlots: initial.length ? 1 : 0,
          mode: recovery ? "initial-recovery" : "daily-first",
          initial: Object.fromEntries(
            initial.map((id) => [id, sources[id].hash]),
          ),
        },
      };
      writes = writes.then(() => writeJson(file, current));
      await writes;
      const normal = [
        ...daily.slice(0, limit - (initial.length ? 1 : 0)),
        ...initial.slice(0, 1),
        ...daily.slice(limit - (initial.length ? 1 : 0)),
        ...initial.slice(1),
        ...active.filter((id) => !pending.includes(id)),
      ];
      return recovery
        ? [initial[0], ...normal.filter((id) => id !== initial[0])]
        : normal;
    },
    report(state: any) {
      const active = Object.entries<any>(current.sources).filter(
        ([id, r]) => sources[id] && !r.removedAt,
      );
      const blockedSources = new Set(
        state.pending.flatMap((p: any) => [
          ...(p.sources || []),
          ...(p.pages || []).flatMap((id: string) =>
            Object.keys(state.pages[id]?.sourceVersions || {}),
          ),
        ]),
      );
      const open = active.filter(
        ([id, r]) =>
          state.sources[id]?.hash !== r.hash || blockedSources.has(id),
      );
      const daily = open.filter(([, r]) => r.classification === "daily");
      const initial = open.filter(([, r]) => r.classification === "initial");
      const initialUnextracted = initial.filter(
        ([, r]) => r.extractedHash !== r.hash,
      ).length;
      const dailyUnextracted = daily.filter(
        ([, r]) => r.extractedHash !== r.hash,
      ).length;
      const overdue = daily
        .filter(([, r]) => berlinDate(now) > r.dueDate)
        .map(([id]) => id);
      return {
        observedAt: now,
        timezone: "Europe/Berlin",
        deadlineBasis: "first-observed-current-version",
        daily: {
          pending: daily.length,
          sources: daily.map(([id]) => id),
          sourceStatements: daily.filter(([, r]) => r.summarizedHash === r.hash)
            .length,
          overdue,
          unknownChangeTime: daily.map(([id]) => id),
        },
        initial: {
          pending: initial.length,
          unextracted: initialUnextracted,
          sources: initial.map(([id]) => id),
        },
        globalComplete: open.length === 0 && state.pending.length === 0,
        capacity: {
          mode: current.fairness?.attempt?.mode || "daily-first",
          missedInitialRounds: current.fairness?.missedInitialRounds || 0,
          backlogStalled:
            initialUnextracted > 0 &&
            (current.fairness?.backlogStalled || false),
          insufficientTimeCapacity: false,
          maxExtractionSources: config.maintenance?.maxExtractionSources || 20,
          reservedInitialSlots: initialUnextracted ? 1 : 0,
          dailyAwaitingExtraction: dailyUnextracted,
          dailyOverCapacity:
            dailyUnextracted > 0 &&
            (dailyUnextracted >
              (config.maintenance?.maxExtractionSources || 20) -
                (initialUnextracted ? 1 : 0) ||
              (current.fairness?.attempt?.dailyCount || 0) >
                (config.maintenance?.maxExtractionSources || 20) -
                  (current.fairness?.attempt?.reservedInitialSlots || 0)),
        },
      };
    },
  };
}
