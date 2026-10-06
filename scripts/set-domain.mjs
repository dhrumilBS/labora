// Switch the site to its real domain in one step.
// Usage: npm run set-domain -- https://www.yourdomain.com
//
// The current domain is read from SITE in scripts/site_chrome.py (the source of truth). Every source file that
// contains it is updated: canonical/Open Graph/JSON-LD URLs, robots.txt, the nginx server block, and the
// security contact email (if it uses the same domain). Then the generated pages and the build (minified files, hashes, sitemap) are rerun.
import { readFileSync, writeFileSync } from 'node:fs';
import { execSync } from 'node:child_process';

const arg = process.argv[2];
let next;
try { next = new URL(arg); } catch { next = null; }
if (!next || !/^https?:$/.test(next.protocol) || next.pathname !== '/' || next.search || next.hash) {
  console.error('Usage: npm run set-domain -- https://www.yourdomain.com   (origin only, no path)');
  process.exit(1);
}

const SOURCES = ['scripts/site_chrome.py', 'scripts/build-pages.py', 'index.html', 'robots.txt', 'deploy/nginx.conf'];
const current = new URL(readFileSync('scripts/site_chrome.py', 'utf8').match(/^SITE = "([^"]+)"/m)[1]);
if (current.origin === next.origin) { console.log(`Already set to ${next.origin}`); process.exit(0); }

const bare = (h) => h.replace(/^www\./, '');
const pairs = [  // most specific first, so "https://www.x" is not half-replaced by the bare-host rule
  [current.origin, next.origin],
  [current.host, next.host],
  [bare(current.host), bare(next.host)],
];
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

for (const file of SOURCES) {
  let text = readFileSync(file, 'utf8');
  const before = text;
  // Only replace whole host names (not e.g. "notlabora.example"); one pass so replacements never chain
  const re = new RegExp(pairs.map(([a]) => `(?<![\\w.-])${esc(a)}(?![\\w-])`).join('|'), 'g');
  text = text.replace(re, (m) => pairs.find(([a]) => a === m)[1]);
  if (file === 'deploy/nginx.conf' && next.host === bare(next.host)) {
    // Canonical host has no "www.": the bare -> www redirect block becomes a www -> bare one (otherwise it would
    // redirect to itself), and the port-80 block lists both names once
    text = text.replace(/\n# https:\/\/\S+ \(no www\)[^\n]*\n(server \{[\s\S]*?\n\})\n/, (m, block) =>
      `\n# https://www.${next.host} -> one canonical host, so search engines never index two copies of the site\n` +
      block.replace(`server_name ${next.host};`, `server_name www.${next.host};`) + '\n');
    text = text.replace(new RegExp(`server_name ${esc(next.host)} ${esc(next.host)};`), `server_name ${next.host} www.${next.host};`);
  }
  if (text !== before) { writeFileSync(file, text); console.log(`updated ${file}`); }
}

console.log('Regenerating pages and running the build...');
const run = (cmd) => execSync(cmd, { stdio: 'inherit' });  // fixed commands, no user input
run('python scripts/build-blog.py');
run('python scripts/build-pages.py');
run('npm run build');
console.log(`\nDone: the site now uses ${next.origin}. If you set up a security@ address on it, update SECURITY_EMAIL in scripts/build-pages.py,`);
console.log('and on the server run `nginx -t` before reloading. The TLS certificate must cover every server_name.');
