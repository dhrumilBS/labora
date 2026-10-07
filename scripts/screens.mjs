// Render product screens (same style as assets/img/screens/*) from HTML templates.
// Usage: npm run screens            (renders every screen below)
//        npm run screens patient-case
// Output: assets/img/screens/<name>-{800,1200,1600,2320}.webp and phone crops <name>-m-{640,800,1080}.webp
// Uses the locally installed Chrome; set CHROME_PATH if it is somewhere else.
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer-core';

const ROOT = resolve(import.meta.dirname, '..');
const CHROME = process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const W = 1200, H = 1035, SCALE = 2320 / 1200;            // CSS canvas -> 2320 x 2000 px, like the existing screens
// The icon sprite from the homepage, so screens use the same icons as the site
const home = readFileSync(join(ROOT, 'index.html'), 'utf8');
const spriteStart = home.indexOf('<svg width="0" height="0"');
const sprite = home.slice(spriteStart, home.indexOf('</svg>\n', spriteStart) + 6);
const font = pathToFileURL(join(ROOT, 'assets/fonts/figtree-latin-wght-normal.woff2')).href;
const i = (n, c = 'ic') => `<svg class="${c}"><use href="#i-${n}"/></svg>`;

const NAV = [['home', 'Dashboard'], ['file', 'Cases'], ['flask', 'Lab'], ['tube', 'Sample Tracking'], ['scan', 'Radiology'], ['activity', 'ECG &amp; Cardiology'],
  ['pin', 'Home Collection'], ['building', 'Centers'], ['truck', 'Outsource Lab'], ['bar', 'Business'], ['users', 'Manage'], ['sliders', 'Settings']];

