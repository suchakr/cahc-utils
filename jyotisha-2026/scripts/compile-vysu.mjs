#!/usr/bin/env node
import { readFile, writeFile, mkdir, readdir, unlink } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { compileVyomaSutraFile, validateStory } from "./vysu-compiler.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");

function usage() {
  console.error("Usage: node scripts/compile-vysu.mjs [slug] [--json-out PATH] [--no-write]");
}

async function readJson(filePath) {
  return JSON.parse(await readFile(filePath, "utf8"));
}

async function writeJson(filePath, data) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

async function compileStorySources(slug, options = {}) {
  const root = path.join(repoRoot, "stories", slug);
  const compiledRoot = path.join(root, "compiled");
  const entries = existsSync(root) ? await readdir(root, { withFileTypes: true }) : [];
  const stories = [];
  const expectedOutputs = new Set();
  if (!options.noWrite) await mkdir(compiledRoot, { recursive: true });

  for (const entry of entries.filter((item) => item.isFile() && item.name.endsWith(".vysu")).sort((a, b) => a.name.localeCompare(b.name))) {
    const sourcePath = path.join(root, entry.name);
    const source = await readFile(sourcePath, "utf8");
    const story = compileVyomaSutraFile(source, path.basename(entry.name, ".vysu"));
    const outPath = path.join(compiledRoot, `${story.id}.json`);
    expectedOutputs.add(outPath);
    validateStory(story);
    if (!options.noWrite) await writeJson(outPath, story);
    stories.push(story);
  }

  for (const entry of entries.filter((item) => item.isFile() && item.name.endsWith(".json")).sort((a, b) => a.name.localeCompare(b.name))) {
    const sourcePath = path.join(root, entry.name);
    const story = validateStory(await readJson(sourcePath));
    const outPath = path.join(compiledRoot, entry.name);
    expectedOutputs.add(outPath);
    if (!options.noWrite) await writeJson(outPath, story);
    stories.push(story);
  }

  if (!options.noWrite && existsSync(compiledRoot)) {
    for (const entry of await readdir(compiledRoot, { withFileTypes: true })) {
      if (!entry.isFile() || !entry.name.endsWith(".json")) continue;
      const stalePath = path.join(compiledRoot, entry.name);
      if (!expectedOutputs.has(stalePath)) await unlink(stalePath);
    }
  }

  stories.sort((a, b) => {
    const order = Number(a.order ?? 9999) - Number(b.order ?? 9999);
    if (order) return order;
    return String(a.title || a.id).localeCompare(String(b.title || b.id));
  });
  return stories;
}

async function main() {
  const args = process.argv.slice(2);
  const slug = args.find((arg) => !arg.startsWith("--")) || "nakshatra-precession-explorer";
  const jsonOutIndex = args.indexOf("--json-out");
  const jsonOut = jsonOutIndex >= 0 ? args[jsonOutIndex + 1] : null;
  const noWrite = args.includes("--no-write");
  if ((jsonOutIndex >= 0 && !jsonOut) || args.includes("--help")) {
    usage();
    process.exit(args.includes("--help") ? 0 : 2);
  }

  const stories = await compileStorySources(slug, { noWrite });
  if (jsonOut) {
    await writeJson(path.resolve(repoRoot, jsonOut), stories);
  } else {
    process.stdout.write(`${JSON.stringify(stories, null, 2)}\n`);
  }
  const warningCount = stories.reduce((count, story) => count + (Array.isArray(story.warnings) ? story.warnings.length : 0), 0);
  console.error(`Compiled ${stories.length} VyomaSutra story source(s) for ${slug}.`);
  if (warningCount) console.error(`Warnings: ${warningCount}`);
}

main().catch((error) => {
  console.error(error?.stack || error?.message || String(error));
  process.exit(1);
});
