import { readFile, writeFile, rename, mkdir } from "node:fs/promises";
import path from "node:path";
import { createHash, randomUUID } from "node:crypto";
export const hash = (text: string | Buffer) =>
  createHash("sha256").update(text).digest("hex");
export async function json(file: string, fallback?: any): Promise<any> {
  try {
    return JSON.parse(await readFile(file, "utf8"));
  } catch (e) {
    if ((e as any).code === "ENOENT" && fallback !== undefined) return fallback;
    throw e;
  }
}
export async function atomic(file: string, body: string) {
  await mkdir(path.dirname(file), { recursive: true });
  const tmp = file + "." + randomUUID() + ".tmp";
  await writeFile(tmp, body);
  await rename(tmp, file);
}
export const writeJson = (file: string, value: any) =>
  atomic(file, JSON.stringify(value, null, 2) + "\n");