const css = `
@font-face { font-family: Figtree; src: url(${font}) format('woff2'); font-weight: 300 900; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: ${W}px; height: ${H}px; overflow: hidden; font: 500 14px/1.4 Figtree, system-ui, sans-serif; color: #25302e; -webkit-font-smoothing: antialiased; }
.canvas { position: relative; width: 100%; height: 100%; overflow: hidden; }
.canvas::before { content: ""; position: absolute; left: -120px; top: -150px; width: 300px; height: 300px; border-radius: 50%; background: rgba(255,255,255,.55); }
.bg-mint { background: linear-gradient(180deg, #ddf1e8 0%, #eef8f3 55%, #f3faf6 100%); }
.bg-cream { background: linear-gradient(180deg, #f8f4ea 0%, #fbf8f1 60%, #fcfaf5 100%); }
.bg-sage { background: linear-gradient(180deg, #e6efe9 0%, #f0f6f2 60%, #f6faf7 100%); }
.app { position: absolute; left: 108px; top: 108px; right: -40px; bottom: -40px; display: grid; grid-template-columns: 218px 1fr; border-radius: 22px 0 0 0; background: #fff; box-shadow: 0 2px 6px rgba(13,58,51,.06), 0 40px 80px -30px rgba(13,58,51,.28); overflow: hidden; }
.side { padding: 20px 14px; border-right: 1px solid #e6ece8; }
.brand { display: flex; align-items: center; gap: 10px; padding: 0 6px; font-weight: 800; font-size: 22px; color: #0d3a33; letter-spacing: -.02em; }
.brand svg { width: 32px; height: 32px; }
.new { display: flex; align-items: center; justify-content: center; gap: 8px; height: 38px; margin: 18px 0 12px; border-radius: 9px; background: #11806a; color: #fff; font-weight: 600; font-size: 14.5px; }
.new .ic { width: 15px; height: 15px; stroke-width: 2.4; }
.nav a { display: flex; align-items: center; gap: 12px; height: 37px; padding: 0 12px; margin-bottom: 2px; border-radius: 9px; color: #3c4744; font-size: 14.5px; text-decoration: none; }
.nav a.on { background: #dcf1e8; color: #0d3a33; font-weight: 600; }
.ic { width: 17px; height: 17px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; flex: none; }
.main { display: flex; flex-direction: column; min-width: 0; background: #f7f9f8; }
.top { display: flex; align-items: center; gap: 14px; height: 64px; padding: 0 28px; background: #fff; border-bottom: 1px solid #e6ece8; }
.top h1 { flex: 1; font-size: 19px; font-weight: 700; color: #0d3a33; letter-spacing: -.01em; display: flex; align-items: center; gap: 10px; }
.top h1 small { font-size: 13px; color: #6b7774; font-weight: 600; }
.search { display: flex; align-items: center; gap: 9px; width: 258px; height: 36px; padding: 0 14px; border: 1px solid #dfe6e2; border-radius: 9px; color: #8a9591; font-size: 13.5px; }
.search .ic { width: 15px; height: 15px; }
.loc { display: flex; align-items: center; gap: 7px; height: 36px; padding: 0 13px; border: 1px solid #dfe6e2; border-radius: 9px; font-size: 13.5px; color: #25302e; font-weight: 600; }
.loc .ic { width: 15px; height: 15px; color: #11806a; }
.bell { position: relative; color: #3c4744; } .bell::after { content: ""; position: absolute; right: -1px; top: -2px; width: 7px; height: 7px; border-radius: 50%; background: #d4483b; border: 2px solid #fff; }
.av { width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center; background: #0d3a33; color: #fff; font-weight: 700; font-size: 13px; flex: none; }
.body { padding: 24px 28px; display: grid; gap: 18px; align-content: start; }
.card { background: #fff; border: 1px solid #e3e9e5; border-radius: 14px; }
.pad { padding: 18px 20px; }
.h { font-size: 15px; font-weight: 700; color: #0d3a33; }
.sub { font-size: 12.5px; color: #6b7774; margin-top: 2px; }
.chip { display: inline-flex; align-items: center; gap: 6px; height: 24px; padding: 0 10px; border-radius: 99px; font-size: 12px; font-weight: 700; white-space: nowrap; }
.chip::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.ok { background: #e3f4ec; color: #0b6654; } .warn { background: #fcf1e1; color: #95590d; } .bad { background: #fbe9e7; color: #b23a2f; } .mute { background: #eef2f0; color: #56635f; } .ink { background: #0d3a33; color: #fff; }
.tag { display: inline-flex; align-items: center; height: 24px; padding: 0 9px; border-radius: 7px; background: #eef2f0; color: #3c4744; font-size: 12px; font-weight: 600; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
th, td { white-space: nowrap; }
th { text-align: left; font-size: 12px; color: #56635f; font-weight: 700; padding: 11px 13px; background: #f7f9f8; border-bottom: 1px solid #e6ece8; }
td { padding: 13px 13px; border-bottom: 1px solid #edf1ef; color: #25302e; }
tr:last-child td { border-bottom: 0; }
td b { color: #0d3a33; font-weight: 700; }
.float { position: absolute; left: 38px; bottom: 62px; display: flex; align-items: center; gap: 14px; padding: 16px 22px 16px 18px; border-radius: 14px; background: #fff; box-shadow: 0 2px 6px rgba(13,58,51,.08), 0 24px 48px -16px rgba(13,58,51,.3); }
.float .fi { width: 46px; height: 46px; border-radius: 12px; display: grid; place-items: center; background: #dcf1e8; color: #11806a; }
.float .fi .ic { width: 22px; height: 22px; }
.float b { display: block; font-size: 17px; color: #0d3a33; font-weight: 700; letter-spacing: -.01em; }
.float span { font-size: 13.5px; color: #56635f; }
.grid2 { display: grid; grid-template-columns: 1.55fr 1fr; gap: 18px; align-items: start; }
.row { display: flex; align-items: center; gap: 10px; }
.sp { flex: 1; }
`;

const shell = ({ bg, active, title, body, float }) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${sprite}
<div class="canvas ${bg}">
  <div class="app">
    <aside class="side">
      <div class="brand"><svg><use href="#logo-mark"/></svg>Labora</div>
      <div class="new">${i('plus')}New Case</div>
      <nav class="nav">${NAV.map(([ic, t]) => `<a class="${t === active ? 'on' : ''}">${i(ic)}${t}</a>`).join('')}</nav>
    </aside>
    <section class="main">
      <header class="top"><h1>${title}</h1><div class="search">${i('search')}Search patient, case or test</div><div class="loc">${i('building')}Main Lab · Austin</div><span class="bell">${i('bell')}</span><span class="av">SM</span></header>
      <div class="body">${body}</div>
    </section>
  </div>
  <div class="float"><span class="fi">${i(float.icon)}</span><div><b>${float.title}</b><span>${float.text}</span></div></div>
</div></body></html>`;

// ---------------------------------------------------------------------------
// Screens. Names, numbers, and times are illustrative product UI, consistent with the other screens.
// crop = phone crop in CSS px [x, y, w, h] (portrait, content without the sidebar)
// ---------------------------------------------------------------------------
const SCREENS = {
  'patient-case': {
    crop: [326, 108, 874, 880],
    html: shell({
      bg: 'bg-mint', active: 'Cases',
      title: `Case LB-24817 <small>Registered today, 9:02 AM</small>`,
      float: { icon: 'users', title: 'Five roles, one case', text: 'Front desk → delivery' },
      body: `
