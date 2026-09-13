import assert from "node:assert/strict";
import { fixture, invoke } from "./support.ts";
import { writeFile, readFile } from "node:fs/promises";
import path from "node:path";
const f = await fixture();
await f.close();
f.config.context = "common-acceptance-01";
f.config.repos[0].id = "private";
f.config.repos[0].scope = "private";
f.config.repos[1].id = "probare-crm";
const personal =
  "# Liquiditätsreserve\n\nDie Liquiditätsreserve ist der heute frei verfügbare Geldbetrag zur Deckung laufender Ausgaben.\n\nDas persönliche Portfolio hat heute 2000 Euro frei verfügbare Reserve. Die Reserve soll bis Oktober laufende Ausgaben decken. Erwartete, noch nicht eingegangene Zahlungen zählen nicht als heutige Liquidität.\n";
const project =
  "# Liquiditätsreserve\n\nDie Liquiditätsreserve ist der heute frei verfügbare Geldbetrag zur Deckung laufender Ausgaben.\n\nEin laufender Projektvertrag sieht einen Zahlungseingang von 5000 Euro im Oktober vor. Der Betrag steht erst nach Zahlungseingang zur Verfügung und darf vorher nicht als verfügbare Reserve gerechnet werden. Diese zeitliche Trennung ist für die Planung laufender Ausgaben relevant.\n";
const control =
  "# Portfolio als Designkatalog\n\nEin Designportfolio zeigt blaue Umschläge und typografische Entwürfe. Portfolio bedeutet in diesem Dokument eine Sammlung von Gestaltungsarbeiten. Es enthält keine Angaben zu Geldreserven, Einnahmen oder Zahlungszeitpunkten.\n";
await writeFile(path.join(f.dir, "alpha/README.md"), personal);
await writeFile(path.join(f.dir, "beta/README.md"), project);
await writeFile(path.join(f.dir, "alpha/control.md"), control);
await f.saveConfig();
console.log("Acceptance directory:", f.dir);
const run = async (name: string, args: string[]) => {
  const result = await invoke(
    [args[0], "--config", f.configPath, ...args.slice(1)],
    { LLMWIKI_PROVIDER: "codex-agent" },
  );
  await writeFile(
    new URL(`../evidence/common-real-${name}.json`, import.meta.url),
    JSON.stringify(result, null, 2) + "\n",
  );
  console.log(
    name,
    result.ok,
    result.error || result.noop || result.evidence?.map((e: any) => e.id) || "",
  );
  if (!result.ok) throw Error(JSON.stringify(result));
  return result;
};
await run("maintain", ["maintain"]);
const queried = await run("query", [
  "query",
  "--question",
  "Wie wirken die erwarteten Projekteinnahmen auf die heutige Liquiditätsplanung des persönlichen Portfolios?",
]);
const limited = await run("limited", [
  "query",
  "--question",
  "Welche Reserve hat das persönliche Portfolio heute?",
  "--repo",
  "private",
]);
assert.equal((await run("noop", ["maintain"])).noop, true);
const state = await run("status", ["status"]);
const shared = state.pages.filter(
  (p: any) =>
    p.sourceVersions["private/README.md"] &&
    p.sourceVersions["probare-crm/README.md"],
);
assert.ok(
  shared.length > 0,
  "maintenance produces a persistent shared concept",
);
assert.ok(
  queried.evidence.some((e: any) => shared.some((p: any) => p.id === e.id)),
);
assert.ok(
  queried.evidence.every((e: any) => !e.sourceVersions["private/control.md"]),
);
assert.ok(
  limited.evidence.every((e: any) =>
    Object.keys(e.sourceVersions).every((id) => id === "private/README.md"),
  ),
);
assert.equal(queried.fallback, false);
assert.ok(
  state.pages.every((p: any) => p.kind === "concept"),
  "queries do not implicitly save answers",
);
const bodies = await Promise.all(
  state.pages
    .filter((p: any) => p.kind === "concept")
    .map(
      async (p: any) =>
        `<!-- ${p.id} -->\n` +
        (await readFile(
          path.join(f.config.output, "wiki", p.id + ".md"),
          "utf8",
        )),
    ),
);
await writeFile(
  new URL("../evidence/common-real-pages.md", import.meta.url),
  bodies.join("\n\n---\n\n"),
);
if (
  (await readFile(path.join(f.dir, "alpha/README.md"), "utf8")) !== personal ||
  (await readFile(path.join(f.dir, "beta/README.md"), "utf8")) !== project ||
  (await readFile(path.join(f.dir, "alpha/control.md"), "utf8")) !== control
)
  throw Error("Originals changed");
console.log("Original source bytes unchanged");
