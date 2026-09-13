export type EvidenceLimits = { repos?: string[]; sources?: string[] };

// Limits are checked before candidates reach either model call. Page graphs are
// traversed as well as flattened provenance, so a partial record cannot widen them.
export function evidenceEligibility(
  config: any,
  state: any,
  sources: any,
  limits: EvidenceLimits = {},
) {
  for (const id of limits.repos || [])
    if (!config.repos.some((r: any) => r.id === id))
      throw Error("Unknown repository limit: " + id);
  for (const id of limits.sources || [])
    if (!sources[id]) throw Error("Unknown or unavailable source limit: " + id);
  const source = (id: string) =>
    (!limits.repos || limits.repos.includes(id.split("/")[0])) &&
    (!limits.sources || limits.sources.includes(id));
  const page = (id: string, ancestors = new Set<string>()): boolean => {
    const record = state.pages[id];
    if (!record || record.withdrawn || ancestors.has(id)) return false;
    const originals = Object.keys(record.sourceVersions || {});
    if (!originals.length || !originals.every(source)) return false;
    const next = new Set(ancestors).add(id);
    return Object.keys(record.pageVersions || {}).every((dep) =>
      page(dep, next),
    );
  };
  return { source, page };
}