<div class="card pad row" style="gap:16px">
  <span class="av" style="width:46px;height:46px;background:#dcf1e8;color:#0b6654;font-size:15px">EC</span>
  <div><div class="h" style="font-size:17px">Emily Carter</div><div class="sub">F · 34 yrs · Patient ID 100482 · Referred by Dr. A. Patel</div></div>
  <span class="sp"></span><span class="chip bad">Urgent</span><span class="chip ok">Bill paid · $142.00</span>
</div>
<div class="card pad">
  <div class="row"><div><div class="h">Case progress</div><div class="sub">Every step recorded with the user and the time</div></div><span class="sp"></span><span class="chip warn">At risk in 22 min</span></div>
  <div style="display:grid;grid-template-columns:repeat(5,1fr);margin-top:20px;position:relative">
    <div style="position:absolute;left:14px;right:14%;top:13px;height:2px;background:linear-gradient(90deg,#11806a 0 76%,#dfe6e2 76%)"></div>
    ${[['check', 'Front desk', 'Registered', '9:02 AM · J. Ortiz', 'done'], ['check', 'Collection', 'Collected', '9:10 AM · J. Ortiz', 'done'], ['check', 'Lab', 'Validated', '10:12 AM · R. Kumar', 'done'],
       ['edit', 'Reporting', 'Awaiting signature', 'Dr. S. Mitchell', 'now'], ['send', 'Delivery', 'Patient + doctor', 'After signature', 'next']].map(([ic, role, what, who, st]) => `
    <div style="position:relative;padding-right:10px">
      <span style="width:28px;height:28px;border-radius:50%;display:grid;place-items:center;${st === 'done' ? 'background:#11806a;color:#fff' : st === 'now' ? 'background:#fff;color:#11806a;box-shadow:0 0 0 2px #11806a, 0 0 0 6px #dcf1e8' : 'background:#fff;color:#8a9591;box-shadow:0 0 0 2px #dfe6e2'}">${i(ic, 'ic" style="width:14px;height:14px;stroke-width:2.4')}</span>
      <div style="margin-top:12px;font-size:12px;font-weight:700;color:#6b7774;text-transform:uppercase;letter-spacing:.04em">${role}</div>
      <div style="margin-top:3px;font-weight:700;color:${st === 'next' ? '#6b7774' : '#0d3a33'}">${what}</div>
      <div class="sub">${who}</div>
    </div>`).join('')}
  </div>
</div>
<div class="grid2">
  <div class="card" style="overflow:hidden">
    <table><thead><tr><th>Test</th><th>Department</th><th>Sample</th><th>Status</th></tr></thead><tbody>
      <tr><td><b>CBC</b></td><td>Hematology</td><td>LB-24817-02 · EDTA</td><td><span class="chip ok">Validated</span></td></tr>
      <tr><td><b>Lipid Profile</b></td><td>Biochemistry</td><td>LB-24817-01 · SST</td><td><span class="chip ok">Validated</span></td></tr>
      <tr><td><b>USG Abdomen</b></td><td>Radiology</td><td>Study · Room 2</td><td><span class="chip warn">Draft saved</span></td></tr>
      <tr><td><b>ECG</b></td><td>Cardiology</td><td>Study · Room 4</td><td><span class="chip mute">Scheduled</span></td></tr>
    </tbody></table>
  </div>
  <div class="card pad">
    <div class="h">Activity</div>
    ${[['RK', 'R. Kumar validated CBC', '10:12 AM'], ['AM', 'A. Mehta stored sample in Rack B-04', '9:24 AM'], ['JO', 'J. Ortiz collected EDTA, SST', '9:10 AM'], ['JO', 'J. Ortiz registered the case', '9:02 AM']].map(([a, t, tm]) => `
    <div class="row" style="margin-top:14px;align-items:flex-start"><span class="av" style="width:30px;height:30px;font-size:11px;background:#eef2f0;color:#0d3a33">${a}</span><div style="font-size:13px;color:#25302e">${t}<div class="sub" style="margin-top:1px">${tm}</div></div></div>`).join('')}
  </div>
