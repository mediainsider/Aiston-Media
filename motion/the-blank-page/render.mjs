// Renders index.html to MP4 frame by frame, split across parallel workers.
//   node render.mjs [out.mp4] [fps] [--workers N]
//   node render.mjs --stills 3,12.5,40 [dir]     PNG preview frames
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const dir = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const flag = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : def; };
const run = (cmd, a) => new Promise((res, rej) => spawn(cmd, a, { stdio: "inherit" }).on("close", c => c ? rej(new Error(`${cmd} exited ${c}`)) : res()));

async function openPage() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto("file://" + path.join(dir, "index.html"));
  await page.evaluate(() => window.ready);
  return { browser, page, duration: await page.evaluate(() => window.DURATION) };
}

const stills = flag("--stills");
const range = flag("--range");
if (stills) {
  const { browser, page } = await openPage();
  for (const t of stills.split(",").map(Number)) {
    await page.evaluate(t => window.seek(t), t);
    await page.screenshot({ path: path.join(args[0] || dir, `still-${t}.png`) });
  }
  await browser.close();
} else if (range) {
  // worker: render frames [a, b) to one segment
  const [a, b] = range.split(":").map(Number);
  const [out, fps] = args;
  const { browser, page } = await openPage();
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", fps, "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", out], { stdio: ["pipe", "inherit", "inherit"] });
  for (let f = a; f < b; f++) {
    await page.evaluate(t => window.seek(t), f / Number(fps));
    const buf = await page.screenshot({ type: "png" });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  await browser.close();
} else {
  const out = path.resolve(args[0] || path.join(dir, "the-blank-page.mp4"));
  const fps = args[1] || "60";
  const workers = Number(flag("--workers", os.cpus().length));
  const { browser, duration } = await openPage();
  await browser.close();
  const total = Math.ceil(duration * Number(fps));
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "render-"));
  const per = Math.ceil(total / workers);
  console.log(`${duration.toFixed(2)}s, ${total} frames, ${workers} workers`);
  const segs = [];
  await Promise.all(Array.from({ length: workers }, (_, i) => {
    const seg = path.join(tmp, `seg${i}.mp4`); segs.push(seg);
    return run(process.execPath, [fileURLToPath(import.meta.url), seg, fps, "--range", `${i * per}:${Math.min(total, (i + 1) * per)}`]);
  }));
  fs.writeFileSync(path.join(tmp, "list.txt"), segs.map(s => `file '${s}'`).join("\n"));
  await run("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", path.join(tmp, "list.txt"), "-c", "copy", "-movflags", "+faststart", out]);
  fs.rmSync(tmp, { recursive: true });
  console.log("wrote", out);
}
