import { createHash } from "node:crypto";
import { readdir, readFile, writeFile } from "node:fs/promises";
import { extname, relative, resolve } from "node:path";

const root = resolve(import.meta.dirname, "../dist");
const manifestPath = resolve(root, "asset-manifest.json");
const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
};

async function files(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map((entry) =>
      entry.isDirectory() ? files(resolve(directory, entry.name)) : [resolve(directory, entry.name)],
    ),
  );
  return nested.flat();
}

const assets = [];
for (const file of (await files(root)).sort()) {
  const path = relative(root, file).replaceAll("\\", "/");
  if (path === "asset-manifest.json") continue;
  const media_type = types[extname(path)];
  if (!media_type || path.endsWith(".map")) throw new Error(`unsupported built asset: ${path}`);
  const data = await readFile(file);
  assets.push({ path, media_type, byte_count: data.length, sha256: createHash("sha256").update(data).digest("hex") });
}
const output = Buffer.from(`${JSON.stringify({ schema_version: "1.0", assets }, null, 2)}\n`);
if (process.argv.includes("--check")) {
  if (!(await readFile(manifestPath)).equals(output)) process.exitCode = 1;
} else await writeFile(manifestPath, output);