</div>
<div class="card pad row" style="gap:14px">
  <span style="width:38px;height:38px;border-radius:10px;display:grid;place-items:center;background:#dcf1e8;color:#11806a">${i('send')}</span>
  <div><div class="h">Delivery after signature</div><div class="sub">Signed PDF to Emily Carter by SMS and email, and to Dr. A. Patel</div></div>
  <span class="sp"></span><span class="tag">Lab report</span><span class="tag">USG report</span><span class="chip mute">Waiting for sign-off</span>
</div>` }),
  },

  'roles-access': {
    crop: [326, 108, 874, 880],
    html: shell({
      bg: 'bg-cream', active: 'Manage',
      title: `Users &amp; roles <small>Manage</small>`,
      float: { icon: 'lock', title: 'Access by role', text: 'Each person sees what they need' },
      body: `
<div class="row"><div class="tag" style="background:#0d3a33;color:#fff">Users 24</div><div class="tag">Roles 6</div><div class="tag">Centers 4</div><span class="sp"></span><span class="chip ok">Audit trail on</span></div>
<div class="grid2" style="grid-template-columns:1.7fr 1fr">
  <div class="card" style="overflow:hidden">
    <table><thead><tr><th>Name</th><th>Role</th><th>Center</th><th>Status</th></tr></thead><tbody>
      ${[['JO', 'Jordan Ortiz', 'Front desk', 'Main Lab', 'ok', 'Active'], ['RK', 'Ravi Kumar', 'Technician', 'Main Lab', 'ok', 'Active'],
         ['SM', 'Dr. Sarah Mitchell', 'Pathologist', 'All centers', 'ok', 'Active'], ['AM', 'Anita Mehta', 'Technician', 'North Center', 'ok', 'Active'],
         ['LB', 'Lena Brooks', 'Accounts', 'All centers', 'ok', 'Active'], ['ML', 'Marcus Lee', 'Phlebotomist', 'Home visits', 'ok', 'On duty'],
         ['TW', 'Tom Walsh', 'Front desk', 'Westside', 'mute', 'Removed']].map(([a, n, r, c, s, st]) => `
      <tr><td><div class="row"><span class="av" style="width:30px;height:30px;font-size:11px;background:#eef2f0;color:#0d3a33">${a}</span><b>${n}</b></div></td><td>${r}</td><td>${c}</td><td><span class="chip ${s}">${st}</span></td></tr>`).join('')}
    </tbody></table>
  </div>
  <div class="card pad">
    <div class="row"><div><div class="sub" style="margin:0">Role</div><div class="h" style="font-size:17px">Front desk</div></div><span class="sp"></span><span class="tag">6 users</span></div>
    <div style="margin-top:14px;border-top:1px solid #edf1ef">
      ${[['Register patients and tests', 1], ['Collect payments', 1], ['Print and share signed reports', 1], ['View results before release', 0], ['Edit results', 0], ['Sign reports', 0], ['Revenue reports', 0]].map(([t, on]) => `
      <div class="row" style="padding:11px 0;border-bottom:1px solid #edf1ef"><span style="font-size:13.5px">${t}</span><span class="sp"></span>
        <span style="width:38px;height:22px;border-radius:99px;position:relative;background:${on ? '#11806a' : '#d6dfda'}"><span style="position:absolute;top:3px;left:${on ? 19 : 3}px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.2)"></span></span></div>`).join('')}
    </div>
    <div class="sub" style="margin-top:12px">Changes are recorded in the audit trail.</div>
  </div>
</div>
<div class="card pad">
  <div class="row"><div class="h">Recent access changes</div><span class="sp"></span><span class="sub" style="margin:0">Audit trail</span></div>
  ${[['lock', 'Tom Walsh: access removed', 'By L. Brooks · Yesterday, 6:10 PM'], ['users', 'Marcus Lee added as Phlebotomist · Home collection', 'By L. Brooks · Oct 2, 9:41 AM'], ['eye', 'Front desk: "View results before release" turned off', 'By Dr. S. Mitchell · Sep 30, 4:15 PM']].map(([ic, t, by]) => `
  <div class="row" style="margin-top:12px"><span style="width:30px;height:30px;border-radius:8px;display:grid;place-items:center;background:#eef2f0;color:#0d3a33">${i(ic, 'ic" style="width:15px;height:15px')}</span><div style="font-size:13.5px">${t}<div class="sub" style="margin-top:1px">${by}</div></div></div>`).join('')}
