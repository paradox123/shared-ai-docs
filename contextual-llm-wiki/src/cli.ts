import { backup, restore } from "./backup.ts";
import { source, lint } from "./inspection.ts";
import { withWriter } from "./lock.ts";
import { query, search, saveDraft } from "./query.ts";
import { setup } from "./completion.ts";
import { status } from "./state.ts";
import { PIN, preflight } from "./runtime.ts";
import { json } from "./storage.ts";
import { loadConfig, initialConfig } from "./config.ts";
import { inventory } from "./sources.ts";
import { maintain } from "./maintenance.ts";
try {
  const args = process.argv.slice(2),
    command = args[0];
  const value = (name: string) => {
    const i = args.indexOf(name);
    return i >= 0 && !args[i + 1]?.startsWith("--") ? args[i + 1] : undefined;
  };
  const required = (name: string) => {
    const v = value(name);
    if (!v) throw Error(name + " is required");
    return v;
  };
  const configPath = value("--config") || "";
  let result;
  if (command === "--help" || command === "help")
    result = {
      ok: true,
      usage:
        "wiki <preflight|setup|init-config|inventory|maintain|status|lint|search|query|save|source|backup|restore> [--config PATH]",
      guide: new URL("../README.md", import.meta.url).pathname,
    };
  else if (command === "preflight") result = { ok: true, ...preflight() };
  else if (command === "init-config")
    result = initialConfig(
      required("--vault"),
      required("--output"),
      args.includes("--private") ? "private" : "general",
    );
  else if (command === "backup") {
    const c = await loadConfig(configPath);
    result = await withWriter(c, () => backup(c, required("--destination")));
  } else if (command === "restore") {
    const c = await loadConfig(configPath);
    result = await withWriter(c, () => restore(c, required("--backup")));
  } else if (command === "save") {
    const c = await loadConfig(configPath);
    result = await withWriter(c, () => saveDraft(c, required("--draft")));
  } else if (command === "source")
    result = await source(await loadConfig(configPath), required("--id"));
  else if (command === "lint")
    result = await lint(await loadConfig(configPath));
  else if (command === "search")
    result = await search(await loadConfig(configPath), required("--question"));
  else if (command === "query") {
    const c = await loadConfig(configPath);
    const action = () => query(c, required("--question"), value("--save"));
    result = args.includes("--save")
      ? await withWriter(c, action)
      : await action();
  } else if (command === "setup") result = await setup();
  else if (command === "status")
    result = await status(await loadConfig(configPath));
  else if (command === "inventory")
    result = await inventory(await loadConfig(configPath));
  else if (command === "maintain") {
    const c = await loadConfig(configPath);
    result = await withWriter(c, () => maintain(c));
  } else throw Error("operation not implemented");
  console.log(JSON.stringify(result));
  if (result.ok === false) process.exitCode = 1;
} catch (error) {
  console.log(
    JSON.stringify({
      ok: false,
      compiler: PIN,
      error: String((error as Error).message),
    }),
  );
  process.exitCode = 1;
}
