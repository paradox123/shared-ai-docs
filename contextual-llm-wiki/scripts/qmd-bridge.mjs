// Runs with QMD's installed Node runtime, independently of the compiler runtime.
import { pathToFileURL } from "node:url";
import { readFileSync } from "node:fs";
const request = JSON.parse(readFileSync(0, "utf8"));
try {
  const { createStore, getDefaultDbPath } = await import(
    pathToFileURL(request.module).href
  );
  const store = await createStore({
    dbPath: request.dbPath || getDefaultDbPath(),
  });
  try {
    const collections = await store.listCollections();
    const existing = collections.find((c) => c.name === request.collection);
    if (
      existing &&
      (existing.pwd !== request.root || existing.glob_pattern !== "**/*.md")
    )
      throw Error("QMD collection conflict: " + request.collection);
    if (!existing) {
      if (!request.isolated)
        throw Error(
          "QMD collection not registered through the owning manifest: " +
            request.collection,
        );
      await store.addCollection(request.collection, {
        path: request.root,
        pattern: "**/*.md",
      });
    }
    let result;
    if (request.operation === "update")
      result = await store.update({ collections: [request.collection] });
    else if (request.operation === "search") {
      result = await store.searchLex(request.question, {
        collection: request.collection,
        limit: 10,
      });
      if (!result.length) {
        const stop = new Set(
          "der die das den dem des ein eine einer einem eines und oder ist sind wird werden was wie welche welchen welcher welches warum wieso gilt beiden aus für von mit über bei zum zur als auf im in es an".split(
            " ",
          ),
        );
        const terms = [
          ...new Set(
            request.question.match(/[\p{L}\p{N}][\p{L}\p{N}_-]{2,}/gu) || [],
          ),
        ].filter((t) => !stop.has(t.toLowerCase()));
        const found = new Map();
        for (const term of terms.slice(0, 8)) {
          for (const hit of await store.searchLex(term, {
            collection: request.collection,
            limit: 10,
          }))
            found.set(hit.filepath, hit);
          if (found.size >= 10) break;
        }
        result = [...found.values()]
          .sort((a, b) => b.score - a.score)
          .slice(0, 10);
      }
    } else throw Error("Unsupported QMD operation");
    console.log(JSON.stringify({ ok: true, result }));
  } finally {
    await store.close();
  }
} catch (e) {
  console.log(JSON.stringify({ ok: false, error: e.message }));
  process.exitCode = 1;
}
