import path from "node:path";
import { readFile } from "node:fs/promises";
import { atomic, hash } from "./storage.ts";
export function originalLink(source: any, label = source.id) {
  return `[${label}](obsidian://open?path=${encodeURIComponent(source.original)})`;
}
export function renderConcept(body: string, versions: any, sources: any) {
  const linked = body.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    (all, label, target) => {
      const id = target
        .replace(/^<|>$/g, "")
        .replace(/^(?:\.\.\/)*sources\//, "");
      return sources[id] ? originalLink(sources[id], label) : all;
    },
  );
  const citations = linked.replace(/\^\[([^\]]+)\]/g, (whole, inside) => {
    const refs = inside.split(/,\s*/).map((ref: string) => {
      const m = ref.match(/^(.*?\.md)(?::(\d+)(?:-(\d+))?)?$/i);
      if (!m || !sources[m[1]]) return ref;
      return originalLink(
        sources[m[1]],
        m[1] + (m[2] ? ` Zeilen ${m[2]}–${m[3] || m[2]}` : ""),
      );
    });
    return "(" + refs.join("; ") + ")";
  });
  return (
    citations +
    "\n\n## Originalquellen\n\n" +
    Object.keys(versions)
      .map((id) => `- ${originalLink(sources[id])} — SHA-256 ${versions[id]}`)
      .join("\n") +
    "\n"
  );
}
export function renderAnswer(
  question: string,
  body: string,
  evidence: any[],
  sources: any,
) {
  const originals = [
    ...new Set(evidence.flatMap((e) => Object.keys(e.sourceVersions))),
  ];
  return (
    `# ${question}\n\n${body}\n\n## Verwendete Evidenz\n\n` +
    evidence
      .map(
        (e) =>
          `- ${e.kind === "source" ? originalLink(sources[e.id.slice(8)]) : `[${e.id}](${encodeURI("../" + e.id + ".md")})`} @ ${e.hash}`,
      )
      .join("\n") +
    "\n\n## Originalquellen\n\n" +
    originals
      .map(
        (id) => `- ${originalLink(sources[id])} — SHA-256 ${sources[id].hash}`,
      )
      .join("\n") +
    "\n"
  );
}
export async function publishPage(config: any, page: any, body: string) {
  page.hash = hash(body);
  const file = path.join(config.output, "wiki", page.id + ".md");
  let current = "";
  try {
    current = await readFile(file, "utf8");
  } catch (e) {
    if ((e as any).code !== "ENOENT") throw e;
  }
  if (current !== body) await atomic(file, body);
}
export async function entry(config: any, state: any) {
  await atomic(
    path.join(config.output, "wiki/index.md"),
    `# Kontext-Wiki: ${config.context}\n\nLetzte vollständige Pflege: ${state.lastCompleted || "noch offen"}.\n\nPrüfbedarf: ${state.pending.length ? state.pending.map((p: any) => (typeof p === "string" ? p : JSON.stringify(p))).join("; ") : "keiner im letzten Pflegeaufruf"}. Originalquellen werden vor jeder verwalteten Abfrage erneut geprüft.\n\n## Wissen\n\n` +
      Object.values<any>(state.pages)
        .filter((p) => !p.withdrawn)
        .map((p) => `- [${p.id}](${p.id}.md)`)
        .join("\n") +
      "\n",
  );
}

export function normalizeLinks(body: string, id: string, pages: any) {
  const known = new Map<string, string>();
  for (const page of Object.values<any>(pages))
    for (const key of [page.id, page.id.split("/").pop(), page.title])
      if (key) known.set(key.toLowerCase(), page.id);
  return body.replace(/\[\[([^\]]+)\]\]/g, (_all, ref: string) => {
    const [target, label] = ref.split("|"),
      key = target.replace(/\.md$/, "").toLowerCase(),
      resolved = known.get(key);
    if (!resolved) return label || target;
    const relative = path.posix.relative(
      path.posix.dirname(id),
      resolved + ".md",
    );
    return `[${label || target}](${encodeURI(relative)})`;
  });
}