</div>` }),
  },

  'centers-overview': {
    crop: [326, 108, 874, 880],
    html: shell({
      bg: 'bg-sage', active: 'Centers',
      title: `Centers <small>All centers · Today</small>`,
      float: { icon: 'building', title: 'Every center, one system', text: 'Switch, compare, and grow' },
      body: `
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px">
  ${[['building', 'Centers', '4', 'plus 1 partner'], ['file', 'Cases today', '248', '↑ 12%'], ['clock', 'On time', '96.4%', 'all centers'], ['dollar', 'Collected', '$18,420', '↑ 8%']].map(([ic, l, v, s]) => `
  <div class="card pad"><span style="width:32px;height:32px;border-radius:9px;display:grid;place-items:center;background:#dcf1e8;color:#11806a">${i(ic, 'ic" style="width:16px;height:16px')}</span>
    <div style="margin-top:12px;font-size:24px;font-weight:800;color:#0d3a33;letter-spacing:-.02em">${v}</div><div class="sub">${l} · ${s}</div></div>`).join('')}
</div>
<div class="grid2" style="grid-template-columns:1.75fr 1fr">
  <div class="card" style="overflow:hidden">
    <table><thead><tr><th>Center</th><th>Type</th><th>Cases</th><th>On time</th><th>Status</th></tr></thead><tbody>
      ${[['Main Lab · Austin', 'Lab, imaging', '132', '97%', 'ok', 'Open'], ['North Center', 'Lab', '58', '95%', 'ok', 'Open'], ['Westside', 'Collection', '34', '96%', 'ok', 'Open'],
         ['Home visits', '6 on duty', '24', '94%', 'warn', '2 en route'], ['Riverside Lab', 'Partner', '11', '—', 'mute', 'B2B']].map(([n, t, c, o, s, st]) => `
      <tr><td><b>${n}</b></td><td>${t}</td><td>${c}</td><td>${o}</td><td><span class="chip ${s}">${st}</span></td></tr>`).join('')}
    </tbody></table>
  </div>
  <div class="card pad">
    <div class="h">Cases by center</div><div class="sub">Today</div>
    ${[['Main Lab', 132], ['North', 58], ['Westside', 34], ['Home', 24]].map(([n, v]) => `
    <div style="margin-top:14px"><div class="row" style="font-size:13px"><span>${n}</span><span class="sp"></span><b style="color:#0d3a33">${v}</b></div>
      <div style="margin-top:6px;height:8px;border-radius:99px;background:#eef2f0"><div style="width:${Math.round(v / 132 * 100)}%;height:100%;border-radius:99px;background:${n === 'Main Lab' ? '#0d3a33' : '#11806a'}"></div></div></div>`).join('')}
  </div>
</div>
<div class="card pad row" style="gap:28px">
  <div><div class="h">Shared setup</div><div class="sub">One configuration, used by every center</div></div>
  ${[['Test menu', '312 tests'], ['Price lists', '3'], ['Report templates', '86'], ['Roles', '6']].map(([l, v]) => `<div><div style="font-size:18px;font-weight:800;color:#0d3a33">${v}</div><div class="sub" style="margin:0">${l}</div></div>`).join('')}
  <span class="sp"></span><span class="chip ok">Synced to all centers</span>
</div>` }),
  },
};

const only = process.argv.slice(2);
const names = only.length ? only : Object.keys(SCREENS);
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true });
const tmp = mkdtempSync(join(tmpdir(), 'labora-screens-'));
const page = await browser.newPage();
for (const name of names) {
  const s = SCREENS[name]; if (!s) throw new Error(`Unknown screen: ${name}`);
  const file = join(tmp, `${name}.html`); writeFileSync(file, s.html);
  const out = (w) => join(ROOT, 'assets/img/screens', `${name}-${w}.webp`);
  // Desktop sizes: render at the full 2320 px, then let Chrome downscale for the smaller files
  for (const w of [2320, 1600, 1200, 800]) {
    await page.setViewport({ width: W, height: H, deviceScaleFactor: SCALE * w / 2320 });
    await page.goto(pathToFileURL(file).href, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: out(w), type: 'webp', quality: w >= 1600 ? 82 : 80, clip: { x: 0, y: 0, width: W, height: 2000 / SCALE } });
  }
  // Phone crops: the case content without the sidebar, sized like the existing -m- files
  const [cx, cy, cw, ch] = s.crop;
  for (const w of [640, 800, 1080]) {
    await page.setViewport({ width: W, height: H, deviceScaleFactor: w / cw });
    await page.goto(pathToFileURL(file).href, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: out(`m-${w}`), type: 'webp', quality: 80, clip: { x: cx, y: cy, width: cw, height: ch } });
  }
  console.log('rendered', name);
}
await browser.close();
rmSync(tmp, { recursive: true, force: true });
