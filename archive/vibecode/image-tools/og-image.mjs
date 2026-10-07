// Render the site-wide social image (assets/img/og-image.png, 1200 x 630) in the site's own type and colors:
// a mono label, the headline in Figtree, and the cleaned dashboard screen on the flat neutral panel.
// Usage: node scripts/og-image.mjs   (uses the locally installed Chrome; set CHROME_PATH if it is elsewhere)
import { writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer-core';

const ROOT = resolve(import.meta.dirname, '..');
const CHROME = process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const url = (p) => pathToFileURL(join(ROOT, p)).href;

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: Figtree; src: url(${url('assets/fonts/figtree-latin-wght-normal.woff2')}) format('woff2'); font-weight: 300 900; }
* { box-sizing: border-box; margin: 0; }
body { width: 1200px; height: 630px; overflow: hidden; display: grid; grid-template-columns: 500px 1fr; background: #fff; font-family: Figtree, sans-serif; color: #0d3a33; -webkit-font-smoothing: antialiased; }
.copy { display: flex; flex-direction: column; padding: 64px 0 60px 72px; }
.brand { display: flex; align-items: center; gap: 12px; font-size: 30px; font-weight: 800; letter-spacing: -.03em; }
.brand img { width: 42px; height: 42px; }
.label { display: flex; align-items: center; gap: 12px; margin-top: auto; font: 600 15px/1.4 ui-monospace, Consolas, monospace; letter-spacing: .08em; text-transform: uppercase; color: #11806a; }
.label::before { content: ""; width: 28px; height: 1.5px; background: currentColor; }
h1 { margin-top: 18px; max-width: 11ch; font-size: 52px; line-height: 1.06; font-weight: 650; letter-spacing: -.03em; }
p { margin-top: 20px; font-size: 21px; line-height: 1.5; color: #56635f; max-width: 25ch; }
.shot { position: relative; background: #f1f0eb; border-left: 1px solid #e0e6e2; overflow: hidden; }
.shot img { position: absolute; left: 0; top: 0; width: 1160px; height: auto; transform: translate(-58px, -40px); }
</style></head><body>
<div class="copy">
  <div class="brand"><img src="${url('favicon.svg')}" alt="">Labora</div>
  <div class="label">Laboratory management software</div>
  <h1>From first sample to signed report</h1>
  <p>Pathology, imaging, home collection, and billing in one system.</p>
</div>
<div class="shot"><img src="${url('assets/img/screens/dashboard-2320.webp')}" alt=""></div>
</body></html>`;

const browser = await puppeteer.launch({ executablePath: CHROME, headless: true });
const page = await browser.newPage();
await page.setViewport({ width: 1200, height: 630, deviceScaleFactor: 1 });
// Load from a file so the page may read the local font and images
const tmp = mkdtempSync(join(tmpdir(), 'labora-og-')), file = join(tmp, 'og.html');
writeFileSync(file, html);
await page.goto(pathToFileURL(file).href, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: join(ROOT, 'assets/img/og-image.png'), type: 'png' });
await browser.close();
rmSync(tmp, { recursive: true, force: true });
console.log('wrote assets/img/og-image.png');
