// Renders index.html to MP4 frame by frame: node render.mjs [out.mp4] [fps] [seconds]
// Pass --stills t1,t2,... to write PNG previews instead.
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const dir = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const stillsIdx = args.indexOf("--stills");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto("file://" + path.join(dir, "index.html"));
await page.evaluate(() => window.ready);

if (stillsIdx >= 0) {
  for (const t of args[stillsIdx + 1].split(",").map(Number)) {
    await page.evaluate(t => window.seek(t), t);
    await page.screenshot({ path: path.join(args[stillsIdx + 2] || dir, `still-${t}.png`) });
  }
} else {
  const [out = path.join(dir, "the-conversation-questions.mp4"), fps = "60", secs = "13"] = args;
  const total = Math.round(Number(fps) * Number(secs));
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", fps, "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], { stdio: ["pipe", "inherit", "inherit"] });
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => window.seek(t), f / Number(fps));
    const buf = await page.screenshot({ type: "png" });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (f % 60 === 0) process.stdout.write(`\rframe ${f}/${total}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  console.log("\nwrote", out);
}
await browser.close();
