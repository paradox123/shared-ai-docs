import path from "node:path";
import { hash } from "./storage.ts";

function remapBody(
  body: string,
  page: any,
  mapping: Map<string, any>,
  files: Record<string, Buffer>,
  snapshotRoot: string,
) {
  const links: any[] = [];
  // Only navigation and evidence-version references change; original prose stays intact.
  const text = body.replace(
    /\[([^\]]+)\]\(([^)]+)\)( @ [a-f0-9]{64})?/g,
    (whole, label, target, version) => {
      if (/^(?:[a-z][a-z0-9+.-]*:|#)/i.test(target)) return whole;
      const [file, anchor] = target.replace(/^<|>$/g, "").split("#");
      let decoded;
      try {
        decoded = decodeURI(file);
      } catch {
        links.push({ target, action: "unresolved" });
        return label;
      }
      const relativeFile = path.posix.normalize(
        path.posix.join("wiki", path.posix.dirname(page.id), decoded),
      );
      const id = relativeFile.replace(/^wiki\//, "").replace(/\.md$/, "");
      const resolved = mapping.get(id);
      if (!resolved) {
        if (files[relativeFile]) {
          const uri =
            "obsidian://open?path=" +
            encodeURIComponent(path.join(snapshotRoot, relativeFile));
          links.push({ target, destination: uri, action: "snapshot" });
          return `[${label} (historisch)](${uri})${version || ""}`;
        }
        links.push({ target, action: "unresolved" });
        return label;
      }
      const relative = path.posix.relative(
        path.posix.dirname(page.id),
        resolved.id + ".md",
      );
      const destination = encodeURI(relative) + (anchor ? "#" + anchor : "");
      links.push({ target, destination, action: "remapped" });
      return `[${label}](${destination})${version ? " @ " + resolved.hash : ""}`;
    },
  );
  return { body: text, links };
}

export function planImport(
  input: any,
  files: Record<string, Buffer>,
  existingPages: any,
  snapshotRoot: string,
  destination: string,
) {
  const reports: any[] = [],
    publications: any[] = [],
    remaining: any[] = input.pages.filter((p: any) => p.eligible),
    mapping = new Map<string, any>();
  for (const p of input.pages.filter((p: any) => !p.eligible))
    reports.push({
      origin: input.root,
      id: p.id,
      action: "quarantined",
      reasons: p.reasons,
    });
  const ordered: any[] = [];
  while (remaining.length) {
    const p = remaining.find((p) =>
      Object.keys(p.pageVersions).every((id) => mapping.has(id)),
    );
    if (!p) throw Error("Unresolved migration dependency graph");
    remaining.splice(remaining.indexOf(p), 1);
    const dependencies = Object.fromEntries(
      Object.keys(p.pageVersions)
        .sort()
        .map((id) => [id, mapping.get(id).migration.revision]),
    );
    const revision = hash(
      JSON.stringify([
        p.id,
        p.hash,
        Object.entries(p.sourceVersions).sort(),
        dependencies,
      ]),
    );
    const id = p.id.split("/")[0] + "/import-" + revision;
    const page: any = {
      ...p,
      id,
      migration: {
        revision,
        originalId: p.id,
        originalHash: p.hash,
        snapshot: destination,
      },
    };
    delete page.reasons;
    delete page.eligible;
    const existing = existingPages[id];
    if (existing && existing.migration?.revision !== revision)
      throw Error("Migration page identity conflict: " + id);
    mapping.set(p.id, existing || page);
    ordered.push(p);
  }
  // All navigation identities exist before rendering; evidence hashes follow dependency order.
  for (const p of ordered) {
    const page = mapping.get(p.id),
      existing = existingPages[page.id];
    let links: any[] = [];
    if (!existing) {
      page.pageVersions = Object.fromEntries(
        Object.keys(p.pageVersions).map((id) => [
          mapping.get(id).id,
          mapping.get(id).hash,
        ]),
      );
      const remapped = remapBody(
        files["wiki/" + p.id + ".md"].toString("utf8"),
        p,
        mapping,
        files,
        snapshotRoot,
      );
      page.hash = hash(remapped.body);
      links = remapped.links;
      publications.push({ page, body: remapped.body });
    }
    reports.push({
      origin: input.root,
      id: p.id,
      target: page.id,
      originalHash: p.hash,
      hash: page.hash,
      action: existing ? "deduplicated" : "preserved",
      links,
    });
  }
  return { reports, publications };
}
