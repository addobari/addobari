// Renders the addobari.com film loop (MeshGradient) seen through the site's
// fluted-glass shader, one deterministic frame at a time, as PNGs.
// usage: node render.mjs <outDir> <frames> <spanMs> <startMs> <chromePath>
import { build } from "esbuild";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer-core";

const here = path.dirname(fileURLToPath(import.meta.url));
const [, , out, frames, span, start, chrome] = process.argv;
const PALETTE = ["#E3EFE8", "#9FD1B7", "#F0B998", "#9EC3E8", "#F2E9DA"]; // the site's project tile colours
const W = 880 + 160, H = 150 + 24;   // overscan 80px each side, 12px top and bottom; cropped later

await build({ entryPoints: [path.join(here, "page.js")], bundle: true, format: "iife",
  outfile: path.join(here, "bundle.js"), logLevel: "warning" });
fs.writeFileSync(path.join(here, "index.html"),
  '<!doctype html><html><body style="margin:0"><div id="mesh"></div><div id="glass"></div><script src="bundle.js"></script></body></html>');
fs.mkdirSync(out, { recursive: true });

const browser = await puppeteer.launch({ executablePath: chrome, headless: "new",
  args: ["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
         "--allow-file-access-from-files", "--ignore-gpu-blocklist"] });
const page = await browser.newPage();
page.on("pageerror", (e) => { console.error(e); process.exit(1); });
await page.goto("file://" + path.join(here, "index.html"));
await page.evaluate((c) => setup(c), { w: W, h: H, ratio: 2, colors: PALETTE, grain: 0.1 });
const n = +frames;
for (let i = 0; i < n; i++) {
  const data = await page.evaluate((ms) => renderFrame(ms), +start + (+span * i) / n);
  fs.writeFileSync(path.join(out, `f${String(i).padStart(4, "0")}.png`), Buffer.from(data.split(",")[1], "base64"));
}
await browser.close();
console.log(`rendered ${n} frames`);
