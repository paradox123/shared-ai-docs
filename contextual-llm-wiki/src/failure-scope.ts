/** Conservative closure across old/new concept ownership and persisted page edges.
 * A source gained through a page edge can in turn affect newly shared concepts,
 * so both graphs must be expanded together until neither adds work.
 */
export function failureScope(
  prior: any,
  next: any,
  pages: any,
  failures: any[],
) {
  const failedSources = new Set<string>(
    failures.flatMap((failure) => failure.sources),
  );
  const blocked = new Set<string>();
  let expanded = true;
  while (expanded) {
    expanded = false;
    const slugs = new Set(
      [...failedSources].flatMap((id) => [
        ...(prior.sources[id]?.concepts || []),
        ...(next.sources[id]?.concepts || []),
      ]),
    );
    for (const records of [prior.sources, next.sources])
      for (const [id, record] of Object.entries<any>(records))
        if (
          !failedSources.has(id) &&
          record.concepts.some((slug: string) => slugs.has(slug))
        ) {
          failedSources.add(id);
          expanded = true;
        }
    for (const page of Object.values<any>(pages)) {
      if (blocked.has(page.id)) continue;
      if (
        Object.keys(page.sourceVersions).some((id) => failedSources.has(id)) ||
        Object.keys(page.pageVersions).some((id) => blocked.has(id))
      ) {
        blocked.add(page.id);
        if (page.kind === "concept")
          for (const id of Object.keys(page.sourceVersions))
            failedSources.add(id);
        expanded = true;
      }
    }
  }
  return { failedSources, blocked };
}
